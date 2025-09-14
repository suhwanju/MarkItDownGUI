"""
파일 충돌 처리기
파일 저장 시 발생하는 충돌을 감지하고 해결하는 중앙화된 시스템
"""

import os
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .models import (
    FileInfo, ConversionResult, FileConflictStatus, FileConflictPolicy,
    FileConflictInfo, FileConflictConfig, ConversionProgressStatus
)
from .exceptions import (
    FileProcessingError, ValidationError, ResourceError, 
    ConcurrencyError, wrap_exception
)
from .logger import get_logger


logger = get_logger(__name__)


@dataclass
class ConflictStatistics:
    """충돌 통계 정보"""
    total_files_checked: int = 0
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    files_skipped: int = 0
    files_overwritten: int = 0
    files_renamed: int = 0
    processing_errors: int = 0
    
    # 정책별 적용 횟수
    policy_usage: Dict[FileConflictPolicy, int] = field(default_factory=lambda: defaultdict(int))
    
    # 처리 시간 통계
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        if self.total_files_checked == 0:
            return 100.0
        return ((self.total_files_checked - self.processing_errors) / self.total_files_checked) * 100
    
    @property
    def conflict_rate(self) -> float:
        """충돌 발생률 계산"""
        if self.total_files_checked == 0:
            return 0.0
        return (self.conflicts_detected / self.total_files_checked) * 100
    
    @property
    def resolution_rate(self) -> float:
        """충돌 해결률 계산"""
        if self.conflicts_detected == 0:
            return 100.0
        return (self.conflicts_resolved / self.conflicts_detected) * 100
    
    def add_policy_usage(self, policy: FileConflictPolicy):
        """정책 사용 횟수 증가"""
        self.policy_usage[policy] += 1
    
    def get_most_used_policy(self) -> Optional[FileConflictPolicy]:
        """가장 많이 사용된 정책 반환"""
        if not self.policy_usage:
            return None
        return max(self.policy_usage.keys(), key=lambda k: self.policy_usage[k])


class FileConflictHandler:
    """
    파일 충돌 처리기
    
    파일 저장 시 발생하는 충돌을 감지하고 정책에 따라 해결하는 중앙화된 시스템.
    스레드 안전성을 보장하며 배치 처리 및 통계 기능을 제공한다.
    """
    
    def __init__(self, config: Optional[FileConflictConfig] = None):
        """
        FileConflictHandler 초기화
        
        Args:
            config: 파일 충돌 설정, None인 경우 기본 설정 사용
        """
        self.config = config or FileConflictConfig()
        self._statistics = ConflictStatistics()
        self._lock = threading.RLock()  # 재진입 가능한 락
        self._user_choices: Dict[str, FileConflictPolicy] = {}  # 사용자 선택 기억
        self._batch_policy: Optional[FileConflictPolicy] = None
        self._apply_to_all = False
        
        logger.info(f"FileConflictHandler 초기화됨 - 기본 정책: {self.config.default_policy}")
    
    @wrap_exception
    def detect_conflict(self, source_path: Path, target_path: Path) -> FileConflictInfo:
        """
        파일 충돌 감지
        
        Args:
            source_path: 원본 파일 경로
            target_path: 대상 파일 경로
        
        Returns:
            FileConflictInfo: 충돌 정보
        
        Raises:
            ValidationError: 경로가 유효하지 않은 경우
            ResourceError: 파일 접근 오류가 발생한 경우
        """
        start_time = datetime.now()
        
        try:
            with self._lock:
                self._statistics.total_files_checked += 1
                
                # 경로 유효성 검증
                if not source_path or not target_path:
                    raise ValidationError("원본 경로와 대상 경로가 모두 필요합니다")
                
                if not source_path.exists():
                    raise ValidationError(f"원본 파일이 존재하지 않습니다: {source_path}")
                
                # 충돌 정보 객체 생성
                conflict_info = FileConflictInfo(
                    source_path=source_path,
                    target_path=target_path,
                    conflict_status=FileConflictStatus.NONE
                )
                
                # 대상 파일 존재 여부 확인
                if target_path.exists():
                    conflict_info.conflict_status = FileConflictStatus.EXISTS
                    self._statistics.conflicts_detected += 1
                    
                    try:
                        # 기존 파일 정보 수집
                        stat = target_path.stat()
                        conflict_info.existing_file_size = stat.st_size
                        conflict_info.existing_file_modified = datetime.fromtimestamp(stat.st_mtime)
                        
                        # 추천 해결 방법 결정
                        conflict_info.suggested_resolution = self._suggest_resolution(
                            source_path, target_path, conflict_info
                        )
                        
                        logger.debug(f"충돌 감지됨: {target_path.name} (크기: {conflict_info.existing_file_size}, "
                                   f"수정일: {conflict_info.existing_file_modified})")
                    
                    except OSError as e:
                        logger.warning(f"기존 파일 정보 수집 실패 ({target_path}): {e}")
                        # 파일 정보를 가져올 수 없어도 충돌은 존재
                        conflict_info.suggested_resolution = self.config.default_policy
                else:
                    logger.debug(f"충돌 없음: {target_path.name}")
                
                # 처리 시간 업데이트
                processing_time = (datetime.now() - start_time).total_seconds()
                self._statistics.total_processing_time += processing_time
                if self._statistics.total_files_checked > 0:
                    self._statistics.average_processing_time = (
                        self._statistics.total_processing_time / self._statistics.total_files_checked
                    )
                
                return conflict_info
                
        except Exception as e:
            with self._lock:
                self._statistics.processing_errors += 1
            logger.error(f"충돌 감지 중 오류 발생 ({target_path}): {e}")
            raise
    
    def _suggest_resolution(self, source_path: Path, target_path: Path, 
                          conflict_info: FileConflictInfo) -> FileConflictPolicy:
        """
        충돌 해결 방법 추천
        
        Args:
            source_path: 원본 파일 경로
            target_path: 대상 파일 경로
            conflict_info: 충돌 정보
        
        Returns:
            FileConflictPolicy: 추천 정책
        """
        # 배치 정책이 설정된 경우 우선 적용
        if self._apply_to_all and self._batch_policy:
            return self._batch_policy
        
        # 사용자가 이전에 선택한 정책이 있고 기억하기 옵션이 활성화된 경우
        if self.config.remember_choices:
            key = target_path.name
            if key in self._user_choices:
                return self._user_choices[key]
        
        # 파일 크기와 수정 시간을 비교하여 지능적 추천
        try:
            source_stat = source_path.stat()
            
            if conflict_info.existing_file_size and conflict_info.existing_file_modified:
                source_modified = datetime.fromtimestamp(source_stat.st_mtime)
                
                # 원본이 더 최신이면 덮어쓰기 추천
                if source_modified > conflict_info.existing_file_modified:
                    return FileConflictPolicy.OVERWRITE
                
                # 크기가 다르면 이름 변경 추천 (둘 다 보존)
                if source_stat.st_size != conflict_info.existing_file_size:
                    return FileConflictPolicy.RENAME
        
        except OSError:
            pass  # 파일 정보를 가져올 수 없는 경우 무시
        
        # 기본 정책 반환
        return self.config.default_policy
    
    @wrap_exception
    def resolve_conflict(self, conflict_info: FileConflictInfo, 
                        policy: Optional[FileConflictPolicy] = None,
                        user_callback: Optional[Callable[[FileConflictInfo], FileConflictPolicy]] = None) -> FileConflictInfo:
        """
        파일 충돌 해결
        
        Args:
            conflict_info: 충돌 정보
            policy: 적용할 정책 (None인 경우 추천 정책 또는 기본 정책 사용)
            user_callback: 사용자 입력 콜백 (ASK_USER 정책 시 사용)
        
        Returns:
            FileConflictInfo: 해결된 충돌 정보
        
        Raises:
            ValidationError: 충돌 정보가 유효하지 않은 경우
            FileProcessingError: 파일 처리 오류가 발생한 경우
        """
        if conflict_info.conflict_status != FileConflictStatus.EXISTS:
            # 충돌이 없는 경우 그대로 반환
            return conflict_info
        
        # 적용할 정책 결정
        if policy is None:
            if self._apply_to_all and self._batch_policy:
                policy = self._batch_policy
            elif conflict_info.suggested_resolution:
                policy = conflict_info.suggested_resolution
            else:
                policy = self.config.default_policy
        
        try:
            with self._lock:
                # ASK_USER 정책인 경우 사용자 입력 요청
                if policy == FileConflictPolicy.ASK_USER:
                    if user_callback:
                        policy = user_callback(conflict_info)
                        # 사용자 선택 기억
                        if self.config.remember_choices:
                            self._user_choices[conflict_info.file_name] = policy
                    else:
                        # 콜백이 없는 경우 기본 정책 사용
                        logger.warning(f"사용자 입력 콜백이 없어 기본 정책 사용: {self.config.default_policy}")
                        policy = self.config.default_policy
                
                # 정책 적용
                resolved_info = self._apply_policy(conflict_info, policy)
                
                # 통계 업데이트
                self._statistics.conflicts_resolved += 1
                self._statistics.add_policy_usage(policy)
                
                if policy == FileConflictPolicy.SKIP:
                    self._statistics.files_skipped += 1
                elif policy == FileConflictPolicy.OVERWRITE:
                    self._statistics.files_overwritten += 1
                elif policy == FileConflictPolicy.RENAME:
                    self._statistics.files_renamed += 1
                
                logger.info(f"충돌 해결됨: {conflict_info.file_name} -> {policy.value}")
                return resolved_info
                
        except Exception as e:
            with self._lock:
                self._statistics.processing_errors += 1
            logger.error(f"충돌 해결 중 오류 발생 ({conflict_info.file_name}): {e}")
            raise FileProcessingError(f"충돌 해결 실패: {e}")
    
    def _apply_policy(self, conflict_info: FileConflictInfo, policy: FileConflictPolicy) -> FileConflictInfo:
        """
        충돌 해결 정책 적용
        
        Args:
            conflict_info: 충돌 정보
            policy: 적용할 정책
        
        Returns:
            FileConflictInfo: 정책이 적용된 충돌 정보
        """
        resolved_info = FileConflictInfo(
            source_path=conflict_info.source_path,
            target_path=conflict_info.target_path,
            conflict_status=FileConflictStatus.RESOLVED,
            existing_file_size=conflict_info.existing_file_size,
            existing_file_modified=conflict_info.existing_file_modified,
            suggested_resolution=conflict_info.suggested_resolution
        )
        
        if policy == FileConflictPolicy.SKIP:
            resolved_info.conflict_status = FileConflictStatus.WILL_SKIP
            resolved_info.resolved_path = None  # 저장하지 않음
            
        elif policy == FileConflictPolicy.OVERWRITE:
            resolved_info.conflict_status = FileConflictStatus.WILL_OVERWRITE
            resolved_info.resolved_path = conflict_info.target_path
            
            # 원본 백업 옵션이 활성화된 경우
            if self.config.backup_original:
                backup_path = self.generate_renamed_path(
                    conflict_info.target_path, 
                    pattern="{name}_backup_{timestamp}{ext}"
                )
                try:
                    conflict_info.target_path.rename(backup_path)
                    logger.info(f"원본 파일 백업됨: {backup_path}")
                except OSError as e:
                    logger.warning(f"원본 파일 백업 실패: {e}")
            
        elif policy == FileConflictPolicy.RENAME:
            resolved_info.conflict_status = FileConflictStatus.WILL_RENAME
            resolved_info.resolved_path = self.generate_renamed_path(
                conflict_info.target_path,
                self.config.auto_rename_pattern
            )
            
        else:
            raise ValidationError(f"알 수 없는 충돌 정책: {policy}")
        
        return resolved_info
    
    @wrap_exception
    def generate_renamed_path(self, target_path: Path, pattern: Optional[str] = None) -> Path:
        """
        충돌을 피하는 새 파일 경로 생성
        
        Args:
            target_path: 원본 대상 경로
            pattern: 이름 변경 패턴 (기본값: config의 auto_rename_pattern)
        
        Returns:
            Path: 충돌이 없는 새 파일 경로
        
        Raises:
            ValidationError: 경로가 유효하지 않은 경우
            ResourceError: 파일 시스템 오류가 발생한 경우
        """
        if not target_path:
            raise ValidationError("대상 경로가 필요합니다")
        
        pattern = pattern or self.config.auto_rename_pattern
        
        try:
            counter = 1
            name_stem = target_path.stem
            suffix = target_path.suffix
            parent = target_path.parent
            
            # 최대 반복 횟수 제한 (무한 루프 방지)
            max_attempts = 1000
            
            while counter <= max_attempts:
                # 패턴에 따른 새 파일명 생성
                if "{timestamp}" in pattern:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = pattern.format(
                        name=name_stem,
                        counter=counter,
                        timestamp=timestamp,
                        ext=suffix
                    )
                else:
                    new_name = pattern.format(
                        name=name_stem,
                        counter=counter,
                        ext=suffix
                    )
                
                new_path = parent / new_name
                
                # 새 경로가 충돌하지 않는지 확인
                if not new_path.exists():
                    logger.debug(f"새 파일 경로 생성됨: {new_path}")
                    return new_path
                
                counter += 1
            
            # 최대 시도 횟수 초과
            raise ResourceError(f"고유한 파일명을 생성할 수 없습니다 (최대 {max_attempts}회 시도)")
            
        except Exception as e:
            if isinstance(e, (ValidationError, ResourceError)):
                raise
            raise ResourceError(f"파일 경로 생성 중 오류: {e}")
    
    @wrap_exception
    def apply_batch_policy(self, files: List[FileInfo], policy: FileConflictPolicy,
                          progress_callback: Optional[Callable[[int, int], None]] = None,
                          user_callback: Optional[Callable[[FileConflictInfo], FileConflictPolicy]] = None) -> List[Tuple[FileInfo, FileConflictInfo]]:
        """
        여러 파일에 대한 배치 충돌 해결
        
        Args:
            files: 처리할 파일 목록
            policy: 적용할 정책
            progress_callback: 진행률 콜백 (current, total)
            user_callback: 사용자 입력 콜백 (ASK_USER 정책 시 사용)
        
        Returns:
            List[Tuple[FileInfo, FileConflictInfo]]: (파일정보, 충돌해결정보) 튜플 목록
        
        Raises:
            ValidationError: 입력이 유효하지 않은 경우
            ConcurrencyError: 스레드 안전성 오류가 발생한 경우
        """
        if not files:
            return []
        
        try:
            with self._lock:
                # 배치 정책 설정
                self._batch_policy = policy
                self._apply_to_all = True
                
                results = []
                total_files = len(files)
                
                logger.info(f"배치 충돌 처리 시작: {total_files}개 파일, 정책: {policy.value}")
                
                for i, file_info in enumerate(files):
                    try:
                        # 출력 경로 생성
                        if file_info.output_path:
                            target_path = file_info.output_path
                        else:
                            # 기본 마크다운 출력 경로 생성
                            target_path = file_info.path.parent / f"{file_info.path.stem}.md"
                        
                        # 충돌 감지
                        conflict_info = self.detect_conflict(file_info.path, target_path)
                        
                        # 충돌 해결
                        if conflict_info.conflict_status == FileConflictStatus.EXISTS:
                            resolved_info = self.resolve_conflict(
                                conflict_info, policy, user_callback
                            )
                        else:
                            resolved_info = conflict_info
                        
                        # 파일 정보 업데이트
                        file_info.conflict_status = resolved_info.conflict_status
                        if resolved_info.resolved_path:
                            file_info.resolved_output_path = resolved_info.resolved_path
                        
                        results.append((file_info, resolved_info))
                        
                        # 진행률 업데이트
                        if progress_callback:
                            progress_callback(i + 1, total_files)
                            
                    except Exception as e:
                        logger.error(f"배치 처리 중 오류 ({file_info.name}): {e}")
                        # 실패한 파일도 결과에 포함 (오류 정보와 함께)
                        error_conflict = FileConflictInfo(
                            source_path=file_info.path,
                            target_path=target_path,
                            conflict_status=FileConflictStatus.NONE
                        )
                        results.append((file_info, error_conflict))
                
                logger.info(f"배치 충돌 처리 완료: {len(results)}개 결과")
                return results
                
        except Exception as e:
            logger.error(f"배치 충돌 처리 실패: {e}")
            raise ConcurrencyError(f"배치 처리 오류: {e}")
        
        finally:
            with self._lock:
                # 배치 모드 해제
                self._batch_policy = None
                self._apply_to_all = False
    
    def get_conflict_statistics(self) -> ConflictStatistics:
        """
        충돌 처리 통계 반환
        
        Returns:
            ConflictStatistics: 통계 정보
        """
        with self._lock:
            return ConflictStatistics(
                total_files_checked=self._statistics.total_files_checked,
                conflicts_detected=self._statistics.conflicts_detected,
                conflicts_resolved=self._statistics.conflicts_resolved,
                files_skipped=self._statistics.files_skipped,
                files_overwritten=self._statistics.files_overwritten,
                files_renamed=self._statistics.files_renamed,
                processing_errors=self._statistics.processing_errors,
                policy_usage=dict(self._statistics.policy_usage),
                total_processing_time=self._statistics.total_processing_time,
                average_processing_time=self._statistics.average_processing_time
            )
    
    def reset_statistics(self):
        """통계 초기화"""
        with self._lock:
            self._statistics = ConflictStatistics()
            logger.info("충돌 처리 통계가 초기화되었습니다")
    
    def clear_user_choices(self):
        """사용자 선택 기억 정보 초기화"""
        with self._lock:
            self._user_choices.clear()
            logger.info("사용자 선택 기억 정보가 초기화되었습니다")
    
    def set_batch_mode(self, policy: FileConflictPolicy, apply_to_all: bool = True):
        """
        배치 모드 설정
        
        Args:
            policy: 배치에서 사용할 정책
            apply_to_all: 모든 파일에 적용할지 여부
        """
        with self._lock:
            self._batch_policy = policy
            self._apply_to_all = apply_to_all
            logger.info(f"배치 모드 설정됨: {policy.value}, 전체 적용: {apply_to_all}")
    
    def clear_batch_mode(self):
        """배치 모드 해제"""
        with self._lock:
            self._batch_policy = None
            self._apply_to_all = False
            logger.info("배치 모드가 해제되었습니다")
    
    def is_batch_mode(self) -> bool:
        """배치 모드 여부 확인"""
        with self._lock:
            return self._batch_policy is not None and self._apply_to_all
    
    def get_batch_policy(self) -> Optional[FileConflictPolicy]:
        """현재 배치 정책 반환"""
        with self._lock:
            return self._batch_policy
    
    def update_config(self, config: FileConflictConfig):
        """
        설정 업데이트
        
        Args:
            config: 새로운 설정
        """
        with self._lock:
            old_config = self.config
            self.config = config
            
            # 기억하기 설정이 비활성화된 경우 기존 선택 초기화
            if not config.remember_choices and old_config.remember_choices:
                self._user_choices.clear()
            
            logger.info(f"충돌 처리 설정 업데이트됨: {config}")
    
    def get_config(self) -> FileConflictConfig:
        """현재 설정 반환"""
        with self._lock:
            return self.config
    
    def __enter__(self):
        """Context manager 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        if exc_type is not None:
            logger.error(f"FileConflictHandler context에서 예외 발생: {exc_val}")
        return False


# 유틸리티 함수들

def create_conflict_handler(config: Optional[FileConflictConfig] = None) -> FileConflictHandler:
    """
    FileConflictHandler 인스턴스 생성 헬퍼 함수
    
    Args:
        config: 충돌 처리 설정
    
    Returns:
        FileConflictHandler: 설정된 충돌 처리기
    """
    return FileConflictHandler(config)


def resolve_file_conflicts_batch(source_files: List[Path], 
                                output_dir: Optional[Path] = None,
                                policy: FileConflictPolicy = FileConflictPolicy.ASK_USER,
                                config: Optional[FileConflictConfig] = None) -> List[Tuple[Path, Path, FileConflictStatus]]:
    """
    여러 파일의 충돌을 일괄 해결하는 편의 함수
    
    Args:
        source_files: 원본 파일 경로 목록
        output_dir: 출력 디렉토리 (None인 경우 원본과 같은 디렉토리)
        policy: 충돌 해결 정책
        config: 충돌 처리 설정
    
    Returns:
        List[Tuple[Path, Path, FileConflictStatus]]: (원본경로, 해결된경로, 상태) 목록
    """
    handler = create_conflict_handler(config)
    results = []
    
    try:
        with handler:
            for source_path in source_files:
                # 출력 경로 결정
                if output_dir:
                    target_path = output_dir / f"{source_path.stem}.md"
                else:
                    target_path = source_path.parent / f"{source_path.stem}.md"
                
                # 충돌 감지 및 해결
                conflict_info = handler.detect_conflict(source_path, target_path)
                
                if conflict_info.conflict_status == FileConflictStatus.EXISTS:
                    resolved_info = handler.resolve_conflict(conflict_info, policy)
                    if resolved_info.resolved_path:
                        results.append((source_path, resolved_info.resolved_path, resolved_info.conflict_status))
                    else:
                        results.append((source_path, target_path, FileConflictStatus.WILL_SKIP))
                else:
                    results.append((source_path, target_path, FileConflictStatus.NONE))
    
    except Exception as e:
        logger.error(f"배치 충돌 해결 실패: {e}")
        raise
    
    return results


def get_conflict_summary(statistics: ConflictStatistics) -> str:
    """
    충돌 통계를 읽기 쉬운 텍스트로 변환
    
    Args:
        statistics: 충돌 통계
    
    Returns:
        str: 포맷된 통계 텍스트
    """
    summary = []
    summary.append(f"총 확인된 파일: {statistics.total_files_checked}개")
    summary.append(f"충돌 감지: {statistics.conflicts_detected}개 ({statistics.conflict_rate:.1f}%)")
    summary.append(f"충돌 해결: {statistics.conflicts_resolved}개 ({statistics.resolution_rate:.1f}%)")
    
    if statistics.conflicts_resolved > 0:
        summary.append(f"  - 건너뛴 파일: {statistics.files_skipped}개")
        summary.append(f"  - 덮어쓴 파일: {statistics.files_overwritten}개")
        summary.append(f"  - 이름 변경된 파일: {statistics.files_renamed}개")
    
    if statistics.processing_errors > 0:
        summary.append(f"처리 오류: {statistics.processing_errors}개")
    
    summary.append(f"성공률: {statistics.success_rate:.1f}%")
    summary.append(f"평균 처리 시간: {statistics.average_processing_time:.3f}초")
    
    # 가장 많이 사용된 정책
    most_used = statistics.get_most_used_policy()
    if most_used:
        usage_count = statistics.policy_usage[most_used]
        summary.append(f"가장 많이 사용된 정책: {most_used.value} ({usage_count}회)")
    
    return "\n".join(summary)


# 테스트 및 검증 함수들

def validate_conflict_handler_setup() -> bool:
    """
    FileConflictHandler의 기본 설정을 검증
    
    Returns:
        bool: 설정이 올바른 경우 True
    """
    try:
        # 기본 설정으로 핸들러 생성
        handler = create_conflict_handler()
        
        # 기본 설정 확인
        config = handler.get_config()
        if not isinstance(config.default_policy, FileConflictPolicy):
            return False
        
        # 통계 초기화 확인
        stats = handler.get_conflict_statistics()
        if stats.total_files_checked != 0:
            return False
        
        logger.info("FileConflictHandler 설정 검증 완료")
        return True
        
    except Exception as e:
        logger.error(f"FileConflictHandler 설정 검증 실패: {e}")
        return False


if __name__ == "__main__":
    # 기본 검증 실행
    if validate_conflict_handler_setup():
        print("✅ FileConflictHandler가 정상적으로 설정되었습니다.")
    else:
        print("❌ FileConflictHandler 설정에 문제가 있습니다.")
    
    # 간단한 사용 예시
    print("\n=== 사용 예시 ===")
    
    from pathlib import Path
    
    # 테스트용 임시 파일 생성 (실제로는 생성하지 않음)
    source_files = [
        Path("test1.docx"),
        Path("test2.pdf"),
        Path("test3.xlsx")
    ]
    
    # 충돌 처리 설정
    config = FileConflictConfig(
        default_policy=FileConflictPolicy.RENAME,
        auto_rename_pattern="{name}_{counter}{ext}",
        remember_choices=True
    )
    
    # 충돌 처리기 생성
    handler = create_conflict_handler(config)
    
    # 통계 출력
    stats = handler.get_conflict_statistics()
    print(get_conflict_summary(stats))
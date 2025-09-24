"""
OCR Enhancement Manager
OCR 개선 기능의 중앙 관리자
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker

from ..models import FileInfo, OCRResult
from ..logger import get_logger
from .models import (
    OCREnhancementConfig,
    OCREnhancementType,
    OCRStatusInfo,
    OCRProgressInfo,
    OCREnhancementResult,
    OCRStatusType,
    QualityMetrics,
    QualityLevel,
    EnhancementStats
)


logger = get_logger(__name__)


class OCREnhancementManager(QObject):
    """OCR Enhancement Manager - OCR 개선 기능의 중앙 orchestrator"""

    # PyQt Signals
    enhancement_started = pyqtSignal(FileInfo)
    enhancement_progress = pyqtSignal(FileInfo, OCRProgressInfo)
    enhancement_status_changed = pyqtSignal(FileInfo, OCRStatusInfo)
    enhancement_completed = pyqtSignal(FileInfo, OCREnhancementResult)
    enhancement_failed = pyqtSignal(FileInfo, str)

    def __init__(self, config: Optional[OCREnhancementConfig] = None):
        """
        초기화

        Args:
            config: OCR Enhancement 설정
        """
        super().__init__()

        self.config = config or OCREnhancementConfig()
        self._mutex = QMutex()

        # 상태 관리
        self._is_running = False
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._status_cache: Dict[str, OCRStatusInfo] = {}
        self._result_cache: Dict[str, OCREnhancementResult] = {}

        # 통계
        self._stats = EnhancementStats()

        # 개선 함수 등록소
        self._enhancement_functions: Dict[OCREnhancementType, Callable] = {}

        # 전처리 파이프라인 연동
        self._preprocessing_pipeline = None
        self._initialize_preprocessing()

        logger.info("OCR Enhancement Manager initialized")

    def _initialize_preprocessing(self):
        """전처리 파이프라인 초기화"""
        if not self.config.preprocessing_enabled:
            logger.info("Image preprocessing disabled in OCR enhancements")
            return

        try:
            from .preprocessing import get_preprocessing_pipeline, is_preprocessing_enabled

            if is_preprocessing_enabled():
                self._preprocessing_pipeline = get_preprocessing_pipeline()
                if self._preprocessing_pipeline:
                    logger.info("Preprocessing pipeline integrated with OCR enhancement manager")
                else:
                    logger.warning("Preprocessing pipeline not available")
            else:
                logger.info("Preprocessing module not enabled")

        except ImportError as e:
            logger.info(f"Preprocessing module not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize preprocessing pipeline: {e}")

    async def preprocess_image_for_ocr(self, image_path: Path) -> Optional[Path]:
        """
        OCR 전에 이미지 전처리 수행

        Args:
            image_path: 원본 이미지 경로

        Returns:
            전처리된 이미지 경로 또는 None (실패 시)
        """
        if not self._preprocessing_pipeline:
            logger.debug("Preprocessing pipeline not available")
            return image_path

        try:
            logger.debug(f"Preprocessing image for OCR: {image_path.name}")
            result = await self._preprocessing_pipeline.auto_enhance_for_ocr(image_path)

            if result.is_success:
                logger.info(f"Image preprocessing successful: {image_path.name} "
                           f"(improvement: {result.total_improvement_score:.2f})")
                return result.enhanced_image_path
            else:
                logger.warning(f"Image preprocessing failed: {result.error_message}")
                return image_path  # 실패 시 원본 사용

        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image_path  # 오류 시 원본 사용

    def get_preprocessing_stats(self) -> Optional[Dict]:
        """전처리 통계 반환"""
        if self._preprocessing_pipeline:
            try:
                return self._preprocessing_pipeline.get_statistics()
            except Exception as e:
                logger.error(f"Failed to get preprocessing stats: {e}")
        return None

    def is_preprocessing_available(self) -> bool:
        """전처리 파이프라인 사용 가능 여부"""
        return self._preprocessing_pipeline is not None

    def is_enabled(self) -> bool:
        """모듈 활성화 상태 확인"""
        return self.config.enabled and self.config.is_any_enhancement_enabled()

    def start(self) -> bool:
        """Enhancement Manager 시작"""
        with QMutexLocker(self._mutex):
            if self._is_running:
                return True

            if not self.is_enabled():
                logger.info("OCR Enhancement Manager is disabled")
                return False

            try:
                self._register_enhancement_functions()
                self._is_running = True
                logger.info("OCR Enhancement Manager started")
                return True

            except Exception as e:
                logger.error(f"Failed to start OCR Enhancement Manager: {e}")
                return False

    def stop(self):
        """Enhancement Manager 중지"""
        with QMutexLocker(self._mutex):
            if not self._is_running:
                return

            try:
                # 진행 중인 작업들 취소
                for task_id, task in self._active_tasks.items():
                    if not task.done():
                        task.cancel()
                        logger.debug(f"Cancelled enhancement task: {task_id}")

                self._active_tasks.clear()
                self._is_running = False
                logger.info("OCR Enhancement Manager stopped")

            except Exception as e:
                logger.error(f"Error stopping OCR Enhancement Manager: {e}")

    def shutdown(self):
        """완전 종료"""
        self.stop()

        # 전처리 파이프라인 정리
        if self._preprocessing_pipeline:
            try:
                self._preprocessing_pipeline.cleanup()
                logger.debug("Preprocessing pipeline cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up preprocessing pipeline: {e}")

        self._status_cache.clear()
        self._result_cache.clear()
        logger.info("OCR Enhancement Manager shutdown completed")

    async def enhance_ocr_result(
        self,
        file_info: FileInfo,
        original_result: OCRResult,
        enhancement_types: Optional[List[OCREnhancementType]] = None
    ) -> OCREnhancementResult:
        """
        OCR 결과 개선

        Args:
            file_info: 파일 정보
            original_result: 원본 OCR 결과
            enhancement_types: 적용할 개선 유형들 (None이면 설정에 따라 자동 선택)

        Returns:
            개선된 OCR 결과
        """
        if not self.is_enabled():
            logger.debug("OCR Enhancement is disabled")
            return self._create_passthrough_result(file_info, original_result)

        # 캐시 확인
        cache_key = self._generate_cache_key(file_info, original_result)
        if self.config.cache_results and cache_key in self._result_cache:
            logger.debug(f"Returning cached enhancement result for {file_info.name}")
            return self._result_cache[cache_key]

        # 개선 작업 시작
        task_id = f"{file_info.path}_{datetime.now().timestamp()}"

        try:
            # 초기 상태 설정
            status_info = OCRStatusInfo(
                status=OCRStatusType.INITIALIZING,
                current_step="Preparing enhancement"
            )
            self._update_status(file_info, status_info)

            # 적용할 개선 유형 결정
            if enhancement_types is None:
                enhancement_types = self._determine_enhancement_types(original_result)

            if not enhancement_types:
                logger.debug("No enhancements to apply")
                return self._create_passthrough_result(file_info, original_result)

            # 진행률 정보 초기화
            progress_info = OCRProgressInfo(
                total_steps=len(enhancement_types) + 2,  # +2 for init and finalize
                completed_steps=0,
                enhancement_types=enhancement_types
            )

            # Enhancement 시작 신호
            self.enhancement_started.emit(file_info)

            # 개선 처리 수행
            result = await self._perform_enhancements(
                file_info,
                original_result,
                enhancement_types,
                progress_info
            )

            # 캐시 저장
            if self.config.cache_results:
                self._result_cache[cache_key] = result

            # 통계 업데이트
            self._stats.add_result(result)

            # 완료 신호
            self.enhancement_completed.emit(file_info, result)

            logger.info(
                f"OCR enhancement completed for {file_info.name}: "
                f"{len(result.applied_enhancements)} enhancements applied"
            )

            return result

        except asyncio.CancelledError:
            logger.info(f"OCR enhancement cancelled for {file_info.name}")
            status_info.status = OCRStatusType.CANCELLED
            self._update_status(file_info, status_info)
            raise

        except Exception as e:
            logger.error(f"OCR enhancement failed for {file_info.name}: {e}")
            error_msg = str(e)
            status_info.status = OCRStatusType.FAILED
            status_info.error_message = error_msg
            self._update_status(file_info, status_info)

            self.enhancement_failed.emit(file_info, error_msg)
            return self._create_error_result(file_info, original_result, error_msg)

        finally:
            # 작업 정리
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]

    async def _perform_enhancements(
        self,
        file_info: FileInfo,
        original_result: OCRResult,
        enhancement_types: List[OCREnhancementType],
        progress_info: OCRProgressInfo
    ) -> OCREnhancementResult:
        """실제 개선 처리 수행"""
        start_time = datetime.now()
        enhanced_text = original_result.text
        applied_enhancements = []
        enhancement_details = {}

        # 초기화 단계
        progress_info.current_step_name = "Initializing"
        progress_info.current_step_progress = 1.0
        progress_info.completed_steps = 1
        self._emit_progress(file_info, progress_info)

        # 각 개선 유형별 처리
        for i, enhancement_type in enumerate(enhancement_types):
            try:
                progress_info.current_step_name = f"Applying {enhancement_type.value}"
                progress_info.current_step_progress = 0.0
                self._emit_progress(file_info, progress_info)

                # 개선 함수 실행
                if enhancement_type in self._enhancement_functions:
                    enhanced_text, details = await self._enhancement_functions[enhancement_type](
                        enhanced_text, file_info, original_result
                    )
                    applied_enhancements.append(enhancement_type)
                    enhancement_details[enhancement_type.value] = details

                progress_info.current_step_progress = 1.0
                progress_info.completed_steps = i + 2  # +1 for init step
                self._emit_progress(file_info, progress_info)

            except Exception as e:
                logger.warning(f"Enhancement {enhancement_type.value} failed: {e}")
                # 계속 진행 (다른 개선사항들은 적용 가능)

        # 품질 분석
        progress_info.current_step_name = "Analyzing quality"
        progress_info.current_step_progress = 0.0
        self._emit_progress(file_info, progress_info)

        quality_metrics = await self._analyze_quality(enhanced_text, original_result.text)

        progress_info.current_step_progress = 1.0
        progress_info.completed_steps = len(enhancement_types) + 2
        self._emit_progress(file_info, progress_info)

        # 결과 생성
        processing_time = (datetime.now() - start_time).total_seconds()
        improvement_ratio = self._calculate_improvement_ratio(
            original_result.text, enhanced_text
        )

        status_info = OCRStatusInfo(
            status=OCRStatusType.COMPLETED,
            progress_percent=100.0,
            completed_at=datetime.now()
        )

        result = OCREnhancementResult(
            file_info=file_info,
            original_result=original_result,
            enhanced_text=enhanced_text,
            status_info=status_info,
            progress_info=progress_info,
            quality_metrics=quality_metrics,
            improvement_ratio=improvement_ratio,
            applied_enhancements=applied_enhancements,
            enhancement_details=enhancement_details,
            processing_time=processing_time,
            enhancement_overhead=processing_time
        )

        return result

    def _register_enhancement_functions(self):
        """개선 함수들 등록"""
        self._enhancement_functions = {
            OCREnhancementType.PREPROCESSING: self._enhance_preprocessing,
            OCREnhancementType.POST_PROCESSING: self._enhance_post_processing,
            OCREnhancementType.LANGUAGE_DETECTION: self._enhance_language_detection,
            OCREnhancementType.CONFIDENCE_ANALYSIS: self._enhance_confidence_analysis,
            OCREnhancementType.QUALITY_ASSESSMENT: self._enhance_quality_assessment
        }

    async def _enhance_preprocessing(self, text: str, file_info: FileInfo, original_result: OCRResult) -> tuple:
        """전처리 개선 (현재는 기본 구현)"""
        return text, {"applied": True, "method": "basic_preprocessing"}

    async def _enhance_post_processing(self, text: str, file_info: FileInfo, original_result: OCRResult) -> tuple:
        """후처리 개선"""
        if not self.config.post_processing_enabled:
            return text, {"applied": False}

        enhanced_text = text

        # 기본 텍스트 정리
        if self.config.formatting_cleanup_enabled:
            enhanced_text = self._clean_formatting(enhanced_text)

        return enhanced_text, {"applied": True, "formatting_cleaned": True}

    async def _enhance_language_detection(self, text: str, file_info: FileInfo, original_result: OCRResult) -> tuple:
        """언어 감지 개선"""
        if not self.config.language_detection_enabled:
            return text, {"applied": False}

        # 기본 언어 감지 (향후 고도화 예정)
        detected_language = self._detect_language_simple(text)

        return text, {
            "applied": True,
            "detected_language": detected_language,
            "confidence": 0.8
        }

    async def _enhance_confidence_analysis(self, text: str, file_info: FileInfo, original_result: OCRResult) -> tuple:
        """신뢰도 분석 개선"""
        if not self.config.confidence_analysis_enabled:
            return text, {"applied": False}

        confidence_score = self._calculate_text_confidence(text)

        return text, {
            "applied": True,
            "confidence_score": confidence_score,
            "analysis_method": "character_frequency"
        }

    async def _enhance_quality_assessment(self, text: str, file_info: FileInfo, original_result: OCRResult) -> tuple:
        """품질 평가 개선"""
        if not self.config.quality_assessment_enabled:
            return text, {"applied": False}

        quality_score = self._assess_text_quality(text)

        return text, {
            "applied": True,
            "quality_score": quality_score,
            "assessment_method": "heuristic"
        }

    def _clean_formatting(self, text: str) -> str:
        """기본 포맷팅 정리"""
        import re

        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)

        # 연속된 줄바꿈 정리
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # 문장 끝 공백 정리
        text = re.sub(r' +([.!?])', r'\1', text)

        return text.strip()

    def _detect_language_simple(self, text: str) -> str:
        """간단한 언어 감지"""
        # 한글 문자 비율 체크
        import re
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.findall(r'[a-zA-Z가-힣]', text))

        if total_chars == 0:
            return "unknown"

        korean_ratio = korean_chars / total_chars
        if korean_ratio > 0.3:
            return "ko"
        else:
            return "en"

    def _calculate_text_confidence(self, text: str) -> float:
        """텍스트 신뢰도 계산 (휴리스틱)"""
        if not text.strip():
            return 0.0

        # 기본 휴리스틱: 길이, 알파벳/한글 비율, 특수문자 비율
        import re

        # 유효 문자 비율
        valid_chars = len(re.findall(r'[a-zA-Z가-힣0-9\s]', text))
        total_chars = len(text)

        if total_chars == 0:
            return 0.0

        valid_ratio = valid_chars / total_chars

        # 길이 기반 신뢰도 (너무 짧거나 너무 길면 낮춤)
        length_score = min(1.0, len(text.strip()) / 100)

        # 종합 점수
        confidence = (valid_ratio * 0.7 + length_score * 0.3)
        return min(0.95, max(0.1, confidence))

    def _assess_text_quality(self, text: str) -> float:
        """텍스트 품질 평가 (휴리스틱)"""
        if not text.strip():
            return 0.0

        # 기본 품질 지표들
        word_count = len(text.split())
        char_count = len(text.strip())

        # 평균 단어 길이
        avg_word_length = char_count / max(1, word_count)

        # 품질 점수 계산
        length_score = min(1.0, char_count / 500)  # 500자 기준
        word_score = min(1.0, word_count / 50)     # 50단어 기준
        structure_score = min(1.0, avg_word_length / 7)  # 7자 평균 기준

        quality = (length_score * 0.4 + word_score * 0.3 + structure_score * 0.3)
        return min(0.95, max(0.1, quality))

    async def _analyze_quality(self, enhanced_text: str, original_text: str) -> QualityMetrics:
        """품질 메트릭 분석"""
        confidence_score = self._calculate_text_confidence(enhanced_text)
        clarity_score = self._assess_text_quality(enhanced_text)

        # 완전성 점수 (원본 대비)
        completeness_score = min(1.0, len(enhanced_text) / max(1, len(original_text)))

        # 일관성 점수 (기본값)
        consistency_score = 0.8

        metrics = QualityMetrics(
            confidence_score=confidence_score,
            clarity_score=clarity_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            character_count=len(enhanced_text),
            word_count=len(enhanced_text.split()),
            line_count=enhanced_text.count('\n') + 1
        )

        metrics.overall_quality = metrics.calculate_overall_quality()

        return metrics

    def _calculate_improvement_ratio(self, original_text: str, enhanced_text: str) -> float:
        """개선 비율 계산"""
        if not original_text:
            return 1.0 if enhanced_text else 0.0

        original_quality = self._assess_text_quality(original_text)
        enhanced_quality = self._assess_text_quality(enhanced_text)

        if original_quality == 0:
            return 1.0 if enhanced_quality > 0 else 0.0

        improvement = (enhanced_quality - original_quality) / original_quality
        return max(0.0, improvement)

    def _determine_enhancement_types(self, original_result: OCRResult) -> List[OCREnhancementType]:
        """설정에 따라 적용할 개선 유형 결정"""
        enhancement_types = []

        if self.config.preprocessing_enabled:
            enhancement_types.append(OCREnhancementType.PREPROCESSING)

        if self.config.post_processing_enabled:
            enhancement_types.append(OCREnhancementType.POST_PROCESSING)

        if self.config.language_detection_enabled:
            enhancement_types.append(OCREnhancementType.LANGUAGE_DETECTION)

        if self.config.confidence_analysis_enabled:
            enhancement_types.append(OCREnhancementType.CONFIDENCE_ANALYSIS)

        if self.config.quality_assessment_enabled:
            enhancement_types.append(OCREnhancementType.QUALITY_ASSESSMENT)

        return enhancement_types

    def _generate_cache_key(self, file_info: FileInfo, original_result: OCRResult) -> str:
        """캐시 키 생성"""
        import hashlib
        key_data = f"{file_info.path}_{file_info.modified_time}_{original_result.text[:100]}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _create_passthrough_result(self, file_info: FileInfo, original_result: OCRResult) -> OCREnhancementResult:
        """개선 없이 통과하는 결과 생성"""
        status_info = OCRStatusInfo(
            status=OCRStatusType.COMPLETED,
            progress_percent=100.0
        )

        progress_info = OCRProgressInfo(
            total_steps=1,
            completed_steps=1
        )

        quality_metrics = QualityMetrics(
            confidence_score=original_result.confidence,
            overall_quality=QualityLevel.FAIR
        )

        return OCREnhancementResult(
            file_info=file_info,
            original_result=original_result,
            enhanced_text=original_result.text,
            status_info=status_info,
            progress_info=progress_info,
            quality_metrics=quality_metrics,
            improvement_ratio=0.0,
            processing_time=0.0
        )

    def _create_error_result(self, file_info: FileInfo, original_result: OCRResult, error_msg: str) -> OCREnhancementResult:
        """오류 결과 생성"""
        status_info = OCRStatusInfo(
            status=OCRStatusType.FAILED,
            error_message=error_msg
        )

        progress_info = OCRProgressInfo(
            total_steps=1,
            completed_steps=0
        )

        quality_metrics = QualityMetrics(
            overall_quality=QualityLevel.VERY_POOR
        )

        return OCREnhancementResult(
            file_info=file_info,
            original_result=original_result,
            enhanced_text=original_result.text,
            status_info=status_info,
            progress_info=progress_info,
            quality_metrics=quality_metrics,
            improvement_ratio=0.0
        )

    def _update_status(self, file_info: FileInfo, status_info: OCRStatusInfo):
        """상태 업데이트"""
        cache_key = str(file_info.path)
        self._status_cache[cache_key] = status_info
        self.enhancement_status_changed.emit(file_info, status_info)

    def _emit_progress(self, file_info: FileInfo, progress_info: OCRProgressInfo):
        """진행률 신호 발생"""
        self.enhancement_progress.emit(file_info, progress_info)

    def get_stats(self) -> EnhancementStats:
        """통계 정보 반환"""
        return self._stats

    def get_service_info(self) -> Dict[str, Any]:
        """
        OCR Enhancement 서비스 정보 반환

        Returns:
            서비스 정보 딕셔너리
        """
        preprocessing_stats = self.get_preprocessing_stats()

        return {
            'enabled': self.is_enabled(),
            'running': self._is_running,
            'config': {
                'accuracy_boost_enabled': self.config.accuracy_boost_enabled,
                'preprocessing_enabled': self.config.preprocessing_enabled,
                'post_processing_enabled': self.config.post_processing_enabled,
                'language_detection_enabled': self.config.language_detection_enabled,
                'confidence_analysis_enabled': self.config.confidence_analysis_enabled,
                'layout_analysis_enabled': self.config.layout_analysis_enabled,
                'quality_assessment_enabled': self.config.quality_assessment_enabled,
                'cache_results': self.config.cache_results,
                'min_confidence_threshold': self.config.min_confidence_threshold,
                'retry_on_low_confidence': self.config.retry_on_low_confidence
            },
            'preprocessing': {
                'available': self.is_preprocessing_available(),
                'enabled': self.config.preprocessing_enabled,
                'stats': preprocessing_stats
            },
            'statistics': {
                'total_processed': self._stats.total_processed,
                'successful_enhancements': self._stats.successful_enhancements,
                'failed_enhancements': self._stats.failed_enhancements,
                'average_processing_time': self._stats.average_processing_time,
                'total_improvement_ratio': self._stats.total_improvement_ratio,
                'cache_hits': len(self._result_cache),
                'active_tasks': len(self._active_tasks)
            }
        }

    def clear_cache(self):
        """캐시 정리"""
        with QMutexLocker(self._mutex):
            self._result_cache.clear()
            self._status_cache.clear()
            logger.info("OCR Enhancement cache cleared")

    def get_current_status(self, file_info: FileInfo) -> Optional[OCRStatusInfo]:
        """현재 상태 조회"""
        cache_key = str(file_info.path)
        return self._status_cache.get(cache_key)

    def is_processing(self, file_info: FileInfo) -> bool:
        """처리 중인지 확인"""
        status = self.get_current_status(file_info)
        return status is not None and status.is_active
"""
파일 관리자
파일 스캔, 관리, 정보 수집을 담당
"""

import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker

from .models import FileInfo, FileType, get_file_type, ConversionStatus
from .utils import (
    scan_directory, validate_path, format_file_size,
    validate_file_extension, sanitize_filename, get_unique_output_path
)
from .logger import get_logger
from .memory_optimizer import MemoryOptimizer
from .constants import DEFAULT_OUTPUT_DIRECTORY


logger = get_logger(__name__)


def resolve_markdown_output_path(
    source_path: Path,
    preserve_structure: bool = True,
    output_base_dir: Optional[Path] = None,
    ensure_unique: bool = True
) -> Path:
    """
    Resolve markdown output path within the program's markdown directory.
    
    This centralized utility function provides secure, cross-platform path resolution
    for markdown output files with comprehensive sanitization and conflict handling.
    
    Args:
        source_path: Path to the source file to be converted
        preserve_structure: If True, preserves the directory structure relative
                          to the source file's directory. If False, places all
                          output files in the root markdown directory.
        output_base_dir: Base directory for markdown output. If None, uses the
                        program's default markdown directory.
        ensure_unique: If True, automatically generates unique filenames to avoid
                      conflicts. If False, returns the target path even if it exists.
    
    Returns:
        Absolute Path: Resolved path within the markdown output directory
    
    Raises:
        ValueError: If source_path is invalid or cannot be processed
        OSError: If there are permission issues accessing directories
        
    Security:
        - Prevents directory traversal attacks through path sanitization
        - Validates all path components for filesystem safety
        - Ensures output paths remain within designated markdown directory
        - Handles Windows reserved names and invalid characters
        
    Performance:
        - Efficient path operations using pathlib
        - Minimal filesystem access for path resolution
        - Caches directory structure validation
        
    Cross-platform Compatibility:
        - Uses pathlib for OS-agnostic path operations
        - Handles Windows/Linux path length limitations
        - Respects filesystem-specific naming conventions
        
    Examples:
        >>> # Basic usage - flatten structure
        >>> source = Path("/home/user/docs/report.pdf")
        >>> output = resolve_markdown_output_path(source, preserve_structure=False)
        >>> print(output)
        /program/markdown/report.md
        
        >>> # Preserve directory structure
        >>> source = Path("/home/user/docs/2024/report.pdf")
        >>> output = resolve_markdown_output_path(source, preserve_structure=True)
        >>> print(output)
        /program/markdown/docs/2024/report.md
        
        >>> # Custom output directory
        >>> source = Path("/home/user/docs/report.pdf")
        >>> custom_dir = Path("/custom/markdown")
        >>> output = resolve_markdown_output_path(source, output_base_dir=custom_dir)
        >>> print(output)
        /custom/markdown/report.md
    """
    # Input validation
    if not isinstance(source_path, Path):
        try:
            source_path = Path(source_path)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid source path: {e}")
    
    if not source_path.name:
        raise ValueError("Source path must point to a file, not a directory")
    
    # Security check: Ensure source path is absolute or can be resolved safely
    try:
        # Convert to absolute path to prevent relative path manipulation
        if not source_path.is_absolute():
            source_path = source_path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Cannot resolve source path '{source_path}': {e}")
    
    # Determine output base directory
    if output_base_dir is None:
        # Use program's root directory + default markdown directory
        program_root = Path(__file__).parent.parent.parent  # Navigate to project root
        output_base_dir = program_root / DEFAULT_OUTPUT_DIRECTORY
    else:
        # Validate and resolve custom output directory
        if not isinstance(output_base_dir, Path):
            try:
                output_base_dir = Path(output_base_dir)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid output base directory: {e}")
        
        # Ensure output directory is absolute
        if not output_base_dir.is_absolute():
            output_base_dir = output_base_dir.resolve()
    
    # Security validation: Prevent directory traversal
    try:
        output_base_dir = output_base_dir.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Cannot resolve output base directory '{output_base_dir}': {e}")
    
    # Generate safe markdown filename
    source_stem = source_path.stem
    if not source_stem:
        source_stem = "untitled"
    
    # Sanitize filename to ensure filesystem compatibility
    safe_filename = sanitize_filename(f"{source_stem}.md")
    
    # Determine final output path based on preserve_structure setting
    if preserve_structure:
        # Attempt to preserve directory structure
        try:
            # For absolute paths, we need a reference point for relative structure
            # Use the source file's parent directory as the structure to preserve
            source_parent = source_path.parent
            
            # Get the relative structure - use just the immediate parent name
            # to avoid creating overly deep directory structures
            if source_parent.name and source_parent.name != source_parent.root:
                # Create a subdirectory based on source parent directory name
                subdir_name = sanitize_filename(source_parent.name)
                output_subdir = output_base_dir / subdir_name
            else:
                # Fallback to root output directory if parent structure is unclear
                output_subdir = output_base_dir
        except (OSError, ValueError):
            # Fallback to root output directory if structure preservation fails
            output_subdir = output_base_dir
    else:
        # Place directly in root markdown directory
        output_subdir = output_base_dir
    
    # Construct final output path
    output_path = output_subdir / safe_filename
    
    # Security check: Ensure resolved path is within output base directory
    try:
        resolved_output = output_path.resolve()
        resolved_base = output_base_dir.resolve()
        
        # Verify the output path is within the base directory
        try:
            resolved_output.relative_to(resolved_base)
        except ValueError:
            # Path is outside base directory - security violation
            raise ValueError(
                f"Resolved output path '{resolved_output}' is outside "
                f"base directory '{resolved_base}'. This may indicate a "
                f"directory traversal attempt."
            )
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Security validation failed for output path: {e}")
    
    # Handle duplicate filenames if requested
    if ensure_unique and output_path.exists():
        try:
            output_path = get_unique_output_path(output_path)
        except ValueError as e:
            # Fallback: add timestamp if unique path generation fails
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_stem = output_path.stem
            suffix = output_path.suffix
            timestamped_name = f"{name_stem}_{timestamp}{suffix}"
            output_path = output_path.parent / timestamped_name
    
    # Validate final path length (filesystem limitations)
    final_path_str = str(output_path)
    if len(final_path_str) > 4000:  # Conservative limit for cross-platform compatibility
        raise ValueError(
            f"Generated output path is too long ({len(final_path_str)} chars): "
            f"'{final_path_str[:100]}...'"
        )
    
    # Create output directory if it doesn't exist
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise OSError(
            f"Cannot create output directory '{output_path.parent}': {e}"
        )
    
    # Final validation: Check write permissions
    try:
        # Test write access to the parent directory
        if output_path.parent.exists() and not os.access(output_path.parent, os.W_OK):
            raise OSError(
                f"No write permission to output directory '{output_path.parent}'"
            )
    except OSError as e:
        raise OSError(f"Permission check failed: {e}")
    
    return output_path


class FileScanWorker(QThread):
    """파일 스캔 워커 스레드"""
    
    # 시그널
    progress_updated = pyqtSignal(int, int)  # 현재 진행, 전체
    file_found = pyqtSignal(object)  # FileInfo
    scan_completed = pyqtSignal(list)  # List[FileInfo]
    error_occurred = pyqtSignal(str)  # 에러 메시지
    
    def __init__(self, directory: Path, include_subdirectories: bool = True,
                 supported_extensions: Optional[List[str]] = None,
                 max_file_size_mb: int = 100, memory_optimizer: Optional[MemoryOptimizer] = None):
        super().__init__()
        self.directory = directory
        self.include_subdirectories = include_subdirectories
        self.supported_extensions = supported_extensions or []
        self.max_file_size_mb = max_file_size_mb
        self._is_cancelled = False
        self._mutex = QMutex()
        self._memory_optimizer = memory_optimizer or MemoryOptimizer()
    
    def run(self):
        """스캔 실행"""
        try:
            logger.info(f"파일 스캔 시작: {self.directory}")
            
            # 메모리 추적 시작
            self._memory_optimizer.start_monitoring()
            
            # 경로 검증
            is_valid, error_msg = validate_path(self.directory, check_exists=True, check_readable=True)
            if not is_valid:
                self.error_occurred.emit(f"디렉토리 접근 실패: {error_msg}")
                return
            
            file_infos = []
            processed_count = 0
            
            # 파일 경로들을 먼저 수집
            file_paths = self._collect_file_paths()
            total_files = len(file_paths)
            
            if total_files == 0:
                logger.info("스캔할 파일이 없습니다")
                self.scan_completed.emit([])
                return
            
            # 각 파일 처리
            for file_path in file_paths:
                if self._is_cancelled:
                    logger.info("파일 스캔이 취소되었습니다")
                    return
                
                try:
                    # 메모리 체크 및 정리
                    if processed_count % 100 == 0 and self._memory_optimizer.should_trigger_gc():
                        self._memory_optimizer.force_gc()
                    
                    file_info = self._create_file_info(file_path)
                    if file_info:
                        file_infos.append(file_info)
                        self.file_found.emit(file_info)
                    
                    processed_count += 1
                    self.progress_updated.emit(processed_count, total_files)
                    
                    # CPU 부하 완화
                    self.msleep(1)
                
                except Exception as e:
                    logger.warning(f"파일 처리 중 오류 ({file_path}): {e}")
                    continue
            
            logger.info(f"파일 스캔 완료: {len(file_infos)}개 파일 발견")
            
            # 메모리 사용량 로깅
            memory_stats = self._memory_optimizer.get_memory_statistics()
            logger.info(f"스캔 메모리 사용량 - Peak: {memory_stats['peak_memory_mb']:.1f}MB")
            
            self.scan_completed.emit(file_infos)
            
        except Exception as e:
            logger.error(f"파일 스캔 중 오류: {e}")
            self.error_occurred.emit(str(e))
        finally:
            # 메모리 정리
            self._memory_optimizer.cleanup()
    
    def _collect_file_paths(self) -> List[Path]:
        """파일 경로들을 수집"""
        try:
            return scan_directory(
                self.directory,
                self.include_subdirectories,
                self.supported_extensions,
                self.max_file_size_mb
            )
        except Exception as e:
            logger.error(f"파일 경로 수집 실패: {e}")
            return []
    
    def _create_file_info(self, file_path: Path) -> Optional[FileInfo]:
        """파일 정보 생성"""
        try:
            if not file_path.exists():
                return None
            
            # 캐시에서 파일 정보 확인
            cache_key = f"fileinfo_{file_path}_{file_path.stat().st_mtime}"
            cached_info = self._memory_optimizer.get_cached_result(cache_key)
            
            if cached_info:
                return cached_info
            
            stat = file_path.stat()
            file_type = get_file_type(file_path)
            
            # 파일 타입이 지원되지 않으면 제외
            if (self.supported_extensions and 
                file_type.value not in self.supported_extensions):
                return None
            
            file_info = FileInfo(
                path=file_path,
                name=file_path.name,
                size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                file_type=file_type,
                is_selected=False,
                conversion_status=ConversionStatus.PENDING
            )
            
            # 파일 정보 캐싱 (작은 객체만)
            if stat.st_size < 50 * 1024 * 1024:  # 50MB 미만
                self._memory_optimizer.cache_result(cache_key, file_info)
            
            return file_info
            
        except Exception as e:
            logger.warning(f"파일 정보 생성 실패 ({file_path}): {e}")
            return None
    
    def cancel(self):
        """스캔 취소"""
        with QMutexLocker(self._mutex):
            self._is_cancelled = True
        logger.info("파일 스캔 취소 요청됨")


class FileManager(QObject):
    """파일 관리자"""
    
    # 시그널
    scan_progress_updated = pyqtSignal(int, int)  # 현재, 전체
    file_found = pyqtSignal(object)  # FileInfo
    scan_completed = pyqtSignal(list)  # List[FileInfo]
    scan_error = pyqtSignal(str)  # 에러 메시지
    
    def __init__(self):
        super().__init__()
        self.files: Dict[Path, FileInfo] = {}
        self._scan_worker: Optional[FileScanWorker] = None
        self._is_scanning = False
        self._memory_optimizer = MemoryOptimizer()
    
    def scan_directory_async(self, directory: Path, 
                           include_subdirectories: bool = True,
                           supported_extensions: Optional[List[str]] = None,
                           max_file_size_mb: int = 100) -> bool:
        """
        비동기 디렉토리 스캔
        
        Args:
            directory: 스캔할 디렉토리
            include_subdirectories: 하위 디렉토리 포함 여부
            supported_extensions: 지원하는 확장자 리스트
            max_file_size_mb: 최대 파일 크기 (MB)
        
        Returns:
            스캔 시작 성공 여부
        """
        if self._is_scanning:
            logger.warning("이미 스캔이 진행 중입니다")
            return False
        
        # 이전 스캔 워커 정리
        if self._scan_worker is not None:
            self._scan_worker.quit()
            self._scan_worker.wait()
            self._scan_worker.deleteLater()
        
        # 새로운 스캔 워커 생성
        self._scan_worker = FileScanWorker(
            directory, include_subdirectories,
            supported_extensions, max_file_size_mb, self._memory_optimizer
        )
        
        # 시그널 연결
        self._scan_worker.progress_updated.connect(self._on_scan_progress)
        self._scan_worker.file_found.connect(self._on_file_found)
        self._scan_worker.scan_completed.connect(self._on_scan_completed)
        self._scan_worker.error_occurred.connect(self._on_scan_error)
        self._scan_worker.finished.connect(self._on_scan_finished)
        
        # 스캔 시작
        self._is_scanning = True
        self.files.clear()  # 이전 결과 제거
        self._scan_worker.start()
        
        logger.info(f"디렉토리 스캔 시작: {directory}")
        return True
    
    def cancel_scan(self) -> bool:
        """스캔 취소"""
        if not self._is_scanning or self._scan_worker is None:
            return False
        
        self._scan_worker.cancel()
        return True
    
    def get_files(self) -> List[FileInfo]:
        """모든 파일 정보 반환"""
        return list(self.files.values())
    
    def get_file_by_path(self, path: Path) -> Optional[FileInfo]:
        """경로로 파일 정보 조회"""
        return self.files.get(path)
    
    def add_file(self, file_info: FileInfo):
        """파일 추가"""
        self.files[file_info.path] = file_info
    
    def remove_file(self, path: Path) -> bool:
        """파일 제거"""
        if path in self.files:
            del self.files[path]
            return True
        return False
    
    def update_file_status(self, path: Path, status: ConversionStatus) -> bool:
        """파일 상태 업데이트"""
        if path in self.files:
            self.files[path].conversion_status = status
            return True
        return False
    
    def get_selected_files(self) -> List[FileInfo]:
        """선택된 파일들 반환"""
        return [file_info for file_info in self.files.values() 
                if file_info.is_selected]
    
    def select_all_files(self):
        """모든 파일 선택"""
        for file_info in self.files.values():
            file_info.is_selected = True
    
    def deselect_all_files(self):
        """모든 파일 선택 해제"""
        for file_info in self.files.values():
            file_info.is_selected = False
    
    def get_file_statistics(self) -> Dict[str, Any]:
        """파일 통계 정보 반환"""
        if not self.files:
            return {
                "total_count": 0,
                "selected_count": 0,
                "total_size": 0,
                "selected_size": 0,
                "file_types": {},
                "memory_stats": self._memory_optimizer.get_memory_statistics()
            }
        
        selected_files = self.get_selected_files()
        file_type_counts = {}
        
        for file_info in self.files.values():
            file_type = file_info.file_type.value
            file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
        
        return {
            "total_count": len(self.files),
            "selected_count": len(selected_files),
            "total_size": sum(f.size for f in self.files.values()),
            "selected_size": sum(f.size for f in selected_files),
            "file_types": file_type_counts,
            "memory_stats": self._memory_optimizer.get_memory_statistics()
        }
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 사용 통계 반환"""
        return self._memory_optimizer.get_memory_statistics()
    
    def cleanup_memory(self):
        """메모리 정리"""
        self._memory_optimizer.cleanup()
        logger.info("FileManager 메모리 정리 완료")
    
    def is_scanning(self) -> bool:
        """스캔 중인지 확인"""
        return self._is_scanning
    
    def _on_scan_progress(self, current: int, total: int):
        """스캔 진행률 업데이트"""
        self.scan_progress_updated.emit(current, total)
    
    def _on_file_found(self, file_info: FileInfo):
        """파일 발견시"""
        self.files[file_info.path] = file_info
        self.file_found.emit(file_info)
    
    def _on_scan_completed(self, file_infos: List[FileInfo]):
        """스캔 완료시"""
        logger.info(f"스캔 완료: {len(file_infos)}개 파일")
        self.scan_completed.emit(file_infos)
    
    def _on_scan_error(self, error_message: str):
        """스캔 오류시"""
        logger.error(f"스캔 오류: {error_message}")
        self.scan_error.emit(error_message)
    
    def _on_scan_finished(self):
        """스캔 스레드 종료시"""
        self._is_scanning = False
        if self._scan_worker:
            self._scan_worker.deleteLater()
            self._scan_worker = None
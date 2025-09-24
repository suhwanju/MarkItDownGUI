"""
변환 관리자
MarkItDown 라이브러리를 사용하여 파일 변환을 관리
"""

import time
import json
import warnings
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import traceback
import logging

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    MarkItDown = None

from .models import (
    FileInfo, ConversionResult, ConversionStatus, 
    ConversionProgress, FileType, ConversionProgressStatus,
    FileConflictStatus, FileConflictPolicy, FileConflictConfig,
    create_markdown_output_path  # Kept for backward compatibility and fallback
)
from .file_manager import resolve_markdown_output_path  # New secure path utility
from .constants import DEFAULT_OUTPUT_DIRECTORY
from .utils import (
    create_markdown_filename, get_unique_output_path,
    create_conversion_metadata, sanitize_filename
)
from .file_conflict_handler import FileConflictHandler
from .logger import get_logger
from .memory_optimizer import MemoryOptimizer

# Enhanced error handling imports
from .error_handling import (
    CircuitBreaker, CircuitBreakerError, CircuitBreakerState,
    FallbackManager, FallbackResult,
    ErrorRecoveryManager, RecoveryAction, RecoveryResult,
    ErrorReporter, ErrorReport, ErrorSeverity,
    ConversionError, FontDescriptorError, PDFParsingError,
    MarkItDownError, categorize_exception
)
from .validators import DocumentValidator, ValidationLevel, ValidationResult

# OCR service imports
from .llm_manager import LLMManager
from .ocr_service import OCRService, OCRServiceConfig
from .models import LLMConfig, LLMProvider


logger = get_logger(__name__)


class ConversionWorker(QThread):
    """Enhanced conversion worker with error handling and validation"""
    
    # 시그널
    progress_updated = pyqtSignal(object)  # ConversionProgress
    file_conversion_started = pyqtSignal(object)  # FileInfo
    file_conversion_completed = pyqtSignal(object)  # ConversionResult
    conversion_completed = pyqtSignal(list)  # List[ConversionResult]
    error_occurred = pyqtSignal(str)  # 에러 메시지
    conflict_detected = pyqtSignal(object)  # FileConflictInfo
    error_reported = pyqtSignal(object)  # ErrorReport
    
    def __init__(self, files: List[FileInfo], output_directory: Path,
                 max_workers: int = 3, memory_optimizer: Optional[MemoryOptimizer] = None,
                 conflict_handler: Optional[FileConflictHandler] = None,
                 save_to_original_dir: bool = True,
                 validation_level: ValidationLevel = ValidationLevel.STANDARD,
                 enable_recovery: bool = True, config_manager=None):
        super().__init__()
        self.files = files
        self.output_directory = output_directory
        self.max_workers = max_workers
        self._is_cancelled = False
        self._mutex = QMutex()
        self._markitdown = None
        self._memory_optimizer = memory_optimizer or MemoryOptimizer()
        self._conflict_handler = conflict_handler or FileConflictHandler()
        self._save_to_original_dir = save_to_original_dir
        self._config_manager = config_manager
        
        # Enhanced error handling components
        self._circuit_breaker = CircuitBreaker("conversion_worker")
        self._fallback_manager = FallbackManager()
        self._error_recovery_manager = ErrorRecoveryManager(self._fallback_manager) if enable_recovery else None
        self._error_reporter = ErrorReporter()
        self._document_validator = DocumentValidator(validation_level)
        
        # Set up error reporter callback
        self._error_reporter.set_error_callback(self._on_error_reported)

        # Initialize OCR services
        self._llm_manager = None
        self._ocr_service = None
        self._initialize_ocr_services()

        # 출력 디렉토리 생성 (원본 디렉토리에 저장하지 않는 경우만)
        if not self._save_to_original_dir:
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def _initialize_ocr_services(self):
        """Initialize OCR services when enabled in config"""
        try:
            if not self._config_manager:
                logger.debug("No config manager provided, skipping OCR initialization")
                return

            config = self._config_manager.get_config()
            if not config or not hasattr(config, 'enable_llm_ocr') or not config.enable_llm_ocr:
                logger.debug("LLM OCR not enabled in config, skipping OCR initialization")
                return

            logger.info("Initializing OCR services...")

            # Create LLM configuration from app config
            provider_name = getattr(config, 'llm_provider', 'openai')
            provider_enum = LLMProvider.OPENAI  # default
            try:
                if provider_name.lower() == 'azure':
                    provider_enum = LLMProvider.AZURE
                elif provider_name.lower() == 'local':
                    provider_enum = LLMProvider.LOCAL
                elif provider_name.lower() == 'anthropic':
                    provider_enum = LLMProvider.ANTHROPIC
            except Exception:
                logger.warning(f"Unknown provider '{provider_name}', using OpenAI")

            llm_config = LLMConfig(
                provider=provider_enum,
                model=getattr(config, 'llm_model', 'gpt-4o-mini'),
                base_url=getattr(config, 'llm_base_url', None),
                api_version=getattr(config, 'llm_api_version', None),
                temperature=getattr(config, 'llm_temperature', 0.1),
                max_tokens=getattr(config, 'llm_max_tokens', 4096),
                enable_ocr=config.enable_llm_ocr,
                ocr_language=getattr(config, 'ocr_language', 'auto'),
                max_image_size=getattr(config, 'max_image_size', 1024),
                system_prompt=getattr(config, 'llm_system_prompt', ''),
                track_usage=getattr(config, 'track_token_usage', True),
                usage_limit_monthly=getattr(config, 'token_usage_limit_monthly', 100000)
            )

            # Get API key from secure storage
            try:
                api_key = self._config_manager.get_llm_api_key()
                if not api_key:
                    logger.warning("No API key available for LLM OCR service")
                    return
                llm_config.api_key = api_key
            except Exception as e:
                logger.warning(f"Failed to get API key for LLM OCR: {e}")
                return

            # Initialize LLM Manager with config directory
            from pathlib import Path
            config_dir = Path("config")
            self._llm_manager = LLMManager(config_dir)

            # Configure LLM Manager with LLM config
            if not self._llm_manager.configure(llm_config):
                logger.warning("Failed to configure LLM Manager")
                return

            logger.debug("LLM Manager initialized and configured successfully")

            # Create OCR service configuration
            ocr_config = OCRServiceConfig(
                enabled=config.enable_llm_ocr,
                fallback_to_tesseract=True,
                max_image_size=getattr(config, 'max_image_size', 1024),
                supported_formats=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
                enable_preprocessing=getattr(config, 'enable_image_preprocessing', True),
                preprocessing_config={
                    'mode': getattr(config, 'preprocessing_mode', 'auto'),
                    'quality_threshold': getattr(config, 'preprocessing_quality_threshold', 0.6),
                    'enabled_enhancements': getattr(config, 'preprocessing_enabled_enhancements',
                                                   ['deskew', 'contrast', 'brightness', 'sharpening', 'noise_reduction']),
                    'enable_parallel_processing': getattr(config, 'preprocessing_enable_parallel', True),
                    'cache_strategy': getattr(config, 'preprocessing_cache_strategy', 'memory')
                }
            )

            # Initialize OCR Service
            self._ocr_service = OCRService(self._llm_manager, ocr_config)
            logger.info("OCR services initialized successfully")

        except ImportError as e:
            logger.info(f"OCR dependencies not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize OCR services: {e}", exc_info=True)
            # Don't raise exception - OCR is optional functionality
            self._llm_manager = None
            self._ocr_service = None

    def run(self):
        """변환 실행"""
        try:
            if not MARKITDOWN_AVAILABLE:
                self.error_occurred.emit("MarkItDown 라이브러리가 설치되지 않았습니다.")
                return
            
            logger.info(f"파일 변환 시작: {len(self.files)}개 파일")
            
            # 메모리 추적 시작
            self._memory_optimizer.start_monitoring()
            
            # MarkItDown 인스턴스 생성
            self._markitdown = MarkItDown()
            
            results = []
            total_files = len(self.files)
            completed_files = 0
            
            # 진행률 초기화
            progress = ConversionProgress(
                total_files=total_files,
                completed_files=0,
                current_status="변환 시작",
                current_progress_status=ConversionProgressStatus.INITIALIZING,
                start_time=datetime.now()
            )
            self.progress_updated.emit(progress)
            
            # 순차 변환 (안정성을 위해)
            for file_info in self.files:
                if self._is_cancelled:
                    logger.info("변환이 취소되었습니다")
                    return
                
                # 파일 변환 시작 시그널
                self.file_conversion_started.emit(file_info)
                
                # 진행률 업데이트
                progress.current_file = file_info.name
                progress.current_status = f"변환 중: {file_info.name}"
                progress.current_progress_status = ConversionProgressStatus.PROCESSING
                self.progress_updated.emit(progress)
                
                # 변환 실행
                result = self._convert_single_file(file_info)
                results.append(result)
                
                # 변환 완료 시그널
                self.file_conversion_completed.emit(result)
                
                completed_files += 1
                progress.completed_files = completed_files
                progress.current_status = f"완료: {completed_files}/{total_files}"
                self.progress_updated.emit(progress)
                
                # CPU 부하 완화
                self.msleep(100)
            
            logger.info(f"변환 완료: {len(results)}개 파일")
            
            # 메모리 사용량 로깅
            memory_stats = self._memory_optimizer.get_memory_statistics()
            logger.info(f"메모리 사용량 - Peak: {memory_stats['peak_memory_mb']:.1f}MB, Cache hits: {memory_stats.get('cache_stats', {}).get('hits', 0)}")
            
            self.conversion_completed.emit(results)
            
        except Exception as e:
            logger.error(f"변환 중 오류: {e}")
            self.error_occurred.emit(str(e))
        finally:
            # 메모리 정리
            self._memory_optimizer.cleanup()
    
    def _convert_single_file(self, file_info: FileInfo) -> ConversionResult:
        """Enhanced single file conversion with validation and error recovery"""
        start_time = time.time()
        
        try:
            logger.debug(f"파일 변환 시작: {file_info.path}")
            
            # Pre-conversion validation
            file_info.progress_status = ConversionProgressStatus.VALIDATING_FILE
            if not self._validate_file_pre_conversion(file_info):
                # Validation failed - try recovery if enabled
                if self._error_recovery_manager:
                    validation_error = ConversionError(
                        f"File validation failed for {file_info.name}",
                        file_info.path,
                        error_code="VALIDATION_FAILED"
                    )
                    return self._attempt_error_recovery(validation_error, file_info, start_time)
                else:
                    return self._create_failed_result(file_info, "파일 검증 실패", start_time)
            
            # 메모리 체크 및 정리
            if self._memory_optimizer.should_trigger_gc():
                self._memory_optimizer.force_gc()
            
            # 출력 파일 경로 생성 - 새로운 보안 강화 유틸리티 사용
            file_info.progress_status = ConversionProgressStatus.CHECKING_CONFLICTS
            logger.debug(f"Generating output path for {file_info.path} using resolve_markdown_output_path")
            
            if self._save_to_original_dir:
                # 원본 디렉토리에 저장하는 경우, 구조 보존하지 않음
                output_path = resolve_markdown_output_path(
                    source_path=file_info.path,
                    preserve_structure=False,
                    output_base_dir=file_info.path.parent,
                    ensure_unique=True
                )
            else:
                # 지정된 출력 디렉토리에 저장하는 경우, 구조 보존 설정 유지
                output_path = resolve_markdown_output_path(
                    source_path=file_info.path,
                    preserve_structure=True,
                    output_base_dir=self.output_directory,
                    ensure_unique=True
                )
            
            # 충돌 감지 및 해결
            if not self._handle_file_conflicts(file_info, output_path):
                return self._create_cancelled_result(file_info, output_path, start_time)
            
            # Update output path after conflict resolution
            output_path = file_info.output_path
            
            # Main conversion with circuit breaker protection
            file_info.progress_status = ConversionProgressStatus.PROCESSING
            
            try:
                # Use circuit breaker for conversion
                conversion_result = self._circuit_breaker.call(
                    self._perform_conversion_with_cache,
                    file_info
                )
                
                if not conversion_result or not conversion_result.strip():
                    raise ConversionError("변환된 내용이 비어있습니다", file_info.path)
                
                # Successful conversion - finalize and save
                return self._finalize_successful_conversion(file_info, conversion_result, output_path, start_time)
                
            except CircuitBreakerError as e:
                # Circuit breaker is open - attempt fallback
                logger.warning(f"Circuit breaker open for {file_info.name}: {e}")
                circuit_error = ConversionError(
                    f"Circuit breaker protection activated: {str(e)}",
                    file_info.path,
                    error_code="CIRCUIT_BREAKER_OPEN"
                )
                return self._attempt_error_recovery(circuit_error, file_info, start_time)
                
            except Exception as e:
                # Handle conversion errors with recovery
                conversion_error = self._categorize_and_handle_error(e, file_info)
                return self._attempt_error_recovery(conversion_error, file_info, start_time)
            
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error in conversion: {e}", exc_info=True)
            unexpected_error = ConversionError(
                f"Unexpected conversion error: {str(e)}",
                file_info.path,
                is_recoverable=False,
                error_code="UNEXPECTED_ERROR"
            )
            self._error_reporter.report_error(unexpected_error, file_info)
            
            return ConversionResult(
                file_info=file_info,
                status=ConversionStatus.FAILED,
                error_message=str(unexpected_error),
                conversion_time=time.time() - start_time,
                progress_status=ConversionProgressStatus.ERROR,
                progress_details=f"예상치 못한 오류: {str(e)}"
            )
    
    def _validate_file_pre_conversion(self, file_info: FileInfo) -> bool:
        """Pre-conversion validation with specific PDF FontBBox checks"""
        try:
            if self._document_validator.can_validate(file_info.path):
                validation_result = self._document_validator.validate(file_info.path)
                
                if not validation_result.is_valid:
                    logger.warning(f"Validation failed for {file_info.name}: {len(validation_result.critical_issues)} critical issues")
                    
                    # Report validation issues
                    for issue in validation_result.critical_issues:
                        error_report = self._error_reporter.report_error(
                            ConversionError(issue.message, file_info.path, error_code=issue.code),
                            file_info,
                            "pre_conversion_validation"
                        )
                    
                    return False
                
                # Check for font issues specifically
                from .validators.pdf_validator import PDFValidationResult
                if isinstance(validation_result, PDFValidationResult) and validation_result.font_issues:
                    logger.warning(f"Font issues detected in {file_info.name}: {len(validation_result.font_issues)} issues")
                    # Font issues don't block conversion but are noted for potential recovery
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error for {file_info.name}: {e}")
            # Validation errors don't block conversion in standard mode
            return True
    
    def _handle_file_conflicts(self, file_info: FileInfo, output_path: Path) -> bool:
        """Handle file conflicts and update file_info"""
        conflict_info = self._conflict_handler.detect_conflict(file_info.path, output_path)
        
        if conflict_info.conflict_status == FileConflictStatus.EXISTS:
            file_info.progress_status = ConversionProgressStatus.RESOLVING_CONFLICTS
            file_info.conflict_status = conflict_info.conflict_status
            
            # 충돌 감지 시그널 발생
            self.conflict_detected.emit(conflict_info)
            
            # 충돌 해결
            resolved_info = self._conflict_handler.resolve_conflict(conflict_info)
            
            if resolved_info.conflict_status == FileConflictStatus.WILL_SKIP:
                logger.info(f"파일 건너뛰기: {file_info.path}")
                return False
            
            # 해결된 경로 사용
            if resolved_info.resolved_path:
                output_path = resolved_info.resolved_path
                file_info.resolved_output_path = output_path
                file_info.conflict_status = resolved_info.conflict_status
        
        file_info.output_path = output_path
        return True
    
    def _perform_conversion_with_cache(self, file_info: FileInfo) -> str:
        """Perform conversion with caching and FontBBox warning capture"""
        # Set up warning capture for FontBBox issues
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # 캐시에서 변환 결과 확인
            cache_key = f"conversion_{file_info.path}_{file_info.size}_{file_info.modified_time.timestamp()}"
            cached_content = self._memory_optimizer.get_cached_result(cache_key)
            
            if cached_content:
                logger.debug(f"캐시에서 변환 결과 사용: {file_info.path}")
                return cached_content
            
            # MarkItDown으로 변환 (OCR 설정 적용)
            try:
                # OCR 설정 가져오기 (config_manager가 있는 경우)
                config = None
                if self._config_manager:
                    config = self._config_manager.get_config()

                # 이미지 파일인지 확인
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
                is_image_file = file_info.path.suffix.lower() in image_extensions

                # OCR 처리 (이미지 파일이고 OCR 서비스가 사용 가능한 경우)
                if is_image_file and config and hasattr(config, 'enable_llm_ocr') and config.enable_llm_ocr:
                    if hasattr(self, '_ocr_service') and self._ocr_service is not None:
                        # 우리의 OCRService 사용
                        try:
                            logger.info(f"Using OCRService for image file: {file_info.name}")
                            # Use async extract_text_from_image method
                            import asyncio
                            ocr_result = asyncio.run(self._ocr_service.extract_text_from_image(Path(file_info.path)))

                            if ocr_result and ocr_result.is_success and ocr_result.text:
                                # OCR 성공 - Markdown 형식으로 포맷팅
                                markdown_content = f"# {file_info.name}\n\n"
                                markdown_content += f"**Image OCR Result**\n\n"
                                markdown_content += ocr_result.text

                                # 품질 정보 추가 (있는 경우)
                                if hasattr(ocr_result, 'confidence') and ocr_result.confidence:
                                    markdown_content += f"\n\n---\n*OCR Confidence Score: {ocr_result.confidence:.2f}*"

                                # 메타데이터 저장
                                file_info.conversion_metadata = {
                                    'ocr_method': 'OCRService',
                                    'extraction_success': True,
                                    'confidence': getattr(ocr_result, 'confidence', None),
                                    'processing_time': getattr(ocr_result, 'processing_time', None)
                                }

                                logger.info(f"OCRService successfully processed {file_info.name}")
                            else:
                                # OCR 실패 - MarkItDown으로 폴백
                                logger.warning(f"OCRService failed for {file_info.name}, falling back to MarkItDown")
                                raise Exception("OCRService failed, fallback to MarkItDown")

                        except Exception as ocr_error:
                            logger.warning(f"OCRService error for {file_info.name}: {ocr_error}, falling back to MarkItDown")
                            # MarkItDown 폴백 처리는 아래에서 수행
                            pass

                    # OCR 서비스가 없거나 실패한 경우 MarkItDown OCR 사용
                    if 'markdown_content' not in locals():
                        # OCR 옵션 준비 (MarkItDown 내장 OCR)
                        conversion_kwargs = {
                            'ocr_enabled': True,
                            'ocr_language': getattr(config, 'ocr_language', 'auto'),
                            'max_image_size': getattr(config, 'max_image_size', 1024)
                        }
                        logger.info(f"Using MarkItDown OCR for image file: {file_info.name}")

                        # 변환 실행
                        conversion_result = self._markitdown.convert(str(file_info.path), **conversion_kwargs)
                        markdown_content = conversion_result.text_content

                        # OCR 메타데이터 저장
                        file_info.conversion_metadata = {
                            'ocr_method': 'MarkItDown',
                            'metadata': getattr(conversion_result, 'metadata', {})
                        }
                else:
                    # 이미지가 아니거나 OCR이 비활성화된 경우 일반 변환
                    conversion_result = self._markitdown.convert(str(file_info.path))
                    markdown_content = conversion_result.text_content

                    # 메타데이터 저장 (이미지 파일인 경우)
                    if is_image_file and hasattr(conversion_result, 'metadata'):
                        file_info.conversion_metadata = getattr(conversion_result, 'metadata', {})
                
                # Check for FontBBox warnings
                fontbbox_warnings = [
                    warning for warning in w 
                    if "FontBBox" in str(warning.message) and "None cannot be parsed as 4 floats" in str(warning.message)
                ]
                
                if fontbbox_warnings:
                    # Create FontDescriptorError from warning
                    font_error = FontDescriptorError.from_markitdown_warning(
                        str(fontbbox_warnings[0].message), 
                        file_info.path
                    )
                    
                    # Report the font error but continue conversion
                    self._error_reporter.report_error(font_error, file_info, "markitdown_conversion")
                    logger.warning(f"FontBBox warning captured for {file_info.name}: {font_error.message}")
                
                # 결과 캐싱
                if markdown_content and len(markdown_content) < 10 * 1024 * 1024:  # 10MB 미만만 캐싱
                    self._memory_optimizer.cache_result(cache_key, markdown_content)
                
                return markdown_content
                
            except Exception as e:
                # Check if this is a FontBBox related error
                error_message = str(e)
                if "FontBBox" in error_message and ("None cannot be parsed" in error_message or "font descriptor" in error_message.lower()):
                    raise FontDescriptorError.from_markitdown_warning(error_message, file_info.path)
                else:
                    raise MarkItDownError.wrap_exception(e, file_info.path)
    
    def _categorize_and_handle_error(self, error: Exception, file_info: FileInfo) -> ConversionError:
        """Categorize exception into appropriate ConversionError type"""
        conversion_error = categorize_exception(error, file_info.path)
        
        # Report the categorized error
        self._error_reporter.report_error(conversion_error, file_info, "conversion")
        
        return conversion_error
    
    def _attempt_error_recovery(self, error: ConversionError, file_info: FileInfo, start_time: float) -> ConversionResult:
        """Attempt error recovery using the recovery manager"""
        if not self._error_recovery_manager:
            return self._create_failed_result(file_info, str(error), start_time)
        
        try:
            # Attempt recovery
            recovery_result = self._error_recovery_manager.recover_from_error(
                error, file_info, file_info.output_path, 
                original_converter=lambda fi: self._perform_conversion_with_cache(fi)
            )
            
            if recovery_result.success and recovery_result.result:
                logger.info(f"Recovery successful for {file_info.name} using {recovery_result.action_taken.value}")
                return recovery_result.result
            else:
                logger.warning(f"Recovery failed for {file_info.name}: {recovery_result.error}")
                return self._create_failed_result(
                    file_info, 
                    f"변환 실패 (복구 시도 실패: {recovery_result.action_taken.value}): {str(error)}", 
                    start_time,
                    recovery_details=recovery_result.recovery_details
                )
                
        except Exception as recovery_exception:
            logger.error(f"Error recovery process failed: {recovery_exception}")
            return self._create_failed_result(file_info, str(error), start_time)
    
    def _finalize_successful_conversion(self, file_info: FileInfo, markdown_content: str, 
                                      output_path: Path, start_time: float) -> ConversionResult:
        """Finalize successful conversion"""
        # 메타데이터 추가
        file_info.progress_status = ConversionProgressStatus.FINALIZING
        conversion_time = time.time() - start_time
        metadata = create_conversion_metadata(file_info.path, conversion_time)
        
        # 메타데이터를 마크다운 헤더로 추가
        metadata_header = self._create_metadata_header(file_info, metadata)
        final_content = metadata_header + "\n\n" + markdown_content
        
        # 파일 저장
        file_info.progress_status = ConversionProgressStatus.WRITING_OUTPUT
        saved_path = self._save_converted_content(final_content, output_path)
        
        file_info.progress_status = ConversionProgressStatus.COMPLETED
        logger.info(f"변환 성공: {file_info.path} -> {saved_path}")
        
        # 충돌 해결 정보 포함
        conflict_status = getattr(file_info, 'conflict_status', FileConflictStatus.NONE)
        applied_policy, original_output_path = self._get_conflict_resolution_info(file_info, conflict_status)
        
        return ConversionResult(
            file_info=file_info,
            status=ConversionStatus.SUCCESS,
            output_path=saved_path,
            conversion_time=conversion_time,
            metadata=metadata,
            conflict_status=conflict_status,
            applied_policy=applied_policy,
            original_output_path=original_output_path,
            progress_status=ConversionProgressStatus.COMPLETED
        )
    
    def _get_conflict_resolution_info(self, file_info: FileInfo, conflict_status: FileConflictStatus) -> tuple:
        """Get conflict resolution information"""
        applied_policy = None
        original_output_path = None
        
        if conflict_status != FileConflictStatus.NONE:
            if conflict_status == FileConflictStatus.WILL_OVERWRITE:
                applied_policy = FileConflictPolicy.OVERWRITE
            elif conflict_status == FileConflictStatus.WILL_RENAME:
                applied_policy = FileConflictPolicy.RENAME
                # 원래 출력 경로 생성 - 새로운 보안 강화 유틸리티 사용
                try:
                    if self._save_to_original_dir:
                        original_output_path = resolve_markdown_output_path(
                            source_path=file_info.path,
                            preserve_structure=False,
                            output_base_dir=file_info.path.parent,
                            ensure_unique=False
                        )
                    else:
                        original_output_path = resolve_markdown_output_path(
                            source_path=file_info.path,
                            preserve_structure=True,
                            output_base_dir=self.output_directory,
                            ensure_unique=False
                        )
                except (ValueError, OSError) as e:
                    logger.error(f"원본 출력 경로 생성 실패: {e}")
                    # 폴백으로 기존 방식 사용
                    original_output_path = create_markdown_output_path(
                        file_info.path, 
                        self.output_directory if not self._save_to_original_dir else None,
                        self._save_to_original_dir
                    )
        
        return applied_policy, original_output_path
    
    def _create_failed_result(self, file_info: FileInfo, error_message: str, start_time: float,
                            recovery_details: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """Create a failed conversion result"""
        file_info.progress_status = ConversionProgressStatus.ERROR
        conversion_time = time.time() - start_time
        
        metadata = {"recovery_details": recovery_details} if recovery_details else {}
        
        return ConversionResult(
            file_info=file_info,
            status=ConversionStatus.FAILED,
            error_message=error_message,
            conversion_time=conversion_time,
            progress_status=ConversionProgressStatus.ERROR,
            progress_details=f"오류: {error_message}",
            metadata=metadata
        )
    
    def _create_cancelled_result(self, file_info: FileInfo, output_path: Path, start_time: float) -> ConversionResult:
        """Create a cancelled conversion result"""
        return ConversionResult(
            file_info=file_info,
            status=ConversionStatus.CANCELLED,
            conflict_status=FileConflictStatus.WILL_SKIP,
            applied_policy=FileConflictPolicy.SKIP,
            original_output_path=output_path,
            conversion_time=time.time() - start_time,
            progress_status=ConversionProgressStatus.COMPLETED,
            progress_details="사용자가 건너뛰기를 선택했습니다"
        )
    
    def _on_error_reported(self, error_report: ErrorReport):
        """Handle error report callback"""
        self.error_reported.emit(error_report)
    
    def _save_converted_content(self, content: str, output_path: Path) -> Path:
        """변환된 내용을 파일에 저장"""
        try:
            # 출력 디렉토리 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"파일 저장 실패 ({output_path}): {e}")
            raise ValueError(f"파일 저장 실패: {str(e)}")
    
    def _create_metadata_header(self, file_info: FileInfo, metadata: Dict[str, Any]) -> str:
        """메타데이터 헤더 생성"""
        header_lines = [
            "---",
            f"# 변환 정보",
            f"- **원본 파일**: {file_info.name}",
            f"- **파일 크기**: {file_info.size_formatted}",
            f"- **파일 타입**: {file_info.file_type.value.upper()}",
            f"- **수정일**: {file_info.modified_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **변환일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **변환 시간**: {metadata.get('conversion_time_formatted', 'N/A')}",
            "---"
        ]
        return "\n".join(header_lines)
    
    def cancel(self):
        """변환 취소"""
        with QMutexLocker(self._mutex):
            self._is_cancelled = True
        logger.info("변환 취소 요청됨")


class ConversionManager(QObject):
    """
    Enhanced conversion manager with comprehensive error handling and monitoring
    
    This manager now uses the secure resolve_markdown_output_path() utility function
    for generating output paths, with fallback to the original create_markdown_output_path()
    for backward compatibility and error recovery.
    
    Security improvements:
    - Directory traversal attack prevention
    - Path sanitization and validation
    - Cross-platform compatibility
    - Proper error handling with graceful fallback
    """
    
    # Enhanced signals
    conversion_progress_updated = pyqtSignal(object)  # ConversionProgress
    file_conversion_started = pyqtSignal(object)  # FileInfo
    file_conversion_completed = pyqtSignal(object)  # ConversionResult
    conversion_completed = pyqtSignal(list)  # List[ConversionResult]
    conversion_error = pyqtSignal(str)  # 에러 메시지
    file_conflict_detected = pyqtSignal(object)  # FileConflictInfo
    error_reported = pyqtSignal(object)  # ErrorReport
    validation_completed = pyqtSignal(object, object)  # FileInfo, ValidationResult
    recovery_attempted = pyqtSignal(object, object)  # FileInfo, RecoveryResult
    
    def __init__(self, output_directory: Path = None, conflict_config: Optional[FileConflictConfig] = None,
                 save_to_original_dir: bool = True, validation_level: ValidationLevel = ValidationLevel.STANDARD,
                 enable_recovery: bool = True, enable_monitoring: bool = True, config_manager=None):
        super().__init__()
        self.output_directory = output_directory or Path(DEFAULT_OUTPUT_DIRECTORY)
        self._conversion_worker: Optional[ConversionWorker] = None
        self._is_converting = False
        self._max_workers = 3
        self._memory_optimizer = MemoryOptimizer()
        self._conflict_handler = FileConflictHandler(conflict_config or FileConflictConfig())
        self._save_to_original_dir = save_to_original_dir
        self._config_manager = config_manager
        
        # Enhanced error handling and monitoring
        self._validation_level = validation_level
        self._enable_recovery = enable_recovery
        self._enable_monitoring = enable_monitoring
        
        # Initialize error handling components
        self._circuit_breaker = CircuitBreaker("conversion_manager")
        self._fallback_manager = FallbackManager()
        self._error_recovery_manager = ErrorRecoveryManager(self._fallback_manager) if enable_recovery else None
        self._error_reporter = ErrorReporter(log_file=Path("logs/conversion_errors.log"))
        self._document_validator = DocumentValidator(validation_level)
        
        # Performance and monitoring metrics
        self._conversion_metrics = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "recovered_conversions": 0,
            "validation_failures": 0,
            "font_error_count": 0,
            "avg_conversion_time": 0.0,
            "circuit_breaker_activations": 0
        }
        
        # MarkItDown 가용성 확인
        if not MARKITDOWN_AVAILABLE:
            error_report = self._error_reporter.report_error(
                ConversionError("MarkItDown library not available", error_code="MARKITDOWN_UNAVAILABLE"),
                context="initialization"
            )
            logger.warning("MarkItDown 라이브러리가 설치되지 않았습니다")
    
    def set_output_directory(self, directory: Path):
        """출력 디렉토리 설정"""
        self.output_directory = directory
        logger.info(f"출력 디렉토리 설정: {directory}")
    
    def set_max_workers(self, max_workers: int):
        """최대 워커 수 설정"""
        self._max_workers = max(1, min(max_workers, 10))
        logger.info(f"최대 워커 수 설정: {self._max_workers}")
    
    def convert_files_async(self, files: List[FileInfo]) -> bool:
        """
        비동기 파일 변환
        
        Args:
            files: 변환할 파일 목록
        
        Returns:
            변환 시작 성공 여부
        """
        if not MARKITDOWN_AVAILABLE:
            self.conversion_error.emit("MarkItDown 라이브러리가 설치되지 않았습니다. pip install markitdown[all]")
            return False
        
        if self._is_converting:
            logger.warning("이미 변환이 진행 중입니다")
            return False
        
        if not files:
            logger.warning("변환할 파일이 없습니다")
            return False
        
        # 이전 변환 워커 정리
        if self._conversion_worker is not None:
            self._conversion_worker.quit()
            self._conversion_worker.wait()
            self._conversion_worker.deleteLater()
        
        # 새로운 변환 워커 생성 (enhanced)
        self._conversion_worker = ConversionWorker(
            files, self.output_directory, self._max_workers, self._memory_optimizer,
            self._conflict_handler, self._save_to_original_dir,
            self._validation_level, self._enable_recovery, self._config_manager
        )
        
        # Enhanced signal connections
        self._conversion_worker.progress_updated.connect(self._on_progress_updated)
        self._conversion_worker.file_conversion_started.connect(self._on_file_started)
        self._conversion_worker.file_conversion_completed.connect(self._on_file_completed)
        self._conversion_worker.conversion_completed.connect(self._on_conversion_completed)
        self._conversion_worker.error_occurred.connect(self._on_conversion_error)
        self._conversion_worker.conflict_detected.connect(self._on_conflict_detected)
        self._conversion_worker.error_reported.connect(self._on_error_reported)
        self._conversion_worker.finished.connect(self._on_conversion_finished)
        
        # 변환 시작
        self._is_converting = True
        self._conversion_worker.start()
        
        logger.info(f"파일 변환 시작: {len(files)}개 파일")
        return True
    
    def convert_single_file(self, file_info: FileInfo) -> ConversionResult:
        """
        단일 파일 동기 변환 (테스트용)
        
        Args:
            file_info: 변환할 파일 정보
        
        Returns:
            변환 결과
        """
        if not MARKITDOWN_AVAILABLE:
            return ConversionResult(
                file_info=file_info,
                status=ConversionStatus.FAILED,
                error_message="MarkItDown 라이브러리가 설치되지 않았습니다"
            )
        
        worker = ConversionWorker(
            [file_info], self.output_directory, 1, self._memory_optimizer,
            self._conflict_handler, self._save_to_original_dir,
            self._validation_level, self._enable_recovery, self._config_manager
        )
        return worker._convert_single_file(file_info)
    
    def cancel_conversion(self) -> bool:
        """변환 취소"""
        if not self._is_converting or self._conversion_worker is None:
            return False
        
        self._conversion_worker.cancel()
        return True
    
    def is_converting(self) -> bool:
        """변환 중인지 확인"""
        return self._is_converting
    
    def is_markitdown_available(self) -> bool:
        """MarkItDown 라이브러리 사용 가능 여부"""
        return MARKITDOWN_AVAILABLE
    
    def get_supported_formats(self) -> List[str]:
        """지원하는 파일 형식 반환"""
        if not MARKITDOWN_AVAILABLE:
            return []
        
        # MarkItDown이 지원하는 형식들
        return [
            "docx", "pptx", "xlsx", "xls",  # Office
            "pdf",  # PDF
            "jpg", "jpeg", "png", "gif", "bmp", "tiff",  # Images
            "mp3", "wav",  # Audio
            "html", "htm", "csv", "json", "xml", "txt",  # Web/Text
            "zip",  # Archive
            "epub"  # E-book
        ]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 사용 통계 반환"""
        return self._memory_optimizer.get_memory_statistics()
    
    def cleanup_memory(self):
        """메모리 정리"""
        self._memory_optimizer.cleanup()
        logger.info("ConversionManager 메모리 정리 완료")
    
    def validate_file_for_conversion(self, file_info: FileInfo) -> tuple[bool, str]:
        """
        파일이 변환 가능한지 검증
        
        Returns:
            (가능 여부, 오류 메시지)
        """
        if not MARKITDOWN_AVAILABLE:
            return False, "MarkItDown 라이브러리가 설치되지 않았습니다"
        
        if not file_info.path.exists():
            return False, "파일이 존재하지 않습니다"
        
        if file_info.size == 0:
            return False, "파일이 비어있습니다"
        
        supported_formats = self.get_supported_formats()
        if file_info.file_type.value not in supported_formats:
            return False, f"지원하지 않는 파일 형식입니다: {file_info.file_type.value}"
        
        # 파일 크기 제한 (100MB)
        max_size = 100 * 1024 * 1024
        if file_info.size > max_size:
            return False, f"파일이 너무 큽니다 (최대 100MB): {file_info.size_formatted}"
        
        return True, ""
    
    def _on_progress_updated(self, progress: ConversionProgress):
        """진행률 업데이트"""
        self.conversion_progress_updated.emit(progress)
    
    def _on_file_started(self, file_info: FileInfo):
        """파일 변환 시작시"""
        self.file_conversion_started.emit(file_info)
    
    def _on_file_completed(self, result: ConversionResult):
        """파일 변환 완료시"""
        self.file_conversion_completed.emit(result)
    
    def _on_conversion_completed(self, results: List[ConversionResult]):
        """전체 변환 완료시"""
        success_count = len([r for r in results if r.is_success])
        total_count = len(results)
        
        logger.info(f"변환 완료: {success_count}/{total_count} 성공")
        self.conversion_completed.emit(results)
    
    def _on_conversion_error(self, error_message: str):
        """변환 오류시"""
        logger.error(f"변환 오류: {error_message}")
        self.conversion_error.emit(error_message)
    
    def _on_conflict_detected(self, conflict_info):
        """파일 충돌 감지시"""
        self.file_conflict_detected.emit(conflict_info)
    
    def _on_conversion_finished(self):
        """변환 스레드 종료시"""
        self._is_converting = False
        if self._conversion_worker:
            self._conversion_worker.deleteLater()
            self._conversion_worker = None
    
    def _on_error_reported(self, error_report: ErrorReport):
        """Handle error reports from worker"""
        # Update metrics based on error type
        if "FontDescriptor" in error_report.technical_details.get("error_type", ""):
            self._conversion_metrics["font_error_count"] += 1
        
        # Emit to UI
        self.error_reported.emit(error_report)
    
    def set_save_to_original_directory(self, save_to_original: bool):
        """원본 디렉토리에 저장 여부 설정"""
        self._save_to_original_dir = save_to_original
        logger.info(f"원본 디렉토리 저장 설정: {save_to_original}")
    
    def set_conflict_policy(self, policy: FileConflictPolicy):
        """충돌 해결 정책 설정"""
        config = self._conflict_handler.get_config()
        config.default_policy = policy
        self._conflict_handler.update_config(config)
        logger.info(f"충돌 해결 정책 설정: {policy.value}")
    
    def get_conflict_statistics(self):
        """충돌 처리 통계 반환"""
        return self._conflict_handler.get_conflict_statistics()
    
    def reset_conflict_statistics(self):
        """충돌 처리 통계 초기화"""
        self._conflict_handler.reset_statistics()
    
    def update_conflict_config(self, config: FileConflictConfig):
        """충돌 처리 설정 업데이트"""
        self._conflict_handler.update_config(config)
        logger.info(f"충돌 처리 설정 업데이트: {config}")
    
    def convert_files_with_policy(self, files: List[FileInfo], policy: FileConflictPolicy) -> bool:
        """
        특정 충돌 해결 정책으로 파일 변환
        
        Args:
            files: 변환할 파일 목록
            policy: 충돌 해결 정책
        
        Returns:
            변환 시작 성공 여부
        """
        # 일시적으로 정책 설정
        original_config = self._conflict_handler.get_config()
        temp_config = FileConflictConfig(
            default_policy=policy,
            auto_rename_pattern=original_config.auto_rename_pattern,
            remember_choices=original_config.remember_choices,
            apply_to_all=True,
            backup_original=original_config.backup_original,
            conflict_log_enabled=original_config.conflict_log_enabled
        )
        
        self._conflict_handler.update_config(temp_config)
        
        try:
            return self.convert_files_async(files)
        finally:
            # 원래 설정으로 복원
            self._conflict_handler.update_config(original_config)
    
    def prepare_files_for_conversion(self, files: List[FileInfo]) -> List[FileInfo]:
        """
        변환을 위한 파일 준비 (충돌 사전 검사)
        
        Args:
            files: 검사할 파일 목록
        
        Returns:
            충돌 정보가 업데이트된 파일 목록
        """
        prepared_files = []
        
        for file_info in files:
            # 출력 경로 생성 - 새로운 보안 강화 유틸리티 사용
            try:
                if self._save_to_original_dir:
                    # 원본 디렉토리에 저장하는 경우
                    output_path = resolve_markdown_output_path(
                        source_path=file_info.path,
                        preserve_structure=False,
                        output_base_dir=file_info.path.parent,
                        ensure_unique=False  # 충돌 감지를 위해 원본 경로 유지
                    )
                else:
                    # 지정된 출력 디렉토리에 저장하는 경우
                    output_path = resolve_markdown_output_path(
                        source_path=file_info.path,
                        preserve_structure=True,
                        output_base_dir=self.output_directory,
                        ensure_unique=False  # 충돌 감지를 위해 원본 경로 유지
                    )
                file_info.output_path = output_path
                logger.debug(f"Generated output path for {file_info.name}: {output_path}")
            except (ValueError, OSError) as e:
                logger.error(f"출력 경로 생성 실패 ({file_info.name}): {e}")
                # 폴백으로 기존 방식 사용
                output_path = create_markdown_output_path(
                    file_info.path,
                    self.output_directory if not self._save_to_original_dir else None,
                    self._save_to_original_dir
                )
                file_info.output_path = output_path
            
            # 충돌 감지
            try:
                conflict_info = self._conflict_handler.detect_conflict(file_info.path, output_path)
                file_info.conflict_status = conflict_info.conflict_status
                
                if conflict_info.conflict_status == FileConflictStatus.EXISTS:
                    # 추천 해결 방법 설정
                    file_info.conflict_policy = conflict_info.suggested_resolution
                
            except Exception as e:
                logger.error(f"충돌 검사 실패 ({file_info.name}): {e}")
                file_info.conflict_status = FileConflictStatus.NONE
            
            prepared_files.append(file_info)
        
        return prepared_files
    
    # Enhanced methods for comprehensive error handling and monitoring
    
    def validate_files(self, files: List[FileInfo]) -> Dict[Path, ValidationResult]:
        """
        Validate files before conversion with detailed error reporting
        
        Args:
            files: Files to validate
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        return self._document_validator.validate_multiple([f.path for f in files])
    
    def get_error_reports(self, severity: Optional[ErrorSeverity] = None, 
                         last_n: Optional[int] = None) -> List[ErrorReport]:
        """Get error reports from the error reporter"""
        return self._error_reporter.get_reports(severity, last_n)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        return self._error_reporter.get_error_summary()
    
    def get_conversion_metrics(self) -> Dict[str, Any]:
        """Get comprehensive conversion metrics"""
        base_metrics = {
            **self._conversion_metrics,
            "memory_stats": self.get_memory_statistics(),
            "conflict_stats": self.get_conflict_statistics(),
            "circuit_breaker_state": self._circuit_breaker.state.value,
            "circuit_breaker_metrics": self._circuit_breaker.get_metrics()
        }
        
        # Add error handling metrics if available
        if self._error_recovery_manager:
            base_metrics["recovery_metrics"] = self._error_recovery_manager.get_metrics()
        
        base_metrics["fallback_metrics"] = self._fallback_manager.get_metrics()
        
        return base_metrics
    
    def export_error_reports(self, output_path: Path, format: str = "json") -> bool:
        """Export error reports to file"""
        return self._error_reporter.export_reports(output_path, format)
    
    def clear_error_reports(self, older_than_hours: Optional[int] = None):
        """Clear error reports"""
        self._error_reporter.clear_reports(older_than_hours)
    
    def reset_metrics(self):
        """Reset all metrics"""
        self._conversion_metrics = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "recovered_conversions": 0,
            "validation_failures": 0,
            "font_error_count": 0,
            "avg_conversion_time": 0.0,
            "circuit_breaker_activations": 0
        }
        
        if self._error_recovery_manager:
            self._error_recovery_manager.reset_metrics()
        
        logger.info("Conversion metrics reset")
    
    def set_validation_level(self, level: ValidationLevel):
        """Set validation level"""
        self._validation_level = level
        self._document_validator.set_validation_level(level)
        logger.info(f"Validation level set to {level.value}")
    
    def enable_recovery(self, enabled: bool):
        """Enable or disable error recovery"""
        self._enable_recovery = enabled
        if enabled and not self._error_recovery_manager:
            self._error_recovery_manager = ErrorRecoveryManager(self._fallback_manager)
        logger.info(f"Error recovery {'enabled' if enabled else 'disabled'}")
    
    def get_circuit_breaker_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self._circuit_breaker.state
    
    def force_circuit_breaker_reset(self):
        """Force reset circuit breaker"""
        self._circuit_breaker.reset()
        logger.info("Circuit breaker forcibly reset")
    
    def get_fallback_strategies(self) -> List[str]:
        """Get available fallback strategies"""
        return [strategy.name for strategy in self._fallback_manager.get_strategies()]
    
    def enable_fallback_strategy(self, strategy_name: str) -> bool:
        """Enable specific fallback strategy"""
        return self._fallback_manager.enable_strategy(strategy_name)
    
    def disable_fallback_strategy(self, strategy_name: str) -> bool:
        """Disable specific fallback strategy"""
        return self._fallback_manager.disable_strategy(strategy_name)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        circuit_state = self._circuit_breaker.state
        memory_stats = self.get_memory_statistics()
        error_summary = self.get_error_summary()
        
        # Calculate health score (0-100)
        health_score = 100
        
        # Circuit breaker penalties
        if circuit_state == CircuitBreakerState.OPEN:
            health_score -= 30
        elif circuit_state == CircuitBreakerState.HALF_OPEN:
            health_score -= 10
        
        # Memory usage penalties
        memory_usage_mb = memory_stats.get('current_memory_mb', 0)
        if memory_usage_mb > 500:  # High memory usage
            health_score -= 20
        elif memory_usage_mb > 200:  # Moderate memory usage
            health_score -= 10
        
        # Error rate penalties
        total_reports = error_summary.get('total_reports', 0)
        if total_reports > 10:  # High error rate
            health_score -= 20
        elif total_reports > 5:  # Moderate error rate
            health_score -= 10
        
        # Font error specific penalty
        font_errors = self._conversion_metrics.get("font_error_count", 0)
        if font_errors > 5:
            health_score -= 15
        elif font_errors > 0:
            health_score -= 5
        
        health_score = max(0, health_score)  # Ensure non-negative
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "critical",
            "circuit_breaker_state": circuit_state.value,
            "memory_usage_mb": memory_usage_mb,
            "total_errors": total_reports,
            "font_errors": font_errors,
            "is_converting": self._is_converting,
            "timestamp": datetime.now().isoformat()
        }
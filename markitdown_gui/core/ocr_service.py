"""
OCR 서비스
이미지와 PDF에서 텍스트 추출을 위한 LLM 기반 OCR 서비스
"""

import asyncio
import tempfile
from typing import Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import logging

from .models import (
    FileType, FileInfo, OCRRequest, OCRResult,
    TokenUsageType, LLMProvider
)
from .llm_manager import LLMManager
from .logger import get_logger


logger = get_logger(__name__)


@dataclass
class OCRServiceConfig:
    """OCR 서비스 설정"""
    enabled: bool = True
    fallback_to_tesseract: bool = True
    tesseract_available: bool = False
    max_image_size: int = 1024
    supported_formats: List[str] = None
    # 전처리 관련 설정
    enable_preprocessing: bool = True
    preprocessing_config: Optional[Dict] = None

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = [
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'
            ]

        if self.preprocessing_config is None:
            self.preprocessing_config = {
                'mode': 'auto',
                'quality_threshold': 0.6,
                'enabled_enhancements': ['deskew', 'contrast', 'brightness', 'sharpening', 'noise_reduction'],
                'enable_parallel_processing': True,
                'cache_strategy': 'memory'
            }


class OCRService:
    """OCR 서비스 클래스"""
    
    def __init__(self, llm_manager: LLMManager, config: OCRServiceConfig = None):
        """
        초기화

        Args:
            llm_manager: LLM 관리자
            config: OCR 서비스 설정
        """
        self.llm_manager = llm_manager
        self.config = config or OCRServiceConfig()

        # Tesseract 가용성 확인
        self._check_tesseract_availability()

        # 전처리 파이프라인 초기화
        self.preprocessing_pipeline = None
        if self.config.enable_preprocessing:
            self._initialize_preprocessing_pipeline()

        logger.info(f"OCR Service initialized (LLM: {self.config.enabled}, Tesseract: {self.config.tesseract_available}, Preprocessing: {self.config.enable_preprocessing})")

    def _initialize_preprocessing_pipeline(self):
        """전처리 파이프라인 초기화"""
        try:
            from .ocr_enhancements.preprocessing import PreprocessingPipeline, initialize_preprocessing

            # 전처리 모듈 초기화 시도
            if initialize_preprocessing(self.config.preprocessing_config):
                from .ocr_enhancements.preprocessing import get_preprocessing_pipeline
                self.preprocessing_pipeline = get_preprocessing_pipeline()

                if self.preprocessing_pipeline:
                    logger.info("Image preprocessing pipeline initialized successfully")
                else:
                    logger.warning("Preprocessing pipeline initialization returned None")
            else:
                logger.warning("Failed to initialize preprocessing module")

        except ImportError as e:
            logger.info(f"Preprocessing module not available: {e}")
            self.config.enable_preprocessing = False
        except Exception as e:
            logger.error(f"Failed to initialize preprocessing pipeline: {e}")
            self.config.enable_preprocessing = False
    
    def _check_tesseract_availability(self):
        """Tesseract OCR 가용성 확인"""
        try:
            import pytesseract
            from PIL import Image
            
            # 간단한 테스트로 Tesseract 동작 확인
            test_image = Image.new('RGB', (100, 50), color='white')
            pytesseract.image_to_string(test_image)
            
            self.config.tesseract_available = True
            logger.info("Tesseract OCR is available")
            
        except ImportError:
            logger.info("Tesseract dependencies not available (pytesseract, PIL)")
            self.config.tesseract_available = False
        except Exception as e:
            logger.warning(f"Tesseract OCR not working: {e}")
            self.config.tesseract_available = False
    
    def is_supported_format(self, file_path: Path) -> bool:
        """
        지원 형식 확인
        
        Args:
            file_path: 파일 경로
        
        Returns:
            지원 여부
        """
        extension = file_path.suffix.lower().lstrip('.')
        return extension in self.config.supported_formats or extension == 'pdf'
    
    async def extract_text_from_image(
        self,
        image_path: Path,
        language: str = "auto",
        prompt: Optional[str] = None
    ) -> OCRResult:
        """
        이미지에서 텍스트 추출 (전처리 포함)

        Args:
            image_path: 이미지 파일 경로
            language: OCR 언어 (auto, ko, en, etc.)
            prompt: 사용자 정의 프롬프트

        Returns:
            OCR 결과
        """
        if not image_path.exists():
            return OCRResult(
                text="",
                error_message=f"Image file not found: {image_path}"
            )

        if not self.is_supported_format(image_path):
            return OCRResult(
                text="",
                error_message=f"Unsupported image format: {image_path.suffix}"
            )

        # 전처리 파이프라인 적용 (활성화된 경우)
        processed_image_path = image_path
        preprocessing_metadata = {}

        if self.config.enable_preprocessing and self.preprocessing_pipeline:
            try:
                logger.debug(f"Applying preprocessing to {image_path.name}")
                preprocessing_result = await self.preprocessing_pipeline.auto_enhance_for_ocr(image_path)

                if preprocessing_result.is_success:
                    processed_image_path = preprocessing_result.enhanced_image_path
                    preprocessing_metadata = {
                        'preprocessing_applied': True,
                        'processing_time': preprocessing_result.processing_time,
                        'improvement_score': preprocessing_result.total_improvement_score,
                        'enhancements_count': len(preprocessing_result.enhancement_results),
                        'cache_hit': preprocessing_result.cache_hit
                    }
                    logger.info(f"Preprocessing completed for {image_path.name} (improvement: {preprocessing_result.total_improvement_score:.2f})")
                else:
                    preprocessing_metadata = {
                        'preprocessing_applied': False,
                        'error': preprocessing_result.error_message
                    }
                    logger.warning(f"Preprocessing failed for {image_path.name}: {preprocessing_result.error_message}")

            except Exception as e:
                logger.error(f"Preprocessing error for {image_path.name}: {e}")
                preprocessing_metadata = {
                    'preprocessing_applied': False,
                    'error': str(e)
                }
        
        # LLM OCR 시도 (전처리된 이미지 사용)
        if self.config.enabled and self.llm_manager.current_config and self.llm_manager.current_config.enable_ocr:
            try:
                request = OCRRequest(
                    image_path=processed_image_path,
                    language=language,
                    max_size=self.config.max_image_size,
                    prompt=prompt
                )

                result = await self.llm_manager.ocr_image(request)

                if result.is_success:
                    # 전처리 메타데이터 추가
                    if hasattr(result, 'metadata') and result.metadata:
                        result.metadata.update(preprocessing_metadata)
                    else:
                        result.metadata = preprocessing_metadata

                    logger.info(f"LLM OCR successful for {image_path.name}")
                    return result
                else:
                    logger.warning(f"LLM OCR failed for {image_path.name}: {result.error_message}")

                    # Tesseract으로 폴백 (전처리된 이미지 사용)
                    if self.config.fallback_to_tesseract and self.config.tesseract_available:
                        return await self._tesseract_ocr(processed_image_path, language, preprocessing_metadata)
                    else:
                        # 전처리 메타데이터 추가
                        if hasattr(result, 'metadata') and result.metadata:
                            result.metadata.update(preprocessing_metadata)
                        else:
                            result.metadata = preprocessing_metadata
                        return result

            except Exception as e:
                logger.error(f"LLM OCR error for {image_path.name}: {e}")

                # Tesseract으로 폴백 (전처리된 이미지 사용)
                if self.config.fallback_to_tesseract and self.config.tesseract_available:
                    return await self._tesseract_ocr(processed_image_path, language, preprocessing_metadata)
                else:
                    return OCRResult(
                        text="",
                        error_message=f"LLM OCR failed: {str(e)}",
                        metadata=preprocessing_metadata
                    )

        # Tesseract OCR 직접 사용 (전처리된 이미지 사용)
        elif self.config.tesseract_available:
            return await self._tesseract_ocr(processed_image_path, language, preprocessing_metadata)

        else:
            return OCRResult(
                text="",
                error_message="No OCR method available (LLM disabled, Tesseract not available)",
                metadata=preprocessing_metadata
            )
    
    async def _tesseract_ocr(self, image_path: Path, language: str = "auto", preprocessing_metadata: Optional[Dict] = None) -> OCRResult:
        """
        Tesseract를 사용한 OCR

        Args:
            image_path: 이미지 경로
            language: 언어 코드
            preprocessing_metadata: 전처리 메타데이터

        Returns:
            OCR 결과
        """
        try:
            import pytesseract
            from PIL import Image
            import time
            
            # 언어 매핑
            lang_map = {
                "auto": "eng",
                "ko": "kor",
                "en": "eng", 
                "zh": "chi_sim",
                "ja": "jpn"
            }
            tesseract_lang = lang_map.get(language, "eng")
            
            start_time = time.time()
            
            # 이미지 로드 및 전처리
            with Image.open(image_path) as image:
                # 그레이스케일 변환
                if image.mode != 'L':
                    image = image.convert('L')
                
                # OCR 실행
                text = pytesseract.image_to_string(
                    image,
                    lang=tesseract_lang,
                    config='--oem 3 --psm 6'  # 최적 설정
                )
                
                processing_time = time.time() - start_time
                
                # 신뢰도 추정 (간단한 휴리스틱)
                confidence = min(0.8, max(0.3, len(text.strip()) / 100))
                
                # 전처리 메타데이터 포함
                metadata = preprocessing_metadata or {}
                metadata.update({
                    'ocr_method': 'tesseract',
                    'tesseract_lang': tesseract_lang,
                    'tesseract_config': '--oem 3 --psm 6'
                })

                return OCRResult(
                    text=text.strip(),
                    confidence=confidence,
                    language_detected=language if language != "auto" else "en",
                    processing_time=processing_time,
                    metadata=metadata
                )
                
        except ImportError:
            metadata = preprocessing_metadata or {}
            metadata.update({'ocr_method': 'tesseract', 'error_type': 'import_error'})
            return OCRResult(
                text="",
                error_message="Tesseract dependencies not available",
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            metadata = preprocessing_metadata or {}
            metadata.update({'ocr_method': 'tesseract', 'error_type': 'processing_error'})
            return OCRResult(
                text="",
                error_message=f"Tesseract OCR failed: {str(e)}",
                metadata=metadata
            )
    
    async def extract_text_from_pdf(
        self,
        pdf_path: Path,
        page_range: Optional[tuple] = None,
        language: str = "auto"
    ) -> List[OCRResult]:
        """
        PDF에서 텍스트 추출 (이미지 PDF의 경우 OCR 적용)
        
        Args:
            pdf_path: PDF 파일 경로
            page_range: 페이지 범위 (start, end) 또는 None (전체)
            language: OCR 언어
        
        Returns:
            페이지별 OCR 결과 리스트
        """
        if not pdf_path.exists():
            return [OCRResult(
                text="",
                error_message=f"PDF file not found: {pdf_path}"
            )]
        
        results = []
        
        try:
            # PDF를 이미지로 변환하여 OCR 적용
            images = await self._pdf_to_images(pdf_path, page_range)
            
            for i, image_path in enumerate(images):
                try:
                    result = await self.extract_text_from_image(image_path, language)
                    
                    # 페이지 정보 추가
                    if result.is_success:
                        result.text = f"<!-- Page {i+1} -->\n{result.text}\n"
                    
                    results.append(result)
                    
                finally:
                    # 임시 이미지 파일 정리
                    if image_path.exists():
                        try:
                            image_path.unlink()
                        except Exception:
                            pass
                            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            results.append(OCRResult(
                text="",
                error_message=f"PDF processing failed: {str(e)}"
            ))
        
        return results
    
    async def _pdf_to_images(
        self,
        pdf_path: Path,
        page_range: Optional[tuple] = None
    ) -> List[Path]:
        """
        PDF를 이미지로 변환
        
        Args:
            pdf_path: PDF 경로
            page_range: 페이지 범위
        
        Returns:
            이미지 경로 리스트
        """
        try:
            import pdf2image
            
            # PDF를 이미지로 변환
            if page_range:
                start_page, end_page = page_range
                images = pdf2image.convert_from_path(
                    pdf_path,
                    first_page=start_page,
                    last_page=end_page,
                    dpi=150  # 적절한 해상도
                )
            else:
                images = pdf2image.convert_from_path(pdf_path, dpi=150)
            
            # 임시 파일로 저장
            image_paths = []
            temp_dir = Path(tempfile.gettempdir()) / "markitdown_ocr"
            temp_dir.mkdir(exist_ok=True)
            
            for i, image in enumerate(images):
                temp_path = temp_dir / f"page_{i+1}_{pdf_path.stem}.png"
                image.save(temp_path, "PNG")
                image_paths.append(temp_path)
            
            return image_paths
            
        except ImportError:
            raise ImportError("pdf2image is required for PDF processing")
        except Exception as e:
            raise Exception(f"Failed to convert PDF to images: {e}")
    
    async def process_file(self, file_info: FileInfo) -> Optional[str]:
        """
        파일 처리 (MarkItDown 통합용)
        
        Args:
            file_info: 파일 정보
        
        Returns:
            추출된 텍스트 (OCR 적용된 경우만)
        """
        if not self.is_supported_format(file_info.path):
            return None
        
        try:
            if file_info.file_type == FileType.PDF:
                # PDF OCR 처리
                results = await self.extract_text_from_pdf(file_info.path)
                
                if results and any(r.is_success for r in results):
                    # 성공한 페이지들의 텍스트 합치기
                    texts = [r.text for r in results if r.is_success]
                    return "\n\n".join(texts)
                else:
                    return None
                    
            else:
                # 이미지 OCR 처리
                result = await self.extract_text_from_image(file_info.path)
                
                if result.is_success:
                    return result.text
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"OCR processing failed for {file_info.path}: {e}")
            return None
    
    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 반환"""
        extensions = self.config.supported_formats.copy()
        extensions.append('pdf')
        return extensions
    
    def get_service_info(self) -> Dict[str, any]:
        """서비스 정보 반환"""
        info = {
            'llm_ocr_enabled': (
                self.config.enabled and
                self.llm_manager.current_config and
                self.llm_manager.current_config.enable_ocr
            ),
            'tesseract_available': self.config.tesseract_available,
            'fallback_enabled': self.config.fallback_to_tesseract,
            'supported_formats': self.config.supported_formats,
            'max_image_size': self.config.max_image_size,
            'preprocessing_enabled': self.config.enable_preprocessing,
            'preprocessing_available': self.preprocessing_pipeline is not None
        }

        # 전처리 통계 추가 (가능한 경우)
        if self.preprocessing_pipeline:
            try:
                preprocessing_stats = self.preprocessing_pipeline.get_statistics()
                info['preprocessing_stats'] = preprocessing_stats
            except Exception as e:
                logger.debug(f"Could not get preprocessing statistics: {e}")

        return info


# OCR 서비스 통합을 위한 헬퍼 함수들

async def enhance_markitdown_conversion(
    file_info: FileInfo,
    original_content: str,
    ocr_service: OCRService
) -> str:
    """
    MarkItDown 변환 결과를 OCR로 향상
    
    Args:
        file_info: 파일 정보
        original_content: 원본 변환 내용
        ocr_service: OCR 서비스
    
    Returns:
        향상된 내용
    """
    # 이미지나 PDF에 OCR 적용 가능한 경우
    if ocr_service.is_supported_format(file_info.path):
        ocr_content = await ocr_service.process_file(file_info)
        
        if ocr_content:
            # OCR 내용이 있으면 원본과 결합
            enhanced_content = f"{original_content}\n\n<!-- OCR Extracted Text -->\n{ocr_content}"
            logger.info(f"Enhanced conversion with OCR for {file_info.name}")
            return enhanced_content
    
    return original_content


def create_ocr_enabled_converter():
    """OCR가 활성화된 변환기 생성 함수"""
    # 이는 conversion_manager.py에서 사용될 예정
    pass
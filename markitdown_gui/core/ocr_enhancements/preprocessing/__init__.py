"""
Image Preprocessing Module for OCR Enhancement
이미지 전처리 모듈 - OCR 정확도 향상을 위한 이미지 전처리 기능

이 모듈은 OCR 전에 이미지를 최적화하여 텍스트 인식 정확도를 향상시킵니다.
"""

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .image_enhancer import ImageEnhancer
    from .quality_analyzer import QualityAnalyzer
    from .preprocessing_pipeline import PreprocessingPipeline

logger = logging.getLogger(__name__)

# 모듈 활성화 상태
_is_enabled = False
_pipeline: Optional['PreprocessingPipeline'] = None

def is_preprocessing_enabled() -> bool:
    """
    이미지 전처리 모듈 활성화 상태 확인

    Returns:
        모듈 활성화 여부
    """
    return _is_enabled

def get_preprocessing_pipeline() -> Optional['PreprocessingPipeline']:
    """
    전처리 파이프라인 인스턴스 반환

    Returns:
        PreprocessingPipeline 인스턴스 또는 None (비활성화된 경우)
    """
    return _pipeline if _is_enabled else None

def initialize_preprocessing(config: Optional[dict] = None) -> bool:
    """
    이미지 전처리 모듈 초기화

    Args:
        config: 전처리 설정 딕셔너리

    Returns:
        초기화 성공 여부
    """
    global _is_enabled, _pipeline

    try:
        # 의존성 확인
        if not _check_dependencies():
            logger.warning("Image preprocessing dependencies not available")
            _is_enabled = False
            _pipeline = None
            return False

        # 모듈 초기화
        from .preprocessing_pipeline import PreprocessingPipeline
        _pipeline = PreprocessingPipeline(config or {})
        _is_enabled = True

        logger.info("Image preprocessing module initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize image preprocessing module: {e}")
        _is_enabled = False
        _pipeline = None
        return False

def shutdown_preprocessing():
    """이미지 전처리 모듈 종료"""
    global _is_enabled, _pipeline

    if _pipeline:
        try:
            _pipeline.cleanup()
        except Exception as e:
            logger.error(f"Error during preprocessing module shutdown: {e}")

    _is_enabled = False
    _pipeline = None
    logger.info("Image preprocessing module shutdown completed")

def _check_dependencies() -> bool:
    """
    필수 의존성 확인

    Returns:
        의존성 만족 여부
    """
    try:
        # PIL/Pillow 확인
        from PIL import Image, ImageEnhance, ImageFilter

        # NumPy 확인
        import numpy as np

        # 기본 라이브러리들 확인
        import asyncio
        from pathlib import Path
        import tempfile
        import math

        # OpenCV 확인 (선택적)
        try:
            import cv2
            logger.info("OpenCV available for advanced image processing")
        except ImportError:
            logger.info("OpenCV not available, using PIL-only implementation")

        # scikit-image 확인 (선택적)
        try:
            import skimage
            logger.info("scikit-image available for advanced algorithms")
        except ImportError:
            logger.info("scikit-image not available, using basic algorithms")

        return True

    except ImportError as e:
        logger.debug(f"Image preprocessing dependency missing: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking image preprocessing dependencies: {e}")
        return False

# Safe imports - 모듈이 비활성화되어도 import 에러가 발생하지 않도록
try:
    from .image_enhancer import ImageEnhancer, EnhancementResult
    from .quality_analyzer import QualityAnalyzer, ImageQuality, QualityMetrics
    from .preprocessing_pipeline import PreprocessingPipeline, PreprocessingConfig

    __all__ = [
        'is_preprocessing_enabled',
        'get_preprocessing_pipeline',
        'initialize_preprocessing',
        'shutdown_preprocessing',
        'ImageEnhancer',
        'QualityAnalyzer',
        'PreprocessingPipeline',
        'EnhancementResult',
        'ImageQuality',
        'QualityMetrics',
        'PreprocessingConfig'
    ]

except ImportError as e:
    logger.debug(f"Image preprocessing components not available: {e}")
    __all__ = [
        'is_preprocessing_enabled',
        'get_preprocessing_pipeline',
        'initialize_preprocessing',
        'shutdown_preprocessing'
    ]

# 버전 정보
__version__ = "1.0.0"
__author__ = "MarkItDown GUI Team"
__description__ = "Image Preprocessing Module for OCR Enhancement"
"""
OCR Enhancement Module
OCR 기능 개선을 위한 독립적인 모듈

이 모듈은 기존 OCR 서비스를 개선하는 추가 기능들을 제공합니다.
feature flag를 통해 활성화/비활성화가 가능하며, 기존 시스템에 영향을 주지 않습니다.
"""

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .ocr_enhancement_manager import OCREnhancementManager
    from .models import OCREnhancementConfig

logger = logging.getLogger(__name__)

# 모듈 활성화 상태
_is_enabled = False
_enhancement_manager: Optional['OCREnhancementManager'] = None

def is_module_enabled() -> bool:
    """
    OCR Enhancement Module 활성화 상태 확인

    Returns:
        모듈 활성화 여부
    """
    return _is_enabled

def get_enhancement_manager() -> Optional['OCREnhancementManager']:
    """
    OCR Enhancement Manager 인스턴스 반환

    Returns:
        OCREnhancementManager 인스턴스 또는 None (비활성화된 경우)
    """
    return _enhancement_manager if _is_enabled else None

def initialize_module(config: Optional['OCREnhancementConfig'] = None) -> bool:
    """
    OCR Enhancement Module 초기화

    Args:
        config: OCR Enhancement 설정

    Returns:
        초기화 성공 여부
    """
    global _is_enabled, _enhancement_manager

    try:
        # feature flag 확인
        if config and not config.enabled:
            logger.info("OCR Enhancement Module is disabled by configuration")
            _is_enabled = False
            _enhancement_manager = None
            return True

        # 의존성 확인
        if not _check_dependencies():
            logger.warning("OCR Enhancement Module dependencies not available")
            _is_enabled = False
            _enhancement_manager = None
            return False

        # 모듈 초기화
        from .ocr_enhancement_manager import OCREnhancementManager
        _enhancement_manager = OCREnhancementManager(config)
        _is_enabled = True

        logger.info("OCR Enhancement Module initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize OCR Enhancement Module: {e}")
        _is_enabled = False
        _enhancement_manager = None
        return False

def shutdown_module():
    """OCR Enhancement Module 종료"""
    global _is_enabled, _enhancement_manager

    if _enhancement_manager:
        try:
            _enhancement_manager.shutdown()
        except Exception as e:
            logger.error(f"Error during OCR Enhancement Module shutdown: {e}")

    _is_enabled = False
    _enhancement_manager = None
    logger.info("OCR Enhancement Module shutdown completed")

def _check_dependencies() -> bool:
    """
    필수 의존성 확인

    Returns:
        의존성 만족 여부
    """
    try:
        # 기존 OCR 서비스 사용 가능성 확인
        from ..ocr_service import OCRService

        # 기본 라이브러리들 확인
        import asyncio
        from pathlib import Path

        return True

    except ImportError as e:
        logger.debug(f"OCR Enhancement Module dependency missing: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking OCR Enhancement Module dependencies: {e}")
        return False

# Safe imports - 모듈이 비활성화되어도 import 에러가 발생하지 않도록
try:
    from .models import (
        OCREnhancementConfig,
        OCRStatusInfo,
        OCRProgressInfo,
        OCREnhancementResult
    )

    # 모듈이 활성화된 경우에만 manager import
    if _is_enabled:
        from .ocr_enhancement_manager import OCREnhancementManager

    __all__ = [
        'is_module_enabled',
        'get_enhancement_manager',
        'initialize_module',
        'shutdown_module',
        'OCREnhancementConfig',
        'OCRStatusInfo',
        'OCRProgressInfo',
        'OCREnhancementResult'
    ]

    # Manager는 활성화된 경우에만 export
    if _is_enabled:
        __all__.append('OCREnhancementManager')

except ImportError as e:
    logger.debug(f"OCR Enhancement Module components not available: {e}")
    __all__ = [
        'is_module_enabled',
        'get_enhancement_manager',
        'initialize_module',
        'shutdown_module'
    ]

# 버전 정보
__version__ = "1.0.0"
__author__ = "MarkItDown GUI Team"
__description__ = "OCR Enhancement Module for advanced OCR capabilities"
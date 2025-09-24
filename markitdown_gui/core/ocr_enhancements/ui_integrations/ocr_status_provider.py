"""
OCR Status Provider
OCR 상태 제공자

Provides OCR status badges and integration hooks for FileListWidget.
Manages status display, badge generation, and caching for performance.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QPen, QBrush
from typing import Dict, Optional, Tuple, Union
from pathlib import Path
from functools import lru_cache

from ..models import (
    OCREnhancementConfig, OCRStatusType, QualityLevel,
    OCREnhancementResult, OCRStatusInfo
)
from ...models import FileInfo, ConversionStatus
from ...logger import get_logger

logger = get_logger(__name__)


class OCRStatusBadge(QLabel):
    """OCR 상태 배지 위젯"""

    def __init__(self, status_type: Optional[OCRStatusType] = None,
                 quality_level: Optional[QualityLevel] = None):
        super().__init__()
        self.setFixedSize(20, 16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(True)

        self._status_type = status_type
        self._quality_level = quality_level
        self._update_badge()

    def _update_badge(self):
        """배지 업데이트"""
        if self._status_type is None:
            self.setVisible(False)
            return

        self.setVisible(True)

        # 상태별 텍스트와 색상
        status_config = self._get_status_config(self._status_type, self._quality_level)

        # 툴팁 설정
        tooltip = self._generate_tooltip(self._status_type, self._quality_level)
        self.setToolTip(tooltip)

        # 배지 이미지 생성
        pixmap = self._create_badge_pixmap(status_config)
        self.setPixmap(pixmap)

    def _get_status_config(self, status: OCRStatusType,
                          quality: Optional[QualityLevel] = None) -> Dict:
        """상태별 설정 반환"""
        configs = {
            OCRStatusType.IDLE: {
                'text': '',
                'bg_color': '#E0E0E0',
                'text_color': '#757575',
                'visible': False
            },
            OCRStatusType.INITIALIZING: {
                'text': '초기',
                'bg_color': '#FFC107',
                'text_color': '#FFFFFF'
            },
            OCRStatusType.PREPROCESSING: {
                'text': '전처리',
                'bg_color': '#FF9800',
                'text_color': '#FFFFFF'
            },
            OCRStatusType.PROCESSING: {
                'text': 'OCR',
                'bg_color': '#2196F3',
                'text_color': '#FFFFFF'
            },
            OCRStatusType.POST_PROCESSING: {
                'text': '후처리',
                'bg_color': '#673AB7',
                'text_color': '#FFFFFF'
            },
            OCRStatusType.ANALYZING: {
                'text': '분석',
                'bg_color': '#9C27B0',
                'text_color': '#FFFFFF'
            },
            OCRStatusType.COMPLETED: {
                'text': self._get_quality_text(quality),
                'bg_color': self._get_quality_color(quality),
                'text_color': '#FFFFFF'
            },
            OCRStatusType.FAILED: {
                'text': '실패',
                'bg_color': '#F44336',
                'text_color': '#FFFFFF'
            },
            OCRStatusType.CANCELLED: {
                'text': '취소',
                'bg_color': '#795548',
                'text_color': '#FFFFFF'
            }
        }

        return configs.get(status, configs[OCRStatusType.IDLE])

    def _get_quality_text(self, quality: Optional[QualityLevel]) -> str:
        """품질 수준별 텍스트"""
        if quality is None:
            return '완료'

        quality_texts = {
            QualityLevel.EXCELLENT: '최고',
            QualityLevel.GOOD: '좋음',
            QualityLevel.FAIR: '보통',
            QualityLevel.POOR: '낮음',
            QualityLevel.VERY_POOR: '매우낮음'
        }
        return quality_texts.get(quality, '완료')

    def _get_quality_color(self, quality: Optional[QualityLevel]) -> str:
        """품질 수준별 색상"""
        if quality is None:
            return '#4CAF50'

        quality_colors = {
            QualityLevel.EXCELLENT: '#2E7D32',  # Dark Green
            QualityLevel.GOOD: '#4CAF50',       # Green
            QualityLevel.FAIR: '#FF9800',       # Orange
            QualityLevel.POOR: '#F57C00',       # Dark Orange
            QualityLevel.VERY_POOR: '#D32F2F'   # Red
        }
        return quality_colors.get(quality, '#4CAF50')

    def _generate_tooltip(self, status: OCRStatusType,
                         quality: Optional[QualityLevel] = None) -> str:
        """툴팁 생성"""
        status_descriptions = {
            OCRStatusType.IDLE: "OCR 대기 중",
            OCRStatusType.INITIALIZING: "OCR 초기화 중",
            OCRStatusType.PREPROCESSING: "이미지 전처리 중",
            OCRStatusType.PROCESSING: "OCR 처리 중",
            OCRStatusType.POST_PROCESSING: "텍스트 후처리 중",
            OCRStatusType.ANALYZING: "품질 분석 중",
            OCRStatusType.COMPLETED: "OCR 완료",
            OCRStatusType.FAILED: "OCR 실패",
            OCRStatusType.CANCELLED: "OCR 취소됨"
        }

        base_tooltip = status_descriptions.get(status, "알 수 없는 상태")

        if status == OCRStatusType.COMPLETED and quality:
            quality_descriptions = {
                QualityLevel.EXCELLENT: "최고 품질 (95-100%)",
                QualityLevel.GOOD: "좋은 품질 (80-94%)",
                QualityLevel.FAIR: "보통 품질 (60-79%)",
                QualityLevel.POOR: "낮은 품질 (40-59%)",
                QualityLevel.VERY_POOR: "매우 낮은 품질 (0-39%)"
            }
            quality_desc = quality_descriptions.get(quality, "알 수 없음")
            base_tooltip += f" - {quality_desc}"

        return base_tooltip

    def _create_badge_pixmap(self, config: Dict) -> QPixmap:
        """배지 픽스맵 생성"""
        if not config.get('visible', True):
            return QPixmap()

        width, height = 20, 16
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 배경 그리기
        bg_color = QColor(config['bg_color'])
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(bg_color))
        painter.drawRoundedRect(0, 0, width, height, 3, 3)

        # 텍스트 그리기
        text = config['text']
        if text:
            font = QFont("맑은 고딕", 7, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(QColor(config['text_color'])))

            # 텍스트 중앙 정렬
            text_rect = painter.fontMetrics().boundingRect(text)
            x = (width - text_rect.width()) // 2
            y = (height + text_rect.height()) // 2 - 2
            painter.drawText(x, y, text)

        painter.end()
        return pixmap

    def update_status(self, status_type: OCRStatusType,
                     quality_level: Optional[QualityLevel] = None):
        """상태 업데이트"""
        self._status_type = status_type
        self._quality_level = quality_level
        self._update_badge()


class OCRMethodBadge(QLabel):
    """OCR 방법 배지 (LLM/Tesseract/Offline)"""

    def __init__(self, method: Optional[str] = None):
        super().__init__()
        self.setFixedSize(24, 16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(True)

        self._method = method
        self._update_badge()

    def _update_badge(self):
        """배지 업데이트"""
        if not self._method:
            self.setVisible(False)
            return

        self.setVisible(True)

        # 방법별 설정
        method_config = self._get_method_config(self._method)

        # 툴팁 설정
        self.setToolTip(method_config['tooltip'])

        # 배지 이미지 생성
        pixmap = self._create_method_pixmap(method_config)
        self.setPixmap(pixmap)

    def _get_method_config(self, method: str) -> Dict:
        """방법별 설정"""
        configs = {
            'llm': {
                'text': 'LLM',
                'bg_color': '#4CAF50',
                'text_color': '#FFFFFF',
                'tooltip': 'LLM 기반 OCR (최고 품질)'
            },
            'tesseract': {
                'text': 'TES',
                'bg_color': '#2196F3',
                'text_color': '#FFFFFF',
                'tooltip': 'Tesseract OCR (표준 품질)'
            },
            'offline': {
                'text': 'OFF',
                'bg_color': '#FF9800',
                'text_color': '#FFFFFF',
                'tooltip': '오프라인 OCR (기본 품질)'
            }
        }

        return configs.get(method.lower(), {
            'text': 'UNK',
            'bg_color': '#9E9E9E',
            'text_color': '#FFFFFF',
            'tooltip': '알 수 없는 OCR 방법'
        })

    def _create_method_pixmap(self, config: Dict) -> QPixmap:
        """방법 배지 픽스맵 생성"""
        width, height = 24, 16
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 배경 그리기
        bg_color = QColor(config['bg_color'])
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(bg_color))
        painter.drawRoundedRect(0, 0, width, height, 2, 2)

        # 텍스트 그리기
        font = QFont("맑은 고딕", 6, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(config['text_color'])))

        text_rect = painter.fontMetrics().boundingRect(config['text'])
        x = (width - text_rect.width()) // 2
        y = (height + text_rect.height()) // 2 - 1
        painter.drawText(x, y, config['text'])

        painter.end()
        return pixmap

    def update_method(self, method: str):
        """방법 업데이트"""
        self._method = method
        self._update_badge()


class OCRStatusProvider(QObject):
    """OCR 상태 제공자 - FileListWidget 통합용"""

    # 시그널
    status_updated = pyqtSignal(str, OCRStatusType)  # file_path, status
    badge_requested = pyqtSignal(str)  # file_path

    def __init__(self, config: OCREnhancementConfig):
        super().__init__()
        self.config = config
        self._status_cache: Dict[str, Tuple[OCRStatusType, Optional[QualityLevel]]] = {}
        self._method_cache: Dict[str, str] = {}
        self._badge_cache: Dict[str, QWidget] = {}

        logger.debug("OCRStatusProvider 초기화됨")

    def is_ocr_enabled(self) -> bool:
        """OCR 개선 기능이 활성화되어 있는지 확인"""
        return self.config.enabled and self.config.is_any_enhancement_enabled()

    def create_status_badge_widget(self, file_info: FileInfo) -> Optional[QWidget]:
        """파일에 대한 OCR 상태 배지 위젯 생성"""
        if not self.is_ocr_enabled():
            return None

        # 이미지 파일만 OCR 적용
        if not self._is_image_file(file_info):
            return None

        file_path = str(file_info.path)

        # 캐시에서 확인
        cached_widget = self._badge_cache.get(file_path)
        if cached_widget:
            return cached_widget

        # 새 위젯 생성
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(2)

        # OCR 방법 배지
        method = self._get_ocr_method(file_info)
        if method:
            method_badge = OCRMethodBadge(method)
            layout.addWidget(method_badge)

        # OCR 상태 배지
        status_type, quality_level = self._get_ocr_status(file_info)
        if status_type != OCRStatusType.IDLE:
            status_badge = OCRStatusBadge(status_type, quality_level)
            layout.addWidget(status_badge)

        # 위젯이 비어있으면 None 반환
        if layout.count() == 0:
            return None

        # 캐시에 저장
        self._badge_cache[file_path] = widget

        return widget

    def update_file_status(self, file_info: FileInfo, status: OCRStatusType,
                          quality_level: Optional[QualityLevel] = None,
                          ocr_method: Optional[str] = None):
        """파일의 OCR 상태 업데이트"""
        file_path = str(file_info.path)

        # 상태 캐시 업데이트
        self._status_cache[file_path] = (status, quality_level)

        # 방법 캐시 업데이트
        if ocr_method:
            self._method_cache[file_path] = ocr_method

        # 배지 캐시 무효화
        self._badge_cache.pop(file_path, None)

        # 시그널 발송
        self.status_updated.emit(file_path, status)

        logger.debug(f"OCR 상태 업데이트: {file_info.name} -> {status.value}")

    def update_from_enhancement_result(self, result: OCREnhancementResult):
        """OCR 개선 결과로부터 상태 업데이트"""
        status = result.status_info.status
        quality = result.quality_metrics.overall_quality

        # 적용된 방법 추정
        method = self._determine_method_from_result(result)

        self.update_file_status(
            result.file_info,
            status,
            quality if status == OCRStatusType.COMPLETED else None,
            method
        )

    def get_status_summary(self, file_info: FileInfo) -> Optional[str]:
        """파일의 OCR 상태 요약 반환"""
        if not self.is_ocr_enabled() or not self._is_image_file(file_info):
            return None

        file_path = str(file_info.path)
        cached_status = self._status_cache.get(file_path)

        if not cached_status:
            return "OCR 대기 중"

        status_type, quality_level = cached_status

        if status_type == OCRStatusType.COMPLETED and quality_level:
            return f"OCR 완료 - {quality_level.value}"
        else:
            return f"OCR {status_type.value}"

    def clear_cache(self):
        """캐시 정리"""
        self._status_cache.clear()
        self._method_cache.clear()
        self._badge_cache.clear()
        logger.debug("OCR 상태 캐시 정리됨")

    def _is_image_file(self, file_info: FileInfo) -> bool:
        """이미지 파일 여부 확인"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
        return file_info.path.suffix.lower() in image_extensions

    def _get_ocr_status(self, file_info: FileInfo) -> Tuple[OCRStatusType, Optional[QualityLevel]]:
        """파일의 OCR 상태 가져오기"""
        file_path = str(file_info.path)
        cached_status = self._status_cache.get(file_path)

        if cached_status:
            return cached_status

        # 기본 상태
        return OCRStatusType.IDLE, None

    def _get_ocr_method(self, file_info: FileInfo) -> Optional[str]:
        """파일의 OCR 방법 가져오기"""
        file_path = str(file_info.path)
        return self._method_cache.get(file_path)

    def _determine_method_from_result(self, result: OCREnhancementResult) -> str:
        """개선 결과로부터 사용된 방법 추정"""
        # 개선 유형에 따라 방법 추정
        if any('llm' in str(enhancement).lower() for enhancement in result.applied_enhancements):
            return 'llm'
        elif result.quality_metrics.confidence_score > 0.8:
            return 'tesseract'
        else:
            return 'offline'

    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        return {
            'status_cache_size': self._status_cache.size(),
            'method_cache_size': self._method_cache.size(),
            'badge_cache_size': self._badge_cache.size(),
            'status_cache_max': self._status_cache.maxCost(),
            'method_cache_max': self._method_cache.maxCost(),
            'badge_cache_max': self._badge_cache.maxCost()
        }
"""
Accessibility Validator System
WCAG 2.1 AA compliance validation for PyQt6 applications
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import colorsys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog, QLabel, QPushButton,
    QCheckBox, QComboBox, QLineEdit, QTextEdit, QProgressBar, QSlider,
    QTabWidget, QGroupBox, QListWidget, QTreeWidget, QTableWidget,
    QScrollArea, QSplitter, QStackedWidget, QFrame, QToolButton
)
from PyQt6.QtCore import QObject, QSettings, Qt, QRect, QSize, QTimer
from PyQt6.QtGui import (
    QColor, QPalette, QFont, QFontMetrics, QPainter, QPixmap, QImage
)
# Import accessibility classes from compatibility layer
from .qt_compatibility import QAccessible, is_accessibility_available

from .logger import get_logger


logger = get_logger(__name__)


class WCAGLevel(Enum):
    """WCAG 준수 수준"""
    A = "A"
    AA = "AA"  
    AAA = "AAA"


class WCAGPrinciple(Enum):
    """WCAG 4대 원칙"""
    PERCEIVABLE = "perceivable"          # 인식 가능
    OPERABLE = "operable"                # 작동 가능  
    UNDERSTANDABLE = "understandable"    # 이해 가능
    ROBUST = "robust"                    # 견고성


class ValidationSeverity(Enum):
    """검증 결과 심각도"""
    CRITICAL = "critical"    # 즉시 수정 필요
    MAJOR = "major"         # 중요한 문제
    MINOR = "minor"         # 경미한 문제
    WARNING = "warning"     # 권고사항
    INFO = "info"          # 정보성


@dataclass
class ValidationIssue:
    """검증 문제"""
    guideline: str           # WCAG 가이드라인 번호 (예: "1.4.3")
    title: str              # 문제 제목
    description: str        # 문제 설명
    severity: ValidationSeverity  # 심각도
    level: WCAGLevel        # 해당 WCAG 레벨
    principle: WCAGPrinciple  # 해당 원칙
    widget: Optional[QWidget] = None  # 관련 위젯
    location: str = ""      # 위치 정보
    recommendation: str = ""  # 수정 권고사항
    help_url: str = ""      # 도움말 URL
    auto_fixable: bool = False  # 자동 수정 가능 여부
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "guideline": self.guideline,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "level": self.level.value,
            "principle": self.principle.value,
            "location": self.location,
            "recommendation": self.recommendation,
            "help_url": self.help_url,
            "auto_fixable": self.auto_fixable
        }


@dataclass
class ValidationResult:
    """검증 결과"""
    total_widgets: int
    tested_widgets: int
    issues: List[ValidationIssue]
    score: float  # 0-100
    level_scores: Dict[WCAGLevel, float] = field(default_factory=dict)
    principle_scores: Dict[WCAGPrinciple, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
    
    @property
    def major_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.MAJOR]
    
    @property
    def passed_tests(self) -> int:
        return max(0, self.tested_widgets - len(self.issues))
    
    def get_compliance_level(self) -> Optional[WCAGLevel]:
        """달성 가능한 최고 준수 수준 반환"""
        try:
            if self.tested_widgets == 0:
                return None  # 테스트된 위젯이 없으면 평가 불가
                
            critical_count = len(self.critical_issues)
            major_count = len(self.major_issues)
            total_issues = len(self.issues)
            
            # AAA 레벨: 90점 이상, 심각한 이슈 없음, 중요 이슈 최소
            if self.score >= 90 and critical_count == 0 and major_count <= 1:
                return WCAGLevel.AAA
            # AA 레벨: 80점 이상, 심각한 이슈 없음
            elif self.score >= 80 and critical_count == 0:
                return WCAGLevel.AA
            # A 레벨: 60점 이상, 심각한 이슈가 전체의 5% 이하
            elif self.score >= 60 and critical_count <= max(1, self.tested_widgets * 0.05):
                return WCAGLevel.A
            else:
                return None  # 기본 준수 수준 미달성
        except Exception:
            return None


class ColorContrastValidator:
    """색상 대비 검증기"""
    
    # WCAG 대비율 기준
    CONTRAST_RATIOS = {
        WCAGLevel.AA: {"normal": 4.5, "large": 3.0},
        WCAGLevel.AAA: {"normal": 7.0, "large": 4.5}
    }
    
    @staticmethod
    def calculate_contrast_ratio(color1: QColor, color2: QColor) -> float:
        """두 색상 간 대비율 계산"""
        try:
            l1 = ColorContrastValidator._get_relative_luminance(color1)
            l2 = ColorContrastValidator._get_relative_luminance(color2)
            
            # 더 밝은 색을 분자에
            lighter = max(l1, l2)
            darker = min(l1, l2)
            
            return (lighter + 0.05) / (darker + 0.05)
            
        except Exception as e:
            logger.error(f"Error calculating contrast ratio: {e}")
            return 1.0
    
    @staticmethod
    def _get_relative_luminance(color: QColor) -> float:
        """상대적 휘도 계산"""
        try:
            # RGB 값을 0-1 범위로 정규화
            r = color.red() / 255.0
            g = color.green() / 255.0  
            b = color.blue() / 255.0
            
            # sRGB 색공간 변환
            def srgb_to_linear(c):
                if c <= 0.03928:
                    return c / 12.92
                else:
                    return pow((c + 0.055) / 1.055, 2.4)
            
            r_linear = srgb_to_linear(r)
            g_linear = srgb_to_linear(g)
            b_linear = srgb_to_linear(b)
            
            # 상대적 휘도 계산
            return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
            
        except Exception as e:
            logger.error(f"Error calculating relative luminance: {e}")
            return 0.0
    
    @staticmethod
    def is_large_text(font: QFont) -> bool:
        """대형 텍스트 여부 판단 (18pt 이상 또는 14pt 이상 굵게)"""
        try:
            point_size = font.pointSize()
            if point_size >= 18:
                return True
            elif point_size >= 14 and font.weight() >= QFont.Weight.Bold.value:
                return True
            return False
        except:
            return False
    
    def validate_widget_contrast(self, widget: QWidget, level: WCAGLevel = WCAGLevel.AA) -> List[ValidationIssue]:
        """위젯의 색상 대비 검증"""
        issues = []
        
        if not widget or not widget.isVisible():
            return issues
        
        try:
            palette = widget.palette()
            
            # 텍스트와 배경 대비 검사
            text_color = palette.color(QPalette.ColorRole.WindowText)
            bg_color = palette.color(QPalette.ColorRole.Window)
            
            # 색상 유효성 검사
            if not text_color.isValid() or not bg_color.isValid():
                return issues
                
            # 투명도 검사 - 완전 투명한 색상은 제외
            if text_color.alpha() == 0 or bg_color.alpha() == 0:
                return issues
            
            contrast_ratio = self.calculate_contrast_ratio(text_color, bg_color)
            
            # 대비율이 1.0 (동일한 색상)이면 문제
            if contrast_ratio <= 1.1:  # 약간의 오차 허용
                issues.append(ValidationIssue(
                    guideline="1.4.3",
                    title="색상 대비 없음",
                    description="텍스트와 배경이 같은 색상입니다",
                    severity=ValidationSeverity.CRITICAL,
                    level=WCAGLevel.A,
                    principle=WCAGPrinciple.PERCEIVABLE,
                    widget=widget,
                    location=self._get_widget_location(widget),
                    recommendation="텍스트와 배경에 서로 다른 색상을 사용하세요"
                ))
                return issues
            
            # 텍스트 크기 확인
            font = widget.font()
            if not font or font.pointSize() <= 0:
                font = QFont()  # 기본 폰트 사용
            is_large = self.is_large_text(font)
            
            # 기준값 확인
            required_ratio = self.CONTRAST_RATIOS[level]["large" if is_large else "normal"]
            
            if contrast_ratio < required_ratio and contrast_ratio > 1.0:  # 유효한 대비율 범위 내에서만
                issues.append(ValidationIssue(
                    guideline="1.4.3" if level == WCAGLevel.AA else "1.4.6",
                    title="색상 대비 부족",
                    description=f"현재 대비율 {contrast_ratio:.1f}:1, 필요 대비율 {required_ratio}:1",
                    severity=ValidationSeverity.MAJOR if level == WCAGLevel.AA else ValidationSeverity.MINOR,
                    level=level,
                    principle=WCAGPrinciple.PERCEIVABLE,
                    widget=widget,
                    location=self._get_widget_location(widget),
                    recommendation=f"텍스트와 배경 색상의 대비를 {required_ratio}:1 이상으로 조정하세요",
                    help_url="https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html"
                ))
            
            # 버튼 포커스 상태 대비 검사 
            if isinstance(widget, QPushButton):
                focus_color = palette.color(QPalette.ColorRole.Highlight)
                focus_text_color = palette.color(QPalette.ColorRole.HighlightedText)
                
                # 포커스 색상 유효성 검사
                if (focus_color.isValid() and focus_text_color.isValid() and 
                    focus_color.alpha() > 0 and focus_text_color.alpha() > 0):
                    
                    focus_contrast = self.calculate_contrast_ratio(focus_text_color, focus_color)
                    if focus_contrast < required_ratio and focus_contrast > 1.0:
                        issues.append(ValidationIssue(
                        guideline="1.4.3",
                        title="포커스 상태 색상 대비 부족",
                        description=f"포커스 상태 대비율 {focus_contrast:.1f}:1",
                        severity=ValidationSeverity.MAJOR,
                        level=WCAGLevel.AA,
                        principle=WCAGPrinciple.PERCEIVABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="포커스 상태의 텍스트와 배경 대비를 개선하세요"
                    ))
                    
        except Exception as e:
            logger.error(f"Error validating widget contrast: {e}")
        
        return issues
    
    def _get_widget_location(self, widget: QWidget) -> str:
        """위젯 위치 정보 생성"""
        try:
            location_parts = []
            
            # 객체 이름
            if widget.objectName():
                location_parts.append(f"name={widget.objectName()}")
            
            # 클래스 이름
            location_parts.append(f"type={widget.__class__.__name__}")
            
            # 부모 정보
            parent = widget.parent()
            if parent and parent.objectName():
                location_parts.append(f"parent={parent.objectName()}")
            
            # 위치 좌표
            if widget.isVisible():
                pos = widget.pos()
                location_parts.append(f"pos=({pos.x()},{pos.y()})")
            
            return ", ".join(location_parts)
            
        except Exception as e:
            logger.debug(f"Error getting widget location: {e}")
            return widget.__class__.__name__


class KeyboardAccessibilityValidator:
    """키보드 접근성 검증기"""
    
    def validate_widget_keyboard_access(self, widget: QWidget) -> List[ValidationIssue]:
        """위젯의 키보드 접근성 검증"""
        issues = []
        
        if not widget or not widget.isVisible() or not widget.isEnabled():
            return issues
        
        try:
            # 포커스 가능한 위젯인지 확인
            is_interactive = isinstance(widget, (
                QPushButton, QCheckBox, QComboBox, QLineEdit, QTextEdit,
                QSlider, QTabWidget, QListWidget, QTreeWidget, QTableWidget,
                QToolButton, QFrame  # 추가 위젯 타입
            ))
            
            # 커스텀 위젯도 체크 (accept 이벤트를 받는지)
            if not is_interactive:
                # 클릭 이벤트나 키 이벤트를 받는 위젯인지 확인
                if (hasattr(widget, 'clicked') or hasattr(widget, 'mousePressEvent') or 
                    hasattr(widget, 'keyPressEvent')):
                    is_interactive = True
            
            if is_interactive:
                # 포커스 정책 확인
                focus_policy = widget.focusPolicy()
                if focus_policy == Qt.FocusPolicy.NoFocus:
                    # 비활성화된 위젯은 포커스를 받을 필요가 없음
                    if widget.isEnabled():
                        issues.append(ValidationIssue(
                            guideline="2.1.1",
                            title="키보드로 접근 불가능",
                            description="상호작용 가능한 위젯이 키보드 포커스를 받을 수 없습니다",
                            severity=ValidationSeverity.CRITICAL,
                            level=WCAGLevel.A,
                            principle=WCAGPrinciple.OPERABLE,
                            widget=widget,
                            location=self._get_widget_location(widget),
                            recommendation="focusPolicy를 Qt.StrongFocus로 설정하세요",
                            help_url="https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html",
                            auto_fixable=True
                        ))
                
                # 탭 인덱스 확인
                if hasattr(widget, 'tabOrder') and not widget.tabOrder():
                    issues.append(ValidationIssue(
                        guideline="2.4.3", 
                        title="탭 순서 미설정",
                        description="위젯의 탭 순서가 논리적이지 않을 수 있습니다",
                        severity=ValidationSeverity.MINOR,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.OPERABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="명확한 탭 순서를 설정하세요"
                    ))
            
            # 키보드 트랩 확인 (모달 다이얼로그)
            if isinstance(widget, QDialog) and widget.isModal():
                # 다이얼로그에 포커스 가능한 요소가 있는지 확인
                focusable_children = self._find_focusable_children(widget)
                if not focusable_children:
                    issues.append(ValidationIssue(
                        guideline="2.1.2",
                        title="키보드 트랩",
                        description="모달 다이얼로그에 포커스 가능한 요소가 없습니다",
                        severity=ValidationSeverity.CRITICAL,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.OPERABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="다이얼로그에 포커스 가능한 버튼이나 입력 필드를 추가하세요"
                    ))
                elif len(focusable_children) == 1:
                    # 단일 포커스 요소도 트랩이 될 수 있음
                    single_widget = focusable_children[0]
                    if not isinstance(single_widget, (QPushButton,)):  # 버튼 하나만 있는 것은 OK
                        issues.append(ValidationIssue(
                            guideline="2.1.2",
                            title="잠재적 키보드 트랩",
                            description="다이얼로그에 포커스 가능한 요소가 하나뿐입니다",
                            severity=ValidationSeverity.WARNING,
                            level=WCAGLevel.A,
                            principle=WCAGPrinciple.OPERABLE,
                            widget=widget,
                            location=self._get_widget_location(widget),
                            recommendation="최소 두 개의 포커스 가능한 요소(예: 확인, 취소 버튼)를 제공하세요"
                        ))
                    
        except Exception as e:
            logger.error(f"Error validating keyboard accessibility: {e}")
        
        return issues
    
    def _find_focusable_children(self, parent: QWidget) -> List[QWidget]:
        """포커스 가능한 자식 위젯들 찾기"""
        focusable = []
        for child in parent.findChildren(QWidget):
            if (child.focusPolicy() != Qt.FocusPolicy.NoFocus and 
                child.isVisible() and child.isEnabled()):
                focusable.append(child)
        return focusable
    
    def _get_widget_location(self, widget: QWidget) -> str:
        """위젯 위치 정보 생성"""
        try:
            return f"{widget.__class__.__name__}({widget.objectName() or 'unnamed'})"
        except:
            return "Unknown widget"


class LabelingValidator:
    """라벨링 검증기"""
    
    def validate_widget_labeling(self, widget: QWidget) -> List[ValidationIssue]:
        """위젯의 라벨링 검증"""
        issues = []
        
        try:
            # 입력 필드 라벨 확인
            if isinstance(widget, (QLineEdit, QTextEdit, QComboBox, QSlider)):
                accessible_name = widget.accessibleName()
                
                if not accessible_name:
                    # 근처 라벨 위젯 찾기
                    associated_label = self._find_associated_label(widget)
                    
                    if not associated_label:
                        issues.append(ValidationIssue(
                            guideline="1.3.1",
                            title="라벨 누락",
                            description="입력 필드에 접근 가능한 이름이 없습니다",
                            severity=ValidationSeverity.CRITICAL,
                            level=WCAGLevel.A,
                            principle=WCAGPrinciple.PERCEIVABLE,
                            widget=widget,
                            location=self._get_widget_location(widget),
                            recommendation="setAccessibleName()으로 이름을 설정하거나 라벨을 연결하세요",
                            help_url="https://www.w3.org/WAI/WCAG21/Understanding/info-and-relationships.html",
                            auto_fixable=True
                        ))
            
            # 버튼 라벨 확인
            elif isinstance(widget, QPushButton):
                text = widget.text()
                accessible_name = widget.accessibleName()
                
                if not text and not accessible_name:
                    issues.append(ValidationIssue(
                        guideline="4.1.2",
                        title="버튼 라벨 누락",
                        description="버튼에 텍스트나 접근 가능한 이름이 없습니다",
                        severity=ValidationSeverity.CRITICAL,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.ROBUST,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="버튼에 텍스트를 설정하거나 setAccessibleName()을 사용하세요",
                        auto_fixable=True
                    ))
                elif text and len(text.strip()) < 2:
                    issues.append(ValidationIssue(
                        guideline="4.1.2",
                        title="버튼 라벨이 너무 짧음",
                        description=f"버튼 텍스트가 너무 짧습니다: '{text}'",
                        severity=ValidationSeverity.MINOR,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.ROBUST,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="더 설명적인 버튼 텍스트를 사용하세요"
                    ))
            
            # 이미지 대체 텍스트 확인
            elif isinstance(widget, QLabel):
                if widget.pixmap() and not widget.pixmap().isNull():
                    accessible_description = widget.accessibleDescription()
                    if not accessible_description:
                        issues.append(ValidationIssue(
                            guideline="1.1.1",
                            title="이미지 대체 텍스트 누락",
                            description="이미지에 대체 텍스트가 없습니다",
                            severity=ValidationSeverity.MAJOR,
                            level=WCAGLevel.A,
                            principle=WCAGPrinciple.PERCEIVABLE,
                            widget=widget,
                            location=self._get_widget_location(widget),
                            recommendation="setAccessibleDescription()으로 대체 텍스트를 설정하세요",
                            help_url="https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html",
                            auto_fixable=False
                        ))
                        
        except Exception as e:
            logger.error(f"Error validating widget labeling: {e}")
        
        return issues
    
    def _find_associated_label(self, widget: QWidget) -> Optional[QLabel]:
        """연관된 라벨 위젯 찾기"""
        try:
            parent = widget.parent()
            if not parent:
                return None
            
            # 같은 부모의 QLabel 자식들 중에서 찾기
            labels = parent.findChildren(QLabel)
            
            # 위젯과 가장 가까운 라벨 찾기
            widget_pos = widget.pos()
            closest_label = None
            min_distance = float('inf')
            
            for label in labels:
                if not label.text():
                    continue
                    
                label_pos = label.pos()
                distance = ((widget_pos.x() - label_pos.x()) ** 2 + 
                          (widget_pos.y() - label_pos.y()) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_label = label
            
            # 거리 임계값 (100픽셀) 이내의 라벨만 연관성 있다고 판단
            if min_distance <= 100:
                return closest_label
                
        except Exception as e:
            logger.debug(f"Error finding associated label: {e}")
            
        return None
    
    def _get_widget_location(self, widget: QWidget) -> str:
        """위젯 위치 정보 생성"""
        try:
            return f"{widget.__class__.__name__}({widget.objectName() or 'unnamed'})"
        except:
            return "Unknown widget"


class SizeAndSpacingValidator:
    """크기 및 간격 검증기"""
    
    # WCAG AA 터치 타겟 최소 크기 (44x44px)
    MIN_TOUCH_TARGET_SIZE = 44
    
    def validate_widget_size(self, widget: QWidget) -> List[ValidationIssue]:
        """위젯의 크기 및 간격 검증"""
        issues = []
        
        if not widget or not widget.isVisible():
            return issues
        
        try:
            # 터치 타겟 크기 확인 (상호작용 가능한 요소)
            if isinstance(widget, (QPushButton, QCheckBox, QComboBox, QToolButton)):
                size = widget.size()
                
                # 유효한 크기인지 확인
                if size.width() <= 0 or size.height() <= 0:
                    return issues
                
                # 24px 미만은 심각한 문제, 44px 미만은 권장사항 위반
                if size.width() < 24 or size.height() < 24:
                    issues.append(ValidationIssue(
                        guideline="2.5.5",
                        title="터치 타겟 크기 매우 작음",
                        description=f"현재 크기: {size.width()}x{size.height()}px, 최소 필요: 24x24px",
                        severity=ValidationSeverity.CRITICAL,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.OPERABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation=f"최소 24x24px 이상으로 설정하세요",
                        help_url="https://www.w3.org/WAI/WCAG21/Understanding/target-size.html",
                        auto_fixable=True
                    ))
                elif size.width() < self.MIN_TOUCH_TARGET_SIZE or size.height() < self.MIN_TOUCH_TARGET_SIZE:
                    issues.append(ValidationIssue(
                        guideline="2.5.5",
                        title="터치 타겟 크기 부족",
                        description=f"현재 크기: {size.width()}x{size.height()}px, 권장: {self.MIN_TOUCH_TARGET_SIZE}x{self.MIN_TOUCH_TARGET_SIZE}px",
                        severity=ValidationSeverity.MAJOR,
                        level=WCAGLevel.AA,
                        principle=WCAGPrinciple.OPERABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation=f"권장 크기 {self.MIN_TOUCH_TARGET_SIZE}x{self.MIN_TOUCH_TARGET_SIZE}px로 설정하세요",
                        help_url="https://www.w3.org/WAI/WCAG21/Understanding/target-size.html",
                        auto_fixable=True
                    ))
            
            # 텍스트 크기 확인 (텍스트가 있는 위젯만)
            if hasattr(widget, 'text') or isinstance(widget, (QLabel, QLineEdit, QTextEdit, QPushButton)):
                font = widget.font()
                point_size = font.pointSize()
                
                # 시스템 기본 폰트 크기 처리 (-1인 경우)
                if point_size <= 0:
                    font_metrics = QFontMetrics(font)
                    # 픽셀 크기를 포인트 크기로 변환 (대략 75 DPI 기준)
                    point_size = font.pixelSize() * 72.0 / 96.0 if font.pixelSize() > 0 else 12
                
                if point_size < 9:  # 9pt 미만은 심각한 문제
                    issues.append(ValidationIssue(
                        guideline="1.4.4",
                        title="텍스트 크기 매우 작음",
                        description=f"현재 텍스트 크기: {point_size:.1f}pt, 최소 필요: 9pt",
                        severity=ValidationSeverity.MAJOR,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.PERCEIVABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="최소 9pt 이상의 텍스트 크기를 사용하세요",
                        auto_fixable=True
                    ))
                elif point_size < 12:  # 12pt 미만은 권장사항 위반
                    issues.append(ValidationIssue(
                        guideline="1.4.4",
                        title="텍스트 크기 부족",
                        description=f"현재 텍스트 크기: {point_size:.1f}pt, 권장: 12pt 이상",
                        severity=ValidationSeverity.MINOR,
                        level=WCAGLevel.AA,
                        principle=WCAGPrinciple.PERCEIVABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="12pt 이상의 텍스트 크기를 사용하세요",
                        auto_fixable=True
                    ))
                
        except Exception as e:
            logger.error(f"Error validating widget size: {e}")
        
        return issues
    
    def _get_widget_location(self, widget: QWidget) -> str:
        """위젯 위치 정보 생성"""
        try:
            return f"{widget.__class__.__name__}({widget.objectName() or 'unnamed'})"
        except:
            return "Unknown widget"


class StructureValidator:
    """구조 검증기"""
    
    def validate_widget_structure(self, widget: QWidget) -> List[ValidationIssue]:
        """위젯의 구조 검증"""
        issues = []
        
        try:
            # 제목 구조 확인 (QGroupBox 등)
            if isinstance(widget, QGroupBox):
                title = widget.title()
                if not title:
                    issues.append(ValidationIssue(
                        guideline="1.3.1",
                        title="제목 누락",
                        description="그룹 박스에 제목이 없습니다",
                        severity=ValidationSeverity.MINOR,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.PERCEIVABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="setTitle()로 그룹의 목적을 설명하는 제목을 설정하세요",
                        auto_fixable=False
                    ))
            
            # 탭 구조 확인
            elif isinstance(widget, QTabWidget):
                for i in range(widget.count()):
                    tab_text = widget.tabText(i)
                    if not tab_text or tab_text.strip() == "":
                        issues.append(ValidationIssue(
                            guideline="4.1.2",
                            title="탭 라벨 누락",
                            description=f"탭 {i+1}에 라벨이 없습니다",
                            severity=ValidationSeverity.MAJOR,
                            level=WCAGLevel.A,
                            principle=WCAGPrinciple.ROBUST,
                            widget=widget,
                            location=self._get_widget_location(widget),
                            recommendation="setTabText()로 각 탭에 설명적인 라벨을 설정하세요"
                        ))
            
            # 테이블 구조 확인
            elif isinstance(widget, QTableWidget):
                # 헤더 확인
                if not widget.horizontalHeader().isVisible() and widget.columnCount() > 1:
                    issues.append(ValidationIssue(
                        guideline="1.3.1",
                        title="테이블 헤더 누락",
                        description="테이블에 열 헤더가 없습니다",
                        severity=ValidationSeverity.MAJOR,
                        level=WCAGLevel.A,
                        principle=WCAGPrinciple.PERCEIVABLE,
                        widget=widget,
                        location=self._get_widget_location(widget),
                        recommendation="테이블 헤더를 표시하고 적절한 라벨을 설정하세요"
                    ))
                    
        except Exception as e:
            logger.error(f"Error validating widget structure: {e}")
        
        return issues
    
    def _get_widget_location(self, widget: QWidget) -> str:
        """위젯 위치 정보 생성"""
        try:
            return f"{widget.__class__.__name__}({widget.objectName() or 'unnamed'})"
        except:
            return "Unknown widget"


class AccessibilityValidator:
    """종합 접근성 검증기"""
    
    def __init__(self, accessibility_manager=None):
        self.accessibility_manager = accessibility_manager
        
        # 개별 검증기들
        self.contrast_validator = ColorContrastValidator()
        self.keyboard_validator = KeyboardAccessibilityValidator()
        self.labeling_validator = LabelingValidator()
        self.size_validator = SizeAndSpacingValidator()
        self.structure_validator = StructureValidator()
        
        # 검증 규칙 활성화 상태
        self.enabled_validators = {
            "contrast": True,
            "keyboard": True,
            "labeling": True,
            "size": True,
            "structure": True
        }
        
        # 검증 설정
        self.target_level = WCAGLevel.AA
        self.ignore_hidden_widgets = True
        self.max_issues_per_widget = 10
        
    def validate_application(self) -> ValidationResult:
        """애플리케이션 전체 접근성 검증"""
        try:
            app = QApplication.instance()
            all_issues = []
            total_widgets = 0
            tested_widgets = 0
            
            # 모든 최상위 위젯 순회
            for top_level_widget in app.topLevelWidgets():
                if top_level_widget.isVisible():
                    widget_issues, widget_count, tested_count = self._validate_widget_tree(top_level_widget)
                    all_issues.extend(widget_issues)
                    total_widgets += widget_count
                    tested_widgets += tested_count
            
            # 전체 점수 계산
            score = self._calculate_overall_score(all_issues, tested_widgets)
            
            # 레벨별 점수 계산
            level_scores = self._calculate_level_scores(all_issues, tested_widgets)
            
            # 원칙별 점수 계산  
            principle_scores = self._calculate_principle_scores(all_issues, tested_widgets)
            
            result = ValidationResult(
                total_widgets=total_widgets,
                tested_widgets=tested_widgets,
                issues=all_issues,
                score=score,
                level_scores=level_scores,
                principle_scores=principle_scores
            )
            
            logger.info(f"Accessibility validation completed: {score:.1f}% score, {len(all_issues)} issues")
            return result
            
        except Exception as e:
            logger.error(f"Error during accessibility validation: {e}")
            return ValidationResult(
                total_widgets=0,
                tested_widgets=0,
                issues=[],
                score=0.0
            )
    
    def validate_widget(self, widget: QWidget) -> List[ValidationIssue]:
        """단일 위젯 접근성 검증"""
        issues = []
        
        try:
            # 숨겨진 위젯 건너뛰기
            if self.ignore_hidden_widgets and not widget.isVisible():
                return issues
            
            # 각 검증기별 검증 수행
            if self.enabled_validators.get("contrast", True):
                issues.extend(self.contrast_validator.validate_widget_contrast(widget, self.target_level))
            
            if self.enabled_validators.get("keyboard", True):
                issues.extend(self.keyboard_validator.validate_widget_keyboard_access(widget))
            
            if self.enabled_validators.get("labeling", True):
                issues.extend(self.labeling_validator.validate_widget_labeling(widget))
            
            if self.enabled_validators.get("size", True):
                issues.extend(self.size_validator.validate_widget_size(widget))
            
            if self.enabled_validators.get("structure", True):
                issues.extend(self.structure_validator.validate_widget_structure(widget))
            
            # 위젯당 이슈 수 제한
            if len(issues) > self.max_issues_per_widget:
                issues = issues[:self.max_issues_per_widget]
                issues.append(ValidationIssue(
                    guideline="0.0.0",
                    title="추가 문제 생략",
                    description=f"이 위젯에서 {self.max_issues_per_widget}개 이상의 문제가 발견되어 일부가 생략되었습니다",
                    severity=ValidationSeverity.INFO,
                    level=WCAGLevel.A,
                    principle=WCAGPrinciple.ROBUST,
                    widget=widget
                ))
            
        except Exception as e:
            logger.error(f"Error validating widget: {e}")
            issues.append(ValidationIssue(
                guideline="0.0.0",
                title="검증 오류",
                description=f"위젯 검증 중 오류가 발생했습니다: {str(e)}",
                severity=ValidationSeverity.WARNING,
                level=WCAGLevel.A,
                principle=WCAGPrinciple.ROBUST,
                widget=widget
            ))
        
        return issues
    
    def _validate_widget_tree(self, root_widget: QWidget) -> Tuple[List[ValidationIssue], int, int]:
        """위젯 트리 전체 검증"""
        all_issues = []
        total_widgets = 0
        tested_widgets = 0
        
        try:
            # 루트 위젯 검증
            if not self.ignore_hidden_widgets or root_widget.isVisible():
                issues = self.validate_widget(root_widget)
                all_issues.extend(issues)
                tested_widgets += 1
            
            total_widgets += 1
            
            # 자식 위젯들 재귀적 검증
            for child in root_widget.findChildren(QWidget):
                try:
                    if not self.ignore_hidden_widgets or child.isVisible():
                        child_issues = self.validate_widget(child)
                        all_issues.extend(child_issues)
                        tested_widgets += 1
                    
                    total_widgets += 1
                    
                except Exception as e:
                    logger.debug(f"Error validating child widget: {e}")
                    
        except Exception as e:
            logger.error(f"Error validating widget tree: {e}")
        
        return all_issues, total_widgets, tested_widgets
    
    def _calculate_overall_score(self, issues: List[ValidationIssue], tested_widgets: int) -> float:
        """전체 점수 계산"""
        try:
            if tested_widgets == 0:
                return 0.0
            
            # 심각도별 가중치
            severity_weights = {
                ValidationSeverity.CRITICAL: 10,
                ValidationSeverity.MAJOR: 5,
                ValidationSeverity.MINOR: 2,
                ValidationSeverity.WARNING: 1,
                ValidationSeverity.INFO: 0
            }
            
            # 총 감점 계산
            total_deduction = sum(severity_weights.get(issue.severity, 0) for issue in issues)
            
            # 최대 가능 점수 (위젯당 10점)
            max_possible_score = tested_widgets * 10
            
            # 점수 계산 (0-100 스케일)
            if max_possible_score == 0:
                return 0.0
            
            score = max(0.0, (max_possible_score - total_deduction) / max_possible_score * 100)
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    def _calculate_level_scores(self, issues: List[ValidationIssue], tested_widgets: int) -> Dict[WCAGLevel, float]:
        """WCAG 레벨별 점수 계산"""
        try:
            level_scores = {}
            
            for level in WCAGLevel:
                level_issues = [issue for issue in issues if issue.level == level]
                
                if tested_widgets == 0:
                    level_scores[level] = 0.0
                else:
                    # 레벨별 감점 계산
                    level_deduction = len(level_issues) * 5  # 이슈당 5점 감점
                    max_score = tested_widgets * 5  # 위젯당 최대 5점
                    
                    score = max(0.0, (max_score - level_deduction) / max_score * 100) if max_score > 0 else 0.0
                    level_scores[level] = min(100.0, score)
            
            return level_scores
            
        except Exception as e:
            logger.error(f"Error calculating level scores: {e}")
            return {level: 0.0 for level in WCAGLevel}
    
    def _calculate_principle_scores(self, issues: List[ValidationIssue], tested_widgets: int) -> Dict[WCAGPrinciple, float]:
        """WCAG 원칙별 점수 계산"""
        try:
            principle_scores = {}
            
            for principle in WCAGPrinciple:
                principle_issues = [issue for issue in issues if issue.principle == principle]
                
                if tested_widgets == 0:
                    principle_scores[principle] = 0.0
                else:
                    # 원칙별 감점 계산
                    principle_deduction = len(principle_issues) * 5  # 이슈당 5점 감점
                    max_score = tested_widgets * 5  # 위젯당 최대 5점
                    
                    score = max(0.0, (max_score - principle_deduction) / max_score * 100) if max_score > 0 else 0.0
                    principle_scores[principle] = min(100.0, score)
            
            return principle_scores
            
        except Exception as e:
            logger.error(f"Error calculating principle scores: {e}")
            return {principle: 0.0 for principle in WCAGPrinciple}
    
    def auto_fix_issues(self, issues: List[ValidationIssue]) -> int:
        """자동 수정 가능한 이슈들 수정"""
        fixed_count = 0
        
        try:
            for issue in issues:
                if not issue.auto_fixable or not issue.widget:
                    continue
                
                try:
                    if issue.guideline == "2.1.1":  # 키보드 접근성
                        issue.widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                        fixed_count += 1
                    
                    elif issue.guideline in ["1.3.1", "4.1.2"]:  # 라벨 누락
                        if isinstance(issue.widget, QPushButton):
                            if not issue.widget.text():
                                issue.widget.setText("버튼")
                                fixed_count += 1
                        else:
                            class_name = issue.widget.__class__.__name__
                            issue.widget.setAccessibleName(f"{class_name} 입력")
                            fixed_count += 1
                    
                    elif issue.guideline == "2.5.5":  # 터치 타겟 크기
                        current_size = issue.widget.size()
                        min_size = max(SizeAndSpacingValidator.MIN_TOUCH_TARGET_SIZE, 
                                     max(current_size.width(), current_size.height()))
                        issue.widget.setMinimumSize(min_size, min_size)
                        fixed_count += 1
                    
                    elif issue.guideline == "1.4.4":  # 텍스트 크기
                        font = issue.widget.font()
                        font.setPointSize(max(12, font.pointSize()))
                        issue.widget.setFont(font)
                        fixed_count += 1
                        
                except Exception as e:
                    logger.debug(f"Error auto-fixing issue: {e}")
                    
        except Exception as e:
            logger.error(f"Error during auto-fix: {e}")
        
        logger.info(f"Auto-fixed {fixed_count} accessibility issues")
        return fixed_count
    
    def generate_report(self, result: ValidationResult, output_path: Path = None) -> str:
        """접근성 검증 보고서 생성"""
        try:
            report = {
                "metadata": {
                    "timestamp": result.timestamp.isoformat(),
                    "total_widgets": result.total_widgets,
                    "tested_widgets": result.tested_widgets,
                    "overall_score": result.score,
                    "compliance_level": result.get_compliance_level().value if result.get_compliance_level() else "None"
                },
                "summary": {
                    "total_issues": len(result.issues),
                    "critical_issues": len(result.critical_issues),
                    "major_issues": len(result.major_issues),
                    "level_scores": {level.value: score for level, score in result.level_scores.items()},
                    "principle_scores": {principle.value: score for principle, score in result.principle_scores.items()}
                },
                "issues": [issue.to_dict() for issue in result.issues]
            }
            
            report_json = json.dumps(report, indent=2, ensure_ascii=False)
            
            if output_path:
                output_path.write_text(report_json, encoding='utf-8')
                logger.info(f"Accessibility report saved to {output_path}")
            
            return report_json
            
        except Exception as e:
            logger.error(f"Error generating accessibility report: {e}")
            return "{}"
    
    def set_target_level(self, level: WCAGLevel):
        """목표 WCAG 레벨 설정"""
        self.target_level = level
    
    def enable_validator(self, validator_name: str, enabled: bool):
        """개별 검증기 활성화/비활성화"""
        if validator_name in self.enabled_validators:
            self.enabled_validators[validator_name] = enabled
    
    def get_validation_settings(self) -> Dict[str, Any]:
        """현재 검증 설정 반환"""
        return {
            "target_level": self.target_level.value,
            "enabled_validators": self.enabled_validators.copy(),
            "ignore_hidden_widgets": self.ignore_hidden_widgets,
            "max_issues_per_widget": self.max_issues_per_widget
        }
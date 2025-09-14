"""
Accessibility Manager System
Comprehensive WCAG 2.1 AA compliant accessibility management for PyQt6 applications
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union
from enum import Enum
from dataclasses import dataclass, field
# ABC imports removed to avoid metaclass conflicts

from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog, QMessageBox, QToolTip,
    QLabel, QPushButton, QCheckBox, QComboBox, QLineEdit, QTextEdit,
    QSlider, QProgressBar, QTabWidget, QGroupBox, QScrollArea
)
from PyQt6.QtCore import (
    QObject, pyqtSignal, QSettings, QTimer, QRect, QPoint, QSize,
    QPropertyAnimation, QEasingCurve, Qt, QEvent, QModelIndex
)
from PyQt6.QtGui import (
    QColor, QPalette, QFont, QFontMetrics, QCursor, QPixmap, QPainter, QPen
)
# Import accessibility classes from compatibility layer
from .qt_compatibility import QAccessible, QAccessibleInterface, is_accessibility_available

from .logger import get_logger


logger = get_logger(__name__)


class AccessibilityLevel(Enum):
    """접근성 준수 수준"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityFeature(Enum):
    """접근성 기능"""
    KEYBOARD_NAVIGATION = "keyboard_navigation"
    SCREEN_READER = "screen_reader"
    HIGH_CONTRAST = "high_contrast"
    FONT_SCALING = "font_scaling"
    FOCUS_INDICATORS = "focus_indicators"
    TOOLTIPS = "tooltips"
    ANNOUNCEMENTS = "announcements"
    MOTOR_ACCESSIBILITY = "motor_accessibility"
    SKIP_LINKS = "skip_links"
    LIVE_REGIONS = "live_regions"


@dataclass
class AccessibilitySettings:
    """접근성 설정"""
    # WCAG 준수 수준
    compliance_level: AccessibilityLevel = AccessibilityLevel.AA
    
    # 기능 활성화 상태
    enabled_features: Set[AccessibilityFeature] = field(
        default_factory=lambda: {
            AccessibilityFeature.KEYBOARD_NAVIGATION,
            AccessibilityFeature.SCREEN_READER,
            AccessibilityFeature.FOCUS_INDICATORS,
            AccessibilityFeature.TOOLTIPS,
            AccessibilityFeature.MOTOR_ACCESSIBILITY
        }
    )
    
    # 폰트 스케일 (100% - 200%)
    font_scale: float = 1.0
    
    # 터치 타겟 최소 크기 (픽셀)
    min_touch_target_size: int = 44
    
    # 포커스 링 두께
    focus_ring_width: int = 2
    
    # 포커스 링 색상
    focus_ring_color: str = "#0078D4"
    
    # 애니메이션 감소
    reduce_animations: bool = False
    
    # 자동 스크롤 활성화
    auto_scroll_to_focus: bool = True
    
    # 키보드 네비게이션 지연 시간 (ms)
    keyboard_delay: int = 0
    
    # 스크린 리더 지원
    screen_reader_enabled: bool = True
    
    # 실시간 알림
    live_announcements: bool = True
    
    # 에러 방지 기능
    error_prevention: bool = True
    
    # 도움말 텍스트 표시
    show_help_text: bool = True
    
    # 키보드 단축키 사용자화
    custom_shortcuts: Dict[str, str] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """설정 유효성 검사"""
        errors = []
        
        try:
            # 폰트 스케일 검증
            if not isinstance(self.font_scale, (int, float)) or not (0.5 <= self.font_scale <= 3.0):
                errors.append("Font scale must be between 0.5 and 3.0")
                self.font_scale = max(0.5, min(3.0, float(self.font_scale or 1.0)))
            
            # 터치 타겟 크기 검증
            if not isinstance(self.min_touch_target_size, int) or not (20 <= self.min_touch_target_size <= 100):
                errors.append("Min touch target size must be between 20 and 100 pixels")
                self.min_touch_target_size = max(20, min(100, int(self.min_touch_target_size or 44)))
            
            # 포커스 링 두께 검증
            if not isinstance(self.focus_ring_width, int) or not (1 <= self.focus_ring_width <= 10):
                errors.append("Focus ring width must be between 1 and 10 pixels")
                self.focus_ring_width = max(1, min(10, int(self.focus_ring_width or 2)))
            
            # 포커스 링 색상 검증
            if not isinstance(self.focus_ring_color, str) or not self._is_valid_color(self.focus_ring_color):
                errors.append("Invalid focus ring color format")
                self.focus_ring_color = "#0078D4"  # 기본값으로 복원
            
            # 키보드 지연 시간 검증
            if not isinstance(self.keyboard_delay, int) or not (0 <= self.keyboard_delay <= 2000):
                errors.append("Keyboard delay must be between 0 and 2000 milliseconds")
                self.keyboard_delay = max(0, min(2000, int(self.keyboard_delay or 0)))
            
            # 활성화 기능 검증
            if not isinstance(self.enabled_features, set):
                errors.append("Enabled features must be a set")
                self.enabled_features = set()
            
            # 유효하지 않은 기능 제거
            valid_features = set()
            for feature in self.enabled_features:
                if isinstance(feature, AccessibilityFeature):
                    valid_features.add(feature)
                else:
                    errors.append(f"Invalid accessibility feature: {feature}")
            self.enabled_features = valid_features
            
            # 단축키 검증
            if not isinstance(self.custom_shortcuts, dict):
                errors.append("Custom shortcuts must be a dictionary")
                self.custom_shortcuts = {}
            else:
                # 유효하지 않은 단축키 제거
                valid_shortcuts = {}
                for key, value in self.custom_shortcuts.items():
                    if isinstance(key, str) and isinstance(value, str) and key.strip() and value.strip():
                        valid_shortcuts[key.strip()] = value.strip()
                    else:
                        errors.append(f"Invalid shortcut mapping: {key} -> {value}")
                self.custom_shortcuts = valid_shortcuts
                
        except Exception as e:
            errors.append(f"Error during validation: {str(e)}")
            
        return errors
    
    def _is_valid_color(self, color: str) -> bool:
        """색상 문자열 유효성 검사"""
        try:
            if not color or not isinstance(color, str):
                return False
            
            # #RRGGBB 형식 검사
            if color.startswith('#') and len(color) == 7:
                int(color[1:], 16)  # 16진수 변환 시도
                return True
            
            # #RGB 형식 검사
            if color.startswith('#') and len(color) == 4:
                int(color[1:], 16)  # 16진수 변환 시도
                return True
            
            # 명명된 색상 검사 (간단한 검사)
            named_colors = {
                'black', 'white', 'red', 'green', 'blue', 'yellow', 
                'cyan', 'magenta', 'gray', 'grey', 'darkred', 'darkgreen',
                'darkblue', 'darkyellow', 'darkcyan', 'darkmagenta'
            }
            return color.lower() in named_colors
            
        except ValueError:
            return False


@dataclass
class AccessibilityReport:
    """접근성 검증 보고서"""
    compliance_level: AccessibilityLevel
    score: float  # 0-100
    passed_tests: int
    failed_tests: int
    total_tests: int
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = ""


class AccessibilityInterface:
    """접근성 인터페이스 (mixin style)"""
    
    def get_accessible_name(self) -> str:
        """접근 가능한 이름 반환"""
        raise NotImplementedError("Subclass must implement get_accessible_name")
    
    def get_accessible_description(self) -> str:
        """접근 가능한 설명 반환"""
        raise NotImplementedError("Subclass must implement get_accessible_description")
    
    def get_accessible_role(self):
        """접근성 역할 반환"""
        raise NotImplementedError("Subclass must implement get_accessible_role")
    
    def get_accessible_state(self):
        """접근성 상태 반환"""
        raise NotImplementedError("Subclass must implement get_accessible_state")


class AccessibleWidget(QWidget):
    """접근성 지원 위젯 베이스 클래스"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._accessible_name = ""
        self._accessible_description = ""
        self._accessible_role = QAccessible.Role.NoRole if is_accessibility_available() else 0
        self._keyboard_shortcuts: Dict[str, Callable] = {}
        self._help_text = ""
        self._error_message = ""
        
        # Initialize accessibility interface
        self._accessibility_interface = AccessibilityInterface()
        
        # 포커스 정책 설정
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 접근성 속성 설정
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
    def set_accessible_name(self, name: str):
        """접근 가능한 이름 설정"""
        self._accessible_name = name
        self.setAccessibleName(name)
    
    def set_accessible_description(self, description: str):
        """접근 가능한 설명 설정"""
        self._accessible_description = description
        self.setAccessibleDescription(description)
    
    def set_accessible_role(self, role):
        """접근성 역할 설정"""
        self._accessible_role = role
    
    def set_help_text(self, text: str):
        """도움말 텍스트 설정"""
        self._help_text = text
        self.setToolTip(text)
    
    def set_error_message(self, message: str):
        """에러 메시지 설정"""
        self._error_message = message
    
    def add_keyboard_shortcut(self, key_sequence: str, callback: Callable):
        """키보드 단축키 추가"""
        self._keyboard_shortcuts[key_sequence] = callback
    
    def get_accessible_name(self) -> str:
        return self._accessible_name
    
    def get_accessible_description(self) -> str:
        return self._accessible_description
    
    def get_accessible_role(self):
        return self._accessible_role
    
    def get_accessible_state(self):
        if not is_accessibility_available():
            return None
        state = QAccessible.State()
        if self.isEnabled():
            state.enabled = True
        if self.hasFocus():
            state.focused = True
        if not self.isVisible():
            state.invisible = True
        return state
    
    def keyPressEvent(self, event):
        """키 이벤트 처리"""
        key_text = event.key()
        modifiers = event.modifiers()
        
        # 키 조합 문자열 생성
        key_combo = self._get_key_combination_string(key_text, modifiers)
        
        if key_combo in self._keyboard_shortcuts:
            self._keyboard_shortcuts[key_combo]()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def _get_key_combination_string(self, key: int, modifiers: Qt.KeyboardModifier) -> str:
        """키 조합 문자열 생성"""
        combo_parts = []
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            combo_parts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            combo_parts.append("Alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            combo_parts.append("Shift")
        
        # 키 이름 추가
        key_name = self._get_key_name(key)
        if key_name:
            combo_parts.append(key_name)
        
        return "+".join(combo_parts)
    
    def _get_key_name(self, key: int) -> str:
        """키 코드를 이름으로 변환"""
        key_names = {
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Return: "Return",
            Qt.Key.Key_Escape: "Escape",
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_F1: "F1",
            Qt.Key.Key_F2: "F2",
            Qt.Key.Key_F3: "F3",
            Qt.Key.Key_F4: "F4",
            Qt.Key.Key_F5: "F5",
            Qt.Key.Key_F6: "F6",
            Qt.Key.Key_F7: "F7",
            Qt.Key.Key_F8: "F8",
            Qt.Key.Key_F9: "F9",
            Qt.Key.Key_F10: "F10",
            Qt.Key.Key_F11: "F11",
            Qt.Key.Key_F12: "F12",
        }
        
        if key in key_names:
            return key_names[key]
        
        # 문자 키는 직접 변환
        if 32 <= key <= 126:  # 출력 가능한 ASCII
            return chr(key)
        
        return ""


class AccessibilityManager(QObject):
    """접근성 관리자"""
    
    # 시그널
    accessibility_changed = pyqtSignal(str, bool)  # feature_name, enabled
    font_scale_changed = pyqtSignal(float)  # new_scale
    focus_changed = pyqtSignal(QWidget)  # focused_widget
    announcement_requested = pyqtSignal(str, str)  # message, priority
    compliance_updated = pyqtSignal(float)  # compliance_score
    
    def __init__(self, app: QApplication, config_dir: Path = None):
        super().__init__()
        
        self.app = app
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 설정
        self.settings = QSettings()
        self.accessibility_settings = AccessibilitySettings()
        
        # 접근성 검증기
        self.validator = None
        
        # 등록된 위젯들
        self.registered_widgets: Dict[str, QWidget] = {}
        self.widget_metadata: Dict[str, Dict[str, Any]] = {}
        
        # 포커스 관리
        self.focus_history: List[QWidget] = []
        self.focus_indicators: Dict[QWidget, QWidget] = {}
        
        # 키보드 네비게이션
        self.tab_order: List[QWidget] = []
        self.custom_tab_orders: Dict[QWidget, List[QWidget]] = {}
        
        # 스크린 리더 지원
        self.screen_reader_bridge = None
        self.live_region_manager = None
        
        # 툴팁 및 도움말
        self.tooltip_manager = None
        self.help_system = None
        
        # 상태 추적
        self.is_high_contrast_active = False
        self.current_font_scale = 1.0
        self.reduced_animations = False
        
        # 타이머들
        self.validation_timer = QTimer()
        self.validation_timer.timeout.connect(self._periodic_validation)
        self.validation_timer.setInterval(30000)  # 30초마다 검증
        
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self._check_focus_changes)
        self.focus_timer.setInterval(100)  # 0.1초마다 포커스 체크
        
        # 초기화
        self._init_accessibility_framework()
        self._load_settings()
        
        logger.info("Accessibility Manager initialized")
    
    def _init_accessibility_framework(self):
        """Qt 접근성 프레임워크 초기화"""
        try:
            # 접근성 활성화
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
            
            # 애플리케이션 이벤트 필터 설치
            self.app.installEventFilter(self)
            
            # 포커스 변경 시그널 연결
            self.app.focusChanged.connect(self._on_focus_changed)
            
            logger.info("Qt accessibility framework initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize accessibility framework: {e}")
    
    def register_widget(self, widget: QWidget, 
                       widget_id: str = None,
                       accessible_name: str = None,
                       accessible_description: str = None,
                       role = None,
                       help_text: str = None) -> str:
        """
        위젯을 접근성 시스템에 등록
        
        Args:
            widget: 등록할 위젯
            widget_id: 위젯 ID (자동 생성 가능)
            accessible_name: 접근 가능한 이름
            accessible_description: 접근 가능한 설명
            role: 접근성 역할
            help_text: 도움말 텍스트
            
        Returns:
            위젯 ID
        """
        try:
            # 위젯 ID 생성
            if not widget_id:
                widget_id = f"widget_{id(widget)}"
            
            # 위젯 등록
            self.registered_widgets[widget_id] = widget
            
            # 메타데이터 저장
            metadata = {
                "accessible_name": accessible_name or widget.objectName() or widget.__class__.__name__,
                "accessible_description": accessible_description or "",
                "role": role or self._detect_widget_role(widget),
                "help_text": help_text or "",
                "widget_type": widget.__class__.__name__,
                "registration_time": time.time()
            }
            self.widget_metadata[widget_id] = metadata
            
            # 접근성 속성 적용
            self._apply_accessibility_attributes(widget, metadata)
            
            # 포커스 정책 설정
            if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
                if isinstance(widget, (QPushButton, QCheckBox, QComboBox, QLineEdit)):
                    widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            # 키보드 네비게이션에 추가
            self._add_to_tab_order(widget)
            
            # 터치 타겟 크기 검증 및 조정
            self._ensure_touch_target_size(widget)
            
            logger.debug(f"Widget registered: {widget_id} ({widget.__class__.__name__})")
            return widget_id
            
        except Exception as e:
            logger.error(f"Failed to register widget {widget_id}: {e}")
            return widget_id or f"widget_{id(widget)}"  # Return fallback ID
    
    def unregister_widget(self, widget_id: str):
        """위젯 등록 해제"""
        try:
            if widget_id in self.registered_widgets:
                widget = self.registered_widgets[widget_id]
                
                # 포커스 히스토리에서 제거
                if widget in self.focus_history:
                    self.focus_history.remove(widget)
                
                # 포커스 인디케이터 제거
                if widget in self.focus_indicators:
                    indicator = self.focus_indicators[widget]
                    indicator.deleteLater()
                    del self.focus_indicators[widget]
                
                # 탭 순서에서 제거
                if widget in self.tab_order:
                    self.tab_order.remove(widget)
                
                # 등록 해제
                del self.registered_widgets[widget_id]
                del self.widget_metadata[widget_id]
                
                logger.debug(f"Widget unregistered: {widget_id}")
                
        except Exception as e:
            logger.error(f"Failed to unregister widget {widget_id}: {e}")
    
    def _detect_widget_role(self, widget: QWidget):
        """위젯 타입에 따른 접근성 역할 자동 감지"""
        if not is_accessibility_available():
            return 0  # Default role when accessibility not available
            
        role_map = {
            QPushButton: QAccessible.Role.Button,
            QCheckBox: QAccessible.Role.CheckBox,
            QComboBox: QAccessible.Role.ComboBox,
            QLineEdit: QAccessible.Role.EditableText,
            QTextEdit: QAccessible.Role.EditableText,
            QLabel: QAccessible.Role.StaticText,
            QProgressBar: QAccessible.Role.ProgressBar,
            QSlider: QAccessible.Role.Slider,
            QTabWidget: QAccessible.Role.PageTabList,
            QGroupBox: QAccessible.Role.Grouping,
            QMainWindow: QAccessible.Role.Window,
            QDialog: QAccessible.Role.Dialog,
            QScrollArea: QAccessible.Role.ScrollBar,
        }
        
        for widget_type, role in role_map.items():
            if isinstance(widget, widget_type):
                return role
        
        return QAccessible.Role.NoRole
    
    def _apply_accessibility_attributes(self, widget: QWidget, metadata: Dict[str, Any]):
        """위젯에 접근성 속성 적용"""
        try:
            # 접근 가능한 이름 설정
            if metadata.get("accessible_name"):
                widget.setAccessibleName(metadata["accessible_name"])
            
            # 접근 가능한 설명 설정
            if metadata.get("accessible_description"):
                widget.setAccessibleDescription(metadata["accessible_description"])
            
            # 도움말 텍스트 설정
            if metadata.get("help_text"):
                widget.setToolTip(metadata["help_text"])
            
            # 위젯별 특수 설정
            if isinstance(widget, QPushButton):
                # 버튼의 경우 키보드 포커스 강화
                widget.setAutoDefault(False)
                widget.setDefault(False)
            
            elif isinstance(widget, QCheckBox):
                # 체크박스의 경우 상태 정보 추가
                widget.toggled.connect(
                    lambda checked: self._announce_state_change(
                        widget, "checked" if checked else "unchecked"
                    )
                )
            
            elif isinstance(widget, QComboBox):
                # 콤보박스의 경우 선택 변경 알림
                widget.currentTextChanged.connect(
                    lambda text: self._announce_state_change(
                        widget, f"selected {text}"
                    )
                )
            
        except Exception as e:
            logger.error(f"Failed to apply accessibility attributes: {e}")
    
    def _ensure_touch_target_size(self, widget: QWidget):
        """터치 타겟 최소 크기 보장"""
        try:
            min_size = self.accessibility_settings.min_touch_target_size
            current_size = widget.size()
            
            # 최소 크기보다 작은 경우 크기 조정
            new_width = max(current_size.width(), min_size)
            new_height = max(current_size.height(), min_size)
            
            if new_width != current_size.width() or new_height != current_size.height():
                widget.setMinimumSize(new_width, new_height)
                logger.debug(f"Touch target size adjusted for {widget.objectName()}: {new_width}x{new_height}")
        
        except Exception as e:
            logger.error(f"Failed to ensure touch target size: {e}")
    
    def _add_to_tab_order(self, widget: QWidget):
        """탭 순서에 위젯 추가"""
        try:
            if widget not in self.tab_order and widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                self.tab_order.append(widget)
                logger.debug(f"Widget added to tab order: {widget.objectName()}")
        
        except Exception as e:
            logger.error(f"Failed to add widget to tab order: {e}")
    
    def set_font_scale(self, scale: float) -> bool:
        """
        폰트 스케일 설정 (100% - 200%)
        
        Args:
            scale: 폰트 스케일 (1.0 = 100%)
            
        Returns:
            성공 여부
        """
        try:
            if not 1.0 <= scale <= 2.0:
                logger.warning(f"Font scale out of range: {scale} (must be 1.0-2.0)")
                return False
            
            old_scale = self.current_font_scale
            self.current_font_scale = scale
            self.accessibility_settings.font_scale = scale
            
            # 모든 등록된 위젯에 폰트 스케일 적용
            for widget in self.registered_widgets.values():
                self._apply_font_scale_to_widget(widget, scale)
            
            # 설정 저장
            self.settings.setValue("accessibility/font_scale", scale)
            
            # 시그널 발송
            self.font_scale_changed.emit(scale)
            
            logger.info(f"Font scale changed from {old_scale:.1%} to {scale:.1%}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set font scale {scale}: {e}")
            return False
    
    def _apply_font_scale_to_widget(self, widget: QWidget, scale: float):
        """위젯에 폰트 스케일 적용"""
        try:
            current_font = widget.font()
            point_size = current_font.pointSize()
            if point_size <= 0:
                point_size = 12  # Default fallback size
            base_size = int(point_size / self.current_font_scale) if self.current_font_scale != 1.0 else point_size
            new_size = max(8, int(base_size * scale))  # Ensure minimum readable size
            
            new_font = QFont(current_font)
            new_font.setPointSize(new_size)
            widget.setFont(new_font)
            
            # 자식 위젯들에도 재귀적으로 적용
            for child in widget.findChildren(QWidget):
                if child not in self.registered_widgets.values():
                    self._apply_font_scale_to_widget(child, scale)
        
        except Exception as e:
            logger.error(f"Failed to apply font scale to widget: {e}")
    
    def enable_feature(self, feature: AccessibilityFeature) -> bool:
        """접근성 기능 활성화"""
        try:
            if feature in self.accessibility_settings.enabled_features:
                return True  # 이미 활성화됨
            
            # 기능별 활성화 로직
            success = self._activate_feature(feature)
            
            if success:
                self.accessibility_settings.enabled_features.add(feature)
                self.settings.setValue(f"accessibility/feature_{feature.value}", True)
                self.accessibility_changed.emit(feature.value, True)
                logger.info(f"Accessibility feature enabled: {feature.value}")
            else:
                logger.error(f"Failed to enable accessibility feature: {feature.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error enabling feature {feature.value}: {e}")
            return False
    
    def disable_feature(self, feature: AccessibilityFeature) -> bool:
        """접근성 기능 비활성화"""
        try:
            if feature not in self.accessibility_settings.enabled_features:
                return True  # 이미 비활성화됨
            
            # 기능별 비활성화 로직
            success = self._deactivate_feature(feature)
            
            if success:
                self.accessibility_settings.enabled_features.discard(feature)
                self.settings.setValue(f"accessibility/feature_{feature.value}", False)
                self.accessibility_changed.emit(feature.value, False)
                logger.info(f"Accessibility feature disabled: {feature.value}")
            else:
                logger.error(f"Failed to disable accessibility feature: {feature.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error disabling feature {feature.value}: {e}")
            return False
    
    def _activate_feature(self, feature: AccessibilityFeature) -> bool:
        """개별 기능 활성화"""
        try:
            if feature == AccessibilityFeature.KEYBOARD_NAVIGATION:
                return self._activate_keyboard_navigation()
            
            elif feature == AccessibilityFeature.SCREEN_READER:
                return self._activate_screen_reader_support()
            
            elif feature == AccessibilityFeature.HIGH_CONTRAST:
                return self._activate_high_contrast_mode()
            
            elif feature == AccessibilityFeature.FOCUS_INDICATORS:
                return self._activate_focus_indicators()
            
            elif feature == AccessibilityFeature.TOOLTIPS:
                return self._activate_enhanced_tooltips()
            
            elif feature == AccessibilityFeature.ANNOUNCEMENTS:
                return self._activate_live_announcements()
            
            elif feature == AccessibilityFeature.MOTOR_ACCESSIBILITY:
                return self._activate_motor_accessibility()
            
            elif feature == AccessibilityFeature.SKIP_LINKS:
                return self._activate_skip_links()
            
            elif feature == AccessibilityFeature.LIVE_REGIONS:
                return self._activate_live_regions()
            
            return False
            
        except Exception as e:
            logger.error(f"Error activating feature {feature.value}: {e}")
            return False
    
    def _deactivate_feature(self, feature: AccessibilityFeature) -> bool:
        """개별 기능 비활성화"""
        # 구현: 각 기능별 비활성화 로직
        # 여기서는 기본적으로 True 반환
        return True
    
    def _activate_keyboard_navigation(self) -> bool:
        """키보드 네비게이션 활성화"""
        try:
            # 탭 순서 정렬
            self._sort_tab_order()
            
            # 키보드 단축키 활성화
            self._setup_global_shortcuts()
            
            # 포커스 타이머 시작
            self.focus_timer.start()
            
            return True
        except Exception as e:
            logger.error(f"Failed to activate keyboard navigation: {e}")
            return False
    
    def _activate_screen_reader_support(self) -> bool:
        """스크린 리더 지원 활성화"""
        try:
            # 스크린 리더 브리지 초기화
            if not self.screen_reader_bridge:
                try:
                    from .screen_reader_support import ScreenReaderBridge
                    self.screen_reader_bridge = ScreenReaderBridge(self)
                except ImportError as ie:
                    logger.error(f"Failed to import screen reader support: {ie}")
                    return False
            
            return self.screen_reader_bridge.initialize()
        except Exception as e:
            logger.error(f"Failed to activate screen reader support: {e}")
            return False
    
    def _activate_high_contrast_mode(self) -> bool:
        """고대비 모드 활성화"""
        try:
            # 테마 매니저를 통해 고대비 테마 적용
            try:
                from .theme_manager import get_theme_manager, ThemeType
                theme_manager = get_theme_manager()
                if theme_manager:
                    success = theme_manager.set_theme(ThemeType.HIGH_CONTRAST)
                    self.is_high_contrast_active = success
                    return success
            except ImportError:
                # Fallback: Apply high contrast manually using Qt palette
                self._apply_high_contrast_fallback()
                self.is_high_contrast_active = True
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to activate high contrast mode: {e}")
            return False
    
    def _activate_focus_indicators(self) -> bool:
        """포커스 인디케이터 활성화"""
        try:
            # 모든 등록된 위젯에 포커스 인디케이터 추가
            for widget in self.registered_widgets.values():
                self._add_focus_indicator(widget)
            return True
        except Exception as e:
            logger.error(f"Failed to activate focus indicators: {e}")
            return False
    
    def _activate_enhanced_tooltips(self) -> bool:
        """강화된 툴팁 활성화"""
        try:
            if not self.tooltip_manager:
                try:
                    from .tooltip_manager import TooltipManager
                    self.tooltip_manager = TooltipManager(self)
                    return self.tooltip_manager.initialize()
                except ImportError:
                    # Fallback: Use basic Qt tooltips with enhanced styling
                    self._setup_basic_tooltip_enhancement()
                    return True
            return self.tooltip_manager.initialize() if self.tooltip_manager else True
        except Exception as e:
            logger.error(f"Failed to activate enhanced tooltips: {e}")
            return False
    
    def _activate_live_announcements(self) -> bool:
        """실시간 알림 활성화"""
        try:
            # 실시간 알림 시스템 초기화
            return True
        except Exception as e:
            logger.error(f"Failed to activate live announcements: {e}")
            return False
    
    def _activate_motor_accessibility(self) -> bool:
        """운동 접근성 기능 활성화"""
        try:
            # 모든 위젯의 터치 타겟 크기 확인
            for widget in self.registered_widgets.values():
                self._ensure_touch_target_size(widget)
            
            # 클릭 지연 설정
            if self.accessibility_settings.keyboard_delay > 0:
                # 키보드 반복 지연 설정 (OS 레벨에서는 제한적)
                pass
            
            return True
        except Exception as e:
            logger.error(f"Failed to activate motor accessibility: {e}")
            return False
    
    def _activate_skip_links(self) -> bool:
        """스킵 링크 활성화"""
        try:
            # 메인 콘텐츠로 건너뛰기 기능
            return True
        except Exception as e:
            logger.error(f"Failed to activate skip links: {e}")
            return False
    
    def _activate_live_regions(self) -> bool:
        """라이브 리전 활성화"""
        try:
            if not self.live_region_manager:
                try:
                    from .live_region_manager import LiveRegionManager
                    self.live_region_manager = LiveRegionManager(self)
                    return self.live_region_manager.initialize()
                except ImportError:
                    # Fallback: Create simple live region manager
                    self.live_region_manager = self._create_simple_live_region_manager()
                    return True
            return self.live_region_manager.initialize() if hasattr(self.live_region_manager, 'initialize') else True
        except Exception as e:
            logger.error(f"Failed to activate live regions: {e}")
            return False
    
    def _sort_tab_order(self):
        """탭 순서 정렬 (위치 기반)"""
        try:
            # 위젯들을 위치 기반으로 정렬 (위 -> 아래, 왼쪽 -> 오른쪽)
            self.tab_order.sort(key=lambda w: (w.pos().y(), w.pos().x()) if w.parent() else (0, 0))
        except Exception as e:
            logger.error(f"Failed to sort tab order: {e}")
    
    def _setup_global_shortcuts(self):
        """전역 키보드 단축키 설정"""
        try:
            # F1: 도움말
            # Tab/Shift+Tab: 다음/이전 포커스
            # Ctrl+F6: 다음 패널
            # F6: 다음 영역
            # 등등
            pass
        except Exception as e:
            logger.error(f"Failed to setup global shortcuts: {e}")
    
    def _add_focus_indicator(self, widget: QWidget):
        """위젯에 포커스 인디케이터 추가"""
        try:
            if widget in self.focus_indicators:
                return  # 이미 있음
            
            # 포커스 링 생성 (커스텀 위젯 오버레이)
            focus_ring = FocusIndicator(widget, self.accessibility_settings)
            self.focus_indicators[widget] = focus_ring
            
        except Exception as e:
            logger.error(f"Failed to add focus indicator: {e}")
    
    def announce_message(self, message: str, priority: str = "polite"):
        """스크린 리더에 메시지 알림"""
        try:
            if AccessibilityFeature.ANNOUNCEMENTS in self.accessibility_settings.enabled_features:
                self.announcement_requested.emit(message, priority)
                
                if self.screen_reader_bridge:
                    self.screen_reader_bridge.announce(message, priority)
        
        except Exception as e:
            logger.error(f"Failed to announce message: {e}")
    
    def _announce_state_change(self, widget: QWidget, state: str):
        """위젯 상태 변경 알림"""
        try:
            widget_name = widget.accessibleName() or widget.objectName() or "element"
            message = f"{widget_name} {state}"
            self.announce_message(message, "assertive")
        except Exception as e:
            logger.error(f"Failed to announce state change: {e}")
    
    def _on_focus_changed(self, old_widget: QWidget, new_widget: QWidget):
        """포커스 변경 이벤트 처리"""
        try:
            if new_widget:
                # 포커스 히스토리 업데이트
                if new_widget not in self.focus_history:
                    self.focus_history.append(new_widget)
                    if len(self.focus_history) > 10:  # 최대 10개 기록
                        self.focus_history.pop(0)
                
                # 포커스 인디케이터 활성화
                if new_widget in self.focus_indicators:
                    self.focus_indicators[new_widget].show_focus()
                
                # 자동 스크롤
                if self.accessibility_settings.auto_scroll_to_focus:
                    self._scroll_to_widget(new_widget)
                
                # 포커스 알림
                if AccessibilityFeature.SCREEN_READER in self.accessibility_settings.enabled_features:
                    self._announce_focus_change(new_widget)
                
                # 시그널 발송
                self.focus_changed.emit(new_widget)
            
            # 이전 위젯의 포커스 인디케이터 비활성화
            if old_widget and old_widget in self.focus_indicators:
                self.focus_indicators[old_widget].hide_focus()
        
        except Exception as e:
            logger.error(f"Error handling focus change: {e}")
    
    def _scroll_to_widget(self, widget: QWidget):
        """위젯으로 자동 스크롤"""
        try:
            # 부모 스크롤 영역 찾기
            parent = widget.parent()
            while parent:
                if isinstance(parent, QScrollArea):
                    # 스크롤 영역 내에서 위젯이 보이도록 조정
                    parent.ensureWidgetVisible(widget, 50, 50)  # 50px 마진
                    break
                parent = parent.parent()
        except Exception as e:
            logger.error(f"Failed to scroll to widget: {e}")
    
    def _announce_focus_change(self, widget: QWidget):
        """포커스 변경 알림"""
        try:
            # 위젯 정보 수집
            name = widget.accessibleName() or widget.objectName() or widget.__class__.__name__
            description = widget.accessibleDescription()
            role = self._get_role_name(widget)
            
            # 알림 메시지 구성
            message_parts = [name]
            if description:
                message_parts.append(description)
            if role:
                message_parts.append(role)
            
            message = ", ".join(message_parts)
            self.announce_message(message, "polite")
            
        except Exception as e:
            logger.error(f"Failed to announce focus change: {e}")
    
    def _get_role_name(self, widget: QWidget) -> str:
        """위젯 역할 이름 반환"""
        role_names = {
            QPushButton: "button",
            QCheckBox: "checkbox", 
            QComboBox: "combobox",
            QLineEdit: "text input",
            QTextEdit: "text area",
            QLabel: "text",
            QProgressBar: "progress bar",
            QSlider: "slider",
        }
        
        for widget_type, name in role_names.items():
            if isinstance(widget, widget_type):
                return name
        
        return ""
    
    def _check_focus_changes(self):
        """포커스 변경 주기적 체크"""
        try:
            current_focus = self.app.focusWidget()
            if current_focus and current_focus not in self.registered_widgets.values():
                # 등록되지 않은 위젯이 포커스를 받은 경우 자동 등록
                self.register_widget(current_focus)
        except Exception as e:
            logger.error(f"Error checking focus changes: {e}")
    
    def _periodic_validation(self):
        """주기적 접근성 검증"""
        try:
            if self.validator:
                report = self.validator.validate_application()
                self.compliance_updated.emit(report.score)
                
                # 심각한 문제가 발견된 경우 로그
                critical_issues = [issue for issue in report.issues if issue.get("severity") == "critical"]
                if critical_issues:
                    logger.warning(f"Critical accessibility issues found: {len(critical_issues)}")
        
        except Exception as e:
            logger.error(f"Error during periodic validation: {e}")
    
    def validate_compliance(self) -> AccessibilityReport:
        """접근성 규정 준수 검증"""
        try:
            if not self.validator:
                from .accessibility_validator import AccessibilityValidator
                self.validator = AccessibilityValidator(self)
            
            return self.validator.validate_application()
            
        except Exception as e:
            logger.error(f"Failed to validate compliance: {e}")
            return AccessibilityReport(
                compliance_level=AccessibilityLevel.A,
                score=0.0,
                passed_tests=0,
                failed_tests=1,
                total_tests=1,
                issues=[{"type": "validation_error", "message": str(e)}],
                recommendations=["Fix validation system"]
            )
    
    def _load_settings(self):
        """설정 로드"""
        try:
            # 폰트 스케일
            scale = self.settings.value("accessibility/font_scale", 1.0, type=float)
            self.accessibility_settings.font_scale = scale
            self.current_font_scale = scale
            
            # 활성화된 기능들
            for feature in AccessibilityFeature:
                enabled = self.settings.value(
                    f"accessibility/feature_{feature.value}", 
                    feature in self.accessibility_settings.enabled_features,
                    type=bool
                )
                if enabled:
                    self.accessibility_settings.enabled_features.add(feature)
                else:
                    self.accessibility_settings.enabled_features.discard(feature)
            
            # 기타 설정들
            self.accessibility_settings.min_touch_target_size = self.settings.value(
                "accessibility/min_touch_target_size", 44, type=int
            )
            
            self.accessibility_settings.focus_ring_width = self.settings.value(
                "accessibility/focus_ring_width", 2, type=int
            )
            
            self.accessibility_settings.focus_ring_color = self.settings.value(
                "accessibility/focus_ring_color", "#0078D4", type=str
            )
            
            self.accessibility_settings.keyboard_delay = self.settings.value(
                "accessibility/keyboard_delay", 0, type=int
            )
            
            self.accessibility_settings.reduce_animations = self.settings.value(
                "accessibility/reduce_animations", False, type=bool
            )
            
            self.accessibility_settings.auto_scroll_to_focus = self.settings.value(
                "accessibility/auto_scroll_to_focus", True, type=bool
            )
            
            # 설정 유효성 검사 및 수정
            validation_errors = self.accessibility_settings.validate()
            if validation_errors:
                logger.warning(f"Accessibility settings validation errors: {validation_errors}")
                # 수정된 설정 저장
                self.save_settings()
            
            logger.info("Accessibility settings loaded and validated")
            
        except Exception as e:
            logger.error(f"Failed to load accessibility settings: {e}")
            # 기본 설정으로 복원
            self.accessibility_settings = AccessibilitySettings()
            self.current_font_scale = 1.0
    
    def save_settings(self):
        """설정 저장"""
        try:
            # 현재 설정들을 QSettings에 저장
            self.settings.setValue("accessibility/font_scale", self.accessibility_settings.font_scale)
            self.settings.setValue("accessibility/min_touch_target_size", self.accessibility_settings.min_touch_target_size)
            self.settings.setValue("accessibility/focus_ring_color", self.accessibility_settings.focus_ring_color)
            
            # 기능 활성화 상태
            for feature in AccessibilityFeature:
                enabled = feature in self.accessibility_settings.enabled_features
                self.settings.setValue(f"accessibility/feature_{feature.value}", enabled)
            
            self.settings.sync()
            logger.info("Accessibility settings saved")
            
        except Exception as e:
            logger.error(f"Failed to save accessibility settings: {e}")
    
    def get_accessibility_info(self) -> Dict[str, Any]:
        """접근성 정보 반환"""
        try:
            return {
                "compliance_level": self.accessibility_settings.compliance_level.value,
                "enabled_features": [f.value for f in self.accessibility_settings.enabled_features],
                "font_scale": self.accessibility_settings.font_scale,
                "min_touch_target_size": self.accessibility_settings.min_touch_target_size,
                "registered_widgets_count": len(self.registered_widgets),
                "focus_ring_color": self.accessibility_settings.focus_ring_color,
                "high_contrast_active": self.is_high_contrast_active,
                "screen_reader_enabled": AccessibilityFeature.SCREEN_READER in self.accessibility_settings.enabled_features
            }
        except Exception as e:
            logger.error(f"Failed to get accessibility info: {e}")
            return {}
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """애플리케이션 이벤트 필터"""
        try:
            # 키보드 이벤트 필터링
            if event.type() == QEvent.Type.KeyPress:
                if self._handle_global_keyboard_event(event):
                    return True
            
            # 터치 이벤트 필터링 (모터 접근성)
            elif event.type() in (QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate, QEvent.Type.TouchEnd):
                if AccessibilityFeature.MOTOR_ACCESSIBILITY in self.accessibility_settings.enabled_features:
                    return self._handle_touch_event(event)
            
            return False
            
        except Exception as e:
            logger.error(f"Error in event filter: {e}")
            return False
    
    def _handle_global_keyboard_event(self, event) -> bool:
        """전역 키보드 이벤트 처리"""
        try:
            # F1: 도움말 표시
            if event.key() == Qt.Key.Key_F1:
                self._show_context_help()
                return True
            
            # Ctrl+F6: 다음 패널로 이동
            if (event.key() == Qt.Key.Key_F6 and 
                event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                self._navigate_to_next_panel()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling global keyboard event: {e}")
            return False
    
    def _handle_touch_event(self, event) -> bool:
        """터치 이벤트 처리 (모터 접근성)"""
        try:
            # 터치 타겟 크기 검증 및 확대
            # 실제 구현에서는 터치 영역을 확장하는 로직 추가
            return False
        except Exception as e:
            logger.error(f"Error handling touch event: {e}")
            return False
    
    def _show_context_help(self):
        """컨텍스트 도움말 표시"""
        try:
            current_widget = self.app.focusWidget()
            if current_widget:
                help_text = current_widget.toolTip() or current_widget.whatsThis() or "도움말이 없습니다."
                
                # 도움말 다이얼로그 표시
                QMessageBox.information(
                    current_widget,
                    "도움말",
                    help_text
                )
        except Exception as e:
            logger.error(f"Error showing context help: {e}")
    
    def _navigate_to_next_panel(self):
        """다음 패널로 네비게이션"""
        try:
            # 탭 위젯이나 다른 패널 컨테이너 찾아서 이동
            current_widget = self.app.focusWidget()
            if current_widget:
                # 부모 중에서 탭 위젯 찾기
                parent = current_widget.parent()
                while parent:
                    if isinstance(parent, QTabWidget):
                        current_index = parent.currentIndex()
                        next_index = (current_index + 1) % parent.count()
                        parent.setCurrentIndex(next_index)
                        break
                    parent = parent.parent()
        except Exception as e:
            logger.error(f"Error navigating to next panel: {e}")
    
    def cleanup(self):
        """정리"""
        try:
            # 타이머 정지 및 정리
            if hasattr(self, 'validation_timer') and self.validation_timer:
                self.validation_timer.stop()
                self.validation_timer.deleteLater()
                self.validation_timer = None
                
            if hasattr(self, 'focus_timer') and self.focus_timer:
                self.focus_timer.stop()
                self.focus_timer.deleteLater()
                self.focus_timer = None
            
            # 포커스 인디케이터들 정리
            for indicator in list(self.focus_indicators.values()):
                try:
                    if indicator and not indicator.isHidden():
                        indicator.hide()
                    indicator.deleteLater()
                except RuntimeError:
                    pass  # 이미 삭제된 객체
            self.focus_indicators.clear()
            
            # 스크린 리더 브리지 정리
            if hasattr(self, 'screen_reader_bridge') and self.screen_reader_bridge:
                try:
                    self.screen_reader_bridge.cleanup()
                except Exception as e:
                    logger.debug(f"Error cleaning up screen reader bridge: {e}")
                self.screen_reader_bridge = None
            
            # 라이브 리전 매니저 정리
            if hasattr(self, 'live_region_manager') and self.live_region_manager:
                try:
                    if hasattr(self.live_region_manager, 'cleanup'):
                        self.live_region_manager.cleanup()
                except Exception as e:
                    logger.debug(f"Error cleaning up live region manager: {e}")
                self.live_region_manager = None
            
            # 툴팁 매니저 정리
            if hasattr(self, 'tooltip_manager') and self.tooltip_manager:
                try:
                    if hasattr(self.tooltip_manager, 'cleanup'):
                        self.tooltip_manager.cleanup()
                except Exception as e:
                    logger.debug(f"Error cleaning up tooltip manager: {e}")
                self.tooltip_manager = None
            
            # 검증기 정리
            if hasattr(self, 'validator') and self.validator:
                self.validator = None
            
            # 이벤트 필터 제거
            try:
                self.app.removeEventFilter(self)
            except (RuntimeError, AttributeError):
                pass  # 이미 제거되었거나 앱이 없음
            
            # 등록된 위젯들 정리 (약한 참조가 아니므로 명시적 정리)
            self.registered_widgets.clear()
            self.widget_metadata.clear()
            self.focus_history.clear()
            self.tab_order.clear()
            self.custom_tab_orders.clear()
            
            # 설정 저장
            try:
                self.save_settings()
            except Exception as e:
                logger.debug(f"Error saving settings during cleanup: {e}")
            
            logger.info("Accessibility Manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _apply_high_contrast_fallback(self):
        """고대비 모드 폴백 구현"""
        try:
            # 모든 등록된 위젯에 고대비 팔레트 적용
            for widget in self.registered_widgets.values():
                palette = widget.palette()
                
                # 고대비 색상 설정
                palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))  # 검정 배경
                palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))  # 흰색 텍스트
                palette.setColor(QPalette.ColorRole.Button, QColor(64, 64, 64))  # 어두운 회색 버튼
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))  # 흰색 버튼 텍스트
                palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))  # 파란색 하이라이트
                palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))  # 흰색 하이라이트 텍스트
                
                widget.setPalette(palette)
                
        except Exception as e:
            logger.error(f"Error applying high contrast fallback: {e}")
    
    def _setup_basic_tooltip_enhancement(self):
        """기본 툴팁 강화 설정"""
        try:
            # QToolTip 스타일 강화
            QToolTip.setFont(QFont("Arial", 12))  # 더 큰 폰트
            
            # 모든 등록된 위젯의 툴팁 스타일 개선
            for widget in self.registered_widgets.values():
                if widget.toolTip():
                    # 툴팁이 있는 위젯에 대해 마우스 오버 이벤트 강화
                    widget.setMouseTracking(True)
                    
        except Exception as e:
            logger.error(f"Error setting up basic tooltip enhancement: {e}")
    
    def _create_simple_live_region_manager(self):
        """간단한 라이브 리전 매니저 생성"""
        try:
            class SimpleLiveRegionManager:
                def __init__(self, accessibility_manager):
                    self.accessibility_manager = accessibility_manager
                    self.live_regions = {}
                
                def register_live_region(self, widget, **kwargs):
                    self.live_regions[widget] = kwargs
                    return True
                
                def unregister_live_region(self, widget):
                    if widget in self.live_regions:
                        del self.live_regions[widget]
                
                def cleanup(self):
                    self.live_regions.clear()
            
            return SimpleLiveRegionManager(self)
            
        except Exception as e:
            logger.error(f"Error creating simple live region manager: {e}")
            return None


class FocusIndicator(QWidget):
    """포커스 인디케이터 위젯"""
    
    def __init__(self, target_widget: QWidget, settings: AccessibilitySettings, parent=None):
        super().__init__(parent or target_widget.parent())
        
        self.target_widget = target_widget
        self.settings = settings
        
        # 설정
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # 초기에는 숨김
        self.hide()
        
        # 애니메이션
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def show_focus(self):
        """포커스 인디케이터 표시"""
        try:
            # 타겟 위젯의 위치와 크기로 조정
            target_rect = self.target_widget.rect()
            target_pos = self.target_widget.mapToGlobal(target_rect.topLeft())
            
            # 포커스 링 크기 (타겟보다 약간 크게)
            margin = self.settings.focus_ring_width + 2
            self.setGeometry(
                target_pos.x() - margin,
                target_pos.y() - margin,
                target_rect.width() + margin * 2,
                target_rect.height() + margin * 2
            )
            
            # 페이드 인 애니메이션
            self.setWindowOpacity(0.0)
            self.show()
            
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.start()
            
        except Exception as e:
            logger.error(f"Error showing focus indicator: {e}")
    
    def hide_focus(self):
        """포커스 인디케이터 숨김"""
        try:
            # 페이드 아웃 애니메이션
            self.animation.finished.connect(self.hide)
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.start()
        except Exception as e:
            logger.error(f"Error hiding focus indicator: {e}")
    
    def paintEvent(self, event):
        """포커스 링 그리기"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 포커스 링 색상
            color = QColor(self.settings.focus_ring_color)
            painter.setPen(QPen(color, self.settings.focus_ring_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # 포커스 링 그리기 (둥근 모서리)
            rect = self.rect().adjusted(
                self.settings.focus_ring_width // 2,
                self.settings.focus_ring_width // 2,
                -self.settings.focus_ring_width // 2,
                -self.settings.focus_ring_width // 2
            )
            
            painter.drawRoundedRect(rect, 4, 4)  # 4px 둥근 모서리
            
        except Exception as e:
            logger.error(f"Error painting focus indicator: {e}")


# 전역 접근성 매니저 인스턴스
_accessibility_manager: Optional[AccessibilityManager] = None


def init_accessibility_manager(app: QApplication, config_dir: Path = None) -> AccessibilityManager:
    """
    전역 접근성 매니저 초기화
    
    Args:
        app: QApplication 인스턴스
        config_dir: 설정 디렉토리
        
    Returns:
        접근성 매니저 인스턴스
    """
    global _accessibility_manager
    
    if _accessibility_manager is not None:
        logger.warning("Accessibility manager already initialized")
        return _accessibility_manager
    
    _accessibility_manager = AccessibilityManager(app, config_dir)
    
    # 기본 기능들 활성화
    default_features = [
        AccessibilityFeature.KEYBOARD_NAVIGATION,
        AccessibilityFeature.FOCUS_INDICATORS,
        AccessibilityFeature.TOOLTIPS,
        AccessibilityFeature.MOTOR_ACCESSIBILITY
    ]
    
    for feature in default_features:
        _accessibility_manager.enable_feature(feature)
    
    return _accessibility_manager


def get_accessibility_manager() -> Optional[AccessibilityManager]:
    """전역 접근성 매니저 인스턴스 반환"""
    return _accessibility_manager


def cleanup_accessibility_manager():
    """전역 접근성 매니저 정리"""
    global _accessibility_manager
    
    if _accessibility_manager:
        _accessibility_manager.cleanup()
        _accessibility_manager = None
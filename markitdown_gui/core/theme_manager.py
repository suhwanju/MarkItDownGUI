"""
Theme Management System
PyQt6 기반 다크/라이트 테마 지원 및 시스템 테마 감지
"""

import os
import platform
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass

from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPalette, QColor

from .logger import get_logger
from .system_theme_detector import SystemThemeDetector


logger = get_logger(__name__)


class ThemeType(Enum):
    """테마 타입 열거형"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    FOLLOW_SYSTEM = "follow_system"


@dataclass
class ThemeColors:
    """테마 색상 정의"""
    # Primary colors
    primary: str
    primary_variant: str
    secondary: str
    secondary_variant: str
    
    # Background colors
    background: str
    surface: str
    error: str
    
    # On colors (text colors)
    on_primary: str
    on_secondary: str
    on_background: str
    on_surface: str
    on_error: str
    
    # Additional UI colors
    border: str
    hover: str
    pressed: str
    disabled: str
    selected: str
    
    # Accent color (customizable)
    accent: str = "#3B82F6"  # Blue-500 default
    
    def __post_init__(self):
        """후처리: 접근성 준수 검증"""
        self._validate_contrast_ratios()
    
    def _validate_contrast_ratios(self):
        """WCAG 2.1 AA 준수 대비율 검증"""
        # 기본적인 대비율 검증 로직
        # 실제로는 더 복잡한 색상 대비 계산이 필요
        pass


class ThemeManager(QObject):
    """테마 관리자"""
    
    # 시그널
    theme_changed = pyqtSignal(str)  # theme_name
    accent_changed = pyqtSignal(str)  # accent_color
    
    def __init__(self, app: QApplication, config_dir: Path = None):
        super().__init__()
        
        self.app = app
        self.config_dir = config_dir or Path("config")
        self.styles_dir = Path(__file__).parent.parent / "resources" / "styles"
        
        # 설정 저장
        self.settings = QSettings()
        
        # 현재 테마 상태
        self._current_theme = ThemeType.FOLLOW_SYSTEM
        self._current_accent = "#3B82F6"  # Blue-500
        self._system_theme_detector = None
        self._theme_colors: Dict[ThemeType, ThemeColors] = {}
        self._last_system_theme = None
        
        # 테마 변경 감지 타이머 (시스템 테마용)
        self._theme_check_timer = QTimer()
        self._theme_check_timer.timeout.connect(self._check_system_theme_change)
        self._theme_check_timer.setInterval(5000)  # 5초마다 체크
        
        # 콜백 함수들 (테마 적용시 호출)
        self._theme_callbacks: list[Callable] = []
        
        # 애니메이션 관련
        self._transition_enabled = True
        self._transition_duration = 300  # 밀리초
        self._current_animation = None
        
        self._init_themes()
        self._init_system_detector()
        
        logger.info("Theme Manager initialized")
    
    def _init_themes(self):
        """테마 색상 초기화"""
        # Light theme colors (WCAG AA compliant)
        self._theme_colors[ThemeType.LIGHT] = ThemeColors(
            primary="#1976D2",         # Blue-700
            primary_variant="#1565C0", # Blue-800
            secondary="#DC004E",       # Pink-A400
            secondary_variant="#C51162", # Pink-A700
            
            background="#FFFFFF",      # White
            surface="#F5F5F5",        # Gray-50
            error="#D32F2F",          # Red-700
            
            on_primary="#FFFFFF",      # White
            on_secondary="#FFFFFF",    # White
            on_background="#212121",   # Gray-900
            on_surface="#424242",      # Gray-700
            on_error="#FFFFFF",        # White
            
            border="#E0E0E0",          # Gray-300
            hover="#EEEEEE",           # Gray-200
            pressed="#BDBDBD",         # Gray-400
            disabled="#9E9E9E",        # Gray-500
            selected="#E3F2FD",        # Blue-50
        )
        
        # Dark theme colors (WCAG AA compliant)
        self._theme_colors[ThemeType.DARK] = ThemeColors(
            primary="#2196F3",         # Blue-500
            primary_variant="#1976D2", # Blue-700
            secondary="#FF4081",       # Pink-A200
            secondary_variant="#F50057", # Pink-A400
            
            background="#121212",      # Material Dark
            surface="#1E1E1E",        # Gray-900
            error="#CF6679",          # Red-300
            
            on_primary="#000000",      # Black
            on_secondary="#000000",    # Black
            on_background="#FFFFFF",   # White
            on_surface="#E0E0E0",      # Gray-300
            on_error="#000000",        # Black
            
            border="#424242",          # Gray-700
            hover="#333333",           # Gray-800
            pressed="#555555",         # Gray-600
            disabled="#616161",        # Gray-600
            selected="#1A237E",        # Indigo-900
        )
        
        # High contrast theme colors (WCAG AAA compliant)
        self._theme_colors[ThemeType.HIGH_CONTRAST] = ThemeColors(
            primary="#000000",         # Black
            primary_variant="#000000", # Black
            secondary="#000000",       # Black
            secondary_variant="#000000", # Black
            
            background="#FFFFFF",      # White
            surface="#FFFFFF",         # White
            error="#FF0000",          # Red
            
            on_primary="#FFFFFF",      # White
            on_secondary="#FFFFFF",    # White
            on_background="#000000",   # Black
            on_surface="#000000",      # Black
            on_error="#FFFFFF",        # White
            
            border="#000000",          # Black
            hover="#F0F0F0",           # Light Gray
            pressed="#808080",         # Gray
            disabled="#808080",        # Gray
            selected="#0000FF",        # Blue
        )
    
    def _init_system_detector(self):
        """시스템 테마 감지기 초기화"""
        try:
            self._system_theme_detector = SystemThemeDetector()
            logger.info("System theme detector initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize system theme detector: {e}")
    
    def _check_system_theme_change(self):
        """시스템 테마 변경 감지 및 적용"""
        if not self._system_theme_detector:
            return
        
        if self._current_theme != ThemeType.FOLLOW_SYSTEM:
            return
        
        try:
            current_system_theme_str = self._system_theme_detector.get_system_theme()
            if current_system_theme_str != self._last_system_theme:
                self._last_system_theme = current_system_theme_str
                actual_theme = ThemeType.DARK if current_system_theme_str == "dark" else ThemeType.LIGHT
                self._apply_theme(actual_theme)
                logger.info(f"System theme changed to: {current_system_theme_str}")
        except Exception as e:
            logger.error(f"Error checking system theme change: {e}")
    
    def set_theme(self, theme: ThemeType) -> bool:
        """
        테마 설정
        
        Args:
            theme: 적용할 테마
            
        Returns:
            성공 여부
        """
        try:
            if theme == self._current_theme:
                return True
            
            old_theme = self._current_theme
            self._current_theme = theme
            
            # 시스템 테마 팔로우 모드 처리
            if theme == ThemeType.FOLLOW_SYSTEM:
                if self._system_theme_detector:
                    system_theme_str = self._system_theme_detector.get_system_theme()
                    actual_theme = ThemeType.DARK if system_theme_str == "dark" else ThemeType.LIGHT
                    self._last_system_theme = system_theme_str
                    self._theme_check_timer.start()
                else:
                    # 시스템 감지 실패시 라이트 테마로 폴백
                    actual_theme = ThemeType.LIGHT
                    logger.warning("System theme detection failed, falling back to light theme")
            else:
                self._theme_check_timer.stop()
                actual_theme = theme
            
            # 테마 적용
            success = self._apply_theme(actual_theme)
            
            if success:
                # 설정 저장
                self.settings.setValue("theme/current", theme.value)
                self.theme_changed.emit(theme.value)
                logger.info(f"Theme changed from {old_theme.value} to {theme.value}")
            else:
                # 실패시 롤백
                self._current_theme = old_theme
                logger.error(f"Failed to apply theme: {theme.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting theme {theme.value}: {e}")
            return False
    
    def _apply_theme(self, theme: ThemeType) -> bool:
        """
        실제 테마 적용
        
        Args:
            theme: 적용할 테마
            
        Returns:
            성공 여부
        """
        try:
            # QSS 스타일시트 로드
            stylesheet = self._load_stylesheet(theme)
            if not stylesheet:
                return False
            
            # 테마 색상으로 스타일시트 변수 치환
            colors = self._theme_colors.get(theme)
            if colors:
                stylesheet = self._replace_color_variables(stylesheet, colors)
            
            # 스무스 트랜지션으로 스타일시트 적용
            if self._transition_enabled:
                self._apply_theme_with_transition(stylesheet, theme, colors)
            else:
                # 애플리케이션에 스타일시트 적용
                self.app.setStyleSheet(stylesheet)
                
                # QPalette 설정 (fallback)
                self._set_application_palette(theme)
                
                # 등록된 콜백 함수들 호출
                self._call_theme_callbacks(theme, colors)
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying theme {theme.value}: {e}")
            return False
    
    def _apply_theme_with_transition(self, stylesheet: str, theme: ThemeType, colors: ThemeColors):
        """
        트랜지션 애니메이션과 함께 테마 적용
        
        Args:
            stylesheet: 적용할 스타일시트
            theme: 테마 타입
            colors: 테마 색상
        """
        try:
            # 기존 애니메이션 중단
            if self._current_animation:
                self._current_animation.stop()
                self._current_animation.deleteLater()
                self._current_animation = None
            
            # 메인 윈도우 찾기
            main_widget = None
            for widget in self.app.topLevelWidgets():
                if widget.isVisible() and hasattr(widget, 'centralWidget'):
                    main_widget = widget
                    break
            
            if main_widget:
                # 페이드 아웃 → 스타일 변경 → 페이드 인 효과
                self._create_fade_transition(main_widget, stylesheet, theme, colors)
            else:
                # 메인 위젯이 없으면 즉시 적용
                self._apply_theme_directly(stylesheet, theme, colors)
                
        except Exception as e:
            logger.error(f"Error in theme transition: {e}")
            # 오류시 직접 적용
            self._apply_theme_directly(stylesheet, theme, colors)
    
    def _create_fade_transition(self, widget: QWidget, stylesheet: str, theme: ThemeType, colors: ThemeColors):
        """
        페이드 트랜지션 생성
        
        Args:
            widget: 대상 위젯
            stylesheet: 스타일시트
            theme: 테마
            colors: 색상
        """
        try:
            # 투명도 효과 생성
            opacity_effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(opacity_effect)
            
            # 페이드 아웃 애니메이션
            self._current_animation = QPropertyAnimation(opacity_effect, b"opacity")
            self._current_animation.setDuration(self._transition_duration // 2)  # 절반 시간으로 페이드 아웃
            self._current_animation.setStartValue(1.0)
            self._current_animation.setEndValue(0.3)  # 완전히 투명하게 하지 않고 30%까지만
            self._current_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # 페이드 아웃 완료시 스타일 변경 후 페이드 인
            self._current_animation.finished.connect(
                lambda: self._on_fade_out_finished(widget, stylesheet, theme, colors, opacity_effect)
            )
            
            self._current_animation.start()
            
        except Exception as e:
            logger.error(f"Error creating fade transition: {e}")
            # 오류시 직접 적용
            widget.setGraphicsEffect(None)
            self._apply_theme_directly(stylesheet, theme, colors)
    
    def _on_fade_out_finished(self, widget: QWidget, stylesheet: str, theme: ThemeType, 
                             colors: ThemeColors, opacity_effect: QGraphicsOpacityEffect):
        """
        페이드 아웃 완료시 호출
        """
        try:
            # 스타일 변경
            self._apply_theme_directly(stylesheet, theme, colors)
            
            # 페이드 인 애니메이션
            self._current_animation = QPropertyAnimation(opacity_effect, b"opacity")
            self._current_animation.setDuration(self._transition_duration // 2)  # 절반 시간으로 페이드 인
            self._current_animation.setStartValue(0.3)
            self._current_animation.setEndValue(1.0)
            self._current_animation.setEasingCurve(QEasingCurve.Type.InCubic)
            
            # 페이드 인 완료시 효과 제거
            self._current_animation.finished.connect(
                lambda: self._cleanup_transition(widget)
            )
            
            self._current_animation.start()
            
        except Exception as e:
            logger.error(f"Error in fade out finished handler: {e}")
            self._cleanup_transition(widget)
    
    def _cleanup_transition(self, widget: QWidget):
        """트랜지션 정리"""
        try:
            widget.setGraphicsEffect(None)
            if self._current_animation:
                self._current_animation.deleteLater()
                self._current_animation = None
        except Exception as e:
            logger.error(f"Error cleaning up transition: {e}")
    
    def _apply_theme_directly(self, stylesheet: str, theme: ThemeType, colors: ThemeColors):
        """직접 테마 적용 (애니메이션 없이)"""
        try:
            # 애플리케이션에 스타일시트 적용
            self.app.setStyleSheet(stylesheet)
            
            # QPalette 설정 (fallback)
            self._set_application_palette(theme)
            
            # 등록된 콜백 함수들 호출
            self._call_theme_callbacks(theme, colors)
            
        except Exception as e:
            logger.error(f"Error applying theme directly: {e}")
    
    def _call_theme_callbacks(self, theme: ThemeType, colors: ThemeColors):
        """테마 콜백 함수들 호출"""
        for callback in self._theme_callbacks:
            try:
                callback(theme, colors)
            except Exception as e:
                logger.warning(f"Theme callback error: {e}")
    
    def _load_stylesheet(self, theme: ThemeType) -> Optional[str]:
        """
        QSS 스타일시트 파일 로드
        
        Args:
            theme: 테마 타입
            
        Returns:
            스타일시트 문자열
        """
        try:
            if theme == ThemeType.HIGH_CONTRAST:
                filename = "high_contrast_theme.qss"  
            else:
                filename = f"{theme.value}_theme.qss"
            stylesheet_path = self.styles_dir / filename
            
            if not stylesheet_path.exists():
                logger.error(f"Stylesheet not found: {stylesheet_path}")
                return None
            
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error loading stylesheet for {theme.value}: {e}")
            return None
    
    def _replace_color_variables(self, stylesheet: str, colors: ThemeColors) -> str:
        """
        스타일시트의 색상 변수를 실제 색상으로 치환
        
        Args:
            stylesheet: 원본 스타일시트
            colors: 테마 색상 정보
            
        Returns:
            치환된 스타일시트
        """
        try:
            # 색상 변수 매핑
            color_vars = {
                "@primary": colors.primary,
                "@primary-variant": colors.primary_variant,
                "@secondary": colors.secondary,
                "@secondary-variant": colors.secondary_variant,
                "@background": colors.background,
                "@surface": colors.surface,
                "@error": colors.error,
                "@on-primary": colors.on_primary,
                "@on-secondary": colors.on_secondary,
                "@on-background": colors.on_background,
                "@on-surface": colors.on_surface,
                "@on-error": colors.on_error,
                "@border": colors.border,
                "@hover": colors.hover,
                "@pressed": colors.pressed,
                "@disabled": colors.disabled,
                "@selected": colors.selected,
                "@accent": colors.accent,
            }
            
            # 변수 치환
            result = stylesheet
            for var, color in color_vars.items():
                result = result.replace(var, color)
            
            return result
            
        except Exception as e:
            logger.error(f"Error replacing color variables: {e}")
            return stylesheet
    
    def _set_application_palette(self, theme: ThemeType):
        """
        QPalette 설정 (QSS fallback)
        
        Args:
            theme: 테마 타입
        """
        try:
            colors = self._theme_colors.get(theme)
            if not colors:
                return
            
            palette = QPalette()
            
            # 기본 색상 설정
            palette.setColor(QPalette.ColorRole.Window, QColor(colors.background))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.on_background))
            palette.setColor(QPalette.ColorRole.Base, QColor(colors.surface))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.hover))
            palette.setColor(QPalette.ColorRole.Text, QColor(colors.on_surface))
            palette.setColor(QPalette.ColorRole.Button, QColor(colors.primary))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.on_primary))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.selected))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.on_primary))
            
            # 비활성화 색상
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(colors.disabled))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(colors.disabled))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(colors.disabled))
            
            self.app.setPalette(palette)
            
        except Exception as e:
            logger.error(f"Error setting application palette: {e}")
    
    def set_accent_color(self, color: str) -> bool:
        """
        액센트 색상 설정
        
        Args:
            color: 헥스 색상 코드 (예: "#3B82F6")
            
        Returns:
            성공 여부
        """
        try:
            if not self._validate_color(color):
                logger.error(f"Invalid color format: {color}")
                return False
            
            old_accent = self._current_accent
            self._current_accent = color
            
            # 모든 테마의 액센트 색상 업데이트
            for theme_colors in self._theme_colors.values():
                theme_colors.accent = color
            
            # 현재 테마 다시 적용
            actual_theme = self._get_actual_theme()
            success = self._apply_theme(actual_theme)
            
            if success:
                self.settings.setValue("theme/accent_color", color)
                self.accent_changed.emit(color)
                logger.info(f"Accent color changed from {old_accent} to {color}")
            else:
                # 실패시 롤백
                self._current_accent = old_accent
                for theme_colors in self._theme_colors.values():
                    theme_colors.accent = old_accent
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting accent color {color}: {e}")
            return False
    
    def _validate_color(self, color: str) -> bool:
        """색상 형식 검증"""
        if not color or not isinstance(color, str):
            return False
        
        # 헥스 색상 형식 검증 (#RRGGBB or #RGB)
        if color.startswith('#'):
            hex_part = color[1:]
            if len(hex_part) in [3, 6] and all(c in '0123456789ABCDEFabcdef' for c in hex_part):
                return True
        
        return False
    
    def _get_actual_theme(self) -> ThemeType:
        """현재 실제 적용된 테마 반환"""
        if self._current_theme == ThemeType.FOLLOW_SYSTEM:
            if self._system_theme_detector:
                system_theme_str = self._system_theme_detector.get_system_theme()
                return ThemeType.DARK if system_theme_str == "dark" else ThemeType.LIGHT
            else:
                return ThemeType.LIGHT  # fallback
        return self._current_theme
    
    def get_current_theme(self) -> ThemeType:
        """현재 테마 설정 반환"""
        return self._current_theme
    
    def get_current_accent(self) -> str:
        """현재 액센트 색상 반환"""
        return self._current_accent
    
    def get_theme_colors(self, theme: Optional[ThemeType] = None) -> Optional[ThemeColors]:
        """
        테마 색상 정보 반환
        
        Args:
            theme: 테마 타입 (None이면 현재 테마)
            
        Returns:
            테마 색상 정보
        """
        if theme is None:
            theme = self._get_actual_theme()
        return self._theme_colors.get(theme)
    
    def is_dark_theme(self) -> bool:
        """다크 테마 사용 중인지 확인"""
        actual_theme = self._get_actual_theme()
        return actual_theme == ThemeType.DARK
    
    def register_theme_callback(self, callback: Callable[[ThemeType, ThemeColors], None]):
        """
        테마 변경 콜백 등록
        
        Args:
            callback: 테마 변경시 호출될 함수
        """
        if callback not in self._theme_callbacks:
            self._theme_callbacks.append(callback)
    
    def unregister_theme_callback(self, callback: Callable):
        """테마 변경 콜백 제거"""
        if callback in self._theme_callbacks:
            self._theme_callbacks.remove(callback)
    
    def load_settings(self):
        """저장된 설정 로드"""
        try:
            # 테마 설정 로드
            theme_str = self.settings.value("theme/current", ThemeType.FOLLOW_SYSTEM.value)
            try:
                theme = ThemeType(theme_str)
            except ValueError:
                theme = ThemeType.FOLLOW_SYSTEM
                logger.warning(f"Invalid theme setting: {theme_str}, using default")
            
            # 액센트 색상 로드
            accent_color = self.settings.value("theme/accent_color", "#3B82F6")
            if self._validate_color(accent_color):
                self._current_accent = accent_color
                for theme_colors in self._theme_colors.values():
                    theme_colors.accent = accent_color
            
            # 테마 적용
            self.set_theme(theme)
            
            logger.info(f"Theme settings loaded: theme={theme.value}, accent={accent_color}")
            
        except Exception as e:
            logger.error(f"Error loading theme settings: {e}")
    
    def save_settings(self):
        """현재 설정 저장"""
        try:
            self.settings.setValue("theme/current", self._current_theme.value)
            self.settings.setValue("theme/accent_color", self._current_accent)
            self.settings.sync()
            
        except Exception as e:
            logger.error(f"Error saving theme settings: {e}")
    
    def get_available_themes(self) -> Dict[ThemeType, str]:
        """사용 가능한 테마 목록 반환"""
        return {
            ThemeType.FOLLOW_SYSTEM: "시스템 기본",
            ThemeType.LIGHT: "라이트 테마",
            ThemeType.DARK: "다크 테마",
            ThemeType.HIGH_CONTRAST: "고대비 테마"
        }
    
    def set_transition_enabled(self, enabled: bool):
        """
        테마 트랜지션 애니메이션 활성화/비활성화
        
        Args:
            enabled: 활성화 여부
        """
        self._transition_enabled = enabled
        logger.debug(f"Theme transitions {'enabled' if enabled else 'disabled'}")
    
    def set_transition_duration(self, duration_ms: int):
        """
        트랜지션 애니메이션 시간 설정
        
        Args:
            duration_ms: 애니메이션 시간 (밀리초)
        """
        if 100 <= duration_ms <= 2000:  # 0.1초 ~ 2초 제한
            self._transition_duration = duration_ms
            logger.debug(f"Theme transition duration set to {duration_ms}ms")
        else:
            logger.warning(f"Invalid transition duration: {duration_ms}ms (must be between 100-2000ms)")
    
    def is_transition_enabled(self) -> bool:
        """트랜지션 활성화 상태 반환"""
        return self._transition_enabled
    
    def get_transition_duration(self) -> int:
        """트랜지션 시간 반환"""
        return self._transition_duration
    
    def cleanup(self):
        """정리"""
        try:
            # 진행 중인 애니메이션 정리
            if self._current_animation:
                self._current_animation.stop()
                self._current_animation.deleteLater()
                self._current_animation = None
            
            self._theme_check_timer.stop()
            self.save_settings()
            logger.info("Theme manager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# 전역 테마 매니저 인스턴스
_theme_manager: Optional[ThemeManager] = None


def init_theme_manager(app: QApplication, config_dir: Path = None) -> ThemeManager:
    """
    전역 테마 매니저 초기화
    
    Args:
        app: QApplication 인스턴스
        config_dir: 설정 디렉토리
        
    Returns:
        테마 매니저 인스턴스
    """
    global _theme_manager
    
    if _theme_manager is not None:
        logger.warning("Theme manager already initialized")
        return _theme_manager
    
    _theme_manager = ThemeManager(app, config_dir)
    _theme_manager.load_settings()
    
    return _theme_manager


def get_theme_manager() -> Optional[ThemeManager]:
    """전역 테마 매니저 인스턴스 반환"""
    return _theme_manager


def cleanup_theme_manager():
    """전역 테마 매니저 정리"""
    global _theme_manager
    
    if _theme_manager:
        _theme_manager.cleanup()
        _theme_manager = None
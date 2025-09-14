"""
Keyboard Navigation System
Comprehensive keyboard navigation and shortcut management for accessibility
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple, Set, Any
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog,
    QPushButton, QCheckBox, QComboBox, QLineEdit, QTextEdit,
    QSlider, QProgressBar, QTabWidget, QGroupBox, QScrollArea,
    QTreeWidget, QListWidget, QTableWidget, QSplitter, QStackedWidget
)
from PyQt6.QtCore import (
    QObject, pyqtSignal, QSettings, QTimer, Qt, QEvent, QModelIndex,
    QKeyCombination
)
from PyQt6.QtGui import (
    QKeySequence, QAction, QShortcut, QKeyEvent, QFocusEvent
)

from .logger import get_logger


logger = get_logger(__name__)


class NavigationScope(Enum):
    """네비게이션 범위"""
    GLOBAL = "global"          # 전역 단축키
    WINDOW = "window"          # 윈도우 레벨
    DIALOG = "dialog"          # 다이얼로그 레벨
    PANEL = "panel"            # 패널/그룹 레벨
    WIDGET = "widget"          # 위젯 레벨


class NavigationAction(Enum):
    """네비게이션 액션"""
    # 기본 네비게이션
    NEXT_FOCUS = "next_focus"
    PREV_FOCUS = "prev_focus"
    FIRST_FOCUS = "first_focus"
    LAST_FOCUS = "last_focus"
    
    # 컨테이너 네비게이션
    NEXT_PANEL = "next_panel"
    PREV_PANEL = "prev_panel"
    NEXT_TAB = "next_tab"
    PREV_TAB = "prev_tab"
    
    # 리스트/테이블 네비게이션
    NEXT_ITEM = "next_item"
    PREV_ITEM = "prev_item"
    FIRST_ITEM = "first_item"
    LAST_ITEM = "last_item"
    
    # 페이지 네비게이션
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"
    HOME = "home"
    END = "end"
    
    # 선택 액션
    SELECT_ITEM = "select_item"
    TOGGLE_SELECTION = "toggle_selection"
    SELECT_ALL = "select_all"
    SELECT_NONE = "select_none"
    
    # 편집 액션
    EDIT_ITEM = "edit_item"
    DELETE_ITEM = "delete_item"
    COPY_ITEM = "copy_item"
    PASTE_ITEM = "paste_item"
    
    # 애플리케이션 액션
    OPEN_FILE = "open_file"
    SAVE_FILE = "save_file"
    NEW_FILE = "new_file"
    CLOSE_WINDOW = "close_window"
    EXIT_APP = "exit_app"
    
    # 도움말
    SHOW_HELP = "show_help"
    SHOW_SHORTCUTS = "show_shortcuts"
    
    # 접근성 기능
    TOGGLE_HIGH_CONTRAST = "toggle_high_contrast"
    INCREASE_FONT_SIZE = "increase_font_size"
    DECREASE_FONT_SIZE = "decrease_font_size"
    
    # 검색
    FIND = "find"
    FIND_NEXT = "find_next"
    FIND_PREV = "find_prev"


@dataclass
class KeyboardShortcut:
    """키보드 단축키 정의"""
    action: NavigationAction
    key_sequence: str
    scope: NavigationScope
    description: str
    callback: Optional[Callable] = None
    widget: Optional[QWidget] = None
    enabled: bool = True
    customizable: bool = True
    context: str = ""


@dataclass
class NavigationContext:
    """네비게이션 컨텍스트"""
    widget: QWidget
    parent_context: Optional['NavigationContext'] = None
    child_contexts: List['NavigationContext'] = field(default_factory=list)
    tab_order: List[QWidget] = field(default_factory=list)
    shortcuts: Dict[str, KeyboardShortcut] = field(default_factory=dict)
    is_modal: bool = False
    
    def add_child(self, child: 'NavigationContext'):
        """자식 컨텍스트 추가"""
        child.parent_context = self
        self.child_contexts.append(child)
    
    def remove_child(self, child: 'NavigationContext'):
        """자식 컨텍스트 제거"""
        if child in self.child_contexts:
            child.parent_context = None
            self.child_contexts.remove(child)


class FocusTracker:
    """포커스 추적기"""
    
    def __init__(self):
        self.focus_history: List[QWidget] = []
        self.focus_stack: List[QWidget] = []  # 모달 다이얼로그용
        self.max_history = 20
    
    def add_focus(self, widget: QWidget):
        """포커스 기록 추가"""
        if widget in self.focus_history:
            self.focus_history.remove(widget)
        
        self.focus_history.append(widget)
        
        if len(self.focus_history) > self.max_history:
            self.focus_history.pop(0)
    
    def get_previous_focus(self) -> Optional[QWidget]:
        """이전 포커스 위젯 반환"""
        if len(self.focus_history) >= 2:
            return self.focus_history[-2]
        return None
    
    def push_focus_context(self, widget: QWidget):
        """포커스 컨텍스트 스택에 푸시 (모달용)"""
        current_focus = QApplication.focusWidget()
        if current_focus:
            self.focus_stack.append(current_focus)
    
    def pop_focus_context(self) -> Optional[QWidget]:
        """포커스 컨텍스트 스택에서 팝"""
        if self.focus_stack:
            return self.focus_stack.pop()
        return None


class KeyboardNavigationManager(QObject):
    """키보드 네비게이션 관리자"""
    
    # 시그널
    focus_changed = pyqtSignal(QWidget, QWidget)  # old, new
    shortcut_activated = pyqtSignal(str, str)     # action, context
    navigation_mode_changed = pyqtSignal(bool)   # enabled
    
    def __init__(self, app: QApplication):
        super().__init__()
        
        self.app = app
        self.settings = QSettings()
        
        # 네비게이션 상태
        self.is_enabled = True
        self.is_navigation_mode = False  # 특별한 네비게이션 모드
        self.skip_next_focus = False
        
        # 컨텍스트 관리
        self.root_contexts: List[NavigationContext] = []
        self.current_context: Optional[NavigationContext] = None
        self.modal_contexts: List[NavigationContext] = []
        
        # 포커스 관리
        self.focus_tracker = FocusTracker()
        
        # 기본 단축키 정의
        self.default_shortcuts: Dict[NavigationAction, str] = {}
        self.custom_shortcuts: Dict[NavigationAction, str] = {}
        self.global_shortcuts: Dict[str, QShortcut] = {}
        
        # 위젯별 네비게이션 핸들러
        self.widget_handlers: Dict[type, Callable] = {}
        
        # 스킵 링크 관리
        self.skip_links: Dict[str, QWidget] = {}
        self.skip_targets: Dict[str, QWidget] = {}
        
        # 초기화
        self._init_default_shortcuts()
        self._init_widget_handlers()
        self._load_custom_shortcuts()
        self._setup_global_shortcuts()
        
        # 애플리케이션 이벤트 연결
        self.app.focusChanged.connect(self._on_focus_changed)
        self.app.installEventFilter(self)
        
        logger.info("Keyboard Navigation Manager initialized")
    
    def _init_default_shortcuts(self):
        """기본 단축키 초기화"""
        self.default_shortcuts = {
            # 기본 네비게이션
            NavigationAction.NEXT_FOCUS: "Tab",
            NavigationAction.PREV_FOCUS: "Shift+Tab",
            NavigationAction.FIRST_FOCUS: "Home",
            NavigationAction.LAST_FOCUS: "End",
            
            # 컨테이너 네비게이션
            NavigationAction.NEXT_PANEL: "Ctrl+F6",
            NavigationAction.PREV_PANEL: "Ctrl+Shift+F6",
            NavigationAction.NEXT_TAB: "Ctrl+Tab",
            NavigationAction.PREV_TAB: "Ctrl+Shift+Tab",
            
            # 리스트/테이블 네비게이션
            NavigationAction.NEXT_ITEM: "Down",
            NavigationAction.PREV_ITEM: "Up",
            NavigationAction.FIRST_ITEM: "Ctrl+Home",
            NavigationAction.LAST_ITEM: "Ctrl+End",
            
            # 페이지 네비게이션
            NavigationAction.PAGE_UP: "Page_Up",
            NavigationAction.PAGE_DOWN: "Page_Down",
            
            # 선택 액션
            NavigationAction.SELECT_ITEM: "Space",
            NavigationAction.TOGGLE_SELECTION: "Ctrl+Space",
            NavigationAction.SELECT_ALL: "Ctrl+A",
            NavigationAction.SELECT_NONE: "Ctrl+Shift+A",
            
            # 편집 액션
            NavigationAction.EDIT_ITEM: "F2",
            NavigationAction.DELETE_ITEM: "Delete",
            NavigationAction.COPY_ITEM: "Ctrl+C",
            NavigationAction.PASTE_ITEM: "Ctrl+V",
            
            # 애플리케이션 액션
            NavigationAction.OPEN_FILE: "Ctrl+O",
            NavigationAction.SAVE_FILE: "Ctrl+S",
            NavigationAction.NEW_FILE: "Ctrl+N",
            NavigationAction.CLOSE_WINDOW: "Ctrl+W",
            NavigationAction.EXIT_APP: "Ctrl+Q",
            
            # 도움말
            NavigationAction.SHOW_HELP: "F1",
            NavigationAction.SHOW_SHORTCUTS: "Ctrl+F1",
            
            # 접근성 기능
            NavigationAction.TOGGLE_HIGH_CONTRAST: "Ctrl+Alt+H",
            NavigationAction.INCREASE_FONT_SIZE: "Ctrl++",
            NavigationAction.DECREASE_FONT_SIZE: "Ctrl+-",
            
            # 검색
            NavigationAction.FIND: "Ctrl+F",
            NavigationAction.FIND_NEXT: "F3",
            NavigationAction.FIND_PREV: "Shift+F3",
        }
    
    def _init_widget_handlers(self):
        """위젯별 네비게이션 핸들러 초기화"""
        self.widget_handlers = {
            QTreeWidget: self._handle_tree_navigation,
            QListWidget: self._handle_list_navigation,
            QTableWidget: self._handle_table_navigation,
            QTabWidget: self._handle_tab_navigation,
            QComboBox: self._handle_combo_navigation,
            QTextEdit: self._handle_text_navigation,
            QLineEdit: self._handle_line_edit_navigation,
        }
    
    def _load_custom_shortcuts(self):
        """사용자 정의 단축키 로드"""
        try:
            self.settings.beginGroup("keyboard_navigation")
            
            for action in NavigationAction:
                key = f"shortcut_{action.value}"
                custom_key = self.settings.value(key, "")
                if custom_key:
                    self.custom_shortcuts[action] = custom_key
            
            self.settings.endGroup()
            logger.info("Custom shortcuts loaded")
            
        except Exception as e:
            logger.error(f"Failed to load custom shortcuts: {e}")
    
    def _save_custom_shortcuts(self):
        """사용자 정의 단축키 저장"""
        try:
            self.settings.beginGroup("keyboard_navigation")
            
            for action, key_sequence in self.custom_shortcuts.items():
                key = f"shortcut_{action.value}"
                self.settings.setValue(key, key_sequence)
            
            self.settings.endGroup()
            self.settings.sync()
            logger.info("Custom shortcuts saved")
            
        except Exception as e:
            logger.error(f"Failed to save custom shortcuts: {e}")
    
    def _setup_global_shortcuts(self):
        """전역 단축키 설정"""
        try:
            # 기본 전역 단축키들
            global_actions = [
                NavigationAction.SHOW_HELP,
                NavigationAction.SHOW_SHORTCUTS,
                NavigationAction.TOGGLE_HIGH_CONTRAST,
                NavigationAction.INCREASE_FONT_SIZE,
                NavigationAction.DECREASE_FONT_SIZE,
            ]
            
            for action in global_actions:
                key_sequence = self.get_key_sequence(action)
                if key_sequence:
                    shortcut = QShortcut(QKeySequence(key_sequence), None)
                    shortcut.activated.connect(
                        lambda a=action: self._handle_global_shortcut(a)
                    )
                    shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
                    self.global_shortcuts[action.value] = shortcut
            
        except Exception as e:
            logger.error(f"Failed to setup global shortcuts: {e}")
    
    def get_key_sequence(self, action: NavigationAction) -> str:
        """액션에 대한 키 시퀀스 반환 (사용자 정의 우선)"""
        return self.custom_shortcuts.get(action) or self.default_shortcuts.get(action, "")
    
    def set_custom_shortcut(self, action: NavigationAction, key_sequence: str) -> bool:
        """사용자 정의 단축키 설정"""
        try:
            # 키 시퀀스 유효성 검사
            if not QKeySequence(key_sequence).isEmpty():
                self.custom_shortcuts[action] = key_sequence
                
                # 전역 단축키인 경우 업데이트
                if action.value in self.global_shortcuts:
                    old_shortcut = self.global_shortcuts[action.value]
                    old_shortcut.deleteLater()
                    
                    new_shortcut = QShortcut(QKeySequence(key_sequence), None)
                    new_shortcut.activated.connect(
                        lambda: self._handle_global_shortcut(action)
                    )
                    new_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
                    self.global_shortcuts[action.value] = new_shortcut
                
                self._save_custom_shortcuts()
                logger.info(f"Custom shortcut set: {action.value} = {key_sequence}")
                return True
            else:
                logger.warning(f"Invalid key sequence: {key_sequence}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set custom shortcut: {e}")
            return False
    
    def reset_shortcut(self, action: NavigationAction) -> bool:
        """단축키를 기본값으로 리셋"""
        try:
            if action in self.custom_shortcuts:
                del self.custom_shortcuts[action]
                
                # 전역 단축키인 경우 업데이트
                if action.value in self.global_shortcuts:
                    old_shortcut = self.global_shortcuts[action.value]
                    old_shortcut.deleteLater()
                    
                    default_key = self.default_shortcuts.get(action)
                    if default_key:
                        new_shortcut = QShortcut(QKeySequence(default_key), None)
                        new_shortcut.activated.connect(
                            lambda: self._handle_global_shortcut(action)
                        )
                        new_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
                        self.global_shortcuts[action.value] = new_shortcut
                
                self._save_custom_shortcuts()
                logger.info(f"Shortcut reset to default: {action.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to reset shortcut: {e}")
            return False
    
    def register_context(self, widget: QWidget, 
                        parent_context: NavigationContext = None) -> NavigationContext:
        """네비게이션 컨텍스트 등록"""
        try:
            context = NavigationContext(widget=widget)
            
            if parent_context:
                parent_context.add_child(context)
            else:
                self.root_contexts.append(context)
            
            # 위젯이 모달인지 확인
            if isinstance(widget, QDialog) and widget.isModal():
                context.is_modal = True
                self.modal_contexts.append(context)
            
            # 위젯의 탭 순서 설정
            self._setup_tab_order(context)
            
            logger.debug(f"Navigation context registered: {widget.__class__.__name__}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to register navigation context: {e}")
            return None
    
    def unregister_context(self, context: NavigationContext):
        """네비게이션 컨텍스트 등록 해제"""
        try:
            if context.parent_context:
                context.parent_context.remove_child(context)
            else:
                if context in self.root_contexts:
                    self.root_contexts.remove(context)
            
            if context in self.modal_contexts:
                self.modal_contexts.remove(context)
            
            if context == self.current_context:
                self.current_context = context.parent_context
            
            logger.debug("Navigation context unregistered")
            
        except Exception as e:
            logger.error(f"Failed to unregister navigation context: {e}")
    
    def _setup_tab_order(self, context: NavigationContext):
        """컨텍스트의 탭 순서 설정"""
        try:
            widget = context.widget
            tab_order = []
            
            # 포커스 가능한 자식 위젯들 찾기
            focusable_widgets = []
            self._find_focusable_widgets(widget, focusable_widgets)
            
            # 위치 기반으로 정렬 (위 → 아래, 왼쪽 → 오른쪽)
            focusable_widgets.sort(key=lambda w: (w.pos().y(), w.pos().x()) if w.parent() else (0, 0))
            
            context.tab_order = focusable_widgets
            
            # Qt 탭 순서도 설정
            for i in range(len(focusable_widgets) - 1):
                QWidget.setTabOrder(focusable_widgets[i], focusable_widgets[i + 1])
            
            logger.debug(f"Tab order set for context: {len(focusable_widgets)} widgets")
            
        except Exception as e:
            logger.error(f"Failed to setup tab order: {e}")
    
    def _find_focusable_widgets(self, parent: QWidget, result: List[QWidget]):
        """포커스 가능한 위젯들 재귀적으로 찾기"""
        for child in parent.findChildren(QWidget):
            if (child.focusPolicy() != Qt.FocusPolicy.NoFocus and 
                child.isVisible() and child.isEnabled()):
                result.append(child)
    
    def add_skip_link(self, link_id: str, source_widget: QWidget, target_widget: QWidget):
        """스킵 링크 추가"""
        try:
            self.skip_links[link_id] = source_widget
            self.skip_targets[link_id] = target_widget
            
            # 소스 위젯에 키보드 이벤트 핸들러 추가
            if hasattr(source_widget, 'keyPressEvent'):
                original_handler = source_widget.keyPressEvent
                def new_handler(event):
                    if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Space:
                        self.activate_skip_link(link_id)
                        event.accept()
                    else:
                        original_handler(event)
                source_widget.keyPressEvent = new_handler
            
            logger.debug(f"Skip link added: {link_id}")
            
        except Exception as e:
            logger.error(f"Failed to add skip link {link_id}: {e}")
    
    def activate_skip_link(self, link_id: str):
        """스킵 링크 활성화"""
        try:
            target = self.skip_targets.get(link_id)
            if target and target.isVisible() and target.isEnabled():
                target.setFocus()
                # 스크린 리더에 알림
                from .accessibility_manager import get_accessibility_manager
                accessibility_manager = get_accessibility_manager()
                if accessibility_manager:
                    accessibility_manager.announce_message(
                        f"스킵: {target.accessibleName() or target.objectName() or '콘텐츠'}로 이동",
                        "assertive"
                    )
                logger.info(f"Skip link activated: {link_id}")
        
        except Exception as e:
            logger.error(f"Failed to activate skip link {link_id}: {e}")
    
    def navigate_to_next_widget(self, current_widget: QWidget = None) -> bool:
        """다음 위젯으로 네비게이션"""
        try:
            if not current_widget:
                current_widget = self.app.focusWidget()
            
            if not current_widget:
                return self._focus_first_widget()
            
            context = self._find_widget_context(current_widget)
            if not context:
                return False
            
            current_index = -1
            try:
                current_index = context.tab_order.index(current_widget)
            except ValueError:
                return False
            
            # 다음 위젯으로 이동
            next_index = (current_index + 1) % len(context.tab_order)
            next_widget = context.tab_order[next_index]
            
            if next_widget.isVisible() and next_widget.isEnabled():
                next_widget.setFocus()
                return True
            else:
                # 다음 유효한 위젯 찾기
                return self._find_next_valid_widget(context, next_index)
        
        except Exception as e:
            logger.error(f"Failed to navigate to next widget: {e}")
            return False
    
    def navigate_to_prev_widget(self, current_widget: QWidget = None) -> bool:
        """이전 위젯으로 네비게이션"""
        try:
            if not current_widget:
                current_widget = self.app.focusWidget()
            
            if not current_widget:
                return self._focus_last_widget()
            
            context = self._find_widget_context(current_widget)
            if not context:
                return False
            
            current_index = -1
            try:
                current_index = context.tab_order.index(current_widget)
            except ValueError:
                return False
            
            # 이전 위젯으로 이동
            prev_index = (current_index - 1) % len(context.tab_order)
            prev_widget = context.tab_order[prev_index]
            
            if prev_widget.isVisible() and prev_widget.isEnabled():
                prev_widget.setFocus()
                return True
            else:
                # 이전 유효한 위젯 찾기
                return self._find_prev_valid_widget(context, prev_index)
        
        except Exception as e:
            logger.error(f"Failed to navigate to prev widget: {e}")
            return False
    
    def _focus_first_widget(self) -> bool:
        """첫 번째 위젯에 포커스"""
        try:
            context = self._get_current_context()
            if context and context.tab_order:
                for widget in context.tab_order:
                    if widget.isVisible() and widget.isEnabled():
                        widget.setFocus()
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to focus first widget: {e}")
            return False
    
    def _focus_last_widget(self) -> bool:
        """마지막 위젯에 포커스"""
        try:
            context = self._get_current_context()
            if context and context.tab_order:
                for widget in reversed(context.tab_order):
                    if widget.isVisible() and widget.isEnabled():
                        widget.setFocus()
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to focus last widget: {e}")
            return False
    
    def _find_next_valid_widget(self, context: NavigationContext, start_index: int) -> bool:
        """다음 유효한 위젯 찾기"""
        try:
            for i in range(len(context.tab_order)):
                index = (start_index + i) % len(context.tab_order)
                widget = context.tab_order[index]
                if widget.isVisible() and widget.isEnabled():
                    widget.setFocus()
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to find next valid widget: {e}")
            return False
    
    def _find_prev_valid_widget(self, context: NavigationContext, start_index: int) -> bool:
        """이전 유효한 위젯 찾기"""
        try:
            for i in range(len(context.tab_order)):
                index = (start_index - i) % len(context.tab_order)
                widget = context.tab_order[index]
                if widget.isVisible() and widget.isEnabled():
                    widget.setFocus()
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to find prev valid widget: {e}")
            return False
    
    def _find_widget_context(self, widget: QWidget) -> Optional[NavigationContext]:
        """위젯이 속한 네비게이션 컨텍스트 찾기"""
        def search_contexts(contexts: List[NavigationContext]) -> Optional[NavigationContext]:
            for context in contexts:
                if widget in context.tab_order or widget == context.widget:
                    return context
                result = search_contexts(context.child_contexts)
                if result:
                    return result
            return None
        
        # 모달 컨텍스트 우선 검색
        if self.modal_contexts:
            result = search_contexts(self.modal_contexts)
            if result:
                return result
        
        # 루트 컨텍스트 검색
        return search_contexts(self.root_contexts)
    
    def _get_current_context(self) -> Optional[NavigationContext]:
        """현재 활성 컨텍스트 반환"""
        if self.modal_contexts:
            return self.modal_contexts[-1]  # 최상위 모달
        
        if self.current_context:
            return self.current_context
        
        # 현재 포커스 위젯의 컨텍스트 찾기
        current_widget = self.app.focusWidget()
        if current_widget:
            return self._find_widget_context(current_widget)
        
        # 기본값: 첫 번째 루트 컨텍스트
        if self.root_contexts:
            return self.root_contexts[0]
        
        return None
    
    def _handle_global_shortcut(self, action: NavigationAction):
        """전역 단축키 처리"""
        try:
            if action == NavigationAction.SHOW_HELP:
                self._show_help()
            elif action == NavigationAction.SHOW_SHORTCUTS:
                self._show_shortcuts_help()
            elif action == NavigationAction.TOGGLE_HIGH_CONTRAST:
                self._toggle_high_contrast()
            elif action == NavigationAction.INCREASE_FONT_SIZE:
                self._change_font_size(0.1)
            elif action == NavigationAction.DECREASE_FONT_SIZE:
                self._change_font_size(-0.1)
            
            self.shortcut_activated.emit(action.value, "global")
            
        except Exception as e:
            logger.error(f"Failed to handle global shortcut {action.value}: {e}")
    
    def _show_help(self):
        """도움말 표시"""
        try:
            current_widget = self.app.focusWidget()
            if current_widget:
                help_text = (current_widget.toolTip() or 
                           current_widget.whatsThis() or 
                           "이 요소에 대한 도움말이 없습니다.")
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    current_widget.window(),
                    "도움말",
                    help_text
                )
        except Exception as e:
            logger.error(f"Failed to show help: {e}")
    
    def _show_shortcuts_help(self):
        """단축키 도움말 표시"""
        try:
            shortcuts_text = "키보드 단축키:\n\n"
            
            # 현재 컨텍스트의 단축키들 표시
            context = self._get_current_context()
            if context:
                for shortcut in context.shortcuts.values():
                    if shortcut.enabled:
                        shortcuts_text += f"{shortcut.key_sequence}: {shortcut.description}\n"
            
            # 전역 단축키들 표시
            shortcuts_text += "\n전역 단축키:\n"
            global_shortcuts = [
                (NavigationAction.SHOW_HELP, "도움말 표시"),
                (NavigationAction.SHOW_SHORTCUTS, "단축키 목록 표시"),
                (NavigationAction.TOGGLE_HIGH_CONTRAST, "고대비 모드 토글"),
                (NavigationAction.INCREASE_FONT_SIZE, "글자 크기 증가"),
                (NavigationAction.DECREASE_FONT_SIZE, "글자 크기 감소"),
            ]
            
            for action, description in global_shortcuts:
                key = self.get_key_sequence(action)
                if key:
                    shortcuts_text += f"{key}: {description}\n"
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "키보드 단축키",
                shortcuts_text
            )
            
        except Exception as e:
            logger.error(f"Failed to show shortcuts help: {e}")
    
    def _toggle_high_contrast(self):
        """고대비 모드 토글"""
        try:
            from .accessibility_manager import get_accessibility_manager
            from .accessibility_manager import AccessibilityFeature
            
            accessibility_manager = get_accessibility_manager()
            if accessibility_manager:
                if AccessibilityFeature.HIGH_CONTRAST in accessibility_manager.accessibility_settings.enabled_features:
                    accessibility_manager.disable_feature(AccessibilityFeature.HIGH_CONTRAST)
                    message = "고대비 모드 비활성화"
                else:
                    accessibility_manager.enable_feature(AccessibilityFeature.HIGH_CONTRAST)
                    message = "고대비 모드 활성화"
                
                accessibility_manager.announce_message(message, "assertive")
        
        except Exception as e:
            logger.error(f"Failed to toggle high contrast: {e}")
    
    def _change_font_size(self, delta: float):
        """폰트 크기 변경"""
        try:
            from .accessibility_manager import get_accessibility_manager
            
            accessibility_manager = get_accessibility_manager()
            if accessibility_manager:
                current_scale = accessibility_manager.accessibility_settings.font_scale
                new_scale = max(1.0, min(2.0, current_scale + delta))
                
                if accessibility_manager.set_font_scale(new_scale):
                    message = f"폰트 크기: {new_scale:.0%}"
                    accessibility_manager.announce_message(message, "assertive")
        
        except Exception as e:
            logger.error(f"Failed to change font size: {e}")
    
    def _on_focus_changed(self, old_widget: QWidget, new_widget: QWidget):
        """포커스 변경 이벤트 처리"""
        try:
            if new_widget:
                self.focus_tracker.add_focus(new_widget)
                
                # 컨텍스트 업데이트
                context = self._find_widget_context(new_widget)
                if context and context != self.current_context:
                    self.current_context = context
            
            self.focus_changed.emit(old_widget, new_widget)
            
        except Exception as e:
            logger.error(f"Error handling focus change: {e}")
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """애플리케이션 이벤트 필터"""
        try:
            if not self.is_enabled:
                return False
            
            if event.type() == QEvent.Type.KeyPress:
                return self._handle_key_press_event(obj, event)
            
            return False
            
        except Exception as e:
            logger.error(f"Error in event filter: {e}")
            return False
    
    def _handle_key_press_event(self, obj: QObject, event: QKeyEvent) -> bool:
        """키 이벤트 처리"""
        try:
            key = event.key()
            modifiers = event.modifiers()
            
            # 네비게이션 모드 토글 (Alt 키)
            if key == Qt.Key.Key_Alt and not modifiers:
                self.is_navigation_mode = not self.is_navigation_mode
                self.navigation_mode_changed.emit(self.is_navigation_mode)
                return True
            
            # 특수 네비게이션 키들 처리
            if self._handle_navigation_keys(key, modifiers):
                return True
            
            # 위젯별 특별 처리
            if isinstance(obj, QWidget):
                return self._handle_widget_specific_navigation(obj, event)
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling key press event: {e}")
            return False
    
    def _handle_navigation_keys(self, key: int, modifiers: Qt.KeyboardModifier) -> bool:
        """네비게이션 키 처리"""
        try:
            # Tab 키 처리
            if key == Qt.Key.Key_Tab:
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    return self.navigate_to_prev_widget()
                else:
                    return self.navigate_to_next_widget()
            
            # F6 키 처리 (패널 간 이동)
            elif key == Qt.Key.Key_F6:
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    return self._navigate_to_next_panel()
                else:
                    return self._navigate_to_next_area()
            
            # 홈/엔드 키 처리
            elif key == Qt.Key.Key_Home:
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    return self._focus_first_widget()
            elif key == Qt.Key.Key_End:
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    return self._focus_last_widget()
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling navigation keys: {e}")
            return False
    
    def _navigate_to_next_panel(self) -> bool:
        """다음 패널로 이동"""
        try:
            # 탭 위젯이나 스택 위젯 찾기
            current_widget = self.app.focusWidget()
            if current_widget:
                parent = current_widget.parent()
                while parent:
                    if isinstance(parent, (QTabWidget, QStackedWidget)):
                        if isinstance(parent, QTabWidget):
                            current_index = parent.currentIndex()
                            next_index = (current_index + 1) % parent.count()
                            parent.setCurrentIndex(next_index)
                            # 새 탭의 첫 번째 위젯에 포커스
                            self._focus_first_widget_in_container(parent.currentWidget())
                            return True
                    parent = parent.parent()
            
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to next panel: {e}")
            return False
    
    def _navigate_to_next_area(self) -> bool:
        """다음 영역으로 이동 (F6)"""
        try:
            # 메인 영역들 간 이동 (예: 툴바 → 메뉴 → 콘텐츠 → 상태바)
            return self._focus_first_widget()
        except Exception as e:
            logger.error(f"Error navigating to next area: {e}")
            return False
    
    def _focus_first_widget_in_container(self, container: QWidget):
        """컨테이너 내 첫 번째 위젯에 포커스"""
        try:
            focusable_widgets = []
            self._find_focusable_widgets(container, focusable_widgets)
            
            if focusable_widgets:
                focusable_widgets[0].setFocus()
                
        except Exception as e:
            logger.error(f"Error focusing first widget in container: {e}")
    
    def _handle_widget_specific_navigation(self, widget: QWidget, event: QKeyEvent) -> bool:
        """위젯별 특별 네비게이션 처리"""
        try:
            widget_type = type(widget)
            if widget_type in self.widget_handlers:
                return self.widget_handlers[widget_type](widget, event)
            
            return False
            
        except Exception as e:
            logger.error(f"Error in widget-specific navigation: {e}")
            return False
    
    def _handle_tree_navigation(self, tree: QTreeWidget, event: QKeyEvent) -> bool:
        """트리 위젯 네비게이션"""
        try:
            key = event.key()
            current_item = tree.currentItem()
            
            if key == Qt.Key.Key_Right and current_item:
                if not current_item.isExpanded():
                    current_item.setExpanded(True)
                    return True
                elif current_item.childCount() > 0:
                    tree.setCurrentItem(current_item.child(0))
                    return True
            
            elif key == Qt.Key.Key_Left and current_item:
                if current_item.isExpanded():
                    current_item.setExpanded(False)
                    return True
                elif current_item.parent():
                    tree.setCurrentItem(current_item.parent())
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in tree navigation: {e}")
            return False
    
    def _handle_list_navigation(self, list_widget: QListWidget, event: QKeyEvent) -> bool:
        """리스트 위젯 네비게이션"""
        try:
            key = event.key()
            modifiers = event.modifiers()
            
            if key == Qt.Key.Key_Space:
                current_item = list_widget.currentItem()
                if current_item:
                    # 스페이스로 선택 토글
                    current_item.setSelected(not current_item.isSelected())
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in list navigation: {e}")
            return False
    
    def _handle_table_navigation(self, table: QTableWidget, event: QKeyEvent) -> bool:
        """테이블 위젯 네비게이션"""
        try:
            # 기본 테이블 네비게이션은 Qt에서 잘 처리하므로 추가 기능만
            return False
            
        except Exception as e:
            logger.error(f"Error in table navigation: {e}")
            return False
    
    def _handle_tab_navigation(self, tab_widget: QTabWidget, event: QKeyEvent) -> bool:
        """탭 위젯 네비게이션"""
        try:
            key = event.key()
            modifiers = event.modifiers()
            
            if key == Qt.Key.Key_Tab and modifiers & Qt.KeyboardModifier.ControlModifier:
                current_index = tab_widget.currentIndex()
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    # Ctrl+Shift+Tab: 이전 탭
                    prev_index = (current_index - 1) % tab_widget.count()
                    tab_widget.setCurrentIndex(prev_index)
                else:
                    # Ctrl+Tab: 다음 탭
                    next_index = (current_index + 1) % tab_widget.count()
                    tab_widget.setCurrentIndex(next_index)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in tab navigation: {e}")
            return False
    
    def _handle_combo_navigation(self, combo: QComboBox, event: QKeyEvent) -> bool:
        """콤보박스 네비게이션"""
        try:
            key = event.key()
            
            if key == Qt.Key.Key_Space and not combo.view().isVisible():
                combo.showPopup()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in combo navigation: {e}")
            return False
    
    def _handle_text_navigation(self, text_edit: QTextEdit, event: QKeyEvent) -> bool:
        """텍스트 에디트 네비게이션"""
        try:
            # 텍스트 에디터 내에서는 기본 네비게이션 사용
            return False
            
        except Exception as e:
            logger.error(f"Error in text navigation: {e}")
            return False
    
    def _handle_line_edit_navigation(self, line_edit: QLineEdit, event: QKeyEvent) -> bool:
        """라인 에디트 네비게이션"""
        try:
            # 라인 에디터는 기본 동작 사용
            return False
            
        except Exception as e:
            logger.error(f"Error in line edit navigation: {e}")
            return False
    
    def get_all_shortcuts(self) -> Dict[str, Dict[str, str]]:
        """모든 단축키 반환 (설정 UI용)"""
        try:
            shortcuts = {}
            
            # 기본 단축키들
            shortcuts["default"] = {
                action.value: key for action, key in self.default_shortcuts.items()
            }
            
            # 사용자 정의 단축키들
            shortcuts["custom"] = {
                action.value: key for action, key in self.custom_shortcuts.items()
            }
            
            # 현재 활성 단축키들
            shortcuts["current"] = {}
            for action in NavigationAction:
                key = self.get_key_sequence(action)
                if key:
                    shortcuts["current"][action.value] = key
            
            return shortcuts
            
        except Exception as e:
            logger.error(f"Failed to get all shortcuts: {e}")
            return {}
    
    def is_shortcut_available(self, key_sequence: str) -> bool:
        """단축키가 사용 가능한지 확인"""
        try:
            current_shortcuts = [self.get_key_sequence(action) for action in NavigationAction]
            return key_sequence not in current_shortcuts
        except Exception as e:
            logger.error(f"Error checking shortcut availability: {e}")
            return False
    
    def enable_navigation(self):
        """키보드 네비게이션 활성화"""
        self.is_enabled = True
        logger.info("Keyboard navigation enabled")
    
    def disable_navigation(self):
        """키보드 네비게이션 비활성화"""
        self.is_enabled = False
        logger.info("Keyboard navigation disabled")
    
    def cleanup(self):
        """정리"""
        try:
            # 전역 단축키들 정리
            for shortcut in self.global_shortcuts.values():
                shortcut.deleteLater()
            self.global_shortcuts.clear()
            
            # 이벤트 필터 제거
            self.app.removeEventFilter(self)
            
            # 설정 저장
            self._save_custom_shortcuts()
            
            logger.info("Keyboard Navigation Manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# 전역 키보드 네비게이션 매니저
_keyboard_navigation_manager: Optional[KeyboardNavigationManager] = None


def init_keyboard_navigation_manager(app: QApplication) -> KeyboardNavigationManager:
    """전역 키보드 네비게이션 매니저 초기화"""
    global _keyboard_navigation_manager
    
    if _keyboard_navigation_manager is not None:
        logger.warning("Keyboard navigation manager already initialized")
        return _keyboard_navigation_manager
    
    _keyboard_navigation_manager = KeyboardNavigationManager(app)
    return _keyboard_navigation_manager


def get_keyboard_navigation_manager() -> Optional[KeyboardNavigationManager]:
    """전역 키보드 네비게이션 매니저 반환"""
    return _keyboard_navigation_manager


def cleanup_keyboard_navigation_manager():
    """전역 키보드 네비게이션 매니저 정리"""
    global _keyboard_navigation_manager
    
    if _keyboard_navigation_manager:
        _keyboard_navigation_manager.cleanup()
        _keyboard_navigation_manager = None
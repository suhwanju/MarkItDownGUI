"""
Tooltip and Help System Manager
Enhanced tooltips and contextual help for accessibility
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QScrollArea, QDialog, QMainWindow,
    QToolTip, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    QObject, pyqtSignal, QSettings, QTimer, Qt, QRect, QPoint, QSize,
    QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup
)
from PyQt6.QtGui import (
    QFont, QFontMetrics, QPalette, QColor, QPainter, QPaintEvent,
    QMouseEvent, QEnterEvent, QLeaveEvent, QKeyEvent, QCursor, QPixmap
)

from .logger import get_logger


logger = get_logger(__name__)


class TooltipType(Enum):
    """툴팁 유형"""
    SIMPLE = "simple"        # 간단한 텍스트
    DETAILED = "detailed"    # 상세 정보
    HELP = "help"           # 도움말
    WARNING = "warning"      # 경고
    ERROR = "error"         # 오류
    SUCCESS = "success"     # 성공


class HelpTopicType(Enum):
    """도움말 주제 유형"""
    WIDGET_HELP = "widget_help"           # 위젯별 도움말
    KEYBOARD_SHORTCUTS = "shortcuts"     # 키보드 단축키
    ACCESSIBILITY = "accessibility"      # 접근성 기능
    TROUBLESHOOTING = "troubleshooting"  # 문제 해결
    GETTING_STARTED = "getting_started"  # 시작하기
    FAQ = "faq"                          # 자주 묻는 질문


@dataclass
class TooltipContent:
    """툴팁 내용"""
    title: str = ""
    description: str = ""
    tooltip_type: TooltipType = TooltipType.SIMPLE
    keyboard_shortcuts: List[str] = field(default_factory=list)
    related_help: str = ""
    auto_hide_delay: int = 5000  # 밀리초
    show_delay: int = 500       # 밀리초
    hide_delay: int = 200       # 밀리초
    
    def get_formatted_text(self) -> str:
        """포맷된 텍스트 반환"""
        parts = []
        
        if self.title:
            parts.append(f"<b>{self.title}</b>")
        
        if self.description:
            parts.append(self.description)
        
        if self.keyboard_shortcuts:
            shortcuts_text = ", ".join(self.keyboard_shortcuts)
            parts.append(f"<i>단축키: {shortcuts_text}</i>")
        
        return "<br><br>".join(parts)


@dataclass
class HelpTopic:
    """도움말 주제"""
    topic_id: str
    title: str
    content: str
    topic_type: HelpTopicType
    keywords: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    last_updated: datetime = field(default_factory=datetime.now)


class EnhancedTooltip(QFrame):
    """향상된 툴팁 위젯"""
    
    # 시그널
    tooltip_shown = pyqtSignal(str)  # tooltip_text
    tooltip_hidden = pyqtSignal()
    help_requested = pyqtSignal(str)  # help_topic
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 기본 설정
        self.setWindowFlags(
            Qt.WindowType.ToolTip | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 스타일 설정
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        # 레이아웃
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(4)
        
        # 제목 라벨
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 1)
        self.title_label.setFont(title_font)
        self.layout.addWidget(self.title_label)
        
        # 설명 라벨
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.description_label)
        
        # 단축키 라벨
        self.shortcuts_label = QLabel()
        self.shortcuts_label.setWordWrap(True)
        shortcut_font = self.shortcuts_label.font()
        shortcut_font.setItalic(True)
        shortcut_font.setPointSize(shortcut_font.pointSize() - 1)
        self.shortcuts_label.setFont(shortcut_font)
        self.layout.addWidget(self.shortcuts_label)
        
        # 도움말 버튼
        self.help_button = QPushButton("자세히...")
        self.help_button.setMaximumHeight(24)
        self.help_button.clicked.connect(self._on_help_requested)
        self.help_button.hide()  # 기본적으로 숨김
        self.layout.addWidget(self.help_button)
        
        # 현재 내용
        self.current_content: Optional[TooltipContent] = None
        self.target_widget: Optional[QWidget] = None
        self.help_topic: str = ""
        
        # 애니메이션
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 그림자 효과
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        # 자동 숨기기 타이머
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_tooltip)
        
        # 초기에는 숨김
        self.hide()
    
    def show_tooltip(self, content: TooltipContent, position: QPoint, widget: QWidget = None):
        """툴팁 표시"""
        try:
            self.current_content = content
            self.target_widget = widget
            
            # 내용 설정
            self._update_content(content)
            
            # 크기 조정
            self.adjustSize()
            
            # 위치 조정 (화면 경계 고려)
            adjusted_pos = self._adjust_position(position)
            self.move(adjusted_pos)
            
            # 페이드 인 애니메이션
            self.setWindowOpacity(0.0)
            self.show()
            
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(0.95)
            self.fade_animation.start()
            
            # 자동 숨기기 설정
            if content.auto_hide_delay > 0:
                self.auto_hide_timer.start(content.auto_hide_delay)
            
            # 접근성 알림
            from .accessibility_manager import get_accessibility_manager
            accessibility_manager = get_accessibility_manager()
            if accessibility_manager:
                tooltip_text = content.get_formatted_text().replace("<br>", " ").replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
                accessibility_manager.announce_message(f"툴팁: {tooltip_text}", "polite")
            
            self.tooltip_shown.emit(content.get_formatted_text())
            logger.debug(f"Tooltip shown: {content.title}")
            
        except Exception as e:
            logger.error(f"Error showing tooltip: {e}")
    
    def hide_tooltip(self):
        """툴팁 숨기기"""
        try:
            self.auto_hide_timer.stop()
            
            # 페이드 아웃 애니메이션
            self.fade_animation.finished.connect(self._on_fade_out_finished)
            self.fade_animation.setStartValue(self.windowOpacity())
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.start()
            
            self.tooltip_hidden.emit()
            
        except Exception as e:
            logger.error(f"Error hiding tooltip: {e}")
    
    def _update_content(self, content: TooltipContent):
        """툴팁 내용 업데이트"""
        try:
            # 제목 설정
            if content.title:
                self.title_label.setText(content.title)
                self.title_label.show()
            else:
                self.title_label.hide()
            
            # 설명 설정
            if content.description:
                self.description_label.setText(content.description)
                self.description_label.show()
            else:
                self.description_label.hide()
            
            # 단축키 설정
            if content.keyboard_shortcuts:
                shortcuts_text = "단축키: " + ", ".join(content.keyboard_shortcuts)
                self.shortcuts_label.setText(shortcuts_text)
                self.shortcuts_label.show()
            else:
                self.shortcuts_label.hide()
            
            # 도움말 버튼 설정
            if content.related_help:
                self.help_topic = content.related_help
                self.help_button.show()
            else:
                self.help_button.hide()
            
            # 타입별 스타일 적용
            self._apply_type_style(content.tooltip_type)
            
        except Exception as e:
            logger.error(f"Error updating tooltip content: {e}")
    
    def _apply_type_style(self, tooltip_type: TooltipType):
        """툴팁 타입별 스타일 적용"""
        try:
            style_map = {
                TooltipType.SIMPLE: {
                    "background": "#FFFFCC",
                    "border": "#CCCCAA",
                    "text": "#000000"
                },
                TooltipType.DETAILED: {
                    "background": "#E6F3FF",
                    "border": "#4A90E2",
                    "text": "#000000"
                },
                TooltipType.HELP: {
                    "background": "#E8F5E8",
                    "border": "#4CAF50",
                    "text": "#000000"
                },
                TooltipType.WARNING: {
                    "background": "#FFF3CD",
                    "border": "#FF9800",
                    "text": "#856404"
                },
                TooltipType.ERROR: {
                    "background": "#F8D7DA",
                    "border": "#DC3545",
                    "text": "#721C24"
                },
                TooltipType.SUCCESS: {
                    "background": "#D1F2EB",
                    "border": "#28A745",
                    "text": "#155724"
                }
            }
            
            style = style_map.get(tooltip_type, style_map[TooltipType.SIMPLE])
            
            self.setStyleSheet(f"""
                EnhancedTooltip {{
                    background-color: {style["background"]};
                    border: 1px solid {style["border"]};
                    border-radius: 4px;
                    color: {style["text"]};
                }}
            """)
            
        except Exception as e:
            logger.error(f"Error applying tooltip style: {e}")
    
    def _adjust_position(self, position: QPoint) -> QPoint:
        """화면 경계를 고려한 위치 조정"""
        try:
            screen = QApplication.primaryScreen()
            screen_rect = screen.availableGeometry()
            
            tooltip_size = self.sizeHint()
            
            # 기본 위치 (마우스 아래쪽)
            x = position.x()
            y = position.y() + 20
            
            # 오른쪽 경계 확인
            if x + tooltip_size.width() > screen_rect.right():
                x = screen_rect.right() - tooltip_size.width()
            
            # 왼쪽 경계 확인
            if x < screen_rect.left():
                x = screen_rect.left()
            
            # 아래쪽 경계 확인
            if y + tooltip_size.height() > screen_rect.bottom():
                y = position.y() - tooltip_size.height() - 10  # 마우스 위쪽으로
            
            # 위쪽 경계 확인
            if y < screen_rect.top():
                y = screen_rect.top()
            
            return QPoint(x, y)
            
        except Exception as e:
            logger.error(f"Error adjusting tooltip position: {e}")
            return position
    
    def _on_fade_out_finished(self):
        """페이드 아웃 완료 시"""
        try:
            self.fade_animation.finished.disconnect()
            self.hide()
        except Exception as e:
            logger.debug(f"Error in fade out finished handler: {e}")
    
    def _on_help_requested(self):
        """도움말 요청 시"""
        try:
            if self.help_topic:
                self.help_requested.emit(self.help_topic)
                self.hide_tooltip()
        except Exception as e:
            logger.error(f"Error handling help request: {e}")
    
    def enterEvent(self, event: QEnterEvent):
        """마우스 진입 시"""
        try:
            self.auto_hide_timer.stop()  # 자동 숨기기 중단
            super().enterEvent(event)
        except Exception as e:
            logger.debug(f"Error in tooltip enter event: {e}")
    
    def leaveEvent(self, event: QLeaveEvent):
        """마우스 떠남 시"""
        try:
            if self.current_content and self.current_content.auto_hide_delay > 0:
                self.auto_hide_timer.start(1000)  # 1초 후 숨기기
            super().leaveEvent(event)
        except Exception as e:
            logger.debug(f"Error in tooltip leave event: {e}")


class HelpDialog(QDialog):
    """도움말 대화상자"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("도움말")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(False)
        self.resize(600, 400)
        
        # 접근성 속성 설정
        self.setAccessibleName("도움말 창")
        self.setAccessibleDescription("애플리케이션 사용법과 기능에 대한 도움말을 제공합니다")
        
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        try:
            layout = QVBoxLayout(self)
            
            # 제목
            self.title_label = QLabel()
            title_font = self.title_label.font()
            title_font.setPointSize(title_font.pointSize() + 2)
            title_font.setBold(True)
            self.title_label.setFont(title_font)
            self.title_label.setAccessibleName("도움말 제목")
            layout.addWidget(self.title_label)
            
            # 내용
            self.content_area = QTextEdit()
            self.content_area.setReadOnly(True)
            self.content_area.setAccessibleName("도움말 내용")
            self.content_area.setAccessibleDescription("선택된 주제에 대한 상세한 도움말 내용")
            layout.addWidget(self.content_area)
            
            # 버튼
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.close_button = QPushButton("닫기")
            self.close_button.setMinimumHeight(44)  # 접근성 터치 타겟 크기
            self.close_button.setAccessibleName("도움말 창 닫기")
            self.close_button.setAccessibleDescription("도움말 창을 닫습니다")
            self.close_button.clicked.connect(self.close)
            self.close_button.setAutoDefault(True)
            button_layout.addWidget(self.close_button)
            
            layout.addLayout(button_layout)
            
        except Exception as e:
            logger.error(f"Error initializing help dialog UI: {e}")
    
    def show_help(self, topic: HelpTopic):
        """도움말 표시"""
        try:
            self.title_label.setText(topic.title)
            self.content_area.setHtml(topic.content)
            
            # 접근성 알림
            from .accessibility_manager import get_accessibility_manager
            accessibility_manager = get_accessibility_manager()
            if accessibility_manager:
                accessibility_manager.announce_message(
                    f"도움말 창 열림: {topic.title}",
                    "assertive"
                )
            
            self.show()
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            logger.error(f"Error showing help topic: {e}")


class TooltipManager(QObject):
    """툴팁 및 도움말 시스템 관리자"""
    
    # 시그널
    tooltip_shown = pyqtSignal(str, str)  # widget_id, content
    help_opened = pyqtSignal(str)         # topic_id
    
    def __init__(self, accessibility_manager=None):
        super().__init__()
        
        self.accessibility_manager = accessibility_manager
        self.settings = QSettings()
        
        # 툴팁 관리
        self.enhanced_tooltip = None
        self.tooltip_contents: Dict[str, TooltipContent] = {}
        self.widget_tooltips: Dict[QWidget, str] = {}
        
        # 도움말 관리
        self.help_topics: Dict[str, HelpTopic] = {}
        self.help_dialog = None
        
        # 타이머
        self.show_timer = QTimer()
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._show_delayed_tooltip)
        
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._hide_tooltip)
        
        # 현재 상태
        self.current_widget: Optional[QWidget] = None
        self.is_tooltip_visible = False
        self.tooltip_enabled = True
        
        # 설정
        self.show_delay = 500       # 표시 지연시간
        self.hide_delay = 200       # 숨기기 지연시간
        self.auto_hide_delay = 5000 # 자동 숨기기 시간
        
        logger.info("Tooltip Manager initialized")
    
    def initialize(self) -> bool:
        """툴팁 매니저 초기화"""
        try:
            # 향상된 툴팁 위젯 생성
            self.enhanced_tooltip = EnhancedTooltip()
            self.enhanced_tooltip.tooltip_shown.connect(self._on_tooltip_shown)
            self.enhanced_tooltip.tooltip_hidden.connect(self._on_tooltip_hidden)
            self.enhanced_tooltip.help_requested.connect(self._on_help_requested)
            
            # 도움말 대화상자 생성
            self.help_dialog = HelpDialog()
            
            # 기본 도움말 주제들 로드
            self._load_default_help_topics()
            
            # 설정 로드
            self._load_settings()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize tooltip manager: {e}")
            return False
    
    def register_tooltip(self, widget: QWidget, content: Union[str, TooltipContent], 
                        tooltip_id: str = None) -> str:
        """위젯에 툴팁 등록"""
        try:
            if not tooltip_id:
                tooltip_id = f"tooltip_{id(widget)}"
            
            # 내용이 문자열이면 TooltipContent로 변환
            if isinstance(content, str):
                content = TooltipContent(description=content)
            
            self.tooltip_contents[tooltip_id] = content
            self.widget_tooltips[widget] = tooltip_id
            
            # 이벤트 필터 설치
            widget.installEventFilter(self)
            
            logger.debug(f"Tooltip registered: {tooltip_id}")
            return tooltip_id
            
        except Exception as e:
            logger.error(f"Failed to register tooltip: {e}")
            return ""
    
    def unregister_tooltip(self, widget: QWidget):
        """위젯의 툴팁 등록 해제"""
        try:
            if widget in self.widget_tooltips:
                tooltip_id = self.widget_tooltips[widget]
                del self.widget_tooltips[widget]
                
                if tooltip_id in self.tooltip_contents:
                    del self.tooltip_contents[tooltip_id]
                
                widget.removeEventFilter(self)
                logger.debug(f"Tooltip unregistered for widget")
                
        except Exception as e:
            logger.error(f"Failed to unregister tooltip: {e}")
    
    def register_help_topic(self, topic: HelpTopic):
        """도움말 주제 등록"""
        try:
            self.help_topics[topic.topic_id] = topic
            logger.debug(f"Help topic registered: {topic.topic_id}")
            
        except Exception as e:
            logger.error(f"Failed to register help topic: {e}")
    
    def show_help(self, topic_id: str):
        """도움말 표시"""
        try:
            if topic_id not in self.help_topics:
                logger.warning(f"Help topic not found: {topic_id}")
                return
            
            if not self.help_dialog:
                self.help_dialog = HelpDialog()
            
            topic = self.help_topics[topic_id]
            self.help_dialog.show_help(topic)
            self.help_opened.emit(topic_id)
            
        except Exception as e:
            logger.error(f"Failed to show help: {e}")
    
    def show_keyboard_shortcuts_help(self):
        """키보드 단축키 도움말 표시"""
        try:
            shortcuts_topic = HelpTopic(
                topic_id="keyboard_shortcuts",
                title="키보드 단축키",
                content=self._generate_shortcuts_help(),
                topic_type=HelpTopicType.KEYBOARD_SHORTCUTS,
                keywords=["단축키", "키보드", "navigation"]
            )
            
            self.register_help_topic(shortcuts_topic)
            self.show_help("keyboard_shortcuts")
            
        except Exception as e:
            logger.error(f"Failed to show keyboard shortcuts help: {e}")
    
    def _generate_shortcuts_help(self) -> str:
        """키보드 단축키 도움말 생성"""
        try:
            shortcuts_html = """
            <h3>기본 단축키</h3>
            <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>단축키</th><th>기능</th></tr>
            <tr><td>F1</td><td>도움말 표시</td></tr>
            <tr><td>Ctrl+F1</td><td>키보드 단축키 목록</td></tr>
            <tr><td>Ctrl+D</td><td>디렉토리 선택</td></tr>
            <tr><td>Ctrl+Q</td><td>애플리케이션 종료</td></tr>
            <tr><td>F3</td><td>선택된 파일 보기</td></tr>
            </table>
            
            <h3>선택 단축키</h3>
            <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>단축키</th><th>기능</th></tr>
            <tr><td>Ctrl+A</td><td>전체 선택</td></tr>
            <tr><td>Ctrl+Shift+A</td><td>전체 해제</td></tr>
            <tr><td>Space</td><td>선택/해제 토글</td></tr>
            </table>
            
            <h3>네비게이션</h3>
            <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>단축키</th><th>기능</th></tr>
            <tr><td>Tab</td><td>다음 요소로 이동</td></tr>
            <tr><td>Shift+Tab</td><td>이전 요소로 이동</td></tr>
            <tr><td>Ctrl+F6</td><td>다음 패널로 이동</td></tr>
            <tr><td>Enter</td><td>스킵 링크 활성화</td></tr>
            </table>
            
            <h3>접근성 기능</h3>
            <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>단축키</th><th>기능</th></tr>
            <tr><td>Ctrl+Alt+H</td><td>고대비 모드 토글</td></tr>
            <tr><td>Ctrl++</td><td>글자 크기 증가</td></tr>
            <tr><td>Ctrl+-</td><td>글자 크기 감소</td></tr>
            </table>
            """
            
            return shortcuts_html
            
        except Exception as e:
            logger.error(f"Error generating shortcuts help: {e}")
            return "<p>단축키 정보를 생성할 수 없습니다.</p>"
    
    def _load_default_help_topics(self):
        """기본 도움말 주제들 로드"""
        try:
            # 시작하기 도움말
            getting_started = HelpTopic(
                topic_id="getting_started",
                title="시작하기",
                content="""
                <h3>MarkItDown GUI Converter 사용법</h3>
                
                <h4>1. 디렉토리 선택</h4>
                <p>먼저 변환할 파일들이 있는 디렉토리를 선택하세요:</p>
                <ul>
                <li>'찾아보기...' 버튼을 클릭하거나 Ctrl+D를 누르세요</li>
                <li>최근 사용한 디렉토리 목록에서 선택할 수도 있습니다</li>
                <li>'하위 디렉토리 포함' 옵션을 체크하면 하위 폴더의 파일들도 포함됩니다</li>
                </ul>
                
                <h4>2. 파일 검색</h4>
                <p>'파일 스캔' 버튼을 클릭하여 변환 가능한 파일들을 찾으세요.</p>
                <p>지원하는 파일 형식: docx, pptx, xlsx, pdf, jpg, png, txt, html 등</p>
                
                <h4>3. 파일 선택</h4>
                <p>파일 목록에서 변환할 파일들을 선택하세요:</p>
                <ul>
                <li>체크박스를 클릭하여 개별 파일 선택</li>
                <li>Ctrl+A로 전체 선택, Ctrl+Shift+A로 전체 해제</li>
                <li>스페이스키로 선택/해제 토글</li>
                </ul>
                
                <h4>4. 변환 실행</h4>
                <p>'선택된 파일 변환' 버튼을 클릭하여 마크다운으로 변환하세요.</p>
                
                <h4>5. 결과 확인</h4>
                <p>변환이 완료되면 '미리보기'로 결과를 확인하거나 '출력 폴더 열기'로 파일을 확인하세요.</p>
                """,
                topic_type=HelpTopicType.GETTING_STARTED,
                keywords=["시작", "사용법", "튜토리얼"],
                difficulty_level="beginner"
            )
            
            # 접근성 도움말
            accessibility_help = HelpTopic(
                topic_id="accessibility_features",
                title="접근성 기능",
                content="""
                <h3>접근성 기능</h3>
                
                <h4>키보드 네비게이션</h4>
                <p>모든 기능을 키보드만으로 사용할 수 있습니다:</p>
                <ul>
                <li>Tab키로 다음 요소로 이동</li>
                <li>Shift+Tab으로 이전 요소로 이동</li>
                <li>Enter 또는 Space로 버튼 클릭</li>
                <li>Ctrl+F6으로 패널 간 이동</li>
                </ul>
                
                <h4>스크린 리더 지원</h4>
                <p>NVDA, JAWS, VoiceOver 등의 스크린 리더를 지원합니다:</p>
                <ul>
                <li>모든 UI 요소에 적절한 라벨과 설명 제공</li>
                <li>상태 변경 시 자동 알림</li>
                <li>진행률과 로그 메시지 실시간 알림</li>
                </ul>
                
                <h4>시각적 접근성</h4>
                <p>시각 장애인을 위한 기능들:</p>
                <ul>
                <li>고대비 모드 (Ctrl+Alt+H)</li>
                <li>폰트 크기 조절 (Ctrl++, Ctrl+-)</li>
                <li>명확한 포커스 표시</li>
                <li>WCAG 2.1 AA 준수 색상 대비</li>
                </ul>
                
                <h4>운동 접근성</h4>
                <p>마우스 사용이 어려운 사용자를 위한 기능:</p>
                <ul>
                <li>44x44 픽셀 이상의 터치 타겟</li>
                <li>충분한 요소 간 간격</li>
                <li>드래그 없이 사용 가능</li>
                </ul>
                """,
                topic_type=HelpTopicType.ACCESSIBILITY,
                keywords=["접근성", "키보드", "스크린리더", "고대비"],
                difficulty_level="beginner"
            )
            
            # FAQ
            faq_help = HelpTopic(
                topic_id="faq",
                title="자주 묻는 질문",
                content="""
                <h3>자주 묻는 질문 (FAQ)</h3>
                
                <h4>Q: 어떤 파일 형식을 지원하나요?</h4>
                <p>A: Word 문서(docx), PowerPoint(pptx), Excel(xlsx), PDF, 이미지(jpg, png), 
                텍스트(txt), HTML 등 다양한 형식을 지원합니다.</p>
                
                <h4>Q: 변환된 파일은 어디에 저장되나요?</h4>
                <p>A: 기본적으로 프로그램 폴더의 'output' 디렉토리에 저장됩니다. 
                설정에서 출력 폴더를 변경할 수 있습니다.</p>
                
                <h4>Q: 한국어 파일도 변환할 수 있나요?</h4>
                <p>A: 네, 한국어를 포함한 다양한 언어의 문서를 변환할 수 있습니다.</p>
                
                <h4>Q: 변환에 실패한 파일은 어떻게 확인하나요?</h4>
                <p>A: 로그 창에서 변환 실패 원인을 확인할 수 있습니다. 
                파일이 손상되었거나 지원하지 않는 형식일 수 있습니다.</p>
                
                <h4>Q: 스크린 리더를 사용 중인데 프로그램이 읽히지 않습니다.</h4>
                <p>A: 스크린 리더가 실행 중인지 확인하고, 프로그램을 다시 시작해보세요. 
                NVDA, JAWS, VoiceOver를 지원합니다.</p>
                """,
                topic_type=HelpTopicType.FAQ,
                keywords=["질문", "답변", "FAQ", "도움", "문제해결"],
                difficulty_level="beginner"
            )
            
            # 주제들 등록
            for topic in [getting_started, accessibility_help, faq_help]:
                self.register_help_topic(topic)
            
        except Exception as e:
            logger.error(f"Error loading default help topics: {e}")
    
    def eventFilter(self, obj: QObject, event) -> bool:
        """이벤트 필터"""
        try:
            if not self.tooltip_enabled:
                return False
            
            widget = obj
            if not isinstance(widget, QWidget) or widget not in self.widget_tooltips:
                return False
            
            if event.type() == event.Type.Enter:
                self._on_widget_enter(widget)
            elif event.type() == event.Type.Leave:
                self._on_widget_leave(widget)
            elif event.type() == event.Type.MouseMove:
                # 마우스 이동 시 툴팁 위치 업데이트할 수 있음
                pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Error in tooltip event filter: {e}")
            return False
    
    def _on_widget_enter(self, widget: QWidget):
        """위젯 마우스 진입"""
        try:
            self.current_widget = widget
            self.hide_timer.stop()
            
            if widget in self.widget_tooltips:
                tooltip_id = self.widget_tooltips[widget]
                if tooltip_id in self.tooltip_contents:
                    content = self.tooltip_contents[tooltip_id]
                    self.show_timer.start(content.show_delay)
                    
        except Exception as e:
            logger.debug(f"Error handling widget enter: {e}")
    
    def _on_widget_leave(self, widget: QWidget):
        """위젯 마우스 떠남"""
        try:
            if self.current_widget == widget:
                self.current_widget = None
                self.show_timer.stop()
                
                if self.is_tooltip_visible:
                    content = None
                    if widget in self.widget_tooltips:
                        tooltip_id = self.widget_tooltips[widget]
                        content = self.tooltip_contents.get(tooltip_id)
                    
                    delay = content.hide_delay if content else self.hide_delay
                    self.hide_timer.start(delay)
                    
        except Exception as e:
            logger.debug(f"Error handling widget leave: {e}")
    
    def _show_delayed_tooltip(self):
        """지연된 툴팁 표시"""
        try:
            if not self.current_widget or self.current_widget not in self.widget_tooltips:
                return
            
            tooltip_id = self.widget_tooltips[self.current_widget]
            content = self.tooltip_contents.get(tooltip_id)
            
            if content and self.enhanced_tooltip:
                # 마우스 위치 가져오기
                cursor_pos = QCursor.pos()
                
                self.enhanced_tooltip.show_tooltip(content, cursor_pos, self.current_widget)
                self.is_tooltip_visible = True
                
        except Exception as e:
            logger.error(f"Error showing delayed tooltip: {e}")
    
    def _hide_tooltip(self):
        """툴팁 숨기기"""
        try:
            if self.enhanced_tooltip and self.is_tooltip_visible:
                self.enhanced_tooltip.hide_tooltip()
                self.is_tooltip_visible = False
                
        except Exception as e:
            logger.error(f"Error hiding tooltip: {e}")
    
    def _on_tooltip_shown(self, content: str):
        """툴팁 표시 시"""
        try:
            widget_id = ""
            if self.current_widget and self.current_widget in self.widget_tooltips:
                widget_id = self.widget_tooltips[self.current_widget]
            
            self.tooltip_shown.emit(widget_id, content)
            
        except Exception as e:
            logger.debug(f"Error handling tooltip shown signal: {e}")
    
    def _on_tooltip_hidden(self):
        """툴팁 숨김 시"""
        try:
            self.is_tooltip_visible = False
        except Exception as e:
            logger.debug(f"Error handling tooltip hidden signal: {e}")
    
    def _on_help_requested(self, topic_id: str):
        """도움말 요청 시"""
        try:
            self.show_help(topic_id)
        except Exception as e:
            logger.error(f"Error handling help request: {e}")
    
    def set_tooltip_enabled(self, enabled: bool):
        """툴팁 활성화/비활성화"""
        try:
            self.tooltip_enabled = enabled
            if not enabled and self.is_tooltip_visible:
                self._hide_tooltip()
                
            logger.debug(f"Tooltips {'enabled' if enabled else 'disabled'}")
            
        except Exception as e:
            logger.error(f"Error setting tooltip enabled state: {e}")
    
    def _load_settings(self):
        """설정 로드"""
        try:
            self.tooltip_enabled = self.settings.value("tooltips/enabled", True, type=bool)
            self.show_delay = self.settings.value("tooltips/show_delay", 500, type=int)
            self.hide_delay = self.settings.value("tooltips/hide_delay", 200, type=int)
            self.auto_hide_delay = self.settings.value("tooltips/auto_hide_delay", 5000, type=int)
            
        except Exception as e:
            logger.error(f"Error loading tooltip settings: {e}")
    
    def save_settings(self):
        """설정 저장"""
        try:
            self.settings.setValue("tooltips/enabled", self.tooltip_enabled)
            self.settings.setValue("tooltips/show_delay", self.show_delay)
            self.settings.setValue("tooltips/hide_delay", self.hide_delay)
            self.settings.setValue("tooltips/auto_hide_delay", self.auto_hide_delay)
            self.settings.sync()
            
        except Exception as e:
            logger.error(f"Error saving tooltip settings: {e}")
    
    def cleanup(self):
        """정리"""
        try:
            # 타이머 정지
            self.show_timer.stop()
            self.hide_timer.stop()
            
            # 툴팁 숨기기
            if self.enhanced_tooltip:
                self.enhanced_tooltip.hide_tooltip()
                self.enhanced_tooltip.deleteLater()
            
            # 도움말 대화상자 닫기
            if self.help_dialog:
                self.help_dialog.close()
                self.help_dialog.deleteLater()
            
            # 이벤트 필터 제거
            for widget in list(self.widget_tooltips.keys()):
                widget.removeEventFilter(self)
            
            # 설정 저장
            self.save_settings()
            
            logger.info("Tooltip manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error during tooltip manager cleanup: {e}")
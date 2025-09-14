"""
검색 위젯
텍스트 검색 기능을 제공하는 위젯
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QCheckBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QAction

from ...core.logger import get_logger


logger = get_logger(__name__)


class SearchWidget(QWidget):
    """검색 위젯"""
    
    # 시그널
    search_requested = pyqtSignal(str, bool, bool)  # text, case_sensitive, whole_words
    close_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._setup_connections()
        
        # 자동 숨김 타이머
        self._not_found_timer = QTimer()
        self._not_found_timer.setSingleShot(True)
        self._not_found_timer.timeout.connect(self._reset_not_found_style)
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 검색 입력
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어 입력...")
        self.search_input.setMinimumWidth(200)
        layout.addWidget(self.search_input)
        
        # 이전/다음 버튼
        self.prev_btn = QPushButton("이전")
        self.prev_btn.setMaximumWidth(50)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("다음")
        self.next_btn.setMaximumWidth(50)
        layout.addWidget(self.next_btn)
        
        # 옵션 체크박스들
        self.case_sensitive_check = QCheckBox("대/소문자 구분")
        layout.addWidget(self.case_sensitive_check)
        
        self.whole_words_check = QCheckBox("단어 단위")
        layout.addWidget(self.whole_words_check)
        
        # 결과 표시
        self.result_label = QLabel()
        layout.addWidget(self.result_label)
        
        layout.addStretch()
        
        # 닫기 버튼
        self.close_btn = QPushButton("×")
        self.close_btn.setMaximumWidth(30)
        self.close_btn.setToolTip("검색 닫기 (Esc)")
        layout.addWidget(self.close_btn)
        
        # 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #ccc;
                padding: 4px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._search_next)
        
        self.prev_btn.clicked.connect(self._search_prev)
        self.next_btn.clicked.connect(self._search_next)
        self.close_btn.clicked.connect(self.close_requested.emit)
        
        self.case_sensitive_check.toggled.connect(self._on_option_changed)
        self.whole_words_check.toggled.connect(self._on_option_changed)
        
        # Esc 키로 검색 닫기
        escape_action = QAction(self)
        escape_action.setShortcut(QKeySequence("Escape"))
        escape_action.triggered.connect(self.close_requested.emit)
        self.addAction(escape_action)
    
    def focus_search_input(self):
        """검색 입력 필드에 포커스"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def show_not_found(self):
        """검색 결과 없음 표시"""
        self.result_label.setText("검색 결과 없음")
        self.result_label.setStyleSheet("color: red;")
        
        # 검색 입력 필드 강조
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ff6b6b;
                border-radius: 4px;
                padding: 4px;
                background-color: #ffe0e0;
            }
        """)
        
        # 3초 후 스타일 리셋
        self._not_found_timer.start(3000)
    
    def clear_not_found(self):
        """검색 결과 없음 상태 클리어"""
        self.result_label.clear()
        self._reset_not_found_style()
    
    def _reset_not_found_style(self):
        """검색 입력 필드 스타일 리셋"""
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
        """)
        self.result_label.setStyleSheet("")
    
    def _on_search_text_changed(self, text: str):
        """검색 텍스트 변경시"""
        if text:
            self.clear_not_found()
            self._perform_search()
        else:
            self.result_label.clear()
    
    def _on_option_changed(self):
        """검색 옵션 변경시"""
        if self.search_input.text():
            self._perform_search()
    
    def _search_prev(self):
        """이전 검색 결과로"""
        # TODO: 이전 검색 구현
        self._perform_search()
    
    def _search_next(self):
        """다음 검색 결과로"""
        self._perform_search()
    
    def _perform_search(self):
        """검색 수행"""
        text = self.search_input.text().strip()
        if not text:
            return
        
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_words = self.whole_words_check.isChecked()
        
        self.search_requested.emit(text, case_sensitive, whole_words)
    
    def set_search_text(self, text: str):
        """검색 텍스트 설정"""
        self.search_input.setText(text)
    
    def get_search_text(self) -> str:
        """현재 검색 텍스트 반환"""
        return self.search_input.text().strip()
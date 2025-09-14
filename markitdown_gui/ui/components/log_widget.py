"""
로그 위젯
애플리케이션 로그를 표시하는 위젯
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QGroupBox, QCheckBox, QComboBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor

import logging
from datetime import datetime
from typing import Optional

from ...core.logger import get_logger


logger = get_logger(__name__)


class LogWidget(QWidget):
    """로그 표시 위젯"""
    
    def __init__(self):
        super().__init__()
        self._max_lines = 1000
        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """UI 초기화"""
        # 그룹박스로 감싸기
        self.group_box = QGroupBox("변환 로그")
        layout = QVBoxLayout(self)
        layout.addWidget(self.group_box)
        
        group_layout = QVBoxLayout(self.group_box)
        
        # 상단 컨트롤
        control_layout = QHBoxLayout()
        
        # 로그 레벨 필터
        level_label = QLabel("레벨:")
        control_layout.addWidget(level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["전체", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentText("INFO")
        self.level_combo.setMaximumWidth(100)
        control_layout.addWidget(self.level_combo)
        
        control_layout.addStretch()
        
        # 자동 스크롤 체크박스
        self.auto_scroll_check = QCheckBox("자동 스크롤")
        self.auto_scroll_check.setChecked(True)
        control_layout.addWidget(self.auto_scroll_check)
        
        # 로그 지우기 버튼
        self.clear_btn = QPushButton("지우기")
        self.clear_btn.setMaximumWidth(60)
        control_layout.addWidget(self.clear_btn)
        
        # 로그 저장 버튼
        self.save_btn = QPushButton("저장")
        self.save_btn.setMaximumWidth(60)
        control_layout.addWidget(self.save_btn)
        
        group_layout.addLayout(control_layout)
        
        # 텍스트 에디트
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumHeight(200)
        
        # 폰트 설정 (모노스페이스)
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.text_edit.setFont(font)
        
        group_layout.addWidget(self.text_edit)
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.clear_btn.clicked.connect(self.clear_log)
        self.save_btn.clicked.connect(self.save_log)
        self.level_combo.currentTextChanged.connect(self._on_level_filter_changed)
    
    def append_log(self, message: str, level: str = "INFO"):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"
        
        # 레벨 필터링
        current_filter = self.level_combo.currentText()
        if current_filter != "전체":
            level_priority = {
                "DEBUG": 10,
                "INFO": 20,
                "WARNING": 30,
                "ERROR": 40,
                "CRITICAL": 50
            }
            
            if level_priority.get(level, 0) < level_priority.get(current_filter, 0):
                return
        
        # 색상 설정
        color = self._get_level_color(level)
        
        # 텍스트 추가
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # 색상 적용
        if color:
            cursor.insertHtml(f'<span style="color: {color};">{formatted_message}</span><br>')
        else:
            cursor.insertText(formatted_message + "\n")
        
        # 최대 라인 수 제한
        self._limit_lines()
        
        # 자동 스크롤
        if self.auto_scroll_check.isChecked():
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
    
    def _get_level_color(self, level: str) -> Optional[str]:
        """로그 레벨에 따른 색상 반환"""
        colors = {
            "DEBUG": "#808080",     # 회색
            "INFO": "#000000",      # 검은색
            "WARNING": "#FF8C00",   # 오렌지
            "ERROR": "#DC143C",     # 빨간색
            "CRITICAL": "#8B0000"   # 진한 빨간색
        }
        return colors.get(level)
    
    def _limit_lines(self):
        """최대 라인 수 제한"""
        document = self.text_edit.document()
        if document.blockCount() > self._max_lines:
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, 
                              QTextCursor.MoveMode.KeepAnchor, 
                              document.blockCount() - self._max_lines)
            cursor.removeSelectedText()
    
    def clear_log(self):
        """로그 지우기"""
        self.text_edit.clear()
        logger.info("로그가 지워졌습니다")
    
    def save_log(self):
        """로그 저장"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "로그 저장",
            f"markitdown_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "텍스트 파일 (*.txt);;모든 파일 (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                logger.info(f"로그가 저장되었습니다: {filename}")
            except Exception as e:
                logger.error(f"로그 저장 실패: {e}")
    
    def _on_level_filter_changed(self, level: str):
        """로그 레벨 필터 변경시"""
        # 현재는 새로운 로그만 필터링
        # 필요시 기존 로그도 다시 필터링하도록 구현
        logger.debug(f"로그 레벨 필터 변경: {level}")
    
    def set_max_lines(self, max_lines: int):
        """최대 라인 수 설정"""
        self._max_lines = max_lines
    
    def get_log_text(self) -> str:
        """현재 로그 텍스트 반환"""
        return self.text_edit.toPlainText()
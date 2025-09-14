#!/usr/bin/env python3
"""
Theme System Test Script
테스트용 간단한 스크립트로 테마 시스템 작동 확인
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import Qt

from markitdown_gui.core.theme_manager import init_theme_manager, ThemeType
from markitdown_gui.core.logger import get_logger

logger = get_logger(__name__)


class TestWindow(QMainWindow):
    """테스트용 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme System Test")
        self.setGeometry(100, 100, 600, 400)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 제목
        title = QLabel("MarkItDown GUI - Theme System Test")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 테마 선택 콤보박스
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("시스템 기본", ThemeType.FOLLOW_SYSTEM.value)
        self.theme_combo.addItem("라이트 테마", ThemeType.LIGHT.value)
        self.theme_combo.addItem("다크 테마", ThemeType.DARK.value)
        self.theme_combo.addItem("고대비 테마", ThemeType.HIGH_CONTRAST.value)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # 테스트 버튼들
        test_button1 = QPushButton("테스트 버튼 1")
        test_button1.clicked.connect(lambda: print("Button 1 clicked"))
        layout.addWidget(test_button1)
        
        test_button2 = QPushButton("테스트 버튼 2")
        test_button2.setProperty("class", "secondary")
        test_button2.clicked.connect(lambda: print("Button 2 clicked"))
        layout.addWidget(test_button2)
        
        # 상태 표시 라벨
        self.status_label = QLabel("테마 시스템이 초기화되었습니다.")
        layout.addWidget(self.status_label)
        
        # 애니메이션 토글 버튼
        self.animation_button = QPushButton("애니메이션 끄기")
        self.animation_button.clicked.connect(self.toggle_animation)
        layout.addWidget(self.animation_button)
        
        layout.addStretch()
    
    def on_theme_changed(self, theme_text: str):
        """테마 변경 핸들러"""
        try:
            theme_value = self.theme_combo.currentData()
            if theme_value:
                theme_type = ThemeType(theme_value)
                theme_manager = self.theme_manager
                
                if theme_manager:
                    success = theme_manager.set_theme(theme_type)
                    if success:
                        self.status_label.setText(f"테마 변경됨: {theme_text}")
                        logger.info(f"Theme changed to: {theme_value}")
                    else:
                        self.status_label.setText("테마 변경 실패")
                        logger.error(f"Failed to change theme to: {theme_value}")
                else:
                    self.status_label.setText("테마 매니저를 찾을 수 없음")
        except Exception as e:
            self.status_label.setText(f"오류: {e}")
            logger.error(f"Error changing theme: {e}")
    
    def toggle_animation(self):
        """애니메이션 토글"""
        if self.theme_manager:
            current = self.theme_manager.is_transition_enabled()
            self.theme_manager.set_transition_enabled(not current)
            self.animation_button.setText("애니메이션 켜기" if current else "애니메이션 끄기")
            self.status_label.setText(f"애니메이션 {'비활성화' if current else '활성화'}됨")
    
    def set_theme_manager(self, theme_manager):
        """테마 매니저 설정"""
        self.theme_manager = theme_manager


def main():
    """메인 함수"""
    try:
        # QApplication 생성
        app = QApplication(sys.argv)
        app.setApplicationName("MarkItDown Theme Test")
        
        # 테마 매니저 초기화
        theme_manager = init_theme_manager(app)
        
        # 테스트 윈도우 생성
        window = TestWindow()
        window.set_theme_manager(theme_manager)
        window.show()
        
        logger.info("Theme test application started")
        
        # 이벤트 루프 실행
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Error starting theme test application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
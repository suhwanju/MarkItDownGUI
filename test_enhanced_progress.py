#!/usr/bin/env python3
"""
테스트: 향상된 진행률 위젯
Enhanced progress widget test
"""

import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal

# 프로젝트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from markitdown_gui.ui.components.progress_widget import ProgressWidget
from markitdown_gui.core.models import (
    ConversionProgress, ConversionProgressStatus, FileInfo, 
    FileType, ConversionStatus, FileConflictStatus
)


class TestWindow(QMainWindow):
    """테스트 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Progress Widget Test")
        self.setGeometry(100, 100, 900, 700)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 테스트 버튼들
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Progress")
        self.update_btn = QPushButton("Update Progress")
        self.finish_btn = QPushButton("Finish Progress")
        self.cancel_btn = QPushButton("Cancel Progress")
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.finish_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # 진행률 위젯
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # 연결
        self.start_btn.clicked.connect(self.start_test)
        self.update_btn.clicked.connect(self.update_test)
        self.finish_btn.clicked.connect(self.finish_test)
        self.cancel_btn.clicked.connect(self.cancel_test)
        
        # 진행률 위젯 시그널 연결
        self.progress_widget.cancel_requested.connect(self.on_cancel_requested)
        self.progress_widget.settings_requested.connect(self.on_settings_requested)
        
        # 테스트 데이터
        self.test_files = [
            FileInfo(
                path=Path("test1.docx"),
                name="test1.docx", 
                size=1024*50,
                modified_time=datetime.now(),
                file_type=FileType.DOCX,
                is_selected=True
            ),
            FileInfo(
                path=Path("test2.pdf"),
                name="test2.pdf",
                size=1024*100,
                modified_time=datetime.now(),
                file_type=FileType.PDF,
                is_selected=True,
                conflict_status=FileConflictStatus.EXISTS
            ),
            FileInfo(
                path=Path("test3.png"),
                name="test3.png",
                size=1024*30,
                modified_time=datetime.now(),
                file_type=FileType.PNG,
                is_selected=True
            )
        ]
        
        self.current_progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_update)
    
    def start_test(self):
        """테스트 시작"""
        print("Starting progress test...")
        self.current_progress = 0
        self.progress_widget.start_progress(len(self.test_files), self.test_files)
        self.timer.start(1000)  # 1초마다 업데이트
    
    def auto_update(self):
        """자동 업데이트"""
        if self.current_progress < len(self.test_files):
            self.update_test()
            self.current_progress += 0.5
        else:
            self.timer.stop()
            self.finish_test()
    
    def update_test(self):
        """진행률 업데이트 테스트"""
        progress = ConversionProgress(
            total_files=len(self.test_files),
            completed_files=int(self.current_progress),
            current_file=self.test_files[min(int(self.current_progress), len(self.test_files)-1)].name,
            current_status="파일 변환 중...",
            current_progress_status=ConversionProgressStatus.PROCESSING,
            current_file_progress=self.current_progress % 1.0,
            conflicts_detected=1,
            conflicts_resolved=0,
            files_skipped=0,
            files_overwritten=0,
            files_renamed=1,
            start_time=datetime.now(),
            estimated_time_remaining=30.0
        )
        
        self.progress_widget.update_progress(progress)
        
        # 파일별 진행률 업데이트
        for i, file_info in enumerate(self.test_files):
            if i <= int(self.current_progress):
                if i < int(self.current_progress):
                    file_info.conversion_status = ConversionStatus.SUCCESS
                    file_info.progress_status = ConversionProgressStatus.COMPLETED
                else:
                    file_info.conversion_status = ConversionStatus.IN_PROGRESS  
                    file_info.progress_status = ConversionProgressStatus.PROCESSING
                
                self.progress_widget.update_file_progress(file_info)
    
    def finish_test(self):
        """테스트 완료"""
        print("Finishing progress test...")
        self.timer.stop()
        self.progress_widget.finish_progress(success=True, message="테스트 완료!")
    
    def cancel_test(self):
        """테스트 취소"""
        print("Canceling progress test...")
        self.timer.stop()
        self.progress_widget.cancel_progress()
    
    def on_cancel_requested(self):
        """취소 요청 처리"""
        print("Cancel requested from progress widget")
    
    def on_settings_requested(self):
        """설정 요청 처리"""
        print("Settings requested from progress widget")


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # 애플리케이션 스타일 설정
    app.setStyle("Fusion")
    
    window = TestWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
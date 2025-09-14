"""
마크다운 미리보기 다이얼로그
변환된 마크다운 파일을 미리보기할 수 있는 다이얼로그
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QPushButton, QLabel, QComboBox, QSpinBox, QGroupBox,
    QMessageBox, QFileDialog, QSplitter, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QWidget
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QKeySequence, QAction
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

try:
    import markdown
    from markdown.extensions import codehilite, tables, toc
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

from ..core.models import FileInfo
from ..core.logger import get_logger


logger = get_logger(__name__)


class MarkdownTextEdit(QTextEdit):
    """검색 기능이 있는 마크다운 텍스트 에디터"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self._setup_font()
    
    def _setup_font(self):
        """폰트 설정"""
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.setFont(font)
    
    def find_text(self, text: str, case_sensitive: bool = False, whole_words: bool = False) -> bool:
        """텍스트 검색"""
        if not text:
            return False
        
        flags = QTextCursor.MoveOperation.NoMove
        if case_sensitive:
            flags |= QTextCursor.MoveOperation.NoMove  # Qt6에서는 다른 방식으로 처리
        
        return self.find(text)
    
    def set_font_size(self, size: int):
        """폰트 크기 설정"""
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)


class PreviewDialog(QDialog):
    """마크다운 미리보기 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file_path: Optional[Path] = None
        self.markdown_content = ""
        self.html_content = ""
        
        self._init_ui()
        self._setup_connections()
        self._load_settings()
        
        logger.info("미리보기 다이얼로그 초기화 완료")
    
    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("마크다운 미리보기")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # 상단 컨트롤
        top_layout = self._create_top_controls()
        layout.addLayout(top_layout)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Raw Markdown 탭
        self.raw_tab = self._create_raw_tab()
        self.tab_widget.addTab(self.raw_tab, "Raw Markdown")
        
        # Rendered HTML 탭
        if MARKDOWN_AVAILABLE:
            self.html_tab = self._create_html_tab()
            self.tab_widget.addTab(self.html_tab, "Rendered HTML")
        else:
            # markdown 라이브러리가 없을 때 안내
            self.html_tab = QLabel("HTML 미리보기를 위해 markdown 라이브러리가 필요합니다.\npip install markdown")
            self.html_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tab_widget.addTab(self.html_tab, "Rendered HTML (비활성)")
        
        # 하단 버튼
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)
    
    def _create_top_controls(self) -> QHBoxLayout:
        """상단 컨트롤 생성"""
        layout = QHBoxLayout()
        
        # 파일 정보
        self.file_info_label = QLabel("파일을 선택하세요.")
        layout.addWidget(self.file_info_label)
        
        layout.addStretch()
        
        # 폰트 크기 조절
        font_label = QLabel("폰트 크기:")
        layout.addWidget(font_label)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix("pt")
        layout.addWidget(self.font_size_spin)
        
        # 검색 버튼
        self.search_btn = QPushButton("검색 (Ctrl+F)")
        layout.addWidget(self.search_btn)
        
        return layout
    
    def _create_raw_tab(self) -> QWidget:
        """Raw Markdown 탭 생성"""
        from ..ui.components.search_widget import SearchWidget
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 검색 위젯 (처음에는 숨김)
        self.search_widget = SearchWidget()
        self.search_widget.setVisible(False)
        layout.addWidget(self.search_widget)
        
        # 텍스트 에디터
        self.raw_text_edit = MarkdownTextEdit()
        layout.addWidget(self.raw_text_edit)
        
        return widget
    
    def _create_html_tab(self) -> QWidget:
        """Rendered HTML 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # HTML 뷰어
        self.html_text_edit = QTextEdit()
        self.html_text_edit.setReadOnly(True)
        layout.addWidget(self.html_text_edit)
        
        return widget
    
    def _create_button_layout(self) -> QHBoxLayout:
        """하단 버튼 레이아웃 생성"""
        layout = QHBoxLayout()
        
        # 왼쪽 버튼들
        self.save_btn = QPushButton("다른 이름으로 저장")
        layout.addWidget(self.save_btn)
        
        self.print_btn = QPushButton("인쇄")
        layout.addWidget(self.print_btn)
        
        layout.addStretch()
        
        # 오른쪽 버튼들
        self.refresh_btn = QPushButton("새로 고침")
        layout.addWidget(self.refresh_btn)
        
        self.close_btn = QPushButton("닫기")
        layout.addWidget(self.close_btn)
        
        return layout
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        self.search_btn.clicked.connect(self._show_search)
        self.save_btn.clicked.connect(self._save_as)
        self.print_btn.clicked.connect(self._print)
        self.refresh_btn.clicked.connect(self._refresh_content)
        self.close_btn.clicked.connect(self.accept)
        
        # 검색 위젯 연결
        self.search_widget.search_requested.connect(self._search_text)
        self.search_widget.close_requested.connect(self._hide_search)
        
        # 키보드 단축키
        search_action = QAction(self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(self._show_search)
        self.addAction(search_action)
    
    def set_markdown_file(self, file_path: Path):
        """마크다운 파일 설정"""
        try:
            if not file_path.exists():
                QMessageBox.warning(self, "파일 오류", f"파일을 찾을 수 없습니다: {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.markdown_content = f.read()
            
            self.current_file_path = file_path
            self.file_info_label.setText(f"파일: {file_path.name}")
            
            # 내용 표시
            self._display_content()
            
            logger.info(f"미리보기 파일 설정: {file_path}")
            
        except Exception as e:
            logger.error(f"파일 읽기 실패: {e}")
            QMessageBox.critical(self, "파일 오류", f"파일을 읽을 수 없습니다:\n{str(e)}")
    
    def set_markdown_content(self, content: str, file_name: str = ""):
        """마크다운 내용 직접 설정"""
        self.markdown_content = content
        self.current_file_path = None
        self.file_info_label.setText(f"내용 미리보기: {file_name}")
        
        self._display_content()
    
    def _display_content(self):
        """내용 표시"""
        # Raw markdown 탭
        self.raw_text_edit.setPlainText(self.markdown_content)
        
        # HTML 탭 (markdown 라이브러리가 있을 때만)
        if MARKDOWN_AVAILABLE and hasattr(self, 'html_text_edit'):
            try:
                # 마크다운을 HTML로 변환
                md = markdown.Markdown(extensions=[
                    'codehilite',
                    'tables',
                    'toc',
                    'fenced_code'
                ])
                self.html_content = md.convert(self.markdown_content)
                self.html_text_edit.setHtml(self.html_content)
                
            except Exception as e:
                logger.error(f"HTML 변환 실패: {e}")
                self.html_text_edit.setPlainText(f"HTML 변환 실패: {str(e)}")
    
    def _on_font_size_changed(self, size: int):
        """폰트 크기 변경시"""
        self.raw_text_edit.set_font_size(size)
        if hasattr(self, 'html_text_edit'):
            font = self.html_text_edit.font()
            font.setPointSize(size)
            self.html_text_edit.setFont(font)
    
    def _show_search(self):
        """검색 위젯 표시"""
        self.search_widget.setVisible(True)
        self.search_widget.focus_search_input()
    
    def _hide_search(self):
        """검색 위젯 숨김"""
        self.search_widget.setVisible(False)
    
    def _search_text(self, text: str, case_sensitive: bool, whole_words: bool):
        """텍스트 검색"""
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.raw_tab:
            success = self.raw_text_edit.find_text(text, case_sensitive, whole_words)
            if not success and text:
                self.search_widget.show_not_found()
        elif hasattr(self, 'html_text_edit') and current_tab == self.html_tab:
            success = self.html_text_edit.find(text)
            if not success and text:
                self.search_widget.show_not_found()
    
    def _save_as(self):
        """다른 이름으로 저장"""
        if not self.markdown_content:
            QMessageBox.information(self, "정보", "저장할 내용이 없습니다.")
            return
        
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.raw_tab:
            # 마크다운으로 저장
            default_name = "preview.md"
            if self.current_file_path:
                default_name = f"preview_{self.current_file_path.stem}.md"
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "마크다운으로 저장",
                default_name,
                "Markdown 파일 (*.md);;텍스트 파일 (*.txt);;모든 파일 (*.*)"
            )
            
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(self.markdown_content)
                    QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{filename}")
                except Exception as e:
                    QMessageBox.critical(self, "저장 오류", f"저장 중 오류가 발생했습니다:\n{str(e)}")
        
        elif MARKDOWN_AVAILABLE and hasattr(self, 'html_text_edit') and current_tab == self.html_tab:
            # HTML로 저장
            default_name = "preview.html"
            if self.current_file_path:
                default_name = f"preview_{self.current_file_path.stem}.html"
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "HTML로 저장",
                default_name,
                "HTML 파일 (*.html);;모든 파일 (*.*)"
            )
            
            if filename:
                try:
                    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Markdown Preview</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 2px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{self.html_content}
</body>
</html>"""
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_template)
                    QMessageBox.information(self, "저장 완료", f"HTML 파일이 저장되었습니다:\n{filename}")
                except Exception as e:
                    QMessageBox.critical(self, "저장 오류", f"저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def _print(self):
        """인쇄"""
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            current_tab = self.tab_widget.currentWidget()
            
            if current_tab == self.raw_tab:
                self.raw_text_edit.print(printer)
            elif hasattr(self, 'html_text_edit') and current_tab == self.html_tab:
                self.html_text_edit.print(printer)
    
    def _refresh_content(self):
        """내용 새로 고침"""
        if self.current_file_path and self.current_file_path.exists():
            self.set_markdown_file(self.current_file_path)
        else:
            self._display_content()
    
    def _load_settings(self):
        """설정 로드"""
        settings = QSettings()
        
        # 윈도우 크기 및 위치
        geometry = settings.value("preview_dialog/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 폰트 크기
        font_size = settings.value("preview_dialog/font_size", 10, int)
        self.font_size_spin.setValue(font_size)
        self._on_font_size_changed(font_size)
    
    def _save_settings(self):
        """설정 저장"""
        settings = QSettings()
        settings.setValue("preview_dialog/geometry", self.saveGeometry())
        settings.setValue("preview_dialog/font_size", self.font_size_spin.value())
    
    def closeEvent(self, event):
        """닫기 이벤트"""
        self._save_settings()
        super().closeEvent(event)
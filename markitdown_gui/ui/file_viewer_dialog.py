"""
원본 파일 뷰어 다이얼로그
원본 파일을 미리보기할 수 있는 다이얼로그
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QTabWidget, QWidget, QMessageBox, QScrollArea,
    QSplitter, QTreeWidget, QTreeWidgetItem, QGroupBox,
    QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QTextCursor

try:
    from PIL import Image, ImageQt
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from ..core.models import FileInfo, FileType
from ..core.logger import get_logger


logger = get_logger(__name__)


class FileContentLoader(QThread):
    """파일 내용 로더 스레드"""
    
    content_loaded = pyqtSignal(str)
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path: Path, file_type: FileType):
        super().__init__()
        self.file_path = file_path
        self.file_type = file_type
        
    def run(self):
        """파일 로딩 실행"""
        try:
            if self.file_type in [FileType.TEXT, FileType.HTML, FileType.CSV, FileType.JSON, FileType.XML]:
                self._load_text_file()
            elif self.file_type in [FileType.IMAGE]:
                self._load_image_file()
            else:
                self.content_loaded.emit("이 파일 형식은 미리보기를 지원하지 않습니다.")
                
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _load_text_file(self):
        """텍스트 파일 로드"""
        encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin-1']
        
        content = None
        for encoding in encodings:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:  # 마지막 시도
                    raise e
        
        if content is None:
            content = "파일을 읽을 수 없습니다. 인코딩을 확인해주세요."
        
        # 파일이 너무 크면 일부만 표시
        if len(content) > 100000:  # 100KB
            content = content[:100000] + f"\n\n... (파일이 너무 큽니다. 처음 100KB만 표시)"
        
        self.content_loaded.emit(content)
    
    def _load_image_file(self):
        """이미지 파일 로드"""
        if not PILLOW_AVAILABLE:
            self.content_loaded.emit("이미지 미리보기를 위해 Pillow 라이브러리가 필요합니다.")
            return
        
        try:
            # PIL로 이미지 로드
            pil_image = Image.open(self.file_path)
            
            # 이미지가 너무 크면 리사이즈
            max_size = (800, 600)
            if pil_image.size[0] > max_size[0] or pil_image.size[1] > max_size[1]:
                # PIL 호환성을 위해 여러 방법 시도
                try:
                    # 최신 PIL 버전
                    pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    # 구 PIL 버전
                    pil_image.thumbnail(max_size, Image.LANCZOS)
            
            # RGBA 이미지의 경우 RGB로 변환 (투명도 처리)
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                # 흰색 배경으로 합성
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ('RGBA', 'LA') else None)
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # QPixmap으로 변환
            try:
                # 최신 PIL 버전 - toqimage() 사용
                qt_image = ImageQt.toqimage(pil_image)
                pixmap = QPixmap.fromImage(qt_image)
            except AttributeError:
                try:
                    # 구 PIL 버전 - ImageQt() 사용
                    qt_image = ImageQt.ImageQt(pil_image)
                    pixmap = QPixmap.fromImage(qt_image)
                except:
                    # 수동 변환
                    import numpy as np
                    img_array = np.array(pil_image)
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    from PyQt6.QtGui import QImage
                    qt_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(qt_image)
            
            if pixmap.isNull():
                self.error_occurred.emit("이미지를 QPixmap으로 변환할 수 없습니다.")
                return
                
            self.image_loaded.emit(pixmap)
            
        except Exception as e:
            self.error_occurred.emit(f"이미지 로드 실패: {str(e)}")


class TextViewer(QTextEdit):
    """텍스트 뷰어"""
    
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
    
    def set_font_size(self, size: int):
        """폰트 크기 설정"""
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)


class ImageViewer(QScrollArea):
    """이미지 뷰어"""
    
    def __init__(self):
        super().__init__()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #ccc; }")
        self.image_label.setMinimumSize(100, 100)
        
        # 기본 플레이스홀더 텍스트 설정
        self.image_label.setText("이미지를 불러오는 중...")
        
        self.setWidget(self.image_label)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 스크롤바 정책 설정
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    
    def set_image(self, pixmap: QPixmap):
        """이미지 설정"""
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
            self.image_label.resize(pixmap.size())
            self.image_label.setText("")  # 플레이스홀더 텍스트 제거
        else:
            self.image_label.setText("이미지를 표시할 수 없습니다.")
            self.image_label.clear()  # 기존 pixmap 제거


class FileViewerDialog(QDialog):
    """원본 파일 뷰어 다이얼로그"""
    
    def __init__(self, file_info: FileInfo, parent=None):
        super().__init__(parent)
        self.file_info = file_info
        self.file_path = Path(file_info.file_path)
        self.loader_thread: Optional[FileContentLoader] = None
        
        self._init_ui()
        self._setup_connections()
        self._load_settings()
        self._load_file_content()
        
        logger.info(f"파일 뷰어 다이얼로그 초기화: {self.file_path.name}")
    
    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(f"파일 뷰어 - {self.file_path.name}")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 상단 정보
        info_layout = self._create_info_section()
        layout.addLayout(info_layout)
        
        # 내용 표시 영역
        content_widget = self._create_content_section()
        layout.addWidget(content_widget)
        
        # 하단 버튼
        button_layout = self._create_button_section()
        layout.addLayout(button_layout)
    
    def _create_info_section(self) -> QHBoxLayout:
        """파일 정보 섹션 생성"""
        layout = QHBoxLayout()
        
        # 파일 정보
        info_group = QGroupBox("파일 정보")
        info_layout = QVBoxLayout(info_group)
        
        self.file_info_label = QLabel()
        self.file_info_label.setText(
            f"파일명: {self.file_path.name}\n"
            f"경로: {self.file_path.parent}\n"
            f"크기: {self._format_file_size(self.file_info.size)}\n"
            f"수정일: {self.file_info.modified_date}\n"
            f"타입: {self.file_info.file_type.value}"
        )
        info_layout.addWidget(self.file_info_label)
        
        layout.addWidget(info_group)
        
        # 표시 옵션
        options_group = QGroupBox("표시 옵션")
        options_layout = QHBoxLayout(options_group)
        
        # 폰트 크기 (텍스트용)
        font_label = QLabel("폰트 크기:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix("pt")
        
        options_layout.addWidget(font_label)
        options_layout.addWidget(self.font_size_spin)
        options_layout.addStretch()
        
        layout.addWidget(options_group)
        
        return layout
    
    def _create_content_section(self) -> QWidget:
        """내용 표시 섹션 생성"""
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        
        # 원본 보기 탭
        self.original_tab = self._create_original_tab()
        self.tab_widget.addTab(self.original_tab, "원본 보기")
        
        # 속성 정보 탭
        self.properties_tab = self._create_properties_tab()
        self.tab_widget.addTab(self.properties_tab, "속성 정보")
        
        return self.tab_widget
    
    def _create_original_tab(self) -> QWidget:
        """원본 보기 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 로딩 상태 표시
        self.loading_label = QLabel("파일을 불러오는 중...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # 텍스트 뷰어
        self.text_viewer = TextViewer()
        self.text_viewer.setVisible(False)
        layout.addWidget(self.text_viewer)
        
        # 이미지 뷰어
        self.image_viewer = ImageViewer()
        self.image_viewer.setVisible(False)
        layout.addWidget(self.image_viewer)
        
        return widget
    
    def _create_properties_tab(self) -> QWidget:
        """속성 정보 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 상세 정보
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setFont(QFont("Consolas", 10))
        
        # 파일 시스템 정보 수집
        properties_info = self._collect_file_properties()
        self.properties_text.setPlainText(properties_info)
        
        layout.addWidget(self.properties_text)
        
        return widget
    
    def _create_button_section(self) -> QHBoxLayout:
        """버튼 섹션 생성"""
        layout = QHBoxLayout()
        
        # 왼쪽 버튼들
        self.open_with_btn = QPushButton("기본 앱으로 열기")
        layout.addWidget(self.open_with_btn)
        
        self.open_folder_btn = QPushButton("폴더에서 보기")
        layout.addWidget(self.open_folder_btn)
        
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
        self.open_with_btn.clicked.connect(self._open_with_default_app)
        self.open_folder_btn.clicked.connect(self._open_in_folder)
        self.refresh_btn.clicked.connect(self._refresh_content)
        self.close_btn.clicked.connect(self.accept)
    
    def _load_file_content(self):
        """파일 내용 로드"""
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait()
        
        self.loader_thread = FileContentLoader(self.file_path, self.file_info.file_type)
        self.loader_thread.content_loaded.connect(self._on_content_loaded)
        self.loader_thread.image_loaded.connect(self._on_image_loaded)
        self.loader_thread.error_occurred.connect(self._on_error_occurred)
        self.loader_thread.start()
    
    def _on_content_loaded(self, content: str):
        """텍스트 내용 로드 완료"""
        self.loading_label.setVisible(False)
        self.text_viewer.setPlainText(content)
        self.text_viewer.setVisible(True)
        self.image_viewer.setVisible(False)
    
    def _on_image_loaded(self, pixmap: QPixmap):
        """이미지 로드 완료"""
        self.loading_label.setVisible(False)
        
        if not pixmap.isNull():
            self.image_viewer.set_image(pixmap)
            self.image_viewer.setVisible(True)
            self.text_viewer.setVisible(False)
            logger.info(f"이미지 로드 성공: {self.file_path.name} ({pixmap.width()}x{pixmap.height()})")
        else:
            self._on_error_occurred("이미지가 비어있거나 손상되었습니다.")
    
    def _on_error_occurred(self, error_message: str):
        """에러 발생시"""
        self.loading_label.setText(f"오류: {error_message}")
        self.text_viewer.setVisible(False)
        self.image_viewer.setVisible(False)
    
    def _on_font_size_changed(self, size: int):
        """폰트 크기 변경"""
        self.text_viewer.set_font_size(size)
        
        # 속성 텍스트도 업데이트
        font = self.properties_text.font()
        font.setPointSize(size)
        self.properties_text.setFont(font)
    
    def _open_with_default_app(self):
        """기본 앱으로 열기"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(str(self.file_path))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(self.file_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(self.file_path)])
                
            logger.info(f"기본 앱으로 파일 열기: {self.file_path}")
            
        except Exception as e:
            logger.error(f"기본 앱으로 열기 실패: {e}")
            QMessageBox.warning(self, "오류", f"파일을 열 수 없습니다:\n{str(e)}")
    
    def _open_in_folder(self):
        """폴더에서 보기"""
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", "/select,", str(self.file_path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", "-R", str(self.file_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(self.file_path.parent)])
                
            logger.info(f"폴더에서 파일 보기: {self.file_path}")
            
        except Exception as e:
            logger.error(f"폴더 열기 실패: {e}")
            QMessageBox.warning(self, "오류", f"폴더를 열 수 없습니다:\n{str(e)}")
    
    def _refresh_content(self):
        """내용 새로 고침"""
        self.loading_label.setText("파일을 다시 불러오는 중...")
        self.loading_label.setVisible(True)
        self.text_viewer.setVisible(False)
        self.image_viewer.setVisible(False)
        
        # 파일 정보 업데이트
        if self.file_path.exists():
            stat = self.file_path.stat()
            self.file_info.size = stat.st_size
            
            self.file_info_label.setText(
                f"파일명: {self.file_path.name}\n"
                f"경로: {self.file_path.parent}\n"
                f"크기: {self._format_file_size(self.file_info.size)}\n"
                f"수정일: {self.file_info.modified_date}\n"
                f"타입: {self.file_info.file_type.value}"
            )
        
        # 속성 정보 업데이트
        properties_info = self._collect_file_properties()
        self.properties_text.setPlainText(properties_info)
        
        # 내용 다시 로드
        self._load_file_content()
    
    def _collect_file_properties(self) -> str:
        """파일 속성 정보 수집"""
        try:
            stat = self.file_path.stat()
            
            properties = f"""파일 정보:
파일명: {self.file_path.name}
전체 경로: {self.file_path.absolute()}
상대 경로: {self.file_path}
확장자: {self.file_path.suffix}

크기 정보:
파일 크기: {self._format_file_size(stat.st_size)} ({stat.st_size:,} bytes)

시간 정보:
생성일시: {self._format_timestamp(stat.st_ctime)}
수정일시: {self._format_timestamp(stat.st_mtime)}
접근일시: {self._format_timestamp(stat.st_atime)}

권한 정보:
모드: {oct(stat.st_mode)}
소유자 읽기: {'예' if stat.st_mode & 0o400 else '아니오'}
소유자 쓰기: {'예' if stat.st_mode & 0o200 else '아니오'}
소유자 실행: {'예' if stat.st_mode & 0o100 else '아니오'}

파일 타입:
추정 타입: {self.file_info.file_type.value}
MIME 타입: {self._get_mime_type()}
"""
            return properties
            
        except Exception as e:
            return f"속성 정보를 가져올 수 없습니다: {str(e)}"
    
    def _format_file_size(self, size: int) -> str:
        """파일 크기 포맷"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _format_timestamp(self, timestamp: float) -> str:
        """타임스탬프 포맷"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_mime_type(self) -> str:
        """MIME 타입 추정"""
        mime_types = {
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.css': 'text/css',
            '.js': 'text/javascript',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.csv': 'text/csv',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.zip': 'application/zip'
        }
        
        return mime_types.get(self.file_path.suffix.lower(), 'application/octet-stream')
    
    def _load_settings(self):
        """설정 로드"""
        settings = QSettings()
        
        # 창 크기 및 위치
        geometry = settings.value("file_viewer_dialog/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 폰트 크기
        font_size = settings.value("file_viewer_dialog/font_size", 10, int)
        self.font_size_spin.setValue(font_size)
        self._on_font_size_changed(font_size)
        
        # 활성 탭
        current_tab = settings.value("file_viewer_dialog/current_tab", 0, int)
        self.tab_widget.setCurrentIndex(current_tab)
    
    def _save_settings(self):
        """설정 저장"""
        settings = QSettings()
        settings.setValue("file_viewer_dialog/geometry", self.saveGeometry())
        settings.setValue("file_viewer_dialog/font_size", self.font_size_spin.value())
        settings.setValue("file_viewer_dialog/current_tab", self.tab_widget.currentIndex())
    
    def closeEvent(self, event):
        """닫기 이벤트"""
        # 로더 스레드 정리
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait()
        
        self._save_settings()
        logger.info(f"파일 뷰어 다이얼로그 닫기: {self.file_path.name}")
        super().closeEvent(event)
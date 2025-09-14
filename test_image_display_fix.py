#!/usr/bin/env python3
"""
이미지 표시 기능 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 경로를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPixmap
    print("✓ PyQt6 import 성공")
except ImportError as e:
    print(f"✗ PyQt6 import 실패: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageQt
    print("✓ PIL import 성공")
    PILLOW_AVAILABLE = True
except ImportError as e:
    print(f"✗ PIL import 실패: {e}")
    PILLOW_AVAILABLE = False

try:
    from markitdown_gui.ui.file_viewer_dialog import FileContentLoader, ImageViewer
    from markitdown_gui.core.models import FileInfo, FileType
    print("✓ MarkItDown GUI 모듈 import 성공")
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"✗ MarkItDown GUI 모듈 import 실패: {e}")
    MODULES_AVAILABLE = False


class ImageDisplayTestDialog(QDialog):
    """이미지 표시 테스트 다이얼로그"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("이미지 표시 기능 테스트")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 상태 라벨
        self.status_label = QLabel("테스트를 시작하려면 버튼을 클릭하세요.")
        layout.addWidget(self.status_label)
        
        # 이미지 뷰어
        if MODULES_AVAILABLE:
            self.image_viewer = ImageViewer()
            layout.addWidget(self.image_viewer)
        else:
            layout.addWidget(QLabel("모듈을 불러올 수 없어 이미지 뷰어를 생성할 수 없습니다."))
        
        # 테스트 버튼들
        if PILLOW_AVAILABLE:
            test_btn1 = QPushButton("테스트 1: PIL 이미지 생성 및 표시")
            test_btn1.clicked.connect(self.test_pil_image_creation)
            layout.addWidget(test_btn1)
            
            test_btn2 = QPushButton("테스트 2: 이미지 파일 로드 (있는 경우)")
            test_btn2.clicked.connect(self.test_image_file_load)
            layout.addWidget(test_btn2)
        else:
            layout.addWidget(QLabel("PIL이 없어서 이미지 테스트를 할 수 없습니다."))
        
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def test_pil_image_creation(self):
        """PIL 이미지 생성 및 표시 테스트"""
        try:
            self.status_label.setText("테스트 이미지 생성 중...")
            
            # 간단한 테스트 이미지 생성
            pil_image = Image.new('RGB', (400, 300), (100, 150, 200))
            
            # 이미지에 패턴 추가
            from PIL import ImageDraw
            draw = ImageDraw.Draw(pil_image)
            draw.rectangle([50, 50, 350, 250], outline=(255, 255, 255), width=3)
            draw.text((200, 150), "Test Image", fill=(255, 255, 255))
            
            # PIL 호환성 테스트
            try:
                # 최신 PIL 버전
                qt_image = ImageQt.toqimage(pil_image)
                pixmap = QPixmap.fromImage(qt_image)
                conversion_method = "ImageQt.toqimage() (최신)"
            except AttributeError:
                try:
                    # 구 PIL 버전
                    qt_image = ImageQt.ImageQt(pil_image)
                    pixmap = QPixmap.fromImage(qt_image)
                    conversion_method = "ImageQt.ImageQt() (구 버전)"
                except Exception as e:
                    # 수동 변환
                    import numpy as np
                    img_array = np.array(pil_image)
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    from PyQt6.QtGui import QImage
                    qt_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(qt_image)
                    conversion_method = "수동 numpy 변환"
            
            if pixmap.isNull():
                self.status_label.setText("❌ 픽스맵 생성 실패")
                return
            
            if hasattr(self, 'image_viewer'):
                self.image_viewer.set_image(pixmap)
                self.status_label.setText(f"✅ 테스트 이미지 표시 성공! (변환 방법: {conversion_method})")
            else:
                self.status_label.setText(f"✅ 픽스맵 생성 성공! (변환 방법: {conversion_method}) - 이미지 뷰어 없음")
            
        except Exception as e:
            self.status_label.setText(f"❌ 테스트 실패: {str(e)}")
    
    def test_image_file_load(self):
        """이미지 파일 로드 테스트"""
        # 프로젝트 폴더에서 이미지 파일 찾기
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        image_files = []
        
        # 현재 폴더와 하위 폴더에서 이미지 파일 찾기
        for ext in image_extensions:
            image_files.extend(list(project_root.rglob(f"*{ext}")))
            image_files.extend(list(project_root.rglob(f"*{ext.upper()}")))
        
        if not image_files:
            self.status_label.setText("❌ 테스트할 이미지 파일을 찾을 수 없습니다.")
            return
        
        try:
            # 첫 번째 이미지 파일 로드
            image_file = image_files[0]
            self.status_label.setText(f"이미지 파일 로드 중: {image_file.name}")
            
            if MODULES_AVAILABLE:
                # FileContentLoader 사용
                file_info = FileInfo(
                    file_path=str(image_file),
                    name=image_file.name,
                    size=image_file.stat().st_size,
                    file_type=FileType.IMAGE,
                    is_selected=False
                )
                
                loader = FileContentLoader(image_file, FileType.IMAGE)
                loader.image_loaded.connect(self.on_test_image_loaded)
                loader.error_occurred.connect(self.on_test_error)
                loader.start()
            else:
                # 직접 PIL로 로드
                pil_image = Image.open(image_file)
                qt_image = ImageQt.toqimage(pil_image)
                pixmap = QPixmap.fromImage(qt_image)
                self.on_test_image_loaded(pixmap)
                
        except Exception as e:
            self.status_label.setText(f"❌ 이미지 파일 로드 실패: {str(e)}")
    
    def on_test_image_loaded(self, pixmap):
        """테스트 이미지 로드 완료"""
        if hasattr(self, 'image_viewer'):
            self.image_viewer.set_image(pixmap)
            self.status_label.setText(f"✅ 이미지 파일 로드 및 표시 성공! ({pixmap.width()}x{pixmap.height()})")
        else:
            self.status_label.setText(f"✅ 이미지 파일 로드 성공! ({pixmap.width()}x{pixmap.height()}) - 이미지 뷰어 없음")
    
    def on_test_error(self, error_message):
        """테스트 에러 발생"""
        self.status_label.setText(f"❌ 테스트 에러: {error_message}")


def main():
    """메인 함수"""
    print("=== 이미지 표시 기능 테스트 시작 ===\n")
    
    # 환경 확인
    print("환경 확인:")
    print(f"- Python 버전: {sys.version}")
    print(f"- PyQt6 사용 가능: {'예' if 'PyQt6' in sys.modules else '아니오'}")
    print(f"- PIL 사용 가능: {'예' if PILLOW_AVAILABLE else '아니오'}")
    print(f"- MarkItDown GUI 모듈 사용 가능: {'예' if MODULES_AVAILABLE else '아니오'}")
    print()
    
    # PIL 버전 확인
    if PILLOW_AVAILABLE:
        try:
            print(f"- PIL 버전: {Image.__version__}")
            # ImageQt 메서드 확인
            if hasattr(ImageQt, 'toqimage'):
                print("- ImageQt.toqimage() 사용 가능 (최신 버전)")
            elif hasattr(ImageQt, 'ImageQt'):
                print("- ImageQt.ImageQt() 사용 가능 (구 버전)")
            else:
                print("- ImageQt 변환 메서드를 찾을 수 없음")
        except:
            pass
    
    print()
    
    if not PILLOW_AVAILABLE:
        print("❌ PIL이 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요: pip install Pillow")
        return
    
    # QApplication 생성
    app = QApplication(sys.argv)
    
    try:
        # 테스트 다이얼로그 실행
        dialog = ImageDisplayTestDialog()
        dialog.exec()
        
        print("\n=== 이미지 표시 기능 테스트 완료 ===")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
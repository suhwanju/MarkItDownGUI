#!/usr/bin/env python3
"""
MarkItDown GUI Converter
메인 애플리케이션 엔트리 포인트
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 시작 경고 메시지 억제 (pydub FFmpeg, QAccessible 경고 등)
from suppress_warnings import initialize_warning_suppression
initialize_warning_suppression()

# PyQt6 임포트
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
except ImportError as e:
    print("PyQt6를 설치해주세요: pip install PyQt6")
    print(f"오류: {e}")
    sys.exit(1)

# 애플리케이션 모듈 임포트
try:
    from markitdown_gui.core.logger import setup_logging, get_logger
    from markitdown_gui.core.config_manager import ConfigManager
    from markitdown_gui.core.i18n_manager import init_i18n
    from markitdown_gui.ui.main_window import MainWindow
except ImportError as e:
    print("필요한 모듈을 찾을 수 없습니다.")
    print(f"오류: {e}")
    sys.exit(1)


def main():
    """메인 함수"""
    # 로깅 설정
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("MarkItDown GUI Converter 시작")
    
    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("MarkItDown GUI Converter")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("MarkItDown GUI Team")
    app.setOrganizationDomain("markitdown-gui.local")
    
    # 고해상도 디스플레이 지원 (PyQt6에서는 기본으로 활성화됨)
    # PyQt6에서는 AA_EnableHighDpiScaling과 AA_UseHighDpiPixmaps가 제거되었음
    # 고해상도 디스플레이는 자동으로 처리됨
    
    # 애플리케이션 아이콘 설정
    icon_paths = [
        Path("resources/icons/app_icon.png"),
        Path("markitdown_gui/resources/icons/app_icon.png"),
        Path("markitdown.png")
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            try:
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    app.setWindowIcon(icon)
                    logger.info(f"애플리케이션 아이콘 설정 완료: {icon_path}")
                    break
            except Exception as e:
                logger.warning(f"아이콘 로드 실패 {icon_path}: {e}")
    else:
        logger.warning("애플리케이션 아이콘을 찾을 수 없음")
    
    try:
        # 설정 관리자 초기화
        config_manager = ConfigManager()
        config = config_manager.load_config()
        logger.info("설정 로드 완료")
        
        # 국제화(i18n) 시스템 초기화
        i18n_manager = init_i18n(app)
        logger.info(f"i18n 시스템 초기화 완료 - 언어: {i18n_manager.get_current_language()}")
        
        # 메인 윈도우 생성 및 표시
        main_window = MainWindow(config_manager)
        main_window.show()
        
        logger.info("메인 윈도우 표시됨")
        
        # 애플리케이션 실행
        exit_code = app.exec()
        logger.info(f"애플리케이션 종료 (코드: {exit_code})")
        return exit_code
        
    except Exception as e:
        logger.critical(f"애플리케이션 초기화 실패: {e}", exc_info=True)
        
        # 에러 다이얼로그 표시
        try:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("초기화 오류")
            error_dialog.setText("애플리케이션을 시작할 수 없습니다.")
            error_dialog.setDetailedText(f"오류 세부사항:\n{str(e)}")
            error_dialog.exec()
        except:
            print(f"애플리케이션 초기화 실패: {e}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
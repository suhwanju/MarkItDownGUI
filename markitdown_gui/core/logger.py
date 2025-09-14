"""
로깅 시스템 설정
애플리케이션 전체의 로깅을 관리
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional


def setup_logging(config_file: Optional[Path] = None, log_dir: Optional[Path] = None) -> None:
    """
    로깅 시스템 설정
    
    Args:
        config_file: 로깅 설정 파일 경로
        log_dir: 로그 파일 저장 디렉토리
    """
    # 기본 경로 설정
    if config_file is None:
        config_file = Path("config") / "logging.conf"
    
    if log_dir is None:
        log_dir = Path("logs")
    
    # 로그 디렉토리 생성
    log_dir.mkdir(exist_ok=True)
    
    # 로깅 설정 파일이 있으면 사용, 없으면 기본 설정
    if config_file.exists():
        try:
            logging.config.fileConfig(config_file, disable_existing_loggers=False)
            logging.info(f"로깅 설정 파일 로드됨: {config_file}")
        except Exception as e:
            _setup_default_logging(log_dir)
            logging.error(f"로깅 설정 파일 로드 실패, 기본 설정 사용: {e}")
    else:
        _setup_default_logging(log_dir)
        logging.info("로깅 설정 파일이 없어 기본 설정 사용")


def _setup_default_logging(log_dir: Path) -> None:
    """
    기본 로깅 설정
    
    Args:
        log_dir: 로그 파일 저장 디렉토리
    """
    # 로그 파일 경로
    log_file = log_dir / "markitdown_gui.log"
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 (회전 로그)
    try:
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
    except Exception as e:
        console_handler.setLevel(logging.DEBUG)
        logging.error(f"파일 핸들러 설정 실패: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 반환
    
    Args:
        name: 로거 이름
    
    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)


class UILogHandler(logging.Handler):
    """UI 로그 위젯에 로그 메시지를 전송하는 핸들러"""
    
    def __init__(self, log_widget=None):
        super().__init__()
        self.log_widget = log_widget
        self.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.setFormatter(formatter)
    
    def emit(self, record):
        """로그 레코드를 UI 위젯으로 전송"""
        if self.log_widget is not None:
            try:
                msg = self.format(record)
                self.log_widget.append_log(msg, record.levelname)
            except Exception:
                # UI 로그 실패시 무시 (무한 루프 방지)
                pass
    
    def set_log_widget(self, log_widget):
        """로그 위젯 설정"""
        self.log_widget = log_widget


# 전역 UI 로그 핸들러
ui_log_handler = UILogHandler()


def add_ui_logging(log_widget) -> None:
    """
    UI 로깅 추가
    
    Args:
        log_widget: 로그를 표시할 UI 위젯
    """
    ui_log_handler.set_log_widget(log_widget)
    
    # 루트 로거에 UI 핸들러 추가
    root_logger = logging.getLogger()
    if ui_log_handler not in root_logger.handlers:
        root_logger.addHandler(ui_log_handler)


def remove_ui_logging() -> None:
    """UI 로깅 제거"""
    root_logger = logging.getLogger()
    if ui_log_handler in root_logger.handlers:
        root_logger.removeHandler(ui_log_handler)
    ui_log_handler.set_log_widget(None)
"""
유틸리티 함수들
파일 처리, 포맷팅, 검증 등의 공통 기능들
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Optional
import logging

from .models import FileType, get_file_type


logger = logging.getLogger(__name__)


def get_default_output_directory() -> Path:
    """
    Get the default output directory for markdown files
    
    Returns:
        Default output directory path (program_root/markdown)
    """
    from .constants import MARKDOWN_OUTPUT_DIR
    
    # Get the project root directory (parent of markitdown_gui package)
    current_file = Path(__file__)  # utils.py
    core_dir = current_file.parent  # markitdown_gui/core
    package_dir = core_dir.parent  # markitdown_gui
    project_root = package_dir.parent  # project root
    
    return project_root / MARKDOWN_OUTPUT_DIR


def validate_file_extension(file_path: Path, supported_extensions: List[str]) -> bool:
    """
    파일 확장자 검증
    
    Args:
        file_path: 검증할 파일 경로
        supported_extensions: 지원하는 확장자 리스트
    
    Returns:
        지원하는 확장자인지 여부
    """
    if not file_path or not file_path.suffix:
        return False
    
    extension = file_path.suffix.lower().lstrip('.')
    return extension in supported_extensions


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 사람이 읽기 쉬운 형태로 포맷팅
    
    Args:
        size_bytes: 바이트 단위 파일 크기
    
    Returns:
        포맷된 파일 크기 문자열
    """
    if size_bytes < 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    파일명에서 사용할 수 없는 문자를 제거하여 안전한 파일명 생성
    
    Args:
        filename: 원본 파일명
        replacement: 대체 문자 (기본값: "_")
    
    Returns:
        정리된 파일명
    """
    if not filename:
        return "untitled"
    
    # Windows/Linux에서 사용할 수 없는 문자들
    invalid_chars = r'[<>:"/\\|?*]'
    
    # 제어 문자 제거 (ASCII 0-31)
    control_chars = ''.join(chr(i) for i in range(32))
    
    # 유효하지 않은 문자 대체
    sanitized = re.sub(invalid_chars, replacement, filename)
    
    # 제어 문자 제거
    sanitized = ''.join(char for char in sanitized if char not in control_chars)
    
    # 연속된 대체 문자를 하나로 합치기
    sanitized = re.sub(f'{re.escape(replacement)}+', replacement, sanitized)
    
    # 앞뒤 공백 및 점 제거
    sanitized = sanitized.strip('. ')
    
    # Windows 예약어 처리
    windows_reserved = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_without_ext = Path(sanitized).stem.upper()
    if name_without_ext in windows_reserved:
        sanitized = f"{replacement}{sanitized}"
    
    # 빈 문자열이면 기본값 사용
    if not sanitized:
        sanitized = "untitled"
    
    # 최대 길이 제한 (확장자 포함 255자)
    if len(sanitized) > 250:
        name = Path(sanitized).stem[:240]
        ext = Path(sanitized).suffix
        sanitized = f"{name}{ext}"
    
    return sanitized


def validate_path(path: Path, check_exists: bool = True, check_readable: bool = True) -> Tuple[bool, str]:
    """
    경로 검증
    
    Args:
        path: 검증할 경로
        check_exists: 존재 여부 확인
        check_readable: 읽기 권한 확인
    
    Returns:
        (검증 성공 여부, 에러 메시지)
    """
    try:
        if not path:
            return False, "경로가 제공되지 않았습니다."
        
        # 경로 길이 확인
        if len(str(path)) > 4096:
            return False, "경로가 너무 깁니다."
        
        # 존재 여부 확인
        if check_exists and not path.exists():
            return False, f"경로가 존재하지 않습니다: {path}"
        
        # 읽기 권한 확인
        if check_readable and path.exists():
            if path.is_file() and not os.access(path, os.R_OK):
                return False, f"파일에 읽기 권한이 없습니다: {path}"
            elif path.is_dir() and not os.access(path, os.R_OK | os.X_OK):
                return False, f"디렉토리에 접근 권한이 없습니다: {path}"
        
        return True, ""
    
    except Exception as e:
        return False, f"경로 검증 중 오류가 발생했습니다: {str(e)}"


def get_unique_output_path(base_path: Path) -> Path:
    """
    중복되지 않는 출력 파일 경로 생성
    
    Args:
        base_path: 기본 파일 경로
    
    Returns:
        유니크한 파일 경로
    """
    if not base_path.exists():
        return base_path
    
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        
        if not new_path.exists():
            return new_path
        
        counter += 1
        
        # 무한루프 방지
        if counter > 9999:
            raise ValueError(f"유니크한 파일명을 생성할 수 없습니다: {base_path}")


def create_markdown_filename(original_path: Path) -> str:
    """
    원본 파일 경로로부터 마크다운 파일명 생성
    
    Args:
        original_path: 원본 파일 경로
    
    Returns:
        마크다운 파일명
    """
    base_name = original_path.stem
    sanitized_name = sanitize_filename(base_name)
    return f"{sanitized_name}.md"


def scan_directory(directory: Path, 
                  include_subdirectories: bool = True,
                  supported_extensions: Optional[List[str]] = None,
                  max_file_size_mb: int = 100) -> List[Path]:
    """
    디렉토리를 스캔하여 지원하는 파일들을 찾아 반환
    
    Args:
        directory: 스캔할 디렉토리
        include_subdirectories: 하위 디렉토리 포함 여부
        supported_extensions: 지원하는 확장자 리스트
        max_file_size_mb: 최대 파일 크기 (MB)
    
    Returns:
        찾은 파일 경로들의 리스트
    """
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"유효하지 않은 디렉토리: {directory}")
        return []
    
    if supported_extensions is None:
        supported_extensions = [e.value for e in FileType if e != FileType.UNKNOWN]
    
    max_file_size_bytes = max_file_size_mb * 1024 * 1024
    found_files = []
    
    try:
        if include_subdirectories:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue
            
            # 확장자 확인
            if not validate_file_extension(file_path, supported_extensions):
                continue
            
            # 파일 크기 확인
            try:
                file_size = file_path.stat().st_size
                if file_size > max_file_size_bytes:
                    logger.info(f"파일 크기 초과로 제외: {file_path} ({format_file_size(file_size)})")
                    continue
            except OSError:
                logger.warning(f"파일 정보 읽기 실패: {file_path}")
                continue
            
            # 읽기 권한 확인
            is_valid, error_msg = validate_path(file_path, check_exists=True, check_readable=True)
            if not is_valid:
                logger.debug(f"파일 접근 불가로 제외: {file_path} - {error_msg}")
                continue
            
            found_files.append(file_path)
    
    except Exception as e:
        logger.error(f"디렉토리 스캔 중 오류: {e}")
    
    logger.info(f"스캔 완료: {len(found_files)}개 파일 발견 (디렉토리: {directory})")
    return found_files


def get_file_icon_name(file_type: FileType) -> str:
    """
    파일 타입에 따른 아이콘 파일명 반환
    
    Args:
        file_type: 파일 타입
    
    Returns:
        아이콘 파일명
    """
    from .models import FILE_TYPE_ICONS
    return FILE_TYPE_ICONS.get(file_type, "file.png")


def estimate_conversion_time(file_size_bytes: int, file_type: FileType) -> float:
    """
    파일 크기와 타입에 따른 예상 변환 시간 계산
    
    Args:
        file_size_bytes: 파일 크기 (바이트)
        file_type: 파일 타입
    
    Returns:
        예상 변환 시간 (초)
    """
    # 기본 처리 속도 (MB/초)
    base_speed = {
        FileType.TXT: 10.0,
        FileType.CSV: 8.0,
        FileType.JSON: 6.0,
        FileType.XML: 5.0,
        FileType.HTML: 4.0,
        FileType.HTM: 4.0,
        FileType.DOCX: 2.0,
        FileType.XLSX: 1.5,
        FileType.XLS: 1.5,
        FileType.PPTX: 1.0,
        FileType.PDF: 0.8,
        FileType.EPUB: 0.8,
        FileType.ZIP: 0.5,
        # 이미지 파일들은 OCR 시간 고려
        FileType.JPG: 0.3,
        FileType.JPEG: 0.3,
        FileType.PNG: 0.3,
        FileType.GIF: 0.3,
        FileType.BMP: 0.2,
        FileType.TIFF: 0.2,
        # 오디오 파일들
        FileType.MP3: 0.1,
        FileType.WAV: 0.1,
    }
    
    speed_mb_per_sec = base_speed.get(file_type, 1.0)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    # 최소 0.1초, 최대 300초 (5분)
    estimated_time = max(0.1, min(300.0, file_size_mb / speed_mb_per_sec))
    
    return estimated_time


def create_conversion_metadata(original_path: Path, conversion_time: float) -> dict:
    """
    변환 메타데이터 생성
    
    Args:
        original_path: 원본 파일 경로
        conversion_time: 변환 소요 시간
    
    Returns:
        메타데이터 딕셔너리
    """
    try:
        file_stat = original_path.stat()
        return {
            "original_file": str(original_path),
            "original_size": file_stat.st_size,
            "original_size_formatted": format_file_size(file_stat.st_size),
            "file_type": get_file_type(original_path).value,
            "conversion_time": conversion_time,
            "conversion_time_formatted": f"{conversion_time:.2f}s" if conversion_time >= 1 else f"{conversion_time*1000:.0f}ms"
        }
    except Exception as e:
        logger.error(f"메타데이터 생성 실패: {e}")
        return {
            "original_file": str(original_path),
            "error": str(e)
        }
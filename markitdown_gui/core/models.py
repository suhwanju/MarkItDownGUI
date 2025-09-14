"""
데이터 모델 클래스들
애플리케이션에서 사용되는 데이터 구조 정의
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from .constants import DEFAULT_OUTPUT_DIRECTORY


class ConversionStatus(Enum):
    """변환 상태"""
    PENDING = "pending"        # 대기 중
    IN_PROGRESS = "in_progress"  # 진행 중
    SUCCESS = "success"        # 성공
    FAILED = "failed"          # 실패
    CANCELLED = "cancelled"    # 취소됨


class FileConflictStatus(Enum):
    """파일 충돌 상태"""
    NONE = "none"                    # 충돌 없음
    EXISTS = "exists"                # 파일이 이미 존재함
    WILL_SKIP = "will_skip"          # 건너뛸 예정
    WILL_OVERWRITE = "will_overwrite"  # 덮어쓸 예정
    WILL_RENAME = "will_rename"      # 이름 변경할 예정
    RESOLVED = "resolved"            # 충돌 해결됨


class FileConflictPolicy(Enum):
    """파일 충돌 처리 정책"""
    SKIP = "skip"            # 건너뛰기
    OVERWRITE = "overwrite"  # 덮어쓰기
    RENAME = "rename"        # 이름 변경
    ASK_USER = "ask_user"    # 사용자에게 묻기


class ConversionProgressStatus(Enum):
    """상세 변환 진행 상태"""
    INITIALIZING = "initializing"      # 초기화 중
    VALIDATING_FILE = "validating_file"  # 파일 검증 중
    READING_FILE = "reading_file"      # 파일 읽기 중
    PROCESSING = "processing"          # 변환 처리 중
    CHECKING_CONFLICTS = "checking_conflicts"  # 충돌 확인 중
    RESOLVING_CONFLICTS = "resolving_conflicts"  # 충돌 해결 중
    WRITING_OUTPUT = "writing_output"  # 출력 파일 쓰기 중
    FINALIZING = "finalizing"          # 마무리 중
    COMPLETED = "completed"            # 완료
    ERROR = "error"                    # 오류


class FileType(Enum):
    """지원하는 파일 타입"""
    # Office 문서
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    XLS = "xls"
    
    # PDF
    PDF = "pdf"
    
    # 이미지
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    
    # 오디오
    MP3 = "mp3"
    WAV = "wav"
    
    # 웹/텍스트
    HTML = "html"
    HTM = "htm"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    TXT = "txt"
    
    # 아카이브
    ZIP = "zip"
    
    # 전자책
    EPUB = "epub"
    
    # 기타
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    """파일 정보"""
    path: Path
    name: str
    size: int
    modified_time: datetime
    file_type: FileType
    is_selected: bool = False
    conversion_status: ConversionStatus = ConversionStatus.PENDING
    # 파일 충돌 관련 필드
    conflict_status: FileConflictStatus = FileConflictStatus.NONE
    conflict_policy: Optional[FileConflictPolicy] = None
    output_path: Optional[Path] = None
    resolved_output_path: Optional[Path] = None
    # 상세 변환 진행 상태
    progress_status: ConversionProgressStatus = ConversionProgressStatus.INITIALIZING
    
    @property
    def size_formatted(self) -> str:
        """파일 크기를 사람이 읽기 쉬운 형태로 반환"""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 ** 2:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 ** 3:
            return f"{self.size / (1024 ** 2):.1f} MB"
        else:
            return f"{self.size / (1024 ** 3):.1f} GB"
    
    @property
    def extension(self) -> str:
        """파일 확장자 반환"""
        return self.path.suffix.lower()


@dataclass
class ConversionResult:
    """변환 결과"""
    file_info: FileInfo
    status: ConversionStatus
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    conversion_time: Optional[float] = None  # 초 단위
    metadata: Optional[Dict[str, Any]] = None
    # 파일 충돌 관련 정보
    conflict_status: FileConflictStatus = FileConflictStatus.NONE
    applied_policy: Optional[FileConflictPolicy] = None
    original_output_path: Optional[Path] = None
    # 상세 진행 정보
    progress_status: ConversionProgressStatus = ConversionProgressStatus.COMPLETED
    progress_details: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """변환 성공 여부"""
        return self.status == ConversionStatus.SUCCESS
    
    @property
    def conversion_time_formatted(self) -> str:
        """변환 시간을 포맷팅하여 반환"""
        if self.conversion_time is None:
            return "N/A"
        elif self.conversion_time < 1:
            return f"{self.conversion_time * 1000:.0f}ms"
        else:
            return f"{self.conversion_time:.1f}s"


@dataclass
class FileConflictConfig:
    """파일 충돌 설정"""
    default_policy: FileConflictPolicy = FileConflictPolicy.ASK_USER
    auto_rename_pattern: str = "{name}_{counter}{ext}"  # 자동 이름 변경 패턴
    remember_choices: bool = True  # 사용자 선택 기억
    apply_to_all: bool = False    # 모든 파일에 적용
    backup_original: bool = False  # 원본 파일 백업
    conflict_log_enabled: bool = True  # 충돌 로그 기록
    ask_user_timeout: int = 30    # 사용자 응답 대기 시간(초)
    preserve_original: bool = False  # 원본 파일 보존 (backup_original과 동일)
    backup_existing: bool = True   # 기존 파일 백업


@dataclass
class AppConfig:
    """애플리케이션 설정"""
    # 일반 설정
    language: str = "ko"
    theme: str = "light"  # light, dark, auto
    
    # 변환 설정
    output_directory: Path = Path(DEFAULT_OUTPUT_DIRECTORY)
    max_concurrent_conversions: int = 3
    include_subdirectories: bool = True
    save_to_original_directory: bool = True  # 원본 디렉토리에 저장
    
    # 파일 충돌 설정
    conflict_config: FileConflictConfig = None
    
    # 파일 설정
    supported_extensions: List[str] = None
    max_file_size_mb: int = 100
    
    # LLM 설정 (이미지 OCR용) - deprecated, moved to secure storage
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o-mini"
    
    # LLM 공급업체 설정
    llm_provider: str = "openai"  # openai, azure, local
    llm_base_url: Optional[str] = None
    llm_api_version: Optional[str] = None
    
    # OCR 설정
    enable_llm_ocr: bool = False
    ocr_language: str = "auto"
    max_image_size: int = 1024
    
    # LLM 고급 설정
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    llm_system_prompt: str = ""
    
    # 토큰 사용량 추적
    track_token_usage: bool = True
    token_usage_limit_monthly: int = 100000  # 월별 토큰 한도
    
    # UI 설정
    window_width: int = 1200
    window_height: int = 800
    recent_directories: List[str] = None
    
    def __post_init__(self):
        """기본값 설정"""
        if self.supported_extensions is None:
            self.supported_extensions = [e.value for e in FileType if e != FileType.UNKNOWN]
        
        if self.recent_directories is None:
            self.recent_directories = []
            
        if self.conflict_config is None:
            self.conflict_config = FileConflictConfig()
    
    def get(self, key: str, default=None):
        """딕셔너리 스타일 접근을 위한 get 메서드"""
        try:
            return getattr(self, key, default)
        except AttributeError:
            return default
    
    def __getitem__(self, key: str):
        """딕셔너리 스타일 접근을 위한 __getitem__ 메서드"""
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"'{key}' not found in AppConfig")
    
    def __setitem__(self, key: str, value):
        """딕셔너리 스타일 할당을 위한 __setitem__ 메서드"""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"'{key}' is not a valid AppConfig attribute")
    
    def __contains__(self, key: str) -> bool:
        """딕셔너리 스타일 in 연산자 지원"""
        return hasattr(self, key)
    
    def keys(self):
        """딕셔너리 스타일 keys() 메서드"""
        return self.__dataclass_fields__.keys()
    
    def items(self):
        """딕셔너리 스타일 items() 메서드"""
        for key in self.__dataclass_fields__.keys():
            yield key, getattr(self, key)
    
    def values(self):
        """딕셔너리 스타일 values() 메서드"""
        for key in self.__dataclass_fields__.keys():
            yield getattr(self, key)


@dataclass
class ConversionProgress:
    """변환 진행률 정보"""
    total_files: int
    completed_files: int
    current_file: Optional[str] = None
    current_status: str = ""
    # 상세 진행 정보
    current_progress_status: ConversionProgressStatus = ConversionProgressStatus.INITIALIZING
    current_file_progress: float = 0.0  # 현재 파일의 진행률 (0.0-1.0)
    # 충돌 처리 통계
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    files_skipped: int = 0
    files_overwritten: int = 0
    files_renamed: int = 0
    # 성능 메트릭
    start_time: Optional[datetime] = None
    estimated_time_remaining: Optional[float] = None  # 초 단위
    
    @property
    def progress_percent(self) -> float:
        """진행률 퍼센트"""
        if self.total_files == 0:
            return 0.0
        # 현재 파일의 부분 진행률도 포함
        base_progress = self.completed_files / self.total_files
        current_file_contribution = self.current_file_progress / self.total_files
        return (base_progress + current_file_contribution) * 100
    
    @property
    def is_complete(self) -> bool:
        """완료 여부"""
        return self.completed_files >= self.total_files
    
    @property
    def has_conflicts(self) -> bool:
        """충돌이 발생했는지 여부"""
        return self.conflicts_detected > 0
    
    @property
    def conflict_resolution_rate(self) -> float:
        """충돌 해결률"""
        if self.conflicts_detected == 0:
            return 100.0
        return (self.conflicts_resolved / self.conflicts_detected) * 100
    
    @property
    def elapsed_time(self) -> float:
        """경과 시간 (초)"""
        if self.start_time is None:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_detailed_status(self) -> str:
        """상세 상태 문자열 반환"""
        if self.current_file:
            return f"{self.current_progress_status.value}: {self.current_file}"
        return self.current_progress_status.value


# 파일 타입별 아이콘 매핑
FILE_TYPE_ICONS = {
    FileType.DOCX: "document.png",
    FileType.PPTX: "presentation.png",
    FileType.XLSX: "spreadsheet.png",
    FileType.XLS: "spreadsheet.png",
    FileType.PDF: "pdf.png",
    FileType.JPG: "image.png",
    FileType.JPEG: "image.png",
    FileType.PNG: "image.png",
    FileType.GIF: "image.png",
    FileType.BMP: "image.png",
    FileType.TIFF: "image.png",
    FileType.MP3: "audio.png",
    FileType.WAV: "audio.png",
    FileType.HTML: "web.png",
    FileType.HTM: "web.png",
    FileType.CSV: "data.png",
    FileType.JSON: "data.png",
    FileType.XML: "data.png",
    FileType.TXT: "text.png",
    FileType.ZIP: "archive.png",
    FileType.EPUB: "ebook.png",
    FileType.UNKNOWN: "file.png",
}


@dataclass
class FileConflictInfo:
    """파일 충돌 정보"""
    source_path: Path
    target_path: Path
    conflict_status: FileConflictStatus
    existing_file_size: Optional[int] = None
    existing_file_modified: Optional[datetime] = None
    suggested_resolution: Optional[FileConflictPolicy] = None
    resolved_path: Optional[Path] = None
    
    @property
    def file_name(self) -> str:
        """파일명 반환"""
        return self.target_path.name
    
    @property
    def has_existing_file(self) -> bool:
        """기존 파일 존재 여부"""
        return self.target_path.exists()
    
    def generate_renamed_path(self, pattern: str = "{name}_{counter}{ext}") -> Path:
        """충돌을 피하는 새 파일 경로 생성"""
        counter = 1
        name_stem = self.target_path.stem
        suffix = self.target_path.suffix
        parent = self.target_path.parent
        
        while True:
            new_name = pattern.format(
                name=name_stem,
                counter=counter,
                ext=suffix
            )
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1


def get_file_type(file_path: Path) -> FileType:
    """파일 경로로부터 파일 타입 결정"""
    extension = file_path.suffix.lower().lstrip('.')
    
    try:
        return FileType(extension)
    except ValueError:
        return FileType.UNKNOWN


def create_markdown_output_path(source_path: Path, output_dir: Optional[Path] = None, 
                               save_to_original_dir: bool = True) -> Path:
    """마크다운 출력 경로 생성"""
    if save_to_original_dir:
        # 원본 파일과 같은 디렉토리에 저장
        return source_path.parent / f"{source_path.stem}.md"
    else:
        # 지정된 출력 디렉토리에 저장
        if output_dir is None:
            output_dir = Path(DEFAULT_OUTPUT_DIRECTORY)
        return output_dir / f"{source_path.stem}.md"


def detect_file_conflict(source_path: Path, target_path: Path) -> FileConflictInfo:
    """파일 충돌 감지"""
    conflict_info = FileConflictInfo(
        source_path=source_path,
        target_path=target_path,
        conflict_status=FileConflictStatus.NONE
    )
    
    if target_path.exists():
        conflict_info.conflict_status = FileConflictStatus.EXISTS
        try:
            stat = target_path.stat()
            conflict_info.existing_file_size = stat.st_size
            conflict_info.existing_file_modified = datetime.fromtimestamp(stat.st_mtime)
        except OSError:
            pass  # 파일 정보를 가져올 수 없는 경우 무시
    
    return conflict_info


# LLM 관련 모델들

class LLMProvider(Enum):
    """LLM 공급업체"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class TokenUsageType(Enum):
    """토큰 사용 유형"""
    OCR = "ocr"
    TEXT_GENERATION = "text_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


@dataclass
class LLMConfig:
    """LLM 설정"""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    
    # 요청 설정
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 30
    max_retries: int = 3
    
    # OCR 설정
    enable_ocr: bool = False
    ocr_language: str = "auto"
    max_image_size: int = 1024
    
    # 시스템 프롬프트
    system_prompt: str = ""
    
    # 토큰 사용량 추적
    track_usage: bool = True
    usage_limit_monthly: int = 100000


@dataclass
class TokenUsage:
    """토큰 사용량 정보"""
    usage_type: TokenUsageType
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def cost_estimate(self) -> float:
        """비용 추정 (USD)"""
        # GPT-4o-mini 기준 (실제로는 모델별로 다름)
        cost_per_1k_prompt = 0.00015  # $0.15/1K tokens
        cost_per_1k_completion = 0.0006  # $0.60/1K tokens
        
        prompt_cost = (self.prompt_tokens / 1000) * cost_per_1k_prompt
        completion_cost = (self.completion_tokens / 1000) * cost_per_1k_completion
        
        return prompt_cost + completion_cost


@dataclass
class LLMResponse:
    """LLM 응답"""
    content: str
    usage: TokenUsage
    model: str
    provider: LLMProvider
    success: bool = True
    error_message: Optional[str] = None
    response_time: float = 0.0
    
    @property
    def is_success(self) -> bool:
        """성공 여부"""
        return self.success and self.error_message is None


@dataclass
class OCRRequest:
    """OCR 요청"""
    image_path: Path
    language: str = "auto"
    max_size: int = 1024
    prompt: Optional[str] = None
    
    @property
    def image_exists(self) -> bool:
        """이미지 파일 존재 여부"""
        return self.image_path.exists()


@dataclass
class OCRResult:
    """OCR 결과"""
    text: str
    confidence: float = 0.0
    language_detected: Optional[str] = None
    processing_time: float = 0.0
    token_usage: Optional[TokenUsage] = None
    error_message: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """성공 여부"""
        return self.error_message is None and len(self.text) > 0


@dataclass
class LLMStats:
    """LLM 통계"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost_estimate: float = 0.0
    average_response_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def add_request(self, response: LLMResponse):
        """요청 결과 추가"""
        self.total_requests += 1
        if response.is_success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_tokens_used += response.usage.total_tokens
        self.total_cost_estimate += response.usage.cost_estimate
        
        # 평균 응답 시간 업데이트
        self.average_response_time = (
            (self.average_response_time * (self.total_requests - 1) + response.response_time) 
            / self.total_requests
        )
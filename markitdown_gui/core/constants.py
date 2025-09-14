"""
상수 정의 모듈
애플리케이션에서 사용되는 매직 넘버와 상수들을 정의
"""

# File Size Constants (bytes)
KB = 1024
MB = 1024 ** 2
GB = 1024 ** 3

# Default file size limits
DEFAULT_MAX_FILE_SIZE_MB = 100
DEFAULT_MAX_FILE_SIZE_BYTES = DEFAULT_MAX_FILE_SIZE_MB * MB

# Image processing constants
DEFAULT_MAX_IMAGE_SIZE = 1024
DEFAULT_IMAGE_QUALITY = 85
MAX_THUMBNAIL_SIZE = (800, 600)
DEFAULT_THUMBNAIL_QUALITY = 75

# UI Constants
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 600
MIN_WINDOW_HEIGHT = 400

# Font sizes
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 20
DEFAULT_FONT_SIZE = 10

# LLM Configuration Constants
DEFAULT_TEMPERATURE = 0.1
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
TEMPERATURE_SCALE = 100  # For slider (0-200 -> 0.0-2.0)

DEFAULT_MAX_TOKENS = 4096
MIN_MAX_TOKENS = 256
MAX_MAX_TOKENS = 32768

DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3

# Token Usage Constants
DEFAULT_MONTHLY_TOKEN_LIMIT = 100000
MIN_MONTHLY_TOKEN_LIMIT = 1000
MAX_MONTHLY_TOKEN_LIMIT = 10000000

# OCR Constants
DEFAULT_OCR_LANGUAGE = "auto"
SUPPORTED_OCR_LANGUAGES = ["auto", "ko", "en", "zh", "ja", "es", "fr", "de"]

# API Client Constants
DEFAULT_REQUEST_TIMEOUT = 30
MAX_REQUEST_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Connection Test Constants
CONNECTION_TEST_TIMEOUT = 10
CONNECTION_TEST_MAX_TOKENS = 50
CONNECTION_TEST_PROMPT = "Hello! Please respond with 'OK' to test the connection."

# File Processing Constants
MAX_CONCURRENT_CONVERSIONS = 8
DEFAULT_CONCURRENT_CONVERSIONS = 3
MIN_CONCURRENT_CONVERSIONS = 1

# Directory and File Management
MAX_RECENT_DIRECTORIES = 10
MAX_RECENT_FILES = 20

# Default Output Directory Constants
MARKDOWN_OUTPUT_DIR = "markdown"  # Markdown output directory relative to program root
DEFAULT_OUTPUT_DIRECTORY = MARKDOWN_OUTPUT_DIR

# Progress and Status Update Intervals
PROGRESS_UPDATE_INTERVAL = 100  # milliseconds
STATUS_UPDATE_INTERVAL = 500   # milliseconds

# Thread and Processing Constants
THREAD_POOL_SIZE = 4
MAX_WORKER_THREADS = 16

# Logging Constants
LOG_MAX_FILE_SIZE = 10 * MB  # 10MB
LOG_BACKUP_COUNT = 5
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Error Messages
class ErrorMessages:
    """Error message constants"""
    
    # General errors
    UNKNOWN_ERROR = "Unknown error occurred"
    INVALID_INPUT = "Invalid input provided"
    FILE_NOT_FOUND = "File not found"
    PERMISSION_DENIED = "Permission denied"
    
    # Network errors
    CONNECTION_TIMEOUT = "Connection timeout"
    CONNECTION_ERROR = "Connection error"
    API_RATE_LIMIT = "API rate limit exceeded"
    API_KEY_INVALID = "Invalid API key"
    
    # LLM errors
    LLM_NOT_CONFIGURED = "LLM not configured"
    LLM_PROVIDER_UNSUPPORTED = "Unsupported LLM provider"
    LLM_MODEL_NOT_FOUND = "Model not found"
    TOKEN_LIMIT_EXCEEDED = "Token limit exceeded"
    
    # OCR errors
    OCR_NOT_AVAILABLE = "OCR service not available"
    TESSERACT_NOT_FOUND = "Tesseract OCR not found"
    PIL_NOT_AVAILABLE = "PIL (Pillow) library not available"
    
    # File processing errors
    UNSUPPORTED_FILE_TYPE = "Unsupported file type"
    FILE_TOO_LARGE = "File too large"
    CONVERSION_FAILED = "Conversion failed"
    
    # Configuration errors
    CONFIG_LOAD_FAILED = "Failed to load configuration"
    CONFIG_SAVE_FAILED = "Failed to save configuration"
    INVALID_CONFIG = "Invalid configuration"

# Success Messages
class SuccessMessages:
    """Success message constants"""
    
    CONFIG_SAVED = "Configuration saved successfully"
    CONNECTION_SUCCESS = "Connection test successful"
    CONVERSION_COMPLETE = "Conversion completed successfully"
    API_KEY_SAVED = "API key saved successfully"
    API_KEY_DELETED = "API key deleted successfully"

# File Type Categories
DOCUMENT_EXTENSIONS = ['.docx', '.pptx', '.xlsx', '.xls', '.pdf']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
AUDIO_EXTENSIONS = ['.mp3', '.wav']
TEXT_EXTENSIONS = ['.txt', '.html', '.htm', '.csv', '.json', '.xml']
ARCHIVE_EXTENSIONS = ['.zip']
EBOOK_EXTENSIONS = ['.epub']

# Supported file extensions for conversion
ALL_SUPPORTED_EXTENSIONS = (
    DOCUMENT_EXTENSIONS + 
    IMAGE_EXTENSIONS + 
    AUDIO_EXTENSIONS + 
    TEXT_EXTENSIONS + 
    ARCHIVE_EXTENSIONS + 
    EBOOK_EXTENSIONS
)

# Cost estimation (per 1K tokens) - updated as of 2024
LLM_COSTS_PER_1K_TOKENS = {
    'gpt-4o': {'prompt': 0.0025, 'completion': 0.01},
    'gpt-4o-mini': {'prompt': 0.00015, 'completion': 0.0006},
    'gpt-4-turbo': {'prompt': 0.01, 'completion': 0.03},
    'gpt-3.5-turbo': {'prompt': 0.0015, 'completion': 0.002},
    'claude-3-opus': {'prompt': 0.015, 'completion': 0.075},
    'claude-3-sonnet': {'prompt': 0.003, 'completion': 0.015},
    'claude-3-haiku': {'prompt': 0.00025, 'completion': 0.00125},
    'gemini-pro': {'prompt': 0.0005, 'completion': 0.0015},
}

# Default LLM cost (fallback)
DEFAULT_LLM_COST = {'prompt': 0.001, 'completion': 0.003}

# UI Theme Colors (for consistency)
class ThemeColors:
    """UI theme color constants"""
    
    # Status colors
    SUCCESS_COLOR = "green"
    ERROR_COLOR = "red"
    WARNING_COLOR = "orange"
    INFO_COLOR = "blue"
    
    # Progress colors
    PROGRESS_COLOR = "#0078d4"
    PROGRESS_BACKGROUND = "#f0f0f0"
    
    # Text colors
    PRIMARY_TEXT = "#000000"
    SECONDARY_TEXT = "#666666"
    DISABLED_TEXT = "#cccccc"

# Validation Constants
class ValidationLimits:
    """Input validation limits"""
    
    # Text input limits
    MAX_PATH_LENGTH = 260
    MAX_FILENAME_LENGTH = 255
    MAX_PROMPT_LENGTH = 10000
    MAX_ERROR_MESSAGE_LENGTH = 1000
    
    # Numeric limits
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0
    MIN_MAX_TOKENS = 1
    MAX_MAX_TOKENS = 128000
    
    # API limits
    MAX_API_KEY_LENGTH = 200
    MIN_API_KEY_LENGTH = 10
    MAX_BASE_URL_LENGTH = 500
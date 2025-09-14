"""
사용자 정의 예외 클래스들
애플리케이션별 예외 상황을 처리하기 위한 커스텀 예외 정의
"""

from typing import Optional, Dict, Any


class MarkItDownError(Exception):
    """Base exception for MarkItDown application"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# Configuration related exceptions
class ConfigurationError(MarkItDownError):
    """Configuration related errors"""
    pass


class ConfigLoadError(ConfigurationError):
    """Configuration load errors"""
    pass


class ConfigSaveError(ConfigurationError):
    """Configuration save errors"""
    pass


class InvalidConfigError(ConfigurationError):
    """Invalid configuration errors"""
    pass


# File processing exceptions
class FileProcessingError(MarkItDownError):
    """File processing related errors"""
    pass


class UnsupportedFileTypeError(FileProcessingError):
    """Unsupported file type errors"""
    pass


class FileSizeError(FileProcessingError):
    """File size related errors"""
    pass


class FilePermissionError(FileProcessingError):
    """File permission errors"""
    pass


class ConversionError(FileProcessingError):
    """File conversion errors"""
    pass


# LLM related exceptions
class LLMError(MarkItDownError):
    """LLM related errors"""
    pass


class LLMConfigurationError(LLMError):
    """LLM configuration errors"""
    pass


class LLMConnectionError(LLMError):
    """LLM connection errors"""
    pass


class LLMAuthenticationError(LLMError):
    """LLM authentication errors"""
    pass


class LLMRateLimitError(LLMError):
    """LLM rate limit errors"""
    pass


class LLMTokenLimitError(LLMError):
    """LLM token limit errors"""
    pass


class UnsupportedProviderError(LLMError):
    """Unsupported LLM provider errors"""
    pass


class ModelNotFoundError(LLMError):
    """Model not found errors"""
    pass


# OCR related exceptions
class OCRError(MarkItDownError):
    """OCR related errors"""
    pass


class OCRNotAvailableError(OCRError):
    """OCR service not available errors"""
    pass


class TesseractNotFoundError(OCRError):
    """Tesseract OCR not found errors"""
    pass


class ImageProcessingError(OCRError):
    """Image processing errors"""
    pass


# API related exceptions
class APIError(MarkItDownError):
    """API related errors"""
    pass


class APIConnectionError(APIError):
    """API connection errors"""
    pass


class APITimeoutError(APIError):
    """API timeout errors"""
    pass


class APIRateLimitError(APIError):
    """API rate limit errors"""
    pass


class APIAuthenticationError(APIError):
    """API authentication errors"""
    pass


class APIResponseError(APIError):
    """API response errors"""
    pass


# Security related exceptions
class SecurityError(MarkItDownError):
    """Security related errors"""
    pass


class KeyringError(SecurityError):
    """Keyring access errors"""
    pass


class APIKeyError(SecurityError):
    """API key related errors"""
    pass


# Validation exceptions
class ValidationError(MarkItDownError):
    """Input validation errors"""
    pass


class InvalidInputError(ValidationError):
    """Invalid input errors"""
    pass


class InvalidPathError(ValidationError):
    """Invalid path errors"""
    pass


class InvalidParameterError(ValidationError):
    """Invalid parameter errors"""
    pass


# Resource exceptions
class ResourceError(MarkItDownError):
    """Resource related errors"""
    pass


class ResourceNotFoundError(ResourceError):
    """Resource not found errors"""
    pass


class ResourceAccessError(ResourceError):
    """Resource access errors"""
    pass


class InsufficientResourceError(ResourceError):
    """Insufficient resource errors"""
    pass


# Thread and concurrency exceptions
class ConcurrencyError(MarkItDownError):
    """Concurrency related errors"""
    pass


class ThreadPoolError(ConcurrencyError):
    """Thread pool errors"""
    pass


class TaskTimeoutError(ConcurrencyError):
    """Task timeout errors"""
    pass


# Utility functions for exception handling
def wrap_exception(func):
    """
    Decorator to wrap functions with proper exception handling
    Converts generic exceptions to specific MarkItDown exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MarkItDownError:
            # Re-raise our custom exceptions as-is
            raise
        except FileNotFoundError as e:
            raise ResourceNotFoundError(str(e), "FILE_NOT_FOUND")
        except PermissionError as e:
            raise FilePermissionError(str(e), "PERMISSION_DENIED")
        except TimeoutError as e:
            raise APITimeoutError(str(e), "TIMEOUT")
        except ConnectionError as e:
            raise APIConnectionError(str(e), "CONNECTION_ERROR")
        except ValueError as e:
            raise InvalidInputError(str(e), "INVALID_VALUE")
        except TypeError as e:
            raise InvalidParameterError(str(e), "INVALID_TYPE")
        except Exception as e:
            # Generic fallback
            raise MarkItDownError(f"Unexpected error: {str(e)}", "UNKNOWN_ERROR")
    
    return wrapper


def handle_api_error(response_status: int, response_text: str) -> APIError:
    """
    Convert HTTP response codes to appropriate API exceptions
    
    Args:
        response_status: HTTP status code
        response_text: Response text
    
    Returns:
        Appropriate API exception
    """
    if response_status == 401:
        return APIAuthenticationError(f"Authentication failed: {response_text}", "AUTH_ERROR")
    elif response_status == 403:
        return APIAuthenticationError(f"Forbidden: {response_text}", "FORBIDDEN")
    elif response_status == 429:
        return APIRateLimitError(f"Rate limit exceeded: {response_text}", "RATE_LIMIT")
    elif response_status == 404:
        return ModelNotFoundError(f"Model not found: {response_text}", "MODEL_NOT_FOUND")
    elif response_status >= 500:
        return APIError(f"Server error ({response_status}): {response_text}", "SERVER_ERROR")
    else:
        return APIResponseError(f"API error ({response_status}): {response_text}", "API_ERROR")


def log_exception(logger, exception: Exception, context: Optional[str] = None):
    """
    Log exception with proper context and details
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Optional context information
    """
    if isinstance(exception, MarkItDownError):
        log_message = f"{exception.message}"
        if context:
            log_message = f"{context}: {log_message}"
        
        if exception.error_code:
            log_message += f" (Code: {exception.error_code})"
        
        if exception.details:
            log_message += f" Details: {exception.details}"
        
        logger.error(log_message)
    else:
        if context:
            logger.error(f"{context}: {str(exception)}")
        else:
            logger.error(f"Unexpected error: {str(exception)}")


class ExceptionContext:
    """Context manager for exception handling with logging"""
    
    def __init__(self, logger, context: str, reraise: bool = True):
        self.logger = logger
        self.context = context
        self.reraise = reraise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            log_exception(self.logger, exc_value, self.context)
            if not self.reraise:
                return True  # Suppress the exception
        return False
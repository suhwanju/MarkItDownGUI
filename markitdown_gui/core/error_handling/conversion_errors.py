"""
Conversion-Specific Error Classes

Extended error hierarchy for document conversion with specific focus
on PDF FontBBox errors and MarkItDown integration issues.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from ..exceptions import MarkItDownError, ConversionError as BaseConversionError


class ConversionError(BaseConversionError):
    """Enhanced conversion error with recovery information"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 is_recoverable: bool = True, recovery_suggestions: Optional[List[str]] = None,
                 error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.file_path = file_path
        self.is_recoverable = is_recoverable
        self.recovery_suggestions = recovery_suggestions or []
    
    def add_recovery_suggestion(self, suggestion: str):
        """Add a recovery suggestion"""
        if suggestion not in self.recovery_suggestions:
            self.recovery_suggestions.append(suggestion)


class RecoverableError(ConversionError):
    """Error that can potentially be recovered from"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 recovery_suggestions: Optional[List[str]] = None,
                 error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, file_path, True, recovery_suggestions, error_code, details)


class UnrecoverableError(ConversionError):
    """Error that cannot be recovered from"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, file_path, False, [], error_code, details)


class PDFParsingError(RecoverableError):
    """PDF parsing related errors"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 pdf_error_type: Optional[str] = None, page_number: Optional[int] = None,
                 error_code: str = "PDF_PARSING_ERROR"):
        details = {
            "pdf_error_type": pdf_error_type,
            "page_number": page_number
        }
        
        recovery_suggestions = [
            "Try using alternative PDF parsing method",
            "Check if PDF is corrupted or password protected",
            "Consider using PDF repair tools"
        ]
        
        super().__init__(message, file_path, recovery_suggestions, error_code, details)
        self.pdf_error_type = pdf_error_type
        self.page_number = page_number


class FontDescriptorError(PDFParsingError):
    """Specific FontBBox descriptor parsing errors"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 font_name: Optional[str] = None, bbox_value: Optional[str] = None,
                 font_issues: Optional[List[Dict[str, Any]]] = None,
                 error_code: str = "FONT_DESCRIPTOR_ERROR"):
        
        details = {
            "font_name": font_name,
            "bbox_value": bbox_value,
            "font_issues": font_issues or []
        }
        
        recovery_suggestions = [
            "Use alternative PDF conversion method that handles font issues",
            "Try extracting text without font formatting information",
            "Consider using OCR-based conversion for this PDF",
            "Repair PDF font descriptors using specialized tools"
        ]
        
        super().__init__(message, file_path, "font_descriptor", None, error_code)
        self.details.update(details)
        self.font_name = font_name
        self.bbox_value = bbox_value
        self.font_issues = font_issues or []
    
    def add_font_issue(self, font_name: str, issue_type: str, details: Optional[Dict[str, Any]] = None):
        """Add a font-specific issue"""
        issue = {
            "font_name": font_name,
            "issue_type": issue_type,
            "details": details or {}
        }
        self.font_issues.append(issue)
        self.details["font_issues"] = self.font_issues
    
    @classmethod
    def from_markitdown_warning(cls, warning_message: str, file_path: Optional[Path] = None) -> 'FontDescriptorError':
        """Create FontDescriptorError from MarkItDown warning message"""
        # Parse common MarkItDown font warning patterns
        if "FontBBox from font descriptor" in warning_message and "None cannot be parsed as 4 floats" in warning_message:
            return cls(
                message=f"FontBBox parsing error: {warning_message}",
                file_path=file_path,
                bbox_value="None",
                error_code="FONTBBOX_NONE_ERROR"
            )
        elif "FontBBox" in warning_message:
            return cls(
                message=f"Font descriptor issue: {warning_message}",
                file_path=file_path,
                error_code="FONTBBOX_PARSING_ERROR"
            )
        else:
            return cls(
                message=f"Font descriptor error: {warning_message}",
                file_path=file_path,
                error_code="FONT_DESCRIPTOR_GENERIC"
            )


class MarkItDownError(RecoverableError):
    """MarkItDown library specific errors"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 markitdown_error_type: Optional[str] = None,
                 original_exception: Optional[Exception] = None,
                 error_code: str = "MARKITDOWN_ERROR"):
        
        details = {
            "markitdown_error_type": markitdown_error_type,
            "original_exception_type": type(original_exception).__name__ if original_exception else None,
            "original_exception_message": str(original_exception) if original_exception else None
        }
        
        recovery_suggestions = [
            "Retry conversion with different MarkItDown settings",
            "Use alternative conversion method for this file type",
            "Check if file format is supported by current MarkItDown version"
        ]
        
        super().__init__(message, file_path, recovery_suggestions, error_code, details)
        self.markitdown_error_type = markitdown_error_type
        self.original_exception = original_exception
    
    @classmethod
    def wrap_exception(cls, original_exception: Exception, file_path: Optional[Path] = None) -> 'MarkItDownError':
        """Wrap a generic exception as MarkItDownError"""
        error_message = str(original_exception)
        
        # Determine error type from exception
        if isinstance(original_exception, ValueError) and "FontBBox" in error_message:
            return FontDescriptorError.from_markitdown_warning(error_message, file_path)
        elif isinstance(original_exception, FileNotFoundError):
            return cls(
                message=f"File not found during MarkItDown conversion: {error_message}",
                file_path=file_path,
                markitdown_error_type="file_not_found",
                original_exception=original_exception,
                error_code="MARKITDOWN_FILE_NOT_FOUND"
            )
        elif isinstance(original_exception, PermissionError):
            return cls(
                message=f"Permission denied during MarkItDown conversion: {error_message}",
                file_path=file_path,
                markitdown_error_type="permission_denied", 
                original_exception=original_exception,
                error_code="MARKITDOWN_PERMISSION_ERROR"
            )
        else:
            return cls(
                message=f"MarkItDown conversion failed: {error_message}",
                file_path=file_path,
                markitdown_error_type="generic",
                original_exception=original_exception,
                error_code="MARKITDOWN_GENERIC_ERROR"
            )


class ConversionTimeoutError(UnrecoverableError):
    """Conversion timeout error"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 timeout_seconds: Optional[float] = None,
                 error_code: str = "CONVERSION_TIMEOUT"):
        details = {"timeout_seconds": timeout_seconds}
        super().__init__(message, file_path, error_code, details)
        self.timeout_seconds = timeout_seconds


class ConversionMemoryError(RecoverableError):
    """Memory-related conversion errors"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 memory_usage_mb: Optional[float] = None,
                 error_code: str = "CONVERSION_MEMORY_ERROR"):
        details = {"memory_usage_mb": memory_usage_mb}
        
        recovery_suggestions = [
            "Try converting file in smaller chunks",
            "Close other applications to free memory",
            "Use streaming conversion method for large files"
        ]
        
        super().__init__(message, file_path, recovery_suggestions, error_code, details)
        self.memory_usage_mb = memory_usage_mb


class UnsupportedFileTypeError(UnrecoverableError):
    """Unsupported file type error"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 file_extension: Optional[str] = None,
                 supported_types: Optional[List[str]] = None,
                 error_code: str = "UNSUPPORTED_FILE_TYPE"):
        details = {
            "file_extension": file_extension,
            "supported_types": supported_types or []
        }
        super().__init__(message, file_path, error_code, details)
        self.file_extension = file_extension
        self.supported_types = supported_types or []


class ValidationFailedError(RecoverableError):
    """Document validation failed error"""
    
    def __init__(self, message: str, file_path: Optional[Path] = None,
                 validation_issues: Optional[List[Dict[str, Any]]] = None,
                 error_code: str = "VALIDATION_FAILED"):
        details = {"validation_issues": validation_issues or []}
        
        recovery_suggestions = [
            "Fix document validation issues before conversion",
            "Use force conversion mode to bypass validation",
            "Try alternative validation method"
        ]
        
        super().__init__(message, file_path, recovery_suggestions, error_code, details)
        self.validation_issues = validation_issues or []


def categorize_exception(exception: Exception, file_path: Optional[Path] = None) -> ConversionError:
    """
    Categorize generic exceptions into specific ConversionError types
    
    Args:
        exception: Original exception
        file_path: Optional file path for context
        
    Returns:
        Categorized ConversionError
    """
    error_message = str(exception)
    exception_type = type(exception).__name__
    
    # Font-related errors
    if "FontBBox" in error_message or "font descriptor" in error_message.lower():
        return FontDescriptorError.from_markitdown_warning(error_message, file_path)
    
    # Memory errors
    if isinstance(exception, MemoryError) or "memory" in error_message.lower():
        return ConversionMemoryError(
            message=f"Memory error during conversion: {error_message}",
            file_path=file_path
        )
    
    # Timeout errors  
    if isinstance(exception, TimeoutError) or "timeout" in error_message.lower():
        return ConversionTimeoutError(
            message=f"Conversion timed out: {error_message}",
            file_path=file_path
        )
    
    # File system errors
    if isinstance(exception, FileNotFoundError):
        return UnrecoverableError(
            message=f"File not found: {error_message}",
            file_path=file_path,
            error_code="FILE_NOT_FOUND"
        )
    
    if isinstance(exception, PermissionError):
        return RecoverableError(
            message=f"Permission denied: {error_message}",
            file_path=file_path,
            recovery_suggestions=["Check file permissions", "Run with administrator privileges"],
            error_code="PERMISSION_DENIED"
        )
    
    # PDF-related errors
    if "pdf" in error_message.lower() or exception_type in ["PdfReadError", "PdfStreamError"]:
        return PDFParsingError(
            message=f"PDF parsing error: {error_message}",
            file_path=file_path,
            pdf_error_type=exception_type.lower()
        )
    
    # MarkItDown-related errors
    if "markitdown" in error_message.lower():
        return MarkItDownError.wrap_exception(exception, file_path)
    
    # Generic conversion error
    return RecoverableError(
        message=f"Conversion failed: {error_message}",
        file_path=file_path,
        recovery_suggestions=["Retry conversion", "Check file integrity"],
        error_code="GENERIC_CONVERSION_ERROR",
        details={"original_exception_type": exception_type}
    )
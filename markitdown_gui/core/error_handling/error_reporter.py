"""
Error Reporter

Comprehensive error reporting system with user-friendly messages,
technical details, and integration with PyQt6 UI components.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
import json

from ..models import FileInfo, ConversionResult
from .conversion_errors import ConversionError, FontDescriptorError, PDFParsingError


class ErrorSeverity(Enum):
    """Error severity levels for reporting"""
    INFO = "info"           # Informational messages
    WARNING = "warning"     # Warning messages  
    ERROR = "error"         # Error messages
    CRITICAL = "critical"   # Critical errors that stop processing


@dataclass
class ErrorReport:
    """Comprehensive error report"""
    severity: ErrorSeverity
    title: str
    message: str
    file_path: Optional[Path] = None
    error_code: Optional[str] = None
    technical_details: Optional[Dict[str, Any]] = None
    user_message: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "file_path": str(self.file_path) if self.file_path else None,
            "error_code": self.error_code,
            "technical_details": self.technical_details,
            "user_message": self.user_message,
            "recovery_suggestions": self.recovery_suggestions,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert report to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class ErrorReporter:
    """Error reporting manager with user-friendly messaging"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        
        # Error report history
        self._reports: List[ErrorReport] = []
        self._max_reports = 1000  # Keep last 1000 reports
        
        # UI callback for error notifications
        self._error_callback: Optional[Callable[[ErrorReport], None]] = None
        
        # Error message templates
        self._message_templates = self._initialize_message_templates()
    
    def _initialize_message_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize user-friendly error message templates"""
        return {
            "FontDescriptorError": {
                "title": "PDF Font Issue",
                "user_message": (
                    "This PDF file contains font formatting issues that prevent proper conversion. "
                    "The document can still be converted using basic text extraction, but some "
                    "formatting may be lost."
                ),
                "recovery_suggestions": [
                    "Use the 'Basic Text Extraction' option for this PDF",
                    "Try opening the PDF in a different application and saving it again",
                    "Consider using OCR-based conversion if the document is scanned"
                ]
            },
            "PDFParsingError": {
                "title": "PDF Reading Error",
                "user_message": (
                    "There was a problem reading this PDF file. The file may be corrupted, "
                    "password-protected, or use an unsupported PDF format."
                ),
                "recovery_suggestions": [
                    "Check if the PDF requires a password to open",
                    "Try opening the PDF in a PDF viewer to verify it's not corrupted",
                    "Save the PDF from another application to create a clean copy"
                ]
            },
            "ConversionMemoryError": {
                "title": "Memory Limit Exceeded",
                "user_message": (
                    "This file is too large or complex to convert with the available memory. "
                    "Try converting smaller files or close other applications to free up memory."
                ),
                "recovery_suggestions": [
                    "Close other applications to free up memory",
                    "Try converting one file at a time instead of batches",
                    "Split large documents into smaller sections before conversion"
                ]
            },
            "ConversionTimeoutError": {
                "title": "Conversion Timeout",
                "user_message": (
                    "The conversion took too long and was stopped to prevent system freezing. "
                    "This usually happens with very large or complex documents."
                ),
                "recovery_suggestions": [
                    "Try converting the document in smaller sections",
                    "Close other applications that might be using system resources",
                    "Check if the document contains complex graphics or embedded objects"
                ]
            },
            "UnsupportedFileTypeError": {
                "title": "Unsupported File Type",
                "user_message": (
                    "This file type is not supported for conversion. Only documents, PDFs, "
                    "images, and other supported formats can be converted to Markdown."
                ),
                "recovery_suggestions": [
                    "Check the list of supported file formats",
                    "Try converting the file to a supported format first",
                    "Use a different conversion tool for this file type"
                ]
            },
            "ValidationFailedError": {
                "title": "Document Validation Failed",
                "user_message": (
                    "The document has validation issues that may affect conversion quality. "
                    "You can try to convert anyway, but the results may not be optimal."
                ),
                "recovery_suggestions": [
                    "Try the 'Force Conversion' option to bypass validation",
                    "Check the document for corruption or unusual formatting",
                    "Use document repair tools if available"
                ]
            },
            "MarkItDownError": {
                "title": "Conversion Library Error", 
                "user_message": (
                    "The conversion library encountered an error processing this document. "
                    "This may be due to unusual document formatting or structure."
                ),
                "recovery_suggestions": [
                    "Try using a fallback conversion method",
                    "Check if the document opens correctly in its native application",
                    "Try saving the document in a different format before conversion"
                ]
            }
        }
    
    def set_error_callback(self, callback: Callable[[ErrorReport], None]):
        """Set callback function for error notifications"""
        self._error_callback = callback
        self.logger.info("Error notification callback set")
    
    def report_error(self, error: Exception, file_info: Optional[FileInfo] = None,
                    context: Optional[str] = None) -> ErrorReport:
        """
        Create and report an error
        
        Args:
            error: The exception to report
            file_info: Optional file information
            context: Optional context information
            
        Returns:
            ErrorReport instance
        """
        # Determine severity
        severity = self._determine_severity(error)
        
        # Get error details
        error_type = type(error).__name__
        file_path = file_info.path if file_info else None
        
        # Get message template
        template = self._message_templates.get(error_type, {})
        
        # Create report
        report = ErrorReport(
            severity=severity,
            title=template.get("title", f"{error_type}"),
            message=str(error),
            file_path=file_path,
            error_code=getattr(error, "error_code", None),
            technical_details=self._extract_technical_details(error, file_info, context),
            user_message=template.get("user_message"),
            recovery_suggestions=template.get("recovery_suggestions", [])
        )
        
        # Enhanced recovery suggestions for specific errors
        if isinstance(error, ConversionError) and hasattr(error, "recovery_suggestions"):
            report.recovery_suggestions.extend(error.recovery_suggestions)
        
        # Store report
        self._add_report(report)
        
        # Log the error
        self._log_error(report)
        
        # Notify UI if callback is set
        if self._error_callback:
            try:
                self._error_callback(report)
            except Exception as e:
                self.logger.error(f"Error callback failed: {e}")
        
        return report
    
    def report_conversion_result(self, result: ConversionResult) -> Optional[ErrorReport]:
        """Report conversion result if it contains errors"""
        if result.status.is_error and result.error_message:
            # Create a generic conversion error
            error = ConversionError(
                result.error_message,
                result.file_info.path,
                error_code="CONVERSION_RESULT_ERROR"
            )
            return self.report_error(error, result.file_info, "conversion_result")
        return None
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type"""
        if isinstance(error, ConversionError):
            if not error.is_recoverable:
                return ErrorSeverity.ERROR
            else:
                return ErrorSeverity.WARNING
        elif isinstance(error, (MemoryError, SystemError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, (FileNotFoundError, PermissionError)):
            return ErrorSeverity.ERROR
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorSeverity.WARNING
        else:
            return ErrorSeverity.ERROR
    
    def _extract_technical_details(self, error: Exception, file_info: Optional[FileInfo] = None,
                                  context: Optional[str] = None) -> Dict[str, Any]:
        """Extract technical details from error"""
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        # Add file information
        if file_info:
            details["file_info"] = {
                "name": file_info.name,
                "path": str(file_info.path),
                "size": file_info.size,
                "type": file_info.file_type.value,
                "modified": file_info.modified_time.isoformat()
            }
        
        # Add ConversionError specific details
        if isinstance(error, ConversionError):
            if hasattr(error, "details") and error.details:
                details["conversion_details"] = error.details
        
        # Add FontDescriptorError specific details
        if isinstance(error, FontDescriptorError):
            details["font_issues"] = error.font_issues
            details["bbox_value"] = error.bbox_value
            details["font_name"] = error.font_name
        
        # Add PDFParsingError specific details
        if isinstance(error, PDFParsingError):
            details["pdf_error_type"] = error.pdf_error_type
            details["page_number"] = error.page_number
        
        return details
    
    def _add_report(self, report: ErrorReport):
        """Add report to history"""
        self._reports.append(report)
        
        # Maintain maximum number of reports
        if len(self._reports) > self._max_reports:
            self._reports = self._reports[-self._max_reports:]
    
    def _log_error(self, report: ErrorReport):
        """Log error report"""
        log_level = {
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[report.severity]
        
        log_message = f"[{report.error_code or 'ERROR'}] {report.title}: {report.message}"
        if report.file_path:
            log_message += f" (File: {report.file_path})"
        
        self.logger.log(log_level, log_message)
        
        # Write to log file if specified
        if self.log_file:
            self._write_to_log_file(report)
    
    def _write_to_log_file(self, report: ErrorReport):
        """Write error report to log file"""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n--- Error Report {report.timestamp.isoformat()} ---\n")
                f.write(report.to_json())
                f.write("\n" + "="*80 + "\n")
                
        except Exception as e:
            self.logger.error(f"Failed to write to log file: {e}")
    
    def get_reports(self, severity: Optional[ErrorSeverity] = None, 
                   last_n: Optional[int] = None) -> List[ErrorReport]:
        """Get error reports with optional filtering"""
        reports = self._reports
        
        # Filter by severity
        if severity:
            reports = [r for r in reports if r.severity == severity]
        
        # Limit to last N reports
        if last_n:
            reports = reports[-last_n:]
        
        return reports
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        total_reports = len(self._reports)
        
        if total_reports == 0:
            return {
                "total_reports": 0,
                "by_severity": {},
                "by_error_type": {},
                "recent_errors": []
            }
        
        # Count by severity
        by_severity = {}
        for severity in ErrorSeverity:
            count = len([r for r in self._reports if r.severity == severity])
            by_severity[severity.value] = count
        
        # Count by error type
        by_error_type = {}
        for report in self._reports:
            error_type = report.technical_details.get("error_type", "Unknown")
            by_error_type[error_type] = by_error_type.get(error_type, 0) + 1
        
        # Recent errors (last 10)
        recent_errors = [
            {
                "timestamp": r.timestamp.isoformat(),
                "severity": r.severity.value,
                "title": r.title,
                "file_path": str(r.file_path) if r.file_path else None
            }
            for r in self._reports[-10:]
        ]
        
        return {
            "total_reports": total_reports,
            "by_severity": by_severity,
            "by_error_type": by_error_type,
            "recent_errors": recent_errors
        }
    
    def clear_reports(self, older_than_hours: Optional[int] = None):
        """Clear error reports"""
        if older_than_hours:
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            self._reports = [
                r for r in self._reports 
                if r.timestamp.timestamp() > cutoff_time
            ]
        else:
            self._reports.clear()
        
        self.logger.info(f"Cleared error reports {'older than {older_than_hours} hours' if older_than_hours else ''}")
    
    def export_reports(self, output_path: Path, format: str = "json") -> bool:
        """Export error reports to file"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                reports_data = [report.to_dict() for report in self._reports]
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(reports_data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("Error Reports Export\n")
                    f.write("="*50 + "\n\n")
                    
                    for report in self._reports:
                        f.write(f"[{report.severity.value.upper()}] {report.title}\n")
                        f.write(f"Time: {report.timestamp.isoformat()}\n")
                        f.write(f"Message: {report.message}\n")
                        if report.file_path:
                            f.write(f"File: {report.file_path}\n")
                        if report.recovery_suggestions:
                            f.write("Recovery Suggestions:\n")
                            for suggestion in report.recovery_suggestions:
                                f.write(f"  - {suggestion}\n")
                        f.write("\n" + "-"*80 + "\n\n")
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            self.logger.info(f"Exported {len(self._reports)} reports to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export reports: {e}")
            return False
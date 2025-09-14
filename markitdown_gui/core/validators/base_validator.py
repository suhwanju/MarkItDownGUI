"""
Base Document Validator

Foundation class for document validation with comprehensive error handling
and standardized validation patterns.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import os

from ..exceptions import ValidationError as BaseValidationError


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"    # Blocks conversion
    WARNING = "warning"      # May affect quality
    INFO = "info"           # Informational only


class ValidationLevel(Enum):
    """Validation depth levels"""
    BASIC = "basic"         # Essential checks only
    STANDARD = "standard"   # Comprehensive validation
    STRICT = "strict"       # Maximum validation depth


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    severity: ValidationSeverity
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation result container"""
    is_valid: bool
    issues: List[ValidationIssue]
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if validation has critical issues"""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get critical issues only"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get warning issues only"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]


class ValidationError(BaseValidationError):
    """Validation specific error"""
    
    def __init__(self, message: str, validation_result: Optional[ValidationResult] = None, 
                 error_code: Optional[str] = None):
        super().__init__(message, error_code)
        self.validation_result = validation_result


class BaseValidator(ABC):
    """Base class for document validators"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._issues: List[ValidationIssue] = []
    
    @abstractmethod
    def validate(self, file_path: Path) -> ValidationResult:
        """
        Validate document
        
        Args:
            file_path: Path to document to validate
            
        Returns:
            ValidationResult with issues and metadata
        """
        pass
    
    @abstractmethod
    def can_validate(self, file_path: Path) -> bool:
        """
        Check if this validator can handle the file type
        
        Args:
            file_path: Path to check
            
        Returns:
            True if validator can handle file type
        """
        pass
    
    def _add_issue(self, severity: ValidationSeverity, code: str, message: str,
                   details: Optional[Dict[str, Any]] = None, location: Optional[str] = None,
                   suggestion: Optional[str] = None):
        """Add validation issue"""
        issue = ValidationIssue(
            severity=severity,
            code=code,
            message=message,
            details=details,
            location=location,
            suggestion=suggestion
        )
        self._issues.append(issue)
        
        # Log the issue
        log_level = {
            ValidationSeverity.CRITICAL: logging.ERROR,
            ValidationSeverity.WARNING: logging.WARNING,
            ValidationSeverity.INFO: logging.INFO
        }[severity]
        
        self.logger.log(log_level, f"[{code}] {message}")
    
    def _clear_issues(self):
        """Clear accumulated issues"""
        self._issues.clear()
    
    @property
    def issues(self) -> List[ValidationIssue]:
        """Get accumulated validation issues"""
        return self._issues
    
    def _create_result(self, is_valid: bool, metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Create validation result with accumulated issues"""
        return ValidationResult(
            is_valid=is_valid and not any(issue.severity == ValidationSeverity.CRITICAL for issue in self._issues),
            issues=self._issues.copy(),
            metadata=metadata or {}
        )
    
    def _validate_file_exists(self, file_path: Path) -> bool:
        """Basic file existence validation"""
        if not file_path.exists():
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "FILE_NOT_FOUND",
                f"File does not exist: {file_path}",
                location=str(file_path)
            )
            return False
        
        if not file_path.is_file():
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "NOT_A_FILE", 
                f"Path is not a file: {file_path}",
                location=str(file_path)
            )
            return False
        
        if file_path.stat().st_size == 0:
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "EMPTY_FILE",
                f"File is empty: {file_path}",
                location=str(file_path),
                suggestion="Ensure the file contains valid content"
            )
            return False
        
        return True
    
    def _validate_file_permissions(self, file_path: Path) -> bool:
        """Basic file permission validation"""
        try:
            if not os.access(file_path, os.R_OK):
                self._add_issue(
                    ValidationSeverity.CRITICAL,
                    "FILE_NOT_READABLE",
                    f"File is not readable: {file_path}",
                    location=str(file_path),
                    suggestion="Check file permissions"
                )
                return False
        except OSError as e:
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "PERMISSION_ERROR",
                f"Permission error accessing file: {e}",
                location=str(file_path),
                details={"os_error": str(e)}
            )
            return False
        
        return True
    
    def _validate_file_size(self, file_path: Path, max_size_mb: int = 100) -> bool:
        """Basic file size validation"""
        max_size_bytes = max_size_mb * 1024 * 1024
        file_size = file_path.stat().st_size
        
        if file_size > max_size_bytes:
            self._add_issue(
                ValidationSeverity.WARNING,
                "FILE_TOO_LARGE",
                f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds recommended maximum ({max_size_mb}MB)",
                location=str(file_path),
                details={"file_size_bytes": file_size, "max_size_bytes": max_size_bytes},
                suggestion=f"Consider files smaller than {max_size_mb}MB for optimal performance"
            )
            return False
        
        return True
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return []
    
    def get_validator_info(self) -> Dict[str, Any]:
        """Get information about this validator"""
        return {
            "name": self.__class__.__name__,
            "validation_level": self.validation_level.value,
            "supported_extensions": self.get_supported_extensions(),
            "can_fix_issues": getattr(self, 'can_fix_issues', False)
        }
"""
Document Validator Factory

Manages multiple document validators and provides unified validation interface.
Routes documents to appropriate validators based on file type.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Union
import logging

from .base_validator import BaseValidator, ValidationResult, ValidationLevel
from .pdf_validator import PDFValidator, PDFValidationResult
from ..exceptions import ValidationError


class DocumentValidator:
    """Document validation orchestrator"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        
        # Initialize available validators
        self._validators: Dict[str, BaseValidator] = {}
        self._register_validators()
    
    def _register_validators(self):
        """Register all available validators"""
        # PDF validator
        pdf_validator = PDFValidator(self.validation_level)
        for ext in pdf_validator.get_supported_extensions():
            self._validators[ext.lower()] = pdf_validator
        
        self.logger.info(f"Registered validators for extensions: {list(self._validators.keys())}")
    
    def can_validate(self, file_path: Path) -> bool:
        """Check if any validator can handle this file type"""
        extension = file_path.suffix.lower()
        return extension in self._validators
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions"""
        return list(self._validators.keys())
    
    def validate(self, file_path: Path) -> ValidationResult:
        """
        Validate document with appropriate validator
        
        Args:
            file_path: Path to document to validate
            
        Returns:
            ValidationResult with validation details
            
        Raises:
            ValidationError: If no validator available for file type
        """
        extension = file_path.suffix.lower()
        
        if extension not in self._validators:
            raise ValidationError(
                f"No validator available for file type: {extension}",
                error_code="UNSUPPORTED_FILE_TYPE"
            )
        
        validator = self._validators[extension]
        
        try:
            result = validator.validate(file_path)
            self.logger.debug(f"Validation completed for {file_path}: {'PASS' if result.is_valid else 'FAIL'}")
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed for {file_path}: {e}")
            raise ValidationError(
                f"Validation failed: {str(e)}",
                error_code="VALIDATION_FAILED"
            ) from e
    
    def validate_multiple(self, file_paths: List[Path]) -> Dict[Path, ValidationResult]:
        """
        Validate multiple documents
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                results[file_path] = self.validate(file_path)
            except Exception as e:
                self.logger.error(f"Failed to validate {file_path}: {e}")
                # Create a failed result
                results[file_path] = ValidationResult(
                    is_valid=False,
                    issues=[],
                    metadata={"validation_error": str(e)}
                )
        
        return results
    
    def get_validator_for_file(self, file_path: Path) -> Optional[BaseValidator]:
        """Get the specific validator for a file type"""
        extension = file_path.suffix.lower()
        return self._validators.get(extension)
    
    def set_validation_level(self, level: ValidationLevel):
        """Update validation level for all validators"""
        self.validation_level = level
        
        # Update existing validators
        for validator in set(self._validators.values()):
            validator.validation_level = level
        
        self.logger.info(f"Updated validation level to {level.value}")
    
    def get_validation_summary(self, results: Dict[Path, ValidationResult]) -> Dict[str, Any]:
        """
        Generate summary statistics from validation results
        
        Args:
            results: Dictionary of validation results
            
        Returns:
            Summary statistics
        """
        total_files = len(results)
        valid_files = sum(1 for result in results.values() if result.is_valid)
        invalid_files = total_files - valid_files
        
        # Count issues by severity
        critical_issues = 0
        warnings = 0
        info_issues = 0
        
        for result in results.values():
            critical_issues += len(result.critical_issues)
            warnings += len(result.warnings)
            info_issues += len([issue for issue in result.issues 
                              if issue.severity.value == "info"])
        
        # File type breakdown
        file_types = {}
        for file_path in results.keys():
            ext = file_path.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "validation_rate": (valid_files / total_files) * 100 if total_files > 0 else 0,
            "issues": {
                "critical": critical_issues,
                "warnings": warnings,
                "info": info_issues,
                "total": critical_issues + warnings + info_issues
            },
            "file_types": file_types,
            "validation_level": self.validation_level.value
        }
    
    def recommend_conversion_order(self, file_paths: List[Path]) -> List[Path]:
        """
        Recommend conversion order based on validation results
        
        Args:
            file_paths: Files to order
            
        Returns:
            Ordered list of files (safest first)
        """
        if not file_paths:
            return []
        
        # Validate all files first
        results = self.validate_multiple(file_paths)
        
        # Score files based on validation results (lower score = safer)
        file_scores = []
        
        for file_path, result in results.items():
            score = 0
            
            # Base score for validity
            if not result.is_valid:
                score += 100
            
            # Add score for issues
            score += len(result.critical_issues) * 10
            score += len(result.warnings) * 2
            
            # PDF-specific scoring
            if isinstance(result, PDFValidationResult) and result.font_issues:
                score += len(result.font_issues) * 5
            
            file_scores.append((score, file_path))
        
        # Sort by score (ascending - safest first)
        file_scores.sort(key=lambda x: x[0])
        
        return [file_path for _, file_path in file_scores]
    
    def get_validator_info(self) -> Dict[str, Any]:
        """Get information about all registered validators"""
        info = {
            "validation_level": self.validation_level.value,
            "supported_extensions": self.get_supported_extensions(),
            "validators": {}
        }
        
        # Get unique validators
        unique_validators = set(self._validators.values())
        
        for validator in unique_validators:
            validator_info = validator.get_validator_info()
            info["validators"][validator_info["name"]] = validator_info
        
        return info
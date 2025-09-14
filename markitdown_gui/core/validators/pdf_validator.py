"""
PDF Document Validator

Comprehensive PDF validation with specific focus on FontBBox descriptor issues
and other common PDF parsing problems that affect MarkItDown conversion.
"""

import io
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from .base_validator import (
    BaseValidator, ValidationResult, ValidationIssue, 
    ValidationSeverity, ValidationLevel
)
from ..exceptions import ValidationError


@dataclass
class FontDescriptorIssue:
    """Font descriptor specific issue"""
    font_name: str
    issue_type: str
    bbox_value: Optional[str] = None
    page_number: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


@dataclass 
class PDFValidationResult(ValidationResult):
    """PDF-specific validation result"""
    page_count: Optional[int] = None
    has_text: bool = False
    has_images: bool = False
    font_issues: List[FontDescriptorIssue] = None
    pdf_version: Optional[str] = None
    is_encrypted: bool = False
    
    def __post_init__(self):
        if self.font_issues is None:
            self.font_issues = []


class FontDescriptorError(ValidationError):
    """Font descriptor specific error"""
    
    def __init__(self, message: str, font_issues: List[FontDescriptorIssue], 
                 error_code: str = "FONT_DESCRIPTOR_ERROR"):
        super().__init__(message, error_code=error_code)
        self.font_issues = font_issues


class PDFValidator(BaseValidator):
    """PDF document validator with FontBBox error detection"""
    
    # Common problematic FontBBox patterns
    PROBLEMATIC_BBOX_PATTERNS = [
        r'FontBBox\s*\[\s*None\s*None\s*None\s*None\s*\]',
        r'FontBBox\s*\[\s*null\s*null\s*null\s*null\s*\]', 
        r'FontBBox\s*\[\s*\]',
        r'FontBBox\s*None',
        r'FontBBox\s*null'
    ]
    
    # Font descriptor validation patterns
    FONT_BBOX_PATTERN = r'FontBBox\s*\[\s*([-+]?\d*\.?\d*)\s+([-+]?\d*\.?\d*)\s+([-+]?\d*\.?\d*)\s+([-+]?\d*\.?\d*)\s*\]'
    FONT_DESCRIPTOR_PATTERN = r'/FontDescriptor\s+\d+\s+\d+\s+R'
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        super().__init__(validation_level)
        self.logger = logging.getLogger(__name__)
        
        # Check available PDF libraries
        self._pdf_libraries = []
        if PYPDF2_AVAILABLE:
            self._pdf_libraries.append("PyPDF2")
        if PDFPLUMBER_AVAILABLE:
            self._pdf_libraries.append("pdfplumber")
            
        if not self._pdf_libraries:
            self.logger.warning("No PDF libraries available. PDF validation will be limited.")
    
    def can_validate(self, file_path: Path) -> bool:
        """Check if this validator can handle PDF files"""
        return file_path.suffix.lower() == '.pdf'
    
    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions"""
        return ['.pdf']
    
    def validate(self, file_path: Path) -> PDFValidationResult:
        """
        Comprehensive PDF validation with FontBBox error detection
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            PDFValidationResult with detailed validation information
        """
        self._clear_issues()
        
        # Basic file validation
        if not self._validate_file_exists(file_path):
            return self._create_pdf_result(False)
        
        if not self._validate_file_permissions(file_path):
            return self._create_pdf_result(False)
        
        if not self._validate_file_size(file_path):
            # File size issues are warnings, not critical
            pass
        
        # PDF-specific validation
        pdf_metadata = {}
        font_issues = []
        
        try:
            # Validate PDF header
            if not self._validate_pdf_header(file_path):
                return self._create_pdf_result(False, pdf_metadata, font_issues)
            
            # Validate PDF structure
            structure_valid, structure_metadata = self._validate_pdf_structure(file_path)
            pdf_metadata.update(structure_metadata)
            
            if not structure_valid and self.validation_level == ValidationLevel.STRICT:
                return self._create_pdf_result(False, pdf_metadata, font_issues)
            
            # Font descriptor validation (critical for MarkItDown)
            font_valid, detected_font_issues = self._validate_font_descriptors(file_path)
            font_issues.extend(detected_font_issues)
            
            if not font_valid:
                self._add_issue(
                    ValidationSeverity.CRITICAL,
                    "FONT_DESCRIPTOR_ISSUES",
                    f"PDF contains {len(detected_font_issues)} font descriptor issues that may cause conversion failures",
                    details={"font_issue_count": len(detected_font_issues)},
                    suggestion="Consider using a PDF repair tool or alternative conversion method"
                )
                return self._create_pdf_result(False, pdf_metadata, font_issues)
            
            # Additional validation based on level
            if self.validation_level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
                self._validate_pdf_content(file_path, pdf_metadata)
            
            if self.validation_level == ValidationLevel.STRICT:
                self._validate_pdf_advanced(file_path, pdf_metadata)
            
            # Determine overall validity
            is_valid = not self._has_critical_issues()
            
            return self._create_pdf_result(is_valid, pdf_metadata, font_issues)
            
        except Exception as e:
            self.logger.error(f"PDF validation failed: {e}")
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "VALIDATION_ERROR",
                f"PDF validation failed: {str(e)}",
                details={"exception_type": type(e).__name__, "exception_message": str(e)}
            )
            return self._create_pdf_result(False, pdf_metadata, font_issues)
    
    def _validate_pdf_header(self, file_path: Path) -> bool:
        """Validate PDF file header"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF-'):
                    self._add_issue(
                        ValidationSeverity.CRITICAL,
                        "INVALID_PDF_HEADER",
                        f"File does not have valid PDF header: {header[:20]}",
                        suggestion="Ensure file is a valid PDF document"
                    )
                    return False
                
                # Extract PDF version
                try:
                    version_line = f.readline().decode('utf-8', errors='ignore')
                    version_match = re.search(r'%PDF-(\d+\.\d+)', version_line)
                    if version_match:
                        version = version_match.group(1)
                        if float(version) < 1.3:
                            self._add_issue(
                                ValidationSeverity.WARNING,
                                "OLD_PDF_VERSION",
                                f"PDF version {version} is quite old and may have compatibility issues",
                                details={"pdf_version": version}
                            )
                except Exception:
                    pass  # Non-critical version detection failure
                
                return True
        except Exception as e:
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "HEADER_READ_ERROR",
                f"Cannot read PDF header: {str(e)}",
                details={"error": str(e)}
            )
            return False
    
    def _validate_pdf_structure(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Validate PDF internal structure"""
        metadata = {}
        
        if not self._pdf_libraries:
            self._add_issue(
                ValidationSeverity.WARNING,
                "NO_PDF_LIBRARY",
                "No PDF libraries available for detailed structure validation",
                suggestion="Install PyPDF2 or pdfplumber for comprehensive validation"
            )
            return True, metadata
        
        # Try PyPDF2 first
        if PYPDF2_AVAILABLE:
            try:
                return self._validate_with_pypdf2(file_path)
            except Exception as e:
                self.logger.debug(f"PyPDF2 validation failed: {e}")
        
        # Fallback to pdfplumber
        if PDFPLUMBER_AVAILABLE:
            try:
                return self._validate_with_pdfplumber(file_path)
            except Exception as e:
                self.logger.debug(f"pdfplumber validation failed: {e}")
        
        # Both failed
        self._add_issue(
            ValidationSeverity.WARNING,
            "STRUCTURE_VALIDATION_FAILED",
            "Could not validate PDF structure with available libraries",
            suggestion="PDF may have structural issues that prevent parsing"
        )
        return False, metadata
    
    def _validate_with_pypdf2(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Validate PDF using PyPDF2"""
        metadata = {}
        
        with open(file_path, 'rb') as f:
            try:
                reader = PyPDF2.PdfReader(f)
                
                # Check encryption
                if reader.is_encrypted:
                    metadata['is_encrypted'] = True
                    self._add_issue(
                        ValidationSeverity.WARNING,
                        "PDF_ENCRYPTED",
                        "PDF is encrypted and may require password for conversion",
                        suggestion="Provide password or decrypt PDF before conversion"
                    )
                
                # Get page count
                page_count = len(reader.pages)
                metadata['page_count'] = page_count
                
                if page_count == 0:
                    self._add_issue(
                        ValidationSeverity.CRITICAL,
                        "NO_PAGES",
                        "PDF contains no pages",
                        suggestion="Ensure PDF file is not corrupted"
                    )
                    return False, metadata
                
                # Check document info
                if reader.metadata:
                    metadata['has_metadata'] = True
                
                # Quick validation of first few pages
                pages_to_check = min(3, page_count)
                for i in range(pages_to_check):
                    try:
                        page = reader.pages[i]
                        # Try to extract text to validate page structure
                        page.extract_text()
                    except Exception as e:
                        self._add_issue(
                            ValidationSeverity.WARNING,
                            "PAGE_EXTRACTION_ERROR",
                            f"Error extracting content from page {i+1}: {str(e)}",
                            details={"page_number": i+1, "error": str(e)}
                        )
                
                return True, metadata
                
            except PyPDF2.errors.PdfReadError as e:
                self._add_issue(
                    ValidationSeverity.CRITICAL,
                    "PDF_READ_ERROR",
                    f"PDF read error: {str(e)}",
                    details={"error": str(e)},
                    suggestion="PDF may be corrupted or have structural issues"
                )
                return False, metadata
            except Exception as e:
                self._add_issue(
                    ValidationSeverity.WARNING,
                    "PYPDF2_ERROR",
                    f"PyPDF2 validation error: {str(e)}",
                    details={"error": str(e)}
                )
                return False, metadata
    
    def _validate_with_pdfplumber(self, file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Validate PDF using pdfplumber"""
        metadata = {}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                metadata['page_count'] = page_count
                
                if page_count == 0:
                    self._add_issue(
                        ValidationSeverity.CRITICAL,
                        "NO_PAGES",
                        "PDF contains no pages"
                    )
                    return False, metadata
                
                # Check document metadata
                if pdf.metadata:
                    metadata['has_metadata'] = True
                
                # Sample first few pages for content
                pages_to_check = min(3, page_count)
                has_text = False
                has_images = False
                
                for i in range(pages_to_check):
                    try:
                        page = pdf.pages[i]
                        
                        # Check for text
                        if page.extract_text().strip():
                            has_text = True
                        
                        # Check for images
                        if hasattr(page, 'images') and page.images:
                            has_images = True
                            
                    except Exception as e:
                        self._add_issue(
                            ValidationSeverity.WARNING,
                            "PAGE_ANALYSIS_ERROR",
                            f"Error analyzing page {i+1}: {str(e)}",
                            details={"page_number": i+1, "error": str(e)}
                        )
                
                metadata['has_text'] = has_text
                metadata['has_images'] = has_images
                
                if not has_text and not has_images:
                    self._add_issue(
                        ValidationSeverity.WARNING,
                        "NO_EXTRACTABLE_CONTENT",
                        "PDF appears to have no extractable text or images",
                        suggestion="PDF may be scanned images requiring OCR"
                    )
                
                return True, metadata
                
        except Exception as e:
            self._add_issue(
                ValidationSeverity.WARNING,
                "PDFPLUMBER_ERROR",
                f"pdfplumber validation error: {str(e)}",
                details={"error": str(e)}
            )
            return False, metadata
    
    def _validate_font_descriptors(self, file_path: Path) -> Tuple[bool, List[FontDescriptorIssue]]:
        """
        Validate font descriptors for FontBBox issues
        
        This is the critical validation for preventing MarkItDown FontBBox errors
        """
        font_issues = []
        
        try:
            # Read raw PDF content for font descriptor analysis
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
                
            # Convert to string for pattern matching (ignore encoding errors)
            pdf_text = pdf_content.decode('latin-1', errors='ignore')
            
            # Find all font descriptors
            font_descriptor_matches = re.finditer(self.FONT_DESCRIPTOR_PATTERN, pdf_text, re.IGNORECASE)
            font_descriptor_count = 0
            
            for match in font_descriptor_matches:
                font_descriptor_count += 1
                
                # Extract the font descriptor section
                start_pos = match.start()
                # Find the end of this object (simplified)
                end_match = re.search(r'endobj', pdf_text[start_pos:start_pos+2000])
                if end_match:
                    descriptor_section = pdf_text[start_pos:start_pos+end_match.end()]
                else:
                    descriptor_section = pdf_text[start_pos:start_pos+1000]  # Fallback
                
                # Check for problematic FontBBox patterns
                for pattern in self.PROBLEMATIC_BBOX_PATTERNS:
                    if re.search(pattern, descriptor_section, re.IGNORECASE):
                        issue = FontDescriptorIssue(
                            font_name=f"Font_{font_descriptor_count}",
                            issue_type="invalid_fontbbox",
                            bbox_value="None/null",
                            details={
                                "pattern_matched": pattern,
                                "descriptor_section": descriptor_section[:200] + "..." if len(descriptor_section) > 200 else descriptor_section
                            }
                        )
                        font_issues.append(issue)
            
            # Also check for valid FontBBox patterns and validate values
            bbox_matches = re.finditer(self.FONT_BBOX_PATTERN, pdf_text, re.IGNORECASE)
            
            for bbox_match in bbox_matches:
                try:
                    coords = [float(x) if x else 0.0 for x in bbox_match.groups()]
                    
                    # Validate FontBBox coordinates
                    if len(coords) != 4:
                        issue = FontDescriptorIssue(
                            font_name="Unknown",
                            issue_type="invalid_bbox_format",
                            bbox_value=bbox_match.group(0),
                            details={"coordinates": coords}
                        )
                        font_issues.append(issue)
                    elif any(abs(coord) > 10000 for coord in coords):
                        # Extremely large coordinates may indicate corruption
                        issue = FontDescriptorIssue(
                            font_name="Unknown", 
                            issue_type="suspicious_bbox_values",
                            bbox_value=bbox_match.group(0),
                            details={"coordinates": coords}
                        )
                        font_issues.append(issue)
                        
                except ValueError:
                    # Invalid float values in FontBBox
                    issue = FontDescriptorIssue(
                        font_name="Unknown",
                        issue_type="invalid_bbox_numbers",
                        bbox_value=bbox_match.group(0),
                        details={"raw_match": bbox_match.group(0)}
                    )
                    font_issues.append(issue)
            
            # Log findings
            if font_issues:
                self.logger.warning(f"Found {len(font_issues)} font descriptor issues in {file_path}")
                for issue in font_issues:
                    self.logger.debug(f"Font issue: {issue.issue_type} - {issue.bbox_value}")
            
            # Return validation result
            has_critical_font_issues = len(font_issues) > 0
            return not has_critical_font_issues, font_issues
            
        except Exception as e:
            self.logger.error(f"Font descriptor validation failed: {e}")
            self._add_issue(
                ValidationSeverity.WARNING,
                "FONT_VALIDATION_ERROR",
                f"Could not validate font descriptors: {str(e)}",
                details={"error": str(e)},
                suggestion="Font validation failed, but conversion may still work"
            )
            return True, font_issues  # Don't block conversion due to validation errors
    
    def _validate_pdf_content(self, file_path: Path, metadata: Dict[str, Any]):
        """Standard level content validation"""
        if self.validation_level == ValidationLevel.BASIC:
            return
        
        # Additional content validation
        # This can be extended based on specific needs
        pass
    
    def _validate_pdf_advanced(self, file_path: Path, metadata: Dict[str, Any]):
        """Strict level advanced validation"""
        if self.validation_level != ValidationLevel.STRICT:
            return
        
        # Advanced PDF validation
        # Can include detailed structural analysis, cross-reference table validation, etc.
        pass
    
    def _has_critical_issues(self) -> bool:
        """Check if there are critical issues"""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self._issues)
    
    def _create_pdf_result(self, is_valid: bool, metadata: Optional[Dict[str, Any]] = None,
                          font_issues: Optional[List[FontDescriptorIssue]] = None) -> PDFValidationResult:
        """Create PDF-specific validation result"""
        metadata = metadata or {}
        font_issues = font_issues or []
        
        return PDFValidationResult(
            is_valid=is_valid and not self._has_critical_issues(),
            issues=self._issues.copy(),
            metadata=metadata,
            page_count=metadata.get('page_count'),
            has_text=metadata.get('has_text', False),
            has_images=metadata.get('has_images', False), 
            font_issues=font_issues,
            pdf_version=metadata.get('pdf_version'),
            is_encrypted=metadata.get('is_encrypted', False)
        )
    
    def get_font_issue_summary(self, result: PDFValidationResult) -> str:
        """Get human-readable summary of font issues"""
        if not result.font_issues:
            return "No font issues detected"
        
        issue_types = {}
        for issue in result.font_issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        summary_parts = []
        for issue_type, count in issue_types.items():
            readable_type = issue_type.replace('_', ' ').title()
            summary_parts.append(f"{count} {readable_type}")
        
        return f"Found {len(result.font_issues)} font issues: {', '.join(summary_parts)}"
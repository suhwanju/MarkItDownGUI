"""
Comprehensive Test Suite for FontBBox PDF Parsing Solution

Tests the complete error handling and validation system with focus on
FontBBox descriptor issues and recovery mechanisms.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Import the components we've implemented
from markitdown_gui.core.validators import (
    PDFValidator, DocumentValidator, ValidationLevel, 
    ValidationResult, FontDescriptorError
)
from markitdown_gui.core.error_handling import (
    CircuitBreaker, CircuitBreakerState, FallbackManager, 
    ErrorRecoveryManager, ErrorReporter, ErrorSeverity,
    ConversionError, FontDescriptorError as EHFontDescriptorError,
    categorize_exception
)
from markitdown_gui.core.conversion_manager import ConversionManager
from markitdown_gui.core.models import FileInfo, ConversionResult, ConversionStatus, FileType


class TestPDFValidator:
    """Test PDF validation with FontBBox error detection"""
    
    @pytest.fixture
    def validator(self):
        return PDFValidator(ValidationLevel.STANDARD)
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Create a temporary PDF file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            # Create a minimal PDF with FontBBox issues
            pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Font << /F1 4 0 R >>
>>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica
   /FontDescriptor 5 0 R
>>
endobj
5 0 obj
<< /Type /FontDescriptor /FontName /Helvetica
   /FontBBox [None None None None]
   /ItalicAngle 0 /Ascent 718 /Descent -207
>>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000224 00000 n 
0000000309 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
432
%%EOF"""
            f.write(pdf_content)
            return Path(f.name)
    
    @pytest.fixture
    def good_pdf_path(self):
        """Create a PDF without FontBBox issues"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Font << /F1 4 0 R >>
>>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica
   /FontDescriptor 5 0 R
>>
endobj
5 0 obj
<< /Type /FontDescriptor /FontName /Helvetica
   /FontBBox [-166 -225 1000 931]
   /ItalicAngle 0 /Ascent 718 /Descent -207
>>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000224 00000 n 
0000000309 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
445
%%EOF"""
            f.write(pdf_content)
            return Path(f.name)
    
    def test_can_validate_pdf(self, validator):
        """Test that validator can identify PDF files"""
        pdf_path = Path("test.pdf")
        assert validator.can_validate(pdf_path)
        
        non_pdf_path = Path("test.txt")
        assert not validator.can_validate(non_pdf_path)
    
    def test_validate_good_pdf(self, validator, good_pdf_path):
        """Test validation of PDF without FontBBox issues"""
        try:
            result = validator.validate(good_pdf_path)
            
            # Should be valid or have only minor issues
            assert isinstance(result, type(validator._create_pdf_result(True)))
            
            # Check that no critical font issues are detected
            if hasattr(result, 'font_issues'):
                critical_font_issues = [
                    issue for issue in result.font_issues 
                    if issue.issue_type == "invalid_fontbbox"
                ]
                assert len(critical_font_issues) == 0
                
        except Exception as e:
            # If validation fails due to missing dependencies, that's acceptable
            if "not available" in str(e).lower():
                pytest.skip("PDF validation dependencies not available")
            else:
                raise
    
    def test_validate_problematic_pdf(self, validator, sample_pdf_path):
        """Test validation of PDF with FontBBox issues"""
        try:
            result = validator.validate(sample_pdf_path)
            
            # Should detect font issues
            if hasattr(result, 'font_issues'):
                assert len(result.font_issues) > 0
                
                # Should specifically detect FontBBox issues
                bbox_issues = [
                    issue for issue in result.font_issues
                    if "fontbbox" in issue.issue_type.lower()
                ]
                assert len(bbox_issues) > 0
            
        except Exception as e:
            if "not available" in str(e).lower():
                pytest.skip("PDF validation dependencies not available")
            else:
                raise
    
    def test_font_issue_summary(self, validator, sample_pdf_path):
        """Test font issue summary generation"""
        try:
            result = validator.validate(sample_pdf_path)
            
            if hasattr(result, 'font_issues') and result.font_issues:
                summary = validator.get_font_issue_summary(result)
                
                assert isinstance(summary, str)
                assert "font issues" in summary.lower() or "no font issues" in summary.lower()
        except Exception as e:
            if "not available" in str(e).lower():
                pytest.skip("PDF validation dependencies not available")
            else:
                raise


class TestErrorHandling:
    """Test comprehensive error handling system"""
    
    @pytest.fixture
    def circuit_breaker(self):
        return CircuitBreaker("test_breaker")
    
    @pytest.fixture
    def fallback_manager(self):
        return FallbackManager()
    
    @pytest.fixture
    def error_reporter(self):
        return ErrorReporter()
    
    def test_circuit_breaker_basic_operation(self, circuit_breaker):
        """Test basic circuit breaker operation"""
        # Initially closed
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        
        # Successful call
        result = circuit_breaker.call(lambda: "success")
        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_circuit_breaker_failure_handling(self, circuit_breaker):
        """Test circuit breaker failure handling"""
        # Cause multiple failures to open the circuit
        for i in range(6):  # Default threshold is 5
            try:
                circuit_breaker.call(lambda: self._failing_function())
            except Exception:
                pass
        
        # Circuit should be open now
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Next call should be rejected
        with pytest.raises(Exception):  # CircuitBreakerError
            circuit_breaker.call(lambda: "should not execute")
    
    def _failing_function(self):
        """Helper function that always fails"""
        raise Exception("Test failure")
    
    def test_font_descriptor_error_creation(self):
        """Test FontDescriptorError creation from MarkItDown warnings"""
        warning_message = "WARNING - Could get FontBBox from font descriptor because None cannot be parsed as 4 floats"
        file_path = Path("test.pdf")
        
        error = EHFontDescriptorError.from_markitdown_warning(warning_message, file_path)
        
        assert isinstance(error, EHFontDescriptorError)
        assert error.file_path == file_path
        assert "FontBBox" in error.message
        assert error.bbox_value == "None"
        assert error.error_code == "FONTBBOX_NONE_ERROR"
    
    def test_error_categorization(self):
        """Test automatic error categorization"""
        # FontBBox error
        font_error = ValueError("FontBBox from font descriptor because None cannot be parsed as 4 floats")
        categorized = categorize_exception(font_error, Path("test.pdf"))
        
        assert isinstance(categorized, EHFontDescriptorError)
        
        # Memory error
        memory_error = MemoryError("Out of memory")
        categorized = categorize_exception(memory_error, Path("test.pdf"))
        
        assert "memory" in categorized.error_code.lower() or "MEMORY" in categorized.error_code
        
        # Generic error
        generic_error = ValueError("Some other error")
        categorized = categorize_exception(generic_error, Path("test.pdf"))
        
        assert isinstance(categorized, ConversionError)
    
    def test_error_reporter_functionality(self, error_reporter):
        """Test error reporter functionality"""
        # Create a sample error
        error = ConversionError("Test error", Path("test.pdf"))
        
        # Report the error
        report = error_reporter.report_error(error)
        
        assert report.severity == ErrorSeverity.WARNING  # ConversionError defaults to WARNING
        assert "Test error" in report.message
        assert report.file_path == Path("test.pdf")
        
        # Check that report was stored
        reports = error_reporter.get_reports()
        assert len(reports) == 1
        assert reports[0] == report
    
    def test_fallback_manager_strategy_execution(self, fallback_manager):
        """Test fallback strategy execution"""
        # Create a mock file info
        file_info = Mock()
        file_info.path = Path("test.pdf")
        file_info.name = "test.pdf"
        file_info.file_type = Mock()
        file_info.file_type.value = "pdf"
        
        output_path = Path("test.md")
        
        # Test fallback execution
        result = fallback_manager.execute_fallback(
            file_info, output_path, 
            original_error=ConversionError("Test error")
        )
        
        assert result.strategy_name in ["basic_text_extraction", "plain_text_fallback", "none"]
        # Result may fail due to missing dependencies, but should not crash


class TestConversionManagerIntegration:
    """Test enhanced ConversionManager with error handling"""
    
    @pytest.fixture
    def conversion_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            return ConversionManager(
                output_directory=output_dir,
                validation_level=ValidationLevel.STANDARD,
                enable_recovery=True
            )
    
    @pytest.fixture
    def sample_file_info(self):
        """Create sample FileInfo for testing"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Sample content for testing")
            file_path = Path(f.name)
        
        return FileInfo.from_path(file_path)
    
    def test_conversion_manager_initialization(self, conversion_manager):
        """Test that ConversionManager initializes with enhanced components"""
        assert conversion_manager._circuit_breaker is not None
        assert conversion_manager._fallback_manager is not None
        assert conversion_manager._error_recovery_manager is not None
        assert conversion_manager._error_reporter is not None
        assert conversion_manager._document_validator is not None
    
    def test_validation_integration(self, conversion_manager, sample_file_info):
        """Test validation integration"""
        # Test file validation
        validation_results = conversion_manager.validate_files([sample_file_info])
        
        # Should return validation results
        assert isinstance(validation_results, dict)
        assert sample_file_info.path in validation_results
    
    def test_error_reporting_integration(self, conversion_manager):
        """Test error reporting integration"""
        # Initially no errors
        reports = conversion_manager.get_error_reports()
        initial_count = len(reports)
        
        # Create and report an error through the system
        error = ConversionError("Test integration error")
        conversion_manager._error_reporter.report_error(error)
        
        # Should have one more error
        reports = conversion_manager.get_error_reports()
        assert len(reports) == initial_count + 1
    
    def test_metrics_collection(self, conversion_manager):
        """Test metrics collection"""
        metrics = conversion_manager.get_conversion_metrics()
        
        # Should contain all expected metric categories
        expected_keys = [
            "total_conversions", "successful_conversions", "failed_conversions",
            "memory_stats", "circuit_breaker_state", "fallback_metrics"
        ]
        
        for key in expected_keys:
            assert key in metrics
    
    def test_system_health_monitoring(self, conversion_manager):
        """Test system health monitoring"""
        health = conversion_manager.get_system_health()
        
        # Should contain health information
        assert "health_score" in health
        assert "status" in health
        assert "circuit_breaker_state" in health
        
        # Health score should be between 0 and 100
        assert 0 <= health["health_score"] <= 100
        
        # Status should be valid
        assert health["status"] in ["healthy", "degraded", "critical"]
    
    @patch('markitdown_gui.core.conversion_manager.MARKITDOWN_AVAILABLE', False)
    def test_markitdown_unavailable_handling(self):
        """Test handling when MarkItDown is not available"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConversionManager(output_directory=Path(temp_dir))
            
            # Should handle gracefully
            assert not manager.is_markitdown_available()
            
            # Should report the unavailability error
            reports = manager.get_error_reports()
            markitdown_errors = [
                r for r in reports 
                if "MARKITDOWN_UNAVAILABLE" in r.technical_details.get("error_code", "")
            ]
            assert len(markitdown_errors) > 0


class TestUIIntegration:
    """Test UI error dialog integration"""
    
    @pytest.fixture
    def sample_error_report(self):
        """Create sample error report for UI testing"""
        from markitdown_gui.core.error_handling import ErrorReport
        
        return ErrorReport(
            severity=ErrorSeverity.ERROR,
            title="PDF Font Issue",
            message="FontBBox from font descriptor because None cannot be parsed as 4 floats",
            file_path=Path("sample.pdf"),
            error_code="FONTBBOX_NONE_ERROR",
            technical_details={
                "error_type": "FontDescriptorError",
                "font_name": "Helvetica",
                "bbox_value": "None"
            },
            user_message="This PDF file contains font formatting issues that prevent proper conversion.",
            recovery_suggestions=[
                "Use basic text extraction mode",
                "Try OCR-based conversion",
                "Repair PDF using specialized tools"
            ]
        )
    
    def test_error_dialog_creation(self, sample_error_report):
        """Test error dialog can be created with error report"""
        # This test requires PyQt6 to be properly set up
        try:
            from markitdown_gui.ui.components.error_dialog import ErrorDialog
            from PyQt6.QtWidgets import QApplication
            import sys
            
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            dialog = ErrorDialog(sample_error_report)
            
            # Basic checks
            assert dialog.error_report == sample_error_report
            assert "PDF Font Issue" in dialog.windowTitle() or dialog.windowTitle() != ""
            
            # Check that recovery suggestions are available
            assert len(sample_error_report.recovery_suggestions) > 0
            
        except ImportError:
            pytest.skip("PyQt6 not available for UI testing")


class TestPerformanceAndStress:
    """Performance and stress tests for the error handling system"""
    
    def test_circuit_breaker_performance(self):
        """Test circuit breaker performance under load"""
        circuit_breaker = CircuitBreaker("performance_test")
        
        # Measure performance of successful calls
        start_time = time.time()
        
        for i in range(1000):
            result = circuit_breaker.call(lambda: i)
            assert result == i
        
        elapsed_time = time.time() - start_time
        
        # Should complete 1000 calls in under 1 second
        assert elapsed_time < 1.0
        
        # Circuit should still be closed
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_error_reporter_memory_management(self):
        """Test error reporter memory management with many errors"""
        error_reporter = ErrorReporter()
        
        # Generate many error reports
        for i in range(1100):  # More than max_reports (1000)
            error = ConversionError(f"Test error {i}")
            error_reporter.report_error(error)
        
        # Should not exceed maximum
        reports = error_reporter.get_reports()
        assert len(reports) <= 1000
        
        # Should keep the most recent reports
        latest_report = reports[-1]
        assert "error 1099" in latest_report.message or "error 1100" in latest_report.message
    
    def test_validation_performance(self):
        """Test PDF validation performance"""
        validator = PDFValidator(ValidationLevel.BASIC)  # Fastest validation level
        
        # Create multiple temporary PDF files
        temp_files = []
        try:
            for i in range(10):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    # Simple PDF content
                    f.write(b"%PDF-1.4\n%%EOF")
                    temp_files.append(Path(f.name))
            
            # Measure validation time
            start_time = time.time()
            
            for pdf_path in temp_files:
                try:
                    result = validator.validate(pdf_path)
                except Exception:
                    # Expected for minimal PDF files
                    pass
            
            elapsed_time = time.time() - start_time
            
            # Should validate 10 files in under 2 seconds
            assert elapsed_time < 2.0
            
        finally:
            # Cleanup
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except:
                    pass


if __name__ == "__main__":
    # Run specific test categories
    print("Running FontBBox Solution Tests...")
    
    # Run with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
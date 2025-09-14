#!/usr/bin/env python3
"""
Test script to verify runtime error fixes
"""

import os
import tempfile
from pathlib import Path

def test_windowspath_readable_fix():
    """Test that the WindowsPath readable attribute error is fixed"""
    
    print("🔍 Testing WindowsPath readable fix...")
    
    try:
        # Import the validators module
        from markitdown_gui.core.validators import BaseValidator, ValidationResult, ValidationLevel
        from markitdown_gui.core.validators.base_validator import ValidationSeverity, ValidationIssue
        
        # Create a test validator instance
        class TestValidator(BaseValidator):
            def can_validate(self, file_path: Path) -> bool:
                return True
            
            def validate(self, file_path: Path) -> ValidationResult:
                # This will call _validate_file_permissions which had the readable() error
                self._validate_basic_file_properties(file_path)
                return ValidationResult(
                    is_valid=True,
                    issues=self.issues,
                    metadata={}
                )
        
        validator = TestValidator()
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_file = Path(f.name)
        
        try:
            # This should not raise the 'readable' attribute error anymore
            result = validator.validate(temp_file)
            print("✅ WindowsPath readable fix successful - no AttributeError")
            print(f"   - Validation result: {'PASS' if result.is_valid else 'FAIL'}")
            print(f"   - Issues count: {len(result.issues)}")
            
            return True
            
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
        
    except AttributeError as e:
        if "'WindowsPath' object has no attribute 'readable'" in str(e):
            print(f"❌ WindowsPath readable error still present: {e}")
            return False
        else:
            print(f"❌ Unexpected AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_validation_error_handling():
    """Test that validation errors are handled properly"""
    
    print("\n🔍 Testing validation error handling...")
    
    try:
        from markitdown_gui.core.validators import DocumentValidator, ValidationLevel, ValidationError
        
        # Create validator
        validator = DocumentValidator()
        
        # Test with non-existent file (should trigger validation error handling)
        non_existent_file = Path("definitely_does_not_exist.pdf")
        
        try:
            result = validator.validate(non_existent_file)
            print("❌ Expected validation error but got result")
            return False
        except ValidationError as ve:
            print("✅ ValidationError properly raised for non-existent file")
            print(f"   - Error message: {ve}")
            print(f"   - Error code: {ve.error_code}")
            return True
        except Exception as e:
            print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing validation error handling: {e}")
        return False


def test_os_access_functionality():
    """Test that os.access is working properly for file permissions"""
    
    print("\n🔍 Testing os.access functionality...")
    
    try:
        # Test with a readable file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            temp_file = Path(f.name)
        
        try:
            # Test os.access directly
            readable = os.access(temp_file, os.R_OK)
            print(f"✅ os.access working correctly")
            print(f"   - File readable: {readable}")
            
            # Test with the validator
            from markitdown_gui.core.validators.base_validator import BaseValidator
            
            class TestPermissionValidator(BaseValidator):
                def can_validate(self, file_path: Path) -> bool:
                    return True
                    
                def validate(self, file_path: Path) -> 'ValidationResult':
                    # This calls _validate_file_permissions internally
                    permission_ok = self._validate_file_permissions(file_path)
                    from markitdown_gui.core.validators import ValidationResult
                    return ValidationResult(
                        is_valid=permission_ok,
                        issues=self.issues,
                        metadata={}
                    )
            
            validator = TestPermissionValidator()
            result = validator.validate(temp_file)
            
            print(f"✅ File permission validation working")
            print(f"   - Permission validation passed: {result.is_valid}")
            
            return True
            
        finally:
            if temp_file.exists():
                temp_file.unlink()
        
    except Exception as e:
        print(f"❌ Error testing os.access functionality: {e}")
        return False


def test_imports_working():
    """Test that all required imports are working after fixes"""
    
    print("\n🔍 Testing all imports after fixes...")
    
    try:
        # Test all the imports that were previously failing
        from markitdown_gui.core.validators import (
            DocumentValidator,
            ValidationLevel, 
            ValidationResult,
            BaseValidator,
            ValidationError,
            PDFValidator
        )
        
        from markitdown_gui.core.error_handling import (
            CircuitBreakerError,
            FallbackResult,
            categorize_exception,
            ConversionError,
            FontDescriptorError
        )
        
        print("✅ All imports working correctly:")
        print("   - Validators: DocumentValidator, ValidationLevel, ValidationResult, BaseValidator, ValidationError, PDFValidator")
        print("   - Error handling: CircuitBreakerError, FallbackResult, categorize_exception, ConversionError, FontDescriptorError")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Runtime Error Fixes Test")
    print("=" * 60)
    
    test1_result = test_windowspath_readable_fix()
    test2_result = test_validation_error_handling()  
    test3_result = test_os_access_functionality()
    test4_result = test_imports_working()
    
    print("\n" + "=" * 60)
    if all([test1_result, test2_result, test3_result, test4_result]):
        print("🎉 ALL TESTS PASSED - Runtime errors are FIXED!")
        print("✅ WindowsPath readable error: RESOLVED")
        print("✅ Validation error handling: WORKING")
        print("✅ File permission checking: WORKING")
        print("✅ All imports: WORKING")
        print("\nThe application should now process files without the runtime errors.")
        print("FontBBox warnings may still appear in logs but will be handled gracefully.")
    else:
        print("❌ Some tests failed - additional fixes may be needed")
        if not test1_result:
            print("   - WindowsPath readable fix failed")
        if not test2_result:
            print("   - Validation error handling test failed")
        if not test3_result:
            print("   - os.access functionality test failed")
        if not test4_result:
            print("   - Import test failed")
    print("=" * 60)
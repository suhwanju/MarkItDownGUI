#!/usr/bin/env python3
"""
Simple test to verify the WindowsPath readable() fix
"""

import os
import tempfile
from pathlib import Path

def test_os_access_fix():
    """Test that os.access is now used instead of file_path.readable()"""
    
    print("🔍 Testing that os.access fix works...")
    
    try:
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_file = Path(f.name)
        
        try:
            # Test os.access directly (this should work)
            readable = os.access(temp_file, os.R_OK)
            print(f"✅ os.access working: file is readable = {readable}")
            
            # Now test importing the fixed base_validator
            from markitdown_gui.core.validators.base_validator import BaseValidator
            print("✅ BaseValidator imported successfully")
            
            # Create a simple test validator to test the _validate_file_permissions method
            class TestValidator(BaseValidator):
                def __init__(self):
                    super().__init__()
                
                def can_validate(self, file_path: Path) -> bool:
                    return True
                    
                def validate(self, file_path: Path):
                    # Call the method that was causing the error
                    result = self._validate_file_permissions(file_path)
                    print(f"✅ _validate_file_permissions executed successfully: {result}")
                    return self._create_result(True)
            
            validator = TestValidator()
            result = validator.validate(temp_file)
            
            print("✅ Validation completed without AttributeError")
            print(f"   - Result type: {type(result).__name__}")
            
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
            print(f"❌ Other AttributeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_direct_os_access():
    """Test os.access functionality directly"""
    
    print("\n🔍 Testing os.access functionality directly...")
    
    try:
        # Test with current working directory (should be readable)
        current_dir = Path.cwd()
        readable = os.access(current_dir, os.R_OK)
        print(f"✅ Current directory readable: {readable}")
        
        # Test with a non-existent file (should be False)
        non_existent = Path("definitely_does_not_exist_12345.txt")
        readable = os.access(non_existent, os.R_OK)
        print(f"✅ Non-existent file readable: {readable}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing os.access: {e}")
        return False


def test_validator_import():
    """Test that validators can be imported after the fix"""
    
    print("\n🔍 Testing validator imports...")
    
    try:
        from markitdown_gui.core.validators import (
            DocumentValidator,
            ValidationLevel,
            ValidationResult,
            BaseValidator
        )
        
        print("✅ All validator classes imported successfully")
        
        # Test creating instances
        doc_validator = DocumentValidator()
        print(f"✅ DocumentValidator created: {doc_validator}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("WindowsPath Readable Fix Test")  
    print("=" * 60)
    
    test1_result = test_os_access_fix()
    test2_result = test_direct_os_access()
    test3_result = test_validator_import()
    
    print("\n" + "=" * 60)
    if all([test1_result, test2_result, test3_result]):
        print("🎉 ALL TESTS PASSED - WindowsPath readable fix is working!")
        print("✅ os.access is working correctly")
        print("✅ BaseValidator._validate_file_permissions fixed")
        print("✅ All validator imports working")
        print("\nThe 'WindowsPath' object has no attribute 'readable' error should be resolved.")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
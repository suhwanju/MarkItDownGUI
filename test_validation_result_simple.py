#!/usr/bin/env python3
"""
Simple test script to verify ValidationResult import fix
"""

def test_validation_result_import():
    """Test that ValidationResult can be imported correctly"""
    
    print("🔍 Testing ValidationResult import...")
    
    try:
        # Test the exact import that was failing
        from markitdown_gui.core.validators import ValidationResult
        print("✅ ValidationResult imported successfully from validators module")
        
        # Test the import that conversion_manager.py uses
        from markitdown_gui.core.validators import DocumentValidator, ValidationLevel, ValidationResult
        print("✅ All required classes imported successfully (DocumentValidator, ValidationLevel, ValidationResult)")
        
        # Test creating a basic ValidationResult
        validation_result = ValidationResult(
            is_valid=True,
            issues=[],
            metadata=None
        )
        
        print(f"✅ ValidationResult instance created successfully")
        print(f"   - Type: {type(validation_result).__name__}")
        print(f"   - Is valid: {validation_result.is_valid}")
        print(f"   - Issues: {len(validation_result.issues)}")
        print(f"   - Has critical issues: {validation_result.has_critical_issues}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_all_validator_exports():
    """Test that all validator exports are working"""
    
    print("\n🔍 Testing all validator module exports...")
    
    try:
        from markitdown_gui.core.validators import (
            PDFValidator,
            PDFValidationResult,
            FontDescriptorError,
            DocumentValidator,
            ValidationLevel,
            BaseValidator,
            ValidationError,
            ValidationResult
        )
        
        print("✅ All validator classes exported correctly:")
        exports = {
            'PDFValidator': PDFValidator,
            'PDFValidationResult': PDFValidationResult,
            'FontDescriptorError': FontDescriptorError,
            'DocumentValidator': DocumentValidator,
            'ValidationLevel': ValidationLevel,
            'BaseValidator': BaseValidator,
            'ValidationError': ValidationError,
            'ValidationResult': ValidationResult
        }
        
        for name, cls in exports.items():
            print(f"   - {name}: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing validator exports: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ValidationResult Import Fix Test")
    print("=" * 60)
    
    test1_result = test_validation_result_import()
    test2_result = test_all_validator_exports()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED - ValidationResult import issue is FIXED!")
        print("✅ ValidationResult import: RESOLVED")
        print("✅ All validator exports: WORKING")
        print("\nThe application should now be able to import ValidationResult without errors.")
        print("The conversion_manager.py import should now work correctly.")
    else:
        print("❌ Some tests failed - issue needs further investigation")
    print("=" * 60)
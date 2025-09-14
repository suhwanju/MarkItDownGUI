#!/usr/bin/env python3
"""
Test script to verify ValidationResult import and functionality
"""

def test_validation_result_import():
    """Test that ValidationResult can be imported and used correctly"""
    
    print("🔍 Testing ValidationResult import and functionality...")
    
    try:
        # Test import from the validators module
        from markitdown_gui.core.validators import ValidationResult
        print("✅ ValidationResult imported successfully")
        
        # Test import alongside other validator classes
        from markitdown_gui.core.validators import (
            DocumentValidator,
            ValidationLevel,
            ValidationResult,
            BaseValidator,
            ValidationError
        )
        print("✅ ValidationResult imported successfully alongside other validator classes")
        
        # Test ValidationResult creation and basic functionality
        from markitdown_gui.core.validators.base_validator import ValidationIssue, ValidationSeverity
        
        # Create a test ValidationResult
        test_issues = [
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="TEST_001",
                message="Test validation issue",
                details={"test": "data"},
                location="test_file.pdf",
                suggestion="Fix the test issue"
            )
        ]
        
        validation_result = ValidationResult(
            is_valid=False,
            issues=test_issues,
            metadata={"file_size": 1024, "pages": 5}
        )
        
        print(f"✅ ValidationResult instance created successfully")
        print(f"   - Is valid: {validation_result.is_valid}")
        print(f"   - Issues count: {len(validation_result.issues)}")
        print(f"   - First issue: {validation_result.issues[0].message}")
        print(f"   - Metadata: {validation_result.metadata}")
        
        # Test properties
        print(f"   - Has critical issues: {validation_result.has_critical_issues}")
        print(f"   - Critical issues count: {validation_result.critical_issues_count}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_conversion_manager_import():
    """Test that conversion_manager can now import ValidationResult successfully"""
    
    print("\n🔍 Testing conversion_manager import with ValidationResult...")
    
    try:
        # This is the exact import that was failing
        from markitdown_gui.core.validators import DocumentValidator, ValidationLevel, ValidationResult
        print("✅ All required imports from validators module successful")
        
        # Test that we can import the conversion manager now (this was failing before)
        print("🔍 Testing conversion_manager import...")
        
        # Import the conversion manager to ensure it doesn't fail
        from markitdown_gui.core import conversion_manager
        print("✅ conversion_manager module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversion_manager imports: {e}")
        return False


def test_all_validators_import():
    """Test that all validator imports still work with ValidationResult"""
    
    print("\n🔍 Testing comprehensive validator imports...")
    
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
        
        print("✅ All validator classes imported successfully:")
        classes = [
            PDFValidator, PDFValidationResult, FontDescriptorError,
            DocumentValidator, ValidationLevel, BaseValidator,
            ValidationError, ValidationResult
        ]
        
        for cls in classes:
            print(f"   - {cls.__name__}: {cls}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing comprehensive validator imports: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ValidationResult Import Test")
    print("=" * 60)
    
    test1_result = test_validation_result_import()
    test2_result = test_conversion_manager_import()
    test3_result = test_all_validators_import()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result and test3_result:
        print("🎉 ALL TESTS PASSED - ValidationResult import issue is FIXED!")
        print("✅ ValidationResult import issue: RESOLVED")
        print("✅ conversion_manager import: WORKING")
        print("✅ All validator imports: WORKING")
        print("\nThe application should now start without ValidationResult import errors.")
        print("Next step: Run 'python main.py' to test full application startup")
    else:
        print("❌ Some tests failed - issue needs further investigation")
        if not test1_result:
            print("   - ValidationResult basic functionality test failed")
        if not test2_result:
            print("   - conversion_manager import test failed") 
        if not test3_result:
            print("   - Comprehensive validator imports test failed")
    print("=" * 60)
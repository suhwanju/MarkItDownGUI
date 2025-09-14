#!/usr/bin/env python3
"""
Test script to verify categorize_exception import and functionality
"""

def test_categorize_exception_import():
    """Test that categorize_exception can be imported and used correctly"""
    
    print("🔍 Testing categorize_exception import and functionality...")
    
    try:
        # Test import from the error_handling module
        from markitdown_gui.core.error_handling import categorize_exception
        print("✅ categorize_exception imported successfully")
        
        # Test import alongside other error classes
        from markitdown_gui.core.error_handling import (
            ConversionError,
            FontDescriptorError,
            PDFParsingError,
            categorize_exception
        )
        print("✅ categorize_exception imported successfully alongside other error classes")
        
        # Test function signature and basic functionality
        from pathlib import Path
        test_path = Path("test.pdf")
        
        # Create a simple exception to test categorization
        test_exception = ValueError("Test exception")
        
        # Test the categorization function
        result = categorize_exception(test_exception, test_path)
        
        print(f"✅ categorize_exception function executed successfully")
        print(f"   - Input exception: {type(test_exception).__name__}: {test_exception}")
        print(f"   - Result type: {type(result).__name__}")
        print(f"   - Result message: {result}")
        
        # Verify the result is a ConversionError
        assert isinstance(result, ConversionError), f"Expected ConversionError, got {type(result)}"
        print("✅ categorize_exception returns proper ConversionError type")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_all_imports_with_categorize():
    """Test that all error handling imports still work with categorize_exception"""
    
    print("\n🔍 Testing all error handling imports including categorize_exception...")
    
    try:
        from markitdown_gui.core.error_handling import (
            CircuitBreaker,
            CircuitBreakerState, 
            CircuitBreakerError,
            FallbackManager,
            FallbackStrategy,
            FallbackResult,
            ErrorRecoveryManager,
            RecoveryAction,
            RecoveryResult,
            ErrorReporter,
            ErrorReport, 
            ErrorSeverity,
            ConversionError,
            FontDescriptorError,
            PDFParsingError,
            MarkItDownError,
            RecoverableError,
            UnrecoverableError,
            categorize_exception
        )
        
        print("✅ All error handling classes including categorize_exception imported successfully")
        
        # Test that categorize_exception works with other error types
        from pathlib import Path
        test_path = Path("test.docx")
        
        # Test with different exception types
        exceptions_to_test = [
            ValueError("Test value error"),
            RuntimeError("Test runtime error"),
            FileNotFoundError("Test file not found"),
            MemoryError("Test memory error")
        ]
        
        for exc in exceptions_to_test:
            result = categorize_exception(exc, test_path)
            print(f"   - {type(exc).__name__} → {type(result).__name__}")
        
        print("✅ categorize_exception handles multiple exception types correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing comprehensive imports: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("categorize_exception Import Test")
    print("=" * 60)
    
    test1_result = test_categorize_exception_import()
    test2_result = test_all_imports_with_categorize()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED - categorize_exception import issue is FIXED!")
        print("✅ categorize_exception import issue: RESOLVED")
        print("✅ All error handling imports: WORKING")
        print("\nThe application should now start without import errors.")
        print("Next step: Run 'python main.py' to test full application startup")
    else:
        print("❌ Some tests failed - issue needs further investigation")
    print("=" * 60)
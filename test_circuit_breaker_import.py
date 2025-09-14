#!/usr/bin/env python3
"""
Test script to verify CircuitBreakerError import and functionality
"""

def test_circuit_breaker_error_import():
    """Test that CircuitBreakerError can be imported and used correctly"""
    
    print("🔍 Testing CircuitBreakerError import and functionality...")
    
    try:
        # Test import from the error_handling module
        from markitdown_gui.core.error_handling import CircuitBreakerError, CircuitBreakerState
        print("✅ CircuitBreakerError imported successfully")
        
        # Test creating an instance of the error
        error = CircuitBreakerError(
            message="Circuit breaker is open due to too many failures",
            state=CircuitBreakerState.OPEN,
            failure_count=5
        )
        
        print(f"✅ CircuitBreakerError instance created: {error}")
        print(f"   - Message: {str(error)}")
        print(f"   - State: {error.state}")
        print(f"   - Failure count: {error.failure_count}")
        
        # Test that it's a proper exception
        try:
            raise error
        except CircuitBreakerError as e:
            print("✅ CircuitBreakerError can be raised and caught properly")
            print(f"   - Caught error: {e}")
            print(f"   - Error state: {e.state.value}")
            
        # Test direct import (the way it was failing before)
        from markitdown_gui.core.error_handling import CircuitBreakerError as CBError
        print("✅ Direct import with alias works")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_all_error_classes():
    """Test that all error handling classes can be imported"""
    
    print("\n🔍 Testing all error handling classes...")
    
    try:
        from markitdown_gui.core.error_handling import (
            CircuitBreaker,
            CircuitBreakerState, 
            CircuitBreakerError,
            FallbackManager,
            FallbackStrategy,
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
            UnrecoverableError
        )
        
        print("✅ All error handling classes imported successfully")
        
        # Test error hierarchy
        font_error = FontDescriptorError("FontBBox parsing failed", font_name="Arial")
        pdf_error = PDFParsingError("PDF structure is malformed")
        
        print(f"✅ Error instances created:")
        print(f"   - FontDescriptorError: {font_error}")
        print(f"   - PDFParsingError: {pdf_error}")
        
        # Test inheritance
        assert isinstance(font_error, ConversionError), "FontDescriptorError should inherit from ConversionError"
        assert isinstance(pdf_error, ConversionError), "PDFParsingError should inherit from ConversionError"
        print("✅ Error inheritance working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing all classes: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CircuitBreakerError Import Test")
    print("=" * 60)
    
    test1_result = test_circuit_breaker_error_import()
    test2_result = test_all_error_classes()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 ALL TESTS PASSED - CircuitBreakerError import issue is FIXED!")
    else:
        print("❌ Some tests failed - issue needs further investigation")
    print("=" * 60)
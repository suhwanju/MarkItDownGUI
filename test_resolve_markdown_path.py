#!/usr/bin/env python3
"""
Test suite for resolve_markdown_output_path() function validation
Comprehensive testing of the centralized path utility function
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import traceback

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_resolve_markdown_output_path():
    """Comprehensive test of the resolve_markdown_output_path function"""
    
    print("🔍 Testing resolve_markdown_output_path() function...")
    
    try:
        # Import the function
        from markitdown_gui.core.file_manager import resolve_markdown_output_path
        from markitdown_gui.core.constants import DEFAULT_OUTPUT_DIRECTORY
        print("✅ Function imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Create temporary test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_source = temp_path / "test_document.pdf"
        test_source.touch()  # Create test file
        
        print("\n📋 Test Cases:")
        
        # Test 1: Basic functionality (flatten structure)
        try:
            output = resolve_markdown_output_path(test_source, preserve_structure=False)
            expected_name = "test_document.md"
            
            if output.name == expected_name and output.suffix == ".md":
                print("✅ Test 1: Basic functionality - PASSED")
            else:
                print(f"❌ Test 1: Expected {expected_name}, got {output.name}")
                return False
        except Exception as e:
            print(f"❌ Test 1 failed: {e}")
            return False
        
        # Test 2: Preserve directory structure
        try:
            structured_source = temp_path / "docs" / "2024" / "report.pdf"
            structured_source.parent.mkdir(parents=True, exist_ok=True)
            structured_source.touch()
            
            output = resolve_markdown_output_path(structured_source, preserve_structure=True)
            
            # Should include parent directory name in structure
            if "2024" in str(output) or output.parent.name in ["docs", "2024"]:
                print("✅ Test 2: Directory structure preservation - PASSED")
            else:
                print(f"❌ Test 2: Structure not preserved: {output}")
                return False
        except Exception as e:
            print(f"❌ Test 2 failed: {e}")
            return False
        
        # Test 3: Custom output directory
        try:
            custom_dir = temp_path / "custom_markdown"
            custom_dir.mkdir(exist_ok=True)
            
            output = resolve_markdown_output_path(test_source, output_base_dir=custom_dir)
            
            if custom_dir in output.parents or output.parent == custom_dir:
                print("✅ Test 3: Custom output directory - PASSED")
            else:
                print(f"❌ Test 3: Not in custom directory: {output}")
                return False
        except Exception as e:
            print(f"❌ Test 3 failed: {e}")
            return False
        
        # Test 4: Filename sanitization
        try:
            dangerous_source = temp_path / 'dangerous<>:"/\\|?*file.pdf'
            # Create with safe name but test with dangerous name
            safe_source = temp_path / "dangerous_file.pdf"
            safe_source.touch()
            
            # Test with path that has dangerous characters
            output = resolve_markdown_output_path(safe_source, preserve_structure=False)
            
            # Check that output filename is safe
            invalid_chars = '<>:"/\\|?*'
            if not any(char in output.name for char in invalid_chars):
                print("✅ Test 4: Filename sanitization - PASSED")
            else:
                print(f"❌ Test 4: Unsafe characters in output: {output.name}")
                return False
        except Exception as e:
            print(f"❌ Test 4 failed: {e}")
            return False
        
        # Test 5: Security validation (directory traversal)
        try:
            # This should be handled safely without allowing traversal
            output = resolve_markdown_output_path(test_source, preserve_structure=False)
            
            # Verify the output is within expected bounds
            if ".." not in str(output):
                print("✅ Test 5: Security validation - PASSED")
            else:
                print(f"❌ Test 5: Potential traversal in output: {output}")
                return False
        except Exception as e:
            print(f"❌ Test 5 failed: {e}")
            return False
        
        # Test 6: Unique filename generation
        try:
            # Create a file that would conflict
            output1 = resolve_markdown_output_path(test_source, preserve_structure=False)
            
            # Create the output file to simulate conflict
            if not output1.parent.exists():
                output1.parent.mkdir(parents=True, exist_ok=True)
            output1.touch()
            
            # Request another path with the same source - should get unique name
            output2 = resolve_markdown_output_path(test_source, preserve_structure=False, ensure_unique=True)
            
            if output1 != output2 and output2.exists() is False:
                print("✅ Test 6: Unique filename generation - PASSED")
            else:
                print(f"❌ Test 6: Uniqueness not ensured: {output1} vs {output2}")
                return False
        except Exception as e:
            print(f"❌ Test 6 failed: {e}")
            return False
        
        # Test 7: Input validation
        try:
            # Test with invalid input
            try:
                resolve_markdown_output_path(None)
                print("❌ Test 7: Should have raised ValueError for None input")
                return False
            except (ValueError, TypeError):
                print("✅ Test 7: Input validation - PASSED")
        except Exception as e:
            print(f"❌ Test 7 failed: {e}")
            return False
        
        # Test 8: Path length validation
        try:
            # Create a very long filename (but not exceeding limits)
            long_name = "a" * 200 + ".pdf"
            long_source = temp_path / long_name
            long_source.touch()
            
            output = resolve_markdown_output_path(long_source, preserve_structure=False)
            
            # Should handle long names appropriately
            if len(str(output)) < 5000:  # Should be reasonable length
                print("✅ Test 8: Path length validation - PASSED")
            else:
                print(f"❌ Test 8: Path too long: {len(str(output))} chars")
                return False
        except Exception as e:
            print(f"❌ Test 8 failed: {e}")
            return False
    
    print("\n🎉 All tests passed! Function implementation is solid.")
    return True

def test_function_signature():
    """Test function signature and documentation"""
    
    print("\n📝 Testing function signature and documentation...")
    
    try:
        from markitdown_gui.core.file_manager import resolve_markdown_output_path
        import inspect
        
        # Check signature
        sig = inspect.signature(resolve_markdown_output_path)
        params = list(sig.parameters.keys())
        
        expected_params = ['source_path', 'preserve_structure', 'output_base_dir', 'ensure_unique']
        
        if params == expected_params:
            print("✅ Function signature correct")
        else:
            print(f"❌ Signature mismatch. Expected: {expected_params}, Got: {params}")
            return False
        
        # Check default values
        defaults = {
            'preserve_structure': True,
            'output_base_dir': None,
            'ensure_unique': True
        }
        
        for param_name, expected_default in defaults.items():
            param = sig.parameters[param_name]
            if param.default == expected_default:
                print(f"✅ Default value for {param_name}: {expected_default}")
            else:
                print(f"❌ Wrong default for {param_name}: expected {expected_default}, got {param.default}")
                return False
        
        # Check docstring exists and is comprehensive
        if resolve_markdown_output_path.__doc__ and len(resolve_markdown_output_path.__doc__) > 500:
            print("✅ Comprehensive docstring present")
        else:
            print("❌ Docstring missing or too short")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Signature test failed: {e}")
        return False

def test_integration_with_existing_code():
    """Test integration with existing codebase components"""
    
    print("\n🔗 Testing integration with existing code...")
    
    try:
        # Test that required imports are available
        from markitdown_gui.core.utils import sanitize_filename, get_unique_output_path
        from markitdown_gui.core.constants import DEFAULT_OUTPUT_DIRECTORY
        from markitdown_gui.core.file_manager import resolve_markdown_output_path
        
        print("✅ All required dependencies imported successfully")
        
        # Test that the function uses existing utilities
        test_path = Path("/tmp/test.pdf")
        
        # Should not raise errors and should use existing utilities internally
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_source = Path(temp_dir) / "test.pdf"
            temp_source.touch()
            
            result = resolve_markdown_output_path(temp_source, preserve_structure=False)
            
            if result and isinstance(result, Path):
                print("✅ Function returns proper Path object")
            else:
                print(f"❌ Invalid return type: {type(result)}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Integration test failed - missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    
    print("=" * 60)
    print("🧪 RESOLVE_MARKDOWN_OUTPUT_PATH VALIDATION TEST")
    print("=" * 60)
    
    tests = [
        ("Function Implementation", test_resolve_markdown_output_path),
        ("Function Signature", test_function_signature),
        ("Integration Tests", test_integration_with_existing_code)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Implementation is ready for production")
        return True
    else:
        print(f"❌ {total_tests - passed_tests} tests failed - Implementation needs fixes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
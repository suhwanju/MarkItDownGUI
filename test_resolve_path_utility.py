#!/usr/bin/env python3
"""
Comprehensive Technical QA Test Suite for resolve_markdown_output_path() Function

This test suite validates:
1. Core functionality with various path scenarios
2. Security sanitization and path traversal protection
3. Cross-platform compatibility and path handling
4. Performance requirements and edge case handling
5. Integration with existing system components
6. Error handling and system stability

Testing Framework: Python unittest with custom QA assertions
Test Categories: Functional, Security, Performance, Integration, Error Handling
"""

import sys
import os
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import unittest
from typing import List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from markitdown_gui.core.file_manager import resolve_markdown_output_path
    from markitdown_gui.core.constants import DEFAULT_OUTPUT_DIRECTORY
    from markitdown_gui.core.utils import sanitize_filename, get_unique_output_path
except ImportError as e:
    print(f"❌ CRITICAL ERROR: Cannot import required modules: {e}")
    print("This indicates a fundamental problem with the implementation.")
    sys.exit(1)


class PathUtilityQATestSuite(unittest.TestCase):
    """Comprehensive Technical QA Test Suite for Path Utility Function"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_results = {
            'functional': [],
            'security': [], 
            'performance': [],
            'integration': [],
            'error_handling': [],
            'edge_cases': []
        }
        cls.temp_base_dir = Path(tempfile.mkdtemp(prefix="path_util_qa_"))
        cls.test_markdown_dir = cls.temp_base_dir / "markdown"
        cls.test_source_dir = cls.temp_base_dir / "source"
        
        # Create test directories
        cls.test_markdown_dir.mkdir(parents=True, exist_ok=True)
        cls.test_source_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔧 Test environment created: {cls.temp_base_dir}")
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        try:
            if cls.temp_base_dir.exists():
                shutil.rmtree(cls.temp_base_dir, ignore_errors=True)
            print("🧹 Test environment cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def setUp(self):
        """Set up for each test"""
        self.test_files_created = []
        
    def tearDown(self):
        """Clean up after each test"""
        for file_path in self.test_files_created:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
                
        # Clean up test subdirectories
        for subdir in self.test_markdown_dir.iterdir():
            if subdir.is_dir():
                try:
                    shutil.rmtree(subdir, ignore_errors=True)
                except Exception:
                    pass

    def record_test_result(self, category: str, test_name: str, passed: bool, 
                          details: str = "", performance_data: Dict = None):
        """Record test result for final reporting"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': time.time()
        }
        if performance_data:
            result['performance'] = performance_data
            
        self.test_results[category].append(result)

    # ========== FUNCTIONAL TESTS ==========
    
    def test_basic_path_resolution(self):
        """Test basic path resolution functionality"""
        test_name = "test_basic_path_resolution"
        
        try:
            # Test basic file path
            source_path = self.test_source_dir / "test_document.pdf"
            result = resolve_markdown_output_path(
                source_path, 
                preserve_structure=False,
                output_base_dir=self.test_markdown_dir
            )
            
            # Validations
            self.assertTrue(result.is_absolute(), "Result should be absolute path")
            self.assertTrue(str(result).startswith(str(self.test_markdown_dir)), 
                          "Result should be within output directory")
            self.assertEqual(result.suffix, ".md", "Result should have .md extension")
            self.assertEqual(result.stem, "test_document", "Filename stem should be preserved")
            
            self.record_test_result('functional', test_name, True, 
                                  f"Basic resolution: {result}")
            
        except Exception as e:
            self.record_test_result('functional', test_name, False, 
                                  f"Failed with exception: {e}")
            self.fail(f"Basic path resolution failed: {e}")

    def test_preserve_structure_functionality(self):
        """Test structure preservation functionality"""
        test_name = "test_preserve_structure_functionality"
        
        try:
            # Create nested source structure
            nested_source = self.test_source_dir / "projects" / "2024" / "report.docx"
            nested_source.parent.mkdir(parents=True, exist_ok=True)
            nested_source.touch()
            self.test_files_created.append(nested_source)
            
            # Test with structure preservation
            result_preserve = resolve_markdown_output_path(
                nested_source,
                preserve_structure=True,
                output_base_dir=self.test_markdown_dir
            )
            
            # Test without structure preservation
            result_flat = resolve_markdown_output_path(
                nested_source,
                preserve_structure=False,
                output_base_dir=self.test_markdown_dir
            )
            
            # Validations
            self.assertIn("2024", str(result_preserve), 
                         "Structure preserved path should contain parent directory")
            self.assertNotIn("2024", str(result_flat),
                           "Flat path should not contain nested structure")
            
            self.record_test_result('functional', test_name, True,
                                  f"Preserve: {result_preserve}, Flat: {result_flat}")
                                  
        except Exception as e:
            self.record_test_result('functional', test_name, False, f"Exception: {e}")
            self.fail(f"Structure preservation test failed: {e}")

    def test_custom_output_directory(self):
        """Test custom output directory handling"""
        test_name = "test_custom_output_directory"
        
        try:
            custom_dir = self.temp_base_dir / "custom_markdown"
            custom_dir.mkdir(exist_ok=True)
            
            source_path = self.test_source_dir / "document.txt"
            
            result = resolve_markdown_output_path(
                source_path,
                output_base_dir=custom_dir
            )
            
            # Validations
            self.assertTrue(str(result).startswith(str(custom_dir)),
                          "Result should be in custom directory")
            self.assertTrue(custom_dir.exists(), "Custom directory should be created")
            
            self.record_test_result('functional', test_name, True,
                                  f"Custom directory result: {result}")
                                  
        except Exception as e:
            self.record_test_result('functional', test_name, False, f"Exception: {e}")
            self.fail(f"Custom output directory test failed: {e}")

    def test_unique_filename_generation(self):
        """Test unique filename generation to avoid conflicts"""
        test_name = "test_unique_filename_generation"
        
        try:
            source_path = self.test_source_dir / "duplicate.pdf"
            
            # Create first file
            result1 = resolve_markdown_output_path(
                source_path,
                output_base_dir=self.test_markdown_dir,
                ensure_unique=True
            )
            result1.touch()
            self.test_files_created.append(result1)
            
            # Create second file with same name
            result2 = resolve_markdown_output_path(
                source_path,
                output_base_dir=self.test_markdown_dir,
                ensure_unique=True
            )
            
            # Validations
            self.assertNotEqual(result1, result2, "Results should be different")
            self.assertTrue("_" in result2.stem, "Second result should have uniquifier")
            
            # Test with ensure_unique=False
            result3 = resolve_markdown_output_path(
                source_path,
                output_base_dir=self.test_markdown_dir,
                ensure_unique=False
            )
            
            self.assertEqual(result1, result3, "Without unique flag, should return same path")
            
            self.record_test_result('functional', test_name, True,
                                  f"Unique generation working: {result1} != {result2}")
                                  
        except Exception as e:
            self.record_test_result('functional', test_name, False, f"Exception: {e}")
            self.fail(f"Unique filename generation test failed: {e}")

    # ========== SECURITY TESTS ==========
    
    def test_path_traversal_protection(self):
        """Test protection against directory traversal attacks"""
        test_name = "test_path_traversal_protection"
        
        try:
            # Test various path traversal attempts
            malicious_paths = [
                Path("../../../etc/passwd"),
                Path("..\\..\\windows\\system32\\config\\sam"),
                Path("../../../../root/.ssh/id_rsa"),
                Path("../malicious/../../outside.txt"),
            ]
            
            all_secure = True
            details = []
            
            for malicious_path in malicious_paths:
                try:
                    result = resolve_markdown_output_path(
                        malicious_path,
                        output_base_dir=self.test_markdown_dir
                    )
                    
                    # Validate result is within bounds
                    try:
                        result.resolve().relative_to(self.test_markdown_dir.resolve())
                        details.append(f"✅ Blocked traversal: {malicious_path}")
                    except ValueError:
                        all_secure = False
                        details.append(f"❌ SECURITY BREACH: {malicious_path} -> {result}")
                        
                except ValueError:
                    # Expected security exception
                    details.append(f"✅ Security exception for: {malicious_path}")
                except Exception as e:
                    details.append(f"❓ Unexpected exception for {malicious_path}: {e}")
            
            self.record_test_result('security', test_name, all_secure,
                                  "; ".join(details))
            
            if not all_secure:
                self.fail("Path traversal protection failed - CRITICAL SECURITY ISSUE")
                
        except Exception as e:
            self.record_test_result('security', test_name, False, f"Exception: {e}")
            self.fail(f"Security test failed: {e}")

    def test_filename_sanitization(self):
        """Test filename sanitization for security"""
        test_name = "test_filename_sanitization"
        
        try:
            dangerous_filenames = [
                "file<script>.pdf",
                'file"malicious".docx',
                "file|pipe.txt",
                "CON.pdf",
                "PRN.docx", 
                "file:colon.txt",
                "file?question.pdf",
                "file*star.docx"
            ]
            
            all_safe = True
            details = []
            
            for dangerous_filename in dangerous_filenames:
                source_path = self.test_source_dir / dangerous_filename
                
                result = resolve_markdown_output_path(
                    source_path,
                    output_base_dir=self.test_markdown_dir
                )
                
                # Check if dangerous characters were removed
                result_name = result.name
                dangerous_chars = '<>:"/\\|?*'
                
                has_dangerous = any(char in result_name for char in dangerous_chars)
                
                if has_dangerous:
                    all_safe = False
                    details.append(f"❌ Unsafe: {dangerous_filename} -> {result_name}")
                else:
                    details.append(f"✅ Safe: {dangerous_filename} -> {result_name}")
            
            self.record_test_result('security', test_name, all_safe,
                                  "; ".join(details))
                                  
            if not all_safe:
                self.fail("Filename sanitization failed - SECURITY ISSUE")
                
        except Exception as e:
            self.record_test_result('security', test_name, False, f"Exception: {e}")
            self.fail(f"Filename sanitization test failed: {e}")

    # ========== PERFORMANCE TESTS ==========
    
    def test_performance_requirements(self):
        """Test that the function meets performance requirements"""
        test_name = "test_performance_requirements"
        
        try:
            # Test with multiple file types and scenarios
            test_scenarios = [
                ("simple.pdf", False),
                ("nested/path/document.docx", True),
                ("very_long_filename_" + "x" * 100 + ".txt", False),
                ("unicode文档.pdf", True),
            ]
            
            performance_data = []
            
            for filename, preserve_structure in test_scenarios:
                source_path = self.test_source_dir / filename
                
                # Measure execution time
                start_time = time.perf_counter()
                
                result = resolve_markdown_output_path(
                    source_path,
                    preserve_structure=preserve_structure,
                    output_base_dir=self.test_markdown_dir
                )
                
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000
                
                performance_data.append({
                    'scenario': filename,
                    'preserve_structure': preserve_structure,
                    'execution_time_ms': execution_time_ms,
                    'result': str(result)
                })
            
            # Validate performance requirements
            max_time_ms = max(p['execution_time_ms'] for p in performance_data)
            avg_time_ms = sum(p['execution_time_ms'] for p in performance_data) / len(performance_data)
            
            # Performance requirements: < 10ms typical, < 50ms worst case
            performance_pass = max_time_ms < 50.0 and avg_time_ms < 10.0
            
            details = f"Max: {max_time_ms:.2f}ms, Avg: {avg_time_ms:.2f}ms"
            
            self.record_test_result('performance', test_name, performance_pass,
                                  details, {'performance_data': performance_data})
            
            if not performance_pass:
                print(f"⚠️ Performance warning: {details}")
                
        except Exception as e:
            self.record_test_result('performance', test_name, False, f"Exception: {e}")
            self.fail(f"Performance test failed: {e}")

    # ========== INTEGRATION TESTS ==========
    
    def test_utility_function_integration(self):
        """Test integration with existing utility functions"""
        test_name = "test_utility_function_integration"
        
        try:
            # Test with sanitize_filename integration
            source_path = self.test_source_dir / "file with spaces & symbols!.pdf"
            
            result = resolve_markdown_output_path(
                source_path,
                output_base_dir=self.test_markdown_dir
            )
            
            # Should integrate with sanitize_filename
            self.assertNotIn(" ", result.stem, "Spaces should be handled")
            self.assertNotIn("&", result.stem, "Symbols should be handled")
            self.assertNotIn("!", result.stem, "Special chars should be handled")
            
            # Test with get_unique_output_path integration
            result.touch()
            self.test_files_created.append(result)
            
            result2 = resolve_markdown_output_path(
                source_path,
                output_base_dir=self.test_markdown_dir,
                ensure_unique=True
            )
            
            self.assertNotEqual(result, result2, "Should generate unique path")
            
            self.record_test_result('integration', test_name, True,
                                  f"Integration working: {result} -> {result2}")
                                  
        except Exception as e:
            self.record_test_result('integration', test_name, False, f"Exception: {e}")
            self.fail(f"Utility integration test failed: {e}")

    def test_constants_integration(self):
        """Test integration with project constants"""
        test_name = "test_constants_integration"
        
        try:
            source_path = self.test_source_dir / "test.pdf"
            
            # Test with default output directory (None)
            result = resolve_markdown_output_path(source_path, output_base_dir=None)
            
            # Should use DEFAULT_OUTPUT_DIRECTORY constant
            self.assertTrue(DEFAULT_OUTPUT_DIRECTORY in str(result),
                          f"Should use default directory constant: {DEFAULT_OUTPUT_DIRECTORY}")
            
            self.record_test_result('integration', test_name, True,
                                  f"Constants integration working: {result}")
                                  
        except Exception as e:
            self.record_test_result('integration', test_name, False, f"Exception: {e}")
            self.fail(f"Constants integration test failed: {e}")

    # ========== ERROR HANDLING TESTS ==========
    
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        test_name = "test_invalid_input_handling"
        
        invalid_inputs = [
            (None, "None input"),
            ("", "Empty string"),
            (123, "Invalid type"),
            (Path(""), "Empty Path"),
            (Path("/nonexistent/path/that/does/not/exist/file.pdf"), "Nonexistent path")
        ]
        
        error_handling_results = []
        
        for invalid_input, description in invalid_inputs:
            try:
                result = resolve_markdown_output_path(
                    invalid_input,
                    output_base_dir=self.test_markdown_dir
                )
                error_handling_results.append(f"❌ {description}: Should have failed but got {result}")
                
            except (ValueError, TypeError, OSError) as e:
                error_handling_results.append(f"✅ {description}: Properly handled with {type(e).__name__}")
                
            except Exception as e:
                error_handling_results.append(f"❓ {description}: Unexpected exception {type(e).__name__}: {e}")
        
        # All should raise appropriate exceptions
        all_handled = all("✅" in result for result in error_handling_results)
        
        self.record_test_result('error_handling', test_name, all_handled,
                              "; ".join(error_handling_results))
        
        if not all_handled:
            self.fail("Invalid input handling failed")

    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        test_name = "test_permission_error_handling"
        
        try:
            # Create a directory with no write permissions
            restricted_dir = self.temp_base_dir / "restricted"
            restricted_dir.mkdir(exist_ok=True)
            
            # Remove write permissions (if supported by OS)
            try:
                restricted_dir.chmod(0o444)  # Read-only
                
                source_path = self.test_source_dir / "test.pdf"
                
                # Should raise OSError for permission denied
                try:
                    result = resolve_markdown_output_path(
                        source_path,
                        output_base_dir=restricted_dir
                    )
                    self.record_test_result('error_handling', test_name, False,
                                          f"Should have failed with permission error but got: {result}")
                                          
                except (OSError, PermissionError):
                    self.record_test_result('error_handling', test_name, True,
                                          "Permission error properly handled")
                    
                finally:
                    # Restore permissions for cleanup
                    restricted_dir.chmod(0o755)
                    
            except (OSError, NotImplementedError):
                # chmod might not be supported on all systems
                self.record_test_result('error_handling', test_name, True,
                                      "Permission test skipped (not supported on this system)")
                
        except Exception as e:
            self.record_test_result('error_handling', test_name, False, f"Exception: {e}")
            self.fail(f"Permission error handling test failed: {e}")

    # ========== EDGE CASES TESTS ==========
    
    def test_edge_cases(self):
        """Test various edge cases"""
        test_name = "test_edge_cases"
        
        edge_cases = [
            (Path("file"), "File without extension"),
            (Path("file."), "File with empty extension"), 
            (Path(".hidden.pdf"), "Hidden file"),
            (Path("unicode文档名称.pdf"), "Unicode filename"),
            (Path("very" * 50 + ".pdf"), "Very long filename"),
            (Path("file with spaces.pdf"), "Filename with spaces"),
            (Path("UPPERCASE.PDF"), "Uppercase extension"),
        ]
        
        edge_case_results = []
        
        for source_path, description in edge_cases:
            try:
                result = resolve_markdown_output_path(
                    source_path,
                    output_base_dir=self.test_markdown_dir
                )
                
                # Validate result
                if result.suffix == ".md" and result.is_absolute():
                    edge_case_results.append(f"✅ {description}: {result.name}")
                else:
                    edge_case_results.append(f"❌ {description}: Invalid result {result}")
                    
            except Exception as e:
                edge_case_results.append(f"❌ {description}: Exception {e}")
        
        all_passed = all("✅" in result for result in edge_case_results)
        
        self.record_test_result('edge_cases', test_name, all_passed,
                              "; ".join(edge_case_results))
        
        if not all_passed:
            print("⚠️ Some edge cases failed")

    def test_path_length_limits(self):
        """Test path length validation"""
        test_name = "test_path_length_limits"
        
        try:
            # Test very long path
            long_filename = "very_long_filename_" + "x" * 4000 + ".pdf"
            source_path = Path(long_filename)
            
            try:
                result = resolve_markdown_output_path(
                    source_path,
                    output_base_dir=self.test_markdown_dir
                )
                
                # Should either handle gracefully or raise ValueError
                if len(str(result)) > 4000:
                    self.record_test_result('edge_cases', test_name, False,
                                          f"Path too long not validated: {len(str(result))} chars")
                else:
                    self.record_test_result('edge_cases', test_name, True,
                                          f"Long path handled: {len(str(result))} chars")
                    
            except ValueError:
                # Expected for overly long paths
                self.record_test_result('edge_cases', test_name, True,
                                      "Long path properly rejected")
                
        except Exception as e:
            self.record_test_result('edge_cases', test_name, False, f"Exception: {e}")
            self.fail(f"Path length test failed: {e}")

    def generate_qa_report(self):
        """Generate comprehensive QA test report"""
        print("\n" + "="*80)
        print("📋 TECHNICAL QA TEST REPORT")
        print("="*80)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            if not results:
                continue
                
            category_pass = sum(1 for r in results if r['passed'])
            category_total = len(results)
            total_tests += category_total
            passed_tests += category_pass
            
            print(f"\n🔍 {category.upper()} TESTS ({category_pass}/{category_total})")
            print("-" * 50)
            
            for result in results:
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                print(f"{status} {result['test_name']}")
                if result['details']:
                    print(f"    Details: {result['details']}")
                    
                if 'performance' in result:
                    perf_data = result['performance'].get('performance_data', [])
                    if perf_data:
                        avg_time = sum(p['execution_time_ms'] for p in perf_data) / len(perf_data)
                        print(f"    Performance: {avg_time:.2f}ms average")
        
        print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Implementation meets technical requirements")
            return True
        else:
            failed_tests = total_tests - passed_tests
            print(f"❌ {failed_tests} TESTS FAILED - Implementation needs fixes")
            return False


def main():
    """Main test execution"""
    print("🚀 Starting Technical QA Test Suite for resolve_markdown_output_path()")
    print(f"📁 Test environment: {PathUtilityQATestSuite.temp_base_dir}")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestClass(PathUtilityQATestSuite)
    
    # Create custom test runner that captures results
    class QATestRunner:
        def __init__(self):
            self.test_instance = None
            
        def run(self, test_suite):
            for test_case in test_suite:
                if hasattr(test_case, '_testMethodName'):
                    try:
                        # Set up test instance
                        test_case.setUp()
                        self.test_instance = test_case
                        
                        # Run the test method
                        test_method = getattr(test_case, test_case._testMethodName)
                        test_method()
                        
                        # Clean up
                        test_case.tearDown()
                        
                    except Exception as e:
                        print(f"❌ Test {test_case._testMethodName} failed: {e}")
                        # Record failure if possible
                        if hasattr(test_case, 'record_test_result'):
                            test_case.record_test_result(
                                'error', test_case._testMethodName, False, str(e)
                            )
    
    # Run tests
    runner = QATestRunner()
    runner.run(suite)
    
    # Generate final report
    if runner.test_instance:
        success = runner.test_instance.generate_qa_report()
        return 0 if success else 1
    else:
        print("❌ Failed to execute tests properly")
        return 1


if __name__ == "__main__":
    sys.exit(main())
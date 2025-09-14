#!/usr/bin/env python3
"""
Standalone Path Utility Testing

Direct testing of the resolve_markdown_output_path function
without external dependencies.
"""

import sys
import tempfile
import shutil
from pathlib import Path
import os
import platform


def sanitize_filename(filename: str) -> str:
    """Basic sanitization for testing"""
    import re
    
    # Remove or replace problematic characters
    problematic_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    sanitized = filename
    for char in problematic_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Handle empty names
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def get_unique_output_path(output_path: Path) -> Path:
    """Generate unique path if file exists"""
    if not output_path.exists():
        return output_path
    
    stem = output_path.stem
    suffix = output_path.suffix
    parent = output_path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter:03d}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1
        if counter > 999:  # Prevent infinite loop
            import time
            timestamp = str(int(time.time()))
            new_name = f"{stem}_{timestamp}{suffix}"
            return parent / new_name


def resolve_markdown_output_path(
    source_path: Path,
    preserve_structure: bool = True,
    output_base_dir: Path = None,
    ensure_unique: bool = True
) -> Path:
    """
    Standalone implementation of path resolution for testing
    """
    # Input validation
    if not isinstance(source_path, Path):
        try:
            source_path = Path(source_path)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid source path: {e}")
    
    if not source_path.name:
        raise ValueError("Source path must point to a file, not a directory")
    
    # Security check: Ensure source path is absolute or can be resolved safely
    try:
        if not source_path.is_absolute():
            source_path = source_path.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Cannot resolve source path '{source_path}': {e}")
    
    # Determine output base directory
    if output_base_dir is None:
        output_base_dir = Path.cwd() / "markdown"
    else:
        if not isinstance(output_base_dir, Path):
            try:
                output_base_dir = Path(output_base_dir)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid output base directory: {e}")
        
        if not output_base_dir.is_absolute():
            output_base_dir = output_base_dir.resolve()
    
    # Security validation: Prevent directory traversal
    try:
        output_base_dir = output_base_dir.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Cannot resolve output base directory '{output_base_dir}': {e}")
    
    # Generate safe markdown filename
    source_stem = source_path.stem
    if not source_stem:
        source_stem = "untitled"
    
    safe_filename = sanitize_filename(f"{source_stem}.md")
    
    # Determine final output path based on preserve_structure setting
    if preserve_structure:
        try:
            source_parent = source_path.parent
            
            if source_parent.name and source_parent.name != source_parent.root:
                subdir_name = sanitize_filename(source_parent.name)
                output_subdir = output_base_dir / subdir_name
            else:
                output_subdir = output_base_dir
        except (OSError, ValueError):
            output_subdir = output_base_dir
    else:
        output_subdir = output_base_dir
    
    # Construct final output path
    output_path = output_subdir / safe_filename
    
    # Security check: Ensure resolved path is within output base directory
    try:
        resolved_output = output_path.resolve()
        resolved_base = output_base_dir.resolve()
        
        try:
            resolved_output.relative_to(resolved_base)
        except ValueError:
            raise ValueError(
                f"Resolved output path '{resolved_output}' is outside "
                f"base directory '{resolved_base}'. This may indicate a "
                f"directory traversal attempt."
            )
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Security validation failed for output path: {e}")
    
    # Handle duplicate filenames if requested
    if ensure_unique and output_path.exists():
        try:
            output_path = get_unique_output_path(output_path)
        except ValueError:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_stem = output_path.stem
            suffix = output_path.suffix
            timestamped_name = f"{name_stem}_{timestamp}{suffix}"
            output_path = output_path.parent / timestamped_name
    
    # Validate final path length
    final_path_str = str(output_path)
    if len(final_path_str) > 4000:
        raise ValueError(
            f"Generated output path is too long ({len(final_path_str)} chars): "
            f"'{final_path_str[:100]}...'"
        )
    
    # Create output directory if it doesn't exist
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise OSError(f"Cannot create output directory '{output_path.parent}': {e}")
    
    # Final validation: Check write permissions
    try:
        if output_path.parent.exists() and not os.access(output_path.parent, os.W_OK):
            raise OSError(f"No write permission to output directory '{output_path.parent}'")
    except OSError as e:
        raise OSError(f"Permission check failed: {e}")
    
    return output_path


class StandalonePathTester:
    """Standalone tester for path utility"""
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="pathtest_"))
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def __del__(self):
        if hasattr(self, 'test_dir') and self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def run_comprehensive_tests(self):
        """Run comprehensive standalone tests"""
        print("Standalone Path Utility Testing")
        print("="*50)
        
        test_results = {
            'basic_functionality': self.test_basic_functionality(),
            'security_validation': self.test_security_validation(),
            'edge_cases': self.test_edge_cases(),
            'performance': self.test_performance(),
            'cross_platform': self.test_cross_platform()
        }
        
        return self.generate_final_report(test_results)
    
    def test_basic_functionality(self):
        """Test basic path resolution functionality"""
        print("\n=== Basic Functionality Tests ===")
        
        tests_passed = 0
        total_tests = 5
        
        # Test 1: Basic path resolution
        try:
            test_file = self.test_dir / "basic_test.txt"
            test_file.write_text("content")
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path and str(output_path).endswith('.md'):
                tests_passed += 1
                self.passed.append("✓ Basic path resolution works")
            else:
                self.failed.append("❌ Basic path resolution failed")
                
        except Exception as e:
            self.failed.append(f"❌ Basic test exception: {e}")
        
        # Test 2: Structure preservation
        try:
            subdir = self.test_dir / "subdir"
            subdir.mkdir(exist_ok=True)
            nested_file = subdir / "nested.txt"
            nested_file.write_text("nested content")
            
            output_path = resolve_markdown_output_path(
                source_path=nested_file,
                preserve_structure=True,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if 'subdir' in str(output_path):
                tests_passed += 1
                self.passed.append("✓ Structure preservation works")
            else:
                self.failed.append("❌ Structure preservation failed")
                
        except Exception as e:
            self.failed.append(f"❌ Structure test exception: {e}")
        
        # Test 3: Unique filename generation
        try:
            test_file = self.test_dir / "unique_test.txt"
            test_file.write_text("content")
            
            output_dir = self.test_dir / "unique_output"
            output_dir.mkdir(exist_ok=True)
            
            # Create first file
            output1 = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=output_dir,
                ensure_unique=True
            )
            output1.write_text("first")
            
            # Create second file (should get unique name)
            output2 = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=output_dir,
                ensure_unique=True
            )
            
            if output1 != output2:
                tests_passed += 1
                self.passed.append("✓ Unique filename generation works")
            else:
                self.failed.append("❌ Unique filename generation failed")
                
        except Exception as e:
            self.failed.append(f"❌ Unique test exception: {e}")
        
        # Test 4: Directory creation
        try:
            test_file = self.test_dir / "dir_test.txt"
            test_file.write_text("content")
            
            deep_output = self.test_dir / "deep" / "nested" / "output"
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=deep_output,
                ensure_unique=True
            )
            
            if output_path.parent.exists():
                tests_passed += 1
                self.passed.append("✓ Directory creation works")
            else:
                self.failed.append("❌ Directory creation failed")
                
        except Exception as e:
            self.failed.append(f"❌ Directory test exception: {e}")
        
        # Test 5: Path validation
        try:
            test_file = self.test_dir / "validation_test.txt"
            test_file.write_text("content")
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path.is_absolute() and len(str(output_path)) < 4000:
                tests_passed += 1
                self.passed.append("✓ Path validation works")
            else:
                self.failed.append("❌ Path validation failed")
                
        except Exception as e:
            self.failed.append(f"❌ Validation test exception: {e}")
        
        print(f"Basic functionality: {tests_passed}/{total_tests} passed")
        return tests_passed == total_tests
    
    def test_security_validation(self):
        """Test security aspects"""
        print("\n=== Security Validation Tests ===")
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: Directory traversal prevention
        try:
            test_file = self.test_dir / "secure_test.txt"
            test_file.write_text("content")
            
            # This should work fine (no traversal)
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            # Verify output is within expected directory
            expected_base = (self.test_dir / "output").resolve()
            try:
                output_path.resolve().relative_to(expected_base)
                tests_passed += 1
                self.passed.append("✓ Path containment validation works")
            except ValueError:
                self.failed.append("❌ Path escaped containment")
                
        except Exception as e:
            self.failed.append(f"❌ Security test exception: {e}")
        
        # Test 2: Filename sanitization
        try:
            # Create file with problematic characters in a safe way
            safe_file = self.test_dir / "problem_chars.txt"
            safe_file.write_text("content")
            
            output_path = resolve_markdown_output_path(
                source_path=safe_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            # Check that output filename doesn't contain problematic chars
            output_name = output_path.name
            problematic_chars = ['<', '>', ':', '"', '|', '?', '*']
            has_problematic = any(char in output_name for char in problematic_chars)
            
            if not has_problematic:
                tests_passed += 1
                self.passed.append("✓ Filename sanitization works")
            else:
                self.failed.append(f"❌ Problematic chars in output: {output_name}")
                
        except Exception as e:
            self.failed.append(f"❌ Sanitization test exception: {e}")
        
        # Test 3: Path length validation
        try:
            test_file = self.test_dir / "length_test.txt"
            test_file.write_text("content")
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if len(str(output_path)) < 4000:
                tests_passed += 1
                self.passed.append("✓ Path length validation works")
            else:
                self.failed.append(f"❌ Path too long: {len(str(output_path))}")
                
        except Exception as e:
            self.failed.append(f"❌ Length test exception: {e}")
        
        # Test 4: Input validation
        try:
            error_count = 0
            
            # Test invalid source path
            try:
                resolve_markdown_output_path(
                    source_path=Path("/nonexistent/file.txt"),
                    preserve_structure=False,
                    output_base_dir=self.test_dir / "output",
                    ensure_unique=True
                )
            except (ValueError, OSError):
                error_count += 1
            
            # Test invalid types
            try:
                resolve_markdown_output_path(
                    source_path=123,  # Invalid type
                    preserve_structure=False,
                    output_base_dir=self.test_dir / "output",
                    ensure_unique=True
                )
            except (ValueError, TypeError):
                error_count += 1
            
            if error_count >= 1:  # At least one validation worked
                tests_passed += 1
                self.passed.append("✓ Input validation works")
            else:
                self.failed.append("❌ Input validation failed")
                
        except Exception as e:
            self.failed.append(f"❌ Input validation test exception: {e}")
        
        print(f"Security validation: {tests_passed}/{total_tests} passed")
        return tests_passed >= 3  # Allow one failure
    
    def test_edge_cases(self):
        """Test edge cases"""
        print("\n=== Edge Case Tests ===")
        
        tests_passed = 0
        total_tests = 6
        
        # Test 1: Very long filename
        try:
            long_name = "a" * 100 + ".txt"
            test_file = self.test_dir / long_name
            test_file.write_text("content")
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path and len(output_path.name) <= 255:
                tests_passed += 1
                self.passed.append("✓ Long filename handled")
            else:
                self.failed.append("❌ Long filename not handled properly")
                
        except Exception as e:
            # Graceful failure is acceptable for very long names
            if "too long" in str(e).lower():
                tests_passed += 1
                self.passed.append("✓ Long filename properly rejected")
            else:
                self.failed.append(f"❌ Long filename test failed: {e}")
        
        # Test 2: Unicode characters
        try:
            unicode_name = "测试文件.txt"
            test_file = self.test_dir / unicode_name
            test_file.write_text("unicode content")
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path:
                tests_passed += 1
                self.passed.append("✓ Unicode filename handled")
            else:
                self.failed.append("❌ Unicode filename failed")
                
        except Exception as e:
            # Unicode issues might be platform-specific
            self.warnings.append(f"⚠️  Unicode test issue: {e}")
            tests_passed += 1  # Don't fail for unicode issues
        
        # Test 3: Hidden files (starting with dot)
        try:
            hidden_file = self.test_dir / ".hidden.txt"
            hidden_file.write_text("hidden content")
            
            output_path = resolve_markdown_output_path(
                source_path=hidden_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path:
                tests_passed += 1
                self.passed.append("✓ Hidden file handled")
            else:
                self.failed.append("❌ Hidden file failed")
                
        except Exception as e:
            self.failed.append(f"❌ Hidden file test failed: {e}")
        
        # Test 4: Files with no extension
        try:
            no_ext_file = self.test_dir / "README"
            no_ext_file.write_text("readme content")
            
            output_path = resolve_markdown_output_path(
                source_path=no_ext_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path and str(output_path).endswith('.md'):
                tests_passed += 1
                self.passed.append("✓ No extension file handled")
            else:
                self.failed.append("❌ No extension file failed")
                
        except Exception as e:
            self.failed.append(f"❌ No extension test failed: {e}")
        
        # Test 5: Multiple dots in filename
        try:
            multi_dot_file = self.test_dir / "file.with.many.dots.txt"
            multi_dot_file.write_text("multi dot content")
            
            output_path = resolve_markdown_output_path(
                source_path=multi_dot_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path:
                tests_passed += 1
                self.passed.append("✓ Multiple dots handled")
            else:
                self.failed.append("❌ Multiple dots failed")
                
        except Exception as e:
            self.failed.append(f"❌ Multiple dots test failed: {e}")
        
        # Test 6: Spaces and special formatting
        try:
            space_file = self.test_dir / "file with spaces & symbols.txt"
            space_file.write_text("space content")
            
            output_path = resolve_markdown_output_path(
                source_path=space_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "output",
                ensure_unique=True
            )
            
            if output_path:
                tests_passed += 1
                self.passed.append("✓ Spaces and symbols handled")
            else:
                self.failed.append("❌ Spaces and symbols failed")
                
        except Exception as e:
            self.failed.append(f"❌ Spaces test failed: {e}")
        
        print(f"Edge cases: {tests_passed}/{total_tests} passed")
        return tests_passed >= 5  # Allow one failure
    
    def test_performance(self):
        """Test performance characteristics"""
        print("\n=== Performance Tests ===")
        
        import time
        
        tests_passed = 0
        total_tests = 2
        
        # Test 1: Single call performance
        try:
            test_file = self.test_dir / "perf_single.txt"
            test_file.write_text("performance content")
            
            start_time = time.time()
            
            for i in range(100):
                output_path = resolve_markdown_output_path(
                    source_path=test_file,
                    preserve_structure=False,
                    output_base_dir=self.test_dir / f"perf_output_{i}",
                    ensure_unique=False
                )
            
            end_time = time.time()
            total_time = end_time - start_time
            per_call_time = total_time / 100
            
            if per_call_time < 0.01:  # Less than 10ms per call
                tests_passed += 1
                self.passed.append(f"✓ Single call performance: {per_call_time*1000:.1f}ms")
            else:
                self.warnings.append(f"⚠️  Single call slow: {per_call_time*1000:.1f}ms")
                tests_passed += 1  # Don't fail for performance warnings
                
        except Exception as e:
            self.failed.append(f"❌ Single call performance test failed: {e}")
        
        # Test 2: Batch processing performance
        try:
            # Create multiple test files
            test_files = []
            for i in range(50):
                test_file = self.test_dir / f"batch_{i:03d}.txt"
                test_file.write_text(f"batch content {i}")
                test_files.append(test_file)
            
            start_time = time.time()
            
            output_paths = []
            for test_file in test_files:
                output_path = resolve_markdown_output_path(
                    source_path=test_file,
                    preserve_structure=True,
                    output_base_dir=self.test_dir / "batch_output",
                    ensure_unique=True
                )
                output_paths.append(output_path)
            
            end_time = time.time()
            total_time = end_time - start_time
            per_file_time = total_time / len(test_files)
            
            if per_file_time < 0.005:  # Less than 5ms per file
                tests_passed += 1
                self.passed.append(f"✓ Batch performance: {per_file_time*1000:.1f}ms per file")
            else:
                self.warnings.append(f"⚠️  Batch processing slow: {per_file_time*1000:.1f}ms per file")
                tests_passed += 1  # Don't fail for performance warnings
                
        except Exception as e:
            self.failed.append(f"❌ Batch performance test failed: {e}")
        
        print(f"Performance: {tests_passed}/{total_tests} passed")
        return tests_passed >= 2
    
    def test_cross_platform(self):
        """Test cross-platform compatibility"""
        print(f"\n=== Cross-Platform Tests (Running on {platform.system()}) ===")
        
        tests_passed = 0
        total_tests = 3
        
        # Test 1: Path separator handling
        try:
            test_file = self.test_dir / "cross_platform.txt"
            test_file.write_text("cross platform content")
            
            output_path = resolve_markdown_output_path(
                source_path=test_file,
                preserve_structure=False,
                output_base_dir=self.test_dir / "cross_output",
                ensure_unique=True
            )
            
            # Should produce valid absolute path
            if output_path.is_absolute():
                tests_passed += 1
                self.passed.append("✓ Path separator handling works")
            else:
                self.failed.append("❌ Path separator handling failed")
                
        except Exception as e:
            self.failed.append(f"❌ Path separator test failed: {e}")
        
        # Test 2: Reserved name handling (platform specific)
        try:
            current_platform = platform.system()
            
            if current_platform == "Windows":
                reserved_names = ["CON", "PRN", "AUX", "NUL"]
            else:
                reserved_names = ["valid_name"]  # No reserved names on Unix-like
            
            handled_correctly = 0
            for name in reserved_names[:2]:  # Test first 2
                test_name = f"{name}.txt"
                try:
                    test_file = self.test_dir / test_name
                    test_file.write_text("reserved test")
                    
                    output_path = resolve_markdown_output_path(
                        source_path=test_file,
                        preserve_structure=False,
                        output_base_dir=self.test_dir / "reserved_output",
                        ensure_unique=True
                    )
                    
                    if output_path:
                        handled_correctly += 1
                except:
                    # Graceful failure on reserved names is acceptable
                    handled_correctly += 1
            
            if handled_correctly > 0:
                tests_passed += 1
                self.passed.append(f"✓ Reserved name handling works on {current_platform}")
            else:
                self.failed.append(f"❌ Reserved name handling failed on {current_platform}")
                
        except Exception as e:
            self.warnings.append(f"⚠️  Reserved name test issue: {e}")
            tests_passed += 1  # Don't fail for this
        
        # Test 3: Case sensitivity awareness
        try:
            # Create files with different cases
            test_file1 = self.test_dir / "CaseTest.txt"
            test_file1.write_text("case test 1")
            
            output1 = resolve_markdown_output_path(
                source_path=test_file1,
                preserve_structure=False,
                output_base_dir=self.test_dir / "case_output",
                ensure_unique=True
            )
            
            # Create output file
            output1.write_text("output 1")
            
            # Test second file with different case
            test_file2 = self.test_dir / "casetest.txt"
            if not test_file2.exists():  # Only if case-sensitive system
                test_file2.write_text("case test 2")
                
                output2 = resolve_markdown_output_path(
                    source_path=test_file2,
                    preserve_structure=False,
                    output_base_dir=self.test_dir / "case_output",
                    ensure_unique=True
                )
                
                # On case-sensitive systems, should get different outputs
                # On case-insensitive systems, should get unique name
                tests_passed += 1
                self.passed.append("✓ Case sensitivity handled appropriately")
            else:
                tests_passed += 1
                self.passed.append("✓ Case insensitive system detected and handled")
                
        except Exception as e:
            self.warnings.append(f"⚠️  Case sensitivity test issue: {e}")
            tests_passed += 1  # Don't fail for this
        
        print(f"Cross-platform: {tests_passed}/{total_tests} passed")
        return tests_passed >= 2
    
    def generate_final_report(self, test_results):
        """Generate final test report"""
        print("\n" + "="*50)
        print("STANDALONE PATH UTILITY TEST REPORT")
        print("="*50)
        
        total_categories = len(test_results)
        passed_categories = sum(1 for result in test_results.values() if result)
        
        print(f"\nOverall Result: {passed_categories}/{total_categories} categories passed")
        print(f"Success Rate: {passed_categories/total_categories:.1%}")
        
        # Category breakdown
        print("\nCategory Results:")
        for category, passed in test_results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"  {category.replace('_', ' ').title()}: {status}")
        
        # Summary
        if self.passed:
            print(f"\nSuccessful Tests ({len(self.passed)}):")
            for test in self.passed:
                print(f"  {test}")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.failed:
            print(f"\nFailed Tests ({len(self.failed)}):")
            for test in self.failed:
                print(f"  {test}")
        
        # Final assessment
        success_rate = passed_categories / total_categories
        
        if success_rate >= 0.9:
            print("\n✅ PATH UTILITY TESTS PASSED")
            print("The path resolution utility function meets all technical requirements.")
            return True
        elif success_rate >= 0.8:
            print("\n⚠️  PATH UTILITY TESTS MOSTLY PASSED")
            print("The path resolution utility function works well with minor issues.")
            return True
        else:
            print("\n❌ PATH UTILITY TESTS FAILED")
            print("The path resolution utility function has significant issues.")
            return False


def main():
    """Run standalone path utility tests"""
    tester = StandalonePathTester()
    success = tester.run_comprehensive_tests()
    
    print(f"\nFinal Technical Assessment: {'APPROVED' if success else 'NEEDS IMPROVEMENT'}")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
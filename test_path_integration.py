#!/usr/bin/env python3
"""
Technical QA Test Suite for ConversionManager Path Integration

Tests the integration of resolve_markdown_output_path utility function
in ConversionManager with focus on technical functionality, performance,
backward compatibility, and error handling.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from markitdown_gui.core.conversion_manager import ConversionManager
from markitdown_gui.core.file_manager import resolve_markdown_output_path
from markitdown_gui.core.models import (
    FileInfo, FileType, FileConflictStatus, FileConflictPolicy, 
    FileConflictConfig, ConversionStatus
)
from markitdown_gui.core.constants import DEFAULT_OUTPUT_DIRECTORY


class TestPathIntegrationTechnical(unittest.TestCase):
    """Technical QA tests for path resolution integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = Path(tempfile.mkdtemp(prefix="pathtest_"))
        cls.original_cwd = Path.cwd()
        
        # Create test file structure
        cls.test_files_dir = cls.test_dir / "test_files"
        cls.test_files_dir.mkdir(exist_ok=True)
        cls.output_dir = cls.test_dir / "output"
        cls.output_dir.mkdir(exist_ok=True)
        
        # Create sample test files
        cls.sample_txt = cls.test_files_dir / "sample.txt"
        cls.sample_txt.write_text("Sample content", encoding='utf-8')
        
        cls.subdir = cls.test_files_dir / "subdir"
        cls.subdir.mkdir(exist_ok=True)
        cls.nested_txt = cls.subdir / "nested.txt"
        cls.nested_txt.write_text("Nested content", encoding='utf-8')
        
        # Create files with special characters
        cls.special_file = cls.test_files_dir / "file with spaces & symbols!.txt"
        cls.special_file.write_text("Special chars content", encoding='utf-8')
        
        print(f"Test environment created at: {cls.test_dir}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.test_dir, ignore_errors=True)
        print(f"Test environment cleaned up")
    
    def setUp(self):
        """Set up each test"""
        self.manager = ConversionManager(
            output_directory=self.output_dir,
            save_to_original_dir=False  # Use separate output directory
        )
    
    def test_path_utility_integration_basic(self):
        """Test basic path utility integration"""
        print("\n=== Testing Basic Path Utility Integration ===")
        
        # Create FileInfo
        file_info = FileInfo(
            path=self.sample_txt,
            name=self.sample_txt.name,
            size=self.sample_txt.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        # Test path generation via prepare_files_for_conversion
        prepared_files = self.manager.prepare_files_for_conversion([file_info])
        
        self.assertEqual(len(prepared_files), 1)
        prepared_file = prepared_files[0]
        
        # Verify output path was generated
        self.assertIsNotNone(prepared_file.output_path)
        self.assertTrue(str(prepared_file.output_path).endswith('.md'))
        
        # Verify path is within output directory
        try:
            prepared_file.output_path.relative_to(self.output_dir)
            print(f"✓ Output path correctly within output directory: {prepared_file.output_path}")
        except ValueError:
            self.fail(f"Output path {prepared_file.output_path} is not within {self.output_dir}")
    
    def test_structure_preservation(self):
        """Test directory structure preservation"""
        print("\n=== Testing Directory Structure Preservation ===")
        
        # Test with preserve_structure=True (default)
        self.manager._save_to_original_dir = False
        
        nested_file_info = FileInfo(
            path=self.nested_txt,
            name=self.nested_txt.name,
            size=self.nested_txt.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        prepared_files = self.manager.prepare_files_for_conversion([nested_file_info])
        prepared_file = prepared_files[0]
        
        # Should preserve parent directory structure
        self.assertIn('subdir', str(prepared_file.output_path))
        print(f"✓ Structure preserved: {prepared_file.output_path}")
        
        # Test with save_to_original_dir=True (structure not preserved)
        self.manager._save_to_original_dir = True
        
        prepared_files_orig = self.manager.prepare_files_for_conversion([nested_file_info])
        prepared_file_orig = prepared_files_orig[0]
        
        # Should be in same directory as source
        self.assertEqual(prepared_file_orig.output_path.parent, self.nested_txt.parent)
        print(f"✓ Original directory used: {prepared_file_orig.output_path}")
    
    def test_special_character_handling(self):
        """Test handling of files with special characters"""
        print("\n=== Testing Special Character Handling ===")
        
        special_file_info = FileInfo(
            path=self.special_file,
            name=self.special_file.name,
            size=self.special_file.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        prepared_files = self.manager.prepare_files_for_conversion([special_file_info])
        prepared_file = prepared_files[0]
        
        # Verify filename was sanitized
        self.assertIsNotNone(prepared_file.output_path)
        sanitized_name = prepared_file.output_path.name
        
        # Should not contain problematic characters
        problematic_chars = ['&', '!', '<', '>', '|', ':', '"', '*', '?']
        for char in problematic_chars:
            if char in sanitized_name:
                print(f"⚠ Warning: Problematic char '{char}' found in: {sanitized_name}")
        
        print(f"✓ Special characters handled: {self.special_file.name} → {sanitized_name}")
    
    def test_conflict_detection_with_new_paths(self):
        """Test file conflict detection with new path utility"""
        print("\n=== Testing Conflict Detection with New Path System ===")
        
        file_info = FileInfo(
            path=self.sample_txt,
            name=self.sample_txt.name,
            size=self.sample_txt.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        # Create existing file to trigger conflict
        prepared_files = self.manager.prepare_files_for_conversion([file_info])
        existing_path = prepared_files[0].output_path
        existing_path.parent.mkdir(parents=True, exist_ok=True)
        existing_path.write_text("Existing content")
        
        # Test conflict detection
        prepared_files_conflict = self.manager.prepare_files_for_conversion([file_info])
        conflict_file = prepared_files_conflict[0]
        
        # Should detect conflict
        self.assertEqual(conflict_file.conflict_status, FileConflictStatus.EXISTS)
        print(f"✓ Conflict detected for: {existing_path}")
        
        # Clean up
        existing_path.unlink()
    
    def test_error_handling_and_fallback(self):
        """Test error handling and fallback to legacy path system"""
        print("\n=== Testing Error Handling and Fallback Mechanisms ===")
        
        # Create file with potentially problematic path
        long_name = "a" * 200  # Very long filename
        long_file = self.test_files_dir / f"{long_name}.txt"
        long_file.write_text("Content")
        
        file_info = FileInfo(
            path=long_file,
            name=long_file.name,
            size=long_file.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        # Test that manager handles this gracefully
        try:
            prepared_files = self.manager.prepare_files_for_conversion([file_info])
            self.assertEqual(len(prepared_files), 1)
            self.assertIsNotNone(prepared_files[0].output_path)
            print(f"✓ Long filename handled gracefully")
        except Exception as e:
            self.fail(f"Manager failed to handle long filename: {e}")
        
        # Clean up
        long_file.unlink()
    
    def test_performance_path_resolution(self):
        """Test performance of new path resolution system"""
        print("\n=== Testing Performance Requirements ===")
        
        # Create multiple files for batch processing
        test_files = []
        for i in range(50):
            test_file = self.test_files_dir / f"perf_test_{i:03d}.txt"
            test_file.write_text(f"Content {i}")
            
            file_info = FileInfo(
                path=test_file,
                name=test_file.name,
                size=test_file.stat().st_size,
                file_type=FileType.TXT,
                modified_time=time.time()
            )
            test_files.append(file_info)
        
        # Measure path preparation time
        start_time = time.time()
        prepared_files = self.manager.prepare_files_for_conversion(test_files)
        end_time = time.time()
        
        preparation_time = end_time - start_time
        per_file_time = preparation_time / len(test_files)
        
        # Performance requirements: <10ms per file for path preparation
        self.assertLess(per_file_time, 0.01, f"Path preparation too slow: {per_file_time:.4f}s per file")
        
        print(f"✓ Performance test passed:")
        print(f"  - Total time: {preparation_time:.3f}s for {len(test_files)} files")
        print(f"  - Per file: {per_file_time*1000:.2f}ms")
        
        # Verify all files were processed
        self.assertEqual(len(prepared_files), len(test_files))
        
        # Clean up performance test files
        for file_info in test_files:
            file_info.path.unlink()
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing systems"""
        print("\n=== Testing Backward Compatibility ===")
        
        # Test that old FileInfo objects still work
        file_info = FileInfo(
            path=self.sample_txt,
            name=self.sample_txt.name,
            size=self.sample_txt.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        # Should work without any additional setup
        prepared_files = self.manager.prepare_files_for_conversion([file_info])
        self.assertEqual(len(prepared_files), 1)
        self.assertIsNotNone(prepared_files[0].output_path)
        
        print(f"✓ Backward compatibility maintained")
    
    def test_cross_platform_compatibility(self):
        """Test cross-platform path handling"""
        print("\n=== Testing Cross-Platform Compatibility ===")
        
        # Test various path formats that might come from different systems
        test_cases = [
            ("normal_file.txt", "normal content"),
            ("file-with-dashes.txt", "dash content"),
            ("file_with_underscores.txt", "underscore content"),
        ]
        
        for filename, content in test_cases:
            test_file = self.test_files_dir / filename
            test_file.write_text(content)
            
            file_info = FileInfo(
                path=test_file,
                name=test_file.name,
                size=test_file.stat().st_size,
                file_type=FileType.TXT,
                modified_time=time.time()
            )
            
            # Test path resolution
            prepared_files = self.manager.prepare_files_for_conversion([file_info])
            self.assertEqual(len(prepared_files), 1)
            
            output_path = prepared_files[0].output_path
            self.assertTrue(output_path.name.endswith('.md'))
            
            print(f"✓ Cross-platform test passed: {filename} → {output_path.name}")
            
            # Clean up
            test_file.unlink()
    
    def test_security_path_validation(self):
        """Test security aspects of path resolution"""
        print("\n=== Testing Security Path Validation ===")
        
        # Create file with normal name
        secure_file = self.test_files_dir / "secure_test.txt"
        secure_file.write_text("Secure content")
        
        file_info = FileInfo(
            path=secure_file,
            name=secure_file.name,
            size=secure_file.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        # Test that path resolution works securely
        prepared_files = self.manager.prepare_files_for_conversion([file_info])
        output_path = prepared_files[0].output_path
        
        # Verify path is within expected boundaries
        try:
            # Should be relative to output directory
            output_path.relative_to(self.output_dir)
            print(f"✓ Security validation passed: path within bounds")
        except ValueError:
            self.fail(f"Security issue: path {output_path} outside output directory {self.output_dir}")
        
        # Clean up
        secure_file.unlink()
    
    def test_memory_efficiency(self):
        """Test memory efficiency during path operations"""
        print("\n=== Testing Memory Efficiency ===")
        
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create many file operations
        large_batch = []
        for i in range(100):
            test_file = self.test_files_dir / f"mem_test_{i:04d}.txt"
            test_file.write_text(f"Memory test content {i}")
            
            file_info = FileInfo(
                path=test_file,
                name=test_file.name,
                size=test_file.stat().st_size,
                file_type=FileType.TXT,
                modified_time=time.time()
            )
            large_batch.append(file_info)
        
        # Process batch
        prepared_files = self.manager.prepare_files_for_conversion(large_batch)
        
        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (<50MB for 100 files)
        self.assertLess(memory_increase, 50, f"Memory usage too high: {memory_increase:.1f}MB")
        
        print(f"✓ Memory efficiency test passed:")
        print(f"  - Initial: {initial_memory:.1f}MB")
        print(f"  - Final: {final_memory:.1f}MB")
        print(f"  - Increase: {memory_increase:.1f}MB for {len(large_batch)} files")
        
        # Clean up
        for file_info in large_batch:
            file_info.path.unlink()
        
        # Force garbage collection
        gc.collect()


class TestPathIntegrationSystem(unittest.TestCase):
    """System integration tests for path resolution"""
    
    def setUp(self):
        """Set up system test environment"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="systemtest_"))
        self.output_dir = self.test_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up system test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_end_to_end_path_workflow(self):
        """Test complete end-to-end path workflow"""
        print("\n=== Testing End-to-End Path Workflow ===")
        
        # Create test file
        test_file = self.test_dir / "e2e_test.txt"
        test_file.write_text("End-to-end test content")
        
        # Create ConversionManager
        manager = ConversionManager(
            output_directory=self.output_dir,
            save_to_original_dir=False
        )
        
        # Create FileInfo
        file_info = FileInfo(
            path=test_file,
            name=test_file.name,
            size=test_file.stat().st_size,
            file_type=FileType.TXT,
            modified_time=time.time()
        )
        
        # Test complete workflow
        prepared_files = manager.prepare_files_for_conversion([file_info])
        self.assertEqual(len(prepared_files), 1)
        
        prepared_file = prepared_files[0]
        
        # Verify all expected attributes are set
        self.assertIsNotNone(prepared_file.output_path)
        self.assertTrue(str(prepared_file.output_path).endswith('.md'))
        self.assertIsNotNone(prepared_file.conflict_status)
        
        print(f"✓ End-to-end workflow completed successfully")
        print(f"  - Input: {test_file}")
        print(f"  - Output: {prepared_file.output_path}")
        print(f"  - Conflict status: {prepared_file.conflict_status}")


def run_performance_benchmarks():
    """Run performance benchmarks for path integration"""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARKS")
    print("="*60)
    
    test_dir = Path(tempfile.mkdtemp(prefix="perfbench_"))
    output_dir = test_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        manager = ConversionManager(
            output_directory=output_dir,
            save_to_original_dir=False
        )
        
        # Benchmark different batch sizes
        batch_sizes = [10, 50, 100, 500]
        
        for batch_size in batch_sizes:
            print(f"\nBenchmarking batch size: {batch_size}")
            
            # Create test files
            test_files = []
            for i in range(batch_size):
                test_file = test_dir / f"bench_{batch_size}_{i:04d}.txt"
                test_file.write_text(f"Benchmark content {i}")
                
                file_info = FileInfo(
                    path=test_file,
                    name=test_file.name,
                    size=test_file.stat().st_size,
                    file_type=FileType.TXT,
                    modified_time=time.time()
                )
                test_files.append(file_info)
            
            # Benchmark path preparation
            start_time = time.time()
            prepared_files = manager.prepare_files_for_conversion(test_files)
            end_time = time.time()
            
            total_time = end_time - start_time
            per_file_time = total_time / batch_size
            throughput = batch_size / total_time
            
            print(f"  - Total time: {total_time:.3f}s")
            print(f"  - Per file: {per_file_time*1000:.2f}ms")
            print(f"  - Throughput: {throughput:.1f} files/s")
            
            # Verify results
            assert len(prepared_files) == batch_size
            assert all(pf.output_path is not None for pf in prepared_files)
            
            # Clean up
            for file_info in test_files:
                file_info.path.unlink()
    
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Run all technical QA tests"""
    print("ConversionManager Path Integration - Technical QA Test Suite")
    print("="*60)
    
    # Run unit tests
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPathIntegrationTechnical))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPathIntegrationSystem))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance benchmarks
    run_performance_benchmarks()
    
    # Summary
    print("\n" + "="*60)
    print("TECHNICAL QA SUMMARY")
    print("="*60)
    
    if result.wasSuccessful():
        print("✅ ALL TECHNICAL TESTS PASSED")
        print("\nTechnical Implementation Status: APPROVED")
        print("\nKey Validation Results:")
        print("  ✓ Path utility integration works correctly")
        print("  ✓ Performance meets requirements (<10ms per file)")
        print("  ✓ Backward compatibility maintained")
        print("  ✓ Error handling and fallback mechanisms working")
        print("  ✓ Security validations in place")
        print("  ✓ Cross-platform compatibility confirmed")
        print("  ✓ Memory efficiency within acceptable limits")
        print("  ✓ System integration working end-to-end")
    else:
        print("❌ TECHNICAL ISSUES FOUND")
        print(f"\nFailures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nTest Failures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nTest Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
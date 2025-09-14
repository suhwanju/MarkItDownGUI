"""
End-to-End performance benchmark tests
"""

import pytest
import time
import threading
import tracemalloc
import psutil
import os
from pathlib import Path
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from markitdown_gui.core.file_manager import FileManager
from markitdown_gui.core.conversion_manager import ConversionManager


class TestPerformanceBenchmarks:
    """Performance benchmark tests for the conversion system"""
    
    @pytest.fixture
    def performance_test_files(self, temp_dir):
        """Create files of various sizes for performance testing"""
        files = {}
        
        # Small files (< 1KB)
        for i in range(5):
            small_file = temp_dir / f"small_{i}.txt"
            small_file.write_text(f"Small test content {i}" * 10)
            files[f'small_{i}'] = str(small_file)
        
        # Medium files (10-50KB)
        for i in range(3):
            medium_file = temp_dir / f"medium_{i}.txt"
            content = f"Medium test content {i}\n" * 500
            medium_file.write_text(content)
            files[f'medium_{i}'] = str(medium_file)
        
        # Large files (100KB+)
        for i in range(2):
            large_file = temp_dir / f"large_{i}.txt"
            content = f"Large test content {i}\n" * 2000
            large_file.write_text(content)
            files[f'large_{i}'] = str(large_file)
        
        return files
    
    @pytest.fixture
    def benchmark_managers(self, config_manager):
        """Create managers configured for performance testing"""
        file_manager = FileManager()
        conversion_manager = ConversionManager(config_manager)
        
        # Configure for optimal performance
        config_manager.set_value("Conversion/max_workers", 4)
        conversion_manager.update_configuration()
        
        return file_manager, conversion_manager
    
    def test_single_file_conversion_performance(self, benchmark_managers, performance_test_files):
        """Benchmark single file conversion performance"""
        file_manager, conversion_manager = benchmark_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup fast mock conversion
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Fast conversion result"
            
            performance_results = {}
            
            # Test different file sizes
            test_categories = {
                'small': [f for f in performance_test_files.keys() if 'small' in f],
                'medium': [f for f in performance_test_files.keys() if 'medium' in f],
                'large': [f for f in performance_test_files.keys() if 'large' in f]
            }
            
            for category, file_keys in test_categories.items():
                times = []
                
                for file_key in file_keys:
                    file_path = performance_test_files[file_key]
                    
                    # Measure conversion time
                    start_time = time.perf_counter()
                    result = conversion_manager.convert_file(file_path)
                    end_time = time.perf_counter()
                    
                    conversion_time = end_time - start_time
                    times.append(conversion_time)
                    
                    # Verify successful conversion
                    assert result.status.name == "SUCCESS"
                
                # Calculate statistics
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                performance_results[category] = {
                    'avg_time': avg_time,
                    'max_time': max_time,
                    'min_time': min_time,
                    'file_count': len(times)
                }
                
                # Performance assertions
                assert avg_time < 0.1  # Average under 100ms
                assert max_time < 0.2  # Max under 200ms
                assert min_time > 0    # Positive time
            
            # Compare performance across file sizes
            assert performance_results['small']['avg_time'] <= performance_results['medium']['avg_time']
            assert performance_results['medium']['avg_time'] <= performance_results['large']['avg_time']
    
    def test_batch_conversion_performance(self, benchmark_managers, performance_test_files):
        """Benchmark batch conversion performance and parallelization"""
        file_manager, conversion_manager = benchmark_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with small delay to test parallelization
            def timed_convert(file_path):
                time.sleep(0.01)  # 10ms simulated processing time
                result = Mock()
                result.text_content = f"# Batch converted {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = timed_convert
            
            all_files = list(performance_test_files.values())
            
            # Test sequential vs parallel performance
            sequential_times = []
            parallel_times = []
            
            # Sequential processing (1 worker)
            conversion_manager.max_workers = 1
            for _ in range(3):  # Multiple runs for average
                start_time = time.perf_counter()
                results = conversion_manager.convert_files(all_files[:5])  # First 5 files
                end_time = time.perf_counter()
                
                sequential_times.append(end_time - start_time)
                assert len(results) == 5
                assert all(r.status.name == "SUCCESS" for r in results)
            
            # Parallel processing (4 workers)
            conversion_manager.max_workers = 4
            for _ in range(3):  # Multiple runs for average
                start_time = time.perf_counter()
                results = conversion_manager.convert_files(all_files[:5])  # First 5 files
                end_time = time.perf_counter()
                
                parallel_times.append(end_time - start_time)
                assert len(results) == 5
                assert all(r.status.name == "SUCCESS" for r in results)
            
            # Calculate averages
            avg_sequential = sum(sequential_times) / len(sequential_times)
            avg_parallel = sum(parallel_times) / len(parallel_times)
            
            # Parallel should be significantly faster
            speedup = avg_sequential / avg_parallel
            
            # Performance assertions
            assert avg_sequential > 0.04  # Should take time sequentially (5 * 10ms = 50ms minimum)
            assert avg_parallel < avg_sequential  # Parallel should be faster
            assert speedup > 1.5  # At least 50% speedup
            
            # Throughput calculation
            throughput_sequential = 5 / avg_sequential  # files per second
            throughput_parallel = 5 / avg_parallel
            
            assert throughput_parallel > throughput_sequential
            assert throughput_parallel > 10  # At least 10 files per second
    
    def test_memory_usage_performance(self, benchmark_managers, performance_test_files):
        """Benchmark memory usage during conversions"""
        file_manager, conversion_manager = benchmark_managers
        
        # Start memory tracing
        tracemalloc.start()
        process = psutil.Process()
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Memory test content"
            
            # Baseline memory
            baseline_memory = process.memory_info().rss
            
            # Convert all files
            all_files = list(performance_test_files.values())
            results = conversion_manager.convert_files(all_files)
            
            # Peak memory during conversion
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            process_memory = process.memory_info().rss
            
            # Memory assertions
            memory_increase = process_memory - baseline_memory
            
            # Memory usage should be reasonable
            assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
            assert peak_memory < 50 * 1024 * 1024       # Less than 50MB peak traced
            assert current_memory < 30 * 1024 * 1024    # Less than 30MB current traced
            
            # Verify conversions succeeded
            assert len(results) == len(all_files)
            assert all(r.status.name == "SUCCESS" for r in results)
            
            # Test memory cleanup
            conversion_manager.clear_results()
            tracemalloc.stop()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Memory after cleanup should be closer to baseline
            final_memory = process.memory_info().rss
            cleanup_reduction = process_memory - final_memory
            
            # Should free some memory (at least 10% of what was allocated)
            assert cleanup_reduction > memory_increase * 0.1
    
    def test_file_discovery_performance(self, benchmark_managers, temp_dir):
        """Benchmark file discovery performance with many files"""
        file_manager, conversion_manager = benchmark_managers
        
        # Create many test files
        file_count = 100
        subdirs = 5
        
        for subdir_i in range(subdirs):
            subdir = temp_dir / f"subdir_{subdir_i}"
            subdir.mkdir()
            
            for file_i in range(file_count // subdirs):
                test_file = subdir / f"test_{file_i}.txt"
                test_file.write_text(f"Test content {file_i}")
        
        file_manager.set_root_directory(str(temp_dir))
        
        # Benchmark file discovery
        discovery_times = []
        
        for _ in range(5):  # Multiple runs
            start_time = time.perf_counter()
            files = file_manager.scan_directory(include_subdirs=True)
            end_time = time.perf_counter()
            
            discovery_times.append(end_time - start_time)
            
            # Verify file count
            assert len(files) >= file_count
        
        # Calculate performance metrics
        avg_discovery_time = sum(discovery_times) / len(discovery_times)
        files_per_second = file_count / avg_discovery_time
        
        # Performance assertions
        assert avg_discovery_time < 1.0  # Should complete within 1 second
        assert files_per_second > 50     # At least 50 files per second discovery rate
        
        # Test filtering performance
        filter_times = []
        
        for _ in range(5):
            start_time = time.perf_counter()
            filtered_files = file_manager.filter_by_type(files, ['.txt'])
            end_time = time.perf_counter()
            
            filter_times.append(end_time - start_time)
            assert len(filtered_files) >= file_count
        
        avg_filter_time = sum(filter_times) / len(filter_times)
        
        # Filtering should be very fast
        assert avg_filter_time < 0.1  # Under 100ms
    
    def test_concurrent_conversion_performance(self, benchmark_managers, performance_test_files):
        """Test performance under concurrent load"""
        file_manager, conversion_manager = benchmark_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with small delay
            def concurrent_convert(file_path):
                time.sleep(0.02)  # 20ms processing time
                result = Mock()
                result.text_content = f"# Concurrent converted {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = concurrent_convert
            
            # Test different concurrency levels
            concurrency_results = {}
            test_files = list(performance_test_files.values())[:8]  # Use 8 files
            
            for workers in [1, 2, 4, 8]:
                conversion_manager.max_workers = workers
                
                times = []
                for _ in range(3):  # Multiple runs
                    start_time = time.perf_counter()
                    results = conversion_manager.convert_files(test_files)
                    end_time = time.perf_counter()
                    
                    times.append(end_time - start_time)
                    assert len(results) == len(test_files)
                    assert all(r.status.name == "SUCCESS" for r in results)
                
                avg_time = sum(times) / len(times)
                throughput = len(test_files) / avg_time
                
                concurrency_results[workers] = {
                    'avg_time': avg_time,
                    'throughput': throughput
                }
            
            # Verify concurrency improves performance
            assert concurrency_results[2]['throughput'] > concurrency_results[1]['throughput']
            assert concurrency_results[4]['throughput'] > concurrency_results[2]['throughput']
            
            # 4 workers should be close to optimal for 8 files
            optimal_throughput = concurrency_results[4]['throughput']
            assert optimal_throughput > 20  # At least 20 files per second
    
    def test_stress_test_performance(self, benchmark_managers, temp_dir):
        """Stress test with high load"""
        file_manager, conversion_manager = benchmark_managers
        
        # Create stress test scenario
        stress_file_count = 50
        stress_files = []
        
        for i in range(stress_file_count):
            stress_file = temp_dir / f"stress_{i}.txt"
            content = f"Stress test content {i}\n" * 100  # ~2KB per file
            stress_file.write_text(content)
            stress_files.append(str(stress_file))
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with variable delay
            def stress_convert(file_path):
                # Variable processing time (10-30ms)
                import random
                time.sleep(random.uniform(0.01, 0.03))
                result = Mock()
                result.text_content = f"# Stress converted {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = stress_convert
            
            # Monitor system resources during stress test
            start_cpu_percent = psutil.cpu_percent(interval=0.1)
            start_memory = psutil.Process().memory_info().rss
            
            # Run stress test
            start_time = time.perf_counter()
            results = conversion_manager.convert_files(stress_files)
            end_time = time.perf_counter()
            
            end_cpu_percent = psutil.cpu_percent(interval=0.1)
            end_memory = psutil.Process().memory_info().rss
            
            # Performance metrics
            total_time = end_time - start_time
            throughput = len(stress_files) / total_time
            cpu_usage = end_cpu_percent - start_cpu_percent
            memory_usage = end_memory - start_memory
            
            # Verify all conversions succeeded
            assert len(results) == stress_file_count
            success_count = sum(1 for r in results if r.status.name == "SUCCESS")
            assert success_count == stress_file_count
            
            # Performance assertions
            assert total_time < 10.0         # Complete within 10 seconds
            assert throughput > 5.0          # At least 5 files per second
            assert memory_usage < 200 * 1024 * 1024  # Less than 200MB memory increase
            
            # CPU usage should be reasonable (not maxing out system)
            assert abs(cpu_usage) < 80.0  # Less than 80% CPU usage difference
    
    def test_error_recovery_performance(self, benchmark_managers, performance_test_files):
        """Test performance impact of error handling"""
        file_manager, conversion_manager = benchmark_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with 50% failure rate
            def error_prone_convert(file_path):
                import random
                if random.random() < 0.5:  # 50% chance of error
                    raise Exception(f"Random error processing {Path(file_path).name}")
                
                time.sleep(0.01)  # Normal processing time
                result = Mock()
                result.text_content = f"# Error test converted {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = error_prone_convert
            
            test_files = list(performance_test_files.values())
            
            # Test performance with errors
            error_times = []
            for _ in range(5):  # Multiple runs due to randomness
                start_time = time.perf_counter()
                results = conversion_manager.convert_files(test_files)
                end_time = time.perf_counter()
                
                error_times.append(end_time - start_time)
                
                # Should have both successes and failures
                success_count = sum(1 for r in results if r.status.name == "SUCCESS")
                failure_count = sum(1 for r in results if r.status.name == "FAILED")
                
                assert len(results) == len(test_files)
                assert success_count + failure_count == len(results)
                assert failure_count > 0  # Should have some failures
            
            avg_error_time = sum(error_times) / len(error_times)
            
            # Compare with normal performance (no errors)
            mock_instance.convert.side_effect = None
            mock_instance.convert.return_value.text_content = "# Normal conversion"
            
            normal_times = []
            for _ in range(3):
                start_time = time.perf_counter()
                results = conversion_manager.convert_files(test_files)
                end_time = time.perf_counter()
                
                normal_times.append(end_time - start_time)
                assert all(r.status.name == "SUCCESS" for r in results)
            
            avg_normal_time = sum(normal_times) / len(normal_times)
            
            # Error handling should not significantly slow down processing
            performance_ratio = avg_error_time / avg_normal_time
            
            # Error handling overhead should be reasonable (less than 50% slower)
            assert performance_ratio < 1.5
            assert avg_error_time < 2.0  # Still complete within reasonable time
    
    def test_scaling_performance(self, benchmark_managers, temp_dir):
        """Test performance scaling with different file counts"""
        file_manager, conversion_manager = benchmark_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Scaling test"
            
            scaling_results = {}
            file_counts = [10, 25, 50, 100]
            
            for count in file_counts:
                # Create test files for this scale
                scale_files = []
                for i in range(count):
                    scale_file = temp_dir / f"scale_{count}_{i}.txt"
                    scale_file.write_text(f"Scaling test content {i}")
                    scale_files.append(str(scale_file))
                
                # Measure performance
                times = []
                for _ in range(3):  # Multiple runs
                    start_time = time.perf_counter()
                    results = conversion_manager.convert_files(scale_files)
                    end_time = time.perf_counter()
                    
                    times.append(end_time - start_time)
                    assert len(results) == count
                    assert all(r.status.name == "SUCCESS" for r in results)
                
                avg_time = sum(times) / len(times)
                throughput = count / avg_time
                
                scaling_results[count] = {
                    'avg_time': avg_time,
                    'throughput': throughput,
                    'time_per_file': avg_time / count
                }
                
                # Clean up files
                for file_path in scale_files:
                    Path(file_path).unlink()
            
            # Analyze scaling characteristics
            for count in file_counts:
                result = scaling_results[count]
                
                # Performance should remain reasonable at all scales
                assert result['throughput'] > 5.0  # At least 5 files/sec
                assert result['time_per_file'] < 0.2  # Less than 200ms per file
            
            # Throughput should not degrade significantly with scale
            small_scale_throughput = scaling_results[10]['throughput']
            large_scale_throughput = scaling_results[100]['throughput']
            
            # Large scale should be at least 50% of small scale throughput
            assert large_scale_throughput > small_scale_throughput * 0.5
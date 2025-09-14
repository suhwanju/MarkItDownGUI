"""
End-to-End tests for large file processing
"""

import pytest
import time
import tracemalloc
import psutil
from pathlib import Path
from unittest.mock import Mock, patch

from markitdown_gui.core.file_manager import FileManager
from markitdown_gui.core.conversion_manager import ConversionManager, ConversionStatus


class TestLargeFileProcessing:
    """Test large file processing capabilities and performance"""
    
    @pytest.fixture
    def large_test_files(self, temp_dir):
        """Create large test files for processing"""
        files = {}
        
        # 1MB text file
        mb1_file = temp_dir / "large_1mb.txt"
        content = "Line of text content for large file testing.\n" * 20000  # ~1MB
        mb1_file.write_text(content)
        files['1mb'] = str(mb1_file)
        
        # 5MB text file
        mb5_file = temp_dir / "large_5mb.txt"
        content = "Larger content line for extensive testing of file processing capabilities.\n" * 70000  # ~5MB
        mb5_file.write_text(content)
        files['5mb'] = str(mb5_file)
        
        # 10MB binary-like file
        mb10_file = temp_dir / "large_10mb.pdf"
        content = b"Binary content simulation " * 400000  # ~10MB
        mb10_file.write_bytes(content)
        files['10mb'] = str(mb10_file)
        
        return files
    
    @pytest.fixture
    def large_file_managers(self, config_manager, temp_dir):
        """Create managers optimized for large file processing"""
        file_manager = FileManager()
        conversion_manager = ConversionManager(config_manager)
        
        # Configure for large file handling
        conversion_manager.max_file_size = 50 * 1024 * 1024  # 50MB limit
        conversion_manager.max_workers = 2  # Reduce workers for memory efficiency
        conversion_manager.processing_timeout = 30.0  # Longer timeout
        
        # Set output directory
        output_dir = temp_dir / "large_output"
        output_dir.mkdir()
        config_manager.set_value("Conversion/output_dir", str(output_dir))
        
        return file_manager, conversion_manager
    
    def test_single_large_file_processing(self, large_file_managers, large_test_files):
        """Test processing single large files"""
        file_manager, conversion_manager = large_file_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock to simulate processing large content
            def large_file_convert(file_path):
                # Simulate processing time proportional to file size
                file_size = Path(file_path).stat().st_size
                processing_time = min(file_size / (10 * 1024 * 1024), 2.0)  # Max 2 seconds
                time.sleep(processing_time)
                
                result = Mock()
                result.text_content = f"# Large file converted\n\nProcessed {file_size} bytes"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = large_file_convert
            
            # Test 1MB file
            start_time = time.perf_counter()
            result_1mb = conversion_manager.convert_file(large_test_files['1mb'])
            end_time = time.perf_counter()
            
            assert result_1mb.status == ConversionStatus.SUCCESS
            assert "Large file converted" in result_1mb.content
            assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
            
            # Test 5MB file
            start_time = time.perf_counter()
            result_5mb = conversion_manager.convert_file(large_test_files['5mb'])
            end_time = time.perf_counter()
            
            assert result_5mb.status == ConversionStatus.SUCCESS
            assert "Large file converted" in result_5mb.content
            assert (end_time - start_time) < 10.0  # Should complete within 10 seconds
    
    def test_memory_usage_large_files(self, large_file_managers, large_test_files):
        """Test memory usage during large file processing"""
        file_manager, conversion_manager = large_file_managers
        
        # Start memory monitoring
        tracemalloc.start()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that simulates memory usage
            def memory_conscious_convert(file_path):
                # Simulate reading file content (memory usage)
                file_size = Path(file_path).stat().st_size
                
                # For very large files, we should stream/chunk process
                if file_size > 1024 * 1024:  # > 1MB
                    time.sleep(0.1)  # Simulate streaming processing
                
                result = Mock()
                result.text_content = f"# Memory-conscious conversion of {file_size} byte file"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = memory_conscious_convert
            
            # Process large files sequentially
            for file_key in ['1mb', '5mb']:
                result = conversion_manager.convert_file(large_test_files[file_key])
                
                # Check memory after each file
                current_memory = process.memory_info().rss
                memory_increase = current_memory - baseline_memory
                
                # Memory increase should be reasonable (< 100MB per file)
                assert memory_increase < 100 * 1024 * 1024
                assert result.status == ConversionStatus.SUCCESS
                
                # Cleanup after each file
                conversion_manager.clear_results()
        
        # Final memory check
        final_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Peak memory should be manageable
        assert peak_memory < 50 * 1024 * 1024  # Less than 50MB peak
    
    def test_large_file_batch_processing(self, large_file_managers, large_test_files):
        """Test batch processing of multiple large files"""
        file_manager, conversion_manager = large_file_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock for batch processing
            def batch_large_convert(file_path):
                file_size = Path(file_path).stat().st_size
                # Simulate proportional processing time
                processing_time = file_size / (20 * 1024 * 1024)  # 20MB/sec simulation
                time.sleep(min(processing_time, 1.0))  # Max 1 second per file
                
                result = Mock()
                result.text_content = f"# Batch converted {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = batch_large_convert
            
            # Process multiple large files
            test_files = [large_test_files['1mb'], large_test_files['5mb']]
            
            start_time = time.perf_counter()
            results = conversion_manager.convert_files(test_files)
            end_time = time.perf_counter()
            
            # All should succeed
            assert len(results) == 2
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
            
            # Batch should be faster than sequential due to parallelism
            total_time = end_time - start_time
            assert total_time < 3.0  # Should complete within 3 seconds total
            
            # Check progress was tracked
            stats = conversion_manager.get_conversion_stats()
            assert stats['successful'] == 2
            assert stats['total_files'] == 2
    
    def test_file_size_limits(self, large_file_managers, temp_dir):
        """Test file size limit enforcement"""
        file_manager, conversion_manager = large_file_managers
        
        # Create file that exceeds size limit
        oversized_file = temp_dir / "oversized.txt"
        content = "Large content " * 5000000  # Very large content
        oversized_file.write_text(content)
        
        # Set smaller size limit for testing
        conversion_manager.max_file_size = 1024 * 1024  # 1MB limit
        
        file_size = oversized_file.stat().st_size
        
        if file_size > conversion_manager.max_file_size:
            # Should reject oversized files
            result = conversion_manager.convert_file(str(oversized_file))
            
            assert result.status == ConversionStatus.FAILED
            assert "size" in result.error_message.lower()
    
    def test_large_file_progress_tracking(self, large_file_managers, large_test_files):
        """Test progress tracking for large file operations"""
        file_manager, conversion_manager = large_file_managers
        
        progress_updates = []
        
        def progress_handler(current, total, message):
            progress_updates.append({
                'current': current,
                'total': total,
                'message': message,
                'timestamp': time.perf_counter()
            })
        
        conversion_manager.progress_updated.connect(progress_handler)
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with progress simulation
            def progressive_convert(file_path):
                # Simulate multi-stage processing with progress
                time.sleep(0.2)  # Stage 1
                time.sleep(0.2)  # Stage 2
                time.sleep(0.2)  # Stage 3
                
                result = Mock()
                result.text_content = f"# Progressive conversion of {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = progressive_convert
            
            # Process large files with progress tracking
            test_files = [large_test_files['1mb'], large_test_files['5mb']]
            results = conversion_manager.convert_files(test_files)
            
            # Verify progress updates
            assert len(progress_updates) >= len(test_files)
            
            # Check progress sequence
            for i, update in enumerate(progress_updates):
                assert update['current'] <= update['total']
                assert update['total'] == len(test_files)
                
                # Progress should increase over time
                if i > 0:
                    assert update['timestamp'] >= progress_updates[i-1]['timestamp']
                    assert update['current'] >= progress_updates[i-1]['current']
            
            # All conversions should succeed
            assert len(results) == len(test_files)
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
    
    def test_large_file_cancellation(self, large_file_managers, large_test_files):
        """Test cancellation during large file processing"""
        file_manager, conversion_manager = large_file_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with long processing time
            def slow_large_convert(file_path):
                # Simulate very slow processing
                for i in range(10):
                    if conversion_manager.is_cancelled:
                        raise InterruptedError("Processing cancelled")
                    time.sleep(0.1)
                
                result = Mock()
                result.text_content = "# Slow large conversion"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = slow_large_convert
            
            # Start processing in background
            import threading
            results = []
            exception_occurred = []
            
            def background_processing():
                try:
                    result = conversion_manager.convert_file(large_test_files['5mb'])
                    results.append(result)
                except Exception as e:
                    exception_occurred.append(e)
            
            thread = threading.Thread(target=background_processing)
            thread.start()
            
            # Cancel after short delay
            time.sleep(0.2)
            conversion_manager.cancel_conversion()
            
            # Wait for completion
            thread.join(timeout=2.0)
            
            # Should have been cancelled
            assert conversion_manager.is_cancelled == True
            
            # Check results
            if results:
                # If conversion completed, it should indicate cancellation
                assert results[0].status in [ConversionStatus.FAILED, ConversionStatus.CANCELLED]
            elif exception_occurred:
                # Exception during cancellation is acceptable
                assert len(exception_occurred) > 0
    
    def test_concurrent_large_file_processing(self, large_file_managers, large_test_files):
        """Test concurrent processing of large files"""
        file_manager, conversion_manager = large_file_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with thread-safe processing
            import threading
            thread_counter = {'count': 0}
            thread_lock = threading.Lock()
            
            def concurrent_convert(file_path):
                with thread_lock:
                    thread_counter['count'] += 1
                    current_threads = thread_counter['count']
                
                # Simulate processing time
                time.sleep(0.3)
                
                with thread_lock:
                    thread_counter['count'] -= 1
                
                result = Mock()
                result.text_content = f"# Concurrent conversion (max threads: {current_threads})"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = concurrent_convert
            
            # Process multiple large files concurrently
            test_files = list(large_test_files.values())
            
            start_time = time.perf_counter()
            results = conversion_manager.convert_files(test_files)
            end_time = time.perf_counter()
            
            # All should succeed
            assert len(results) == len(test_files)
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
            
            # Should be faster than sequential processing
            total_time = end_time - start_time
            sequential_time = len(test_files) * 0.3  # 0.3s per file
            
            # Should show parallelism benefit (allow some overhead)
            assert total_time < sequential_time * 0.8
    
    def test_large_file_error_recovery(self, large_file_managers, large_test_files):
        """Test error recovery with large files"""
        file_manager, conversion_manager = large_file_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that fails on largest file but succeeds on others
            def selective_large_error(file_path):
                file_size = Path(file_path).stat().st_size
                
                if file_size > 2 * 1024 * 1024:  # Files larger than 2MB fail
                    raise MemoryError(f"Mock memory error for large file: {file_size} bytes")
                else:
                    result = Mock()
                    result.text_content = f"# Success for smaller file"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = selective_large_error
            
            # Process mixed batch
            test_files = [large_test_files['1mb'], large_test_files['5mb'], large_test_files['10mb']]
            results = conversion_manager.convert_files(test_files)
            
            assert len(results) == 3
            
            # Check results by file size
            for result in results:
                file_size = Path(result.input_file).stat().st_size
                
                if file_size <= 2 * 1024 * 1024:  # <= 2MB
                    assert result.status == ConversionStatus.SUCCESS
                else:  # > 2MB
                    assert result.status == ConversionStatus.FAILED
                    assert "memory" in result.error_message.lower()
            
            # Verify partial success statistics
            stats = conversion_manager.get_conversion_stats()
            assert stats['successful'] >= 1  # At least 1MB file succeeded
            assert stats['failed'] >= 2      # 5MB and 10MB files failed
    
    def test_large_file_cleanup(self, large_file_managers, large_test_files):
        """Test resource cleanup after large file processing"""
        file_manager, conversion_manager = large_file_managers
        
        import gc
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that creates temporary data
            def cleanup_test_convert(file_path):
                # Simulate creating temporary data during processing
                temp_data = [i for i in range(100000)]  # Create some data
                
                result = Mock()
                result.text_content = f"# Cleanup test for {Path(file_path).name}"
                result._temp_data = temp_data  # Attach data to result
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = cleanup_test_convert
            
            # Process files
            results = conversion_manager.convert_files(list(large_test_files.values()))
            
            # All should succeed
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
            
            # Results should contain temporary data
            assert all(hasattr(r, '_temp_data') for r in results)
            
            # Clear results and cleanup
            conversion_manager.clear_results()
            conversion_manager.cleanup()
            
            # Force garbage collection
            gc.collect()
            
            # Verify cleanup (results should be cleared)
            assert len(conversion_manager.conversion_results) == 0
    
    def test_large_file_streaming_simulation(self, large_file_managers, large_test_files):
        """Test streaming-like processing of large files"""
        file_manager, conversion_manager = large_file_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that simulates streaming/chunked processing
            def streaming_convert(file_path):
                file_size = Path(file_path).stat().st_size
                chunk_size = 1024 * 1024  # 1MB chunks
                chunks = (file_size + chunk_size - 1) // chunk_size  # Ceiling division
                
                # Simulate processing chunks
                processed_content = []
                for chunk_i in range(chunks):
                    time.sleep(0.01)  # Small delay per chunk
                    processed_content.append(f"Chunk {chunk_i + 1}/{chunks}")
                
                result = Mock()
                result.text_content = f"# Streamed conversion\n\n" + "\n".join(processed_content)
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = streaming_convert
            
            # Test streaming on largest file
            start_time = time.perf_counter()
            result = conversion_manager.convert_file(large_test_files['10mb'])
            end_time = time.perf_counter()
            
            # Should succeed
            assert result.status == ConversionStatus.SUCCESS
            assert "Streamed conversion" in result.content
            assert "Chunk" in result.content
            
            # Should complete in reasonable time (streaming should be efficient)
            processing_time = end_time - start_time
            assert processing_time < 2.0  # Should complete within 2 seconds
            
            # Content should indicate chunked processing
            chunks_mentioned = result.content.count("Chunk")
            assert chunks_mentioned >= 5  # 10MB file should have multiple chunks
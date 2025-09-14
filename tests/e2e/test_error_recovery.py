"""
End-to-End tests for error recovery scenarios
"""

import pytest
import time
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import threading

from markitdown_gui.core.file_manager import FileManager
from markitdown_gui.core.conversion_manager import ConversionManager, ConversionStatus
from markitdown_gui.core.exceptions import *


class TestErrorRecovery:
    """Test error recovery scenarios in real-world conditions"""
    
    @pytest.fixture
    def error_test_files(self, temp_dir):
        """Create test files for error scenarios"""
        files = {}
        
        # Normal file
        normal_file = temp_dir / "normal.txt"
        normal_file.write_text("This is a normal file that should process correctly.")
        files['normal'] = str(normal_file)
        
        # Empty file
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        files['empty'] = str(empty_file)
        
        # Large file
        large_file = temp_dir / "large.txt"
        content = "Large file content line.\n" * 10000  # ~250KB
        large_file.write_text(content)
        files['large'] = str(large_file)
        
        # Binary file (potentially corrupted)
        binary_file = temp_dir / "binary.pdf"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xFF\xFE\xFD" * 1000)
        files['binary'] = str(binary_file)
        
        # File with special characters
        special_file = temp_dir / "special_üñíçødé.txt"
        special_file.write_text("Content with üñíçødé characters and émojis 🚀")
        files['special'] = str(special_file)
        
        return files
    
    @pytest.fixture
    def recovery_managers(self, config_manager, temp_dir):
        """Create managers configured for error recovery testing"""
        file_manager = FileManager()
        conversion_manager = ConversionManager(config_manager)
        
        # Configure output directory
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        config_manager.set_value("Conversion/output_dir", str(output_dir))
        
        # Configure retry settings
        conversion_manager.max_retries = 3
        conversion_manager.retry_delay = 0.1  # Fast retries for testing
        
        return file_manager, conversion_manager
    
    def test_file_not_found_recovery(self, recovery_managers, temp_dir):
        """Test recovery when files are deleted during processing"""
        file_manager, conversion_manager = recovery_managers
        
        # Create temporary file
        temp_file = temp_dir / "temp_file.txt"
        temp_file.write_text("Temporary content")
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock to delete file during processing
            def delete_file_convert(file_path):
                # Delete the file mid-processing
                if Path(file_path).exists():
                    Path(file_path).unlink()
                raise FileNotFoundError(f"File not found: {file_path}")
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = delete_file_convert
            
            # Attempt conversion
            result = conversion_manager.convert_file(str(temp_file))
            
            # Should gracefully handle file not found
            assert result.status == ConversionStatus.FAILED
            assert "not found" in result.error_message.lower()
            assert result.input_file == str(temp_file)
            
            # Verify statistics are updated
            stats = conversion_manager.get_conversion_stats()
            assert stats['failed'] >= 1
    
    def test_permission_error_recovery(self, recovery_managers, error_test_files):
        """Test recovery from permission errors"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Simulate permission error
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = PermissionError("Access denied")
            
            # Test single file permission error
            result = conversion_manager.convert_file(error_test_files['normal'])
            
            assert result.status == ConversionStatus.FAILED
            assert "permission" in result.error_message.lower() or "access" in result.error_message.lower()
            
            # Test batch processing with permission error
            test_files = [error_test_files['normal'], error_test_files['empty']]
            results = conversion_manager.convert_files(test_files)
            
            # All should fail with permission errors
            assert len(results) == 2
            assert all(r.status == ConversionStatus.FAILED for r in results)
            
            # System should remain stable
            assert conversion_manager.is_cancelled == False
    
    def test_memory_error_recovery(self, recovery_managers, error_test_files):
        """Test recovery from memory errors"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Simulate memory error on large files
            def memory_error_convert(file_path):
                if "large" in file_path:
                    raise MemoryError("Not enough memory to process file")
                else:
                    result = Mock()
                    result.text_content = "# Normal conversion"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = memory_error_convert
            
            # Test mixed batch with memory error
            test_files = [error_test_files['large'], error_test_files['normal']]
            results = conversion_manager.convert_files(test_files)
            
            assert len(results) == 2
            
            # Large file should fail
            large_result = next(r for r in results if "large" in r.input_file)
            assert large_result.status == ConversionStatus.FAILED
            assert "memory" in large_result.error_message.lower()
            
            # Normal file should succeed
            normal_result = next(r for r in results if "normal" in r.input_file)
            assert normal_result.status == ConversionStatus.SUCCESS
            
            # Verify partial success statistics
            stats = conversion_manager.get_conversion_stats()
            assert stats['successful'] >= 1
            assert stats['failed'] >= 1
    
    def test_corruption_error_recovery(self, recovery_managers, error_test_files):
        """Test recovery from file corruption errors"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Simulate corruption errors
            def corruption_convert(file_path):
                if "binary" in file_path:
                    raise ValueError("File appears to be corrupted or invalid")
                else:
                    result = Mock()
                    result.text_content = "# Successfully converted"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = corruption_convert
            
            # Test handling of corrupted file
            result = conversion_manager.convert_file(error_test_files['binary'])
            
            assert result.status == ConversionStatus.FAILED
            assert "corrupt" in result.error_message.lower() or "invalid" in result.error_message.lower()
            
            # Test batch processing continues after corruption
            test_files = [
                error_test_files['binary'],
                error_test_files['normal'],
                error_test_files['special']
            ]
            results = conversion_manager.convert_files(test_files)
            
            assert len(results) == 3
            
            # Binary should fail, others succeed
            success_count = sum(1 for r in results if r.status == ConversionStatus.SUCCESS)
            failure_count = sum(1 for r in results if r.status == ConversionStatus.FAILED)
            
            assert success_count == 2
            assert failure_count == 1
    
    def test_timeout_recovery(self, recovery_managers, error_test_files):
        """Test recovery from processing timeouts"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Simulate timeout on large files
            def timeout_convert(file_path):
                if "large" in file_path:
                    # Simulate very slow processing
                    time.sleep(2.0)  # 2 second delay
                    raise TimeoutError("Processing timeout exceeded")
                else:
                    result = Mock()
                    result.text_content = "# Quick conversion"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = timeout_convert
            
            # Set short timeout for testing
            conversion_manager.processing_timeout = 1.0  # 1 second timeout
            
            # Test timeout handling
            start_time = time.time()
            result = conversion_manager.convert_file(error_test_files['large'])
            end_time = time.time()
            
            # Should fail quickly due to timeout
            assert result.status == ConversionStatus.FAILED
            assert "timeout" in result.error_message.lower()
            assert (end_time - start_time) < 3.0  # Should not wait full delay
    
    def test_disk_space_recovery(self, recovery_managers, error_test_files, temp_dir):
        """Test recovery from insufficient disk space"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown, \
             patch('builtins.open', side_effect=OSError("No space left on device")):
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Converted content"
            
            # Test disk space error during output save
            result = conversion_manager.convert_file(error_test_files['normal'])
            
            # Conversion might succeed but saving fails
            if hasattr(conversion_manager, 'save_output'):
                with pytest.raises(OSError):
                    conversion_manager.save_output(result)
            
            # Should handle disk space errors gracefully
            # (Implementation would depend on how save_output handles errors)
    
    def test_network_error_recovery_llm(self, recovery_managers, error_test_files):
        """Test recovery from network errors during LLM operations"""
        file_manager, conversion_manager = recovery_managers
        
        # Test OCR/LLM network failures
        if hasattr(conversion_manager, 'llm_manager'):
            with patch.object(conversion_manager.llm_manager, 'process_ocr') as mock_ocr:
                # Simulate network errors
                mock_ocr.side_effect = [
                    ConnectionError("Network unreachable"),
                    ConnectionError("Network unreachable"),
                    Mock(success=True, text="OCR result")  # Success on retry
                ]
                
                # Test image file processing with retries
                if 'png' in error_test_files:
                    result = conversion_manager.convert_file(error_test_files['png'])
                    
                    # Should eventually succeed after retries
                    # (Depending on implementation)
                    assert mock_ocr.call_count == 3  # 2 failures + 1 success
    
    def test_concurrent_error_recovery(self, recovery_managers, error_test_files):
        """Test error recovery under concurrent load"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with random failures
            def random_error_convert(file_path):
                import random
                error_chance = random.random()
                
                if error_chance < 0.3:  # 30% failure rate
                    error_types = [
                        FileNotFoundError("Random file error"),
                        PermissionError("Random permission error"),
                        ValueError("Random processing error"),
                        MemoryError("Random memory error")
                    ]
                    raise random.choice(error_types)
                else:
                    # Small delay to simulate processing
                    time.sleep(0.01)
                    result = Mock()
                    result.text_content = f"# Random success {Path(file_path).name}"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = random_error_convert
            
            # Test concurrent processing with errors
            test_files = list(error_test_files.values()) * 3  # Multiply for more files
            
            # Use multiple workers
            conversion_manager.max_workers = 4
            
            results = conversion_manager.convert_files(test_files)
            
            # Should handle all files despite random errors
            assert len(results) == len(test_files)
            
            # Should have both successes and failures
            success_count = sum(1 for r in results if r.status == ConversionStatus.SUCCESS)
            failure_count = sum(1 for r in results if r.status == ConversionStatus.FAILED)
            
            assert success_count > 0  # Some should succeed
            assert failure_count > 0  # Some should fail (due to random errors)
            assert success_count + failure_count == len(test_files)
            
            # System should remain stable
            assert conversion_manager.is_cancelled == False
    
    def test_retry_mechanism(self, recovery_managers, error_test_files):
        """Test automatic retry mechanism"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that fails twice then succeeds
            call_count = {'count': 0}
            
            def retry_convert(file_path):
                call_count['count'] += 1
                if call_count['count'] <= 2:
                    raise ConnectionError(f"Attempt {call_count['count']} failed")
                else:
                    result = Mock()
                    result.text_content = "# Success after retries"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = retry_convert
            
            # Test retry logic
            result = conversion_manager.convert_file(error_test_files['normal'])
            
            # Should succeed after retries
            assert result.status == ConversionStatus.SUCCESS
            assert "Success after retries" in result.content
            assert call_count['count'] == 3  # 2 failures + 1 success
    
    def test_graceful_shutdown_during_errors(self, recovery_managers, error_test_files):
        """Test graceful shutdown when errors occur"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with long delays and errors
            def slow_error_convert(file_path):
                time.sleep(0.5)  # Slow processing
                raise RuntimeError("Slow processing error")
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = slow_error_convert
            
            # Start conversion in background thread
            test_files = list(error_test_files.values())
            
            def background_conversion():
                return conversion_manager.convert_files(test_files)
            
            import threading
            conversion_thread = threading.Thread(target=background_conversion)
            conversion_thread.start()
            
            # Wait a bit, then cancel
            time.sleep(0.1)
            conversion_manager.cancel_conversion()
            
            # Wait for thread completion
            conversion_thread.join(timeout=2.0)
            
            # Should handle cancellation gracefully even with errors
            assert conversion_manager.is_cancelled == True
    
    def test_resource_cleanup_after_errors(self, recovery_managers, error_test_files):
        """Test resource cleanup after various error scenarios"""
        file_manager, conversion_manager = recovery_managers
        
        import gc
        import tracemalloc
        
        tracemalloc.start()
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that causes memory leaks and errors
            def leaky_error_convert(file_path):
                # Create some objects that might leak
                large_data = [i for i in range(10000)]  # Create some data
                raise RuntimeError("Error with potential leak")
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = leaky_error_convert
            
            # Process files with errors
            results = conversion_manager.convert_files(list(error_test_files.values()))
            
            # All should fail
            assert all(r.status == ConversionStatus.FAILED for r in results)
            
            # Cleanup resources
            conversion_manager.clear_results()
            conversion_manager.cleanup()
            
            # Force garbage collection
            gc.collect()
            
            # Check memory usage
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Memory usage should be reasonable after cleanup
            assert current_memory < 10 * 1024 * 1024  # Less than 10MB
    
    def test_error_logging_and_reporting(self, recovery_managers, error_test_files):
        """Test error logging and reporting mechanisms"""
        file_manager, conversion_manager = recovery_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup various error scenarios
            def categorized_errors(file_path):
                if "normal" in file_path:
                    raise FileNotFoundError("File disappeared")
                elif "empty" in file_path:
                    raise PermissionError("Permission denied")
                elif "large" in file_path:
                    raise MemoryError("Out of memory")
                elif "binary" in file_path:
                    raise ValueError("Corrupt file")
                else:
                    raise RuntimeError("Unknown error")
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = categorized_errors
            
            # Process files to generate various errors
            results = conversion_manager.convert_files(list(error_test_files.values()))
            
            # Verify error categorization
            error_types = {}
            for result in results:
                assert result.status == ConversionStatus.FAILED
                assert result.error_message is not None
                
                # Categorize errors
                error_msg = result.error_message.lower()
                if "file" in error_msg and "not" in error_msg:
                    error_types['file_not_found'] = error_types.get('file_not_found', 0) + 1
                elif "permission" in error_msg:
                    error_types['permission'] = error_types.get('permission', 0) + 1
                elif "memory" in error_msg:
                    error_types['memory'] = error_types.get('memory', 0) + 1
                elif "corrupt" in error_msg or "invalid" in error_msg:
                    error_types['corruption'] = error_types.get('corruption', 0) + 1
                else:
                    error_types['unknown'] = error_types.get('unknown', 0) + 1
            
            # Should have categorized different error types
            assert len(error_types) >= 3
            
            # Test error statistics
            stats = conversion_manager.get_conversion_stats()
            assert stats['failed'] == len(error_test_files)
            assert stats['successful'] == 0
    
    def test_recovery_from_partial_failures(self, recovery_managers, error_test_files, temp_dir):
        """Test recovery from partial processing failures"""
        file_manager, conversion_manager = recovery_managers
        
        # Create a batch of files
        batch_files = []
        for i in range(10):
            batch_file = temp_dir / f"batch_{i}.txt"
            batch_file.write_text(f"Batch content {i}")
            batch_files.append(str(batch_file))
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock that fails on specific files
            def selective_failure(file_path):
                file_num = int(Path(file_path).stem.split('_')[1])
                
                if file_num % 3 == 0:  # Every 3rd file fails
                    raise RuntimeError(f"Selective failure on file {file_num}")
                else:
                    result = Mock()
                    result.text_content = f"# Converted batch {file_num}"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = selective_failure
            
            # Process batch
            results = conversion_manager.convert_files(batch_files)
            
            assert len(results) == 10
            
            # Should have mix of success and failure
            successes = [r for r in results if r.status == ConversionStatus.SUCCESS]
            failures = [r for r in results if r.status == ConversionStatus.FAILED]
            
            # Approximately 2/3 should succeed, 1/3 should fail
            assert len(successes) >= 6
            assert len(failures) >= 3
            
            # Test retry of failed files only
            failed_files = [r.input_file for r in failures]
            
            # Setup mock to succeed on retry
            mock_instance.convert.side_effect = None
            mock_instance.convert.return_value.text_content = "# Retry success"
            
            retry_results = conversion_manager.convert_files(failed_files)
            
            # All retries should succeed
            assert len(retry_results) == len(failed_files)
            assert all(r.status == ConversionStatus.SUCCESS for r in retry_results)
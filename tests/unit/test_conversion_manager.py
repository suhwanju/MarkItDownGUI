"""
Unit tests for ConversionManager
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import asyncio
from pathlib import Path

from markitdown_gui.core.conversion_manager import ConversionManager, ConversionResult, ConversionStatus
from markitdown_gui.core.exceptions import ConversionError, UnsupportedFileTypeError, FileSizeError


class TestConversionManager:
    """Test suite for ConversionManager"""
    
    def test_initialization(self, conversion_manager):
        """Test ConversionManager initialization"""
        assert conversion_manager is not None
        assert conversion_manager.config_manager is not None
        assert conversion_manager.max_workers > 0
        assert conversion_manager.conversion_results == []
    
    def test_supported_formats(self, conversion_manager):
        """Test supported file format detection"""
        # Should support common document formats
        assert conversion_manager.is_supported('.pdf') == True
        assert conversion_manager.is_supported('.docx') == True
        assert conversion_manager.is_supported('.xlsx') == True
        assert conversion_manager.is_supported('.pptx') == True
        assert conversion_manager.is_supported('.txt') == True
        assert conversion_manager.is_supported('.md') == True
        
        # Should support image formats
        assert conversion_manager.is_supported('.png') == True
        assert conversion_manager.is_supported('.jpg') == True
        assert conversion_manager.is_supported('.jpeg') == True
        
        # Should not support unsupported formats
        assert conversion_manager.is_supported('.xyz') == False
        assert conversion_manager.is_supported('.bin') == False
    
    @patch('markitdown_gui.core.conversion_manager.MarkItDown')
    def test_single_file_conversion_success(self, mock_markitdown, conversion_manager, temp_dir):
        """Test successful single file conversion"""
        # Setup mock
        mock_instance = mock_markitdown.return_value
        mock_instance.convert.return_value.text_content = "# Test Content\n\nConverted successfully"
        
        # Create test file
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b"Test PDF content")
        
        # Convert file
        result = conversion_manager.convert_file(str(test_file))
        
        # Verify result
        assert result is not None
        assert result.status == ConversionStatus.SUCCESS
        assert result.input_file == str(test_file)
        assert "Test Content" in result.content
        assert result.error_message is None
        
        # Verify MarkItDown was called
        mock_instance.convert.assert_called_once_with(str(test_file))
    
    @patch('markitdown_gui.core.conversion_manager.MarkItDown')
    def test_single_file_conversion_failure(self, mock_markitdown, conversion_manager, temp_dir):
        """Test failed single file conversion"""
        # Setup mock to raise exception
        mock_instance = mock_markitdown.return_value
        mock_instance.convert.side_effect = Exception("Conversion failed")
        
        # Create test file
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b"Test PDF content")
        
        # Convert file
        result = conversion_manager.convert_file(str(test_file))
        
        # Verify result
        assert result is not None
        assert result.status == ConversionStatus.FAILED
        assert result.input_file == str(test_file)
        assert result.content is None
        assert "Conversion failed" in result.error_message
    
    def test_unsupported_file_conversion(self, conversion_manager, temp_dir):
        """Test conversion of unsupported file type"""
        # Create unsupported file
        test_file = temp_dir / "test.xyz"
        test_file.write_bytes(b"Unsupported content")
        
        # Should raise exception
        with pytest.raises(UnsupportedFileTypeError):
            conversion_manager.convert_file(str(test_file))
    
    def test_nonexistent_file_conversion(self, conversion_manager, temp_dir):
        """Test conversion of non-existent file"""
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        
        result = conversion_manager.convert_file(nonexistent_file)
        
        assert result.status == ConversionStatus.FAILED
        assert "not found" in result.error_message.lower()
    
    def test_file_size_limit(self, conversion_manager, temp_dir):
        """Test file size limit enforcement"""
        # Create large file (simulate)
        test_file = temp_dir / "large.pdf"
        test_file.write_bytes(b"x" * (100 * 1024 * 1024))  # 100MB
        
        # Set small file size limit
        conversion_manager.max_file_size = 50 * 1024 * 1024  # 50MB
        
        with pytest.raises(FileSizeError):
            conversion_manager.convert_file(str(test_file))
    
    @patch('markitdown_gui.core.conversion_manager.MarkItDown')
    def test_batch_conversion(self, mock_markitdown, conversion_manager, temp_dir):
        """Test batch file conversion"""
        # Setup mock
        mock_instance = mock_markitdown.return_value
        mock_instance.convert.return_value.text_content = "# Converted Content"
        
        # Create multiple test files
        files = []
        for i in range(5):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test content {i}")
            files.append(str(test_file))
        
        # Convert files
        results = conversion_manager.convert_files(files)
        
        # Verify results
        assert len(results) == 5
        assert all(r.status == ConversionStatus.SUCCESS for r in results)
        assert all("Converted Content" in r.content for r in results)
        
        # Verify MarkItDown was called for each file
        assert mock_instance.convert.call_count == 5
    
    @patch('markitdown_gui.core.conversion_manager.MarkItDown')
    def test_batch_conversion_partial_failure(self, mock_markitdown, conversion_manager, temp_dir):
        """Test batch conversion with some failures"""
        # Setup mock to fail on second file
        mock_instance = mock_markitdown.return_value
        def side_effect(file_path):
            if "test_1.pdf" in file_path:
                raise Exception("Simulated failure")
            result = Mock()
            result.text_content = "# Converted Content"
            return result
        
        mock_instance.convert.side_effect = side_effect
        
        # Create test files
        files = []
        for i in range(3):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test content")
            files.append(str(test_file))
        
        # Convert files
        results = conversion_manager.convert_files(files)
        
        # Verify mixed results
        assert len(results) == 3
        success_count = sum(1 for r in results if r.status == ConversionStatus.SUCCESS)
        failure_count = sum(1 for r in results if r.status == ConversionStatus.FAILED)
        
        assert success_count == 2
        assert failure_count == 1
    
    def test_conversion_cancellation(self, conversion_manager, temp_dir):
        """Test conversion cancellation"""
        # Create test files
        files = []
        for i in range(10):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test content")
            files.append(str(test_file))
        
        # Start conversion in background
        conversion_manager.start_batch_conversion(files)
        
        # Cancel immediately
        conversion_manager.cancel_conversion()
        
        # Wait a bit and check status
        import time
        time.sleep(0.1)
        
        assert conversion_manager.is_cancelled == True
    
    def test_progress_tracking(self, conversion_manager, temp_dir):
        """Test conversion progress tracking"""
        progress_updates = []
        
        def progress_callback(current, total, message):
            progress_updates.append((current, total, message))
        
        conversion_manager.progress_updated.connect(progress_callback)
        
        # Create test files
        files = []
        for i in range(3):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test content")
            files.append(str(test_file))
        
        # Mock successful conversions
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Converted"
            
            # Convert files
            results = conversion_manager.convert_files(files)
        
        # Check progress updates were sent
        assert len(progress_updates) > 0
        
        # Should have final progress update
        final_progress = progress_updates[-1]
        assert final_progress[0] == final_progress[1]  # current == total
    
    def test_retry_logic(self, conversion_manager, temp_dir):
        """Test retry logic for failed conversions"""
        conversion_manager.max_retries = 2
        
        # Create test file
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b"Test content")
        
        # Mock to fail twice then succeed
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            
            call_count = 0
            def side_effect(file_path):
                nonlocal call_count
                call_count += 1
                if call_count <= 2:
                    raise Exception("Temporary failure")
                result = Mock()
                result.text_content = "# Success after retry"
                return result
            
            mock_instance.convert.side_effect = side_effect
            
            # Convert file
            result = conversion_manager.convert_file(str(test_file))
            
            # Should succeed after retries
            assert result.status == ConversionStatus.SUCCESS
            assert "Success after retry" in result.content
            assert mock_instance.convert.call_count == 3  # 1 initial + 2 retries
    
    def test_output_directory_creation(self, conversion_manager, temp_dir):
        """Test output directory creation"""
        output_dir = temp_dir / "output" / "nested"
        
        # Should create nested directories
        conversion_manager.ensure_output_directory(str(output_dir))
        
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_filename_sanitization(self, conversion_manager):
        """Test filename sanitization for output files"""
        # Test various problematic filenames
        test_cases = [
            ("file with spaces.pdf", "file_with_spaces.md"),
            ("file/with/slashes.docx", "file_with_slashes.md"),
            ("file:with:colons.xlsx", "file_with_colons.md"),
            ("file<with>brackets.pptx", "file_with_brackets.md"),
            ("file\"with\"quotes.txt", "file_with_quotes.md"),
        ]
        
        for input_name, expected in test_cases:
            result = conversion_manager.sanitize_filename(input_name)
            assert result == expected
    
    def test_conversion_statistics(self, conversion_manager, temp_dir):
        """Test conversion statistics tracking"""
        # Initially no stats
        stats = conversion_manager.get_conversion_stats()
        assert stats['total_files'] == 0
        assert stats['successful'] == 0
        assert stats['failed'] == 0
        
        # Create and convert files
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            
            # Mock mixed results
            def side_effect(file_path):
                if "fail" in file_path:
                    raise Exception("Simulated failure")
                result = Mock()
                result.text_content = "# Converted"
                return result
            
            mock_instance.convert.side_effect = side_effect
            
            # Create test files
            success_file = temp_dir / "success.pdf"
            success_file.write_bytes(b"content")
            
            fail_file = temp_dir / "fail.pdf"
            fail_file.write_bytes(b"content")
            
            # Convert files
            conversion_manager.convert_file(str(success_file))
            conversion_manager.convert_file(str(fail_file))
        
        # Check updated stats
        stats = conversion_manager.get_conversion_stats()
        assert stats['total_files'] == 2
        assert stats['successful'] == 1
        assert stats['failed'] == 1
    
    def test_memory_cleanup(self, conversion_manager, temp_dir):
        """Test memory cleanup after conversions"""
        # Create many files to convert
        files = []
        for i in range(50):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test content")
            files.append(str(test_file))
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Converted"
            
            # Convert files
            results = conversion_manager.convert_files(files)
        
        # Clear results to free memory
        conversion_manager.clear_results()
        
        # Check results are cleared
        assert len(conversion_manager.conversion_results) == 0
        
        # But return value should still be intact
        assert len(results) == 50
    
    def test_concurrent_conversions(self, conversion_manager, temp_dir):
        """Test concurrent file conversions"""
        conversion_manager.max_workers = 3
        
        # Create test files
        files = []
        for i in range(10):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test content")
            files.append(str(test_file))
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            
            # Add delay to simulate work
            def slow_convert(file_path):
                import time
                time.sleep(0.01)  # Small delay
                result = Mock()
                result.text_content = f"# Converted {Path(file_path).name}"
                return result
            
            mock_instance.convert.side_effect = slow_convert
            
            # Measure conversion time
            import time
            start_time = time.time()
            results = conversion_manager.convert_files(files)
            end_time = time.time()
            
            # Should be faster than sequential (but allow some overhead)
            sequential_time = len(files) * 0.01  # Minimum time if sequential
            actual_time = end_time - start_time
            
            # With 3 workers, should be significantly faster
            assert actual_time < sequential_time * 0.7  # At least 30% faster
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
    
    def test_error_recovery(self, conversion_manager, temp_dir):
        """Test error recovery mechanisms"""
        # Test recovery from various error conditions
        
        # 1. Corrupted file
        corrupted_file = temp_dir / "corrupted.pdf"
        corrupted_file.write_bytes(b"Not a valid PDF")
        
        # Should handle gracefully
        result = conversion_manager.convert_file(str(corrupted_file))
        assert result.status == ConversionStatus.FAILED
        assert result.error_message is not None
        
        # 2. Permission denied (simulate)
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = conversion_manager.convert_file(str(corrupted_file))
            assert result.status == ConversionStatus.FAILED
            assert "permission" in result.error_message.lower()
        
        # 3. Out of memory (simulate)
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = MemoryError("Out of memory")
            
            result = conversion_manager.convert_file(str(corrupted_file))
            assert result.status == ConversionStatus.FAILED
            assert "memory" in result.error_message.lower()
    
    def test_cleanup(self, conversion_manager):
        """Test proper cleanup of resources"""
        # Add some results
        conversion_manager.conversion_results = [Mock(), Mock(), Mock()]
        
        # Cleanup
        conversion_manager.cleanup()
        
        # Results should be cleared
        assert len(conversion_manager.conversion_results) == 0
        
        # Should not raise any errors
        conversion_manager.cleanup()  # Second cleanup should be safe
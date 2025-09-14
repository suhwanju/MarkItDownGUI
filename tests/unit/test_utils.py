"""
Unit tests for utility functions
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

from markitdown_gui.core.utils import (
    format_file_size, validate_file_path, detect_file_encoding,
    safe_filename, calculate_md5_hash, is_binary_file,
    get_file_type_icon, format_duration, parse_file_filters,
    sanitize_html, truncate_text, get_system_info,
    create_backup_filename, is_image_file, get_file_mime_type
)
from markitdown_gui.core.exceptions import InvalidPathError, ValidationError


class TestUtilityFunctions:
    """Test suite for utility functions"""
    
    def test_format_file_size(self):
        """Test file size formatting"""
        # Test bytes
        assert format_file_size(0) == "0 B"
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"
        
        # Test kilobytes
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(2048) == "2.0 KB"
        
        # Test megabytes
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536 * 1024) == "1.5 MB"
        
        # Test gigabytes
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1536 * 1024 * 1024) == "1.5 GB"
        
        # Test terabytes
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
        
        # Test negative values
        assert format_file_size(-1) == "0 B"
    
    def test_validate_file_path(self, temp_dir):
        """Test file path validation"""
        # Valid existing file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        assert validate_file_path(str(test_file)) == True
        
        # Valid existing directory
        assert validate_file_path(str(temp_dir)) == True
        
        # Non-existent path
        non_existent = temp_dir / "nonexistent.txt"
        assert validate_file_path(str(non_existent)) == False
        
        # Invalid path format
        assert validate_file_path("") == False
        assert validate_file_path(None) == False
        
        # Path with invalid characters (platform dependent)
        if Path.cwd().drive:  # Windows
            assert validate_file_path("C:\\invalid<>path.txt") == False
    
    def test_detect_file_encoding(self, temp_dir):
        """Test file encoding detection"""
        # UTF-8 file
        utf8_file = temp_dir / "utf8.txt"
        utf8_file.write_text("Hello 世界", encoding='utf-8')
        
        encoding = detect_file_encoding(str(utf8_file))
        assert encoding.lower() in ['utf-8', 'utf-8-sig']
        
        # ASCII file
        ascii_file = temp_dir / "ascii.txt"
        ascii_file.write_text("Hello World", encoding='ascii')
        
        encoding = detect_file_encoding(str(ascii_file))
        assert encoding.lower() in ['ascii', 'utf-8']  # ASCII is subset of UTF-8
        
        # Binary file should return None or 'binary'
        binary_file = temp_dir / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xFF\xFE')
        
        encoding = detect_file_encoding(str(binary_file))
        assert encoding is None or encoding.lower() == 'binary'
    
    def test_safe_filename(self):
        """Test filename sanitization"""
        # Test various problematic characters
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("file/with/slashes.txt", "file_with_slashes.txt"),
            ("file\\with\\backslashes.txt", "file_with_backslashes.txt"),
            ("file:with:colons.txt", "file_with_colons.txt"),
            ("file*with*stars.txt", "file_with_stars.txt"),
            ("file?with?questions.txt", "file_with_questions.txt"),
            ("file\"with\"quotes.txt", "file_with_quotes.txt"),
            ("file<with>brackets.txt", "file_with_brackets.txt"),
            ("file|with|pipes.txt", "file_with_pipes.txt"),
        ]
        
        for input_name, expected in test_cases:
            result = safe_filename(input_name)
            assert result == expected
        
        # Test length limits
        long_name = "a" * 300 + ".txt"
        result = safe_filename(long_name)
        assert len(result) <= 255  # Typical filesystem limit
        
        # Test empty filename
        assert safe_filename("") == "untitled"
        assert safe_filename(None) == "untitled"
    
    def test_calculate_md5_hash(self, temp_dir):
        """Test MD5 hash calculation"""
        # Create test file with known content
        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        # Calculate hash
        hash_result = calculate_md5_hash(str(test_file))
        
        # Verify hash is correct format (32 hex characters)
        assert len(hash_result) == 32
        assert all(c in '0123456789abcdef' for c in hash_result.lower())
        
        # Same content should produce same hash
        test_file2 = temp_dir / "test2.txt"
        test_file2.write_text(test_content)
        
        hash_result2 = calculate_md5_hash(str(test_file2))
        assert hash_result == hash_result2
        
        # Different content should produce different hash
        test_file3 = temp_dir / "test3.txt"
        test_file3.write_text("Different content")
        
        hash_result3 = calculate_md5_hash(str(test_file3))
        assert hash_result != hash_result3
        
        # Non-existent file should return None
        non_existent = str(temp_dir / "nonexistent.txt")
        assert calculate_md5_hash(non_existent) is None
    
    def test_is_binary_file(self, temp_dir):
        """Test binary file detection"""
        # Text file
        text_file = temp_dir / "text.txt"
        text_file.write_text("This is a text file with normal characters.")
        
        assert is_binary_file(str(text_file)) == False
        
        # Binary file
        binary_file = temp_dir / "binary.bin"
        binary_file.write_bytes(bytes(range(256)))  # All possible byte values
        
        assert is_binary_file(str(binary_file)) == True
        
        # File with some null bytes (common in binary files)
        mixed_file = temp_dir / "mixed.dat"
        mixed_file.write_bytes(b"Text content\x00\x01\x02with binary data")
        
        assert is_binary_file(str(mixed_file)) == True
        
        # Empty file should be considered text
        empty_file = temp_dir / "empty.txt"
        empty_file.write_bytes(b"")
        
        assert is_binary_file(str(empty_file)) == False
    
    def test_get_file_type_icon(self):
        """Test file type icon mapping"""
        # Test common file types
        assert get_file_type_icon('.pdf') == '📄'
        assert get_file_type_icon('.docx') == '📝'
        assert get_file_type_icon('.xlsx') == '📊'
        assert get_file_type_icon('.pptx') == '📈'
        assert get_file_type_icon('.txt') == '📄'
        assert get_file_type_icon('.md') == '📝'
        
        # Test image types
        assert get_file_type_icon('.png') == '🖼️'
        assert get_file_type_icon('.jpg') == '🖼️'
        assert get_file_type_icon('.gif') == '🖼️'
        
        # Test archive types
        assert get_file_type_icon('.zip') == '📦'
        assert get_file_type_icon('.rar') == '📦'
        
        # Test unknown type
        assert get_file_type_icon('.unknown') == '📄'  # Default
        
        # Test case insensitive
        assert get_file_type_icon('.PDF') == '📄'
        assert get_file_type_icon('.DOCX') == '📝'
    
    def test_format_duration(self):
        """Test duration formatting"""
        # Test seconds
        assert format_duration(0) == "0s"
        assert format_duration(1) == "1s"
        assert format_duration(59) == "59s"
        
        # Test minutes and seconds
        assert format_duration(60) == "1m 0s"
        assert format_duration(61) == "1m 1s"
        assert format_duration(125) == "2m 5s"
        
        # Test hours, minutes, and seconds
        assert format_duration(3600) == "1h 0m 0s"
        assert format_duration(3661) == "1h 1m 1s"
        assert format_duration(7325) == "2h 2m 5s"
        
        # Test negative duration
        assert format_duration(-1) == "0s"
        
        # Test float duration
        assert format_duration(61.5) == "1m 1s"  # Should truncate
    
    def test_parse_file_filters(self):
        """Test file filter parsing"""
        # Test single filter
        filters = parse_file_filters("*.pdf")
        assert filters == ['.pdf']
        
        # Test multiple filters
        filters = parse_file_filters("*.pdf,*.docx,*.txt")
        assert set(filters) == {'.pdf', '.docx', '.txt'}
        
        # Test with spaces
        filters = parse_file_filters("*.pdf, *.docx, *.txt")
        assert set(filters) == {'.pdf', '.docx', '.txt'}
        
        # Test with semicolon separator
        filters = parse_file_filters("*.pdf;*.docx;*.txt")
        assert set(filters) == {'.pdf', '.docx', '.txt'}
        
        # Test case normalization
        filters = parse_file_filters("*.PDF,*.DocX")
        assert set(filters) == {'.pdf', '.docx'}
        
        # Test invalid format
        filters = parse_file_filters("pdf,docx")  # No asterisk
        assert filters == []
        
        # Test empty string
        filters = parse_file_filters("")
        assert filters == []
        
        # Test None
        filters = parse_file_filters(None)
        assert filters == []
    
    def test_sanitize_html(self):
        """Test HTML sanitization"""
        # Test basic HTML removal
        html_text = "<p>Hello <b>World</b>!</p>"
        result = sanitize_html(html_text)
        assert result == "Hello World!"
        
        # Test script tag removal
        malicious_html = "<script>alert('xss')</script>Safe text"
        result = sanitize_html(malicious_html)
        assert "script" not in result.lower()
        assert "Safe text" in result
        
        # Test preserving line breaks
        html_with_br = "Line 1<br>Line 2<br/>Line 3"
        result = sanitize_html(html_with_br)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result
        
        # Test empty input
        assert sanitize_html("") == ""
        assert sanitize_html(None) == ""
    
    def test_truncate_text(self):
        """Test text truncation"""
        long_text = "This is a very long text that should be truncated properly."
        
        # Test normal truncation
        result = truncate_text(long_text, max_length=20)
        assert len(result) <= 23  # 20 + "..." length
        assert result.endswith("...")
        
        # Test text shorter than limit
        short_text = "Short text"
        result = truncate_text(short_text, max_length=20)
        assert result == short_text
        
        # Test custom suffix
        result = truncate_text(long_text, max_length=20, suffix="[more]")
        assert result.endswith("[more]")
        
        # Test zero length
        result = truncate_text(long_text, max_length=0)
        assert result == "..."
        
        # Test negative length
        result = truncate_text(long_text, max_length=-1)
        assert result == "..."
        
        # Test None input
        result = truncate_text(None, max_length=20)
        assert result == ""
    
    def test_get_system_info(self):
        """Test system information gathering"""
        info = get_system_info()
        
        # Check required fields
        assert 'platform' in info
        assert 'python_version' in info
        assert 'cpu_count' in info
        assert 'memory_total' in info
        assert 'disk_free' in info
        
        # Verify types
        assert isinstance(info['platform'], str)
        assert isinstance(info['python_version'], str)
        assert isinstance(info['cpu_count'], int)
        assert isinstance(info['memory_total'], (int, float))
        assert isinstance(info['disk_free'], (int, float))
        
        # Verify reasonable values
        assert info['cpu_count'] > 0
        assert info['memory_total'] > 0
        assert info['disk_free'] >= 0
    
    def test_create_backup_filename(self):
        """Test backup filename creation"""
        # Test basic backup name
        result = create_backup_filename("document.txt")
        assert result.startswith("document")
        assert result.endswith(".txt")
        assert "_backup_" in result
        
        # Test with full path
        result = create_backup_filename("/path/to/document.pdf")
        assert result.startswith("/path/to/document")
        assert result.endswith(".pdf")
        
        # Test with no extension
        result = create_backup_filename("document")
        assert result.startswith("document")
        assert "_backup_" in result
        
        # Test custom suffix
        result = create_backup_filename("document.txt", suffix="v2")
        assert "_v2_" in result
        
        # Test timestamp format
        result = create_backup_filename("document.txt")
        # Should contain date/time pattern
        import re
        pattern = r"_backup_\d{8}_\d{6}"  # YYYYMMDD_HHMMSS
        assert re.search(pattern, result) is not None
    
    def test_is_image_file(self):
        """Test image file detection"""
        # Test common image extensions
        assert is_image_file("photo.jpg") == True
        assert is_image_file("photo.jpeg") == True
        assert is_image_file("image.png") == True
        assert is_image_file("graphic.gif") == True
        assert is_image_file("vector.svg") == True
        assert is_image_file("bitmap.bmp") == True
        assert is_image_file("raw.tiff") == True
        
        # Test case insensitive
        assert is_image_file("PHOTO.JPG") == True
        assert is_image_file("Image.PNG") == True
        
        # Test non-image files
        assert is_image_file("document.pdf") == False
        assert is_image_file("text.txt") == False
        assert is_image_file("spreadsheet.xlsx") == False
        
        # Test no extension
        assert is_image_file("filename") == False
        
        # Test empty string
        assert is_image_file("") == False
        assert is_image_file(None) == False
    
    def test_get_file_mime_type(self, temp_dir):
        """Test MIME type detection"""
        # Create test files
        text_file = temp_dir / "test.txt"
        text_file.write_text("Hello World")
        
        # Test text file
        mime_type = get_file_mime_type(str(text_file))
        assert mime_type.startswith("text/")
        
        # Test by extension for known types
        assert get_file_mime_type("document.pdf") == "application/pdf"
        assert get_file_mime_type("image.png") == "image/png"
        assert get_file_mime_type("image.jpg") == "image/jpeg"
        assert get_file_mime_type("data.json") == "application/json"
        
        # Test unknown extension
        unknown_mime = get_file_mime_type("file.unknown")
        assert unknown_mime in ["application/octet-stream", "text/plain", None]
        
        # Test non-existent file (should fall back to extension)
        mime_type = get_file_mime_type("nonexistent.pdf")
        assert mime_type == "application/pdf"
    
    def test_error_handling(self, temp_dir):
        """Test error handling in utility functions"""
        # Test with protected/system files (if available)
        try:
            # Try to access a system file that might be restricted
            system_file = "/etc/passwd"  # Unix-like systems
            if not Path(system_file).exists():
                system_file = "C:\\Windows\\System32\\config\\SAM"  # Windows
            
            if Path(system_file).exists():
                # Should handle permission errors gracefully
                result = detect_file_encoding(system_file)
                # Should not raise exception, might return None or a guess
                assert result is None or isinstance(result, str)
        except PermissionError:
            # Expected on some systems
            pass
        
        # Test with corrupted or unusual files
        weird_file = temp_dir / "weird.bin"
        weird_file.write_bytes(b'\xFF\xFE\x00\x00' * 1000)  # Unusual byte pattern
        
        # Should handle gracefully without exceptions
        encoding = detect_file_encoding(str(weird_file))
        is_binary = is_binary_file(str(weird_file))
        mime_type = get_file_mime_type(str(weird_file))
        
        # Should return reasonable defaults
        assert encoding is None or isinstance(encoding, str)
        assert isinstance(is_binary, bool)
        assert mime_type is None or isinstance(mime_type, str)
    
    def test_unicode_handling(self, temp_dir):
        """Test Unicode text handling"""
        # Create file with Unicode content
        unicode_file = temp_dir / "unicode.txt"
        unicode_content = "Hello 世界 🌍 Ελληνικά Русский العربية"
        unicode_file.write_text(unicode_content, encoding='utf-8')
        
        # Test encoding detection
        encoding = detect_file_encoding(str(unicode_file))
        assert encoding.lower() in ['utf-8', 'utf-8-sig']
        
        # Test binary detection (should be false for UTF-8 text)
        assert is_binary_file(str(unicode_file)) == False
        
        # Test filename handling with Unicode
        unicode_filename = safe_filename("файл_测试_🚀.txt")
        assert isinstance(unicode_filename, str)
        # Should either preserve Unicode or convert safely
        assert len(unicode_filename) > 0
    
    def test_performance_with_large_files(self, temp_dir):
        """Test performance with larger files"""
        import time
        
        # Create a moderately large file (1MB)
        large_file = temp_dir / "large.txt"
        content = "x" * (1024 * 1024)  # 1MB of 'x'
        large_file.write_text(content)
        
        # Test MD5 calculation performance
        start_time = time.time()
        hash_result = calculate_md5_hash(str(large_file))
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second for 1MB)
        assert (end_time - start_time) < 1.0
        assert len(hash_result) == 32
        
        # Test binary detection performance
        start_time = time.time()
        is_binary = is_binary_file(str(large_file))
        end_time = time.time()
        
        # Should be fast (< 0.1 seconds) since it only reads first portion
        assert (end_time - start_time) < 0.1
        assert is_binary == False
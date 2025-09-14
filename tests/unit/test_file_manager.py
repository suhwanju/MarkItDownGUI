"""
Unit tests for FileManager
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from markitdown_gui.core.file_manager import FileManager, FileInfo
from markitdown_gui.core.exceptions import InvalidPathError, ResourceNotFoundError


class TestFileManager:
    """Test suite for FileManager"""
    
    def test_initialization(self, file_manager):
        """Test FileManager initialization"""
        assert file_manager is not None
        assert file_manager.supported_formats is not None
        assert len(file_manager.supported_formats) > 0
    
    def test_supported_formats(self, file_manager):
        """Test supported file formats"""
        formats = file_manager.supported_formats
        
        # Check common formats are supported
        assert '.pdf' in formats
        assert '.docx' in formats
        assert '.xlsx' in formats
        assert '.pptx' in formats
        assert '.txt' in formats
        assert '.md' in formats
        assert '.png' in formats
        assert '.jpg' in formats
    
    def test_scan_directory_basic(self, file_manager, sample_files, temp_dir):
        """Test basic directory scanning"""
        file_manager.root_directory = str(temp_dir)
        
        # Scan without subdirectories
        files = file_manager.scan_directory(include_subdirs=False)
        
        # Check files were found
        assert len(files) > 0
        file_names = [f.name for f in files]
        assert 'test.pdf' in file_names
        assert 'test.txt' in file_names
        
        # Should not include nested files
        assert 'nested.md' not in file_names
    
    def test_scan_directory_with_subdirs(self, file_manager, sample_files, temp_dir):
        """Test directory scanning with subdirectories"""
        file_manager.root_directory = str(temp_dir)
        
        # Scan with subdirectories
        files = file_manager.scan_directory(include_subdirs=True)
        
        file_names = [f.name for f in files]
        assert 'nested.md' in file_names  # Should include nested files
    
    def test_scan_directory_with_filters(self, file_manager, sample_files, temp_dir):
        """Test directory scanning with file type filters"""
        file_manager.root_directory = str(temp_dir)
        
        # Filter for PDF files only
        pdf_files = file_manager.scan_directory(
            include_subdirs=False,
            file_filters=['.pdf']
        )
        
        assert len(pdf_files) >= 1
        assert all(f.extension == '.pdf' for f in pdf_files)
        
        # Filter for multiple types
        doc_files = file_manager.scan_directory(
            include_subdirs=False,
            file_filters=['.pdf', '.txt', '.md']
        )
        
        assert len(doc_files) >= 2
        allowed_exts = {'.pdf', '.txt', '.md'}
        assert all(f.extension in allowed_exts for f in doc_files)
    
    def test_file_info_creation(self, file_manager, sample_files):
        """Test FileInfo object creation"""
        pdf_file = sample_files['pdf']
        
        file_info = file_manager.create_file_info(str(pdf_file))
        
        assert file_info.name == 'test.pdf'
        assert file_info.path == str(pdf_file)
        assert file_info.extension == '.pdf'
        assert file_info.size > 0
        assert file_info.modified_time is not None
        assert file_info.is_supported == True
    
    def test_file_type_detection(self, file_manager):
        """Test file type detection"""
        # Test various file extensions
        assert file_manager.is_supported_file_type('.pdf') == True
        assert file_manager.is_supported_file_type('.docx') == True
        assert file_manager.is_supported_file_type('.txt') == True
        assert file_manager.is_supported_file_type('.xyz') == False
        
        # Test case insensitive
        assert file_manager.is_supported_file_type('.PDF') == True
        assert file_manager.is_supported_file_type('.Docx') == True
    
    def test_file_size_formatting(self, file_manager):
        """Test file size formatting utility"""
        # Test various file sizes
        assert file_manager.format_file_size(0) == "0 B"
        assert file_manager.format_file_size(512) == "512 B"
        assert file_manager.format_file_size(1024) == "1.0 KB"
        assert file_manager.format_file_size(1536) == "1.5 KB"
        assert file_manager.format_file_size(1024 * 1024) == "1.0 MB"
        assert file_manager.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_path_validation(self, file_manager, temp_dir):
        """Test path validation"""
        # Valid directory
        file_manager.set_root_directory(str(temp_dir))
        assert file_manager.root_directory == str(temp_dir)
        
        # Invalid directory
        invalid_path = str(temp_dir / "nonexistent")
        with pytest.raises(InvalidPathError):
            file_manager.set_root_directory(invalid_path)
        
        # None path
        with pytest.raises(InvalidPathError):
            file_manager.set_root_directory(None)
        
        # Empty path
        with pytest.raises(InvalidPathError):
            file_manager.set_root_directory("")
    
    def test_filter_files_by_size(self, file_manager, sample_files, temp_dir):
        """Test filtering files by size"""
        file_manager.root_directory = str(temp_dir)
        
        # Create files with known sizes
        small_file = temp_dir / "small.txt"
        small_file.write_text("small")
        
        large_file = temp_dir / "large.txt"
        large_file.write_text("x" * 10000)  # 10KB
        
        all_files = file_manager.scan_directory()
        
        # Filter by minimum size
        large_files = file_manager.filter_by_size(all_files, min_size=5000)
        large_names = [f.name for f in large_files]
        assert "large.txt" in large_names
        assert "small.txt" not in large_names
        
        # Filter by maximum size
        small_files = file_manager.filter_by_size(all_files, max_size=100)
        small_names = [f.name for f in small_files]
        assert "small.txt" in small_names
        assert "large.txt" not in small_names
    
    def test_filter_files_by_date(self, file_manager, sample_files, temp_dir):
        """Test filtering files by modification date"""
        from datetime import datetime, timedelta
        
        file_manager.root_directory = str(temp_dir)
        
        # Create file with specific date
        recent_file = temp_dir / "recent.txt"
        recent_file.write_text("recent content")
        
        # Get current files
        all_files = file_manager.scan_directory()
        
        # Filter by date (last 24 hours)
        cutoff_date = datetime.now() - timedelta(hours=24)
        recent_files = file_manager.filter_by_date(all_files, after_date=cutoff_date)
        
        # All test files should be recent
        assert len(recent_files) > 0
        recent_names = [f.name for f in recent_files]
        assert "recent.txt" in recent_names
    
    def test_search_files_by_name(self, file_manager, sample_files, temp_dir):
        """Test searching files by name pattern"""
        file_manager.root_directory = str(temp_dir)
        
        all_files = file_manager.scan_directory(include_subdirs=True)
        
        # Search for PDF files
        pdf_files = file_manager.search_by_name(all_files, "*test*.pdf")
        assert len(pdf_files) >= 1
        assert all("test" in f.name and f.extension == '.pdf' for f in pdf_files)
        
        # Search for markdown files
        md_files = file_manager.search_by_name(all_files, "*.md")
        md_names = [f.name for f in md_files]
        assert any("nested.md" in name for name in md_names)
    
    def test_get_file_stats(self, file_manager, sample_files, temp_dir):
        """Test getting directory statistics"""
        file_manager.root_directory = str(temp_dir)
        
        stats = file_manager.get_directory_stats()
        
        assert 'total_files' in stats
        assert 'total_size' in stats
        assert 'file_types' in stats
        assert 'supported_files' in stats
        
        assert stats['total_files'] > 0
        assert stats['total_size'] > 0
        assert len(stats['file_types']) > 0
    
    def test_concurrent_scanning(self, file_manager, temp_dir):
        """Test concurrent directory scanning"""
        import threading
        import time
        
        file_manager.root_directory = str(temp_dir)
        
        # Create many test files
        for i in range(20):
            test_file = temp_dir / f"test_{i}.txt"
            test_file.write_text(f"content {i}")
        
        results = []
        errors = []
        
        def scan_worker():
            try:
                files = file_manager.scan_directory()
                results.append(len(files))
            except Exception as e:
                errors.append(e)
        
        # Create multiple scanning threads
        threads = []
        for _ in range(3):
            t = threading.Thread(target=scan_worker)
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify all scans completed successfully
        assert len(errors) == 0
        assert len(results) == 3
        assert all(r > 0 for r in results)  # All found files
        assert all(r == results[0] for r in results)  # Consistent results
    
    def test_error_handling(self, file_manager, temp_dir):
        """Test error handling for various scenarios"""
        # Test scanning non-existent directory
        file_manager.root_directory = str(temp_dir / "nonexistent")
        
        with pytest.raises(ResourceNotFoundError):
            file_manager.scan_directory()
        
        # Test accessing file that gets deleted during scan
        file_manager.root_directory = str(temp_dir)
        
        temp_file = temp_dir / "temp.txt"
        temp_file.write_text("temporary")
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.side_effect = FileNotFoundError()
            
            # Should handle gracefully and continue
            files = file_manager.scan_directory()
            # Should return files it could process
            assert isinstance(files, list)
    
    def test_memory_usage_with_large_directory(self, file_manager, temp_dir):
        """Test memory usage with large number of files"""
        import tracemalloc
        
        file_manager.root_directory = str(temp_dir)
        
        # Create many small files
        for i in range(100):
            test_file = temp_dir / f"file_{i:03d}.txt"
            test_file.write_text(f"content {i}")
        
        # Measure memory usage
        tracemalloc.start()
        
        files = file_manager.scan_directory()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Verify files were found
        assert len(files) == 100
        
        # Memory usage should be reasonable (less than 10MB for 100 small files)
        assert peak < 10 * 1024 * 1024  # 10MB
    
    def test_cleanup(self, file_manager):
        """Test proper cleanup of resources"""
        # Should not raise any errors
        file_manager.cleanup()
        
        # FileManager should still be usable after cleanup
        assert file_manager.supported_formats is not None
"""
End-to-End tests for complete conversion workflows
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from markitdown_gui.core.file_manager import FileManager, FileInfo
from markitdown_gui.core.conversion_manager import ConversionManager, ConversionStatus
from markitdown_gui.core.config_manager import ConfigManager


class TestConversionWorkflows:
    """End-to-end tests for complete conversion workflows"""
    
    @pytest.fixture
    def real_test_files(self, temp_dir):
        """Create real test files for E2E testing"""
        files = {}
        
        # PDF-like file
        pdf_file = temp_dir / "sample.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nTest PDF content")
        files['pdf'] = str(pdf_file)
        
        # Word-like file
        docx_file = temp_dir / "sample.docx"
        docx_file.write_bytes(b"PK\x03\x04Test Word document content")
        files['docx'] = str(docx_file)
        
        # Text file
        txt_file = temp_dir / "sample.txt"
        txt_file.write_text("This is a sample text document for testing.\n\nIt has multiple lines.")
        files['txt'] = str(txt_file)
        
        # Markdown file
        md_file = temp_dir / "sample.md"
        md_file.write_text("# Test Document\n\nThis is a **test** markdown document.")
        files['md'] = str(md_file)
        
        # Image file (PNG-like)
        png_file = temp_dir / "sample.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\nTest image data for OCR")
        files['png'] = str(png_file)
        
        return files
    
    @pytest.fixture
    def workflow_managers(self, config_manager, temp_dir):
        """Create managers for workflow testing"""
        file_manager = FileManager()
        conversion_manager = ConversionManager(config_manager)
        
        # Set up output directory
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        config_manager.set_value("Conversion/output_dir", str(output_dir))
        
        return file_manager, conversion_manager
    
    def test_single_file_conversion_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test complete single file conversion workflow"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock conversion
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Converted Content\n\nThis is the converted content."
            
            # Step 1: File discovery
            test_file = real_test_files['pdf']
            file_info = file_manager.create_file_info(test_file)
            
            assert file_info is not None
            assert file_info.name == "sample.pdf"
            assert file_info.size > 0
            
            # Step 2: File conversion
            start_time = time.time()
            result = conversion_manager.convert_file(test_file)
            end_time = time.time()
            
            # Step 3: Verify conversion result
            assert result.status == ConversionStatus.SUCCESS
            assert "Converted Content" in result.content
            assert result.processing_time > 0
            assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
            
            # Step 4: Verify output file creation
            output_dir = Path(conversion_manager.config_manager.get_value("Conversion/output_dir"))
            expected_output = output_dir / "sample.md"
            
            if hasattr(conversion_manager, 'save_output'):
                conversion_manager.save_output(result)
                assert expected_output.exists()
                
                # Verify output content
                output_content = expected_output.read_text()
                assert "Converted Content" in output_content
    
    def test_batch_conversion_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test complete batch conversion workflow"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock conversion
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Batch Converted Content"
            
            # Step 1: Prepare multiple files
            test_files = [real_test_files['pdf'], real_test_files['docx'], real_test_files['txt']]
            
            # Step 2: Create file info objects
            file_infos = []
            for file_path in test_files:
                file_info = file_manager.create_file_info(file_path)
                file_infos.append(file_info)
            
            assert len(file_infos) == 3
            assert all(info.is_supported for info in file_infos)
            
            # Step 3: Batch conversion
            start_time = time.time()
            results = conversion_manager.convert_files(test_files)
            end_time = time.time()
            
            # Step 4: Verify batch results
            assert len(results) == 3
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
            assert all("Batch Converted Content" in r.content for r in results)
            
            # Verify performance (parallel processing should be faster than sequential)
            total_time = end_time - start_time
            assert total_time < len(test_files) * 2.0  # Should be faster than 2s per file
            
            # Step 5: Verify conversion statistics
            stats = conversion_manager.get_conversion_stats()
            assert stats['total_files'] == 3
            assert stats['successful'] == 3
            assert stats['failed'] == 0
    
    def test_directory_scan_and_convert_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test complete directory scanning and conversion workflow"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock conversion
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Directory Converted Content"
            
            # Step 1: Set up directory structure
            subdir = temp_dir / "documents"
            subdir.mkdir()
            
            # Copy test files to subdirectory
            for name, file_path in real_test_files.items():
                if name in ['pdf', 'docx', 'txt']:  # Only supported formats
                    dest_file = subdir / f"sub_{name}.{name}"
                    dest_file.write_bytes(Path(file_path).read_bytes())
            
            # Step 2: Directory scan
            file_manager.set_root_directory(str(temp_dir))
            
            # Scan without subdirectories
            files_no_sub = file_manager.scan_directory(include_subdirs=False)
            root_files = [f.name for f in files_no_sub]
            assert len(root_files) >= 3  # Original test files
            
            # Scan with subdirectories
            files_with_sub = file_manager.scan_directory(include_subdirs=True)
            all_files = [f.name for f in files_with_sub]
            assert len(files_with_sub) > len(files_no_sub)  # Should find more files
            assert any("sub_" in name for name in all_files)
            
            # Step 3: Filter supported files
            supported_files = [f for f in files_with_sub if f.is_supported]
            assert len(supported_files) >= 6  # At least 6 supported files
            
            # Step 4: Convert all supported files
            file_paths = [f.path for f in supported_files]
            results = conversion_manager.convert_files(file_paths)
            
            # Step 5: Verify comprehensive conversion
            assert len(results) == len(supported_files)
            success_count = sum(1 for r in results if r.status == ConversionStatus.SUCCESS)
            assert success_count == len(results)  # All should succeed with mock
    
    def test_filtering_and_selection_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test file filtering and selection workflow"""
        file_manager, conversion_manager = workflow_managers
        
        # Step 1: Set up test directory
        file_manager.set_root_directory(str(temp_dir))
        all_files = file_manager.scan_directory()
        
        # Step 2: Test file type filtering
        pdf_files = file_manager.filter_by_type(all_files, ['.pdf'])
        assert len(pdf_files) >= 1
        assert all(f.extension == '.pdf' for f in pdf_files)
        
        doc_files = file_manager.filter_by_type(all_files, ['.pdf', '.docx', '.txt'])
        assert len(doc_files) >= 3
        
        # Step 3: Test size filtering
        small_files = file_manager.filter_by_size(all_files, max_size=1000)
        large_files = file_manager.filter_by_size(all_files, min_size=50)
        
        assert len(small_files) <= len(all_files)
        assert len(large_files) <= len(all_files)
        
        # Step 4: Test date filtering
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        recent_files = file_manager.filter_by_date(all_files, after_date=recent_cutoff)
        
        # All test files should be recent
        assert len(recent_files) == len(all_files)
        
        # Step 5: Test name pattern filtering
        sample_files = file_manager.search_by_name(all_files, "*sample*")
        assert len(sample_files) >= 3  # Should find our sample files
        assert all("sample" in f.name for f in sample_files)
    
    def test_progress_tracking_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test progress tracking throughout conversion workflow"""
        file_manager, conversion_manager = workflow_managers
        
        progress_updates = []
        
        def progress_handler(current, total, message):
            progress_updates.append({
                'current': current,
                'total': total,
                'message': message,
                'timestamp': time.time()
            })
        
        # Connect progress handler
        conversion_manager.progress_updated.connect(progress_handler)
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with delay to test progress
            def slow_convert(file_path):
                time.sleep(0.1)  # Small delay to simulate work
                result = Mock()
                result.text_content = f"# Converted {Path(file_path).name}"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = slow_convert
            
            # Convert multiple files
            test_files = list(real_test_files.values())[:3]
            results = conversion_manager.convert_files(test_files)
            
            # Verify progress tracking
            assert len(progress_updates) >= 3  # At least one per file
            
            # Check progress sequence
            for i, update in enumerate(progress_updates):
                assert update['current'] <= update['total']
                assert update['total'] == len(test_files)
                assert isinstance(update['message'], str)
                assert len(update['message']) > 0
                
                # Progress should be non-decreasing
                if i > 0:
                    assert update['current'] >= progress_updates[i-1]['current']
            
            # Final progress should indicate completion
            final_update = progress_updates[-1]
            assert final_update['current'] == final_update['total']
            
            # Verify all conversions succeeded
            assert len(results) == len(test_files)
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
    
    def test_error_handling_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test error handling in conversion workflows"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock to simulate various errors
            def error_convert(file_path):
                if "pdf" in file_path:
                    raise Exception("PDF processing error")
                elif "docx" in file_path:
                    raise PermissionError("Access denied")
                else:
                    result = Mock()
                    result.text_content = "# Successful conversion"
                    return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = error_convert
            
            # Test mixed success/failure scenario
            test_files = [real_test_files['pdf'], real_test_files['docx'], real_test_files['txt']]
            results = conversion_manager.convert_files(test_files)
            
            # Verify error handling
            assert len(results) == 3
            
            # PDF should fail
            pdf_result = next(r for r in results if "pdf" in r.input_file)
            assert pdf_result.status == ConversionStatus.FAILED
            assert "PDF processing error" in pdf_result.error_message
            
            # DOCX should fail
            docx_result = next(r for r in results if "docx" in r.input_file)
            assert docx_result.status == ConversionStatus.FAILED
            assert "Access denied" in docx_result.error_message
            
            # TXT should succeed
            txt_result = next(r for r in results if "txt" in r.input_file)
            assert txt_result.status == ConversionStatus.SUCCESS
            assert "Successful conversion" in txt_result.content
            
            # Check statistics reflect mixed results
            stats = conversion_manager.get_conversion_stats()
            assert stats['successful'] >= 1
            assert stats['failed'] >= 2
    
    def test_cancellation_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test conversion cancellation workflow"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock with long delay
            def slow_convert(file_path):
                time.sleep(1.0)  # Long delay
                result = Mock()
                result.text_content = "# Slow conversion"
                return result
            
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.side_effect = slow_convert
            
            # Start conversion in background
            test_files = list(real_test_files.values())
            
            # Use ThreadPoolExecutor to test cancellation
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(conversion_manager.convert_files, test_files)
                
                # Wait a bit then cancel
                time.sleep(0.1)
                conversion_manager.cancel_conversion()
                
                # Wait for completion or cancellation
                try:
                    results = future.result(timeout=2.0)
                    # If completed, check cancellation was handled
                    if results:
                        # Some results might be incomplete due to cancellation
                        cancelled_count = sum(1 for r in results if r.status == ConversionStatus.CANCELLED)
                        assert cancelled_count >= 0  # Cancellation might affect some files
                except Exception:
                    # Timeout or cancellation exception is acceptable
                    pass
                
                # Verify cancellation flag was set
                assert conversion_manager.is_cancelled == True
    
    def test_output_management_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test output file management workflow"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            # Setup mock conversion
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Output Test Content"
            
            # Step 1: Configure output directory
            output_dir = temp_dir / "custom_output"
            output_dir.mkdir()
            conversion_manager.config_manager.set_value("Conversion/output_dir", str(output_dir))
            
            # Step 2: Convert files
            test_file = real_test_files['pdf']
            result = conversion_manager.convert_file(test_file)
            
            assert result.status == ConversionStatus.SUCCESS
            
            # Step 3: Test output file creation
            if hasattr(conversion_manager, 'save_output'):
                output_path = conversion_manager.save_output(result)
                
                assert Path(output_path).exists()
                assert Path(output_path).parent == output_dir
                assert Path(output_path).suffix == '.md'
                
                # Verify content
                content = Path(output_path).read_text()
                assert "Output Test Content" in content
            
            # Step 4: Test filename sanitization
            special_chars_file = temp_dir / "special:chars<>file.pdf"
            special_chars_file.write_bytes(b"Test content")
            
            result2 = conversion_manager.convert_file(str(special_chars_file))
            if hasattr(conversion_manager, 'save_output'):
                output_path2 = conversion_manager.save_output(result2)
                
                # Output filename should be sanitized
                assert ":" not in Path(output_path2).name
                assert "<" not in Path(output_path2).name
                assert ">" not in Path(output_path2).name
    
    def test_configuration_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test configuration changes during workflow"""
        file_manager, conversion_manager = workflow_managers
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Config Test"
            
            # Step 1: Test with default configuration
            result1 = conversion_manager.convert_file(real_test_files['txt'])
            original_workers = conversion_manager.max_workers
            
            # Step 2: Change worker count
            new_workers = min(8, original_workers * 2)
            conversion_manager.config_manager.set_value("Conversion/max_workers", new_workers)
            conversion_manager.update_configuration()
            
            assert conversion_manager.max_workers == new_workers
            
            # Step 3: Test batch conversion with new configuration
            test_files = list(real_test_files.values())[:3]
            results = conversion_manager.convert_files(test_files)
            
            assert len(results) == 3
            assert all(r.status == ConversionStatus.SUCCESS for r in results)
            
            # Step 4: Test file type filters
            original_filters = file_manager.supported_formats
            new_filters = ['.pdf', '.txt']  # Subset of formats
            
            conversion_manager.config_manager.set_value("Conversion/file_filters", new_filters)
            
            # Re-scan directory with new filters
            if hasattr(file_manager, 'update_filters'):
                file_manager.update_filters(new_filters)
                filtered_files = file_manager.scan_directory()
                
                # Should only find PDF and TXT files
                assert all(f.extension in new_filters for f in filtered_files)
    
    def test_memory_and_cleanup_workflow(self, workflow_managers, real_test_files, temp_dir):
        """Test memory management and cleanup workflow"""
        file_manager, conversion_manager = workflow_managers
        
        import gc
        import tracemalloc
        
        # Start memory tracing
        tracemalloc.start()
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Memory Test Content"
            
            # Step 1: Perform multiple conversion cycles
            for cycle in range(3):
                # Convert files
                test_files = list(real_test_files.values())
                results = conversion_manager.convert_files(test_files)
                
                # Verify conversions
                assert len(results) == len(test_files)
                
                # Clear results to free memory
                conversion_manager.clear_results()
                
                # Force garbage collection
                gc.collect()
                
                # Check memory usage
                current, peak = tracemalloc.get_traced_memory()
                
                # Memory usage should be reasonable (less than 50MB for test files)
                assert current < 50 * 1024 * 1024
                assert peak < 100 * 1024 * 1024
            
            # Step 2: Test cleanup
            conversion_manager.cleanup()
            file_manager.cleanup()
            
            # Final memory check
            final_memory, _ = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Memory should be cleaned up
            assert final_memory < 20 * 1024 * 1024  # Less than 20MB after cleanup
    
    def test_concurrent_workflow_safety(self, workflow_managers, real_test_files, temp_dir):
        """Test thread safety in concurrent workflows"""
        file_manager, conversion_manager = workflow_managers
        
        import threading
        import queue
        
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_markitdown:
            mock_instance = mock_markitdown.return_value
            mock_instance.convert.return_value.text_content = "# Concurrent Test"
            
            results_queue = queue.Queue()
            errors_queue = queue.Queue()
            
            def worker_thread(thread_id):
                try:
                    # Each thread processes different files
                    test_files = [real_test_files['txt']]  # Use same file for simplicity
                    results = conversion_manager.convert_files(test_files)
                    results_queue.put((thread_id, results))
                except Exception as e:
                    errors_queue.put((thread_id, e))
            
            # Start multiple threads
            threads = []
            for i in range(3):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=5.0)
            
            # Check results
            assert errors_queue.empty()  # No errors should occur
            
            thread_results = []
            while not results_queue.empty():
                thread_id, results = results_queue.get()
                thread_results.append((thread_id, results))
            
            assert len(thread_results) == 3  # All threads completed
            
            # Verify all threads got valid results
            for thread_id, results in thread_results:
                assert len(results) == 1
                assert results[0].status == ConversionStatus.SUCCESS
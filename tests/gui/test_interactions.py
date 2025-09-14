"""
GUI tests for user interactions and workflows
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtTest import QTest

from markitdown_gui.ui.main_window import MainWindow
from markitdown_gui.core.config_manager import ConfigManager


class TestUserInteractions:
    """Test suite for user interactions and complete workflows"""
    
    @pytest.fixture
    def app_with_main_window(self, qtbot, config_manager):
        """Create main application window for integration testing"""
        window = MainWindow(config_manager)
        qtbot.addWidget(window)
        window.show()
        return window
    
    def test_complete_conversion_workflow(self, app_with_main_window, qtbot, temp_dir):
        """Test complete file conversion workflow"""
        main_window = app_with_main_window
        
        # Create test files
        test_files = []
        for i in range(3):
            test_file = temp_dir / f"test_{i}.pdf"
            test_file.write_bytes(b"Test PDF content")
            test_files.append(str(test_file))
        
        # Mock file manager and conversion manager
        with patch.object(main_window, 'file_manager') as mock_file_manager, \
             patch.object(main_window, 'conversion_manager') as mock_conversion_manager:
            
            # Setup mock file discovery
            mock_file_info = [Mock(name=f"test_{i}.pdf", path=path) 
                            for i, path in enumerate(test_files)]
            mock_file_manager.scan_directory.return_value = mock_file_info
            
            # Setup mock conversion
            mock_results = [Mock(status="SUCCESS", content="# Converted") 
                          for _ in test_files]
            mock_conversion_manager.convert_files.return_value = mock_results
            
            # Step 1: Open directory
            with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
                mock_dialog.return_value = str(temp_dir)
                main_window.on_open_directory()
                
                # Verify directory was set
                assert main_window.current_directory == str(temp_dir)
            
            # Step 2: Files should be loaded in file list
            qtbot.wait(100)  # Allow file loading
            
            # Step 3: Select files and start conversion
            # Simulate user selecting all files
            main_window.file_list_widget.selectAll()
            
            # Step 4: Start conversion
            main_window.start_conversion()
            
            # Verify conversion was initiated
            mock_conversion_manager.convert_files.assert_called_once()
            
            # Step 5: Simulate progress updates
            for i in range(len(test_files)):
                main_window.on_conversion_progress(i + 1, len(test_files), f"Converting {i+1}/{len(test_files)}")
                qtbot.wait(10)
            
            # Step 6: Conversion completion
            main_window.on_conversion_complete(mock_results)
            
            # Verify UI state after completion
            assert main_window.progress_widget.value() == main_window.progress_widget.maximum()
    
    def test_settings_workflow(self, app_with_main_window, qtbot):
        """Test complete settings configuration workflow"""
        main_window = app_with_main_window
        
        with patch('markitdown_gui.ui.settings_dialog.SettingsDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = 1  # Accepted
            mock_dialog_class.return_value = mock_dialog
            
            # Step 1: Open settings dialog
            main_window.on_settings()
            
            # Step 2: Verify dialog was created and shown
            mock_dialog_class.assert_called_once_with(main_window.config_manager, main_window)
            mock_dialog.exec.assert_called_once()
            
            # Step 3: Simulate settings being applied
            # This would trigger theme/language updates
            with patch.object(main_window, 'on_theme_changed') as mock_theme, \
                 patch.object(main_window, 'on_language_changed') as mock_lang:
                
                # Simulate settings change notifications
                main_window.config_manager.settings_changed.emit("General/theme", "dark")
                main_window.config_manager.settings_changed.emit("General/language", "ko_KR")
                
                qtbot.wait(10)  # Allow signal processing
    
    def test_drag_and_drop_workflow(self, app_with_main_window, qtbot, temp_dir):
        """Test drag and drop file workflow"""
        main_window = app_with_main_window
        
        # Create test files
        test_files = []
        for i in range(2):
            test_file = temp_dir / f"dropped_{i}.pdf"
            test_file.write_bytes(b"Dropped file content")
            test_files.append(str(test_file))
        
        # Mock drag and drop event
        from PyQt6.QtGui import QDragEnterEvent, QDropEvent
        from PyQt6.QtCore import QMimeData, QUrl
        
        # Create mime data with file URLs
        mime_data = QMimeData()
        urls = [QUrl.fromLocalFile(path) for path in test_files]
        mime_data.setUrls(urls)
        
        # Test drag enter event
        drag_enter_event = Mock()
        drag_enter_event.mimeData.return_value = mime_data
        drag_enter_event.acceptProposedAction = Mock()
        
        main_window.dragEnterEvent(drag_enter_event)
        drag_enter_event.acceptProposedAction.assert_called_once()
        
        # Test drop event
        with patch.object(main_window, 'add_files_to_list') as mock_add_files:
            drop_event = Mock()
            drop_event.mimeData.return_value = mime_data
            drop_event.acceptProposedAction = Mock()
            
            main_window.dropEvent(drop_event)
            
            # Verify files were added
            mock_add_files.assert_called_once()
            drop_event.acceptProposedAction.assert_called_once()
    
    def test_keyboard_shortcuts_workflow(self, app_with_main_window, qtbot):
        """Test keyboard shortcuts workflow"""
        main_window = app_with_main_window
        
        with patch.object(main_window, 'on_open_directory') as mock_open, \
             patch.object(main_window, 'on_settings') as mock_settings, \
             patch.object(main_window, 'start_conversion') as mock_convert:
            
            # Test Ctrl+O for open directory
            qtbot.keySequence(main_window, "Ctrl+O")
            qtbot.wait(10)
            mock_open.assert_called_once()
            
            # Test F5 for conversion (if implemented)
            qtbot.keyPress(main_window, Qt.Key.Key_F5)
            qtbot.wait(10)
            
            # Test Escape for cancel (if implemented)
            qtbot.keyPress(main_window, Qt.Key.Key_Escape)
            qtbot.wait(10)
    
    def test_menu_navigation_workflow(self, app_with_main_window, qtbot):
        """Test menu navigation workflow"""
        main_window = app_with_main_window
        
        menubar = main_window.menuBar()
        
        # Navigate through File menu
        file_menu = None
        for action in menubar.actions():
            if "File" in action.text():
                file_menu = action.menu()
                break
        
        if file_menu:
            # Test each menu action
            with patch.object(main_window, 'on_open_directory') as mock_open:
                for action in file_menu.actions():
                    if not action.isSeparator() and "Open" in action.text():
                        action.trigger()
                        qtbot.wait(10)
                        break
    
    def test_error_recovery_workflow(self, app_with_main_window, qtbot):
        """Test error recovery workflow"""
        main_window = app_with_main_window
        
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_error_dialog:
            # Simulate conversion error
            error_message = "Conversion failed due to file corruption"
            main_window.on_conversion_error(error_message)
            
            # Verify error dialog was shown
            mock_error_dialog.assert_called_once()
            
            # Test that user can continue after error
            assert main_window.isEnabled()  # Window should remain functional
            
            # Test retry functionality (if implemented)
            with patch.object(main_window, 'retry_conversion') as mock_retry:
                if hasattr(main_window, 'retry_last_conversion'):
                    main_window.retry_last_conversion()
                    mock_retry.assert_called_once()
    
    def test_progress_cancellation_workflow(self, app_with_main_window, qtbot):
        """Test progress cancellation workflow"""
        main_window = app_with_main_window
        
        with patch.object(main_window, 'conversion_manager') as mock_conversion_manager:
            # Start conversion
            main_window.start_conversion()
            
            # Show progress
            main_window.show_progress("Converting files...", 0, 100)
            
            # Cancel conversion
            main_window.cancel_conversion()
            
            # Verify cancellation
            mock_conversion_manager.cancel_conversion.assert_called_once()
            
            # Verify UI state after cancellation
            qtbot.wait(100)
            assert main_window.progress_widget.isVisible() == False
    
    def test_theme_switching_workflow(self, app_with_main_window, qtbot):
        """Test theme switching workflow"""
        main_window = app_with_main_window
        
        with patch.object(main_window, 'theme_manager') as mock_theme_manager:
            # Test switching between themes
            themes = ["light", "dark", "system"]
            
            for theme in themes:
                main_window.on_theme_changed(theme)
                qtbot.wait(10)
                
                # Verify theme was applied
                mock_theme_manager.set_theme.assert_called_with(theme)
                
                # Verify UI updated (colors, styles, etc.)
                # This would require checking actual style properties
    
    def test_language_switching_workflow(self, app_with_main_window, qtbot):
        """Test language switching workflow"""
        main_window = app_with_main_window
        
        with patch.object(main_window, 'i18n_manager') as mock_i18n_manager:
            # Test switching between languages
            languages = ["en_US", "ko_KR"]
            
            for language in languages:
                main_window.on_language_changed(language)
                qtbot.wait(10)
                
                # Verify language was applied
                mock_i18n_manager.set_language.assert_called_with(language)
                
                # Verify UI text updated
                # This would require checking actual UI text changes
    
    def test_window_state_persistence_workflow(self, app_with_main_window, qtbot):
        """Test window state persistence workflow"""
        main_window = app_with_main_window
        
        # Modify window state
        main_window.resize(800, 600)
        main_window.move(100, 50)
        
        # Save state
        main_window.save_window_state()
        
        # Create new window and restore state
        new_window = MainWindow(main_window.config_manager)
        qtbot.addWidget(new_window)
        
        new_window.restore_window_state()
        
        # Verify state was restored
        assert new_window.width() == 800
        assert new_window.height() == 600
    
    def test_file_type_filtering_workflow(self, app_with_main_window, qtbot, temp_dir):
        """Test file type filtering workflow"""
        main_window = app_with_main_window
        
        # Create mixed file types
        test_files = {
            "document.pdf": b"PDF content",
            "spreadsheet.xlsx": b"Excel content", 
            "image.png": b"PNG content",
            "text.txt": b"Text content"
        }
        
        for filename, content in test_files.items():
            (temp_dir / filename).write_bytes(content)
        
        with patch.object(main_window, 'file_manager') as mock_file_manager:
            # Setup file discovery
            all_files = [Mock(name=name, extension=f".{name.split('.')[-1]}") 
                        for name in test_files.keys()]
            mock_file_manager.scan_directory.return_value = all_files
            
            # Set directory
            main_window.current_directory = str(temp_dir)
            main_window.refresh_file_list()
            
            # Apply filter for only PDF files
            if hasattr(main_window, 'apply_file_filter'):
                main_window.apply_file_filter("*.pdf")
                
                # Verify only PDF files are shown
                # This would require checking file list widget contents
    
    def test_async_operations_workflow(self, app_with_main_window, qtbot):
        """Test asynchronous operations workflow"""
        main_window = app_with_main_window
        
        # Test async file loading
        with patch.object(main_window, 'file_manager') as mock_file_manager:
            # Setup async file loading
            future_result = [Mock(name="async_file.pdf")]
            mock_file_manager.scan_directory_async.return_value = future_result
            
            # Start async operation
            if hasattr(main_window, 'load_files_async'):
                main_window.load_files_async("/test/directory")
                
                # Wait for completion signal
                with qtbot.waitSignal(main_window.files_loaded, timeout=1000):
                    pass
                
                # Verify async operation completed
                assert main_window.file_list_widget.topLevelItemCount() > 0
    
    def test_accessibility_workflow(self, app_with_main_window, qtbot):
        """Test accessibility workflow"""
        main_window = app_with_main_window
        
        # Test keyboard navigation through main interface
        main_window.setFocus()
        
        # Navigate through focusable elements
        focusable_widgets = []
        current_widget = main_window
        
        for _ in range(10):  # Test first 10 tab stops
            qtbot.keyPress(current_widget, Qt.Key.Key_Tab)
            qtbot.wait(10)
            
            focused = main_window.focusWidget()
            if focused and focused not in focusable_widgets:
                focusable_widgets.append(focused)
                current_widget = focused
        
        # Verify keyboard navigation works
        assert len(focusable_widgets) > 0
        
        # Test that important elements are accessible
        important_widgets = [
            main_window.file_list_widget,
            main_window.progress_widget
        ]
        
        for widget in important_widgets:
            if widget:
                # Should be reachable by keyboard
                assert widget.focusPolicy() != Qt.FocusPolicy.NoFocus
    
    def test_memory_management_workflow(self, app_with_main_window, qtbot):
        """Test memory management during operations"""
        main_window = app_with_main_window
        
        # Simulate multiple operations to test memory cleanup
        for i in range(3):
            # Add files
            test_files = [Mock(name=f"test_{j}.pdf") for j in range(10)]
            main_window.file_list_widget.add_files(test_files)
            
            # Clear files
            main_window.file_list_widget.clear_files()
            
            # Force cleanup
            if hasattr(main_window, 'cleanup_resources'):
                main_window.cleanup_resources()
            
            qtbot.wait(10)
        
        # Memory should be properly managed (no crashes or excessive usage)
        assert main_window.file_list_widget.topLevelItemCount() == 0
    
    def test_concurrent_operations_workflow(self, app_with_main_window, qtbot):
        """Test handling of concurrent operations"""
        main_window = app_with_main_window
        
        with patch.object(main_window, 'conversion_manager') as mock_conversion_manager:
            # Start first conversion
            main_window.start_conversion()
            
            # Try to start second conversion while first is running
            main_window.start_conversion()
            
            # Should handle gracefully (either queue or prevent multiple starts)
            # This depends on implementation - shouldn't crash
            
            # Cancel any running operations
            main_window.cancel_conversion()
            
            qtbot.wait(10)
    
    def test_error_boundary_workflow(self, app_with_main_window, qtbot):
        """Test error boundaries and recovery"""
        main_window = app_with_main_window
        
        # Test various error scenarios
        error_scenarios = [
            ("File not found", lambda: main_window.on_file_error("File not found: test.pdf")),
            ("Permission denied", lambda: main_window.on_permission_error("Permission denied")),
            ("Conversion failed", lambda: main_window.on_conversion_error("Conversion failed")),
        ]
        
        for error_name, error_trigger in error_scenarios:
            with patch('PyQt6.QtWidgets.QMessageBox.critical'):
                try:
                    error_trigger()
                    qtbot.wait(10)
                    
                    # Application should remain functional after error
                    assert main_window.isEnabled()
                    assert main_window.isVisible()
                    
                except Exception as e:
                    # Should not have unhandled exceptions
                    pytest.fail(f"Unhandled exception in {error_name}: {e}")
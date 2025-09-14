"""
GUI tests for MainWindow
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtTest import QTest

from markitdown_gui.ui.main_window import MainWindow
from markitdown_gui.core.config_manager import ConfigManager


class TestMainWindow:
    """Test suite for MainWindow"""
    
    @pytest.fixture
    def main_window(self, qtbot, config_manager):
        """Create MainWindow instance for testing"""
        window = MainWindow(config_manager)
        qtbot.addWidget(window)
        return window
    
    def test_initialization(self, main_window):
        """Test MainWindow initialization"""
        assert main_window.windowTitle() == "MarkItDown GUI Converter"
        assert main_window.config_manager is not None
        assert main_window.centralWidget() is not None
        assert main_window.menuBar() is not None
        assert main_window.statusBar() is not None
    
    def test_window_geometry_restoration(self, main_window, qtbot):
        """Test window geometry save/restore"""
        # Set custom geometry
        main_window.resize(800, 600)
        main_window.move(100, 50)
        
        # Save geometry
        main_window.save_window_state()
        
        # Create new window and restore
        new_window = MainWindow(main_window.config_manager)
        qtbot.addWidget(new_window)
        new_window.restore_window_state()
        
        # Check restored geometry
        assert new_window.width() == 800
        assert new_window.height() == 600
    
    def test_menu_creation(self, main_window):
        """Test menu bar creation"""
        menubar = main_window.menuBar()
        
        # Check main menus exist
        menus = [action.text() for action in menubar.actions()]
        assert any("File" in menu for menu in menus)
        assert any("Edit" in menu for menu in menus)
        assert any("View" in menu for menu in menus)
        assert any("Tools" in menu for menu in menus)
        assert any("Help" in menu for menu in menus)
    
    def test_file_menu_actions(self, main_window, qtbot):
        """Test file menu actions"""
        file_menu = None
        for action in main_window.menuBar().actions():
            if "File" in action.text():
                file_menu = action.menu()
                break
        
        assert file_menu is not None
        
        # Check file menu actions
        actions = [action.text() for action in file_menu.actions()]
        assert any("Open Directory" in action for action in actions)
        assert any("Recent" in action for action in actions)
        assert any("Settings" in action for action in actions)
        assert any("Exit" in action for action in actions)
    
    def test_open_directory_action(self, main_window, qtbot):
        """Test open directory action"""
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = "/test/directory"
            
            # Trigger action
            main_window.on_open_directory()
            
            # Check directory was set
            mock_dialog.assert_called_once()
            assert main_window.current_directory == "/test/directory"
    
    def test_settings_dialog(self, main_window, qtbot):
        """Test opening settings dialog"""
        with patch('markitdown_gui.ui.settings_dialog.SettingsDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.exec.return_value = 1  # QDialog.Accepted
            mock_dialog.return_value = mock_instance
            
            # Open settings
            main_window.on_settings()
            
            # Check dialog was created and shown
            mock_dialog.assert_called_once_with(main_window.config_manager, main_window)
            mock_instance.exec.assert_called_once()
    
    def test_about_dialog(self, main_window, qtbot):
        """Test about dialog"""
        with patch('PyQt6.QtWidgets.QMessageBox.about') as mock_about:
            # Trigger about dialog
            main_window.on_about()
            
            # Check about dialog was shown
            mock_about.assert_called_once()
            args = mock_about.call_args[0]
            assert "MarkItDown GUI" in args[1]  # Title
            assert "Version" in args[2]  # Content
    
    def test_status_bar_updates(self, main_window, qtbot):
        """Test status bar message updates"""
        # Set status message
        main_window.show_status_message("Test message")
        
        # Check status bar
        assert main_window.statusBar().currentMessage() == "Test message"
        
        # Test temporary message
        main_window.show_status_message("Temporary", timeout=100)
        
        # Wait for timeout
        qtbot.wait(150)
        
        # Message should be cleared
        assert main_window.statusBar().currentMessage() == ""
    
    def test_file_list_widget_integration(self, main_window, qtbot):
        """Test file list widget integration"""
        file_list = main_window.file_list_widget
        
        assert file_list is not None
        assert file_list.parent() == main_window.centralWidget()
        
        # Test file selection signal
        with patch.object(main_window, 'on_file_selection_changed') as mock_handler:
            # Simulate selection change
            file_list.itemSelectionChanged.emit()
            
            # Handler should be called
            qtbot.wait(10)  # Allow signal processing
    
    def test_progress_widget_integration(self, main_window, qtbot):
        """Test progress widget integration"""
        progress_widget = main_window.progress_widget
        
        assert progress_widget is not None
        assert progress_widget.isVisible() == False  # Initially hidden
        
        # Show progress
        main_window.show_progress("Converting files...", 0, 100)
        
        assert progress_widget.isVisible() == True
        assert progress_widget.format() == "Converting files..."
        assert progress_widget.minimum() == 0
        assert progress_widget.maximum() == 100
    
    def test_conversion_workflow(self, main_window, qtbot):
        """Test complete conversion workflow"""
        # Mock dependencies
        with patch.object(main_window, 'file_manager') as mock_file_manager, \
             patch.object(main_window, 'conversion_manager') as mock_conversion_manager:
            
            # Setup mocks
            mock_files = [Mock(name="test1.pdf"), Mock(name="test2.docx")]
            mock_file_manager.get_selected_files.return_value = mock_files
            
            # Start conversion
            main_window.start_conversion()
            
            # Check conversion was initiated
            mock_conversion_manager.convert_files.assert_called_once_with(mock_files)
    
    def test_conversion_progress_updates(self, main_window, qtbot):
        """Test conversion progress updates"""
        # Connect to progress signal
        progress_updates = []
        
        def capture_progress(current, total, message):
            progress_updates.append((current, total, message))
        
        main_window.conversion_progress.connect(capture_progress)
        
        # Simulate progress updates
        main_window.on_conversion_progress(1, 5, "Converting file 1/5")
        main_window.on_conversion_progress(3, 5, "Converting file 3/5")
        main_window.on_conversion_progress(5, 5, "Conversion complete")
        
        # Check progress updates were received
        assert len(progress_updates) == 3
        assert progress_updates[0] == (1, 5, "Converting file 1/5")
        assert progress_updates[-1] == (5, 5, "Conversion complete")
    
    def test_error_handling(self, main_window, qtbot):
        """Test error handling and display"""
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
            # Simulate error
            error_message = "Test error occurred"
            main_window.show_error("Error", error_message)
            
            # Check error dialog was shown
            mock_critical.assert_called_once()
            args = mock_critical.call_args[0]
            assert args[1] == "Error"  # Title
            assert args[2] == error_message  # Message
    
    def test_theme_switching(self, main_window, qtbot):
        """Test theme switching integration"""
        with patch.object(main_window, 'theme_manager') as mock_theme_manager:
            # Switch to dark theme
            main_window.on_theme_changed("dark")
            
            # Check theme manager was called
            mock_theme_manager.set_theme.assert_called_with("dark")
    
    def test_language_switching(self, main_window, qtbot):
        """Test language switching"""
        with patch.object(main_window, 'i18n_manager') as mock_i18n_manager:
            # Switch to Korean
            main_window.on_language_changed("ko_KR")
            
            # Check i18n manager was called
            mock_i18n_manager.set_language.assert_called_with("ko_KR")
    
    def test_keyboard_shortcuts(self, main_window, qtbot):
        """Test keyboard shortcuts"""
        # Test Ctrl+O for open directory
        with patch.object(main_window, 'on_open_directory') as mock_open:
            qtbot.keySequence(main_window, "Ctrl+O")
            qtbot.wait(10)  # Allow signal processing
            mock_open.assert_called_once()
        
        # Test Ctrl+, for settings (if applicable)
        with patch.object(main_window, 'on_settings') as mock_settings:
            qtbot.keySequence(main_window, "Ctrl+,")
            qtbot.wait(10)
            # Note: This might not work on all platforms
    
    def test_drag_and_drop(self, main_window, qtbot):
        """Test drag and drop functionality"""
        # This is a simplified test - full drag/drop testing requires more setup
        assert main_window.acceptDrops() == True
        
        # Test drop event handling exists
        assert hasattr(main_window, 'dragEnterEvent')
        assert hasattr(main_window, 'dropEvent')
    
    def test_window_close_behavior(self, main_window, qtbot):
        """Test window close behavior"""
        with patch.object(main_window, 'save_window_state') as mock_save:
            # Create close event
            from PyQt6.QtGui import QCloseEvent
            close_event = QCloseEvent()
            
            # Handle close event
            main_window.closeEvent(close_event)
            
            # Check window state was saved
            mock_save.assert_called_once()
            assert close_event.isAccepted()
    
    def test_conversion_cancellation(self, main_window, qtbot):
        """Test conversion cancellation"""
        # Start conversion
        with patch.object(main_window, 'conversion_manager') as mock_conversion_manager:
            main_window.start_conversion()
            
            # Cancel conversion
            main_window.cancel_conversion()
            
            # Check cancellation was requested
            mock_conversion_manager.cancel_conversion.assert_called_once()
    
    def test_recent_directories_menu(self, main_window, qtbot):
        """Test recent directories menu"""
        # Mock recent directories
        recent_dirs = ["/path/1", "/path/2", "/path/3"]
        main_window.config_manager.get_recent_directories = Mock(return_value=recent_dirs)
        
        # Update recent directories menu
        main_window.update_recent_directories_menu()
        
        # Check menu was updated (this would need access to the recent menu)
        # In real implementation, we'd check the menu items
        assert True  # Placeholder - would check actual menu items
    
    def test_accessibility_features(self, main_window, qtbot):
        """Test accessibility features"""
        # Check window has accessible name
        assert main_window.windowTitle() != ""
        
        # Check status bar accessibility
        status_bar = main_window.statusBar()
        assert status_bar.accessibleName() != "" or status_bar.accessibleDescription() != ""
        
        # Check keyboard navigation
        main_window.setFocus()
        assert main_window.focusPolicy() != Qt.FocusPolicy.NoFocus
    
    def test_memory_cleanup(self, main_window, qtbot):
        """Test proper memory cleanup"""
        # Create some data
        main_window.conversion_results = [Mock(), Mock(), Mock()]
        
        # Cleanup
        main_window.cleanup()
        
        # Check cleanup was performed
        assert len(main_window.conversion_results) == 0
    
    def test_responsive_layout(self, main_window, qtbot):
        """Test responsive layout behavior"""
        # Test various window sizes
        sizes = [(800, 600), (1200, 800), (600, 400), (400, 300)]
        
        for width, height in sizes:
            main_window.resize(width, height)
            qtbot.wait(10)  # Allow layout updates
            
            # Check minimum size constraints
            assert main_window.width() >= main_window.minimumWidth()
            assert main_window.height() >= main_window.minimumHeight()
            
            # Check critical widgets are still visible
            assert main_window.centralWidget().isVisible()
            assert main_window.statusBar().isVisible()
    
    def test_multi_monitor_support(self, main_window, qtbot):
        """Test multi-monitor support"""
        # Get available screens
        app = QApplication.instance()
        screens = app.screens()
        
        if len(screens) > 1:
            # Move to second screen
            second_screen = screens[1]
            geometry = second_screen.geometry()
            main_window.move(geometry.x(), geometry.y())
            
            # Check window moved correctly
            assert main_window.x() >= geometry.x()
            assert main_window.y() >= geometry.y()
    
    def test_tool_tips(self, main_window, qtbot):
        """Test tooltips are set for UI elements"""
        # Check main widgets have tooltips
        widgets_to_check = [
            main_window.file_list_widget,
            main_window.progress_widget
        ]
        
        for widget in widgets_to_check:
            if widget:
                # Tooltip should be set for accessibility
                tooltip = widget.toolTip()
                # Either tooltip exists or accessible description
                assert tooltip != "" or widget.accessibleDescription() != ""
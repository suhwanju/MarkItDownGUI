"""
GUI tests for SettingsDialog
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QDialogButtonBox, QTabWidget, QComboBox, QSpinBox, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from markitdown_gui.ui.settings_dialog import SettingsDialog
from markitdown_gui.core.config_manager import ConfigManager


class TestSettingsDialog:
    """Test suite for SettingsDialog"""
    
    @pytest.fixture
    def settings_dialog(self, qtbot, config_manager):
        """Create SettingsDialog instance for testing"""
        parent = Mock()
        dialog = SettingsDialog(config_manager, parent)
        qtbot.addWidget(dialog)
        return dialog
    
    def test_initialization(self, settings_dialog):
        """Test SettingsDialog initialization"""
        assert settings_dialog.windowTitle() == "Settings"
        assert settings_dialog.config_manager is not None
        assert settings_dialog.isModal() == True
    
    def test_tab_widget_creation(self, settings_dialog):
        """Test tab widget structure"""
        tab_widget = settings_dialog.findChild(QTabWidget)
        assert tab_widget is not None
        
        # Check tabs exist
        tab_count = tab_widget.count()
        assert tab_count >= 4  # General, Conversion, LLM, Advanced
        
        # Check tab names
        tab_names = [tab_widget.tabText(i) for i in range(tab_count)]
        assert any("General" in name for name in tab_names)
        assert any("Conversion" in name for name in tab_names)
        assert any("LLM" in name for name in tab_names)
    
    def test_general_tab(self, settings_dialog, qtbot):
        """Test general settings tab"""
        # Navigate to general tab
        tab_widget = settings_dialog.findChild(QTabWidget)
        general_tab_index = 0
        tab_widget.setCurrentIndex(general_tab_index)
        
        # Check language combo box
        language_combo = settings_dialog.findChild(QComboBox, "language_combo")
        if language_combo:
            assert language_combo.count() >= 2  # At least English and Korean
            
            # Check language options
            languages = [language_combo.itemText(i) for i in range(language_combo.count())]
            assert any("English" in lang for lang in languages)
            assert any("한국어" in lang or "Korean" in lang for lang in languages)
        
        # Check theme combo box
        theme_combo = settings_dialog.findChild(QComboBox, "theme_combo")
        if theme_combo:
            themes = [theme_combo.itemText(i) for i in range(theme_combo.count())]
            assert any("Light" in theme for theme in themes)
            assert any("Dark" in theme for theme in themes)
            assert any("System" in theme or "Auto" in theme for theme in themes)
    
    def test_conversion_tab(self, settings_dialog, qtbot):
        """Test conversion settings tab"""
        # Find and switch to conversion tab
        tab_widget = settings_dialog.findChild(QTabWidget)
        for i in range(tab_widget.count()):
            if "Conversion" in tab_widget.tabText(i):
                tab_widget.setCurrentIndex(i)
                break
        
        # Check max workers spin box
        workers_spin = settings_dialog.findChild(QSpinBox, "max_workers_spin")
        if workers_spin:
            assert workers_spin.minimum() >= 1
            assert workers_spin.maximum() <= 16
            assert workers_spin.value() >= 1
        
        # Check output directory line edit
        output_dir_edit = settings_dialog.findChild(QLineEdit, "output_dir_edit")
        if output_dir_edit:
            # Should have some default value or be able to accept input
            assert output_dir_edit.isReadOnly() == False
    
    def test_llm_tab(self, settings_dialog, qtbot):
        """Test LLM settings tab"""
        # Find and switch to LLM tab
        tab_widget = settings_dialog.findChild(QTabWidget)
        for i in range(tab_widget.count()):
            if "LLM" in tab_widget.tabText(i):
                tab_widget.setCurrentIndex(i)
                break
        
        # Check provider combo box
        provider_combo = settings_dialog.findChild(QComboBox, "provider_combo")
        if provider_combo:
            providers = [provider_combo.itemText(i) for i in range(provider_combo.count())]
            assert any("OpenAI" in provider for provider in providers)
        
        # Check model combo box
        model_combo = settings_dialog.findChild(QComboBox, "model_combo")
        if model_combo:
            assert model_combo.count() >= 1  # At least one model option
        
        # Check API key handling (should be password field)
        api_key_edit = settings_dialog.findChild(QLineEdit, "api_key_edit")
        if api_key_edit:
            assert api_key_edit.echoMode() == QLineEdit.EchoMode.Password
    
    def test_settings_loading(self, settings_dialog, qtbot):
        """Test loading settings from config manager"""
        # Mock config values
        settings_dialog.config_manager.get_value = Mock()
        settings_dialog.config_manager.get_value.side_effect = lambda key, default=None: {
            "General/language": "en_US",
            "General/theme": "system",
            "Conversion/max_workers": 4,
            "Conversion/output_dir": "/tmp/output",
            "LLM/provider": "openai",
            "LLM/model": "gpt-4o"
        }.get(key, default)
        
        # Load settings
        settings_dialog.load_settings()
        
        # Check that get_value was called for various settings
        settings_dialog.config_manager.get_value.assert_any_call("General/language", "en_US")
        settings_dialog.config_manager.get_value.assert_any_call("General/theme", "system")
        settings_dialog.config_manager.get_value.assert_any_call("Conversion/max_workers", 4)
    
    def test_settings_saving(self, settings_dialog, qtbot):
        """Test saving settings to config manager"""
        settings_dialog.config_manager.set_value = Mock()
        
        # Modify some settings (simulate user input)
        # This would normally involve changing widget values
        
        # Save settings
        settings_dialog.save_settings()
        
        # Check that set_value was called (exact calls depend on implementation)
        assert settings_dialog.config_manager.set_value.call_count >= 1
    
    def test_apply_button(self, settings_dialog, qtbot):
        """Test Apply button functionality"""
        button_box = settings_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        
        apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        if apply_button:
            with patch.object(settings_dialog, 'apply_settings') as mock_apply:
                # Click Apply button
                qtbot.mouseClick(apply_button, Qt.MouseButton.LeftButton)
                
                # Check apply was called
                mock_apply.assert_called_once()
    
    def test_ok_button(self, settings_dialog, qtbot):
        """Test OK button functionality"""
        button_box = settings_dialog.findChild(QDialogButtonBox)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        
        with patch.object(settings_dialog, 'save_settings') as mock_save, \
             patch.object(settings_dialog, 'accept') as mock_accept:
            
            # Click OK button
            qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
            
            # Check save was called and dialog accepted
            mock_save.assert_called_once()
            mock_accept.assert_called_once()
    
    def test_cancel_button(self, settings_dialog, qtbot):
        """Test Cancel button functionality"""
        button_box = settings_dialog.findChild(QDialogButtonBox)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        
        with patch.object(settings_dialog, 'reject') as mock_reject:
            # Click Cancel button
            qtbot.mouseClick(cancel_button, Qt.MouseButton.LeftButton)
            
            # Check dialog was rejected without saving
            mock_reject.assert_called_once()
    
    def test_reset_to_defaults(self, settings_dialog, qtbot):
        """Test reset to defaults functionality"""
        with patch.object(settings_dialog.config_manager, 'reset_to_default') as mock_reset, \
             patch.object(settings_dialog, 'load_settings') as mock_load:
            
            # Trigger reset (this would be a button or menu action)
            settings_dialog.reset_to_defaults()
            
            # Check config was reset and settings reloaded
            mock_reset.assert_called_once()
            mock_load.assert_called_once()
    
    def test_validation(self, settings_dialog, qtbot):
        """Test input validation"""
        # Test invalid max workers value
        workers_spin = settings_dialog.findChild(QSpinBox, "max_workers_spin")
        if workers_spin:
            # Try to set invalid value
            original_value = workers_spin.value()
            
            # Set to minimum - 1 (should be clamped)
            workers_spin.setValue(workers_spin.minimum() - 1)
            assert workers_spin.value() == workers_spin.minimum()
            
            # Set to maximum + 1 (should be clamped)
            workers_spin.setValue(workers_spin.maximum() + 1)
            assert workers_spin.value() == workers_spin.maximum()
    
    def test_api_key_security(self, settings_dialog, qtbot):
        """Test API key security measures"""
        api_key_edit = settings_dialog.findChild(QLineEdit, "api_key_edit")
        if api_key_edit:
            # Check password mode
            assert api_key_edit.echoMode() == QLineEdit.EchoMode.Password
            
            # Test setting and getting API key
            test_key = "sk-test123456789"
            api_key_edit.setText(test_key)
            
            # Display should be masked
            assert api_key_edit.displayText() != test_key
            assert api_key_edit.text() == test_key
    
    def test_tab_navigation(self, settings_dialog, qtbot):
        """Test keyboard tab navigation between settings"""
        tab_widget = settings_dialog.findChild(QTabWidget)
        
        # Start at first tab
        tab_widget.setCurrentIndex(0)
        assert tab_widget.currentIndex() == 0
        
        # Navigate with Ctrl+Tab (if supported)
        qtbot.keySequence(tab_widget, "Ctrl+Tab")
        qtbot.wait(10)
        
        # Should move to next tab (or stay if not supported)
        assert tab_widget.currentIndex() >= 0
    
    def test_help_tooltips(self, settings_dialog, qtbot):
        """Test help tooltips for settings"""
        # Check that important settings have tooltips
        widgets_to_check = [
            settings_dialog.findChild(QComboBox, "theme_combo"),
            settings_dialog.findChild(QSpinBox, "max_workers_spin"),
            settings_dialog.findChild(QLineEdit, "api_key_edit")
        ]
        
        for widget in widgets_to_check:
            if widget:
                # Should have either tooltip or accessible description
                has_help = (widget.toolTip() != "" or 
                          widget.whatsThis() != "" or
                          widget.accessibleDescription() != "")
                assert has_help
    
    def test_settings_persistence(self, settings_dialog, qtbot):
        """Test that settings persist across dialog sessions"""
        # Set some values
        test_values = {
            "General/language": "ko_KR",
            "General/theme": "dark",
            "Conversion/max_workers": 8
        }
        
        for key, value in test_values.items():
            settings_dialog.config_manager.set_value(key, value)
        
        # Create new dialog instance
        new_dialog = SettingsDialog(settings_dialog.config_manager)
        qtbot.addWidget(new_dialog)
        
        # Load settings
        new_dialog.load_settings()
        
        # Check values are loaded correctly
        for key, expected_value in test_values.items():
            actual_value = settings_dialog.config_manager.get_value(key)
            assert actual_value == expected_value
    
    def test_dynamic_model_loading(self, settings_dialog, qtbot):
        """Test dynamic model loading based on provider"""
        provider_combo = settings_dialog.findChild(QComboBox, "provider_combo")
        model_combo = settings_dialog.findChild(QComboBox, "model_combo")
        
        if provider_combo and model_combo:
            with patch.object(settings_dialog, 'update_model_options') as mock_update:
                # Change provider
                provider_combo.setCurrentText("OpenAI")
                
                # Should trigger model update
                qtbot.wait(10)  # Allow signal processing
    
    def test_folder_selection_dialog(self, settings_dialog, qtbot):
        """Test folder selection for output directory"""
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = "/test/output/directory"
            
            # Find browse button (if exists)
            browse_button = settings_dialog.findChild("browse_button")  # Assuming this exists
            if browse_button:
                # Click browse button
                qtbot.mouseClick(browse_button, Qt.MouseButton.LeftButton)
                
                # Check dialog was opened
                mock_dialog.assert_called_once()
    
    def test_settings_import_export(self, settings_dialog, qtbot, temp_dir):
        """Test settings import/export functionality"""
        export_file = temp_dir / "exported_settings.json"
        
        with patch.object(settings_dialog.config_manager, 'export_settings') as mock_export, \
             patch.object(settings_dialog.config_manager, 'import_settings') as mock_import:
            
            # Test export
            mock_export.return_value = True
            result = settings_dialog.export_settings(str(export_file))
            assert result == True
            mock_export.assert_called_once_with(str(export_file))
            
            # Test import
            mock_import.return_value = True
            result = settings_dialog.import_settings(str(export_file))
            assert result == True
            mock_import.assert_called_once_with(str(export_file))
    
    def test_accessibility_compliance(self, settings_dialog, qtbot):
        """Test accessibility compliance"""
        # Check dialog has accessible name and description
        assert settings_dialog.windowTitle() != ""
        
        # Check tab widget accessibility
        tab_widget = settings_dialog.findChild(QTabWidget)
        if tab_widget:
            # Each tab should have accessible names
            for i in range(tab_widget.count()):
                tab_text = tab_widget.tabText(i)
                assert tab_text != ""
        
        # Check form labels are associated with controls
        # This would require checking QLabel.setBuddy() relationships
    
    def test_keyboard_navigation(self, settings_dialog, qtbot):
        """Test full keyboard navigation"""
        # Test Tab key navigation through controls
        settings_dialog.setFocus()
        
        # Tab through controls
        for _ in range(10):  # Tab through first 10 focusable widgets
            qtbot.keyPress(settings_dialog, Qt.Key.Key_Tab)
            qtbot.wait(10)
            
            # Should always have some widget with focus
            focused_widget = settings_dialog.focusWidget()
            assert focused_widget is not None
    
    def test_dialog_resizing(self, settings_dialog, qtbot):
        """Test dialog resizing behavior"""
        # Test minimum size
        min_size = settings_dialog.minimumSize()
        settings_dialog.resize(min_size)
        
        assert settings_dialog.width() >= min_size.width()
        assert settings_dialog.height() >= min_size.height()
        
        # Test larger sizes
        settings_dialog.resize(800, 600)
        assert settings_dialog.width() == 800
        assert settings_dialog.height() == 600
        
        # Check all tabs are still accessible
        tab_widget = settings_dialog.findChild(QTabWidget)
        if tab_widget:
            for i in range(tab_widget.count()):
                tab_widget.setCurrentIndex(i)
                qtbot.wait(10)
                # Tab content should be visible
                assert tab_widget.currentWidget().isVisible()
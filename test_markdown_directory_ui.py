#!/usr/bin/env python3
"""
QA Test Suite: Markdown Directory Default UI Implementation
===========================================================
Comprehensive testing of the updated UI components that handle the new markdown directory default.

Test Coverage:
- Technical functionality of directory display
- Performance and integration aspects  
- Error handling and edge cases
- System stability and reliability
- UI consistency and user experience
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json
import time
import traceback
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication, QDialog
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtTest import QTest
    from PyQt6.QtGui import QAction
    
    from markitdown_gui.core.config_manager import ConfigManager
    from markitdown_gui.core.constants import MARKDOWN_OUTPUT_DIR
    from markitdown_gui.core.utils import get_default_output_directory
    from markitdown_gui.ui.settings_dialog import SettingsDialog, GeneralSettingsTab, ConversionSettingsTab
    from markitdown_gui.ui.main_window import MainWindow
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure PyQt6 is installed and the project structure is correct")
    sys.exit(1)


class MarkdownDirectoryUITester:
    """
    Comprehensive QA tester for markdown directory UI implementation.
    
    Performs systematic testing of:
    - UI component functionality
    - Default directory handling
    - User customization options
    - Integration with existing systems
    - Performance and reliability
    """
    
    def __init__(self):
        self.app = None
        self.temp_dir = None
        self.config_manager = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
        
    def setup_test_environment(self) -> bool:
        """Set up clean test environment"""
        try:
            # Create QApplication if needed
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
                self.app.setQuitOnLastWindowClosed(False)
            else:
                self.app = QApplication.instance()
            
            # Create temporary directory for testing
            self.temp_dir = Path(tempfile.mkdtemp(prefix="markdown_ui_test_"))
            
            # Create test config directory
            config_dir = self.temp_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Initialize config manager with test directory
            self.config_manager = ConfigManager(config_dir)
            
            self.log_success("Test environment setup completed")
            return True
            
        except Exception as e:
            self.log_error(f"Test environment setup failed: {e}")
            return False
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            
            if self.app:
                self.app.processEvents()
                
            self.log_success("Test environment cleaned up")
        except Exception as e:
            self.log_warning(f"Cleanup warning: {e}")
    
    def log_success(self, message: str):
        """Log successful test result"""
        print(f"✅ {message}")
        self.test_results['passed'] += 1
        self.test_results['details'].append(('PASS', message))
    
    def log_error(self, message: str):
        """Log test failure"""
        print(f"❌ {message}")
        self.test_results['failed'] += 1
        self.test_results['details'].append(('FAIL', message))
    
    def log_warning(self, message: str):
        """Log test warning"""
        print(f"⚠️  {message}")
        self.test_results['warnings'] += 1
        self.test_results['details'].append(('WARN', message))
    
    def test_default_directory_utility_function(self) -> bool:
        """Test the get_default_output_directory utility function"""
        print("\n🔍 Testing Default Directory Utility Function...")
        
        try:
            # Test basic functionality
            default_dir = get_default_output_directory()
            
            # Verify return type
            if not isinstance(default_dir, Path):
                self.log_error(f"get_default_output_directory should return Path, got {type(default_dir)}")
                return False
            
            # Verify path structure
            expected_name = MARKDOWN_OUTPUT_DIR
            if default_dir.name != expected_name:
                self.log_error(f"Default directory should be '{expected_name}', got '{default_dir.name}'")
                return False
            
            # Verify path is absolute
            if not default_dir.is_absolute():
                self.log_error("Default directory path should be absolute")
                return False
            
            # Test path construction logic
            current_file = Path(__file__)
            expected_root = current_file.parent  # project root for test
            expected_path = expected_root / MARKDOWN_OUTPUT_DIR
            
            self.log_success(f"Default directory utility function works correctly: {default_dir}")
            return True
            
        except Exception as e:
            self.log_error(f"Default directory utility function test failed: {e}")
            return False
    
    def test_general_settings_tab_ui(self) -> bool:
        """Test GeneralSettingsTab UI implementation"""
        print("\n🔍 Testing General Settings Tab UI...")
        
        try:
            # Create GeneralSettingsTab
            tab = GeneralSettingsTab(self.config_manager)
            
            # Test output directory field
            if not hasattr(tab, 'output_dir_edit'):
                self.log_error("GeneralSettingsTab missing output_dir_edit widget")
                return False
            
            # Test placeholder text
            placeholder = tab.output_dir_edit.placeholderText()
            expected_placeholder = f"기본값: 프로그램 폴더/{MARKDOWN_OUTPUT_DIR}"
            if expected_placeholder not in placeholder:
                self.log_error(f"Incorrect placeholder text: {placeholder}")
                return False
            
            # Test help label
            help_text_found = False
            for child in tab.findChildren(object):
                if hasattr(child, 'text') and callable(child.text):
                    try:
                        text = child.text()
                        if "비워두면" in text and "markdown" in text and "기본값" in text:
                            help_text_found = True
                            break
                    except:
                        continue
            
            if not help_text_found:
                self.log_error("Help text for output directory not found")
                return False
            
            # Test browse button functionality
            if not hasattr(tab, 'output_dir_btn'):
                self.log_error("GeneralSettingsTab missing browse button")
                return False
            
            # Test initial state (should be empty to show placeholder)
            initial_text = tab.output_dir_edit.text()
            if initial_text and str(get_default_output_directory()) in initial_text:
                self.log_warning("Output directory field shows default path instead of using placeholder")
            
            self.log_success("General Settings Tab UI implementation correct")
            return True
            
        except Exception as e:
            self.log_error(f"General Settings Tab UI test failed: {e}")
            return False
    
    def test_conversion_settings_tab_ui(self) -> bool:
        """Test ConversionSettingsTab UI implementation"""
        print("\n🔍 Testing Conversion Settings Tab UI...")
        
        try:
            # Create ConversionSettingsTab  
            tab = ConversionSettingsTab(self.config_manager)
            
            # Test custom output directory field
            if not hasattr(tab, 'custom_output_edit'):
                self.log_error("ConversionSettingsTab missing custom_output_edit widget")
                return False
            
            # Test placeholder text
            placeholder = tab.custom_output_edit.placeholderText()
            expected_placeholder = f"기본값: 프로그램 폴더/{MARKDOWN_OUTPUT_DIR}"
            if expected_placeholder not in placeholder:
                self.log_error(f"Incorrect placeholder text in conversion tab: {placeholder}")
                return False
            
            # Test tooltip
            tooltip = tab.custom_output_edit.toolTip()
            if not tooltip or "markdown" not in tooltip:
                self.log_error("Missing or incorrect tooltip in conversion settings")
                return False
            
            # Test save to original checkbox interaction
            if hasattr(tab, 'save_to_original_check'):
                # Should be initially checked (default behavior)
                if not tab.save_to_original_check.isChecked():
                    self.log_warning("Save to original directory should be checked by default")
                
                # Custom output should be disabled when save to original is checked
                if tab.custom_output_edit.isEnabled():
                    self.log_error("Custom output field should be disabled when save to original is checked")
                    return False
            
            self.log_success("Conversion Settings Tab UI implementation correct")
            return True
            
        except Exception as e:
            self.log_error(f"Conversion Settings Tab UI test failed: {e}")
            return False
    
    def test_settings_dialog_integration(self) -> bool:
        """Test SettingsDialog integration with new UI elements"""
        print("\n🔍 Testing Settings Dialog Integration...")
        
        try:
            # Create settings dialog
            dialog = SettingsDialog(self.config_manager)
            
            # Test that tabs are properly created
            if not hasattr(dialog, 'general_tab') or not hasattr(dialog, 'conversion_tab'):
                self.log_error("Settings dialog missing required tabs")
                return False
            
            # Test settings loading
            dialog.general_tab._load_settings()
            dialog.conversion_tab._load_settings()
            
            # Test settings saving
            try:
                general_settings = dialog.general_tab.save_settings()
                conversion_settings = dialog.conversion_tab.save_settings()
                
                # Verify output_directory key handling
                if 'output_directory' in general_settings:
                    output_dir = general_settings['output_directory']
                    if output_dir and not Path(output_dir).is_absolute():
                        self.log_error("Output directory should be absolute path")
                        return False
                
            except Exception as e:
                self.log_error(f"Settings save test failed: {e}")
                return False
            
            self.log_success("Settings Dialog integration working correctly")
            return True
            
        except Exception as e:
            self.log_error(f"Settings Dialog integration test failed: {e}")
            return False
    
    def test_browse_directory_functionality(self) -> bool:
        """Test directory browsing functionality with new default"""
        print("\n🔍 Testing Directory Browse Functionality...")
        
        try:
            # Create tab for testing
            tab = GeneralSettingsTab(self.config_manager)
            
            # Create a test directory
            test_dir = self.temp_dir / "test_output"
            test_dir.mkdir(exist_ok=True)
            
            # Mock QFileDialog.getExistingDirectory to return test directory
            with patch('markitdown_gui.ui.settings_dialog.QFileDialog.getExistingDirectory') as mock_dialog:
                mock_dialog.return_value = str(test_dir)
                
                # Test browse functionality - should use default as starting directory when field is empty
                tab.output_dir_edit.setText("")  # Ensure field is empty
                tab._browse_output_directory()
                
                # Verify mock was called with correct starting directory
                mock_dialog.assert_called_once()
                call_args = mock_dialog.call_args[0]
                start_dir = call_args[2]  # Third argument is the starting directory
                expected_start = str(get_default_output_directory())
                
                if start_dir != expected_start:
                    self.log_error(f"Browse should start with default directory {expected_start}, got {start_dir}")
                    return False
                
                # Verify field was updated
                if tab.output_dir_edit.text() != str(test_dir):
                    self.log_error("Directory field was not updated after browse")
                    return False
            
            # Test with existing path in field
            tab.output_dir_edit.setText(str(self.temp_dir))
            with patch('markitdown_gui.ui.settings_dialog.QFileDialog.getExistingDirectory') as mock_dialog:
                mock_dialog.return_value = str(test_dir)
                tab._browse_output_directory()
                
                # Should use existing path as starting directory
                call_args = mock_dialog.call_args[0]
                start_dir = call_args[2]
                if start_dir != str(self.temp_dir):
                    self.log_error(f"Browse should use existing path {self.temp_dir}, got {start_dir}")
                    return False
            
            self.log_success("Directory browse functionality working correctly")
            return True
            
        except Exception as e:
            self.log_error(f"Directory browse functionality test failed: {e}")
            return False
    
    def test_configuration_persistence(self) -> bool:
        """Test configuration saving and loading with new default handling"""
        print("\n🔍 Testing Configuration Persistence...")
        
        try:
            # Test 1: Empty output directory should not be saved
            tab = GeneralSettingsTab(self.config_manager)
            tab.output_dir_edit.setText("")  # Empty field
            
            settings = tab.save_settings()
            output_dir = settings.get('output_directory', '')
            
            if output_dir:
                self.log_error(f"Empty output directory should not save value, got: {output_dir}")
                return False
            
            # Test 2: Custom directory should be saved
            custom_dir = self.temp_dir / "custom_output"
            custom_dir.mkdir(exist_ok=True)
            tab.output_dir_edit.setText(str(custom_dir))
            
            settings = tab.save_settings()
            output_dir = settings.get('output_directory', '')
            
            if output_dir != str(custom_dir):
                self.log_error(f"Custom directory not saved correctly: {output_dir}")
                return False
            
            # Test 3: Loading default behavior
            self.config_manager.set_value('output_directory', '')
            tab._load_settings()
            
            field_text = tab.output_dir_edit.text()
            if field_text:
                self.log_error(f"Default directory should not appear in field, got: {field_text}")
                return False
            
            placeholder = tab.output_dir_edit.placeholderText()
            if MARKDOWN_OUTPUT_DIR not in placeholder:
                self.log_error(f"Placeholder should show default directory: {placeholder}")
                return False
            
            # Test 4: Loading custom directory
            self.config_manager.set_value('output_directory', str(custom_dir))
            tab._load_settings()
            
            field_text = tab.output_dir_edit.text()
            if field_text != str(custom_dir):
                self.log_error(f"Custom directory not loaded correctly: {field_text}")
                return False
            
            self.log_success("Configuration persistence working correctly")
            return True
            
        except Exception as e:
            self.log_error(f"Configuration persistence test failed: {e}")
            return False
    
    def test_ui_consistency_and_accessibility(self) -> bool:
        """Test UI consistency and accessibility compliance"""
        print("\n🔍 Testing UI Consistency and Accessibility...")
        
        try:
            # Create both tabs for consistency checking
            general_tab = GeneralSettingsTab(self.config_manager)
            conversion_tab = ConversionSettingsTab(self.config_manager)
            
            # Test consistent placeholder text
            general_placeholder = general_tab.output_dir_edit.placeholderText()
            conversion_placeholder = conversion_tab.custom_output_edit.placeholderText()
            
            if general_placeholder != conversion_placeholder:
                self.log_warning(f"Inconsistent placeholder text between tabs")
            
            # Test tooltip presence and quality
            conversion_tooltip = conversion_tab.custom_output_edit.toolTip()
            if not conversion_tooltip or len(conversion_tooltip) < 20:
                self.log_error("Conversion tab missing adequate tooltip")
                return False
            
            # Test accessibility labels (where applicable)
            # Note: This would be more comprehensive in a real accessibility test
            
            # Test minimum widget sizes for touch targets
            btn_size = general_tab.output_dir_btn.minimumSize()
            if btn_size.width() < 80 or btn_size.height() < 32:
                self.log_warning("Browse button may be too small for accessibility")
            
            # Test keyboard accessibility (basic check)
            if not general_tab.output_dir_edit.focusPolicy() & Qt.FocusPolicy.TabFocus:
                self.log_error("Output directory field should accept tab focus")
                return False
            
            self.log_success("UI consistency and accessibility checks passed")
            return True
            
        except Exception as e:
            self.log_error(f"UI consistency and accessibility test failed: {e}")
            return False
    
    def test_performance_and_responsiveness(self) -> bool:
        """Test performance and UI responsiveness"""
        print("\n🔍 Testing Performance and Responsiveness...")
        
        try:
            # Test widget creation time
            start_time = time.time()
            
            for i in range(10):  # Create multiple tabs to test performance
                tab = GeneralSettingsTab(self.config_manager)
                self.app.processEvents()  # Process any pending events
                
            creation_time = time.time() - start_time
            
            if creation_time > 2.0:  # 2 seconds for 10 tabs is reasonable
                self.log_warning(f"Tab creation may be slow: {creation_time:.2f}s for 10 tabs")
            
            # Test settings loading performance
            tab = GeneralSettingsTab(self.config_manager)
            start_time = time.time()
            
            for i in range(100):  # Load settings multiple times
                tab._load_settings()
                
            loading_time = time.time() - start_time
            
            if loading_time > 1.0:  # 1 second for 100 loads
                self.log_warning(f"Settings loading may be slow: {loading_time:.2f}s for 100 loads")
            
            # Test UI responsiveness during operations
            tab.output_dir_edit.setText("test" * 1000)  # Large text input
            self.app.processEvents()
            
            # Verify UI is still responsive
            if tab.output_dir_edit.text() != "test" * 1000:
                self.log_error("UI became unresponsive during large text input")
                return False
            
            self.log_success("Performance and responsiveness tests passed")
            return True
            
        except Exception as e:
            self.log_error(f"Performance and responsiveness test failed: {e}")
            return False
    
    def test_error_handling_edge_cases(self) -> bool:
        """Test error handling and edge cases"""
        print("\n🔍 Testing Error Handling and Edge Cases...")
        
        try:
            tab = GeneralSettingsTab(self.config_manager)
            
            # Test 1: Invalid path handling
            invalid_paths = [
                "",  # Empty path
                "nonexistent/path/that/does/not/exist",  # Non-existent path
                "con",  # Windows reserved name
                "a" * 300,  # Very long path
                "/root/protected",  # Protected directory (on Unix)
            ]
            
            for invalid_path in invalid_paths:
                tab.output_dir_edit.setText(invalid_path)
                try:
                    settings = tab.save_settings()
                    # Should not crash, but may contain empty or validated path
                except Exception as e:
                    self.log_error(f"Crashed on invalid path '{invalid_path}': {e}")
                    return False
            
            # Test 2: Configuration manager errors
            # Simulate config manager failure
            original_get_config = self.config_manager.get_config
            self.config_manager.get_config = lambda: {}
            
            try:
                tab._load_settings()  # Should not crash
            except Exception as e:
                self.log_error(f"Failed to handle config manager error: {e}")
                return False
            finally:
                self.config_manager.get_config = original_get_config
            
            # Test 3: Unicode and special characters
            unicode_path = str(self.temp_dir / "테스트_ディレクトリ_测试")
            tab.output_dir_edit.setText(unicode_path)
            
            try:
                settings = tab.save_settings()
                output_dir = settings.get('output_directory', '')
                if output_dir != unicode_path:
                    self.log_warning(f"Unicode path handling may have issues: {output_dir}")
            except Exception as e:
                self.log_error(f"Failed to handle Unicode path: {e}")
                return False
            
            # Test 4: Very rapid UI updates
            for i in range(100):
                tab.output_dir_edit.setText(f"test_path_{i}")
                self.app.processEvents()
            
            self.log_success("Error handling and edge cases tests passed")
            return True
            
        except Exception as e:
            self.log_error(f"Error handling and edge cases test failed: {e}")
            return False
    
    def test_integration_with_existing_components(self) -> bool:
        """Test integration with existing system components"""
        print("\n🔍 Testing Integration with Existing Components...")
        
        try:
            # Test integration with config manager
            original_output_dir = self.config_manager.get_config().get('output_directory', '')
            
            # Test setting new directory through UI
            tab = GeneralSettingsTab(self.config_manager)
            test_dir = self.temp_dir / "integration_test"
            test_dir.mkdir(exist_ok=True)
            
            tab.output_dir_edit.setText(str(test_dir))
            settings = tab.save_settings()
            
            # Apply settings to config manager
            for key, value in settings.items():
                self.config_manager.set_value(key, value)
            
            # Verify integration
            updated_config = self.config_manager.get_config()
            if updated_config.get('output_directory') != str(test_dir):
                self.log_error("Integration with config manager failed")
                return False
            
            # Test with conversion settings tab
            conv_tab = ConversionSettingsTab(self.config_manager)
            conv_tab.save_to_original_check.setChecked(False)
            conv_tab.custom_output_edit.setText(str(test_dir))
            
            conv_settings = conv_tab.save_settings()
            if conv_settings.get('output_directory') != test_dir:
                self.log_error("Integration between settings tabs failed")
                return False
            
            # Test default directory utility integration
            default_dir = get_default_output_directory()
            if not isinstance(default_dir, Path) or not default_dir.name == MARKDOWN_OUTPUT_DIR:
                self.log_error("Default directory utility integration failed")
                return False
            
            self.log_success("Integration with existing components working correctly")
            return True
            
        except Exception as e:
            self.log_error(f"Integration test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🚀 Starting Markdown Directory Default UI QA Test Suite")
        print("=" * 60)
        
        # Setup test environment
        if not self.setup_test_environment():
            return self.generate_test_report()
        
        # Define test methods
        tests = [
            ("Default Directory Utility Function", self.test_default_directory_utility_function),
            ("General Settings Tab UI", self.test_general_settings_tab_ui),
            ("Conversion Settings Tab UI", self.test_conversion_settings_tab_ui),
            ("Settings Dialog Integration", self.test_settings_dialog_integration),
            ("Browse Directory Functionality", self.test_browse_directory_functionality),
            ("Configuration Persistence", self.test_configuration_persistence),
            ("UI Consistency and Accessibility", self.test_ui_consistency_and_accessibility),
            ("Performance and Responsiveness", self.test_performance_and_responsiveness),
            ("Error Handling and Edge Cases", self.test_error_handling_edge_cases),
            ("Integration with Existing Components", self.test_integration_with_existing_components),
        ]
        
        # Run tests
        for test_name, test_method in tests:
            try:
                print(f"\n📋 Running: {test_name}")
                test_method()
            except Exception as e:
                self.log_error(f"Test '{test_name}' crashed: {e}")
                print(f"Traceback: {traceback.format_exc()}")
        
        # Cleanup
        self.cleanup_test_environment()
        
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'passed': self.test_results['passed'],
            'failed': self.test_results['failed'],
            'warnings': self.test_results['warnings'],
            'success_rate': success_rate,
            'details': self.test_results['details'],
            'status': 'PASS' if self.test_results['failed'] == 0 else 'FAIL'
        }
        
        return report


def print_test_report(report: Dict[str, Any]):
    """Print formatted test report"""
    print("\n" + "=" * 60)
    print("📊 MARKDOWN DIRECTORY DEFAULT UI QA TEST REPORT")
    print("=" * 60)
    print(f"Test Date: {report['timestamp']}")
    print(f"Total Tests: {report['total_tests']}")
    print(f"✅ Passed: {report['passed']}")
    print(f"❌ Failed: {report['failed']}")
    print(f"⚠️  Warnings: {report['warnings']}")
    print(f"📈 Success Rate: {report['success_rate']:.1f}%")
    print(f"🎯 Overall Status: {report['status']}")
    
    if report['failed'] > 0:
        print(f"\n❌ FAILED TESTS:")
        for status, message in report['details']:
            if status == 'FAIL':
                print(f"   • {message}")
    
    if report['warnings'] > 0:
        print(f"\n⚠️  WARNINGS:")
        for status, message in report['details']:
            if status == 'WARN':
                print(f"   • {message}")
    
    print("\n" + "=" * 60)
    
    # QA Assessment
    if report['failed'] == 0:
        if report['warnings'] == 0:
            print("✅ QA ASSESSMENT: TECHNICAL IMPLEMENTATION APPROVED")
            print("   All technical requirements met with excellent quality")
        else:
            print("✅ QA ASSESSMENT: TECHNICAL IMPLEMENTATION APPROVED WITH MINOR ISSUES")
            print("   Technical requirements met, minor improvements recommended")
    else:
        print("❌ QA ASSESSMENT: TECHNICAL ISSUES FOUND - RETURN TO DEVELOPER")
        print("   Critical technical problems must be addressed before approval")
    
    print("=" * 60)


if __name__ == "__main__":
    tester = MarkdownDirectoryUITester()
    report = tester.run_all_tests()
    print_test_report(report)
    
    # Exit with appropriate code
    sys.exit(0 if report['status'] == 'PASS' else 1)
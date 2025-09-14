"""
Unit tests for ConfigManager
"""

import pytest
from pathlib import Path
from PyQt6.QtCore import QSettings

from markitdown_gui.core.config_manager import ConfigManager
from markitdown_gui.core.exceptions import ConfigurationError, InvalidConfigError


class TestConfigManager:
    """Test suite for ConfigManager"""
    
    def test_initialization(self, config_manager):
        """Test ConfigManager initialization"""
        assert config_manager is not None
        assert config_manager.settings is not None
        assert config_manager.config_version >= "1.0.0"
    
    def test_default_values(self, config_manager):
        """Test default configuration values"""
        # General settings
        assert config_manager.get_value("General/language", "en_US") == "en_US"
        assert config_manager.get_value("General/theme", "system") == "system"
        
        # Conversion settings
        assert config_manager.get_value("Conversion/output_dir", "") != ""
        assert config_manager.get_value("Conversion/max_workers", 4) == 4
        assert config_manager.get_value("Conversion/include_subdirs", True) == True
        
        # LLM settings
        assert config_manager.get_value("LLM/provider", "openai") == "openai"
        assert config_manager.get_value("LLM/model", "gpt-4o") == "gpt-4o"
    
    def test_set_and_get_value(self, config_manager):
        """Test setting and getting configuration values"""
        # Set string value
        config_manager.set_value("Test/string_key", "test_value")
        assert config_manager.get_value("Test/string_key") == "test_value"
        
        # Set integer value
        config_manager.set_value("Test/int_key", 42)
        assert config_manager.get_value("Test/int_key", 0) == 42
        
        # Set boolean value
        config_manager.set_value("Test/bool_key", True)
        assert config_manager.get_value("Test/bool_key", False) == True
        
        # Set list value
        test_list = ["item1", "item2", "item3"]
        config_manager.set_value("Test/list_key", test_list)
        assert config_manager.get_value("Test/list_key", []) == test_list
    
    def test_value_validation(self, config_manager):
        """Test configuration value validation"""
        # Valid language code
        config_manager.set_value("General/language", "ko_KR")
        assert config_manager.get_value("General/language") == "ko_KR"
        
        # Valid theme
        config_manager.set_value("General/theme", "dark")
        assert config_manager.get_value("General/theme") == "dark"
        
        # Valid worker count
        config_manager.set_value("Conversion/max_workers", 8)
        assert config_manager.get_value("Conversion/max_workers") == 8
        
        # Invalid worker count should use default
        config_manager.set_value("Conversion/max_workers", -1)
        assert config_manager.get_value("Conversion/max_workers", 4) == 4
    
    def test_reset_to_default(self, config_manager):
        """Test resetting configuration to defaults"""
        # Change some values
        config_manager.set_value("General/language", "ko_KR")
        config_manager.set_value("Conversion/max_workers", 8)
        
        # Reset to defaults
        config_manager.reset_to_default()
        
        # Check values are reset
        assert config_manager.get_value("General/language") == "en_US"
        assert config_manager.get_value("Conversion/max_workers") == 4
    
    def test_export_and_import_settings(self, config_manager, temp_dir):
        """Test exporting and importing settings"""
        # Set custom values
        config_manager.set_value("Test/export_key", "export_value")
        config_manager.set_value("Test/export_number", 123)
        
        # Export settings
        export_file = temp_dir / "exported_settings.json"
        success = config_manager.export_settings(str(export_file))
        assert success == True
        assert export_file.exists()
        
        # Reset and verify values are gone
        config_manager.reset_to_default()
        assert config_manager.get_value("Test/export_key", "") == ""
        
        # Import settings back
        success = config_manager.import_settings(str(export_file))
        assert success == True
        
        # Verify imported values
        assert config_manager.get_value("Test/export_key") == "export_value"
        assert config_manager.get_value("Test/export_number") == 123
    
    def test_recent_directories(self, config_manager, temp_dir):
        """Test recent directories management"""
        # Initially empty
        assert config_manager.get_recent_directories() == []
        
        # Add directories
        dir1 = str(temp_dir / "dir1")
        dir2 = str(temp_dir / "dir2")
        dir3 = str(temp_dir / "dir3")
        
        config_manager.add_recent_directory(dir1)
        config_manager.add_recent_directory(dir2)
        config_manager.add_recent_directory(dir3)
        
        recent = config_manager.get_recent_directories()
        assert len(recent) == 3
        assert dir3 in recent  # Most recent first
        
        # Add duplicate - should move to top
        config_manager.add_recent_directory(dir1)
        recent = config_manager.get_recent_directories()
        assert recent[0] == dir1
        
        # Test max limit (10 directories)
        for i in range(15):
            config_manager.add_recent_directory(str(temp_dir / f"dir_{i}"))
        
        recent = config_manager.get_recent_directories()
        assert len(recent) <= 10
    
    def test_file_type_filters(self, config_manager):
        """Test file type filter configuration"""
        # Get default filters
        filters = config_manager.get_file_filters()
        assert len(filters) > 0
        assert any('.pdf' in f for f in filters)
        assert any('.docx' in f for f in filters)
        
        # Add custom filter
        custom_filters = filters + ['.custom']
        config_manager.set_value("Conversion/file_filters", custom_filters)
        
        new_filters = config_manager.get_file_filters()
        assert '.custom' in new_filters
    
    def test_configuration_migration(self, config_manager):
        """Test configuration version migration"""
        # Set old version
        config_manager.set_value("General/config_version", "0.9.0")
        
        # Trigger migration check
        config_manager.check_and_migrate_config()
        
        # Verify version updated
        version = config_manager.get_value("General/config_version", "")
        assert version >= "1.0.0"
    
    def test_thread_safety(self, config_manager):
        """Test thread-safe configuration access"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(index):
            try:
                for i in range(10):
                    key = f"Thread/key_{index}_{i}"
                    value = f"value_{index}_{i}"
                    config_manager.set_value(key, value)
                    retrieved = config_manager.get_value(key)
                    results.append(retrieved == value)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify no errors and all operations succeeded
        assert len(errors) == 0
        assert all(results)
    
    def test_cleanup(self, config_manager):
        """Test proper cleanup of resources"""
        # Set some values
        config_manager.set_value("Test/cleanup", "test")
        
        # Cleanup
        config_manager.cleanup()
        
        # Settings should still be accessible (cleanup doesn't delete)
        assert config_manager.settings is not None
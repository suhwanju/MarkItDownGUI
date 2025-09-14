# Configuration Management

## Overview

This guide covers comprehensive configuration management for the MarkItDown GUI application, including environment-specific settings, deployment configurations, and runtime configuration options.

## Configuration Architecture

### Configuration Layers
- **Default Configuration**: Built-in application defaults
- **System Configuration**: System-wide settings for all users
- **User Configuration**: User-specific preferences and settings
- **Environment Configuration**: Environment-specific overrides
- **Runtime Configuration**: Dynamic configuration changes

### Configuration Hierarchy
```
Runtime Configuration (highest priority)
    ↓
Environment Variables
    ↓
User Configuration Files
    ↓
System Configuration Files
    ↓
Default Application Settings (lowest priority)
```

## Configuration File Structure

### Main Configuration File
```yaml
# config/app.yaml - Main application configuration
application:
  name: "MarkItDown GUI"
  version: "1.0.0"
  debug: false
  log_level: "INFO"
  
  # Window settings
  window:
    width: 1200
    height: 800
    remember_size: true
    remember_position: true
    start_maximized: false
  
  # Default directories
  directories:
    output: "./markdown"
    temp: "./temp"
    plugins: "./plugins"
    logs: "./logs"
    cache: "./cache"

# File handling settings
file_handling:
  max_file_size_mb: 100
  supported_extensions:
    - ".docx"
    - ".pptx" 
    - ".xlsx"
    - ".pdf"
    - ".jpg"
    - ".jpeg"
    - ".png"
    - ".gif"
    - ".mp3"
    - ".wav"
    - ".html"
    - ".csv"
    - ".json"
    - ".xml"
    - ".txt"
    - ".zip"
    - ".epub"
  
  # File processing
  concurrent_conversions: 3
  timeout_seconds: 300
  retry_attempts: 2
  auto_retry_failed: true

# Conversion settings
conversion:
  # MarkItDown library settings
  markitdown:
    preserve_formatting: true
    extract_images: true
    include_metadata: true
    
  # Output settings
  output:
    format: "markdown"
    encoding: "utf-8"
    line_endings: "auto"  # auto, unix, windows
    
  # Quality settings
  quality:
    validate_output: true
    check_links: false
    optimize_images: true
    compress_images: false

# UI settings
ui:
  theme: "light"  # light, dark, high_contrast, auto
  language: "auto"  # auto, en, ko, es, fr, de
  
  # Accessibility
  accessibility:
    high_contrast: false
    large_text: false
    screen_reader_support: true
    keyboard_navigation: true
  
  # Layout
  layout:
    show_toolbar: true
    show_status_bar: true
    show_file_preview: true
    sidebar_width: 300

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # File logging
  file:
    enabled: true
    max_size_mb: 10
    backup_count: 5
    rotation: "time"  # size, time
  
  # Console logging
  console:
    enabled: true
    level: "WARNING"

# Performance settings
performance:
  # Memory management
  memory:
    max_usage_mb: 512
    cache_size_mb: 64
    gc_threshold: 100
  
  # Threading
  threading:
    worker_threads: 4
    io_threads: 2
    
  # Caching
  cache:
    enabled: true
    ttl_seconds: 3600
    max_entries: 1000

# Network settings
network:
  timeout_seconds: 30
  retry_attempts: 3
  proxy:
    enabled: false
    host: ""
    port: 8080
    username: ""
    password: ""
  
  # Update checking
  updates:
    check_enabled: true
    check_interval_hours: 24
    auto_download: false

# Security settings
security:
  # File access
  file_access:
    restrict_to_user_dirs: false
    allow_system_dirs: false
    scan_for_malware: false
  
  # Privacy
  privacy:
    collect_usage_stats: false
    crash_reporting: true
    share_error_logs: false

# Plugin settings
plugins:
  enabled: true
  auto_load: true
  development_mode: false
  
  # Plugin directories
  directories:
    - "./plugins"
    - "~/.markitdown-gui/plugins"
  
  # Plugin security
  security:
    verify_signatures: false
    allow_unsigned: true
    sandbox_plugins: false

# Advanced settings
advanced:
  # Experimental features
  experimental:
    async_ui: false
    gpu_acceleration: false
    neural_ocr: false
  
  # Debugging
  debug:
    verbose_logging: false
    save_temp_files: false
    profile_performance: false
    memory_profiling: false
```

### Environment-Specific Configurations

#### Development Configuration
```yaml
# config/environments/development.yaml
application:
  debug: true
  log_level: "DEBUG"

logging:
  level: "DEBUG"
  console:
    enabled: true
    level: "DEBUG"

advanced:
  debug:
    verbose_logging: true
    save_temp_files: true
    profile_performance: true

plugins:
  development_mode: true

# Development-specific paths
directories:
  output: "./dev-output"
  temp: "./dev-temp"
  logs: "./dev-logs"

# Relaxed security for development
security:
  file_access:
    restrict_to_user_dirs: false
  privacy:
    collect_usage_stats: false
    crash_reporting: false
```

#### Production Configuration
```yaml
# config/environments/production.yaml
application:
  debug: false
  log_level: "WARNING"

logging:
  level: "WARNING"
  console:
    enabled: false
  file:
    enabled: true
    max_size_mb: 50
    backup_count: 10

# Enhanced security for production
security:
  file_access:
    restrict_to_user_dirs: true
    allow_system_dirs: false
    scan_for_malware: true
  privacy:
    collect_usage_stats: true
    crash_reporting: true

# Conservative performance settings
performance:
  memory:
    max_usage_mb: 256
  threading:
    worker_threads: 2

# Disable experimental features
advanced:
  experimental:
    async_ui: false
    gpu_acceleration: false
    neural_ocr: false
  debug:
    verbose_logging: false
    save_temp_files: false
    profile_performance: false
```

#### Testing Configuration
```yaml
# config/environments/testing.yaml
application:
  debug: true
  log_level: "ERROR"  # Reduce noise in tests

# Use temporary directories for testing
directories:
  output: "/tmp/markitdown-test/output"
  temp: "/tmp/markitdown-test/temp"
  logs: "/tmp/markitdown-test/logs"

# Fast settings for tests
file_handling:
  concurrent_conversions: 1
  timeout_seconds: 10
  retry_attempts: 1

# Minimal UI for headless testing
ui:
  theme: "light"
  layout:
    show_toolbar: false
    show_status_bar: false
    show_file_preview: false

# Disable external connections
network:
  timeout_seconds: 5
  updates:
    check_enabled: false

# No plugins in testing
plugins:
  enabled: false
  auto_load: false
```

## Configuration Management Implementation

### Configuration Manager Class
```python
# markitdown_gui/core/config_manager.py
import os
import yaml
import json
from typing import Any, Dict, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

@dataclass
class ConfigPaths:
    """Configuration file paths"""
    app_config: str = "config/app.yaml"
    user_config: str = "~/.markitdown-gui/config.yaml"
    system_config: str = "/etc/markitdown-gui/config.yaml"
    env_config: str = None
    
    def __post_init__(self):
        # Expand user paths
        self.user_config = os.path.expanduser(self.user_config)
        
        # Set environment-specific config
        env = os.getenv('MARKITDOWN_ENV', 'production')
        self.env_config = f"config/environments/{env}.yaml"

class ConfigManager:
    """Manages application configuration from multiple sources"""
    
    def __init__(self, config_paths: Optional[ConfigPaths] = None):
        self.config_paths = config_paths or ConfigPaths()
        self.config: Dict[str, Any] = {}
        self.watchers: List[callable] = []
        self.logger = logging.getLogger(__name__)
        
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from all sources in priority order"""
        # Start with default configuration
        self.config = self._get_default_config()
        
        # Load configuration files in order (lower priority first)
        config_files = [
            self.config_paths.app_config,
            self.config_paths.system_config,
            self.config_paths.env_config,
            self.config_paths.user_config
        ]
        
        for config_file in config_files:
            if config_file and os.path.exists(config_file):
                try:
                    file_config = self._load_config_file(config_file)
                    self.config = self._deep_merge(self.config, file_config)
                    self.logger.info(f"Loaded configuration from {config_file}")
                except Exception as e:
                    self.logger.error(f"Error loading config file {config_file}: {e}")
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        # Validate configuration
        self._validate_config()
        
        # Notify watchers
        self._notify_watchers()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default application configuration"""
        return {
            'application': {
                'name': 'MarkItDown GUI',
                'version': '1.0.0',
                'debug': False,
                'log_level': 'INFO'
            },
            'file_handling': {
                'max_file_size_mb': 100,
                'concurrent_conversions': 3,
                'timeout_seconds': 300
            },
            'ui': {
                'theme': 'light',
                'language': 'auto'
            },
            'logging': {
                'level': 'INFO',
                'file': {'enabled': True},
                'console': {'enabled': True}
            }
        }
    
    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return yaml.safe_load(f) or {}
            elif file_path.endswith('.json'):
                return json.load(f) or {}
            else:
                raise ValueError(f"Unsupported config file format: {file_path}")
    
    def _deep_merge(self, base: Dict, overlay: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        # Map environment variables to config paths
        env_mappings = {
            'MARKITDOWN_DEBUG': 'application.debug',
            'MARKITDOWN_LOG_LEVEL': 'logging.level',
            'MARKITDOWN_OUTPUT_DIR': 'directories.output',
            'MARKITDOWN_TEMP_DIR': 'directories.temp',
            'MARKITDOWN_MAX_FILE_SIZE': 'file_handling.max_file_size_mb',
            'MARKITDOWN_CONCURRENT_CONVERSIONS': 'file_handling.concurrent_conversions',
            'MARKITDOWN_THEME': 'ui.theme',
            'MARKITDOWN_LANGUAGE': 'ui.language',
            'MARKITDOWN_PROXY_HOST': 'network.proxy.host',
            'MARKITDOWN_PROXY_PORT': 'network.proxy.port'
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_config_value(config_path, self._convert_env_value(env_value))
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Try boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_config_value(self, path: str, value: Any):
        """Set configuration value using dot notation path"""
        keys = path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate required sections
        required_sections = ['application', 'file_handling', 'ui', 'logging']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Required configuration section missing: {section}")
        
        # Validate specific values
        max_file_size = self.get('file_handling.max_file_size_mb', 100)
        if max_file_size <= 0 or max_file_size > 1000:
            raise ValueError(f"Invalid max_file_size_mb: {max_file_size}")
        
        concurrent_conversions = self.get('file_handling.concurrent_conversions', 3)
        if concurrent_conversions <= 0 or concurrent_conversions > 10:
            raise ValueError(f"Invalid concurrent_conversions: {concurrent_conversions}")
        
        # Validate directories exist or can be created
        directories = self.get('directories', {})
        for dir_type, dir_path in directories.items():
            if dir_path:
                try:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.logger.warning(f"Cannot create directory {dir_type}: {dir_path} - {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        current = self.config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, persist: bool = False):
        """Set configuration value using dot notation"""
        self._set_config_value(key, value)
        
        if persist:
            self.save_user_config()
        
        self._notify_watchers()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any], persist: bool = False):
        """Update configuration section"""
        current_section = self.get_section(section)
        updated_section = self._deep_merge(current_section, values)
        self.set(section, updated_section, persist)
    
    def save_user_config(self):
        """Save current configuration to user config file"""
        user_config_dir = os.path.dirname(self.config_paths.user_config)
        os.makedirs(user_config_dir, exist_ok=True)
        
        with open(self.config_paths.user_config, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Saved user configuration to {self.config_paths.user_config}")
    
    def reload(self):
        """Reload configuration from all sources"""
        self.load_configuration()
    
    def add_watcher(self, callback: callable):
        """Add configuration change watcher"""
        self.watchers.append(callback)
    
    def remove_watcher(self, callback: callable):
        """Remove configuration change watcher"""
        if callback in self.watchers:
            self.watchers.remove(callback)
    
    def _notify_watchers(self):
        """Notify all watchers of configuration changes"""
        for callback in self.watchers:
            try:
                callback(self.config)
            except Exception as e:
                self.logger.error(f"Error in config watcher: {e}")
    
    def export_config(self, file_path: str, format: str = 'yaml'):
        """Export current configuration to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == 'yaml':
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
    
    def import_config(self, file_path: str, merge: bool = True):
        """Import configuration from file"""
        imported_config = self._load_config_file(file_path)
        
        if merge:
            self.config = self._deep_merge(self.config, imported_config)
        else:
            self.config = imported_config
        
        self._validate_config()
        self._notify_watchers()

# Global configuration manager instance
config_manager = ConfigManager()
```

### Environment Variable Configuration

#### Development Environment Variables
```bash
# .env.development
MARKITDOWN_ENV=development
MARKITDOWN_DEBUG=true
MARKITDOWN_LOG_LEVEL=DEBUG
MARKITDOWN_OUTPUT_DIR=./dev-output
MARKITDOWN_TEMP_DIR=./dev-temp
MARKITDOWN_CONCURRENT_CONVERSIONS=1
```

#### Production Environment Variables
```bash
# .env.production
MARKITDOWN_ENV=production
MARKITDOWN_DEBUG=false
MARKITDOWN_LOG_LEVEL=WARNING
MARKITDOWN_OUTPUT_DIR=/var/lib/markitdown-gui/output
MARKITDOWN_TEMP_DIR=/tmp/markitdown-gui
MARKITDOWN_CONCURRENT_CONVERSIONS=4
MARKITDOWN_MAX_FILE_SIZE=50
```

#### Docker Environment Variables
```bash
# Docker environment variables
MARKITDOWN_ENV=docker
MARKITDOWN_OUTPUT_DIR=/app/output
MARKITDOWN_TEMP_DIR=/tmp
MARKITDOWN_CONFIG_FILE=/app/config/docker.yaml
MARKITDOWN_PROXY_HOST=proxy.company.com
MARKITDOWN_PROXY_PORT=8080
```

## Configuration Validation

### Configuration Schema
```python
# markitdown_gui/core/config_schema.py
from typing import Dict, Any, List
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "application": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
                "debug": {"type": "boolean"},
                "log_level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                }
            },
            "required": ["name", "version"]
        },
        "file_handling": {
            "type": "object",
            "properties": {
                "max_file_size_mb": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000
                },
                "concurrent_conversions": {
                    "type": "integer", 
                    "minimum": 1,
                    "maximum": 10
                },
                "timeout_seconds": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 3600
                },
                "supported_extensions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },
        "ui": {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "enum": ["light", "dark", "high_contrast", "auto"]
                },
                "language": {
                    "type": "string",
                    "pattern": "^(auto|en|ko|es|fr|de|ja|zh-CN|zh-TW)$"
                }
            }
        },
        "logging": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                },
                "file": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "max_size_mb": {"type": "integer", "minimum": 1}
                    }
                }
            }
        }
    },
    "required": ["application", "file_handling", "ui", "logging"]
}

def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate configuration against schema"""
    try:
        jsonschema.validate(config, CONFIG_SCHEMA)
        return []
    except jsonschema.ValidationError as e:
        return [str(e)]
    except Exception as e:
        return [f"Validation error: {e}"]
```

## Runtime Configuration

### Dynamic Configuration Updates
```python
# markitdown_gui/ui/settings_dialog.py
from PyQt6.QtWidgets import QDialog, QTabWidget, QVBoxLayout
from ..core.config_manager import config_manager

class SettingsDialog(QDialog):
    """Settings dialog with live configuration updates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setup_ui()
        self.load_current_settings()
        
        # Watch for configuration changes
        config_manager.add_watcher(self.on_config_changed)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.tab_widget = QTabWidget()
        
        # Add setting tabs
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_conversion_tab(), "Conversion")
        self.tab_widget.addTab(self.create_ui_tab(), "Interface")
        self.tab_widget.addTab(self.create_advanced_tab(), "Advanced")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def on_setting_changed(self, setting_path: str, value: Any):
        """Handle setting changes with validation"""
        try:
            # Update configuration
            config_manager.set(setting_path, value, persist=True)
            
            # Apply immediate changes
            self.apply_setting_change(setting_path, value)
            
        except Exception as e:
            # Show error dialog
            self.show_error(f"Failed to update setting: {e}")
    
    def apply_setting_change(self, setting_path: str, value: Any):
        """Apply setting changes immediately"""
        if setting_path == 'ui.theme':
            self.parent().apply_theme(value)
        elif setting_path == 'ui.language':
            self.parent().change_language(value)
        elif setting_path.startswith('logging'):
            self.parent().update_logging_config()
        # Add more immediate updates as needed
    
    def on_config_changed(self, config: Dict[str, Any]):
        """Handle external configuration changes"""
        # Update UI to reflect new configuration
        self.load_current_settings()
```

### Configuration Profiles
```python
# markitdown_gui/core/config_profiles.py
from typing import Dict, Any, List
import os
import yaml

class ConfigProfile:
    """Represents a named configuration profile"""
    
    def __init__(self, name: str, config: Dict[str, Any], description: str = ""):
        self.name = name
        self.config = config
        self.description = description
    
    def apply_to_manager(self, config_manager):
        """Apply this profile to configuration manager"""
        config_manager.config = config_manager._deep_merge(
            config_manager._get_default_config(),
            self.config
        )
        config_manager._validate_config()
        config_manager._notify_watchers()

class ProfileManager:
    """Manages configuration profiles"""
    
    def __init__(self, profiles_dir: str = "config/profiles"):
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, ConfigProfile] = {}
        self.load_profiles()
    
    def load_profiles(self):
        """Load all profiles from profiles directory"""
        if not os.path.exists(self.profiles_dir):
            self.create_default_profiles()
            return
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(('.yaml', '.yml')):
                profile_path = os.path.join(self.profiles_dir, filename)
                try:
                    with open(profile_path, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    profile = ConfigProfile(
                        name=data.get('name', filename[:-5]),
                        config=data.get('config', {}),
                        description=data.get('description', '')
                    )
                    self.profiles[profile.name] = profile
                    
                except Exception as e:
                    print(f"Error loading profile {filename}: {e}")
    
    def create_default_profiles(self):
        """Create default configuration profiles"""
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Performance profile
        performance_profile = {
            'name': 'Performance',
            'description': 'Optimized for maximum performance',
            'config': {
                'file_handling': {
                    'concurrent_conversions': 8,
                    'timeout_seconds': 600
                },
                'performance': {
                    'memory': {'max_usage_mb': 1024},
                    'threading': {'worker_threads': 8}
                },
                'ui': {
                    'layout': {'show_file_preview': False}
                }
            }
        }
        
        # Conservative profile
        conservative_profile = {
            'name': 'Conservative',
            'description': 'Safe settings for stability',
            'config': {
                'file_handling': {
                    'concurrent_conversions': 1,
                    'timeout_seconds': 120,
                    'max_file_size_mb': 25
                },
                'performance': {
                    'memory': {'max_usage_mb': 256},
                    'threading': {'worker_threads': 2}
                }
            }
        }
        
        # Save profiles
        for profile in [performance_profile, conservative_profile]:
            profile_path = os.path.join(self.profiles_dir, f"{profile['name'].lower()}.yaml")
            with open(profile_path, 'w') as f:
                yaml.dump(profile, f, default_flow_style=False, indent=2)
    
    def get_profile(self, name: str) -> Optional[ConfigProfile]:
        """Get profile by name"""
        return self.profiles.get(name)
    
    def apply_profile(self, name: str, config_manager) -> bool:
        """Apply profile to configuration manager"""
        profile = self.get_profile(name)
        if profile:
            profile.apply_to_manager(config_manager)
            return True
        return False
    
    def save_current_as_profile(self, name: str, description: str, config_manager):
        """Save current configuration as new profile"""
        profile = ConfigProfile(name, config_manager.config.copy(), description)
        self.profiles[name] = profile
        
        # Save to file
        profile_path = os.path.join(self.profiles_dir, f"{name.lower().replace(' ', '_')}.yaml")
        profile_data = {
            'name': name,
            'description': description,
            'config': profile.config
        }
        
        with open(profile_path, 'w') as f:
            yaml.dump(profile_data, f, default_flow_style=False, indent=2)
```

## Configuration Migration

### Version Migration System
```python
# markitdown_gui/core/config_migration.py
from typing import Dict, Any, List, Callable
import logging

class ConfigMigration:
    """Handles configuration migration between versions"""
    
    def __init__(self):
        self.migrations: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self.register_migrations()
    
    def register_migration(self, from_version: str, to_version: str, 
                          migration_func: Callable):
        """Register a migration function"""
        key = f"{from_version}->{to_version}"
        self.migrations[key] = migration_func
    
    def register_migrations(self):
        """Register all known migrations"""
        self.register_migration("0.9.0", "1.0.0", self.migrate_0_9_to_1_0)
        self.register_migration("1.0.0", "1.1.0", self.migrate_1_0_to_1_1)
    
    def migrate_config(self, config: Dict[str, Any], 
                      from_version: str, to_version: str) -> Dict[str, Any]:
        """Migrate configuration from one version to another"""
        current_version = from_version
        migrated_config = config.copy()
        
        # Find migration path
        migration_path = self.find_migration_path(from_version, to_version)
        
        for migration_key in migration_path:
            if migration_key in self.migrations:
                try:
                    migrated_config = self.migrations[migration_key](migrated_config)
                    self.logger.info(f"Applied migration: {migration_key}")
                except Exception as e:
                    self.logger.error(f"Migration {migration_key} failed: {e}")
                    raise
        
        return migrated_config
    
    def find_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """Find migration path between versions"""
        # Simple implementation - in practice, this could be more sophisticated
        # to handle complex version graphs
        if from_version == "0.9.0" and to_version == "1.0.0":
            return ["0.9.0->1.0.0"]
        elif from_version == "1.0.0" and to_version == "1.1.0":
            return ["1.0.0->1.1.0"]
        elif from_version == "0.9.0" and to_version == "1.1.0":
            return ["0.9.0->1.0.0", "1.0.0->1.1.0"]
        else:
            return []
    
    def migrate_0_9_to_1_0(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.9.0 to 1.0.0"""
        migrated = config.copy()
        
        # Rename 'processing' section to 'file_handling'
        if 'processing' in migrated:
            migrated['file_handling'] = migrated.pop('processing')
        
        # Move theme setting from 'appearance' to 'ui'
        if 'appearance' in migrated:
            if 'ui' not in migrated:
                migrated['ui'] = {}
            migrated['ui']['theme'] = migrated['appearance'].get('theme', 'light')
            del migrated['appearance']
        
        # Update log level values
        if 'logging' in migrated and 'level' in migrated['logging']:
            old_level = migrated['logging']['level']
            level_mapping = {
                'debug': 'DEBUG',
                'info': 'INFO', 
                'warning': 'WARNING',
                'error': 'ERROR'
            }
            migrated['logging']['level'] = level_mapping.get(old_level, 'INFO')
        
        return migrated
    
    def migrate_1_0_to_1_1(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.0.0 to 1.1.0"""
        migrated = config.copy()
        
        # Add new performance section
        if 'performance' not in migrated:
            migrated['performance'] = {
                'memory': {'max_usage_mb': 512},
                'threading': {'worker_threads': 4},
                'cache': {'enabled': True, 'ttl_seconds': 3600}
            }
        
        # Add new plugin settings
        if 'plugins' not in migrated:
            migrated['plugins'] = {
                'enabled': True,
                'auto_load': True,
                'development_mode': False
            }
        
        return migrated
```

## Configuration Security

### Sensitive Configuration Handling
```python
# markitdown_gui/core/config_security.py
import os
import base64
from cryptography.fernet import Fernet
from typing import Dict, Any

class SecureConfigManager:
    """Handles encryption/decryption of sensitive configuration values"""
    
    def __init__(self):
        self.cipher_suite = self._get_or_create_cipher()
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption cipher"""
        key_file = os.path.expanduser("~/.markitdown-gui/.config_key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            # Save key with restricted permissions
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Read/write for owner only
        
        return Fernet(key)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a configuration value"""
        encrypted = self.cipher_suite.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a configuration value"""
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def encrypt_sensitive_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive values in configuration"""
        sensitive_paths = [
            'network.proxy.password',
            'database.password',
            'api_keys.openai',
            'api_keys.azure'
        ]
        
        encrypted_config = config.copy()
        
        for path in sensitive_paths:
            value = self._get_nested_value(encrypted_config, path)
            if value and isinstance(value, str):
                encrypted_value = self.encrypt_value(value)
                self._set_nested_value(encrypted_config, path, f"encrypted:{encrypted_value}")
        
        return encrypted_config
    
    def decrypt_sensitive_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive values in configuration"""
        decrypted_config = config.copy()
        
        self._decrypt_nested_values(decrypted_config)
        
        return decrypted_config
    
    def _decrypt_nested_values(self, obj: Any):
        """Recursively decrypt encrypted values"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith("encrypted:"):
                    try:
                        encrypted_value = value[10:]  # Remove "encrypted:" prefix
                        obj[key] = self.decrypt_value(encrypted_value)
                    except Exception:
                        # If decryption fails, leave the original value
                        pass
                else:
                    self._decrypt_nested_values(value)
        elif isinstance(obj, list):
            for item in obj:
                self._decrypt_nested_values(item)
    
    def _get_nested_value(self, obj: Dict, path: str) -> Any:
        """Get nested value using dot notation"""
        keys = path.split('.')
        current = obj
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def _set_nested_value(self, obj: Dict, path: str, value: Any):
        """Set nested value using dot notation"""
        keys = path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
```

## Related Documentation

- 🚀 [Deployment Guide](deployment.md) - Production deployment
- 📊 [Performance Tuning](performance.md) - Optimization guidelines
- 🔒 [Security Guidelines](security.md) - Security best practices
- 📋 [Monitoring](monitoring.md) - System monitoring and alerts

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
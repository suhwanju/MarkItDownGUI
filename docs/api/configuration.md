# Configuration API Reference

Complete API reference for MarkItDown GUI configuration management and settings.

## Table of Contents

- [Overview](#overview)
- [Configuration Schema](#configuration-schema)
- [ConfigManager API](#configmanager-api)
- [Settings Categories](#settings-categories)
- [Validation and Defaults](#validation-and-defaults)
- [Environment Variables](#environment-variables)
- [Migration and Versioning](#migration-and-versioning)

## Overview

The Configuration API provides centralized management of application settings, user preferences, and runtime configuration. All configuration is type-safe, validated, and supports both programmatic and file-based management.

### Key Features
- **Type-safe configuration** with full validation
- **Hierarchical settings** with inheritance and overrides
- **Environment variable support** for deployment flexibility
- **Hot reload capability** for runtime configuration changes
- **Version migration** for backward compatibility
- **Secure handling** of sensitive configuration data

## Configuration Schema

### Core Configuration Structure
```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from pathlib import Path

@dataclass
class UIConfig:
    """User interface configuration."""
    theme: str = 'auto'                    # 'light', 'dark', 'auto'
    language: str = 'en'                   # ISO language code
    font_family: str = 'system'            # Font family name
    font_size: int = 10                    # Base font size
    window_geometry: Optional[Dict[str, int]] = None
    window_state: Optional[bytes] = None
    show_splash: bool = True
    check_updates: bool = True
    remember_files: bool = True
    max_recent_files: int = 10

@dataclass
class ConversionConfig:
    """Document conversion configuration."""
    default_output_format: str = 'markdown'
    output_directory: Optional[str] = None
    filename_template: str = '{stem}.{ext}'
    preserve_metadata: bool = True
    preserve_formatting: bool = True
    enable_ocr: bool = True
    ocr_language: str = 'eng'
    ocr_confidence_threshold: float = 0.7
    batch_size: int = 10
    parallel_processing: bool = True
    worker_threads: int = 4
    timeout_seconds: int = 300

@dataclass
class PerformanceConfig:
    """Performance and resource configuration."""
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    memory_limit: int = 1024 * 1024 * 1024   # 1GB
    cache_enabled: bool = True
    cache_size: int = 100
    cache_ttl: int = 3600                     # 1 hour
    temp_cleanup: bool = True
    preview_max_size: int = 1024 * 1024       # 1MB
    background_processing: bool = True

@dataclass
class SecurityConfig:
    """Security and privacy configuration."""
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
        '.xlsx', '.xls', '.txt', '.html', '.htm',
        '.md', '.rtf', '.odt', '.odp', '.ods'
    ])
    scan_files: bool = True
    quarantine_suspicious: bool = True
    log_file_access: bool = False
    privacy_mode: bool = False
    telemetry_enabled: bool = False

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = 'INFO'                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
    file_logging: bool = True
    console_logging: bool = True
    log_file: Optional[str] = None
    max_log_size: int = 10 * 1024 * 1024   # 10MB
    backup_count: int = 5
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'

@dataclass
class Config:
    """Main application configuration."""
    version: str = '1.0.0'
    ui: UIConfig = field(default_factory=UIConfig)
    conversion: ConversionConfig = field(default_factory=ConversionConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Custom settings for plugins and extensions
    custom: Dict[str, Any] = field(default_factory=dict)
```

## ConfigManager API

### Primary Interface
```python
class ConfigManager:
    """Central configuration management system.
    
    Handles loading, saving, validation, and runtime management of
    application configuration from multiple sources with proper
    precedence and validation.
    """
    
    def __init__(self, 
                 config_dir: Optional[Path] = None,
                 config_file: Optional[str] = None,
                 auto_save: bool = True) -> None:
        """Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory
            config_file: Custom configuration filename
            auto_save: Automatically save changes
        """
        self._config_dir = config_dir or self._get_default_config_dir()
        self._config_file = config_file or 'config.yaml'
        self._auto_save = auto_save
        self._config: Optional[Config] = None
        self._watchers: List[Callable[[Config], None]] = []
    
    def load_config(self, reload: bool = False) -> Config:
        """Load configuration from all sources.
        
        Configuration is loaded with the following precedence:
        1. Command line arguments (highest priority)
        2. Environment variables
        3. User configuration file
        4. System configuration file
        5. Default values (lowest priority)
        
        Args:
            reload: Force reload even if already loaded
            
        Returns:
            Loaded and validated configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
            FileNotFoundError: If required config file missing
        """
        if self._config and not reload:
            return self._config
        
        # Load from multiple sources
        config_data = self._load_default_config()
        config_data = self._merge_config(config_data, self._load_system_config())
        config_data = self._merge_config(config_data, self._load_user_config())
        config_data = self._merge_config(config_data, self._load_env_config())
        config_data = self._merge_config(config_data, self._load_cli_config())
        
        # Create and validate configuration object
        try:
            self._config = Config(**config_data)
            self._validate_config(self._config)
        except (TypeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration: {e}")
        
        # Setup file watching for hot reload
        if reload:
            self._setup_file_watching()
        
        return self._config
    
    def save_config(self, config: Optional[Config] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save (None = current config)
            
        Raises:
            ConfigurationError: If config cannot be saved
        """
        if config is None:
            config = self.get_config()
        
        config_path = self._config_dir / self._config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable dictionary
        config_dict = self._config_to_dict(config)
        
        # Save with backup
        self._save_with_backup(config_path, config_dict)
        
        # Notify watchers
        self._notify_watchers(config)
    
    def get_config(self) -> Config:
        """Get current configuration.
        
        Returns:
            Current configuration object
            
        Raises:
            RuntimeError: If configuration not loaded
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values.
        
        Supports nested updates using dot notation:
        update_config(ui__theme='dark', conversion__output_format='html')
        
        Args:
            **kwargs: Configuration updates with nested key support
        """
        config = self.get_config()
        
        for key, value in kwargs.items():
            self._set_nested_value(config, key, value)
        
        # Validate updated configuration
        self._validate_config(config)
        
        # Auto-save if enabled
        if self._auto_save:
            self.save_config(config)
        
        # Notify watchers
        self._notify_watchers(config)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Supports nested keys using dot notation: 'ui.theme', 'conversion.output_format'
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        config = self.get_config()
        return self._get_nested_value(config, key, default)
    
    def set_value(self, key: str, value: Any) -> None:
        """Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        self.update_config(**{key.replace('.', '__'): value})
    
    def watch_config(self, callback: Callable[[Config], None]) -> None:
        """Watch for configuration changes.
        
        Args:
            callback: Function called when config changes
        """
        self._watchers.append(callback)
    
    def unwatch_config(self, callback: Callable[[Config], None]) -> None:
        """Stop watching configuration changes.
        
        Args:
            callback: Function to remove from watchers
        """
        try:
            self._watchers.remove(callback)
        except ValueError:
            pass
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = Config()
        
        if self._auto_save:
            self.save_config()
        
        self._notify_watchers(self._config)
    
    def export_config(self, file_path: Path, format_type: str = 'yaml') -> None:
        """Export configuration to file.
        
        Args:
            file_path: Export file path
            format_type: Export format ('yaml', 'json', 'toml')
        """
        config = self.get_config()
        config_dict = self._config_to_dict(config)
        
        if format_type.lower() == 'yaml':
            import yaml
            with open(file_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        elif format_type.lower() == 'json':
            import json
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        elif format_type.lower() == 'toml':
            import toml
            with open(file_path, 'w') as f:
                toml.dump(config_dict, f)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def import_config(self, file_path: Path, merge: bool = True) -> None:
        """Import configuration from file.
        
        Args:
            file_path: Import file path
            merge: Whether to merge with existing config
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        # Determine format from extension
        format_type = file_path.suffix.lower()[1:]  # Remove dot
        
        if format_type == 'yaml' or format_type == 'yml':
            import yaml
            with open(file_path) as f:
                config_dict = yaml.safe_load(f)
        elif format_type == 'json':
            import json
            with open(file_path) as f:
                config_dict = json.load(f)
        elif format_type == 'toml':
            import toml
            with open(file_path) as f:
                config_dict = toml.load(f)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if merge and self._config:
            # Merge with existing config
            current_dict = self._config_to_dict(self._config)
            config_dict = self._merge_config(current_dict, config_dict)
        
        # Create new config object
        self._config = Config(**config_dict)
        self._validate_config(self._config)
        
        if self._auto_save:
            self.save_config()
        
        self._notify_watchers(self._config)
```

### Configuration Validation
```python
class ConfigValidator:
    """Validates configuration values and structure."""
    
    @staticmethod
    def validate_config(config: Config) -> List[str]:
        """Validate entire configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate UI config
        errors.extend(ConfigValidator._validate_ui_config(config.ui))
        
        # Validate conversion config
        errors.extend(ConfigValidator._validate_conversion_config(config.conversion))
        
        # Validate performance config
        errors.extend(ConfigValidator._validate_performance_config(config.performance))
        
        # Validate security config
        errors.extend(ConfigValidator._validate_security_config(config.security))
        
        # Validate logging config
        errors.extend(ConfigValidator._validate_logging_config(config.logging))
        
        return errors
    
    @staticmethod
    def _validate_ui_config(ui: UIConfig) -> List[str]:
        """Validate UI configuration."""
        errors = []
        
        # Validate theme
        valid_themes = ['light', 'dark', 'auto']
        if ui.theme not in valid_themes:
            errors.append(f"Invalid theme '{ui.theme}'. Must be one of: {valid_themes}")
        
        # Validate language
        if not ui.language or len(ui.language) != 2:
            errors.append(f"Invalid language code '{ui.language}'. Must be 2-character ISO code.")
        
        # Validate font size
        if ui.font_size < 6 or ui.font_size > 72:
            errors.append(f"Font size {ui.font_size} out of range. Must be 6-72.")
        
        # Validate max recent files
        if ui.max_recent_files < 0 or ui.max_recent_files > 100:
            errors.append(f"Max recent files {ui.max_recent_files} out of range. Must be 0-100.")
        
        return errors
    
    @staticmethod
    def _validate_conversion_config(conversion: ConversionConfig) -> List[str]:
        """Validate conversion configuration."""
        errors = []
        
        # Validate output format
        valid_formats = ['markdown', 'html', 'text', 'json']
        if conversion.default_output_format not in valid_formats:
            errors.append(f"Invalid output format '{conversion.default_output_format}'.")
        
        # Validate OCR confidence threshold
        if not 0.0 <= conversion.ocr_confidence_threshold <= 1.0:
            errors.append(f"OCR confidence threshold must be 0.0-1.0")
        
        # Validate batch size
        if conversion.batch_size < 1 or conversion.batch_size > 1000:
            errors.append(f"Batch size must be 1-1000")
        
        # Validate worker threads
        if conversion.worker_threads < 1 or conversion.worker_threads > 32:
            errors.append(f"Worker threads must be 1-32")
        
        # Validate timeout
        if conversion.timeout_seconds < 10 or conversion.timeout_seconds > 3600:
            errors.append(f"Timeout must be 10-3600 seconds")
        
        return errors
    
    @staticmethod
    def _validate_performance_config(performance: PerformanceConfig) -> List[str]:
        """Validate performance configuration."""
        errors = []
        
        # Validate file size limits
        if performance.max_file_size < 1024:  # 1KB minimum
            errors.append("Max file size must be at least 1KB")
        
        if performance.memory_limit < 64 * 1024 * 1024:  # 64MB minimum
            errors.append("Memory limit must be at least 64MB")
        
        # Validate cache settings
        if performance.cache_size < 0 or performance.cache_size > 10000:
            errors.append("Cache size must be 0-10000")
        
        if performance.cache_ttl < 0 or performance.cache_ttl > 86400:  # 1 day max
            errors.append("Cache TTL must be 0-86400 seconds")
        
        return errors
```

## Settings Categories

### UI Settings
```python
class UISettings:
    """User interface settings management."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def get_theme(self) -> str:
        """Get current theme setting."""
        return self.config_manager.get_value('ui.theme', 'auto')
    
    def set_theme(self, theme: str) -> None:
        """Set theme setting.
        
        Args:
            theme: Theme name ('light', 'dark', 'auto')
        """
        valid_themes = ['light', 'dark', 'auto']
        if theme not in valid_themes:
            raise ValueError(f"Invalid theme. Must be one of: {valid_themes}")
        
        self.config_manager.set_value('ui.theme', theme)
    
    def get_language(self) -> str:
        """Get current language setting."""
        return self.config_manager.get_value('ui.language', 'en')
    
    def set_language(self, language: str) -> None:
        """Set language setting.
        
        Args:
            language: ISO language code
        """
        # Validate language code
        if not language or len(language) != 2:
            raise ValueError("Language must be 2-character ISO code")
        
        self.config_manager.set_value('ui.language', language)
    
    def get_font_settings(self) -> Dict[str, Any]:
        """Get font settings."""
        return {
            'family': self.config_manager.get_value('ui.font_family', 'system'),
            'size': self.config_manager.get_value('ui.font_size', 10)
        }
    
    def set_font_settings(self, family: str = None, size: int = None) -> None:
        """Set font settings.
        
        Args:
            family: Font family name
            size: Font size (6-72)
        """
        if family:
            self.config_manager.set_value('ui.font_family', family)
        
        if size:
            if not 6 <= size <= 72:
                raise ValueError("Font size must be 6-72")
            self.config_manager.set_value('ui.font_size', size)
    
    def get_window_settings(self) -> Dict[str, Any]:
        """Get window settings."""
        return {
            'geometry': self.config_manager.get_value('ui.window_geometry'),
            'state': self.config_manager.get_value('ui.window_state')
        }
    
    def set_window_settings(self, geometry: Dict[str, int] = None, 
                           state: bytes = None) -> None:
        """Set window settings.
        
        Args:
            geometry: Window geometry dictionary
            state: Window state bytes
        """
        if geometry:
            self.config_manager.set_value('ui.window_geometry', geometry)
        
        if state:
            self.config_manager.set_value('ui.window_state', state)
```

### Conversion Settings
```python
class ConversionSettings:
    """Conversion settings management."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get output settings."""
        return {
            'format': self.config_manager.get_value('conversion.default_output_format', 'markdown'),
            'directory': self.config_manager.get_value('conversion.output_directory'),
            'template': self.config_manager.get_value('conversion.filename_template', '{stem}.{ext}')
        }
    
    def set_output_format(self, format_type: str) -> None:
        """Set default output format.
        
        Args:
            format_type: Output format ('markdown', 'html', 'text', 'json')
        """
        valid_formats = ['markdown', 'html', 'text', 'json']
        if format_type not in valid_formats:
            raise ValueError(f"Invalid format. Must be one of: {valid_formats}")
        
        self.config_manager.set_value('conversion.default_output_format', format_type)
    
    def set_output_directory(self, directory: Optional[str]) -> None:
        """Set output directory.
        
        Args:
            directory: Output directory path (None = same as input)
        """
        self.config_manager.set_value('conversion.output_directory', directory)
    
    def get_ocr_settings(self) -> Dict[str, Any]:
        """Get OCR settings."""
        return {
            'enabled': self.config_manager.get_value('conversion.enable_ocr', True),
            'language': self.config_manager.get_value('conversion.ocr_language', 'eng'),
            'confidence_threshold': self.config_manager.get_value('conversion.ocr_confidence_threshold', 0.7)
        }
    
    def set_ocr_settings(self, enabled: bool = None, language: str = None, 
                        confidence_threshold: float = None) -> None:
        """Set OCR settings.
        
        Args:
            enabled: Whether OCR is enabled
            language: OCR language code
            confidence_threshold: OCR confidence threshold (0.0-1.0)
        """
        if enabled is not None:
            self.config_manager.set_value('conversion.enable_ocr', enabled)
        
        if language:
            self.config_manager.set_value('conversion.ocr_language', language)
        
        if confidence_threshold is not None:
            if not 0.0 <= confidence_threshold <= 1.0:
                raise ValueError("Confidence threshold must be 0.0-1.0")
            self.config_manager.set_value('conversion.ocr_confidence_threshold', confidence_threshold)
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance settings."""
        return {
            'parallel_processing': self.config_manager.get_value('conversion.parallel_processing', True),
            'worker_threads': self.config_manager.get_value('conversion.worker_threads', 4),
            'batch_size': self.config_manager.get_value('conversion.batch_size', 10),
            'timeout_seconds': self.config_manager.get_value('conversion.timeout_seconds', 300)
        }
```

## Environment Variables

### Environment Variable Support
```python
class EnvironmentConfig:
    """Environment variable configuration support."""
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        'MARKITDOWN_GUI_THEME': 'ui.theme',
        'MARKITDOWN_GUI_LANGUAGE': 'ui.language',
        'MARKITDOWN_GUI_OUTPUT_FORMAT': 'conversion.default_output_format',
        'MARKITDOWN_GUI_OUTPUT_DIR': 'conversion.output_directory',
        'MARKITDOWN_GUI_OCR_ENABLED': 'conversion.enable_ocr',
        'MARKITDOWN_GUI_OCR_LANGUAGE': 'conversion.ocr_language',
        'MARKITDOWN_GUI_WORKER_THREADS': 'conversion.worker_threads',
        'MARKITDOWN_GUI_MAX_FILE_SIZE': 'performance.max_file_size',
        'MARKITDOWN_GUI_CACHE_ENABLED': 'performance.cache_enabled',
        'MARKITDOWN_GUI_LOG_LEVEL': 'logging.level',
        'MARKITDOWN_GUI_LOG_FILE': 'logging.log_file',
        'MARKITDOWN_GUI_DEBUG': 'logging.level',  # Special handling for debug flag
    }
    
    @classmethod
    def load_from_environment(cls) -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Returns:
            Configuration dictionary from environment
        """
        import os
        
        config = {}
        
        for env_var, config_key in cls.ENV_MAPPINGS.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Type conversion based on config key
                converted_value = cls._convert_env_value(config_key, value)
                cls._set_nested_dict_value(config, config_key, converted_value)
        
        return config
    
    @staticmethod
    def _convert_env_value(config_key: str, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        
        # Boolean values
        if config_key in ['conversion.enable_ocr', 'conversion.parallel_processing',
                         'performance.cache_enabled', 'ui.check_updates']:
            return value.lower() in ('true', '1', 'yes', 'on')
        
        # Integer values
        if config_key in ['conversion.worker_threads', 'conversion.batch_size',
                         'conversion.timeout_seconds', 'performance.max_file_size',
                         'performance.cache_size', 'ui.font_size']:
            try:
                return int(value)
            except ValueError:
                return value  # Let validation handle the error
        
        # Float values
        if config_key in ['conversion.ocr_confidence_threshold']:
            try:
                return float(value)
            except ValueError:
                return value
        
        # Special handling for debug flag
        if config_key == 'logging.level' and value.lower() in ('true', '1', 'debug'):
            return 'DEBUG'
        
        # Default: return as string
        return value
    
    @staticmethod
    def _set_nested_dict_value(dictionary: Dict, key: str, value: Any) -> None:
        """Set nested dictionary value using dot notation."""
        keys = key.split('.')
        current = dictionary
        
        for key_part in keys[:-1]:
            if key_part not in current:
                current[key_part] = {}
            current = current[key_part]
        
        current[keys[-1]] = value
```

## Migration and Versioning

### Configuration Migration
```python
class ConfigMigrator:
    """Handles configuration migration between versions."""
    
    # Migration functions for each version
    MIGRATIONS = {
        '0.9.0': '_migrate_from_0_9_0',
        '1.0.0': '_migrate_from_1_0_0',
    }
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def migrate_if_needed(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration if version change detected.
        
        Args:
            config_data: Raw configuration data
            
        Returns:
            Migrated configuration data
        """
        current_version = config_data.get('version', '0.9.0')
        target_version = Config().version
        
        if current_version == target_version:
            return config_data
        
        # Apply migrations in sequence
        migrated_data = config_data.copy()
        
        for version in sorted(self.MIGRATIONS.keys()):
            if self._version_greater_than(version, current_version):
                migration_func = getattr(self, self.MIGRATIONS[version])
                migrated_data = migration_func(migrated_data)
        
        # Update version
        migrated_data['version'] = target_version
        
        return migrated_data
    
    def _migrate_from_0_9_0(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 0.9.0 to 1.0.0."""
        migrated = config_data.copy()
        
        # Rename 'interface' section to 'ui'
        if 'interface' in migrated:
            migrated['ui'] = migrated.pop('interface')
        
        # Move theme setting
        if 'ui' in migrated and 'appearance' in migrated['ui']:
            appearance = migrated['ui'].pop('appearance')
            if 'theme' in appearance:
                migrated['ui']['theme'] = appearance['theme']
        
        # Update output format names
        if 'conversion' in migrated and 'output_format' in migrated['conversion']:
            format_mapping = {
                'md': 'markdown',
                'htm': 'html',
                'txt': 'text'
            }
            old_format = migrated['conversion']['output_format']
            migrated['conversion']['default_output_format'] = format_mapping.get(old_format, old_format)
            del migrated['conversion']['output_format']
        
        return migrated
    
    def _migrate_from_1_0_0(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.0.0 to future version."""
        # Placeholder for future migrations
        return config_data
    
    @staticmethod
    def _version_greater_than(version1: str, version2: str) -> bool:
        """Compare version strings."""
        def version_tuple(v):
            return tuple(map(int, (v.split('.'))))
        
        return version_tuple(version1) > version_tuple(version2)
```

---

**Related Documentation:**
- 🔧 [Core API](core.md) - Core functionality reference
- 🧩 [Components API](components.md) - UI component reference
- 🔧 [Development Setup](../developer/setup.md) - Environment configuration
- 🚀 [Deployment Guide](../deployment/deployment.md) - Production configuration
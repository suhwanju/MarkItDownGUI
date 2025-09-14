# Core API Reference

Complete API reference for MarkItDown GUI core functionality and interfaces.

## Table of Contents

- [Overview](#overview)
- [Core Interfaces](#core-interfaces)
- [Configuration API](#configuration-api)
- [Conversion API](#conversion-api)
- [File Management API](#file-management-api)
- [Internationalization API](#internationalization-api)
- [Logging API](#logging-api)
- [Event System API](#event-system-api)
- [Error Handling](#error-handling)

## Overview

The Core API provides the fundamental interfaces and services that power MarkItDown GUI. These APIs are designed to be:

- **Type-safe**: Full type annotations for better IDE support
- **Extensible**: Plugin-friendly architecture
- **Testable**: Clean interfaces for unit testing
- **Async-aware**: Support for asynchronous operations

### Import Structure
```python
# Core functionality
from markitdown_gui.core import (
    ConfigManager,
    ConversionEngine,
    FileService,
    I18nManager,
    Logger
)

# Models and types
from markitdown_gui.models import (
    Document,
    ConversionJob,
    ConversionResult,
    Config,
    ValidationResult
)

# Exceptions
from markitdown_gui.core.exceptions import (
    MarkItDownGUIError,
    ConversionError,
    ValidationError,
    ConfigurationError
)
```

## Core Interfaces

### Base Interfaces

#### IConverter
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

class IConverter(ABC):
    """Interface for document converters."""
    
    @abstractmethod
    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the file.
        
        Args:
            file_path: Path to the input file
            
        Returns:
            True if converter can handle the file
        """
        pass
    
    @abstractmethod
    def convert(self, 
                input_file: Path, 
                output_format: str = 'markdown',
                options: Optional[Dict[str, Any]] = None) -> 'ConversionResult':
        """Convert a file to the specified format.
        
        Args:
            input_file: Path to input file
            output_format: Target format (default: 'markdown')
            options: Conversion-specific options
            
        Returns:
            ConversionResult object with conversion details
            
        Raises:
            ConversionError: If conversion fails
            ValidationError: If input validation fails
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats.
        
        Returns:
            List of file extensions (e.g., ['.pdf', '.docx'])
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Converter name for identification."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Converter version."""
        pass
```

#### IConfigProvider
```python
class IConfigProvider(ABC):
    """Interface for configuration providers."""
    
    @abstractmethod
    def load_config(self, config_path: Optional[Path] = None) -> 'Config':
        """Load configuration from source.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            Config object
            
        Raises:
            ConfigurationError: If config cannot be loaded
        """
        pass
    
    @abstractmethod
    def save_config(self, config: 'Config', config_path: Optional[Path] = None) -> None:
        """Save configuration to storage.
        
        Args:
            config: Configuration object to save
            config_path: Optional path for config file
            
        Raises:
            ConfigurationError: If config cannot be saved
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: 'Config') -> 'ValidationResult':
        """Validate configuration object.
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationResult with validation status
        """
        pass
```

#### IFileValidator
```python
class IFileValidator(ABC):
    """Interface for file validation."""
    
    @abstractmethod
    def validate(self, file_path: Path) -> 'ValidationResult':
        """Validate a file for processing.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with validation details
        """
        pass
    
    @abstractmethod
    def get_file_info(self, file_path: Path) -> 'FileInfo':
        """Get detailed file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            FileInfo object with file details
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be accessed
        """
        pass
```

## Configuration API

### ConfigManager
```python
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration."""
    
    # UI Settings
    theme: str = 'auto'
    language: str = 'en'
    window_geometry: Optional[Dict[str, int]] = None
    
    # Conversion Settings
    default_output_format: str = 'markdown'
    output_directory: Optional[str] = None
    preserve_metadata: bool = True
    enable_ocr: bool = True
    ocr_language: str = 'eng'
    
    # Performance Settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    worker_threads: int = 4
    cache_enabled: bool = True
    cache_size: int = 100
    
    # Logging Settings
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    enable_debug: bool = False

class ConfigManager(IConfigProvider):
    """Central configuration management."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Optional custom configuration directory
        """
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_file = self.config_dir / 'config.yaml'
        self._config: Optional[Config] = None
    
    def load_config(self, config_path: Optional[Path] = None) -> Config:
        """Load configuration from file or defaults.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            Loaded configuration object
            
        Example:
            >>> manager = ConfigManager()
            >>> config = manager.load_config()
            >>> print(config.theme)
            'auto'
        """
        config_path = config_path or self.config_file
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                import yaml
                config_data = yaml.safe_load(f)
                self._config = Config(**config_data)
        else:
            self._config = Config()
        
        return self._config
    
    def save_config(self, config: Config, config_path: Optional[Path] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration object to save
            config_path: Optional path for config file
            
        Example:
            >>> config.theme = 'dark'
            >>> manager.save_config(config)
        """
        config_path = config_path or self.config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config.__dict__, f, default_flow_style=False)
    
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
        
        Args:
            **kwargs: Configuration key-value pairs to update
            
        Example:
            >>> manager.update_config(theme='dark', language='es')
        """
        if self._config is None:
            self._config = Config()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = Config()
    
    def _get_default_config_dir(self) -> Path:
        """Get platform-specific default configuration directory."""
        import platform
        
        system = platform.system()
        if system == 'Windows':
            import os
            return Path(os.environ.get('APPDATA', '')) / 'markitdown-gui'
        elif system == 'Darwin':  # macOS
            return Path.home() / 'Library' / 'Application Support' / 'MarkItDown GUI'
        else:  # Linux and others
            return Path.home() / '.config' / 'markitdown-gui'
```

## Conversion API

### ConversionEngine
```python
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ConversionStatus(Enum):
    """Conversion job status."""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

@dataclass
class ConversionResult:
    """Result of a conversion operation."""
    
    job_id: str
    input_file: Path
    output_file: Optional[Path]
    output_content: Optional[str]
    status: ConversionStatus
    message: str
    started_at: datetime
    completed_at: Optional[datetime]
    processing_time: Optional[float]  # seconds
    metadata: Dict[str, Any]
    
    @property
    def success(self) -> bool:
        """Check if conversion was successful."""
        return self.status == ConversionStatus.COMPLETED
    
    @property
    def error_message(self) -> Optional[str]:
        """Get error message if conversion failed."""
        return self.message if self.status == ConversionStatus.FAILED else None

@dataclass
class ConversionJob:
    """Represents a conversion job."""
    
    id: str
    input_file: Path
    output_format: str
    output_file: Optional[Path] = None
    options: Dict[str, Any] = None
    status: ConversionStatus = ConversionStatus.PENDING
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.options is None:
            self.options = {}

class ConversionEngine:
    """Core conversion engine."""
    
    def __init__(self, config: Config, logger: 'Logger'):
        """Initialize conversion engine.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self._converters: Dict[str, IConverter] = {}
        self._register_default_converters()
    
    def register_converter(self, converter: IConverter) -> None:
        """Register a new converter.
        
        Args:
            converter: Converter implementation to register
            
        Example:
            >>> engine = ConversionEngine(config, logger)
            >>> engine.register_converter(CustomPDFConverter())
        """
        for format_ext in converter.get_supported_formats():
            self._converters[format_ext.lower()] = converter
        
        self.logger.info(f"Registered converter: {converter.name} v{converter.version}")
    
    def get_supported_formats(self) -> List[str]:
        """Get all supported input formats.
        
        Returns:
            List of supported file extensions
        """
        return list(self._converters.keys())
    
    def can_convert(self, file_path: Path) -> bool:
        """Check if file can be converted.
        
        Args:
            file_path: Path to input file
            
        Returns:
            True if file can be converted
        """
        extension = file_path.suffix.lower()
        return extension in self._converters
    
    def create_job(self, 
                   input_file: Path, 
                   output_format: str = 'markdown',
                   output_file: Optional[Path] = None,
                   options: Optional[Dict[str, Any]] = None) -> ConversionJob:
        """Create a new conversion job.
        
        Args:
            input_file: Path to input file
            output_format: Target output format
            output_file: Optional output file path
            options: Conversion options
            
        Returns:
            Created ConversionJob
            
        Raises:
            ValidationError: If input file is invalid
        """
        import uuid
        
        # Validate input file
        if not input_file.exists():
            raise ValidationError(f"Input file does not exist: {input_file}")
        
        if not self.can_convert(input_file):
            raise ValidationError(f"Unsupported file format: {input_file.suffix}")
        
        # Generate output file if not provided
        if output_file is None:
            output_file = self._generate_output_file(input_file, output_format)
        
        job = ConversionJob(
            id=str(uuid.uuid4()),
            input_file=input_file,
            output_format=output_format,
            output_file=output_file,
            options=options or {}
        )
        
        return job
    
    def convert(self, job: ConversionJob) -> ConversionResult:
        """Execute conversion job.
        
        Args:
            job: Conversion job to execute
            
        Returns:
            ConversionResult with conversion details
            
        Example:
            >>> job = engine.create_job(Path('document.pdf'))
            >>> result = engine.convert(job)
            >>> if result.success:
            ...     print(f"Converted to: {result.output_file}")
        """
        start_time = datetime.now()
        
        try:
            job.status = ConversionStatus.RUNNING
            
            # Get appropriate converter
            extension = job.input_file.suffix.lower()
            converter = self._converters[extension]
            
            # Perform conversion
            conversion_result = converter.convert(
                input_file=job.input_file,
                output_format=job.output_format,
                options=job.options
            )
            
            # Save output if file path provided
            output_content = conversion_result
            if job.output_file and isinstance(conversion_result, str):
                job.output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(job.output_file, 'w', encoding='utf-8') as f:
                    f.write(conversion_result)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return ConversionResult(
                job_id=job.id,
                input_file=job.input_file,
                output_file=job.output_file,
                output_content=output_content,
                status=ConversionStatus.COMPLETED,
                message="Conversion completed successfully",
                started_at=start_time,
                completed_at=end_time,
                processing_time=processing_time,
                metadata={'converter': converter.name}
            )
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Conversion failed for {job.input_file}: {e}")
            
            return ConversionResult(
                job_id=job.id,
                input_file=job.input_file,
                output_file=None,
                output_content=None,
                status=ConversionStatus.FAILED,
                message=str(e),
                started_at=start_time,
                completed_at=end_time,
                processing_time=processing_time,
                metadata={}
            )
    
    def batch_convert(self, jobs: List[ConversionJob]) -> List[ConversionResult]:
        """Convert multiple files in batch.
        
        Args:
            jobs: List of conversion jobs
            
        Returns:
            List of conversion results
            
        Example:
            >>> jobs = [
            ...     engine.create_job(Path('doc1.pdf')),
            ...     engine.create_job(Path('doc2.docx'))
            ... ]
            >>> results = engine.batch_convert(jobs)
            >>> successful = [r for r in results if r.success]
        """
        results = []
        
        for job in jobs:
            result = self.convert(job)
            results.append(result)
            
            # Log progress
            self.logger.info(
                f"Converted {job.input_file.name}: "
                f"{result.status.value} ({len(results)}/{len(jobs)})"
            )
        
        return results
    
    def _register_default_converters(self) -> None:
        """Register built-in converters."""
        from markitdown_gui.converters import (
            MarkItDownConverter,
            PDFConverter,
            WordConverter,
            PowerPointConverter,
            ExcelConverter
        )
        
        # Register default converters
        self.register_converter(MarkItDownConverter())
        
        # Register specific converters if available
        try:
            self.register_converter(PDFConverter())
        except ImportError:
            self.logger.warning("PDF converter not available")
    
    def _generate_output_file(self, input_file: Path, output_format: str) -> Path:
        """Generate output file path."""
        if self.config.output_directory:
            output_dir = Path(self.config.output_directory)
        else:
            output_dir = input_file.parent
        
        # Determine file extension
        ext_map = {
            'markdown': '.md',
            'text': '.txt',
            'html': '.html',
            'json': '.json'
        }
        extension = ext_map.get(output_format, '.md')
        
        output_file = output_dir / f"{input_file.stem}{extension}"
        return output_file
```

## File Management API

### FileService
```python
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileInfo:
    """Detailed file information."""
    
    path: Path
    name: str
    size: int
    extension: str
    mime_type: Optional[str]
    created_at: datetime
    modified_at: datetime
    is_readable: bool
    is_writable: bool
    checksum: Optional[str] = None
    
    @classmethod
    def from_path(cls, file_path: Path) -> 'FileInfo':
        """Create FileInfo from file path."""
        import mimetypes
        import hashlib
        
        stat = file_path.stat()
        
        return cls(
            path=file_path,
            name=file_path.name,
            size=stat.st_size,
            extension=file_path.suffix.lower(),
            mime_type=mimetypes.guess_type(str(file_path))[0],
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            is_readable=file_path.is_file() and os.access(file_path, os.R_OK),
            is_writable=os.access(file_path.parent, os.W_OK)
        )

@dataclass
class ValidationResult:
    """File validation result."""
    
    is_valid: bool
    message: str
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class FileService(IFileValidator):
    """File management and validation service."""
    
    # Security constraints
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {
        '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
        '.xlsx', '.xls', '.txt', '.html', '.htm',
        '.md', '.rtf', '.odt', '.odp', '.ods'
    }
    
    def __init__(self, config: Config, logger: 'Logger'):
        """Initialize file service.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
    
    def validate(self, file_path: Path) -> ValidationResult:
        """Validate file for processing.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with validation details
            
        Example:
            >>> service = FileService(config, logger)
            >>> result = service.validate(Path('document.pdf'))
            >>> if result.is_valid:
            ...     print("File is valid for processing")
        """
        errors = []
        warnings = []
        
        # Check if file exists
        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return ValidationResult(False, "File not found", errors, warnings)
        
        # Check if it's a file (not directory)
        if not file_path.is_file():
            errors.append(f"Path is not a file: {file_path}")
        
        # Check file extension
        extension = file_path.suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            errors.append(f"File type not supported: {extension}")
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            max_size = self.config.max_file_size or self.MAX_FILE_SIZE
            
            if file_size > max_size:
                errors.append(f"File too large: {file_size} bytes (max: {max_size})")
            elif file_size == 0:
                warnings.append("File is empty")
        except OSError as e:
            errors.append(f"Cannot access file: {e}")
        
        # Check permissions
        if not os.access(file_path, os.R_OK):
            errors.append("File is not readable")
        
        # Validate file content
        try:
            content_result = self._validate_content(file_path)
            if not content_result.is_valid:
                errors.extend(content_result.errors)
                warnings.extend(content_result.warnings)
        except Exception as e:
            warnings.append(f"Content validation failed: {e}")
        
        is_valid = len(errors) == 0
        message = "Valid file" if is_valid else f"Validation failed: {len(errors)} errors"
        
        return ValidationResult(is_valid, message, errors, warnings)
    
    def get_file_info(self, file_path: Path) -> FileInfo:
        """Get detailed file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            FileInfo object with file details
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be accessed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            return FileInfo.from_path(file_path)
        except OSError as e:
            raise PermissionError(f"Cannot access file: {e}")
    
    def find_files(self, 
                   directory: Path, 
                   pattern: str = "*",
                   recursive: bool = False,
                   include_hidden: bool = False) -> List[Path]:
        """Find files matching criteria.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern for matching
            recursive: Search subdirectories
            include_hidden: Include hidden files
            
        Returns:
            List of matching file paths
            
        Example:
            >>> files = service.find_files(
            ...     Path('/documents'), 
            ...     pattern='*.pdf',
            ...     recursive=True
            ... )
        """
        if not directory.exists() or not directory.is_dir():
            return []
        
        glob_method = directory.rglob if recursive else directory.glob
        files = []
        
        for file_path in glob_method(pattern):
            if file_path.is_file():
                # Skip hidden files if requested
                if not include_hidden and file_path.name.startswith('.'):
                    continue
                
                # Filter by allowed extensions
                if file_path.suffix.lower() in self.ALLOWED_EXTENSIONS:
                    files.append(file_path)
        
        return sorted(files)
    
    def calculate_checksum(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate file checksum.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm ('sha256', 'md5', etc.)
            
        Returns:
            Hexadecimal checksum string
            
        Example:
            >>> checksum = service.calculate_checksum(Path('document.pdf'))
            >>> print(f"SHA256: {checksum}")
        """
        import hashlib
        
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def _validate_content(self, file_path: Path) -> ValidationResult:
        """Validate file content and structure."""
        warnings = []
        errors = []
        
        try:
            # Basic file header validation
            with open(file_path, 'rb') as f:
                header = f.read(1024)  # First 1KB
            
            extension = file_path.suffix.lower()
            
            # PDF validation
            if extension == '.pdf':
                if not header.startswith(b'%PDF-'):
                    errors.append("Invalid PDF header")
            
            # Office document validation
            elif extension in ['.docx', '.pptx', '.xlsx']:
                # ZIP-based formats
                if not header.startswith(b'PK'):
                    errors.append("Invalid Office document structure")
            
            # HTML validation
            elif extension in ['.html', '.htm']:
                try:
                    content = header.decode('utf-8', errors='ignore')
                    if not any(tag in content.lower() for tag in ['<html', '<body', '<!doctype']):
                        warnings.append("File may not be valid HTML")
                except UnicodeDecodeError:
                    warnings.append("File encoding may be problematic")
            
        except Exception as e:
            warnings.append(f"Content validation error: {e}")
        
        is_valid = len(errors) == 0
        message = "Content validation passed" if is_valid else "Content validation failed"
        
        return ValidationResult(is_valid, message, errors, warnings)
```

## Internationalization API

### I18nManager
```python
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication

class I18nManager:
    """Internationalization and localization manager."""
    
    def __init__(self, app: QCoreApplication, translations_dir: Path):
        """Initialize i18n manager.
        
        Args:
            app: Qt application instance
            translations_dir: Directory containing translation files
        """
        self.app = app
        self.translations_dir = translations_dir
        self.current_language = 'en'
        self.translators: List[QTranslator] = []
        self._translations: Dict[str, Dict[str, str]] = {}
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available languages.
        
        Returns:
            List of language dictionaries with 'code', 'name', 'native_name'
            
        Example:
            >>> manager = I18nManager(app, translations_dir)
            >>> languages = manager.get_available_languages()
            >>> print(languages[0])
            {'code': 'en', 'name': 'English', 'native_name': 'English'}
        """
        languages = [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'es', 'name': 'Spanish', 'native_name': 'Español'},
            {'code': 'fr', 'name': 'French', 'native_name': 'Français'},
            {'code': 'de', 'name': 'German', 'native_name': 'Deutsch'},
            {'code': 'ja', 'name': 'Japanese', 'native_name': '日本語'},
            {'code': 'ko', 'name': 'Korean', 'native_name': '한국어'},
            {'code': 'zh', 'name': 'Chinese', 'native_name': '中文'},
            {'code': 'ru', 'name': 'Russian', 'native_name': 'Русский'},
        ]
        
        # Filter to only available translations
        available = []
        for lang in languages:
            translation_file = self.translations_dir / f"{lang['code']}.qm"
            if translation_file.exists():
                available.append(lang)
        
        return available
    
    def set_language(self, language_code: str) -> bool:
        """Set application language.
        
        Args:
            language_code: ISO language code (e.g., 'en', 'es')
            
        Returns:
            True if language was successfully set
            
        Example:
            >>> success = manager.set_language('es')
            >>> if success:
            ...     print("Language changed to Spanish")
        """
        # Remove existing translators
        for translator in self.translators:
            self.app.removeTranslator(translator)
        self.translators.clear()
        
        if language_code == 'en':
            # English is the source language, no translation needed
            self.current_language = language_code
            return True
        
        # Load Qt base translations
        qt_translator = QTranslator()
        qt_path = QLibraryInfo.location(QLibraryInfo.LibraryLocation.TranslationsPath)
        if qt_translator.load(f"qt_{language_code}", qt_path):
            self.app.installTranslator(qt_translator)
            self.translators.append(qt_translator)
        
        # Load application translations
        app_translator = QTranslator()
        translation_file = self.translations_dir / f"{language_code}.qm"
        
        if translation_file.exists() and app_translator.load(str(translation_file)):
            self.app.installTranslator(app_translator)
            self.translators.append(app_translator)
            self.current_language = language_code
            return True
        
        return False
    
    def get_current_language(self) -> str:
        """Get current language code.
        
        Returns:
            Current language code
        """
        return self.current_language
    
    def translate(self, context: str, text: str, **kwargs) -> str:
        """Translate text with context.
        
        Args:
            context: Translation context (usually class name)
            text: Text to translate
            **kwargs: Format arguments for string substitution
            
        Returns:
            Translated text
            
        Example:
            >>> translated = manager.translate(
            ...     'MainWindow', 'Convert {count} files', count=5
            ... )
        """
        from PyQt6.QtCore import QCoreApplication
        
        translated = QCoreApplication.translate(context, text)
        
        # Apply string formatting if arguments provided
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, ValueError):
                # Fall back to original text if formatting fails
                pass
        
        return translated
    
    def tr(self, text: str, context: Optional[str] = None, **kwargs) -> str:
        """Convenience method for translation.
        
        Args:
            text: Text to translate
            context: Optional context (defaults to calling class)
            **kwargs: Format arguments
            
        Returns:
            Translated text
        """
        if context is None:
            # Try to determine context from call stack
            import inspect
            frame = inspect.currentframe().f_back
            context = frame.f_locals.get('self', type(None)).__class__.__name__
        
        return self.translate(context, text, **kwargs)
    
    def get_system_language(self) -> str:
        """Get system default language.
        
        Returns:
            System language code
        """
        system_locale = QLocale.system()
        language = system_locale.name().split('_')[0]  # e.g., 'en_US' -> 'en'
        return language
    
    def format_number(self, number: float, decimals: int = 2) -> str:
        """Format number according to current locale.
        
        Args:
            number: Number to format
            decimals: Number of decimal places
            
        Returns:
            Formatted number string
        """
        locale = QLocale(self.current_language)
        return locale.toString(number, 'f', decimals)
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return self.tr("{seconds:.1f} seconds", seconds=seconds)
        elif seconds < 3600:
            minutes = seconds / 60
            return self.tr("{minutes:.1f} minutes", minutes=minutes)
        else:
            hours = seconds / 3600
            return self.tr("{hours:.1f} hours", hours=hours)
```

## Logging API

### Logger
```python
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class Logger:
    """Enhanced logging system for MarkItDown GUI."""
    
    def __init__(self, config: Config):
        """Initialize logger with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger instance.
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Logger instance
            
        Example:
            >>> logger_manager = Logger(config)
            >>> logger = logger_manager.get_logger(__name__)
            >>> logger.info("Application started")
        """
        if name not in self._loggers:
            self._loggers[name] = self._create_logger(name)
        
        return self._loggers[name]
    
    def set_level(self, level: str) -> None:
        """Set logging level for all loggers.
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        for logger in self._loggers.values():
            logger.setLevel(numeric_level)
    
    def add_file_handler(self, log_file: Path, level: str = 'INFO') -> None:
        """Add file handler to all loggers.
        
        Args:
            log_file: Path to log file
            level: Minimum logging level for file
        """
        # Create log directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add to all existing loggers
        for logger in self._loggers.values():
            logger.addHandler(file_handler)
    
    def log_conversion_start(self, job: 'ConversionJob') -> None:
        """Log conversion job start.
        
        Args:
            job: Conversion job being started
        """
        logger = self.get_logger('conversion')
        logger.info(
            f"Starting conversion: {job.input_file.name} -> {job.output_format} "
            f"(Job ID: {job.id})"
        )
    
    def log_conversion_end(self, result: 'ConversionResult') -> None:
        """Log conversion job completion.
        
        Args:
            result: Conversion result
        """
        logger = self.get_logger('conversion')
        
        if result.success:
            logger.info(
                f"Conversion completed: {result.input_file.name} "
                f"in {result.processing_time:.2f}s"
            )
        else:
            logger.error(
                f"Conversion failed: {result.input_file.name} - "
                f"{result.error_message}"
            )
    
    def log_performance_metric(self, operation: str, duration: float, **metadata) -> None:
        """Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
            **metadata: Additional metadata
        """
        logger = self.get_logger('performance')
        
        metadata_str = ', '.join(f"{k}={v}" for k, v in metadata.items())
        logger.info(
            f"Performance: {operation} took {duration:.3f}s "
            f"({metadata_str})" if metadata_str else ""
        )
    
    def _setup_logging(self) -> None:
        """Setup basic logging configuration."""
        # Set root logger level
        root_logger = logging.getLogger()
        level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        root_logger.setLevel(level)
        
        # Create console handler if none exists
        if not root_logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            formatter = logging.Formatter(
                '%(levelname)s - %(name)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            root_logger.addHandler(console_handler)
        
        # Add file handler if specified in config
        if self.config.log_file:
            log_file = Path(self.config.log_file)
            self.add_file_handler(log_file, self.config.log_level)
    
    def _create_logger(self, name: str) -> logging.Logger:
        """Create a new logger instance."""
        logger = logging.getLogger(name)
        
        # Set level from config
        level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        return logger
```

## Event System API

### EventBus
```python
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import threading

@dataclass
class Event:
    """Event object with metadata."""
    
    type: str
    data: Any
    timestamp: datetime
    source: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

class EventBus:
    """Application-wide event bus for loose coupling."""
    
    def __init__(self):
        """Initialize event bus."""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to events of specific type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to handle events
            
        Example:
            >>> def on_file_converted(event):
            ...     print(f"File converted: {event.data.input_file}")
            >>> 
            >>> event_bus = EventBus()
            >>> event_bus.subscribe('file_converted', on_file_converted)
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from events.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                except ValueError:
                    pass  # Handler not found
    
    def publish(self, event_type: str, data: Any, source: Optional[str] = None) -> None:
        """Publish event to subscribers.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Optional event source identifier
            
        Example:
            >>> event_bus.publish('file_converted', result, 'ConversionEngine')
        """
        event = Event(
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )
        
        # Get copy of subscribers to avoid issues if list changes
        with self._lock:
            handlers = self._subscribers.get(event_type, []).copy()
        
        # Call handlers (outside lock to avoid deadlock)
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue processing other handlers
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Event handler error: {e}")
    
    def clear_subscribers(self, event_type: Optional[str] = None) -> None:
        """Clear subscribers.
        
        Args:
            event_type: Specific event type to clear, or None for all
        """
        with self._lock:
            if event_type:
                self._subscribers.pop(event_type, None)
            else:
                self._subscribers.clear()
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for event type.
        
        Args:
            event_type: Event type to check
            
        Returns:
            Number of subscribers
        """
        with self._lock:
            return len(self._subscribers.get(event_type, []))
```

## Error Handling

### Exception Hierarchy
```python
class MarkItDownGUIError(Exception):
    """Base exception for all MarkItDown GUI errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize exception.
        
        Args:
            message: Human-readable error message
            code: Optional error code for programmatic handling
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class ValidationError(MarkItDownGUIError):
    """Raised when input validation fails."""
    pass

class ConversionError(MarkItDownGUIError):
    """Raised when document conversion fails."""
    pass

class ConfigurationError(MarkItDownGUIError):
    """Raised when configuration is invalid."""
    pass

class FileSystemError(MarkItDownGUIError):
    """Raised for file system related errors."""
    pass

class PermissionError(MarkItDownGUIError):
    """Raised when insufficient permissions."""
    pass

# Error handling utilities
def handle_error(error: Exception, logger: logging.Logger, context: str = "") -> None:
    """Standard error handling function.
    
    Args:
        error: Exception to handle
        logger: Logger instance
        context: Additional context information
    """
    if isinstance(error, MarkItDownGUIError):
        logger.error(f"{context}: {error.message} (Code: {error.code})")
        if error.details:
            logger.debug(f"Error details: {error.details}")
    else:
        logger.error(f"{context}: Unexpected error: {error}")
        logger.debug(f"Error type: {type(error).__name__}")
```

---

**Related Documentation:**
- 🏗️ [Architecture Overview](../developer/architecture.md) - System design
- 🧩 [Component API](components.md) - UI component reference
- ⚙️ [Configuration API](configuration.md) - Settings management
- 🎯 [Event System API](events.md) - Event handling reference
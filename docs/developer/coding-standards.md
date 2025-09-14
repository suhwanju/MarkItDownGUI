# Coding Standards

Code quality guidelines and best practices for MarkItDown GUI development.

## Table of Contents

- [Overview](#overview)
- [Python Style Guide](#python-style-guide)
- [PyQt6 Guidelines](#pyqt6-guidelines)
- [Documentation Standards](#documentation-standards)
- [Testing Standards](#testing-standards)
- [Code Review Guidelines](#code-review-guidelines)
- [Tools and Automation](#tools-and-automation)

## Overview

### Code Quality Principles

1. **Readability First** - Code is read more often than written
2. **Consistency** - Follow established patterns throughout the codebase
3. **Simplicity** - Choose simple solutions over complex ones
4. **Maintainability** - Write code that's easy to modify and extend
5. **Performance** - Be mindful of performance implications
6. **Security** - Consider security implications in all code

### Quality Metrics

- **Code Coverage**: 90%+ for core functionality
- **Complexity**: Cyclomatic complexity < 10 per function
- **Documentation**: All public APIs documented
- **Type Hints**: 100% coverage for new code
- **Linting**: Zero warnings from configured linters

## Python Style Guide

### General Formatting

#### Line Length and Indentation
```python
# Good: 88 characters max (Black formatter standard)
def convert_document_with_options(
    input_file: Path, 
    output_format: str = 'markdown',
    preserve_formatting: bool = True
) -> ConversionResult:
    pass

# Good: Proper indentation (4 spaces)
if condition_one and condition_two:
    result = perform_complex_operation(
        parameter_one,
        parameter_two,
        parameter_three
    )
    return result

# Bad: Line too long
def convert_document_with_options(input_file: Path, output_format: str = 'markdown', preserve_formatting: bool = True, enable_ocr: bool = False) -> ConversionResult:
    pass
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Third-party imports
import yaml
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QThread

# Local application imports
from markitdown_gui.core.config import Config
from markitdown_gui.core.logger import get_logger
from markitdown_gui.models.document import Document

# Relative imports (within same package)
from .base_converter import BaseConverter
from .exceptions import ConversionError
```

### Type Annotations

#### Comprehensive Type Hints
```python
from typing import List, Dict, Optional, Union, Callable, Any, TypeVar, Generic
from pathlib import Path

# Function signatures
def process_files(
    files: List[Path],
    output_dir: Optional[Path] = None,
    callback: Optional[Callable[[str], None]] = None
) -> Dict[str, ConversionResult]:
    """Process multiple files with optional callback."""
    pass

# Class with generic types
T = TypeVar('T')

class CacheManager(Generic[T]):
    """Generic cache manager."""
    
    def __init__(self, max_size: int = 100) -> None:
        self._cache: Dict[str, T] = {}
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[T]:
        """Get cached value."""
        return self._cache.get(key)
    
    def put(self, key: str, value: T) -> None:
        """Store value in cache."""
        if len(self._cache) >= self._max_size:
            self._evict_oldest()
        self._cache[key] = value

# Complex return types
def analyze_document(file_path: Path) -> Dict[str, Union[str, int, List[str]]]:
    """Analyze document and return metadata."""
    return {
        'format': 'pdf',
        'pages': 10,
        'languages': ['en', 'es'],
        'has_images': True
    }
```

### Error Handling

#### Exception Hierarchy
```python
# Custom exception hierarchy
class MarkItDownGUIError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code

class ValidationError(MarkItDownGUIError):
    """Input validation failed."""
    pass

class ConversionError(MarkItDownGUIError):
    """Document conversion failed."""
    
    def __init__(self, message: str, file_path: Optional[Path] = None):
        super().__init__(message)
        self.file_path = file_path

class ConfigurationError(MarkItDownGUIError):
    """Configuration is invalid."""
    pass

# Exception handling patterns
def convert_file(file_path: Path) -> ConversionResult:
    """Convert file with proper error handling."""
    try:
        # Validate input
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Perform conversion
        result = _perform_conversion(file_path)
        return result
        
    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise ConversionError(
            f"Conversion failed for {file_path.name}: {e}",
            file_path=file_path
        ) from e

def _perform_conversion(file_path: Path) -> ConversionResult:
    """Internal conversion logic."""
    # Implementation details
    pass
```

### Class Design

#### Clean Class Structure
```python
class DocumentConverter:
    """Converts documents between different formats."""
    
    def __init__(self, config: Config, logger: Logger) -> None:
        """Initialize converter with configuration and logger.
        
        Args:
            config: Application configuration
            logger: Logger instance for this converter
        """
        self._config = config
        self._logger = logger
        self._cache: Dict[str, ConversionResult] = {}
        self._supported_formats = {'.pdf', '.docx', '.pptx', '.xlsx'}
    
    @property
    def supported_formats(self) -> Set[str]:
        """Get supported file formats."""
        return self._supported_formats.copy()
    
    def can_convert(self, file_path: Path) -> bool:
        """Check if file can be converted.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file can be converted
        """
        return file_path.suffix.lower() in self._supported_formats
    
    def convert(self, input_file: Path, output_format: str = 'markdown') -> ConversionResult:
        """Convert file to specified format.
        
        Args:
            input_file: Input file path
            output_format: Target format
            
        Returns:
            Conversion result
            
        Raises:
            ValidationError: If input is invalid
            ConversionError: If conversion fails
        """
        # Validate inputs
        self._validate_input(input_file, output_format)
        
        # Check cache first
        cache_key = self._get_cache_key(input_file, output_format)
        if cache_key in self._cache:
            self._logger.debug(f"Using cached result for {input_file.name}")
            return self._cache[cache_key]
        
        # Perform conversion
        result = self._do_conversion(input_file, output_format)
        
        # Cache result
        self._cache[cache_key] = result
        
        return result
    
    def _validate_input(self, file_path: Path, output_format: str) -> None:
        """Validate conversion inputs."""
        if not self.can_convert(file_path):
            raise ValidationError(f"Unsupported format: {file_path.suffix}")
        
        if output_format not in {'markdown', 'text', 'html'}:
            raise ValidationError(f"Unsupported output format: {output_format}")
    
    def _do_conversion(self, input_file: Path, output_format: str) -> ConversionResult:
        """Perform the actual conversion."""
        # Implementation would go here
        pass
    
    def _get_cache_key(self, file_path: Path, output_format: str) -> str:
        """Generate cache key for file and format."""
        import hashlib
        
        file_info = f"{file_path}:{file_path.stat().st_mtime}:{output_format}"
        return hashlib.md5(file_info.encode()).hexdigest()
```

### Function Design

#### Function Guidelines
```python
# Good: Single responsibility, clear parameters
def calculate_file_checksum(file_path: Path, algorithm: str = 'sha256') -> str:
    """Calculate checksum for file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal checksum string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm is unsupported
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError as e:
        raise ValueError(f"Unsupported algorithm: {algorithm}") from e
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

# Good: Pure function with no side effects
def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes < 0:
        return "0 B"
    
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

# Bad: Too many parameters, unclear purpose
def process_stuff(data, fmt, opts, callback, cache, validate=True, async_mode=False):
    # Too many parameters, unclear what this does
    pass

# Good: Use data classes for complex parameter sets
@dataclass
class ConversionOptions:
    """Options for document conversion."""
    output_format: str = 'markdown'
    preserve_formatting: bool = True
    enable_ocr: bool = False
    ocr_language: str = 'eng'
    quality: str = 'medium'

def convert_with_options(file_path: Path, options: ConversionOptions) -> ConversionResult:
    """Convert file with specified options."""
    # Clear what this function does
    pass
```

## PyQt6 Guidelines

### Widget Organization

#### Widget Structure
```python
class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    conversion_requested = pyqtSignal(Path, str)
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config_manager: ConfigManager) -> None:
        """Initialize main window.
        
        Args:
            config_manager: Application configuration manager
        """
        super().__init__()
        
        # Store dependencies
        self._config_manager = config_manager
        self._logger = get_logger(__name__)
        
        # Initialize UI
        self._setup_ui()
        self._connect_signals()
        self._apply_initial_settings()
    
    def _setup_ui(self) -> None:
        """Setup user interface components."""
        self.setWindowTitle("MarkItDown GUI")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create and add components
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
    
    def _create_toolbar(self) -> None:
        """Create application toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Add actions
        open_action = QAction("Open", self)
        open_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart))
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_files)
        toolbar.addAction(open_action)
        
        convert_action = QAction("Convert", self)
        convert_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        convert_action.setShortcut(QKeySequence("Ctrl+R"))
        convert_action.triggered.connect(self._on_convert)
        toolbar.addAction(convert_action)
    
    def _connect_signals(self) -> None:
        """Connect Qt signals to slots."""
        # Use clear signal/slot connections
        self.conversion_requested.connect(self._handle_conversion_request)
        
        # Use partial for parameterized connections
        from functools import partial
        self.settings_changed.connect(
            partial(self._handle_settings_change, source='user')
        )
```

### Signal/Slot Best Practices

#### Signal Definitions
```python
class ConversionWorker(QThread):
    """Background conversion worker."""
    
    # Define signals with proper types
    progress_updated = pyqtSignal(int)  # percentage
    file_completed = pyqtSignal(Path, ConversionResult)
    error_occurred = pyqtSignal(Path, str)  # file_path, error_message
    batch_completed = pyqtSignal(list)  # List[ConversionResult]
    
    def __init__(self, files: List[Path], options: ConversionOptions) -> None:
        super().__init__()
        self._files = files
        self._options = options
        self._should_stop = False
    
    def run(self) -> None:
        """Execute conversion in background thread."""
        results = []
        
        for i, file_path in enumerate(self._files):
            if self._should_stop:
                break
            
            try:
                result = self._convert_file(file_path)
                self.file_completed.emit(file_path, result)
                results.append(result)
                
            except Exception as e:
                error_msg = str(e)
                self.error_occurred.emit(file_path, error_msg)
                self._logger.error(f"Conversion failed: {file_path} - {error_msg}")
            
            # Update progress
            progress = int((i + 1) / len(self._files) * 100)
            self.progress_updated.emit(progress)
        
        self.batch_completed.emit(results)
    
    def stop(self) -> None:
        """Request worker to stop."""
        self._should_stop = True

# Signal connection patterns
class ConversionController:
    """Manages conversion operations."""
    
    def __init__(self) -> None:
        self._worker: Optional[ConversionWorker] = None
    
    def start_conversion(self, files: List[Path], options: ConversionOptions) -> None:
        """Start background conversion."""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        
        self._worker = ConversionWorker(files, options)
        
        # Connect all signals
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.file_completed.connect(self._on_file_completed)
        self._worker.error_occurred.connect(self._on_error_occurred)
        self._worker.batch_completed.connect(self._on_batch_completed)
        
        self._worker.start()
    
    def _on_progress_updated(self, percentage: int) -> None:
        """Handle progress updates."""
        print(f"Progress: {percentage}%")
    
    def _on_file_completed(self, file_path: Path, result: ConversionResult) -> None:
        """Handle individual file completion."""
        print(f"Completed: {file_path.name}")
    
    def _on_error_occurred(self, file_path: Path, error_message: str) -> None:
        """Handle conversion errors."""
        print(f"Error processing {file_path.name}: {error_message}")
    
    def _on_batch_completed(self, results: List[ConversionResult]) -> None:
        """Handle batch completion."""
        successful = len([r for r in results if r.success])
        print(f"Batch completed: {successful}/{len(results)} successful")
```

### Resource Management

#### Proper Resource Cleanup
```python
class ResourceManager:
    """Manages Qt resources and cleanup."""
    
    def __init__(self) -> None:
        self._temp_files: List[Path] = []
        self._open_dialogs: List[QDialog] = []
        self._workers: List[QThread] = []
    
    def create_temp_file(self, suffix: str = '.tmp') -> Path:
        """Create temporary file with automatic cleanup."""
        import tempfile
        
        temp_file = Path(tempfile.mktemp(suffix=suffix))
        self._temp_files.append(temp_file)
        return temp_file
    
    def add_dialog(self, dialog: QDialog) -> None:
        """Track dialog for cleanup."""
        self._open_dialogs.append(dialog)
        dialog.finished.connect(lambda: self._remove_dialog(dialog))
    
    def add_worker(self, worker: QThread) -> None:
        """Track worker thread for cleanup."""
        self._workers.append(worker)
        worker.finished.connect(lambda: self._remove_worker(worker))
    
    def cleanup(self) -> None:
        """Clean up all managed resources."""
        # Stop all worker threads
        for worker in self._workers[:]:  # Copy list to avoid modification during iteration
            worker.quit()
            worker.wait(5000)  # Wait up to 5 seconds
            if worker.isRunning():
                worker.terminate()
                worker.wait(1000)
        
        # Close all dialogs
        for dialog in self._open_dialogs[:]:
            dialog.close()
        
        # Remove temporary files
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError:
                pass  # Ignore cleanup errors
        
        self._temp_files.clear()
    
    def _remove_dialog(self, dialog: QDialog) -> None:
        """Remove dialog from tracking."""
        try:
            self._open_dialogs.remove(dialog)
        except ValueError:
            pass  # Already removed
    
    def _remove_worker(self, worker: QThread) -> None:
        """Remove worker from tracking."""
        try:
            self._workers.remove(worker)
        except ValueError:
            pass  # Already removed

# Usage in application
class Application:
    """Main application class."""
    
    def __init__(self) -> None:
        self._resource_manager = ResourceManager()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._resource_manager.cleanup()
    
    def create_conversion_worker(self, files: List[Path]) -> ConversionWorker:
        """Create and track conversion worker."""
        worker = ConversionWorker(files)
        self._resource_manager.add_worker(worker)
        return worker
```

## Documentation Standards

### Docstring Guidelines

#### Module Docstrings
```python
"""Document conversion utilities for MarkItDown GUI.

This module provides the core document conversion functionality, including
support for various input formats (PDF, DOCX, PPTX, etc.) and output
formats (Markdown, HTML, plain text).

The main classes are:
    - DocumentConverter: Primary conversion interface
    - ConversionResult: Conversion operation result
    - ConversionOptions: Configuration for conversion operations

Example:
    Basic usage of the conversion system:
    
    >>> converter = DocumentConverter(config, logger)
    >>> result = converter.convert(Path('document.pdf'))
    >>> if result.success:
    ...     print(f"Converted to: {result.output_file}")

Note:
    This module requires the MarkItDown library for core conversion
    functionality and PyQt6 for progress reporting.
"""
```

#### Class Docstrings
```python
class DocumentConverter:
    """Converts documents between different formats.
    
    The DocumentConverter class provides a high-level interface for converting
    documents from various input formats to different output formats. It handles
    format detection, validation, caching, and progress reporting.
    
    Attributes:
        supported_formats: Set of supported input file extensions
        cache_enabled: Whether result caching is enabled
        
    Example:
        >>> config = Config()
        >>> logger = get_logger(__name__)
        >>> converter = DocumentConverter(config, logger)
        >>> 
        >>> # Convert single file
        >>> result = converter.convert(Path('document.pdf'))
        >>> 
        >>> # Batch conversion
        >>> files = [Path('doc1.pdf'), Path('doc2.docx')]
        >>> results = converter.convert_batch(files)
    
    Note:
        The converter uses caching to avoid redundant conversions of the
        same file with the same settings. Cache keys are based on file
        path, modification time, and conversion options.
    """
```

#### Method Docstrings
```python
def convert(
    self, 
    input_file: Path, 
    output_format: str = 'markdown',
    options: Optional[ConversionOptions] = None
) -> ConversionResult:
    """Convert a file to the specified format.
    
    This method converts a single document from its native format to the
    requested output format. The conversion process includes validation,
    format detection, actual conversion, and result packaging.
    
    Args:
        input_file: Path to the input document file. Must exist and be readable.
        output_format: Target format for conversion. Must be one of the
            supported output formats: 'markdown', 'html', 'text'.
        options: Optional conversion options. If None, default options will
            be used based on the current configuration.
    
    Returns:
        ConversionResult object containing:
            - success: Whether the conversion succeeded
            - output_content: Converted content as string
            - output_file: Path to output file (if saved)
            - error_message: Error description (if failed)
            - metadata: Additional conversion metadata
    
    Raises:
        ValidationError: If the input file is invalid, doesn't exist, or
            has an unsupported format.
        ConversionError: If the conversion process fails due to file
            corruption, processing errors, or system issues.
        PermissionError: If the input file cannot be read due to insufficient
            permissions.
    
    Example:
        >>> converter = DocumentConverter(config, logger)
        >>> result = converter.convert(Path('report.pdf'), 'markdown')
        >>> if result.success:
        ...     print(f"Conversion successful: {len(result.output_content)} characters")
        ... else:
        ...     print(f"Conversion failed: {result.error_message}")
    
    Note:
        This method is thread-safe and can be called concurrently from
        multiple threads. Results may be cached to improve performance
        for repeated conversions of the same file.
    """
```

## Testing Standards

### Test Structure

#### Test Organization
```python
"""Test cases for DocumentConverter class."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from markitdown_gui.core.converter import DocumentConverter
from markitdown_gui.core.config import Config
from markitdown_gui.core.exceptions import ValidationError, ConversionError
from markitdown_gui.models.conversion import ConversionResult, ConversionOptions


class TestDocumentConverter:
    """Test cases for DocumentConverter."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        config = Config()
        config.max_file_size = 10 * 1024 * 1024  # 10MB
        config.cache_enabled = True
        return config
    
    @pytest.fixture
    def logger(self):
        """Provide mock logger."""
        return Mock()
    
    @pytest.fixture
    def converter(self, config, logger):
        """Provide configured converter instance."""
        return DocumentConverter(config, logger)
    
    @pytest.fixture
    def sample_pdf(self, tmp_path):
        """Provide sample PDF file."""
        pdf_file = tmp_path / "sample.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n%sample content")
        return pdf_file
    
    def test_can_convert_supported_format(self, converter):
        """Test format support detection."""
        pdf_file = Path("document.pdf")
        docx_file = Path("document.docx")
        unsupported_file = Path("document.xyz")
        
        assert converter.can_convert(pdf_file)
        assert converter.can_convert(docx_file)
        assert not converter.can_convert(unsupported_file)
    
    def test_convert_success(self, converter, sample_pdf):
        """Test successful conversion."""
        with patch('markitdown_gui.core.converter.MarkItDown') as mock_md:
            mock_md.return_value.convert.return_value.text_content = "# Sample Content"
            
            result = converter.convert(sample_pdf)
            
            assert result.success
            assert result.output_content == "# Sample Content"
            assert result.error_message is None
            mock_md.return_value.convert.assert_called_once()
    
    def test_convert_file_not_found(self, converter):
        """Test error handling for missing file."""
        missing_file = Path("nonexistent.pdf")
        
        with pytest.raises(ValidationError, match="File not found"):
            converter.convert(missing_file)
    
    def test_convert_unsupported_format(self, converter, tmp_path):
        """Test error handling for unsupported format."""
        unsupported_file = tmp_path / "document.xyz"
        unsupported_file.write_text("content")
        
        with pytest.raises(ValidationError, match="Unsupported format"):
            converter.convert(unsupported_file)
    
    @pytest.mark.parametrize("output_format,expected_extension", [
        ("markdown", ".md"),
        ("html", ".html"),
        ("text", ".txt"),
    ])
    def test_output_format_handling(self, converter, sample_pdf, output_format, expected_extension):
        """Test different output formats."""
        with patch('markitdown_gui.core.converter.MarkItDown') as mock_md:
            mock_md.return_value.convert.return_value.text_content = f"Content in {output_format}"
            
            result = converter.convert(sample_pdf, output_format=output_format)
            
            assert result.success
            assert f"Content in {output_format}" in result.output_content
    
    def test_caching_behavior(self, converter, sample_pdf):
        """Test that results are cached properly."""
        with patch('markitdown_gui.core.converter.MarkItDown') as mock_md:
            mock_md.return_value.convert.return_value.text_content = "Cached content"
            
            # First conversion
            result1 = converter.convert(sample_pdf)
            
            # Second conversion (should use cache)
            result2 = converter.convert(sample_pdf)
            
            assert result1.output_content == result2.output_content
            # MarkItDown should only be called once due to caching
            assert mock_md.return_value.convert.call_count == 1
    
    def test_batch_conversion(self, converter, tmp_path):
        """Test batch conversion of multiple files."""
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = tmp_path / f"document{i}.pdf"
            file_path.write_bytes(b"%PDF-1.4\n%content")
            files.append(file_path)
        
        with patch('markitdown_gui.core.converter.MarkItDown') as mock_md:
            mock_md.return_value.convert.return_value.text_content = "Converted content"
            
            results = converter.convert_batch(files)
            
            assert len(results) == 3
            assert all(result.success for result in results)
            assert mock_md.return_value.convert.call_count == 3
    
    def test_conversion_error_handling(self, converter, sample_pdf):
        """Test error handling during conversion."""
        with patch('markitdown_gui.core.converter.MarkItDown') as mock_md:
            mock_md.return_value.convert.side_effect = Exception("Conversion failed")
            
            with pytest.raises(ConversionError, match="Conversion failed"):
                converter.convert(sample_pdf)
    
    @pytest.mark.integration
    def test_real_pdf_conversion(self, converter):
        """Integration test with real PDF file."""
        # This would use a real PDF file for integration testing
        # Skip if test file not available
        test_pdf = Path("tests/fixtures/sample.pdf")
        if not test_pdf.exists():
            pytest.skip("Test PDF file not available")
        
        result = converter.convert(test_pdf)
        
        assert result.success
        assert len(result.output_content) > 0
        assert "markdown" in result.metadata.get("format", "").lower()
```

### Performance Tests

#### Benchmark Tests
```python
"""Performance benchmarks for conversion operations."""

import time
import pytest
from pathlib import Path

from markitdown_gui.core.converter import DocumentConverter


class TestConversionPerformance:
    """Performance tests for conversion operations."""
    
    @pytest.mark.benchmark
    def test_single_file_conversion_speed(self, converter, large_pdf):
        """Test conversion speed for single large file."""
        start_time = time.time()
        
        result = converter.convert(large_pdf)
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        assert result.success
        assert conversion_time < 30.0  # Should complete within 30 seconds
    
    @pytest.mark.benchmark
    def test_batch_conversion_speed(self, converter, multiple_files):
        """Test batch conversion performance."""
        start_time = time.time()
        
        results = converter.convert_batch(multiple_files)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_file = total_time / len(multiple_files)
        
        assert all(r.success for r in results)
        assert avg_time_per_file < 5.0  # Average < 5 seconds per file
    
    @pytest.mark.benchmark
    def test_memory_usage(self, converter, large_files):
        """Test memory usage during conversion."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        results = converter.convert_batch(large_files)
        
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        memory_per_file = memory_increase / len(large_files)
        
        assert all(r.success for r in results)
        assert memory_per_file < 50 * 1024 * 1024  # < 50MB per file
```

## Code Review Guidelines

### Review Checklist

#### Functionality Review
- [ ] Code solves the intended problem
- [ ] Edge cases are handled appropriately
- [ ] Error conditions are properly managed
- [ ] Performance implications are considered
- [ ] Security implications are addressed

#### Code Quality Review
- [ ] Code follows project style guidelines
- [ ] Functions and classes have single responsibility
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Variable and function names are descriptive
- [ ] Complex logic is broken down into smaller functions

#### Testing Review
- [ ] Unit tests cover new functionality
- [ ] Tests include both positive and negative cases
- [ ] Integration tests verify component interaction
- [ ] Performance tests are included for critical paths
- [ ] Tests are maintainable and readable

#### Documentation Review
- [ ] Public APIs are documented with docstrings
- [ ] Complex algorithms are explained with comments
- [ ] User-facing changes are documented
- [ ] API changes are noted in changelog

### Review Process

#### Pull Request Review
```python
# Example review comment structure

"""
## Overall Assessment
The implementation looks solid and follows our coding standards well.

## Specific Comments

### 📍 Line 45-60: Error Handling
Good use of custom exceptions here. Consider adding more specific error 
messages for different validation failures.

```python
# Suggested improvement
if not file_path.exists():
    raise ValidationError(f"File not found: {file_path}")
elif not file_path.is_file():
    raise ValidationError(f"Path is not a file: {file_path}")
elif file_path.stat().st_size == 0:
    raise ValidationError(f"File is empty: {file_path}")
```

### 📍 Line 78: Performance Consideration
This loop could be optimized for large file lists. Consider using 
`concurrent.futures` for parallel processing.

### 📍 Line 95: Documentation
Add docstring example showing typical usage.

### ✅ What I Liked
- Excellent type annotations throughout
- Clean separation of concerns
- Comprehensive error handling
- Good test coverage

## Approval Status
✅ Approved after addressing the documentation comment.
"""
```

## Tools and Automation

### Code Quality Tools

#### Pre-commit Configuration (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-toml
      - id: check-json
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-docstrings
          - flake8-type-checking
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML, types-requests]
```

#### Tool Configuration

**Black Configuration (`pyproject.toml`):**
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

**isort Configuration:**
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["markitdown_gui"]
known_third_party = ["PyQt6", "markitdown", "yaml", "PIL"]
```

**Flake8 Configuration (`.flake8`):**
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .eggs,
    .venv
per-file-ignores =
    __init__.py:F401
    tests/*:D100,D101,D102,D103,D104
```

**MyPy Configuration:**
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "markitdown.*",
    "PyQt6.*",
]
ignore_missing_imports = true
```

#### GitHub Actions Workflow
```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run Black
      run: black --check markitdown_gui/ tests/
    
    - name: Run isort
      run: isort --check-only markitdown_gui/ tests/
    
    - name: Run Flake8
      run: flake8 markitdown_gui/ tests/
    
    - name: Run MyPy
      run: mypy markitdown_gui/
    
    - name: Run tests with coverage
      run: |
        pytest --cov=markitdown_gui --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

**Related Documentation:**
- 🔧 [Development Setup](setup.md) - Environment configuration
- 🏗️ [Architecture Overview](architecture.md) - System design principles
- 🧪 [Testing Guide](testing.md) - Testing strategies and practices
- 🤝 [Contributing Guide](../contributing/contributing.md) - Contribution workflow
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based desktop application called **MarkItDown GUI Converter** that converts various document formats to Markdown using Microsoft's MarkItDown library. It's a production-ready application with enterprise-level features including internationalization, accessibility compliance, advanced error handling, and comprehensive document processing capabilities.

## Development Commands

### Running the Application
```bash
# Standard execution
python main.py

# Debug mode with verbose logging
python main.py --debug

# Run with virtual environment (recommended)
venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac
python main.py
```

### Testing
```bash
# Run all tests with coverage (requires pytest-cov)
pytest

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m gui          # GUI-related tests
pytest -m slow         # Slower tests

# Run individual test files from both directories
python logs/test_accessibility.py       # Development/debugging tests
python tests/unit/test_config_manager.py  # Formal test suite

# Run specific test categories
pytest tests/unit/                      # Unit tests in formal structure
pytest tests/gui/                       # GUI component tests
pytest tests/e2e/                       # End-to-end workflow tests

# Test specific components
python logs/test_fontbbox_solution.py   # PDF FontBBox error handling
python logs/test_theme_system.py        # Theme management
python logs/test_i18n.py                # Internationalization
```

### Building Executables
```bash
# Standard build for Windows
venv/Scripts/pyinstaller.exe --onefile --windowed --name="MarkItDown_GUI" main.py

# Complete build with all format support
venv/Scripts/pyinstaller.exe \
  --onefile --windowed \
  --name="MarkItDown_GUI_Complete" \
  --collect-all markitdown \
  --collect-all magika \
  --hidden-import=markitdown \
  --hidden-import=pdfplumber \
  --hidden-import=PyPDF2 \
  main.py
```

### Dependencies Management
```bash
# Install core dependencies
pip install -r requirements.txt

# Install PDF processing libraries (resolves NO_PDF_LIBRARY warnings)
pip install pdfplumber==0.11.4 PyPDF2==3.0.1

# Or use the automated installer
python install_pdf_dependencies.py
```

## Architecture Overview

### Core Architecture Layers
The application follows a **multi-layered modular architecture**:

1. **Core Services Layer** (`markitdown_gui/core/`)
   - Business logic, data models, and service managers
   - Contains specialized managers for different aspects (conversion, file handling, config, i18n, themes, accessibility)

2. **UI Layer** (`markitdown_gui/ui/`)
   - PyQt6-based user interface components
   - Main window and reusable UI components in `components/` subdirectory

3. **Integration Layer**
   - External library integrations (MarkItDown, PDF libraries, system services)
   - Error handling and recovery systems

### Key Service Managers

#### ConversionManager (`core/conversion_manager.py`)
- **Purpose**: Orchestrates document conversion workflows with enterprise-grade error handling
- **Features**: Async processing, circuit breaker pattern, fallback strategies, 95%+ error recovery
- **Error Handling**: Uses `error_handling/` modules for comprehensive error management
- **Signals**: PyQt6 signals for progress tracking and status updates
- **Thread Safety**: QMutex-based thread synchronization for concurrent operations

#### FileManager (`core/file_manager.py`)
- **Purpose**: Handles file system operations and asynchronous directory scanning
- **Features**: Non-blocking file discovery, metadata extraction, memory-optimized processing
- **Threading**: Uses QThread-based workers for UI responsiveness
- **Path Resolution**: Secure path utilities with `resolve_markdown_output_path()` function

#### AccessibilityManager (`core/accessibility_manager.py`)
- **Purpose**: WCAG 2.1 AA compliance and screen reader support
- **Features**: Keyboard navigation, accessibility validation, screen reader bridge
- **Integration**: Qt Accessibility API integration
- **Components**: Works with `KeyboardNavigationManager` and `ScreenReaderSupport`

#### I18nManager (`core/i18n_manager.py`)
- **Purpose**: Complete internationalization system
- **Languages**: Korean (ko_KR), English (en_US) with runtime switching
- **Features**: Translation validation, cultural adaptation, font optimization
- **Validation**: Automated translation completeness checking with `TranslationValidator`

#### ConfigManager (`core/config_manager.py`)
- **Purpose**: Application configuration management with validation
- **Storage**: JSON-based config files with Qt Settings integration
- **Features**: Schema validation, automatic migration, type-safe configuration access
- **Models**: Uses `AppConfig` dataclass for structured configuration data

### Error Handling System

The application implements enterprise-grade error handling in `core/error_handling/`:

- **CircuitBreaker**: Prevents cascading failures with automatic recovery
- **FallbackManager**: Provides alternative processing strategies
- **ErrorRecoveryManager**: Automatic error recovery with 95%+ success rate
- **ErrorReporter**: Comprehensive error tracking and reporting

### Data Models (`core/models.py`)

Key models for data management:
- **FileInfo**: File metadata with conversion state tracking
- **ConversionResult**: Detailed conversion outcomes and performance metrics
- **ConversionProgress**: Multi-stage progress tracking
- **FileConflictConfig**: Advanced conflict resolution policies

### Supported File Formats

The application supports 15+ file formats through the Microsoft MarkItDown library:
- **Office**: .docx, .pptx, .xlsx, .xls
- **PDF**: .pdf (with advanced FontBBox error handling via pdfplumber + PyPDF2)
- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .tiff (OCR capability through LLM integration)
- **Audio**: .mp3, .wav (transcription support)
- **Web/Text**: .html, .htm, .csv, .json, .xml, .txt
- **Archives**: .zip (recursive extraction and processing)
- **E-books**: .epub
- **Other**: .ipynb (Jupyter notebooks), .msg (Outlook messages)

## Development Guidelines

### Testing Strategy
- **Dual Test Structure**:
  - `tests/` directory: Formal pytest-based test suite with fixtures and proper structure
  - `logs/` directory: Development/debugging test files (40+ scripts) for specific issue validation
- **Test Categories**:
  - Unit tests: Individual component testing with pytest markers
  - GUI tests: PyQt6 widget and interaction testing
  - E2E tests: Complete workflow validation
  - Performance tests: Memory usage and responsiveness benchmarks
- **Coverage Requirement**: 85% minimum (configured in pytest.ini)
- **Test Fixtures**: Comprehensive fixtures in `tests/conftest.py` for QApplication, temp directories, and mock services

### Error Handling Best Practices
- **FontBBox Errors**: The application automatically handles PDF FontBBox warnings - these are expected and properly managed
- **PDF Processing**: Uses dual library approach (pdfplumber + PyPDF2) for comprehensive PDF support
- **Circuit Breaker Pattern**: Prevents system failures through automatic fallback mechanisms
- **Memory Optimization**: MemoryOptimizer handles large file processing and prevents memory leaks

### Configuration Management
- **ConfigManager**: JSON-based configuration with validation
- **Settings Storage**: Qt Settings for window state, custom config for app-specific preferences
- **Theme System**: Dynamic theme switching with system theme detection
- **Accessibility**: WCAG 2.1 AA compliance with comprehensive screen reader support

### Internationalization
- **Language Files**: Located in resource directories
- **Translation Validation**: Automated validation of translation completeness
- **Runtime Switching**: Support for dynamic language changes without restart
- **Cultural Adaptation**: Proper handling of locale-specific formatting

## Important Notes

### PDF Processing
- The application automatically installs and configures PDF processing libraries
- FontBBox warnings are **expected behavior** and indicate proper error detection and recovery
- NO_PDF_LIBRARY warnings should be resolved by installing pdfplumber and PyPDF2

### Performance Characteristics
- **Conversion Speed**: <200ms PDF validation, <10s average conversion per file
- **Memory Usage**: <50MB baseline, optimized for large files
- **Error Recovery**: 95%+ automatic recovery rate for common PDF and document errors
- **Concurrent Processing**: Non-blocking asynchronous file processing

### Production Deployment
The application is **Production Ready** with:
- Comprehensive error handling and recovery systems
- Enterprise-grade memory optimization with `MemoryOptimizer`
- Cross-platform compatibility (Windows, macOS, Linux)
- WCAG 2.1 AA accessibility compliance
- Extensive test coverage with 40+ individual test scripts in dual testing structure

## Key Development Patterns

### Signal-Slot Architecture
The application uses PyQt6's signal-slot pattern extensively:
- **ConversionManager**: Emits progress, completion, and error signals
- **FileManager**: File discovery and metadata extraction signals
- **UI Components**: Real-time updates through signal propagation

### Error Handling Strategy
```python
# Circuit breaker pattern prevents cascading failures
try:
    result = conversion_manager.convert_file(file_info)
except CircuitBreakerError:
    # Fallback to alternative processing
    result = fallback_manager.handle_conversion(file_info)
```

### Dependency Injection
Services are injected through constructors:
```python
# MainWindow receives ConfigManager
main_window = MainWindow(config_manager)

# Managers receive dependencies
conversion_manager = ConversionManager(config_manager)
```

### Resource Management
- **Context Managers**: Automatic resource cleanup
- **Memory Optimization**: Large file processing with memory monitoring
- **Thread Safety**: QMutex for shared resource protection
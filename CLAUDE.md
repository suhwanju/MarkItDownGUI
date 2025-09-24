# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based desktop application called **MarkItDown GUI Converter** that converts various document formats to Markdown using Microsoft's MarkItDown library. It's a production-ready application with enterprise-level features including internationalization, accessibility compliance, advanced error handling, and comprehensive document processing capabilities.

## Quick Start Commands

### Development Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install PDF processing libraries (resolves warnings)
python install_pdf_dependencies.py
```

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
# Run formal test suite with coverage
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m gui          # GUI-related tests
pytest -m slow         # Slower tests

# Run tests in specific directories
pytest tests/unit/      # Formal unit tests
pytest tests/gui/       # GUI component tests
pytest tests/e2e/       # End-to-end workflow tests

# Run development/debugging tests (40+ scripts)
python logs/test_accessibility.py     # Accessibility testing
python logs/test_fontbbox_solution.py # PDF error handling
python logs/test_theme_system.py      # Theme system
python logs/test_i18n.py              # Internationalization

# Validate all fixes
python verify_all_fixes.py            # Comprehensive validation
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

### Linting and Code Quality
```bash
# The project uses pytest configuration for testing standards
# Coverage requirement: 85% minimum (configured in pytest.ini)
# Run with coverage reporting:
pytest --cov=markitdown_gui --cov-report=html:htmlcov

# Check specific test markers defined in pytest.ini:
pytest --markers  # List all available markers
```

## Architecture Overview

The application follows a **multi-layered modular architecture** with dependency injection patterns:

### Core Architecture Layers

1. **Core Services Layer** (`markitdown_gui/core/`)
   - Business logic, data models, and service managers
   - Key components: ConversionManager, FileManager, ConfigManager, I18nManager
   - OCR Enhancement Module (`ocr_enhancements/`) - independent system for 15-40% OCR accuracy improvement
   - Error handling system (`error_handling/`) with circuit breaker pattern and 95%+ recovery rate

2. **UI Layer** (`markitdown_gui/ui/`)
   - PyQt6-based interface with signal-slot architecture
   - Main window, settings dialog, and reusable components (`components/`)
   - Responsive design with accessibility (WCAG 2.1 AA) compliance

3. **Integration Layer**
   - Microsoft MarkItDown library integration with comprehensive error handling
   - PDF processing (pdfplumber + PyPDF2) with FontBBox error recovery
   - System service integrations (themes, i18n, accessibility APIs)

### Key Service Managers

#### ConversionManager (`core/conversion_manager.py`)
- **Purpose**: Orchestrates document conversion workflows with dependency injection
- **Architecture**: Receives ConfigManager via constructor for proper OCR settings access
- **Thread Safety**: QThread-based ConversionWorker with QMutex synchronization
- **Error Handling**: Circuit breaker pattern with fallback strategies (95%+ recovery rate)
- **Recent Fix**: ConfigManager now properly injected to ConversionWorker for OCR functionality

#### ConfigManager (`core/config_manager.py`)
- **Purpose**: INI-based configuration with section independence
- **Architecture**: Each section (General, LLM, ImagePreprocessing, UI) parses independently
- **Storage**: settings.ini with Qt Settings integration for window state
- **Recent Fix**: Eliminated cross-section dependencies to prevent parsing crashes

#### FileManager (`core/file_manager.py`)
- **Purpose**: Asynchronous file system operations with FileScanWorker
- **Features**: Non-blocking directory scanning, metadata extraction, secure path utilities
- **Key Function**: `resolve_markdown_output_path()` for safe file path resolution

#### OCREnhancementManager (`core/ocr_enhancements/`)
- **Architecture**: Independent module with feature flag control (`__init__.py`)
- **Components**: ImagePreprocessor, QualityAnalyzer, StatusProvider, ProgressTracker
- **Pipeline**: 5-stage enhancement (contrast, brightness, deskew, denoise, sharpen)
- **UI Integration**: Status badges in file list, real-time progress tracking

### Error Handling Architecture (`core/error_handling/`)

Enterprise-grade error handling system with comprehensive recovery:

- **CircuitBreaker**: Prevents cascading failures with automatic recovery
- **FallbackManager**: Alternative processing strategies for different error types
- **ErrorRecoveryManager**: 95%+ automatic recovery rate with intelligent retry logic
- **ErrorReporter**: Structured error tracking with severity classification
- **FontBBox Recovery**: Automatic PDF font error detection and graceful handling

### Data Models (`core/models.py`)

Key models with comprehensive state management:
- **FileInfo**: File metadata with conversion state tracking and OCR status
- **ConversionResult**: Detailed outcomes with timing, errors, and recovery information
- **ConversionProgress**: Multi-stage progress tracking with conflict detection
- **AppConfig**: Application configuration with section-based organization
- **OCR Models**: OCREnhancementConfig, OCRStatusInfo, QualityMetrics for enhancement pipeline

### Supported File Formats (15+)

Microsoft MarkItDown integration with enhanced processing:
- **Office**: .docx, .pptx, .xlsx, .xls
- **PDF**: .pdf (FontBBox error recovery, dual library support: pdfplumber + PyPDF2)
- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .tiff (OCR enhancement pipeline)
- **Audio**: .mp3, .wav (transcription support)
- **Web/Text**: .html, .htm, .csv, .json, .xml, .txt
- **Archives**: .zip (recursive extraction), **E-books**: .epub, **Other**: .ipynb, .msg

## Development Guidelines

### Dependency Injection Pattern
The application uses dependency injection for ConfigManager throughout the architecture:
```python
# Proper injection chain
MainWindow(config_manager) → ConversionManager(config_manager) → ConversionWorker(config_manager)
```

### Testing Strategy
- **Dual Test Structure**:
  - `tests/`: Formal pytest suite with 85% coverage requirement
  - `logs/`: 40+ development/debugging scripts for specific issue validation
- **Key Test Categories**: unit, integration, gui, slow (defined in pytest.ini)
- **Test Fixtures**: Comprehensive fixtures in `tests/conftest.py`

### Error Handling Best Practices
- **FontBBox Warnings**: Expected behavior for PDF processing - logged but handled gracefully
- **Circuit Breaker Pattern**: Prevents cascading failures with automatic recovery
- **Section-Independent Config**: Each INI section loads independently to prevent crashes

### Key Development Patterns
- **Signal-Slot Architecture**: PyQt6 signals for decoupled component communication
- **QThread Workers**: Non-blocking operations (FileScanWorker, ConversionWorker)
- **Memory Optimization**: MemoryOptimizer for large file processing and leak prevention
- **Feature Flag Control**: Safe deployment patterns (see OCR module `__init__.py`)

## Important Notes

### Expected Behaviors
- **FontBBox Warnings**: Expected for PDF processing - indicates proper error detection and recovery
- **NO_PDF_LIBRARY**: Resolved by running `python install_pdf_dependencies.py`
- **OCR Status Badges**: Appear in file list when OCR enhancement is enabled

### Performance Characteristics
- **PDF Processing**: <200ms validation, automatic FontBBox error recovery
- **OCR Enhancement**: 15-40% accuracy improvement via 5-stage preprocessing pipeline
- **Memory Usage**: <50MB baseline with MemoryOptimizer for large files
- **Error Recovery**: 95%+ automatic recovery rate via circuit breaker pattern

### Recent Critical Fixes (2025-02-18)
- **ConfigManager Injection**: Fixed ConversionWorker AttributeError by proper dependency injection
- **Configuration Robustness**: Each INI section now parses independently to prevent crashes
- **OCR Integration**: ConversionWorker now receives ConfigManager for proper OCR functionality

## Key Code Patterns

### Dependency Injection Implementation
```python
# Fixed pattern: ConfigManager injection chain
class MainWindow:
    def __init__(self, config_manager):
        self.conversion_manager = ConversionManager(config_manager=config_manager)

class ConversionManager:
    def __init__(self, config_manager=None, ...):
        self._config_manager = config_manager

    def start_conversion(self):
        worker = ConversionWorker(..., config_manager=self._config_manager)
```

### Configuration Section Independence
```python
# Each section loads independently to prevent crashes
def _load_section(self, section_name, defaults):
    try:
        return self._parse_section(section_name)
    except:
        return defaults  # Graceful fallback
```

### Error Recovery Pattern
```python
# Circuit breaker with fallback strategies
try:
    result = primary_conversion_method()
except RecoverableError as e:
    result = fallback_manager.handle(e)
except FontDescriptorError:
    # Expected for PDF processing - log and continue
    logger.warning(f"FontBBox issue handled: {e}")
```
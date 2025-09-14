# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **fully implemented** PyQt6-based GUI application for converting various document formats to Markdown using Microsoft's MarkItDown library. The application features enterprise-grade architecture with advanced error handling, accessibility compliance, internationalization, and comprehensive testing infrastructure.

## Architecture Overview

The project follows a sophisticated multi-layered architecture with clear separation of concerns:

```
markitdown_gui/
├── core/                          # Business logic and services
│   ├── conversion_manager.py      # Main conversion orchestrator with error recovery
│   ├── file_manager.py           # Async file operations and scanning
│   ├── config_manager.py         # Configuration and settings management
│   ├── i18n_manager.py           # Internationalization (ko_KR, en_US)
│   ├── theme_manager.py          # Dynamic theme system (dark/light/high-contrast)
│   ├── accessibility_manager.py  # WCAG 2.1 AA compliance framework
│   ├── file_conflict_handler.py  # Advanced conflict resolution strategies
│   ├── memory_optimizer.py       # Memory management and performance optimization
│   ├── error_handling/           # Enterprise-grade error management
│   │   ├── circuit_breaker.py    # Circuit breaker pattern implementation
│   │   ├── fallback_manager.py   # Fallback strategies and recovery
│   │   ├── error_recovery.py     # Automatic error recovery system
│   │   └── error_reporter.py     # Comprehensive error reporting
│   ├── validators/               # Document validation system
│   │   ├── pdf_validator.py      # PDF structure and FontBBox error handling
│   │   └── document_validator.py # Generic document validation
│   └── models.py                 # Data models, enums, and type definitions
├── ui/                           # User interface layer
│   ├── main_window.py           # Primary application window with responsive design
│   ├── settings_dialog.py       # Configuration interface with accessibility
│   ├── preview_dialog.py        # Markdown preview with syntax highlighting
│   ├── file_viewer_dialog.py    # Source file content viewer
│   └── components/             # Reusable UI widgets
│       ├── file_list_widget.py  # Enhanced file management with keyboard nav
│       ├── progress_widget.py   # Advanced progress tracking with animations
│       └── log_widget.py       # Real-time logging with filtering
├── resources/
│   ├── translations/           # JSON-based i18n files with validation
│   └── styles/                # QSS theme files with accessibility features
└── markdown/                  # Default output directory (auto-created)
```

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies (includes PDF processing libraries)
pip install -r requirements.txt

# Install additional PDF dependencies if needed
pip install pdfplumber==0.11.4 PyPDF2==3.0.1

# Run the application
python main.py

# Run with debug mode
python main.py --debug
```

### Testing Commands
```bash
# Core validation suite
python verify_all_fixes.py                 # Comprehensive system validation
python test_validation.py                  # Core functionality tests
python test_functional_workflow.py         # End-to-end workflow testing

# Component-specific tests
python test_accessibility_fixes.py         # WCAG 2.1 AA compliance
python test_i18n_fixes.py                 # Internationalization system
python test_theme_system.py               # Theme management and switching
python test_pyqt6_compatibility.py        # PyQt6 compatibility validation
python test_enhanced_progress.py          # Progress tracking system

# Error handling and recovery tests
python test_fontbbox_solution.py          # PDF FontBBox error handling
python test_circuit_breaker_import.py     # Circuit breaker pattern
python test_runtime_fixes.py              # Runtime error recovery

# Performance and optimization
python memory_optimization_validation.py   # Memory usage optimization
python ui_responsiveness_validation.py     # UI performance metrics
python performance_monitor.py             # System performance monitoring

# Integration and security tests
python test_integration_validation.py     # Cross-component integration
python security_analysis_report.py       # Security vulnerability analysis
```

### Build Commands
```bash
# Standard Windows executable build
venv/Scripts/pyinstaller.exe --onefile --windowed --name="MarkItDown_GUI" main.py

# Optimized build with all dependencies (recommended)
venv/Scripts/pyinstaller.exe --onefile --windowed --name="MarkItDown_GUI" \
  --hidden-import=PyQt6 --hidden-import=psutil --hidden-import=logging \
  --hidden-import=pdfplumber --hidden-import=PyPDF2 \
  --exclude-module=markdown --exclude-module=markitdown main.py

# Full-featured build with all format support
venv/Scripts/pyinstaller.exe \
  --onefile --windowed \
  --name="MarkItDown_GUI_Complete" \
  --collect-all markitdown \
  --collect-all magika \
  --add-data "venv/Lib/site-packages/magika/models;magika/models" \
  --hidden-import=markitdown --hidden-import=magika \
  --hidden-import=pptx --hidden-import=pdfminer.six \
  --exclude-module=markdown \
  main.py
```

## Key Technical Components

### Enterprise-Grade Error Handling System
The application features a sophisticated error handling architecture:

- **CircuitBreaker Pattern**: Prevents cascading failures during PDF processing and document conversion
- **FallbackManager**: Provides alternative processing strategies when primary methods fail
- **ErrorRecoveryManager**: Automatic recovery from FontBBox errors, PDF parsing failures, and MarkItDown library issues
- **ErrorReporter**: Comprehensive error reporting with categorization and severity levels

### Document Processing Pipeline
- **ConversionManager**: Main orchestrator with threaded conversion workers and progress tracking
- **FileManager**: Asynchronous file scanning with memory optimization for large directories
- **ValidationSystem**: Pre-conversion validation including PDF structure analysis and FontBBox error detection
- **ConflictResolution**: Advanced file conflict handling with user-configurable policies

### UI Architecture & Accessibility
- **Responsive Design**: Memory-optimized widgets with adaptive layouts
- **WCAG 2.1 AA Compliance**: Full accessibility support including screen reader compatibility
- **Dynamic Theming**: System-integrated theme switching (light/dark/high-contrast) with accessibility features
- **Keyboard Navigation**: Complete keyboard navigation with focus management
- **Internationalization**: Runtime language switching between Korean and English

### Configuration & Persistence
- **ConfigManager**: JSON-based configuration with validation and migration support
- **ThemeManager**: Dynamic theme application with accessibility considerations
- **I18nManager**: Translation management with validation and fallback support
- **MemoryOptimizer**: Intelligent memory management for large-scale file processing

## Development Guidelines

### Code Organization & Architecture Patterns
- **Layered Architecture**: Clear separation between core services, UI components, and resources
- **Manager Pattern**: Centralized service managers for theme, i18n, accessibility, error handling
- **Observer Pattern**: PyQt6 signals/slots for event-driven communication between components
- **Strategy Pattern**: Pluggable conflict resolution, error recovery, and conversion strategies
- **Circuit Breaker Pattern**: Fault tolerance in document processing pipeline
- **Factory Pattern**: Dynamic widget creation and theme application

### Error Handling Philosophy
- **Defensive Programming**: Comprehensive validation at all system boundaries
- **Graceful Degradation**: Fallback strategies for PDF processing and document conversion failures
- **Circuit Breaker**: Prevent cascading failures during bulk operations
- **Centralized Reporting**: All errors flow through ErrorReporter for consistent handling
- **Recovery First**: Automatic error recovery before user notification

### Performance & Memory Management
- **Async-First Design**: All file I/O operations use QThread workers to maintain UI responsiveness
- **Memory Optimization**: MemoryOptimizer manages resource usage during large-scale operations
- **Lazy Loading**: Components and resources loaded on-demand
- **Batch Processing**: Efficient bulk file processing with progress tracking and cancellation support
- **Resource Cleanup**: Automatic cleanup of temporary files and memory resources

## Critical Implementation Details

### PDF Processing & Error Handling
- **FontBBox Error Recovery**: Automatic detection and recovery from PDF font descriptor errors
- **PDF Library Integration**: pdfplumber and PyPDF2 for enhanced PDF processing capabilities
- **Circuit Breaker Protection**: Prevents system failures during problematic PDF processing
- **Validation Pipeline**: Pre-conversion PDF structure validation with fallback strategies

### Accessibility Implementation (WCAG 2.1 AA)
- **Screen Reader Support**: Complete ARIA labeling and semantic markup
- **Keyboard Navigation**: Full keyboard accessibility with focus management and visual indicators
- **High Contrast Mode**: System-integrated high contrast theme with enhanced visibility
- **Scalable Interface**: Dynamic font scaling and responsive layout adaptation
- **Focus Management**: Proper tab order and focus indication throughout the application

### File Processing Capabilities
- **Supported Formats**: 15+ file types including Office documents (.docx, .pptx, .xlsx), PDFs, images, audio files, web formats, and archives
- **Conflict Resolution**: Advanced file conflict handling with policies (overwrite, skip, rename, ask)
- **Metadata Preservation**: Original file metadata embedded in generated Markdown
- **Batch Processing**: Memory-efficient processing of large file sets with progress tracking

### Internationalization System
- **Language Support**: Complete Korean (ko_KR) and English (en_US) translations
- **Runtime Language Switching**: Dynamic language changes without application restart
- **Locale-Aware Formatting**: Proper formatting for dates, numbers, file sizes, and currency
- **Translation Validation**: Built-in validation system ensuring translation completeness

### Testing & Quality Assurance
- **Test Coverage**: 40+ comprehensive test scripts covering all major components
- **Integration Testing**: End-to-end workflow validation and cross-component testing
- **Performance Testing**: Memory usage, UI responsiveness, and scalability validation
- **Accessibility Testing**: WCAG compliance verification and screen reader compatibility
- **Error Simulation**: Comprehensive error condition testing and recovery validation

### Production Deployment
- **Build System**: PyInstaller with optimized configurations for Windows, macOS, and Linux
- **Dependencies**: Carefully managed dependency tree with version pinning
- **Memory Footprint**: Optimized for enterprise deployment with memory usage monitoring
- **Error Reporting**: Production-ready error reporting and logging system
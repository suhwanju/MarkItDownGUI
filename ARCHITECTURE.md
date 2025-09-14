# MarkItDown GUI Converter - System Architecture

## Overview

MarkItDown GUI Converter is a sophisticated PyQt6-based desktop application that provides a comprehensive document conversion solution. The application converts various document formats to Markdown using Microsoft's MarkItDown library, featuring enterprise-level capabilities including internationalization, accessibility compliance, advanced theming, and intelligent file conflict resolution.

## Architecture Philosophy

The system follows a **multi-layered modular architecture** with clear separation of concerns:

- **Core Layer**: Business logic, data models, and service managers
- **UI Layer**: User interface components and presentation logic  
- **Integration Layer**: External library integrations and system services
- **Resource Layer**: Themes, translations, and static assets

## System Structure

```
MarkItDown GUI Converter
├── Application Entry Point (main.py)
├── Core Services Layer (markitdown_gui/core/)
├── User Interface Layer (markitdown_gui/ui/)
├── Resource Management (markitdown_gui/resources/)
└── Configuration & Storage
```

## Core Services Layer

### 1. Service Managers

#### ConversionManager
**Purpose**: Orchestrates document conversion workflows with advanced progress tracking and error recovery
- **Key Features**: Async file processing, intelligent conflict resolution, progress monitoring
- **Dependencies**: MarkItDown library, FileConflictHandler, MemoryOptimizer
- **Signals**: `conversion_progress_updated`, `file_conversion_started`, `file_conversion_completed`, `conversion_completed`, `conversion_error`

#### FileManager
**Purpose**: Handles file system operations, scanning, and metadata extraction
- **Key Features**: Asynchronous directory scanning, file type detection, size validation
- **Components**: FileScanWorker (QThread), memory-optimized file discovery
- **Signals**: `scan_progress_updated`, `file_found`, `scan_completed`, `scan_error`

#### ConfigManager
**Purpose**: Manages application configuration, user preferences, and persistent settings
- **Storage**: JSON-based configuration with validation
- **Features**: Recent directories, user preferences, conflict policies
- **Integration**: Qt Settings for window state, custom config for app-specific data

#### I18nManager (Internationalization)
**Purpose**: Complete internationalization system with dynamic language switching
- **Supported Languages**: Korean (ko_KR), English (en_US)
- **Features**: Runtime language switching, locale-aware formatting, font optimization
- **Components**: Translation validation, cultural adaptation
- **Signals**: `language_changed`, `font_changed`

#### ThemeManager
**Purpose**: Advanced theming system with WCAG 2.1 AA compliance
- **Themes**: Light, Dark, High-contrast, System-aware
- **Features**: Dynamic theme switching, variable-based stylesheets, accessibility optimization
- **Components**: SystemThemeDetector for OS integration
- **Signals**: `theme_changed`, `system_theme_detected`

#### AccessibilityManager  
**Purpose**: Comprehensive accessibility compliance and screen reader support
- **Standards**: WCAG 2.1 AA compliant
- **Features**: Screen reader bridge, keyboard navigation, accessibility validation
- **Components**: AccessibilityValidator, ScreenReaderSupport, KeyboardNavigationManager
- **Integration**: Qt Accessibility API, ARIA support

### 2. Data Models

#### Core Models (models.py)
- **FileInfo**: Comprehensive file metadata with conversion state tracking
- **ConversionResult**: Detailed conversion outcomes with timing and error information  
- **ConversionProgress**: Multi-stage progress tracking with conflict detection
- **FileConflictConfig**: Advanced conflict resolution policies
- **AppConfig**: Application-wide configuration structure

#### Enums for State Management
- **ConversionStatus**: `PENDING`, `IN_PROGRESS`, `SUCCESS`, `FAILED`, `CANCELLED`
- **FileConflictPolicy**: `SKIP`, `OVERWRITE`, `RENAME`, `ASK_USER`
- **ConversionProgressStatus**: Detailed stage tracking from initialization to completion
- **FileType**: Comprehensive file format support (15+ formats)

### 3. Specialized Services

#### FileConflictHandler
**Purpose**: Intelligent file conflict resolution with multiple strategies
- **Policies**: Automatic renaming, overwrite, skip, user prompt
- **Features**: Backup creation, pattern-based naming, conflict logging

#### MemoryOptimizer  
**Purpose**: Performance optimization and memory management
- **Features**: Automatic garbage collection, weak reference management, resource monitoring
- **Components**: WeakReferenceManager, resource context management

#### LLMManager
**Purpose**: Secure LLM integration for OCR and image processing
- **Features**: Secure key storage, multiple provider support, API client management
- **Security**: Encrypted credential storage, secure API communication

## User Interface Layer

### 1. Main Architecture

#### MainWindow (main_window.py)
**Central Hub**: Primary application interface with comprehensive feature integration
- **Layout**: Splitter-based responsive design with file list and control panels
- **Features**: Menu system, status bar, accessibility integration
- **Components**: Integrates all UI widgets and dialogs

#### Component Architecture
```
MainWindow
├── Directory Selection Group
├── File List Widget (Splitter Top)
├── Bottom Panel (Splitter Bottom)
│   ├── Progress Widget  
│   └── Log Widget
└── Action Button Bar
```

### 2. Reusable Components

#### FileListWidget
**Purpose**: Advanced file management with multi-selection and status tracking
- **Features**: Tree view with file icons, status indicators, context menus
- **Performance**: Memory-optimized display with lazy loading
- **Accessibility**: Screen reader support, keyboard navigation

#### ProgressWidget  
**Purpose**: Sophisticated progress tracking with multi-stage visualization
- **Features**: File-level progress, overall progress, cancellation support
- **Display**: Progress bars, status text, conflict indicators

#### LogWidget
**Purpose**: Real-time activity logging with filtering and search
- **Features**: Color-coded log levels, automatic scrolling, search functionality
- **Integration**: Connects to Python logging system

### 3. Dialog Systems

#### SettingsDialog
**Purpose**: Comprehensive configuration interface with tabbed organization
- **Tabs**: General settings, conversion options, accessibility preferences
- **Features**: Live preview, validation, reset options

#### PreviewDialog
**Purpose**: Markdown preview with syntax highlighting and rendering
- **Features**: Split-view (raw/rendered), search, export options

#### FileViewerDialog  
**Purpose**: Multi-format file content viewer
- **Support**: Text files, images, structured data preview

## Integration Layer

### 1. External Libraries

#### MarkItDown Integration
- **Primary Library**: Microsoft MarkItDown for document conversion
- **Wrapper**: ConversionManager provides abstraction layer
- **Error Handling**: Comprehensive exception handling and recovery

#### PyQt6 Integration
- **UI Framework**: Complete PyQt6 ecosystem utilization
- **Threading**: QThread-based asynchronous operations
- **Signals/Slots**: Event-driven communication system

### 2. System Integration

#### Platform Support
- **Windows**: Native file associations, system theming
- **macOS**: System theme detection, native dialogs
- **Linux**: Desktop environment integration

#### Accessibility Integration
- **Screen Readers**: NVDA, JAWS, VoiceOver support
- **System Integration**: Platform accessibility APIs
- **Keyboard Navigation**: Complete keyboard control

## Data Flow Architecture

### 1. File Processing Pipeline

```
User Directory Selection
↓
Asynchronous File Scanning (FileManager)
↓  
File Validation & Type Detection
↓
UI Display Update (FileListWidget)
↓
User File Selection  
↓
Conversion Pipeline (ConversionManager)
├── File Validation
├── Conflict Detection & Resolution
├── MarkItDown Processing
├── Output Generation
└── Status Reporting
↓
Results Display & Logging
```

### 2. Event-Driven Communication

#### Signal/Slot Architecture
- **Inter-Component**: PyQt signals for decoupled communication
- **Progress Updates**: Real-time status propagation
- **Error Handling**: Centralized error event processing

#### State Management
- **File States**: Individual file conversion tracking
- **Application State**: Global state coordination
- **Configuration State**: User preference synchronization

## Performance & Optimization

### 1. Memory Management

#### MemoryOptimizer System
- **Automatic Cleanup**: Resource lifecycle management
- **Weak References**: Preventing memory leaks
- **Monitoring**: Real-time memory usage tracking

#### UI Optimization
- **ResponsivenessOptimizer**: UI thread performance management
- **Lazy Loading**: On-demand resource initialization
- **Batch Operations**: Efficient bulk processing

### 2. Asynchronous Operations

#### Threading Strategy
- **File Scanning**: Dedicated worker threads (FileScanWorker)
- **File Conversion**: Parallel processing (ConversionWorker)
- **UI Updates**: Thread-safe progress reporting

#### Resource Management
- **ThreadPool**: Controlled concurrency management
- **Memory Limits**: Configurable resource constraints
- **Cancellation**: Graceful operation termination

## Security & Quality

### 1. Security Features

#### Secure Storage
- **API Keys**: Encrypted credential storage
- **User Data**: Privacy-conscious data handling
- **File Access**: Validated file system operations

#### Input Validation
- **File Paths**: Path traversal protection
- **Configuration**: Input sanitization
- **External Data**: Safe parsing and handling

### 2. Quality Assurance

#### Error Handling
- **Comprehensive**: Multi-level exception handling
- **User-Friendly**: Meaningful error messages
- **Recovery**: Graceful degradation strategies

#### Logging System
- **Structured**: Consistent logging format
- **Configurable**: Adjustable log levels
- **Integration**: UI and file logging coordination

## Configuration Architecture

### 1. Configuration Layers

#### Application Configuration
- **Base Config**: Default application settings
- **User Config**: Personalized preferences
- **Session Config**: Runtime state management

#### Resource Configuration
- **Themes**: QSS stylesheet management
- **Translations**: JSON-based i18n resources
- **Assets**: Icon and resource organization

### 2. Persistence Strategy

#### Settings Storage
- **Qt Settings**: Window state and system integration
- **JSON Config**: Application-specific configuration
- **Secure Storage**: Encrypted sensitive data

## Extensibility & Modularity

### 1. Plugin Architecture Readiness

#### Manager Pattern
- **Service Managers**: Centralized capability management
- **Interface Abstraction**: Consistent service APIs
- **Dependency Injection**: Configurable service resolution

### 2. Internationalization Ready

#### Translation System
- **Complete Coverage**: All user-facing text
- **Cultural Adaptation**: Region-specific formatting
- **Extensible**: Easy addition of new languages

## Development & Maintenance

### 1. Code Organization

#### Module Structure
- **Separation of Concerns**: Clear layer boundaries
- **Cohesive Modules**: Related functionality grouping
- **Minimal Coupling**: Reduced inter-module dependencies

#### Design Patterns
- **Manager Pattern**: Service coordination
- **Observer Pattern**: Event-driven updates  
- **Strategy Pattern**: Configurable algorithms
- **Factory Pattern**: Object creation abstraction

### 2. Testing & Validation

#### Comprehensive Testing Suite
- **Unit Tests**: Individual component validation
- **Integration Tests**: Cross-component functionality
- **Accessibility Tests**: WCAG compliance verification
- **Performance Tests**: Memory and speed validation

## Future Architecture Considerations

### 1. Scalability Enhancements

#### Plugin System
- **Conversion Plugins**: Additional format support
- **UI Plugins**: Custom interface extensions
- **Service Plugins**: External service integration

#### Cloud Integration
- **Remote Processing**: Cloud-based conversion
- **Sync Services**: Cross-device configuration
- **Collaborative Features**: Shared conversion projects

### 2. Advanced Features

#### AI/ML Integration
- **Enhanced OCR**: Advanced text recognition
- **Content Analysis**: Intelligent document processing
- **User Experience**: Adaptive interface learning

This architecture provides a robust, scalable, and maintainable foundation for the MarkItDown GUI Converter, ensuring long-term viability and extensibility while maintaining high standards for user experience, accessibility, and performance.
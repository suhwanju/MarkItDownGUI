# Architecture Overview

Comprehensive guide to the MarkItDown GUI system architecture, design patterns, and component relationships.

## Table of Contents

- [System Overview](#system-overview)
- [Architectural Principles](#architectural-principles)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Integration Points](#integration-points)
- [Performance Considerations](#performance-considerations)
- [Security Architecture](#security-architecture)

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User Interface                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Main Window │  │   Dialogs   │  │   Widgets   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │ PyQt6 Signals/Slots
┌─────────────────┴───────────────────────────────────┐
│                 Business Logic                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Services   │  │   Models    │  │ Controllers │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │ Interface Contracts
┌─────────────────┴───────────────────────────────────┐
│                  Core Engine                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Converters  │  │ Config Mgr  │  │  Utilities  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │ System Interfaces
┌─────────────────┴───────────────────────────────────┐
│                External Systems                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ File System │  │ MarkItDown  │  │   OCR APIs  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend Layer
- **GUI Framework**: PyQt6 for native desktop interface
- **Layout Management**: Qt layouts and custom widgets
- **Styling**: Qt Style Sheets (QSS) and themes
- **Internationalization**: Qt translation system

#### Business Logic Layer
- **Architecture Pattern**: Model-View-Controller (MVC)
- **Service Layer**: Business logic encapsulation
- **Data Models**: Document and conversion state management
- **Event System**: Observer pattern with Qt signals/slots

#### Core Engine Layer
- **Conversion Engine**: MarkItDown library integration
- **Configuration**: YAML-based configuration management
- **Logging**: Structured logging with multiple outputs
- **Utilities**: File handling, validation, and processing

#### External Integration Layer
- **File System**: Cross-platform file operations
- **Document Libraries**: Format-specific processing
- **OCR Services**: Text recognition for images
- **System Services**: OS integration and notifications

## Architectural Principles

### 1. Separation of Concerns
- **UI Layer**: Only handles presentation and user interaction
- **Business Logic**: Manages application rules and workflows
- **Data Layer**: Handles data persistence and external integrations
- **Cross-Cutting**: Logging, configuration, and error handling

### 2. Dependency Inversion
```python
# Abstract interfaces define contracts
class IConverter(ABC):
    @abstractmethod
    def convert(self, input_file: Path, output_format: str) -> ConversionResult:
        pass

# Concrete implementations depend on abstractions
class PDFConverter(IConverter):
    def convert(self, input_file: Path, output_format: str) -> ConversionResult:
        # Implementation details
```

### 3. Single Responsibility Principle
Each component has a single, well-defined responsibility:
- **ConfigManager**: Configuration loading and validation
- **ConversionService**: Document conversion orchestration
- **FileWatcher**: File system monitoring
- **I18nManager**: Internationalization and localization

### 4. Open/Closed Principle
System is open for extension but closed for modification:
- **Plugin Architecture**: New converters can be added
- **Theme System**: Custom themes without core changes
- **Configuration**: New settings without code changes

## Component Architecture

### Core Components

#### 1. Application Core (`markitdown_gui/core/`)

```python
# Configuration Management
class ConfigManager:
    """Centralized configuration management"""
    def load_config(self) -> Config
    def save_config(self, config: Config) -> None
    def validate_config(self, config: Config) -> ValidationResult

# Logging System
class Logger:
    """Structured logging with multiple outputs"""
    def configure_logging(self, level: str, output: str) -> None
    def get_logger(self, name: str) -> logging.Logger

# Internationalization
class I18nManager:
    """Multi-language support"""
    def load_translations(self, language: str) -> None
    def translate(self, key: str, **kwargs) -> str
```

#### 2. User Interface (`markitdown_gui/ui/`)

```python
# Main Application Window
class MainWindow(QMainWindow):
    """Primary application interface"""
    def __init__(self, config_manager: ConfigManager)
    def setup_ui(self) -> None
    def connect_signals(self) -> None

# Custom Widgets
class FileListWidget(QListWidget):
    """File management and display"""
    file_added = pyqtSignal(str)
    file_removed = pyqtSignal(str)

class PreviewWidget(QWidget):
    """Document preview and editing"""
    content_changed = pyqtSignal(str)
```

#### 3. Business Logic (`markitdown_gui/services/`)

```python
# Conversion Service
class ConversionService:
    """Document conversion orchestration"""
    def __init__(self, config: Config, logger: Logger)
    def convert_file(self, file_path: Path) -> ConversionResult
    def batch_convert(self, files: List[Path]) -> BatchResult

# File Management Service
class FileService:
    """File operations and validation"""
    def validate_file(self, file_path: Path) -> ValidationResult
    def get_file_info(self, file_path: Path) -> FileInfo
```

#### 4. Data Models (`markitdown_gui/models/`)

```python
# Document Models
@dataclass
class Document:
    """Document representation"""
    path: Path
    format: str
    size: int
    metadata: Dict[str, Any]

@dataclass
class ConversionJob:
    """Conversion task representation"""
    id: str
    document: Document
    output_format: str
    settings: ConversionSettings
    status: JobStatus
```

### Component Relationships

#### Dependency Graph
```
MainWindow
├── ConversionService
│   ├── MarkItDownConverter
│   ├── ConfigManager
│   └── Logger
├── FileService
│   ├── FileValidator
│   └── FileWatcher
├── I18nManager
└── ThemeManager
    ├── StyleSheetLoader
    └── IconProvider
```

#### Communication Patterns
1. **Qt Signals/Slots**: UI component communication
2. **Service Injection**: Dependency injection for services
3. **Event Bus**: Loose coupling for cross-component events
4. **Observer Pattern**: State change notifications

## Data Flow

### Document Processing Flow

```
User Input (File Selection)
         ↓
File Validation & Metadata Extraction
         ↓
Conversion Job Creation
         ↓
┌─────────────────────────────────┐
│     Conversion Pipeline         │
│  ┌─────────────────────────┐    │
│  │  1. Format Detection    │    │
│  │  2. Converter Selection │    │
│  │  3. Preprocessing       │    │
│  │  4. Core Conversion     │    │
│  │  5. Post-processing     │    │
│  │  6. Output Generation   │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
         ↓
Result Handling & User Notification
         ↓
Output File Generation
```

### Configuration Flow

```
Application Startup
         ↓
Configuration Loading
    ┌─────────┴─────────┐
    │  Default Config   │
    │  User Config      │
    │  CLI Arguments    │
    │  Environment      │
    └─────────┬─────────┘
         ↓
Configuration Validation
         ↓
Configuration Merge & Resolution
         ↓
Service Configuration
         ↓
UI Initialization
```

### Event Flow

```
User Action (UI Event)
         ↓
Signal Emission
         ↓
Slot Handler (Controller)
         ↓
Business Logic (Service)
         ↓
Model Update
         ↓
Change Notification
         ↓
UI Update (View Refresh)
```

## Design Patterns

### 1. Model-View-Controller (MVC)

#### Implementation
```python
# Model: Data and business logic
class ConversionModel(QObject):
    data_changed = pyqtSignal()
    
    def __init__(self):
        self._jobs = []
    
    def add_job(self, job: ConversionJob):
        self._jobs.append(job)
        self.data_changed.emit()

# View: UI presentation
class ConversionView(QWidget):
    job_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def update_display(self, jobs: List[ConversionJob]):
        # Update UI with job data

# Controller: Coordination between Model and View
class ConversionController:
    def __init__(self, model: ConversionModel, view: ConversionView):
        self.model = model
        self.view = view
        self.connect_signals()
    
    def connect_signals(self):
        self.view.job_requested.connect(self.handle_job_request)
        self.model.data_changed.connect(self.update_view)
```

### 2. Observer Pattern

#### Event System
```python
class EventBus:
    """Central event dispatcher"""
    def __init__(self):
        self._subscribers = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable):
        self._subscribers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Any):
        for handler in self._subscribers[event_type]:
            handler(data)

# Usage
event_bus = EventBus()
event_bus.subscribe('file_converted', self.on_file_converted)
event_bus.publish('file_converted', conversion_result)
```

### 3. Strategy Pattern

#### Converter Selection
```python
class ConversionStrategy(ABC):
    @abstractmethod
    def convert(self, input_file: Path) -> ConversionResult:
        pass

class PDFConversionStrategy(ConversionStrategy):
    def convert(self, input_file: Path) -> ConversionResult:
        # PDF-specific conversion logic

class ConversionContext:
    def __init__(self):
        self._strategies = {
            '.pdf': PDFConversionStrategy(),
            '.docx': WordConversionStrategy(),
            '.pptx': PowerPointConversionStrategy(),
        }
    
    def convert(self, file_path: Path) -> ConversionResult:
        strategy = self._strategies.get(file_path.suffix.lower())
        if not strategy:
            raise UnsupportedFormatError(file_path.suffix)
        return strategy.convert(file_path)
```

### 4. Factory Pattern

#### Widget Creation
```python
class WidgetFactory:
    """Creates UI widgets based on configuration"""
    
    @staticmethod
    def create_widget(widget_type: str, config: Dict) -> QWidget:
        if widget_type == 'file_list':
            return FileListWidget(config)
        elif widget_type == 'preview':
            return PreviewWidget(config)
        elif widget_type == 'progress':
            return ProgressWidget(config)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")
```

### 5. Command Pattern

#### Action System
```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass

class ConvertFileCommand(Command):
    def __init__(self, service: ConversionService, file_path: Path):
        self.service = service
        self.file_path = file_path
        self.result = None
    
    def execute(self) -> None:
        self.result = self.service.convert_file(self.file_path)
    
    def undo(self) -> None:
        if self.result and self.result.output_file.exists():
            self.result.output_file.unlink()

class ActionManager:
    def __init__(self):
        self._history = []
    
    def execute(self, command: Command):
        command.execute()
        self._history.append(command)
    
    def undo_last(self):
        if self._history:
            command = self._history.pop()
            command.undo()
```

## Integration Points

### External System Integration

#### MarkItDown Library
```python
class MarkItDownAdapter:
    """Adapter for MarkItDown library"""
    
    def __init__(self):
        from markitdown import MarkItDown
        self.converter = MarkItDown()
    
    def convert(self, file_path: Path) -> str:
        result = self.converter.convert(str(file_path))
        return result.text_content
```

#### File System Integration
```python
class FileSystemWatcher:
    """Monitor file system changes"""
    
    def __init__(self):
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.on_file_changed)
    
    def watch_directory(self, path: Path):
        self.watcher.addPath(str(path))
    
    def on_file_changed(self, path: str):
        # Handle file changes
```

#### Plugin Architecture
```python
class PluginManager:
    """Dynamic plugin loading and management"""
    
    def __init__(self):
        self.plugins = []
    
    def load_plugins(self, plugin_dir: Path):
        for plugin_file in plugin_dir.glob('*.py'):
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'get_plugin'):
                plugin = module.get_plugin()
                self.plugins.append(plugin)
```

## Performance Considerations

### 1. Threading Model

#### Background Processing
```python
class ConversionWorker(QThread):
    """Background conversion processing"""
    
    progress_updated = pyqtSignal(int)
    conversion_completed = pyqtSignal(ConversionResult)
    
    def __init__(self, jobs: List[ConversionJob]):
        super().__init__()
        self.jobs = jobs
    
    def run(self):
        for i, job in enumerate(self.jobs):
            result = self.process_job(job)
            self.conversion_completed.emit(result)
            
            progress = int((i + 1) / len(self.jobs) * 100)
            self.progress_updated.emit(progress)
```

#### Thread Pool Management
```python
class ThreadPoolManager:
    """Manages worker thread pool"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []
    
    def submit_job(self, job: ConversionJob) -> Future:
        future = self.executor.submit(self.process_job, job)
        self.futures.append(future)
        return future
```

### 2. Memory Management

#### Resource Cleanup
```python
class ResourceManager:
    """Manages system resources and cleanup"""
    
    def __init__(self):
        self._temp_files = []
        self._open_files = []
    
    def cleanup(self):
        # Clean up temporary files
        for temp_file in self._temp_files:
            try:
                temp_file.unlink()
            except FileNotFoundError:
                pass
        
        # Close open files
        for file_handle in self._open_files:
            try:
                file_handle.close()
            except:
                pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

### 3. Caching Strategy

#### Result Caching
```python
class ConversionCache:
    """Cache conversion results for improved performance"""
    
    def __init__(self, max_size: int = 100):
        self.cache = LRUCache(max_size)
    
    def get_cache_key(self, file_path: Path, settings: ConversionSettings) -> str:
        file_hash = self.calculate_file_hash(file_path)
        settings_hash = hash(settings)
        return f"{file_hash}_{settings_hash}"
    
    def get(self, file_path: Path, settings: ConversionSettings) -> Optional[ConversionResult]:
        key = self.get_cache_key(file_path, settings)
        return self.cache.get(key)
    
    def put(self, file_path: Path, settings: ConversionSettings, result: ConversionResult):
        key = self.get_cache_key(file_path, settings)
        self.cache[key] = result
```

## Security Architecture

### 1. Input Validation

#### File Validation
```python
class SecurityValidator:
    """Security-focused file validation"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.html'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        # Extension validation
        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            return ValidationResult(False, "File type not allowed")
        
        # Size validation
        if file_path.stat().st_size > self.MAX_FILE_SIZE:
            return ValidationResult(False, "File too large")
        
        # Content validation
        if not self.validate_file_content(file_path):
            return ValidationResult(False, "Invalid file content")
        
        return ValidationResult(True, "Valid file")
```

### 2. Privilege Management

#### Sandboxing
```python
class SandboxManager:
    """Manages sandboxed execution environment"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='markitdown_sandbox_')
    
    def execute_in_sandbox(self, operation: Callable, *args) -> Any:
        # Change to sandbox directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            return operation(*args)
        finally:
            os.chdir(original_cwd)
```

### 3. Data Protection

#### Sensitive Data Handling
```python
class SecureDataHandler:
    """Handles sensitive data securely"""
    
    def scrub_metadata(self, document: Document) -> Document:
        """Remove sensitive metadata from document"""
        safe_metadata = {}
        allowed_keys = {'format', 'size', 'created_date'}
        
        for key, value in document.metadata.items():
            if key in allowed_keys:
                safe_metadata[key] = value
        
        return Document(
            path=document.path,
            format=document.format,
            size=document.size,
            metadata=safe_metadata
        )
```

---

**Related Documentation:**
- 🔧 [Development Setup](setup.md) - Environment configuration
- 📋 [Coding Standards](coding-standards.md) - Code quality guidelines
- 🧪 [Testing Guide](testing.md) - Testing strategies
- 🔌 [API Reference](../api/core.md) - Core API documentation
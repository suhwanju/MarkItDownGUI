# Plugin System API

## Overview

The MarkItDown GUI application features a comprehensive plugin system that allows extending functionality through custom converters, UI components, processors, and integrations. This document provides the complete API reference for developing and integrating plugins.

## Plugin Architecture

### Core Concepts
- **Plugin Interface**: Base classes defining plugin contracts
- **Plugin Discovery**: Automatic detection and loading of plugins
- **Lifecycle Management**: Plugin initialization, activation, and cleanup
- **Dependency Resolution**: Managing plugin dependencies and load order
- **Configuration Integration**: Plugin-specific settings and preferences
- **Event System**: Plugin integration with application events

### Plugin Types
- **Converter Plugins**: Custom file format converters
- **Processor Plugins**: Post-processing and enhancement filters
- **UI Plugins**: Custom user interface components
- **Export Plugins**: Alternative output formats and destinations
- **Integration Plugins**: External service integrations
- **Theme Plugins**: Custom visual themes and styling

## Base Plugin System

### Core Plugin Interface
```python
# markitdown_gui/core/plugin_system.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from enum import Enum
import importlib
import sys
import os

class PluginType(Enum):
    """Types of plugins supported by the system"""
    CONVERTER = "converter"
    PROCESSOR = "processor"
    UI_COMPONENT = "ui_component"
    EXPORTER = "exporter"
    INTEGRATION = "integration"
    THEME = "theme"

class PluginStatus(Enum):
    """Plugin status states"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVATED = "activated"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class PluginInfo:
    """Plugin metadata and information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    entry_point: str
    dependencies: List[str] = None
    min_app_version: str = "1.0.0"
    max_app_version: str = "*"
    config_schema: Optional[Dict] = None
    status: PluginStatus = PluginStatus.DISCOVERED
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class IPlugin(ABC):
    """Base interface for all plugins"""
    
    def __init__(self):
        self.info: Optional[PluginInfo] = None
        self.config: Dict[str, Any] = {}
        self.is_active = False
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Return plugin information"""
        pass
    
    @abstractmethod
    def initialize(self, app_context: 'ApplicationContext') -> bool:
        """Initialize the plugin with application context"""
        pass
    
    @abstractmethod
    def activate(self) -> bool:
        """Activate the plugin"""
        pass
    
    @abstractmethod
    def deactivate(self) -> bool:
        """Deactivate the plugin"""
        pass
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the plugin with settings"""
        self.config = config.copy()
        return True
    
    def get_config_schema(self) -> Optional[Dict]:
        """Return configuration schema for UI generation"""
        return None
    
    def validate_dependencies(self, available_plugins: List[str]) -> bool:
        """Validate that required dependencies are available"""
        if not self.info or not self.info.dependencies:
            return True
        
        for dependency in self.info.dependencies:
            if dependency not in available_plugins:
                return False
        return True

class ApplicationContext:
    """Context object passed to plugins for accessing application services"""
    
    def __init__(self, main_window, event_bus, file_manager, conversion_manager, config_manager):
        self.main_window = main_window
        self.event_bus = event_bus
        self.file_manager = file_manager
        self.conversion_manager = conversion_manager
        self.config_manager = config_manager
        self._services = {}
    
    def register_service(self, name: str, service: Any):
        """Register a service for plugin access"""
        self._services[name] = service
    
    def get_service(self, name: str) -> Any:
        """Get a registered service"""
        return self._services.get(name)
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all registered services"""
        return self._services.copy()

class PluginManager:
    """Manages plugin discovery, loading, and lifecycle"""
    
    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        self.plugins: Dict[str, IPlugin] = {}
        self.plugin_paths: List[str] = []
        self.plugin_configs: Dict[str, Dict] = {}
        self.load_order: List[str] = []
        
        # Default plugin directories
        self.add_plugin_path("plugins")
        self.add_plugin_path(os.path.expanduser("~/.markitdown-gui/plugins"))
    
    def add_plugin_path(self, path: str):
        """Add a directory to search for plugins"""
        if os.path.exists(path) and path not in self.plugin_paths:
            self.plugin_paths.append(path)
            if path not in sys.path:
                sys.path.insert(0, path)
    
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins in plugin paths"""
        discovered = []
        
        for plugin_path in self.plugin_paths:
            if not os.path.exists(plugin_path):
                continue
            
            for item in os.listdir(plugin_path):
                item_path = os.path.join(plugin_path, item)
                
                # Check for Python packages
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
                    plugin_info = self._load_plugin_info(item_path, item)
                    if plugin_info:
                        discovered.append(plugin_info)
                
                # Check for single Python files
                elif item.endswith('.py') and not item.startswith('__'):
                    plugin_name = item[:-3]
                    plugin_info = self._load_plugin_info(plugin_path, plugin_name)
                    if plugin_info:
                        discovered.append(plugin_info)
        
        return discovered
    
    def _load_plugin_info(self, path: str, name: str) -> Optional[PluginInfo]:
        """Load plugin information from plugin file/directory"""
        try:
            # Try to import the plugin module
            if path not in sys.path:
                sys.path.insert(0, path)
            
            module = importlib.import_module(name)
            
            # Look for plugin info
            if hasattr(module, 'PLUGIN_INFO'):
                info_dict = module.PLUGIN_INFO
                return PluginInfo(**info_dict)
            
            # Look for plugin class
            elif hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
                if issubclass(plugin_class, IPlugin):
                    temp_plugin = plugin_class()
                    return temp_plugin.get_info()
            
        except Exception as e:
            print(f"Error loading plugin info from {name}: {e}")
        
        return None
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            # Find plugin in discovered plugins
            plugin_info = None
            for path in self.plugin_paths:
                plugin_info = self._load_plugin_info(path, plugin_name)
                if plugin_info:
                    break
            
            if not plugin_info:
                return False
            
            # Import plugin module
            module = importlib.import_module(plugin_name)
            
            # Get plugin class
            if hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
                plugin_instance = plugin_class()
                
                # Initialize plugin
                if plugin_instance.initialize(self.app_context):
                    self.plugins[plugin_name] = plugin_instance
                    plugin_info.status = PluginStatus.LOADED
                    return True
            
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
        
        return False
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin"""
        if plugin_name not in self.plugins:
            if not self.load_plugin(plugin_name):
                return False
        
        plugin = self.plugins[plugin_name]
        
        # Check dependencies
        active_plugins = [name for name, p in self.plugins.items() if p.is_active]
        if not plugin.validate_dependencies(active_plugins):
            print(f"Plugin {plugin_name} has unmet dependencies")
            return False
        
        # Configure plugin
        config = self.plugin_configs.get(plugin_name, {})
        plugin.configure(config)
        
        # Activate plugin
        if plugin.activate():
            plugin.is_active = True
            if plugin.info:
                plugin.info.status = PluginStatus.ACTIVATED
            return True
        
        return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if plugin.deactivate():
                plugin.is_active = False
                if plugin.info:
                    plugin.info.status = PluginStatus.LOADED
                return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Get a plugin instance"""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[IPlugin]:
        """Get all plugins of a specific type"""
        return [p for p in self.plugins.values() 
                if p.info and p.info.plugin_type == plugin_type and p.is_active]
    
    def get_active_plugins(self) -> Dict[str, IPlugin]:
        """Get all active plugins"""
        return {name: plugin for name, plugin in self.plugins.items() if plugin.is_active}
    
    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]):
        """Configure a plugin"""
        self.plugin_configs[plugin_name] = config
        
        if plugin_name in self.plugins:
            self.plugins[plugin_name].configure(config)
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin (useful for development)"""
        # Deactivate and remove
        if plugin_name in self.plugins:
            self.deactivate_plugin(plugin_name)
            del self.plugins[plugin_name]
        
        # Reload module
        if plugin_name in sys.modules:
            importlib.reload(sys.modules[plugin_name])
        
        # Load again
        return self.load_plugin(plugin_name)
```

## Converter Plugins

### Converter Plugin Interface
```python
# markitdown_gui/plugins/interfaces/converter.py
from abc import abstractmethod
from typing import List, Dict, Any, Optional, BinaryIO, TextIO
from dataclasses import dataclass
from ..core.plugin_system import IPlugin, PluginType, PluginInfo

@dataclass
class ConversionResult:
    """Result of a conversion operation"""
    success: bool
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

@dataclass
class ConversionOptions:
    """Options for conversion operations"""
    preserve_formatting: bool = True
    extract_images: bool = True
    include_metadata: bool = True
    output_format: str = "markdown"
    custom_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_options is None:
            self.custom_options = {}

class IConverterPlugin(IPlugin):
    """Interface for converter plugins"""
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions (e.g., ['.docx', '.pdf'])"""
        pass
    
    @abstractmethod
    def get_supported_mime_types(self) -> List[str]:
        """Return list of supported MIME types"""
        pass
    
    @abstractmethod
    def can_convert(self, file_path: str) -> bool:
        """Check if this plugin can convert the given file"""
        pass
    
    @abstractmethod
    def convert_file(self, file_path: str, options: ConversionOptions) -> ConversionResult:
        """Convert a file to markdown"""
        pass
    
    @abstractmethod
    def convert_stream(self, input_stream: BinaryIO, file_extension: str, 
                      options: ConversionOptions) -> ConversionResult:
        """Convert from an input stream"""
        pass
    
    def get_conversion_options_schema(self) -> Dict[str, Any]:
        """Return JSON schema for conversion options UI"""
        return {
            "type": "object",
            "properties": {
                "preserve_formatting": {
                    "type": "boolean",
                    "title": "Preserve Formatting",
                    "description": "Maintain original document formatting",
                    "default": True
                },
                "extract_images": {
                    "type": "boolean", 
                    "title": "Extract Images",
                    "description": "Extract and convert embedded images",
                    "default": True
                },
                "include_metadata": {
                    "type": "boolean",
                    "title": "Include Metadata",
                    "description": "Include document metadata in output",
                    "default": True
                }
            }
        }
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate file before conversion"""
        return {
            "is_valid": True,
            "file_size": os.path.getsize(file_path),
            "estimated_time": 0,
            "warnings": []
        }

# Example converter plugin implementation
class CustomPDFConverter(IConverterPlugin):
    """Example PDF converter plugin"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="custom_pdf_converter",
            version="1.0.0",
            description="Custom PDF converter with OCR support",
            author="Plugin Developer",
            plugin_type=PluginType.CONVERTER,
            entry_point="custom_pdf_converter.CustomPDFConverter",
            dependencies=["tesseract", "poppler"]
        )
    
    def initialize(self, app_context) -> bool:
        self.app_context = app_context
        # Initialize OCR engine, check dependencies, etc.
        return True
    
    def activate(self) -> bool:
        # Register with conversion manager
        conversion_manager = self.app_context.conversion_manager
        conversion_manager.register_converter(self)
        return True
    
    def deactivate(self) -> bool:
        # Unregister from conversion manager
        conversion_manager = self.app_context.conversion_manager
        conversion_manager.unregister_converter(self)
        return True
    
    def get_supported_extensions(self) -> List[str]:
        return ['.pdf']
    
    def get_supported_mime_types(self) -> List[str]:
        return ['application/pdf']
    
    def can_convert(self, file_path: str) -> bool:
        return file_path.lower().endswith('.pdf')
    
    def convert_file(self, file_path: str, options: ConversionOptions) -> ConversionResult:
        try:
            # Custom PDF conversion logic here
            # This would use OCR, text extraction, etc.
            
            content = self._extract_text_from_pdf(file_path, options)
            metadata = self._extract_metadata(file_path) if options.include_metadata else None
            
            return ConversionResult(
                success=True,
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def convert_stream(self, input_stream: BinaryIO, file_extension: str, 
                      options: ConversionOptions) -> ConversionResult:
        # Implementation for stream conversion
        pass
    
    def _extract_text_from_pdf(self, file_path: str, options: ConversionOptions) -> str:
        # Custom PDF text extraction implementation
        return "# Extracted PDF Content\n\nPDF content goes here..."
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        # Extract PDF metadata
        return {
            "title": "Document Title",
            "author": "Document Author",
            "creation_date": "2025-01-13"
        }
```

## Processor Plugins

### Post-Processing Plugin Interface
```python
# markitdown_gui/plugins/interfaces/processor.py
from abc import abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..core.plugin_system import IPlugin, PluginType

@dataclass
class ProcessingContext:
    """Context information for processing operations"""
    source_file_path: str
    original_content: str
    metadata: Optional[Dict[str, Any]] = None
    conversion_options: Optional[Dict[str, Any]] = None

@dataclass
class ProcessingResult:
    """Result of a processing operation"""
    success: bool
    processed_content: Optional[str] = None
    modified_metadata: Optional[Dict[str, Any]] = None
    processing_notes: List[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.processing_notes is None:
            self.processing_notes = []

class IProcessorPlugin(IPlugin):
    """Interface for content processor plugins"""
    
    @abstractmethod
    def get_processing_order(self) -> int:
        """Return processing order (lower numbers process first)"""
        pass
    
    @abstractmethod
    def can_process(self, context: ProcessingContext) -> bool:
        """Check if this processor can handle the given content"""
        pass
    
    @abstractmethod
    def process_content(self, context: ProcessingContext) -> ProcessingResult:
        """Process the markdown content"""
        pass
    
    def get_processing_options_schema(self) -> Dict[str, Any]:
        """Return JSON schema for processing options"""
        return {
            "type": "object",
            "properties": {}
        }
    
    def supports_batch_processing(self) -> bool:
        """Whether this processor supports batch operations"""
        return False
    
    def process_batch(self, contexts: List[ProcessingContext]) -> List[ProcessingResult]:
        """Process multiple documents in batch (if supported)"""
        if self.supports_batch_processing():
            # Override in subclass for efficient batch processing
            pass
        else:
            # Fallback to individual processing
            return [self.process_content(context) for context in contexts]

# Example processor plugin implementations
class LinkValidatorProcessor(IProcessorPlugin):
    """Validates and fixes markdown links"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="link_validator",
            version="1.0.0",
            description="Validates and fixes markdown links",
            author="Plugin Developer",
            plugin_type=PluginType.PROCESSOR,
            entry_point="link_validator.LinkValidatorProcessor"
        )
    
    def initialize(self, app_context) -> bool:
        self.app_context = app_context
        return True
    
    def activate(self) -> bool:
        # Register with processing manager
        processing_manager = self.app_context.get_service('processing_manager')
        if processing_manager:
            processing_manager.register_processor(self)
        return True
    
    def deactivate(self) -> bool:
        processing_manager = self.app_context.get_service('processing_manager')
        if processing_manager:
            processing_manager.unregister_processor(self)
        return True
    
    def get_processing_order(self) -> int:
        return 100  # Process after basic formatting but before final cleanup
    
    def can_process(self, context: ProcessingContext) -> bool:
        # Check if content contains markdown links
        return '[' in context.original_content and '](' in context.original_content
    
    def process_content(self, context: ProcessingContext) -> ProcessingResult:
        try:
            processed_content = self._validate_and_fix_links(context.original_content)
            
            return ProcessingResult(
                success=True,
                processed_content=processed_content,
                processing_notes=["Validated and fixed markdown links"]
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e)
            )
    
    def _validate_and_fix_links(self, content: str) -> str:
        import re
        
        # Simple link validation and fixing
        # In a real implementation, this would be more sophisticated
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def fix_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Basic URL validation and fixing
            if not url.startswith(('http://', 'https://', 'mailto:', '#')):
                if '.' in url and not url.startswith('/'):
                    url = 'https://' + url
            
            return f'[{text}]({url})'
        
        return re.sub(link_pattern, fix_link, content)

class TableOfContentsProcessor(IProcessorPlugin):
    """Generates table of contents for markdown documents"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="toc_generator",
            version="1.0.0", 
            description="Generates table of contents for markdown documents",
            author="Plugin Developer",
            plugin_type=PluginType.PROCESSOR,
            entry_point="toc_generator.TableOfContentsProcessor"
        )
    
    def initialize(self, app_context) -> bool:
        return True
    
    def activate(self) -> bool:
        return True
    
    def deactivate(self) -> bool:
        return True
    
    def get_processing_order(self) -> int:
        return 200  # Process after link validation
    
    def can_process(self, context: ProcessingContext) -> bool:
        # Check if content has headings
        return '#' in context.original_content
    
    def process_content(self, context: ProcessingContext) -> ProcessingResult:
        try:
            content_with_toc = self._generate_toc(context.original_content)
            
            return ProcessingResult(
                success=True,
                processed_content=content_with_toc,
                processing_notes=["Generated table of contents"]
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e)
            )
    
    def _generate_toc(self, content: str) -> str:
        import re
        
        # Extract headings
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        headings = []
        
        for line in content.split('\n'):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                anchor = re.sub(r'[^a-zA-Z0-9\-_]', '', title.lower().replace(' ', '-'))
                headings.append((level, title, anchor))
        
        if not headings:
            return content
        
        # Generate TOC
        toc_lines = ['## Table of Contents', '']
        for level, title, anchor in headings:
            indent = '  ' * (level - 1)
            toc_lines.append(f'{indent}- [{title}](#{anchor})')
        
        toc_lines.append('')
        
        # Insert TOC after first heading or at beginning
        content_lines = content.split('\n')
        first_heading_index = 0
        
        for i, line in enumerate(content_lines):
            if re.match(r'^#{1,6}\s+', line):
                first_heading_index = i + 1
                break
        
        # Insert TOC
        result_lines = (content_lines[:first_heading_index] + 
                       toc_lines + 
                       content_lines[first_heading_index:])
        
        return '\n'.join(result_lines)
```

## UI Plugins

### UI Component Plugin Interface
```python
# markitdown_gui/plugins/interfaces/ui_component.py
from abc import abstractmethod
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import QWidget, QAction, QMenu
from ..core.plugin_system import IPlugin, PluginType

class IUIComponentPlugin(IPlugin):
    """Interface for UI component plugins"""
    
    @abstractmethod
    def get_component_name(self) -> str:
        """Return unique component name"""
        pass
    
    @abstractmethod
    def get_component_category(self) -> str:
        """Return component category (menu, toolbar, panel, dialog, etc.)"""
        pass
    
    @abstractmethod
    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        """Create the main widget for this component"""
        pass
    
    def get_menu_actions(self) -> List[QAction]:
        """Return menu actions to add to application menus"""
        return []
    
    def get_toolbar_actions(self) -> List[QAction]:
        """Return toolbar actions"""
        return []
    
    def get_context_menu_actions(self) -> List[QAction]:
        """Return context menu actions"""
        return []
    
    def get_status_bar_widgets(self) -> List[QWidget]:
        """Return widgets to add to status bar"""
        return []
    
    def integrate_with_main_window(self, main_window) -> bool:
        """Integrate component with main window"""
        return True
    
    def get_docking_preferences(self) -> Dict[str, Any]:
        """Return preferences for dockable widgets"""
        return {
            "dock_area": "right",  # left, right, top, bottom
            "initial_size": (300, 400),
            "resizable": True,
            "closable": True,
            "floatable": True
        }

# Example UI plugin implementation
class FilePreviewPlugin(IUIComponentPlugin):
    """Plugin that adds file preview capability"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="file_preview",
            version="1.0.0",
            description="Provides file preview functionality",
            author="Plugin Developer",
            plugin_type=PluginType.UI_COMPONENT,
            entry_point="file_preview.FilePreviewPlugin"
        )
    
    def initialize(self, app_context) -> bool:
        self.app_context = app_context
        self.preview_widget = None
        return True
    
    def activate(self) -> bool:
        # Create and integrate the preview widget
        main_window = self.app_context.main_window
        self.integrate_with_main_window(main_window)
        return True
    
    def deactivate(self) -> bool:
        # Remove preview widget from main window
        if self.preview_widget:
            self.preview_widget.setParent(None)
            self.preview_widget.deleteLater()
            self.preview_widget = None
        return True
    
    def get_component_name(self) -> str:
        return "file_preview"
    
    def get_component_category(self) -> str:
        return "panel"
    
    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QSplitter
        
        widget = QWidget(parent)
        layout = QVBoxLayout()
        
        # File info section
        self.file_info_label = QLabel("No file selected")
        layout.addWidget(self.file_info_label)
        
        # Preview area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        widget.setLayout(layout)
        
        # Connect to file selection events
        file_event_manager = self.app_context.get_service('file_event_manager')
        if file_event_manager:
            file_event_manager.file_selected.connect(self.preview_file)
        
        return widget
    
    def integrate_with_main_window(self, main_window) -> bool:
        # Create the preview widget
        self.preview_widget = self.create_widget()
        
        # Add as dockable widget
        from PyQt6.QtWidgets import QDockWidget
        from PyQt6.QtCore import Qt
        
        dock = QDockWidget("File Preview", main_window)
        dock.setWidget(self.preview_widget)
        main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        
        return True
    
    def preview_file(self, file_path: str):
        """Preview the selected file"""
        import os
        
        if not os.path.exists(file_path):
            self.file_info_label.setText("File not found")
            self.preview_text.clear()
            return
        
        # Update file info
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        self.file_info_label.setText(f"{file_name} ({file_size} bytes)")
        
        # Preview content based on file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            # Text-based files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Limit preview size
                    if len(content) > 10000:
                        content = content[:10000] + "\n\n... (truncated)"
                    self.preview_text.setPlainText(content)
            except Exception as e:
                self.preview_text.setPlainText(f"Error reading file: {e}")
        
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Image files
            self.preview_text.setHtml(f'<img src="{file_path}" style="max-width: 100%; max-height: 400px;">')
        
        else:
            # Other file types
            self.preview_text.setPlainText(f"Preview not available for {file_ext} files")

class AdvancedSettingsPlugin(IUIComponentPlugin):
    """Plugin that adds advanced settings dialog"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="advanced_settings",
            version="1.0.0",
            description="Advanced configuration options",
            author="Plugin Developer",
            plugin_type=PluginType.UI_COMPONENT,
            entry_point="advanced_settings.AdvancedSettingsPlugin"
        )
    
    def initialize(self, app_context) -> bool:
        self.app_context = app_context
        return True
    
    def activate(self) -> bool:
        # Add menu item to Tools menu
        main_window = self.app_context.main_window
        tools_menu = main_window.findChild(QMenu, "tools_menu")
        if tools_menu:
            actions = self.get_menu_actions()
            for action in actions:
                tools_menu.addAction(action)
        return True
    
    def deactivate(self) -> bool:
        # Remove menu items
        return True
    
    def get_component_name(self) -> str:
        return "advanced_settings"
    
    def get_component_category(self) -> str:
        return "dialog"
    
    def create_widget(self, parent: Optional[QWidget] = None) -> QWidget:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QDialogButtonBox
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("Advanced Settings")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        # Tab widget for different setting categories
        tab_widget = QTabWidget()
        
        # Add different setting tabs
        tab_widget.addTab(self._create_conversion_settings_tab(), "Conversion")
        tab_widget.addTab(self._create_performance_settings_tab(), "Performance")
        tab_widget.addTab(self._create_advanced_settings_tab(), "Advanced")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        return dialog
    
    def get_menu_actions(self) -> List[QAction]:
        from PyQt6.QtGui import QAction
        
        action = QAction("Advanced Settings...", None)
        action.triggered.connect(self.show_settings_dialog)
        return [action]
    
    def show_settings_dialog(self):
        """Show the advanced settings dialog"""
        dialog = self.create_widget(self.app_context.main_window)
        dialog.exec()
    
    def _create_conversion_settings_tab(self) -> QWidget:
        from PyQt6.QtWidgets import QWidget, QFormLayout, QCheckBox, QSpinBox, QComboBox
        
        widget = QWidget()
        layout = QFormLayout()
        
        # Conversion options
        layout.addRow("Parallel conversions:", QSpinBox())
        layout.addRow("Timeout (seconds):", QSpinBox())
        layout.addRow("Error handling:", QComboBox())
        layout.addRow("Auto-retry failed:", QCheckBox())
        
        widget.setLayout(layout)
        return widget
    
    def _create_performance_settings_tab(self) -> QWidget:
        from PyQt6.QtWidgets import QWidget, QFormLayout, QSlider, QLabel
        from PyQt6.QtCore import Qt
        
        widget = QWidget()
        layout = QFormLayout()
        
        # Performance settings
        memory_slider = QSlider(Qt.Orientation.Horizontal)
        memory_slider.setRange(256, 4096)
        layout.addRow("Memory limit (MB):", memory_slider)
        
        cpu_slider = QSlider(Qt.Orientation.Horizontal)
        cpu_slider.setRange(1, 16)
        layout.addRow("CPU threads:", cpu_slider)
        
        widget.setLayout(layout)
        return widget
    
    def _create_advanced_settings_tab(self) -> QWidget:
        from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox
        
        widget = QWidget()
        layout = QFormLayout()
        
        # Advanced options
        layout.addRow("Custom temp directory:", QLineEdit())
        layout.addRow("Debug logging:", QCheckBox())
        layout.addRow("Plugin development mode:", QCheckBox())
        
        widget.setLayout(layout)
        return widget
```

## Export Plugins

### Export Plugin Interface
```python
# markitdown_gui/plugins/interfaces/exporter.py
from abc import abstractmethod
from typing import List, Dict, Any, Optional, BinaryIO
from dataclasses import dataclass
from ..core.plugin_system import IPlugin, PluginType

@dataclass
class ExportOptions:
    """Options for export operations"""
    output_format: str
    destination: str
    include_metadata: bool = True
    compress_output: bool = False
    custom_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_options is None:
            self.custom_options = {}

@dataclass
class ExportResult:
    """Result of an export operation"""
    success: bool
    output_path: Optional[str] = None
    exported_files: List[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.exported_files is None:
            self.exported_files = []

class IExportPlugin(IPlugin):
    """Interface for export plugins"""
    
    @abstractmethod
    def get_export_name(self) -> str:
        """Return human-readable export name"""
        pass
    
    @abstractmethod
    def get_export_description(self) -> str:
        """Return export description"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return supported output formats"""
        pass
    
    @abstractmethod
    def export_single_file(self, content: str, metadata: Dict[str, Any], 
                          options: ExportOptions) -> ExportResult:
        """Export a single markdown file"""
        pass
    
    @abstractmethod
    def export_multiple_files(self, files: List[Dict[str, Any]], 
                             options: ExportOptions) -> ExportResult:
        """Export multiple markdown files"""
        pass
    
    def supports_batch_export(self) -> bool:
        """Whether this exporter supports batch operations"""
        return True
    
    def get_export_options_schema(self) -> Dict[str, Any]:
        """Return JSON schema for export options"""
        return {
            "type": "object",
            "properties": {
                "include_metadata": {
                    "type": "boolean",
                    "title": "Include Metadata",
                    "default": True
                },
                "compress_output": {
                    "type": "boolean",
                    "title": "Compress Output",
                    "default": False
                }
            }
        }
    
    def validate_export_options(self, options: ExportOptions) -> Dict[str, Any]:
        """Validate export options"""
        return {"is_valid": True, "errors": []}

# Example export plugin implementations
class HTMLExportPlugin(IExportPlugin):
    """Export markdown to HTML format"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="html_exporter",
            version="1.0.0",
            description="Export markdown to HTML format",
            author="Plugin Developer",
            plugin_type=PluginType.EXPORTER,
            entry_point="html_exporter.HTMLExportPlugin",
            dependencies=["markdown", "pygments"]
        )
    
    def initialize(self, app_context) -> bool:
        self.app_context = app_context
        return True
    
    def activate(self) -> bool:
        export_manager = self.app_context.get_service('export_manager')
        if export_manager:
            export_manager.register_exporter(self)
        return True
    
    def deactivate(self) -> bool:
        export_manager = self.app_context.get_service('export_manager')
        if export_manager:
            export_manager.unregister_exporter(self)
        return True
    
    def get_export_name(self) -> str:
        return "HTML Export"
    
    def get_export_description(self) -> str:
        return "Export markdown files to HTML with syntax highlighting"
    
    def get_supported_formats(self) -> List[str]:
        return ["html"]
    
    def export_single_file(self, content: str, metadata: Dict[str, Any], 
                          options: ExportOptions) -> ExportResult:
        try:
            html_content = self._convert_to_html(content, metadata, options)
            
            # Write HTML file
            output_path = options.destination
            if not output_path.endswith('.html'):
                output_path += '.html'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return ExportResult(
                success=True,
                output_path=output_path,
                exported_files=[output_path]
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def export_multiple_files(self, files: List[Dict[str, Any]], 
                             options: ExportOptions) -> ExportResult:
        try:
            exported_files = []
            
            for file_data in files:
                content = file_data['content']
                metadata = file_data.get('metadata', {})
                file_name = file_data['name']
                
                # Generate output path
                base_name = os.path.splitext(file_name)[0]
                output_path = os.path.join(options.destination, f"{base_name}.html")
                
                # Convert to HTML
                html_content = self._convert_to_html(content, metadata, options)
                
                # Write file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                exported_files.append(output_path)
            
            return ExportResult(
                success=True,
                exported_files=exported_files
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def _convert_to_html(self, content: str, metadata: Dict[str, Any], 
                        options: ExportOptions) -> str:
        import markdown
        from markdown.extensions import codehilite, toc, meta
        
        # Configure markdown processor
        md = markdown.Markdown(extensions=[
            'codehilite',
            'toc',
            'meta',
            'tables',
            'fenced_code'
        ])
        
        # Convert to HTML
        html_body = md.convert(content)
        
        # Create complete HTML document
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        pre {{ background-color: #f6f8fa; padding: 1em; border-radius: 6px; }}
        code {{ background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 1em; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    {metadata_section}
    {content}
</body>
</html>
        """
        
        # Generate metadata section
        metadata_html = ""
        if options.include_metadata and metadata:
            metadata_html = "<div class='metadata'>"
            metadata_html += "<h2>Document Information</h2>"
            metadata_html += "<ul>"
            for key, value in metadata.items():
                metadata_html += f"<li><strong>{key}:</strong> {value}</li>"
            metadata_html += "</ul>"
            metadata_html += "</div>"
        
        # Format final HTML
        title = metadata.get('title', 'Converted Document')
        return html_template.format(
            title=title,
            metadata_section=metadata_html,
            content=html_body
        )

class PDFExportPlugin(IExportPlugin):
    """Export markdown to PDF format"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="pdf_exporter",
            version="1.0.0",
            description="Export markdown to PDF format",
            author="Plugin Developer",
            plugin_type=PluginType.EXPORTER,
            entry_point="pdf_exporter.PDFExportPlugin",
            dependencies=["weasyprint", "markdown"]
        )
    
    def initialize(self, app_context) -> bool:
        return True
    
    def activate(self) -> bool:
        return True
    
    def deactivate(self) -> bool:
        return True
    
    def get_export_name(self) -> str:
        return "PDF Export"
    
    def get_export_description(self) -> str:
        return "Export markdown files to PDF format"
    
    def get_supported_formats(self) -> List[str]:
        return ["pdf"]
    
    def export_single_file(self, content: str, metadata: Dict[str, Any], 
                          options: ExportOptions) -> ExportResult:
        try:
            # Convert markdown to HTML first
            html_content = self._markdown_to_html(content, metadata, options)
            
            # Convert HTML to PDF
            output_path = options.destination
            if not output_path.endswith('.pdf'):
                output_path += '.pdf'
            
            self._html_to_pdf(html_content, output_path)
            
            return ExportResult(
                success=True,
                output_path=output_path,
                exported_files=[output_path]
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                error_message=str(e)
            )
    
    def export_multiple_files(self, files: List[Dict[str, Any]], 
                             options: ExportOptions) -> ExportResult:
        # Implementation for batch PDF export
        pass
    
    def _markdown_to_html(self, content: str, metadata: Dict[str, Any], 
                         options: ExportOptions) -> str:
        # Convert markdown to HTML (similar to HTML exporter)
        pass
    
    def _html_to_pdf(self, html_content: str, output_path: str):
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Create PDF from HTML
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        css = CSS(string='''
            @page {
                margin: 2cm;
                size: A4;
            }
            body {
                font-family: "DejaVu Sans", sans-serif;
                line-height: 1.6;
            }
        ''', font_config=font_config)
        
        html.write_pdf(output_path, stylesheets=[css], font_config=font_config)
```

## Plugin Testing

### Plugin Testing Framework
```python
# tests/test_plugins.py
import pytest
import tempfile
import os
from markitdown_gui.core.plugin_system import PluginManager, ApplicationContext
from markitdown_gui.plugins.interfaces.converter import IConverterPlugin, ConversionOptions

class TestPluginSystem:
    
    @pytest.fixture
    def mock_app_context(self):
        """Create mock application context for testing"""
        context = ApplicationContext(
            main_window=None,
            event_bus=None,
            file_manager=None,
            conversion_manager=None,
            config_manager=None
        )
        return context
    
    @pytest.fixture
    def plugin_manager(self, mock_app_context):
        """Create plugin manager for testing"""
        return PluginManager(mock_app_context)
    
    def test_plugin_discovery(self, plugin_manager, tmp_path):
        """Test plugin discovery functionality"""
        # Create test plugin
        plugin_dir = tmp_path / "test_plugin"
        plugin_dir.mkdir()
        
        plugin_file = plugin_dir / "__init__.py"
        plugin_file.write_text("""
from markitdown_gui.plugins.interfaces.converter import IConverterPlugin
from markitdown_gui.core.plugin_system import PluginInfo, PluginType

PLUGIN_INFO = {
    'name': 'test_converter',
    'version': '1.0.0',
    'description': 'Test converter plugin',
    'author': 'Test Author',
    'plugin_type': PluginType.CONVERTER,
    'entry_point': 'test_plugin.TestConverter'
}

class Plugin(IConverterPlugin):
    def get_info(self):
        return PluginInfo(**PLUGIN_INFO)
    
    def initialize(self, app_context):
        return True
    
    def activate(self):
        return True
    
    def deactivate(self):
        return True
    
    def get_supported_extensions(self):
        return ['.test']
    
    def get_supported_mime_types(self):
        return ['text/test']
    
    def can_convert(self, file_path):
        return file_path.endswith('.test')
    
    def convert_file(self, file_path, options):
        pass
    
    def convert_stream(self, input_stream, file_extension, options):
        pass
        """)
        
        # Add to plugin path
        plugin_manager.add_plugin_path(str(tmp_path))
        
        # Discover plugins
        discovered = plugin_manager.discover_plugins()
        
        assert len(discovered) == 1
        assert discovered[0].name == 'test_converter'
        assert discovered[0].plugin_type == PluginType.CONVERTER
    
    def test_plugin_loading(self, plugin_manager, tmp_path):
        """Test plugin loading functionality"""
        # Create and discover plugin (similar to above)
        # ... 
        
        # Load plugin
        success = plugin_manager.load_plugin('test_plugin')
        assert success
        
        # Check plugin is loaded
        plugin = plugin_manager.get_plugin('test_plugin')
        assert plugin is not None
        assert isinstance(plugin, IConverterPlugin)
    
    def test_plugin_activation(self, plugin_manager, tmp_path):
        """Test plugin activation functionality"""
        # Create, discover, and load plugin
        # ...
        
        # Activate plugin
        success = plugin_manager.activate_plugin('test_plugin')
        assert success
        
        # Check plugin is active
        plugin = plugin_manager.get_plugin('test_plugin')
        assert plugin.is_active
        
        # Get active plugins by type
        converters = plugin_manager.get_plugins_by_type(PluginType.CONVERTER)
        assert len(converters) == 1
    
    def test_converter_plugin_functionality(self):
        """Test converter plugin functionality"""
        # Create test converter
        from markitdown_gui.plugins.interfaces.converter import ConversionResult
        
        class TestConverter(IConverterPlugin):
            def get_info(self):
                return PluginInfo(
                    name="test",
                    version="1.0.0",
                    description="Test",
                    author="Test",
                    plugin_type=PluginType.CONVERTER,
                    entry_point="test"
                )
            
            def initialize(self, app_context):
                return True
            
            def activate(self):
                return True
            
            def deactivate(self):
                return True
            
            def get_supported_extensions(self):
                return ['.test']
            
            def get_supported_mime_types(self):
                return ['text/test']
            
            def can_convert(self, file_path):
                return file_path.endswith('.test')
            
            def convert_file(self, file_path, options):
                return ConversionResult(
                    success=True,
                    content="# Test Content\n\nConverted from test file"
                )
            
            def convert_stream(self, input_stream, file_extension, options):
                return ConversionResult(
                    success=True,
                    content="# Stream Content\n\nConverted from stream"
                )
        
        converter = TestConverter()
        
        # Test supported extensions
        assert '.test' in converter.get_supported_extensions()
        
        # Test can_convert
        assert converter.can_convert('file.test')
        assert not converter.can_convert('file.txt')
        
        # Test conversion
        result = converter.convert_file('test.test', ConversionOptions())
        assert result.success
        assert '# Test Content' in result.content
```

## Related Documentation

- 🔧 [Core API](core.md) - Core functionality reference
- 🧩 [Components API](components.md) - UI component reference
- ⚙️ [Configuration API](configuration.md) - Settings management
- 🎯 [Event System API](events.md) - Event handling reference
- 🏗️ [Architecture Overview](../developer/architecture.md) - System design

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
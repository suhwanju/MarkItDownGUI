# Event System API

## Overview

The MarkItDown GUI application uses a comprehensive event system based on PyQt6 signals and slots, providing a decoupled architecture for handling user interactions, system events, and application state changes.

## Core Event Architecture

### Event Categories
- **File Events**: File system operations and changes
- **Conversion Events**: Document conversion lifecycle
- **UI Events**: User interface interactions
- **System Events**: Application lifecycle and settings
- **Progress Events**: Operation progress tracking
- **Error Events**: Error handling and reporting

### Event Flow Pattern
```
User Action → Signal Emission → Event Processing → State Update → UI Refresh
```

## Event System Implementation

### Base Event Classes

#### Application Events
```python
# markitdown_gui/core/events.py
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BaseEvent:
    """Base event class for all application events"""
    event_type: str
    timestamp: datetime
    source: str
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'data': self.data or {}
        }

class EventBus(QObject):
    """Central event bus for application-wide event handling"""
    
    # Global application events
    application_started = pyqtSignal()
    application_closing = pyqtSignal()
    settings_changed = pyqtSignal(dict)  # setting_name -> value
    theme_changed = pyqtSignal(str)      # theme_name
    language_changed = pyqtSignal(str)   # language_code
    
    # File system events
    directory_selected = pyqtSignal(str)           # directory_path
    files_discovered = pyqtSignal(list)           # list of file paths
    file_selection_changed = pyqtSignal(list)     # list of selected files
    
    # Conversion events
    conversion_started = pyqtSignal(list)         # list of files to convert
    conversion_progress = pyqtSignal(int, int)    # current, total
    file_converted = pyqtSignal(str, bool, str)   # file_path, success, result/error
    conversion_completed = pyqtSignal(bool, dict) # success, results_summary
    conversion_cancelled = pyqtSignal()
    
    # Error events
    error_occurred = pyqtSignal(str, str, dict)   # error_type, message, context
    warning_issued = pyqtSignal(str, dict)        # message, context
    
    # UI events
    ui_action_triggered = pyqtSignal(str, dict)   # action_name, parameters
    status_message_requested = pyqtSignal(str, int) # message, timeout_ms
    
    def __init__(self):
        super().__init__()
        self._event_history = []
        self._max_history = 1000
    
    def emit_event(self, event: BaseEvent):
        """Emit a custom event and log it"""
        self._log_event(event)
        
        # Route to appropriate signal based on event type
        if event.event_type.startswith('file_'):
            self._handle_file_event(event)
        elif event.event_type.startswith('conversion_'):
            self._handle_conversion_event(event)
        elif event.event_type.startswith('error_'):
            self._handle_error_event(event)
        elif event.event_type.startswith('ui_'):
            self._handle_ui_event(event)
    
    def _log_event(self, event: BaseEvent):
        """Log event to history"""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_event_history(self, event_type_filter: Optional[str] = None) -> list:
        """Get event history, optionally filtered by type"""
        if event_type_filter:
            return [e for e in self._event_history if e.event_type == event_type_filter]
        return self._event_history.copy()

# Global event bus instance
event_bus = EventBus()
```

### File System Events

#### File Management Events
```python
# markitdown_gui/core/file_events.py
from PyQt6.QtCore import QObject, pyqtSignal, QFileSystemWatcher
from typing import List, Optional
import os

class FileEventManager(QObject):
    """Manages file system related events"""
    
    # Directory events
    directory_changed = pyqtSignal(str)              # directory_path
    directory_selected = pyqtSignal(str)             # directory_path
    directory_scan_started = pyqtSignal(str)         # directory_path
    directory_scan_completed = pyqtSignal(str, list) # directory_path, files_found
    
    # File discovery events
    files_found = pyqtSignal(list)                   # list of file_info dicts
    supported_files_filtered = pyqtSignal(list)     # list of supported files
    file_count_changed = pyqtSignal(int)            # total_file_count
    
    # File selection events
    file_selected = pyqtSignal(str)                  # file_path
    file_deselected = pyqtSignal(str)                # file_path
    selection_cleared = pyqtSignal()
    all_files_selected = pyqtSignal()
    selection_inverted = pyqtSignal()
    
    # File validation events
    file_validated = pyqtSignal(str, bool, str)      # file_path, is_valid, reason
    validation_completed = pyqtSignal(dict)          # validation_summary
    
    def __init__(self):
        super().__init__()
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.directoryChanged.connect(self.directory_changed)
        self.current_directory = ""
        self.discovered_files = []
        self.selected_files = []
    
    def set_directory(self, directory_path: str):
        """Set the current directory and start monitoring"""
        if os.path.exists(directory_path):
            # Remove old directory from watcher
            if self.current_directory:
                self.file_watcher.removePath(self.current_directory)
            
            # Add new directory to watcher
            self.current_directory = directory_path
            self.file_watcher.addPath(directory_path)
            
            # Emit directory selection event
            self.directory_selected.emit(directory_path)
    
    def scan_directory(self, directory_path: str, recursive: bool = True):
        """Scan directory for supported files"""
        self.directory_scan_started.emit(directory_path)
        
        found_files = []
        try:
            if recursive:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_info = self._get_file_info(file_path)
                        if file_info:
                            found_files.append(file_info)
            else:
                for item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item)
                    if os.path.isfile(item_path):
                        file_info = self._get_file_info(item_path)
                        if file_info:
                            found_files.append(file_info)
            
            self.discovered_files = found_files
            self.directory_scan_completed.emit(directory_path, found_files)
            self.files_found.emit(found_files)
            self.file_count_changed.emit(len(found_files))
            
        except Exception as e:
            event_bus.error_occurred.emit("file_scan_error", str(e), {
                'directory': directory_path,
                'recursive': recursive
            })
    
    def _get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information dictionary"""
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': os.path.splitext(file_path)[1].lower(),
                'is_supported': self._is_supported_file(file_path)
            }
        except Exception:
            return None
    
    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file type is supported for conversion"""
        supported_extensions = {
            '.docx', '.pptx', '.xlsx', '.xls',  # Office
            '.pdf',                              # PDF
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',  # Images
            '.mp3', '.wav',                      # Audio
            '.html', '.htm', '.csv', '.json', '.xml', '.txt',  # Text/Web
            '.zip',                              # Archive
            '.epub'                              # E-book
        }
        
        extension = os.path.splitext(file_path)[1].lower()
        return extension in supported_extensions
    
    def select_file(self, file_path: str):
        """Select a file"""
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
            self.file_selected.emit(file_path)
    
    def deselect_file(self, file_path: str):
        """Deselect a file"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self.file_deselected.emit(file_path)
    
    def select_all_files(self):
        """Select all discovered files"""
        self.selected_files = [f['path'] for f in self.discovered_files if f['is_supported']]
        self.all_files_selected.emit()
    
    def clear_selection(self):
        """Clear all file selections"""
        self.selected_files.clear()
        self.selection_cleared.emit()
    
    def get_selected_files(self) -> List[str]:
        """Get list of selected file paths"""
        return self.selected_files.copy()

# Global file event manager
file_event_manager = FileEventManager()
```

### Conversion Events

#### Conversion Process Events
```python
# markitdown_gui/core/conversion_events.py
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ConversionResult:
    """Result of a file conversion operation"""
    file_path: str
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    file_size_original: int = 0
    file_size_converted: int = 0
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ConversionEventManager(QObject):
    """Manages conversion process events"""
    
    # Conversion lifecycle events
    conversion_queued = pyqtSignal(list)              # files_to_convert
    conversion_started = pyqtSignal(int)              # total_file_count
    conversion_paused = pyqtSignal()
    conversion_resumed = pyqtSignal()
    conversion_cancelled = pyqtSignal(str)            # cancellation_reason
    conversion_completed = pyqtSignal(dict)           # conversion_summary
    
    # Individual file events
    file_conversion_started = pyqtSignal(str)         # file_path
    file_conversion_progress = pyqtSignal(str, int)   # file_path, percentage
    file_conversion_completed = pyqtSignal(object)    # ConversionResult
    file_conversion_failed = pyqtSignal(str, str)     # file_path, error_message
    
    # Batch progress events
    batch_progress_updated = pyqtSignal(int, int, float)  # completed, total, percentage
    batch_stats_updated = pyqtSignal(dict)            # statistics_dict
    
    # Quality events
    conversion_quality_checked = pyqtSignal(str, dict) # file_path, quality_metrics
    post_processing_started = pyqtSignal(str)         # file_path
    post_processing_completed = pyqtSignal(str, bool) # file_path, success
    
    def __init__(self):
        super().__init__()
        self.current_batch = []
        self.completed_conversions = []
        self.failed_conversions = []
        self.batch_start_time = None
        self.total_files = 0
        self.completed_files = 0
        
        # Progress reporting timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._emit_progress_update)
        self.progress_timer.setInterval(500)  # Update every 500ms
    
    def start_conversion_batch(self, file_paths: List[str]):
        """Start a batch conversion process"""
        self.current_batch = file_paths.copy()
        self.completed_conversions.clear()
        self.failed_conversions.clear()
        self.total_files = len(file_paths)
        self.completed_files = 0
        self.batch_start_time = datetime.now()
        
        # Emit events
        self.conversion_queued.emit(file_paths)
        self.conversion_started.emit(self.total_files)
        
        # Start progress reporting
        self.progress_timer.start()
    
    def report_file_conversion_start(self, file_path: str):
        """Report that file conversion has started"""
        self.file_conversion_started.emit(file_path)
    
    def report_file_conversion_progress(self, file_path: str, percentage: int):
        """Report file conversion progress"""
        self.file_conversion_progress.emit(file_path, percentage)
    
    def report_file_conversion_completed(self, result: ConversionResult):
        """Report successful file conversion"""
        self.completed_conversions.append(result)
        self.completed_files += 1
        
        # Emit individual file completion
        self.file_conversion_completed.emit(result)
        
        # Check if batch is complete
        if self.completed_files >= self.total_files:
            self._complete_batch()
    
    def report_file_conversion_failed(self, file_path: str, error_message: str):
        """Report failed file conversion"""
        failed_result = ConversionResult(
            file_path=file_path,
            success=False,
            error_message=error_message
        )
        
        self.failed_conversions.append(failed_result)
        self.completed_files += 1
        
        # Emit individual file failure
        self.file_conversion_failed.emit(file_path, error_message)
        
        # Check if batch is complete
        if self.completed_files >= self.total_files:
            self._complete_batch()
    
    def cancel_conversion(self, reason: str = "User cancelled"):
        """Cancel the current conversion batch"""
        self.progress_timer.stop()
        self.conversion_cancelled.emit(reason)
    
    def pause_conversion(self):
        """Pause the current conversion"""
        self.progress_timer.stop()
        self.conversion_paused.emit()
    
    def resume_conversion(self):
        """Resume a paused conversion"""
        self.progress_timer.start()
        self.conversion_resumed.emit()
    
    def _complete_batch(self):
        """Complete the current batch conversion"""
        self.progress_timer.stop()
        
        # Calculate summary statistics
        batch_end_time = datetime.now()
        total_time = (batch_end_time - self.batch_start_time).total_seconds()
        
        summary = {
            'total_files': self.total_files,
            'successful_conversions': len(self.completed_conversions),
            'failed_conversions': len(self.failed_conversions),
            'success_rate': (len(self.completed_conversions) / self.total_files) * 100,
            'total_time_seconds': total_time,
            'average_time_per_file': total_time / self.total_files if self.total_files > 0 else 0,
            'completed_results': [r.to_dict() for r in self.completed_conversions],
            'failed_results': [r.to_dict() for r in self.failed_conversions]
        }
        
        self.conversion_completed.emit(summary)
    
    def _emit_progress_update(self):
        """Emit periodic progress updates"""
        if self.total_files > 0:
            percentage = (self.completed_files / self.total_files) * 100
            
            # Calculate statistics
            current_time = datetime.now()
            elapsed_time = (current_time - self.batch_start_time).total_seconds()
            
            stats = {
                'elapsed_time': elapsed_time,
                'files_per_second': self.completed_files / elapsed_time if elapsed_time > 0 else 0,
                'estimated_remaining': ((self.total_files - self.completed_files) / 
                                      (self.completed_files / elapsed_time)) if elapsed_time > 0 and self.completed_files > 0 else 0
            }
            
            self.batch_progress_updated.emit(self.completed_files, self.total_files, percentage)
            self.batch_stats_updated.emit(stats)

# Global conversion event manager
conversion_event_manager = ConversionEventManager()
```

### Progress Events

#### Progress Tracking System
```python
# markitdown_gui/core/progress_events.py
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ProgressInfo:
    """Progress information structure"""
    operation_id: str
    operation_name: str
    current_value: int
    maximum_value: int
    percentage: float
    status_message: str
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    is_indeterminate: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation_id': self.operation_id,
            'operation_name': self.operation_name,
            'current_value': self.current_value,
            'maximum_value': self.maximum_value,
            'percentage': self.percentage,
            'status_message': self.status_message,
            'start_time': self.start_time.isoformat(),
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'is_indeterminate': self.is_indeterminate
        }

class ProgressEventManager(QObject):
    """Manages progress tracking and reporting events"""
    
    # Progress lifecycle events
    operation_started = pyqtSignal(str, str)          # operation_id, operation_name
    operation_completed = pyqtSignal(str, bool)       # operation_id, success
    operation_cancelled = pyqtSignal(str)             # operation_id
    
    # Progress update events
    progress_updated = pyqtSignal(object)             # ProgressInfo object
    status_changed = pyqtSignal(str, str)             # operation_id, status_message
    indeterminate_progress = pyqtSignal(str, bool)    # operation_id, is_indeterminate
    
    # Time estimation events
    time_estimate_updated = pyqtSignal(str, object)   # operation_id, estimated_completion
    remaining_time_changed = pyqtSignal(str, int)     # operation_id, seconds_remaining
    
    def __init__(self):
        super().__init__()
        self.active_operations: Dict[str, ProgressInfo] = {}
        
        # Timer for updating time estimates
        self.estimation_timer = QTimer()
        self.estimation_timer.timeout.connect(self._update_time_estimates)
        self.estimation_timer.setInterval(1000)  # Update every second
        self.estimation_timer.start()
    
    def start_operation(self, operation_id: str, operation_name: str, 
                       maximum_value: int = 100, is_indeterminate: bool = False):
        """Start tracking a new operation"""
        progress_info = ProgressInfo(
            operation_id=operation_id,
            operation_name=operation_name,
            current_value=0,
            maximum_value=maximum_value,
            percentage=0.0,
            status_message="Starting...",
            start_time=datetime.now(),
            is_indeterminate=is_indeterminate
        )
        
        self.active_operations[operation_id] = progress_info
        self.operation_started.emit(operation_id, operation_name)
        self.progress_updated.emit(progress_info)
    
    def update_progress(self, operation_id: str, current_value: int, 
                       status_message: Optional[str] = None):
        """Update progress for an operation"""
        if operation_id not in self.active_operations:
            return
        
        progress_info = self.active_operations[operation_id]
        progress_info.current_value = current_value
        
        if not progress_info.is_indeterminate and progress_info.maximum_value > 0:
            progress_info.percentage = (current_value / progress_info.maximum_value) * 100
        
        if status_message:
            progress_info.status_message = status_message
            self.status_changed.emit(operation_id, status_message)
        
        # Update estimated completion time
        self._calculate_estimated_completion(progress_info)
        
        self.progress_updated.emit(progress_info)
    
    def set_indeterminate(self, operation_id: str, is_indeterminate: bool):
        """Set whether an operation has indeterminate progress"""
        if operation_id in self.active_operations:
            self.active_operations[operation_id].is_indeterminate = is_indeterminate
            self.indeterminate_progress.emit(operation_id, is_indeterminate)
    
    def complete_operation(self, operation_id: str, success: bool = True):
        """Mark an operation as completed"""
        if operation_id in self.active_operations:
            progress_info = self.active_operations[operation_id]
            progress_info.current_value = progress_info.maximum_value
            progress_info.percentage = 100.0
            progress_info.status_message = "Completed" if success else "Failed"
            
            self.progress_updated.emit(progress_info)
            self.operation_completed.emit(operation_id, success)
            
            # Remove from active operations after a delay
            QTimer.singleShot(2000, lambda: self._remove_operation(operation_id))
    
    def cancel_operation(self, operation_id: str):
        """Cancel an active operation"""
        if operation_id in self.active_operations:
            progress_info = self.active_operations[operation_id]
            progress_info.status_message = "Cancelled"
            
            self.progress_updated.emit(progress_info)
            self.operation_cancelled.emit(operation_id)
            self._remove_operation(operation_id)
    
    def get_operation_info(self, operation_id: str) -> Optional[ProgressInfo]:
        """Get progress information for an operation"""
        return self.active_operations.get(operation_id)
    
    def get_active_operations(self) -> Dict[str, ProgressInfo]:
        """Get all active operations"""
        return self.active_operations.copy()
    
    def _calculate_estimated_completion(self, progress_info: ProgressInfo):
        """Calculate estimated completion time"""
        if progress_info.is_indeterminate or progress_info.current_value <= 0:
            return
        
        elapsed_time = datetime.now() - progress_info.start_time
        progress_rate = progress_info.current_value / elapsed_time.total_seconds()
        
        if progress_rate > 0:
            remaining_items = progress_info.maximum_value - progress_info.current_value
            remaining_seconds = remaining_items / progress_rate
            progress_info.estimated_completion = datetime.now() + timedelta(seconds=remaining_seconds)
            
            self.time_estimate_updated.emit(progress_info.operation_id, 
                                          progress_info.estimated_completion)
            self.remaining_time_changed.emit(progress_info.operation_id, 
                                           int(remaining_seconds))
    
    def _update_time_estimates(self):
        """Update time estimates for all active operations"""
        for progress_info in self.active_operations.values():
            if not progress_info.is_indeterminate:
                self._calculate_estimated_completion(progress_info)
    
    def _remove_operation(self, operation_id: str):
        """Remove an operation from tracking"""
        if operation_id in self.active_operations:
            del self.active_operations[operation_id]

# Global progress event manager
progress_event_manager = ProgressEventManager()
```

### Error and Status Events

#### Error Handling System
```python
# markitdown_gui/core/error_events.py
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    FILE_SYSTEM = "file_system"
    CONVERSION = "conversion"
    NETWORK = "network"
    VALIDATION = "validation"
    USER_INPUT = "user_input"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    source_file: Optional[str] = None
    source_function: Optional[str] = None
    stack_trace: Optional[str] = None
    user_message: Optional[str] = None
    recovery_suggestions: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_id': self.error_id,
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'details': self.details,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'source_file': self.source_file,
            'source_function': self.source_function,
            'stack_trace': self.stack_trace,
            'user_message': self.user_message,
            'recovery_suggestions': self.recovery_suggestions
        }

class ErrorEventManager(QObject):
    """Manages error reporting and handling events"""
    
    # Error reporting events
    error_occurred = pyqtSignal(object)               # ErrorInfo object
    warning_issued = pyqtSignal(str, str, dict)       # message, category, context
    info_message = pyqtSignal(str, dict)              # message, context
    
    # Error handling events
    error_acknowledged = pyqtSignal(str)              # error_id
    error_dismissed = pyqtSignal(str)                 # error_id
    recovery_attempted = pyqtSignal(str, str)         # error_id, recovery_action
    
    # Status events
    status_changed = pyqtSignal(str, str)             # status_type, message
    notification_requested = pyqtSignal(str, str, int) # title, message, duration_ms
    
    def __init__(self):
        super().__init__()
        self.error_history: List[ErrorInfo] = []
        self.max_history = 100
        self.error_counter = 0
    
    def report_error(self, message: str, 
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    details: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None,
                    user_message: Optional[str] = None,
                    recovery_suggestions: Optional[List[str]] = None) -> str:
        """Report an error and return error ID"""
        
        self.error_counter += 1
        error_id = f"ERR_{self.error_counter:06d}"
        
        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            severity=severity,
            category=category,
            message=message,
            details=details,
            context=context or {},
            user_message=user_message,
            recovery_suggestions=recovery_suggestions or []
        )
        
        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        # Emit appropriate event
        if severity == ErrorSeverity.WARNING:
            self.warning_issued.emit(message, category.value, context or {})
        elif severity == ErrorSeverity.INFO:
            self.info_message.emit(message, context or {})
        else:
            self.error_occurred.emit(error_info)
        
        return error_id
    
    def report_file_error(self, file_path: str, operation: str, error_message: str,
                         details: Optional[str] = None) -> str:
        """Report a file-related error"""
        return self.report_error(
            message=f"File operation failed: {operation}",
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.ERROR,
            details=details or error_message,
            context={'file_path': file_path, 'operation': operation},
            user_message=f"Failed to {operation}: {os.path.basename(file_path)}",
            recovery_suggestions=[
                "Check if the file exists and is accessible",
                "Verify file permissions",
                "Try refreshing the file list"
            ]
        )
    
    def report_conversion_error(self, file_path: str, error_message: str) -> str:
        """Report a conversion-related error"""
        return self.report_error(
            message=f"Conversion failed for {os.path.basename(file_path)}",
            category=ErrorCategory.CONVERSION,
            severity=ErrorSeverity.ERROR,
            details=error_message,
            context={'file_path': file_path},
            user_message=f"Could not convert {os.path.basename(file_path)} to Markdown",
            recovery_suggestions=[
                "Check if the file is corrupted",
                "Verify the file format is supported",
                "Try converting the file individually"
            ]
        )
    
    def report_validation_error(self, field_name: str, value: Any, 
                              validation_message: str) -> str:
        """Report a validation error"""
        return self.report_error(
            message=f"Validation failed for {field_name}",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            details=validation_message,
            context={'field': field_name, 'value': str(value)},
            user_message=f"Invalid {field_name}: {validation_message}",
            recovery_suggestions=[
                "Check the input format",
                "Refer to the help documentation"
            ]
        )
    
    def acknowledge_error(self, error_id: str):
        """Mark an error as acknowledged"""
        self.error_acknowledged.emit(error_id)
    
    def dismiss_error(self, error_id: str):
        """Dismiss an error"""
        self.error_dismissed.emit(error_id)
    
    def attempt_recovery(self, error_id: str, recovery_action: str):
        """Attempt error recovery"""
        self.recovery_attempted.emit(error_id, recovery_action)
    
    def update_status(self, status_type: str, message: str):
        """Update application status"""
        self.status_changed.emit(status_type, message)
    
    def show_notification(self, title: str, message: str, duration_ms: int = 3000):
        """Request a notification to be shown"""
        self.notification_requested.emit(title, message, duration_ms)
    
    def get_error_history(self, category_filter: Optional[ErrorCategory] = None,
                         severity_filter: Optional[ErrorSeverity] = None) -> List[ErrorInfo]:
        """Get filtered error history"""
        filtered_history = self.error_history
        
        if category_filter:
            filtered_history = [e for e in filtered_history if e.category == category_filter]
        
        if severity_filter:
            filtered_history = [e for e in filtered_history if e.severity == severity_filter]
        
        return filtered_history
    
    def get_error_by_id(self, error_id: str) -> Optional[ErrorInfo]:
        """Get specific error by ID"""
        for error_info in self.error_history:
            if error_info.error_id == error_id:
                return error_info
        return None

# Global error event manager
error_event_manager = ErrorEventManager()
```

## Event Integration Examples

### UI Component Event Integration
```python
# markitdown_gui/ui/components/file_list_widget.py
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from ...core.events import event_bus
from ...core.file_events import file_event_manager

class FileListWidget(QListWidget):
    """File list widget with integrated event handling"""
    
    def __init__(self):
        super().__init__()
        self.setup_event_connections()
        self.setup_ui()
    
    def setup_event_connections(self):
        """Connect to relevant event signals"""
        # File discovery events
        file_event_manager.files_found.connect(self.populate_file_list)
        file_event_manager.file_selected.connect(self.select_file_item)
        file_event_manager.file_deselected.connect(self.deselect_file_item)
        file_event_manager.selection_cleared.connect(self.clearSelection)
        
        # UI events
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def populate_file_list(self, file_list):
        """Populate list with discovered files"""
        self.clear()
        
        for file_info in file_list:
            item = QListWidgetItem()
            item.setText(file_info['name'])
            item.setData(Qt.ItemDataRole.UserRole, file_info)
            
            # Set appropriate icon based on file type
            icon = self.get_file_type_icon(file_info['extension'])
            item.setIcon(icon)
            
            # Disable unsupported files
            if not file_info['is_supported']:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            
            self.addItem(item)
    
    def on_selection_changed(self):
        """Handle selection changes"""
        selected_files = []
        for item in self.selectedItems():
            file_info = item.data(Qt.ItemDataRole.UserRole)
            if file_info:
                selected_files.append(file_info['path'])
        
        # Update file event manager
        file_event_manager.selected_files = selected_files
        
        # Emit UI event
        event_bus.ui_action_triggered.emit('file_selection_changed', {
            'selected_count': len(selected_files),
            'files': selected_files
        })
    
    def on_item_double_clicked(self, item):
        """Handle double-click on file item"""
        file_info = item.data(Qt.ItemDataRole.UserRole)
        if file_info:
            event_bus.ui_action_triggered.emit('file_double_clicked', {
                'file_path': file_info['path'],
                'file_info': file_info
            })
```

### Main Application Event Coordination
```python
# markitdown_gui/ui/main_window.py
from PyQt6.QtWidgets import QMainWindow
from ..core.events import event_bus
from ..core.file_events import file_event_manager
from ..core.conversion_events import conversion_event_manager
from ..core.progress_events import progress_event_manager
from ..core.error_events import error_event_manager

class MainWindow(QMainWindow):
    """Main window with comprehensive event integration"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_event_connections()
    
    def setup_event_connections(self):
        """Set up all event connections"""
        # File events
        file_event_manager.directory_selected.connect(self.on_directory_selected)
        file_event_manager.files_found.connect(self.on_files_discovered)
        
        # Conversion events
        conversion_event_manager.conversion_started.connect(self.on_conversion_started)
        conversion_event_manager.file_conversion_completed.connect(self.on_file_converted)
        conversion_event_manager.conversion_completed.connect(self.on_conversion_completed)
        
        # Progress events
        progress_event_manager.progress_updated.connect(self.on_progress_updated)
        progress_event_manager.operation_completed.connect(self.on_operation_completed)
        
        # Error events
        error_event_manager.error_occurred.connect(self.on_error_occurred)
        error_event_manager.notification_requested.connect(self.show_notification)
        
        # Application events
        event_bus.theme_changed.connect(self.on_theme_changed)
        event_bus.language_changed.connect(self.on_language_changed)
    
    def on_directory_selected(self, directory_path):
        """Handle directory selection"""
        self.status_bar.showMessage(f"Selected directory: {directory_path}")
        self.directory_label.setText(directory_path)
    
    def on_files_discovered(self, file_list):
        """Handle file discovery"""
        supported_count = sum(1 for f in file_list if f['is_supported'])
        total_count = len(file_list)
        
        message = f"Found {supported_count} supported files ({total_count} total)"
        self.status_bar.showMessage(message)
    
    def on_conversion_started(self, total_files):
        """Handle conversion start"""
        self.progress_widget.setVisible(True)
        self.convert_button.setText("Cancel")
        self.convert_button.clicked.disconnect()
        self.convert_button.clicked.connect(self.cancel_conversion)
    
    def on_file_converted(self, result):
        """Handle individual file conversion completion"""
        if result.success:
            self.log_widget.add_success_message(f"Converted: {result.file_path}")
        else:
            self.log_widget.add_error_message(f"Failed: {result.file_path} - {result.error_message}")
    
    def on_conversion_completed(self, summary):
        """Handle batch conversion completion"""
        self.progress_widget.setVisible(False)
        self.convert_button.setText("Convert Selected")
        self.convert_button.clicked.disconnect()
        self.convert_button.clicked.connect(self.start_conversion)
        
        # Show completion notification
        success_rate = summary['success_rate']
        message = f"Conversion completed: {success_rate:.1f}% success rate"
        self.show_notification("Conversion Complete", message)
    
    def on_progress_updated(self, progress_info):
        """Handle progress updates"""
        self.progress_widget.setValue(progress_info.current_value)
        self.progress_widget.setMaximum(progress_info.maximum_value)
        self.status_bar.showMessage(progress_info.status_message)
    
    def on_error_occurred(self, error_info):
        """Handle error events"""
        self.show_error_dialog(error_info)
    
    def on_theme_changed(self, theme_name):
        """Handle theme changes"""
        self.apply_theme(theme_name)
    
    def on_language_changed(self, language_code):
        """Handle language changes"""
        self.retranslate_ui()
```

## Event Testing

### Event System Testing
```python
# tests/test_events.py
import pytest
from PyQt6.QtCore import QSignalSpy
from markitdown_gui.core.events import event_bus, BaseEvent
from markitdown_gui.core.file_events import file_event_manager
from markitdown_gui.core.conversion_events import conversion_event_manager

class TestEventSystem:
    def test_event_bus_basic_functionality(self, qtbot):
        """Test basic event bus operations"""
        # Create signal spy
        spy = QSignalSpy(event_bus.application_started)
        
        # Emit signal
        event_bus.application_started.emit()
        
        # Verify signal was received
        assert len(spy) == 1
    
    def test_file_event_manager(self, qtbot, tmp_path):
        """Test file event manager"""
        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Set up signal spy
        spy = QSignalSpy(file_event_manager.files_found)
        
        # Scan directory
        file_event_manager.scan_directory(str(tmp_path), recursive=False)
        
        # Verify files were found
        qtbot.waitUntil(lambda: len(spy) > 0, timeout=1000)
        assert len(spy) == 1
        
        # Check file list
        files_found = spy[0][0]  # First argument of first signal emission
        assert len(files_found) == 1
        assert files_found[0]['name'] == 'test.txt'
    
    def test_conversion_event_flow(self, qtbot):
        """Test conversion event flow"""
        # Set up signal spies
        start_spy = QSignalSpy(conversion_event_manager.conversion_started)
        complete_spy = QSignalSpy(conversion_event_manager.conversion_completed)
        
        # Start a mock conversion
        test_files = ['file1.txt', 'file2.txt']
        conversion_event_manager.start_conversion_batch(test_files)
        
        # Verify start event
        assert len(start_spy) == 1
        assert start_spy[0][0] == len(test_files)  # total file count
        
        # Simulate file completions
        for file_path in test_files:
            result = ConversionResult(file_path=file_path, success=True)
            conversion_event_manager.report_file_conversion_completed(result)
        
        # Wait for completion event
        qtbot.waitUntil(lambda: len(complete_spy) > 0, timeout=1000)
        assert len(complete_spy) == 1
        
        # Check summary
        summary = complete_spy[0][0]
        assert summary['total_files'] == 2
        assert summary['successful_conversions'] == 2
    
    def test_error_event_handling(self, qtbot):
        """Test error event handling"""
        # Set up signal spy
        spy = QSignalSpy(error_event_manager.error_occurred)
        
        # Report an error
        error_id = error_event_manager.report_error(
            "Test error",
            category=ErrorCategory.CONVERSION,
            severity=ErrorSeverity.ERROR
        )
        
        # Verify error event
        assert len(spy) == 1
        error_info = spy[0][0]
        assert error_info.error_id == error_id
        assert error_info.message == "Test error"
        assert error_info.category == ErrorCategory.CONVERSION
```

## Related Documentation

- 🔧 [Core API](core.md) - Core functionality reference
- 🧩 [Components API](components.md) - UI component reference
- ⚙️ [Configuration API](configuration.md) - Settings management
- 🏗️ [Architecture Overview](../developer/architecture.md) - System design

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
# GUI Components API Reference

Complete API reference for MarkItDown GUI user interface components and widgets.

## Table of Contents

- [Overview](#overview)
- [Main Window Components](#main-window-components)
- [Dialog Components](#dialog-components)
- [Widget Components](#widget-components)
- [Custom Controls](#custom-controls)
- [Theme System](#theme-system)
- [Event Handling](#event-handling)
- [Accessibility Features](#accessibility-features)

## Overview

The GUI Components API provides a comprehensive set of user interface elements built on PyQt6. All components follow consistent design patterns and accessibility guidelines.

### Component Hierarchy
```
MainWindow
├── MenuBar
├── ToolBar
├── CentralWidget
│   ├── FileListWidget
│   ├── PreviewWidget
│   └── OutputWidget
├── StatusBar
└── Dialogs
    ├── PreferencesDialog
    ├── AboutDialog
    └── ProgressDialog
```

### Import Structure
```python
# Main components
from markitdown_gui.ui.main_window import MainWindow
from markitdown_gui.ui.dialogs import (
    PreferencesDialog,
    AboutDialog,
    ProgressDialog
)

# Custom widgets
from markitdown_gui.ui.widgets import (
    FileListWidget,
    PreviewWidget,
    OutputWidget,
    ProgressWidget
)

# Theme system
from markitdown_gui.ui.theme_manager import ThemeManager
```

## Main Window Components

### MainWindow
```python
class MainWindow(QMainWindow):
    """Main application window with integrated components.
    
    The MainWindow serves as the primary interface, coordinating between
    different components and managing application state.
    
    Signals:
        file_dropped (List[Path]): Files dropped onto window
        conversion_requested (List[Path], str): Conversion request
        settings_changed (Dict[str, Any]): Settings modification
    """
    
    # Signals
    file_dropped = pyqtSignal(list)  # List[Path]
    conversion_requested = pyqtSignal(list, str)  # files, output_format
    settings_changed = pyqtSignal(dict)  # settings dict
    
    def __init__(self, config_manager: 'ConfigManager') -> None:
        """Initialize main window.
        
        Args:
            config_manager: Application configuration manager
        """
        super().__init__()
        self._config_manager = config_manager
        self._setup_ui()
        self._setup_drag_drop()
    
    def show_progress_dialog(self, title: str, maximum: int = 100) -> 'ProgressDialog':
        """Show progress dialog for long operations.
        
        Args:
            title: Dialog title
            maximum: Maximum progress value
            
        Returns:
            ProgressDialog instance
            
        Example:
            >>> progress = main_window.show_progress_dialog("Converting Files", 100)
            >>> progress.set_progress(50, "Processing file 5 of 10")
        """
        progress_dialog = ProgressDialog(title, maximum, self)
        progress_dialog.show()
        return progress_dialog
    
    def add_files(self, file_paths: List[Path]) -> None:
        """Add files to the conversion queue.
        
        Args:
            file_paths: List of file paths to add
        """
        self.file_list_widget.add_files(file_paths)
    
    def clear_files(self) -> None:
        """Clear all files from the queue."""
        self.file_list_widget.clear()
    
    def get_selected_files(self) -> List[Path]:
        """Get currently selected files.
        
        Returns:
            List of selected file paths
        """
        return self.file_list_widget.get_selected_files()
    
    def set_preview_content(self, content: str, format_type: str = 'markdown') -> None:
        """Update preview widget content.
        
        Args:
            content: Content to preview
            format_type: Content format ('markdown', 'html', 'text')
        """
        self.preview_widget.set_content(content, format_type)
    
    def update_status(self, message: str, timeout: int = 0) -> None:
        """Update status bar message.
        
        Args:
            message: Status message
            timeout: Message timeout in milliseconds (0 = permanent)
        """
        self.statusBar().showMessage(message, timeout)
    
    def apply_theme(self, theme_name: str) -> None:
        """Apply theme to main window and all components.
        
        Args:
            theme_name: Theme name ('light', 'dark', 'auto')
        """
        theme_manager = ThemeManager()
        stylesheet = theme_manager.get_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.
        
        Args:
            event: Close event
        """
        # Save window geometry
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # Clean up resources
        self._cleanup_resources()
        
        super().closeEvent(event)
```

### MenuBar Component
```python
class MenuBarManager:
    """Manages main window menu bar."""
    
    def __init__(self, parent: QMainWindow) -> None:
        """Initialize menu bar.
        
        Args:
            parent: Parent main window
        """
        self._parent = parent
        self._setup_menus()
    
    def _setup_menus(self) -> None:
        """Setup all menu items."""
        menubar = self._parent.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        self._add_file_actions(file_menu)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        self._add_edit_actions(edit_menu)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        self._add_view_actions(view_menu)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        self._add_tools_actions(tools_menu)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        self._add_help_actions(help_menu)
    
    def _add_file_actions(self, menu: QMenu) -> None:
        """Add file menu actions."""
        # Open Files
        open_action = QAction('&Open Files...', self._parent)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip('Open files for conversion')
        open_action.triggered.connect(self._parent.open_files)
        menu.addAction(open_action)
        
        # Open Folder
        open_folder_action = QAction('Open &Folder...', self._parent)
        open_folder_action.setShortcut(QKeySequence('Ctrl+Shift+O'))
        open_folder_action.setStatusTip('Open folder for batch conversion')
        open_folder_action.triggered.connect(self._parent.open_folder)
        menu.addAction(open_folder_action)
        
        menu.addSeparator()
        
        # Recent Files submenu
        recent_menu = menu.addMenu('&Recent Files')
        self._setup_recent_files_menu(recent_menu)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction('E&xit', self._parent)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self._parent.close)
        menu.addAction(exit_action)
```

## Dialog Components

### PreferencesDialog
```python
class PreferencesDialog(QDialog):
    """Application preferences configuration dialog.
    
    Provides interface for configuring all application settings including
    conversion options, UI preferences, and advanced settings.
    
    Signals:
        settings_accepted (Dict[str, Any]): Settings were accepted
        settings_rejected (): Settings dialog was cancelled
    """
    
    settings_accepted = pyqtSignal(dict)
    settings_rejected = pyqtSignal()
    
    def __init__(self, config: 'Config', parent: Optional[QWidget] = None) -> None:
        """Initialize preferences dialog.
        
        Args:
            config: Current application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self) -> None:
        """Setup dialog user interface."""
        self.setWindowTitle('Preferences')
        self.setModal(True)
        self.resize(600, 500)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = self._create_general_tab()
        tab_widget.addTab(general_tab, 'General')
        
        # Conversion tab
        conversion_tab = self._create_conversion_tab()
        tab_widget.addTab(conversion_tab, 'Conversion')
        
        # Advanced tab
        advanced_tab = self._create_advanced_tab()
        tab_widget.addTab(advanced_tab, 'Advanced')
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self._accept_settings)
        button_box.rejected.connect(self._reject_settings)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply_settings
        )
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(['English', 'Spanish', 'French', 'German'])
        layout.addRow('Language:', self.language_combo)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Auto', 'Light', 'Dark'])
        layout.addRow('Theme:', self.theme_combo)
        
        # Check for updates
        self.update_check_box = QCheckBox('Check for updates at startup')
        layout.addRow(self.update_check_box)
        
        widget.setLayout(layout)
        return widget
    
    def _create_conversion_tab(self) -> QWidget:
        """Create conversion settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Default output format
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(['Markdown', 'HTML', 'Plain Text'])
        layout.addRow('Default Output Format:', self.output_format_combo)
        
        # Output directory
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        browse_button = QPushButton('Browse...')
        browse_button.clicked.connect(self._browse_output_directory)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(browse_button)
        layout.addRow('Output Directory:', output_layout)
        
        # OCR settings
        ocr_group = QGroupBox('OCR Settings')
        ocr_layout = QFormLayout()
        
        self.enable_ocr_check = QCheckBox('Enable OCR for scanned documents')
        ocr_layout.addRow(self.enable_ocr_check)
        
        self.ocr_language_combo = QComboBox()
        self.ocr_language_combo.addItems(['English', 'Spanish', 'French', 'German'])
        ocr_layout.addRow('OCR Language:', self.ocr_language_combo)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        widget.setLayout(layout)
        return widget
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current dialog settings.
        
        Returns:
            Dictionary of current settings
        """
        return {
            'language': self.language_combo.currentText().lower(),
            'theme': self.theme_combo.currentText().lower(),
            'check_updates': self.update_check_box.isChecked(),
            'default_output_format': self.output_format_combo.currentText().lower(),
            'output_directory': self.output_dir_edit.text(),
            'enable_ocr': self.enable_ocr_check.isChecked(),
            'ocr_language': self.ocr_language_combo.currentText().lower()
        }
```

### ProgressDialog
```python
class ProgressDialog(QDialog):
    """Progress dialog for long-running operations.
    
    Provides progress feedback with cancellation support and detailed
    status information for batch operations.
    
    Signals:
        cancelled (): User requested cancellation
        finished (bool): Operation finished (success/failure)
    """
    
    cancelled = pyqtSignal()
    finished = pyqtSignal(bool)  # success
    
    def __init__(
        self, 
        title: str, 
        maximum: int = 100,
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize progress dialog.
        
        Args:
            title: Dialog title
            maximum: Maximum progress value
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui(title, maximum)
        self._start_time = None
        self._current_operation = ""
    
    def set_progress(self, value: int, message: str = "") -> None:
        """Update progress value and message.
        
        Args:
            value: Progress value (0 to maximum)
            message: Status message
        """
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
            self._current_operation = message
        
        # Update time estimates
        if self._start_time:
            elapsed = time.time() - self._start_time
            if value > 0:
                total_estimated = elapsed * (self.progress_bar.maximum() / value)
                remaining = total_estimated - elapsed
                
                self.time_label.setText(
                    f"Elapsed: {self._format_time(elapsed)} | "
                    f"Remaining: {self._format_time(remaining)}"
                )
    
    def set_indeterminate(self, indeterminate: bool = True) -> None:
        """Set progress bar to indeterminate mode.
        
        Args:
            indeterminate: Whether to use indeterminate mode
        """
        if indeterminate:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
    
    def add_log_message(self, message: str, level: str = 'info') -> None:
        """Add message to progress log.
        
        Args:
            message: Log message
            level: Message level ('info', 'warning', 'error')
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color-code messages by level
        if level == 'error':
            formatted_message = f'<span style="color: red;">[{timestamp}] ERROR: {message}</span>'
        elif level == 'warning':
            formatted_message = f'<span style="color: orange;">[{timestamp}] WARNING: {message}</span>'
        else:
            formatted_message = f'[{timestamp}] {message}'
        
        self.log_text.append(formatted_message)
    
    def start_operation(self, operation_name: str) -> None:
        """Start new operation.
        
        Args:
            operation_name: Name of the operation
        """
        self._start_time = time.time()
        self._current_operation = operation_name
        self.status_label.setText(f"Starting {operation_name}...")
        self.show()
    
    def finish_operation(self, success: bool = True) -> None:
        """Finish current operation.
        
        Args:
            success: Whether operation completed successfully
        """
        if success:
            self.status_label.setText("Operation completed successfully")
            self.add_log_message("Operation completed successfully")
        else:
            self.status_label.setText("Operation failed")
            self.add_log_message("Operation failed", "error")
        
        self.cancel_button.setText("Close")
        self.finished.emit(success)
```

## Widget Components

### FileListWidget
```python
class FileListWidget(QListWidget):
    """Widget for displaying and managing conversion file queue.
    
    Provides drag-and-drop support, file validation, and context menu
    operations for managing the conversion queue.
    
    Signals:
        files_added (List[Path]): Files added to list
        files_removed (List[Path]): Files removed from list
        selection_changed (List[Path]): Selection changed
        file_double_clicked (Path): File was double-clicked
    """
    
    files_added = pyqtSignal(list)  # List[Path]
    files_removed = pyqtSignal(list)  # List[Path]
    selection_changed = pyqtSignal(list)  # List[Path]
    file_double_clicked = pyqtSignal(Path)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize file list widget."""
        super().__init__(parent)
        self._setup_widget()
        self._setup_context_menu()
    
    def add_files(self, file_paths: List[Path]) -> None:
        """Add files to the list.
        
        Args:
            file_paths: Files to add
        """
        valid_files = []
        
        for file_path in file_paths:
            if self._validate_file(file_path):
                item = FileListItem(file_path)
                self.addItem(item)
                valid_files.append(file_path)
            else:
                # Show warning for invalid files
                QMessageBox.warning(
                    self,
                    "Invalid File",
                    f"File format not supported: {file_path.name}"
                )
        
        if valid_files:
            self.files_added.emit(valid_files)
    
    def remove_selected_files(self) -> None:
        """Remove currently selected files."""
        removed_files = []
        
        for item in self.selectedItems():
            if isinstance(item, FileListItem):
                removed_files.append(item.file_path)
                self.takeItem(self.row(item))
        
        if removed_files:
            self.files_removed.emit(removed_files)
    
    def get_all_files(self) -> List[Path]:
        """Get all files in the list.
        
        Returns:
            List of all file paths
        """
        files = []
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, FileListItem):
                files.append(item.file_path)
        return files
    
    def get_selected_files(self) -> List[Path]:
        """Get selected files.
        
        Returns:
            List of selected file paths
        """
        files = []
        for item in self.selectedItems():
            if isinstance(item, FileListItem):
                files.append(item.file_path)
        return files
    
    def update_file_status(self, file_path: Path, status: str, message: str = "") -> None:
        """Update file status display.
        
        Args:
            file_path: File to update
            status: Status ('pending', 'processing', 'completed', 'error')
            message: Optional status message
        """
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, FileListItem) and item.file_path == file_path:
                item.set_status(status, message)
                break

class FileListItem(QListWidgetItem):
    """Custom list item for file display."""
    
    def __init__(self, file_path: Path) -> None:
        """Initialize file list item.
        
        Args:
            file_path: Path to file
        """
        super().__init__()
        self.file_path = file_path
        self.status = 'pending'
        self.message = ''
        self._update_display()
    
    def set_status(self, status: str, message: str = "") -> None:
        """Set item status.
        
        Args:
            status: Item status
            message: Status message
        """
        self.status = status
        self.message = message
        self._update_display()
    
    def _update_display(self) -> None:
        """Update item display text and icon."""
        # Set display text
        text = self.file_path.name
        if self.message:
            text += f" - {self.message}"
        self.setText(text)
        
        # Set status icon
        style = QApplication.style()
        if self.status == 'completed':
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        elif self.status == 'error':
            icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        elif self.status == 'processing':
            icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        else:
            icon = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        
        self.setIcon(icon)
        
        # Set tooltip
        tooltip = f"File: {self.file_path}\nStatus: {self.status}"
        if self.message:
            tooltip += f"\nMessage: {self.message}"
        self.setToolTip(tooltip)
```

### PreviewWidget
```python
class PreviewWidget(QWidget):
    """Widget for previewing document content and conversion results.
    
    Supports multiple content formats with syntax highlighting and
    zoom functionality.
    
    Signals:
        content_changed (str): Content was modified
        zoom_changed (int): Zoom level changed
    """
    
    content_changed = pyqtSignal(str)
    zoom_changed = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize preview widget."""
        super().__init__(parent)
        self._setup_ui()
        self._current_format = 'text'
        self._zoom_level = 100
    
    def set_content(self, content: str, format_type: str = 'markdown') -> None:
        """Set preview content.
        
        Args:
            content: Content to display
            format_type: Content format ('markdown', 'html', 'text')
        """
        self._current_format = format_type
        
        if format_type == 'markdown':
            self._display_markdown(content)
        elif format_type == 'html':
            self._display_html(content)
        else:
            self._display_text(content)
    
    def get_content(self) -> str:
        """Get current content.
        
        Returns:
            Current content as string
        """
        if self._current_format == 'markdown':
            return self.text_edit.toPlainText()
        elif self._current_format == 'html':
            return self.web_view.page().toHtml()
        else:
            return self.text_edit.toPlainText()
    
    def set_zoom_level(self, level: int) -> None:
        """Set zoom level.
        
        Args:
            level: Zoom percentage (50-200)
        """
        level = max(50, min(200, level))
        self._zoom_level = level
        
        # Apply zoom to current view
        if hasattr(self, 'text_edit') and self.text_edit.isVisible():
            font = self.text_edit.font()
            base_size = 10
            new_size = int(base_size * (level / 100))
            font.setPointSize(new_size)
            self.text_edit.setFont(font)
        elif hasattr(self, 'web_view') and self.web_view.isVisible():
            self.web_view.setZoomFactor(level / 100)
        
        self.zoom_changed.emit(level)
    
    def find_text(self, text: str, forward: bool = True) -> bool:
        """Find text in preview.
        
        Args:
            text: Text to find
            forward: Search direction
            
        Returns:
            True if text was found
        """
        if self._current_format in ['markdown', 'text']:
            flags = QTextDocument.FindFlag.FindCaseSensitively
            if not forward:
                flags |= QTextDocument.FindFlag.FindBackward
            
            return self.text_edit.find(text, flags)
        elif self._current_format == 'html':
            return self.web_view.findText(text)
        
        return False
    
    def export_content(self, file_path: Path, format_type: str = None) -> None:
        """Export current content to file.
        
        Args:
            file_path: Output file path
            format_type: Output format (None = detect from extension)
        """
        if format_type is None:
            format_type = file_path.suffix.lower()
        
        content = self.get_content()
        
        if format_type == '.html':
            # Convert markdown to HTML if needed
            if self._current_format == 'markdown':
                import markdown
                content = markdown.markdown(content)
        elif format_type == '.pdf':
            # Export to PDF
            self._export_to_pdf(file_path)
            return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
```

## Custom Controls

### ProgressWidget
```python
class ProgressWidget(QWidget):
    """Enhanced progress widget with multiple progress bars and statistics.
    
    Displays overall progress, individual file progress, and operation
    statistics for batch conversion operations.
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize progress widget."""
        super().__init__(parent)
        self._setup_ui()
        self._reset_stats()
    
    def _setup_ui(self) -> None:
        """Setup widget UI."""
        layout = QVBoxLayout()
        
        # Overall progress
        overall_group = QGroupBox("Overall Progress")
        overall_layout = QVBoxLayout()
        
        self.overall_progress = QProgressBar()
        self.overall_label = QLabel("Ready")
        
        overall_layout.addWidget(self.overall_label)
        overall_layout.addWidget(self.overall_progress)
        overall_group.setLayout(overall_layout)
        
        # Current file progress
        current_group = QGroupBox("Current File")
        current_layout = QVBoxLayout()
        
        self.current_progress = QProgressBar()
        self.current_label = QLabel("No file")
        
        current_layout.addWidget(self.current_label)
        current_layout.addWidget(self.current_progress)
        current_group.setLayout(current_layout)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout()
        
        self.processed_label = QLabel("Processed: 0")
        self.successful_label = QLabel("Successful: 0")
        self.failed_label = QLabel("Failed: 0")
        self.speed_label = QLabel("Speed: 0 files/min")
        
        stats_layout.addWidget(self.processed_label, 0, 0)
        stats_layout.addWidget(self.successful_label, 0, 1)
        stats_layout.addWidget(self.failed_label, 1, 0)
        stats_layout.addWidget(self.speed_label, 1, 1)
        stats_group.setLayout(stats_layout)
        
        # Add to main layout
        layout.addWidget(overall_group)
        layout.addWidget(current_group)
        layout.addWidget(stats_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def start_batch(self, total_files: int) -> None:
        """Start batch operation.
        
        Args:
            total_files: Total number of files to process
        """
        self._total_files = total_files
        self._processed_files = 0
        self._successful_files = 0
        self._failed_files = 0
        self._start_time = time.time()
        
        self.overall_progress.setRange(0, total_files)
        self.overall_progress.setValue(0)
        self.overall_label.setText(f"Processing 0 of {total_files} files")
        
        self._update_stats()
    
    def update_overall_progress(self, processed: int, current_file: str = "") -> None:
        """Update overall progress.
        
        Args:
            processed: Number of files processed
            current_file: Name of current file being processed
        """
        self._processed_files = processed
        
        self.overall_progress.setValue(processed)
        self.overall_label.setText(f"Processing {processed} of {self._total_files} files")
        
        if current_file:
            self.current_label.setText(f"Processing: {current_file}")
        
        self._update_stats()
    
    def update_current_progress(self, value: int, maximum: int = 100) -> None:
        """Update current file progress.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.current_progress.setRange(0, maximum)
        self.current_progress.setValue(value)
    
    def file_completed(self, success: bool) -> None:
        """Mark current file as completed.
        
        Args:
            success: Whether file was processed successfully
        """
        if success:
            self._successful_files += 1
        else:
            self._failed_files += 1
        
        self.current_progress.setValue(self.current_progress.maximum())
        self._update_stats()
    
    def _update_stats(self) -> None:
        """Update statistics display."""
        self.processed_label.setText(f"Processed: {self._processed_files}")
        self.successful_label.setText(f"Successful: {self._successful_files}")
        self.failed_label.setText(f"Failed: {self._failed_files}")
        
        # Calculate processing speed
        if hasattr(self, '_start_time') and self._processed_files > 0:
            elapsed_time = time.time() - self._start_time
            speed = (self._processed_files / elapsed_time) * 60  # files per minute
            self.speed_label.setText(f"Speed: {speed:.1f} files/min")
```

## Theme System

### ThemeManager
```python
class ThemeManager:
    """Manages application themes and styling.
    
    Provides theme loading, switching, and custom theme creation
    capabilities for the entire application.
    """
    
    def __init__(self) -> None:
        """Initialize theme manager."""
        self._themes = {}
        self._current_theme = 'auto'
        self._load_built_in_themes()
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes.
        
        Returns:
            List of theme names
        """
        return list(self._themes.keys())
    
    def get_current_theme(self) -> str:
        """Get current theme name.
        
        Returns:
            Current theme name
        """
        return self._current_theme
    
    def set_theme(self, theme_name: str) -> None:
        """Set current theme.
        
        Args:
            theme_name: Theme name to activate
        """
        if theme_name in self._themes:
            self._current_theme = theme_name
        else:
            raise ValueError(f"Unknown theme: {theme_name}")
    
    def get_stylesheet(self, theme_name: str = None) -> str:
        """Get stylesheet for theme.
        
        Args:
            theme_name: Theme name (None = current theme)
            
        Returns:
            CSS stylesheet string
        """
        if theme_name is None:
            theme_name = self._current_theme
        
        if theme_name == 'auto':
            # Detect system theme
            theme_name = self._detect_system_theme()
        
        return self._themes.get(theme_name, self._themes['light'])
    
    def load_custom_theme(self, theme_file: Path) -> str:
        """Load custom theme from file.
        
        Args:
            theme_file: Path to theme CSS file
            
        Returns:
            Theme name that was loaded
        """
        theme_name = theme_file.stem
        
        with open(theme_file, 'r', encoding='utf-8') as f:
            stylesheet = f.read()
        
        self._themes[theme_name] = stylesheet
        return theme_name
    
    def create_theme_variant(self, base_theme: str, variant_name: str, 
                           modifications: Dict[str, str]) -> None:
        """Create theme variant with modifications.
        
        Args:
            base_theme: Base theme to modify
            variant_name: Name for new variant
            modifications: CSS property modifications
        """
        if base_theme not in self._themes:
            raise ValueError(f"Base theme not found: {base_theme}")
        
        base_css = self._themes[base_theme]
        
        # Apply modifications
        modified_css = base_css
        for selector, properties in modifications.items():
            # Simple CSS modification (would need more robust CSS parser for production)
            property_string = '; '.join(f"{prop}: {value}" for prop, value in properties.items())
            modified_css += f"\n{selector} {{ {property_string}; }}"
        
        self._themes[variant_name] = modified_css
```

## Event Handling

### Event Patterns
```python
class ComponentEventMixin:
    """Mixin for consistent event handling across components."""
    
    def __init__(self):
        self._event_handlers = {}
    
    def bind_event(self, event_name: str, handler: Callable) -> None:
        """Bind event handler.
        
        Args:
            event_name: Name of event
            handler: Handler function
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def unbind_event(self, event_name: str, handler: Callable) -> None:
        """Unbind event handler.
        
        Args:
            event_name: Name of event
            handler: Handler function to remove
        """
        if event_name in self._event_handlers:
            try:
                self._event_handlers[event_name].remove(handler)
            except ValueError:
                pass
    
    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """Emit event to all handlers.
        
        Args:
            event_name: Name of event
            *args: Event arguments
            **kwargs: Event keyword arguments
        """
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                # Log error but continue with other handlers
                print(f"Event handler error: {e}")
```

## Accessibility Features

### Accessibility Support
```python
class AccessibilityManager:
    """Manages accessibility features for UI components."""
    
    def __init__(self):
        self._high_contrast_mode = False
        self._large_text_mode = False
        self._screen_reader_mode = False
    
    def enable_high_contrast(self, enabled: bool = True) -> None:
        """Enable high contrast mode.
        
        Args:
            enabled: Whether to enable high contrast
        """
        self._high_contrast_mode = enabled
        # Apply high contrast styles
    
    def enable_large_text(self, enabled: bool = True) -> None:
        """Enable large text mode.
        
        Args:
            enabled: Whether to enable large text
        """
        self._large_text_mode = enabled
        # Increase font sizes
    
    def setup_widget_accessibility(self, widget: QWidget, 
                                 role: str, description: str) -> None:
        """Setup accessibility properties for widget.
        
        Args:
            widget: Widget to configure
            role: Accessibility role
            description: Widget description
        """
        widget.setAccessibleName(description)
        widget.setAccessibleDescription(description)
        
        # Set appropriate focus policy
        widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        
        # Add keyboard shortcuts where appropriate
        if isinstance(widget, QPushButton):
            # Ensure buttons are keyboard accessible
            widget.setAutoDefault(True)
```

---

**Related Documentation:**
- 🔧 [Core API](core.md) - Core functionality reference
- ⚙️ [Configuration API](configuration.md) - Settings management
- 🎯 [Event System API](events.md) - Event handling
- 🎨 [Theme System](../developer/theming.md) - Theming and styling
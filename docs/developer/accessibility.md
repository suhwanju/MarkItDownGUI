# Accessibility Implementation

## Overview

This guide covers comprehensive accessibility implementation for the MarkItDown GUI application, ensuring compliance with WCAG 2.1 AA standards and creating an inclusive user experience for all users, including those with disabilities.

## Accessibility Standards

### WCAG 2.1 AA Compliance

#### Core Principles (POUR)
- **Perceivable**: Information and UI components must be presentable in ways users can perceive
- **Operable**: UI components and navigation must be operable by all users
- **Understandable**: Information and UI operation must be understandable
- **Robust**: Content must be robust enough to be interpreted reliably by assistive technologies

#### Success Criteria Targets
- **Level A**: All Level A criteria (25 criteria)
- **Level AA**: All Level AA criteria (13 additional criteria)
- **Level AAA**: Selected Level AAA criteria where feasible

### Supported Assistive Technologies

#### Screen Readers
- **Windows**: NVDA, JAWS, Windows Narrator
- **macOS**: VoiceOver
- **Linux**: Orca, Speakup

#### Other Assistive Technologies
- **Magnifiers**: Windows Magnifier, ZoomText, macOS Zoom
- **Voice Control**: Windows Speech Recognition, macOS Voice Control
- **Switch Navigation**: Various switch input devices
- **High Contrast**: System high contrast modes

## Technical Implementation

### PyQt6 Accessibility Framework

#### Accessibility Properties
```python
# markitdown_gui/core/accessibility.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAccessible
from typing import Optional

class AccessibilityHelper:
    """Helper class for implementing accessibility features"""
    
    @staticmethod
    def set_accessible_properties(widget: QWidget, name: str, 
                                description: Optional[str] = None,
                                role: Optional[QAccessible.Role] = None):
        """Set basic accessibility properties for a widget"""
        widget.setAccessibleName(name)
        
        if description:
            widget.setAccessibleDescription(description)
        
        if role:
            widget.setAccessibleRole(role)
        
        # Ensure widget can receive focus for screen readers
        widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    @staticmethod
    def set_landmark_role(widget: QWidget, landmark_type: str):
        """Set ARIA landmark role for navigation"""
        landmark_roles = {
            'banner': QAccessible.Role.Banner,
            'navigation': QAccessible.Role.Navigation,
            'main': QAccessible.Role.Main,
            'complementary': QAccessible.Role.Complementary,
            'contentinfo': QAccessible.Role.ContentInfo,
            'search': QAccessible.Role.Search,
            'form': QAccessible.Role.Form
        }
        
        role = landmark_roles.get(landmark_type)
        if role:
            widget.setAccessibleRole(role)
    
    @staticmethod
    def create_accessible_button(text: str, description: str, 
                               shortcut: Optional[str] = None) -> 'QPushButton':
        """Create an accessible button with proper attributes"""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QKeySequence
        
        button = QPushButton(text)
        button.setAccessibleName(text)
        button.setAccessibleDescription(description)
        
        if shortcut:
            button.setShortcut(QKeySequence(shortcut))
            # Add shortcut info to description
            full_description = f"{description} (Shortcut: {shortcut})"
            button.setAccessibleDescription(full_description)
        
        return button
    
    @staticmethod
    def announce_status(message: str, priority: QAccessible.Event = QAccessible.Event.StatusChanged):
        """Announce status changes to screen readers"""
        # This would typically use QAccessible.updateAccessibility()
        # to notify assistive technologies of important changes
        QAccessible.updateAccessibility(QAccessibleEvent(priority, None, -1, message))

# Custom accessible widgets
class AccessibleLabel(QLabel):
    """Label with enhanced accessibility features"""
    
    def __init__(self, text: str = "", buddy: QWidget = None):
        super().__init__(text)
        
        if buddy:
            self.setBuddy(buddy)
            # Associate label with form control for screen readers
            buddy.setAccessibleName(text)
        
        # Make labels readable by screen readers when focused
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAccessibleRole(QAccessible.Role.StaticText)

class AccessibleProgressBar(QProgressBar):
    """Progress bar with enhanced accessibility announcements"""
    
    def __init__(self):
        super().__init__()
        self.setAccessibleRole(QAccessible.Role.ProgressBar)
        self.valueChanged.connect(self._announce_progress)
    
    def _announce_progress(self, value: int):
        """Announce progress changes to screen readers"""
        if self.maximum() > 0:
            percentage = (value / self.maximum()) * 100
            message = f"Progress: {percentage:.0f}% complete"
            self.setAccessibleDescription(message)
            
            # Announce at key milestones
            if percentage in [25, 50, 75, 100]:
                AccessibilityHelper.announce_status(message)
```

#### Focus Management
```python
# markitdown_gui/core/focus_management.py
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QObject, QEvent
from typing import List, Optional

class FocusManager(QObject):
    """Manages keyboard focus and navigation order"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.focus_widgets: List[QWidget] = []
        self.current_focus_index = -1
        self.setup_focus_management()
    
    def setup_focus_management(self):
        """Set up proper focus order and navigation"""
        # Install event filter to manage focus
        self.main_window.installEventFilter(self)
        
        # Build initial focus order
        self.rebuild_focus_order()
    
    def rebuild_focus_order(self):
        """Rebuild the logical focus order"""
        self.focus_widgets = []
        
        # Add widgets in logical order
        self._add_focus_widgets_recursive(self.main_window)
        
        # Set Qt tab order
        for i in range(len(self.focus_widgets) - 1):
            QWidget.setTabOrder(self.focus_widgets[i], self.focus_widgets[i + 1])
    
    def _add_focus_widgets_recursive(self, widget: QWidget):
        """Recursively add focusable widgets in logical order"""
        # Check if widget can receive focus
        if (widget.focusPolicy() != Qt.FocusPolicy.NoFocus and 
            widget.isVisible() and widget.isEnabled()):
            self.focus_widgets.append(widget)
        
        # Process children in layout order
        for child in widget.findChildren(QWidget):
            if child.parent() == widget:  # Direct children only
                self._add_focus_widgets_recursive(child)
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle focus-related events"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Handle Ctrl+Tab for widget navigation
            if (key == Qt.Key.Key_Tab and 
                modifiers == Qt.KeyboardModifier.ControlModifier):
                self.navigate_to_next_section()
                return True
            
            # Handle F6 for panel navigation (Windows standard)
            elif key == Qt.Key.Key_F6:
                self.navigate_to_next_panel()
                return True
        
        return False
    
    def navigate_to_next_section(self):
        """Navigate to next major section"""
        # Implementation would cycle through main UI sections
        pass
    
    def navigate_to_next_panel(self):
        """Navigate to next panel (F6 key)"""
        # Implementation would cycle through main panels
        pass
    
    def move_focus_to_widget(self, widget: QWidget):
        """Move focus to specific widget with announcement"""
        widget.setFocus(Qt.FocusReason.ProgrammaticFocus)
        
        # Announce focus change to screen readers
        name = widget.accessibleName() or widget.objectName() or "Unnamed control"
        AccessibilityHelper.announce_status(f"Focus moved to {name}")
    
    def skip_to_main_content(self):
        """Skip navigation and go directly to main content"""
        main_content = self.main_window.findChild(QWidget, "main_content")
        if main_content:
            self.move_focus_to_widget(main_content)

# Usage in main window
class AccessibleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.focus_manager = FocusManager(self)
        self.setup_skip_links()
    
    def setup_skip_links(self):
        """Set up skip navigation links"""
        # Create invisible skip link that becomes visible on focus
        skip_link = QPushButton("Skip to main content")
        skip_link.setObjectName("skip_link")
        skip_link.clicked.connect(self.focus_manager.skip_to_main_content)
        skip_link.setStyleSheet("""
            QPushButton#skip_link {
                position: absolute;
                left: -9999px;
                z-index: 999;
            }
            QPushButton#skip_link:focus {
                left: 0;
                top: 0;
                background: black;
                color: white;
                padding: 8px;
            }
        """)
```

### Keyboard Navigation

#### Comprehensive Keyboard Support
```python
# markitdown_gui/ui/keyboard_navigation.py
from PyQt6.QtWidgets import QWidget, QShortcut
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QAction

class KeyboardNavigationMixin:
    """Mixin to add comprehensive keyboard navigation to widgets"""
    
    def setup_keyboard_navigation(self):
        """Set up keyboard shortcuts and navigation"""
        # Standard application shortcuts
        self.setup_standard_shortcuts()
        
        # Custom navigation shortcuts
        self.setup_navigation_shortcuts()
        
        # Accessibility shortcuts
        self.setup_accessibility_shortcuts()
    
    def setup_standard_shortcuts(self):
        """Set up standard keyboard shortcuts"""
        shortcuts = {
            # File operations
            QKeySequence.StandardKey.Open: self.open_folder,
            QKeySequence.StandardKey.Refresh: self.refresh_file_list,
            QKeySequence.StandardKey.Quit: self.close,
            
            # Edit operations
            QKeySequence.StandardKey.SelectAll: self.select_all_files,
            QKeySequence("Ctrl+D"): self.deselect_all_files,
            QKeySequence("Ctrl+I"): self.invert_selection,
            
            # View operations
            QKeySequence("F5"): self.refresh_file_list,
            QKeySequence("F11"): self.toggle_fullscreen,
            
            # Help
            QKeySequence.StandardKey.HelpContents: self.show_help,
        }
        
        for sequence, slot in shortcuts.items():
            shortcut = QShortcut(sequence, self)
            shortcut.activated.connect(slot)
            
            # Add to tooltip/accessible description
            if hasattr(slot, '__self__'):
                widget = slot.__self__
                if hasattr(widget, 'setToolTip'):
                    current_tip = widget.toolTip()
                    shortcut_text = sequence.toString()
                    new_tip = f"{current_tip} ({shortcut_text})" if current_tip else f"Shortcut: {shortcut_text}"
                    widget.setToolTip(new_tip)
    
    def setup_navigation_shortcuts(self):
        """Set up navigation-specific shortcuts"""
        nav_shortcuts = {
            # Panel navigation
            QKeySequence("F6"): self.navigate_next_panel,
            QKeySequence("Shift+F6"): self.navigate_previous_panel,
            
            # List navigation
            QKeySequence("Ctrl+Home"): self.go_to_first_file,
            QKeySequence("Ctrl+End"): self.go_to_last_file,
            QKeySequence("Ctrl+PageUp"): self.go_to_previous_page,
            QKeySequence("Ctrl+PageDown"): self.go_to_next_page,
            
            # Quick actions
            QKeySequence("Space"): self.toggle_current_file_selection,
            QKeySequence("Return"): self.start_conversion,
            QKeySequence("Escape"): self.cancel_operation,
        }
        
        for sequence, slot in nav_shortcuts.items():
            shortcut = QShortcut(sequence, self)
            shortcut.activated.connect(slot)
    
    def setup_accessibility_shortcuts(self):
        """Set up accessibility-specific shortcuts"""
        a11y_shortcuts = {
            # Screen reader announcements
            QKeySequence("Ctrl+Shift+S"): self.announce_status,
            QKeySequence("Ctrl+Shift+P"): self.announce_progress,
            QKeySequence("Ctrl+Shift+F"): self.announce_file_count,
            
            # High contrast toggle
            QKeySequence("Alt+Shift+H"): self.toggle_high_contrast,
            
            # Focus debugging (development only)
            QKeySequence("Ctrl+Shift+F1"): self.debug_focus_info,
        }
        
        for sequence, slot in a11y_shortcuts.items():
            shortcut = QShortcut(sequence, self)
            shortcut.activated.connect(slot)
```

### Screen Reader Support

#### ARIA-like Properties for PyQt6
```python
# markitdown_gui/core/screen_reader.py
from PyQt6.QtWidgets import QWidget, QLabel, QListWidget, QTreeWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAccessible

class ScreenReaderInterface:
    """Interface for screen reader communication"""
    
    @staticmethod
    def describe_widget(widget: QWidget) -> str:
        """Generate comprehensive description for screen reader"""
        description_parts = []
        
        # Widget type
        widget_type = widget.__class__.__name__
        description_parts.append(widget_type)
        
        # Accessible name
        name = widget.accessibleName()
        if name:
            description_parts.append(name)
        
        # State information
        if not widget.isEnabled():
            description_parts.append("disabled")
        
        if hasattr(widget, 'isChecked') and widget.isChecked():
            description_parts.append("checked")
        
        # Value information
        if hasattr(widget, 'value'):
            description_parts.append(f"value {widget.value()}")
        
        # Additional context
        description = widget.accessibleDescription()
        if description:
            description_parts.append(description)
        
        return ", ".join(description_parts)
    
    @staticmethod
    def announce_live_region(widget: QWidget, message: str, 
                           politeness: str = "polite"):
        """Announce changes in live regions"""
        # Set up live region properties
        if politeness == "assertive":
            priority = QAccessible.Event.Alert
        else:
            priority = QAccessible.Event.StatusChanged
        
        widget.setAccessibleDescription(message)
        AccessibilityHelper.announce_status(message, priority)

class AccessibleFileList(QListWidget):
    """File list with enhanced screen reader support"""
    
    selection_announced = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_accessibility()
    
    def setup_accessibility(self):
        """Set up accessibility features"""
        self.setAccessibleName("File list")
        self.setAccessibleDescription("List of files available for conversion")
        
        # Connect selection changes to announcements
        self.itemSelectionChanged.connect(self.announce_selection_change)
        self.currentItemChanged.connect(self.announce_current_item)
    
    def announce_selection_change(self):
        """Announce selection changes to screen reader"""
        selected_count = len(self.selectedItems())
        total_count = self.count()
        
        if selected_count == 0:
            message = "No files selected"
        elif selected_count == 1:
            item_text = self.selectedItems()[0].text()
            message = f"Selected: {item_text}"
        else:
            message = f"{selected_count} of {total_count} files selected"
        
        self.selection_announced.emit(message)
        ScreenReaderInterface.announce_live_region(self, message)
    
    def announce_current_item(self, current, previous):
        """Announce current item details"""
        if current:
            item_text = current.text()
            row = self.row(current)
            total = self.count()
            
            # Get file size and type if available
            file_info = current.data(Qt.ItemDataRole.UserRole)
            if file_info:
                size = file_info.get('size', 'Unknown size')
                file_type = file_info.get('type', 'Unknown type')
                message = f"{item_text}, {file_type}, {size}, item {row + 1} of {total}"
            else:
                message = f"{item_text}, item {row + 1} of {total}"
            
            self.setAccessibleDescription(message)

class AccessibleProgressReporter(QObject):
    """Reports progress information to screen readers"""
    
    def __init__(self, progress_widget):
        super().__init__()
        self.progress_widget = progress_widget
        self.last_announced_percentage = -1
        
        # Connect to progress updates
        if hasattr(progress_widget, 'valueChanged'):
            progress_widget.valueChanged.connect(self.on_progress_changed)
    
    def on_progress_changed(self, value):
        """Handle progress changes"""
        if self.progress_widget.maximum() > 0:
            percentage = int((value / self.progress_widget.maximum()) * 100)
            
            # Announce at 25% intervals to avoid spam
            if (percentage % 25 == 0 and 
                percentage != self.last_announced_percentage):
                
                message = f"Conversion progress: {percentage}% complete"
                ScreenReaderInterface.announce_live_region(
                    self.progress_widget, message, "polite"
                )
                self.last_announced_percentage = percentage
            
            # Always announce completion
            elif percentage == 100:
                message = "Conversion completed successfully"
                ScreenReaderInterface.announce_live_region(
                    self.progress_widget, message, "assertive"
                )
                self.last_announced_percentage = percentage
```

### Color and Contrast

#### High Contrast Support
```python
# markitdown_gui/core/high_contrast.py
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
import sys

class HighContrastDetector(QObject):
    """Detects and responds to system high contrast mode"""
    
    high_contrast_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.is_high_contrast = self.detect_system_high_contrast()
    
    def detect_system_high_contrast(self) -> bool:
        """Detect if system is using high contrast mode"""
        if sys.platform == "win32":
            return self._detect_windows_high_contrast()
        elif sys.platform == "darwin":
            return self._detect_macos_high_contrast()
        else:
            return self._detect_linux_high_contrast()
    
    def _detect_windows_high_contrast(self) -> bool:
        """Detect Windows high contrast mode"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, 
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes")
            current_theme, _ = winreg.QueryValueEx(key, "CurrentTheme")
            winreg.CloseKey(key)
            
            # Check if high contrast theme is active
            return "hc" in current_theme.lower()
        except:
            return False
    
    def _detect_macos_high_contrast(self) -> bool:
        """Detect macOS high contrast mode"""
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleHighlightColor"],
                capture_output=True, text=True
            )
            # This is a simplified check - in practice you'd check more settings
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def _detect_linux_high_contrast(self) -> bool:
        """Detect Linux high contrast mode"""
        # Use Qt palette to check for high contrast
        palette = QApplication.palette()
        
        # Check if background and foreground have high contrast
        bg_color = palette.color(QPalette.ColorRole.Base)
        fg_color = palette.color(QPalette.ColorRole.Text)
        
        # Calculate rough contrast ratio
        bg_lightness = bg_color.lightness()
        fg_lightness = fg_color.lightness()
        
        contrast_diff = abs(bg_lightness - fg_lightness)
        return contrast_diff > 200  # High contrast threshold

class ColorContrastChecker:
    """Utility for checking color contrast ratios"""
    
    @staticmethod
    def get_relative_luminance(color: QColor) -> float:
        """Calculate relative luminance of a color"""
        def gamma_correct(channel):
            channel = channel / 255.0
            if channel <= 0.03928:
                return channel / 12.92
            else:
                return pow((channel + 0.055) / 1.055, 2.4)
        
        r = gamma_correct(color.red())
        g = gamma_correct(color.green())
        b = gamma_correct(color.blue())
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def calculate_contrast_ratio(color1: QColor, color2: QColor) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        lum1 = ColorContrastChecker.get_relative_luminance(color1)
        lum2 = ColorContrastChecker.get_relative_luminance(color2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def meets_wcag_aa(color1: QColor, color2: QColor, 
                     is_large_text: bool = False) -> bool:
        """Check if color combination meets WCAG AA requirements"""
        contrast_ratio = ColorContrastChecker.calculate_contrast_ratio(color1, color2)
        
        if is_large_text:
            return contrast_ratio >= 3.0  # AA standard for large text
        else:
            return contrast_ratio >= 4.5  # AA standard for normal text
    
    @staticmethod
    def meets_wcag_aaa(color1: QColor, color2: QColor, 
                      is_large_text: bool = False) -> bool:
        """Check if color combination meets WCAG AAA requirements"""
        contrast_ratio = ColorContrastChecker.calculate_contrast_ratio(color1, color2)
        
        if is_large_text:
            return contrast_ratio >= 4.5  # AAA standard for large text
        else:
            return contrast_ratio >= 7.0  # AAA standard for normal text

# Usage in theme system
def validate_theme_accessibility(theme):
    """Validate theme meets accessibility standards"""
    checker = ColorContrastChecker()
    
    # Check primary color against background
    primary_color = QColor(theme.colors.primary)
    background_color = QColor(theme.colors.background_primary)
    
    meets_aa = checker.meets_wcag_aa(primary_color, background_color)
    
    if not meets_aa:
        print(f"Warning: Theme '{theme.name}' may not meet WCAG AA contrast requirements")
    
    return meets_aa
```

### Voice and Alternative Input

#### Voice Control Support
```python
# markitdown_gui/core/voice_control.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QAction
from typing import Dict, Callable

class VoiceControlInterface(QObject):
    """Interface for voice control commands"""
    
    command_executed = pyqtSignal(str, bool)  # command, success
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.voice_commands: Dict[str, Callable] = {}
        self.setup_voice_commands()
    
    def setup_voice_commands(self):
        """Set up voice command mappings"""
        commands = {
            # File operations
            "open folder": self.main_window.open_folder,
            "browse files": self.main_window.open_folder,
            "refresh": self.main_window.refresh_file_list,
            
            # Selection commands
            "select all": self.main_window.select_all_files,
            "select none": self.main_window.deselect_all_files,
            "clear selection": self.main_window.deselect_all_files,
            
            # Conversion commands
            "convert files": self.main_window.start_conversion,
            "start conversion": self.main_window.start_conversion,
            "cancel conversion": self.main_window.cancel_conversion,
            
            # Navigation commands
            "go to settings": self.main_window.show_settings,
            "show help": self.main_window.show_help,
            "show about": self.main_window.show_about,
        }
        
        self.voice_commands.update(commands)
    
    def execute_voice_command(self, command: str) -> bool:
        """Execute a voice command"""
        command = command.lower().strip()
        
        if command in self.voice_commands:
            try:
                self.voice_commands[command]()
                self.command_executed.emit(command, True)
                return True
            except Exception as e:
                print(f"Error executing voice command '{command}': {e}")
                self.command_executed.emit(command, False)
                return False
        else:
            # Try partial matching
            for cmd, action in self.voice_commands.items():
                if command in cmd or cmd in command:
                    try:
                        action()
                        self.command_executed.emit(command, True)
                        return True
                    except Exception as e:
                        print(f"Error executing voice command '{command}': {e}")
                        break
            
            self.command_executed.emit(command, False)
            return False
    
    def get_available_commands(self) -> list:
        """Get list of available voice commands"""
        return list(self.voice_commands.keys())

# Switch input support
class SwitchInputManager(QObject):
    """Manager for switch input devices"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_item_index = 0
        self.scannable_items = []
        self.scanning_active = False
        
        # Timer for automatic scanning
        from PyQt6.QtCore import QTimer
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.advance_scan)
        self.scan_timer.setInterval(1000)  # 1 second intervals
    
    def start_scanning(self):
        """Start switch scanning mode"""
        self.build_scannable_items()
        self.scanning_active = True
        self.current_item_index = 0
        self.highlight_current_item()
        self.scan_timer.start()
    
    def stop_scanning(self):
        """Stop switch scanning mode"""
        self.scanning_active = False
        self.scan_timer.stop()
        self.clear_highlights()
    
    def switch_activated(self):
        """Handle switch activation (select current item)"""
        if self.scanning_active and self.scannable_items:
            current_item = self.scannable_items[self.current_item_index]
            self.activate_item(current_item)
    
    def build_scannable_items(self):
        """Build list of scannable UI elements"""
        self.scannable_items = []
        
        # Find all interactive widgets
        for widget in self.main_window.findChildren(QWidget):
            if (widget.isVisible() and widget.isEnabled() and
                widget.focusPolicy() != Qt.FocusPolicy.NoFocus):
                self.scannable_items.append(widget)
        
        # Sort by position for logical scanning order
        self.scannable_items.sort(key=lambda w: (w.y(), w.x()))
    
    def advance_scan(self):
        """Advance to next scannable item"""
        if not self.scannable_items:
            return
        
        # Clear current highlight
        if self.current_item_index < len(self.scannable_items):
            self.clear_item_highlight(self.scannable_items[self.current_item_index])
        
        # Advance index
        self.current_item_index = (self.current_item_index + 1) % len(self.scannable_items)
        
        # Highlight new item
        self.highlight_current_item()
    
    def highlight_current_item(self):
        """Highlight the currently scanned item"""
        if (self.current_item_index < len(self.scannable_items)):
            item = self.scannable_items[self.current_item_index]
            item.setStyleSheet(item.styleSheet() + """
                border: 3px solid red;
                background-color: rgba(255, 0, 0, 0.1);
            """)
    
    def clear_item_highlight(self, item):
        """Clear highlight from an item"""
        # Remove scanning-specific styles
        style = item.styleSheet()
        # This is simplified - in practice you'd need more robust style management
        style = style.replace("border: 3px solid red;", "")
        style = style.replace("background-color: rgba(255, 0, 0, 0.1);", "")
        item.setStyleSheet(style)
    
    def clear_highlights(self):
        """Clear all scan highlights"""
        for item in self.scannable_items:
            self.clear_item_highlight(item)
    
    def activate_item(self, item):
        """Activate the selected item"""
        if hasattr(item, 'click'):
            item.click()
        else:
            item.setFocus()
```

## Testing Accessibility

### Automated Accessibility Testing
```python
# tests/test_accessibility.py
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from markitdown_gui.core.accessibility import AccessibilityHelper
from markitdown_gui.core.high_contrast import ColorContrastChecker
from markitdown_gui.ui.main_window import MainWindow

class TestAccessibility:
    
    def test_widget_accessibility_properties(self, qtbot):
        """Test that widgets have proper accessibility properties"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Check main window has accessible name
        assert window.accessibleName() != ""
        
        # Check that interactive widgets have accessible names
        interactive_widgets = window.findChildren(QWidget)
        for widget in interactive_widgets:
            if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                assert (widget.accessibleName() != "" or 
                       widget.text() != "" or 
                       widget.objectName() != ""), f"Widget {widget} missing accessible name"
    
    def test_keyboard_navigation(self, qtbot):
        """Test keyboard navigation works properly"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Test Tab key navigation
        initial_widget = window.focusWidget()
        qtbot.keyClick(window, Qt.Key.Key_Tab)
        
        new_widget = window.focusWidget()
        assert new_widget != initial_widget, "Tab navigation not working"
        assert new_widget is not None, "No widget received focus after Tab"
    
    def test_color_contrast(self, qtbot):
        """Test color combinations meet WCAG requirements"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Test common color combinations
        palette = window.palette()
        
        bg_color = palette.color(palette.ColorRole.Base)
        text_color = palette.color(palette.ColorRole.Text)
        
        checker = ColorContrastChecker()
        contrast_ratio = checker.calculate_contrast_ratio(bg_color, text_color)
        
        # Should meet WCAG AA standard (4.5:1)
        assert contrast_ratio >= 4.5, f"Text contrast ratio {contrast_ratio} below WCAG AA standard"
    
    def test_screen_reader_announcements(self, qtbot):
        """Test screen reader announcements"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Test that status changes are announced
        # This would need integration with actual screen reader testing tools
        pass
    
    def test_focus_management(self, qtbot):
        """Test focus management and skip links"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Test skip navigation functionality
        skip_link = window.findChild(QPushButton, "skip_link")
        if skip_link:
            qtbot.mouseClick(skip_link, Qt.MouseButton.LeftButton)
            
            # Verify focus moved to main content
            current_focus = window.focusWidget()
            assert current_focus is not None, "Skip link should move focus"
    
    @pytest.mark.parametrize("theme_name", ["light", "dark", "high_contrast"])
    def test_theme_accessibility(self, theme_name):
        """Test themes meet accessibility standards"""
        from markitdown_gui.core.theme_manager import theme_manager
        
        theme = theme_manager.get_theme(theme_name)
        assert theme is not None, f"Theme {theme_name} not found"
        
        # Check color contrast for key color pairs
        checker = ColorContrastChecker()
        
        primary_color = QColor(theme.colors.primary)
        background_color = QColor(theme.colors.background_primary)
        
        contrast_ratio = checker.calculate_contrast_ratio(primary_color, background_color)
        
        if theme_name == "high_contrast":
            # High contrast theme should meet AAA standard
            assert contrast_ratio >= 7.0, f"High contrast theme should meet WCAG AAA (7:1)"
        else:
            # Regular themes should meet AA standard
            assert contrast_ratio >= 4.5, f"Theme {theme_name} should meet WCAG AA (4.5:1)"

class TestAccessibilityIntegration:
    """Integration tests for accessibility features"""
    
    def test_complete_workflow_keyboard_only(self, qtbot, tmp_path):
        """Test complete workflow using only keyboard"""
        # Create test files
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()
        (test_dir / "test.txt").write_text("Test content")
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Navigate and perform actions using only keyboard
        # 1. Open folder dialog (Ctrl+O)
        qtbot.keySequence(window, "Ctrl+O")
        # Note: In real test, you'd need to handle the file dialog
        
        # 2. Select all files (Ctrl+A)
        qtbot.keySequence(window, "Ctrl+A")
        
        # 3. Start conversion (Enter)
        qtbot.keyClick(window, Qt.Key.Key_Return)
        
        # Verify the workflow completed successfully
        # In a real test, you'd check conversion results
    
    def test_screen_reader_workflow(self, qtbot):
        """Test workflow from screen reader user perspective"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Simulate screen reader navigation
        # This would require more sophisticated testing with actual AT
        pass
```

### Manual Testing Guidelines

#### Accessibility Testing Checklist

##### Keyboard Testing
- [ ] All interactive elements reachable via keyboard
- [ ] Tab order follows logical sequence
- [ ] Escape key cancels operations where appropriate
- [ ] Enter/Space activates buttons and controls
- [ ] Arrow keys navigate within lists and grids
- [ ] Keyboard shortcuts work as documented
- [ ] No keyboard traps (can navigate away from any element)

##### Screen Reader Testing
- [ ] All content announced correctly
- [ ] Form labels properly associated with controls
- [ ] Error messages announced immediately
- [ ] Status changes announced to live regions
- [ ] Lists announce item counts and positions
- [ ] Progress updates announced at key intervals
- [ ] Headings create proper document structure

##### Visual Testing
- [ ] Text readable at 200% zoom
- [ ] Color contrast meets WCAG AA standards
- [ ] Information not conveyed by color alone
- [ ] Focus indicators clearly visible
- [ ] UI usable in high contrast mode
- [ ] Text remains readable with custom fonts

##### Motor Accessibility Testing
- [ ] Click targets at least 44x44 pixels
- [ ] Drag and drop has keyboard alternatives
- [ ] Time limits can be extended or disabled
- [ ] Operations can be cancelled mid-process
- [ ] No actions require precise timing or coordination

## Related Documentation

- 🎨 [UI Guidelines](ui-guidelines.md) - Interface design principles
- 🎨 [Theme System](theming.md) - Custom themes and high contrast support
- 🌍 [Internationalization](i18n.md) - Multi-language accessibility
- 🧪 [Testing Guide](testing.md) - Comprehensive testing strategies

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
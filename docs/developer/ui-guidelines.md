# UI/UX Guidelines

## Overview

This guide establishes UI/UX design principles, patterns, and standards for the MarkItDown GUI application, ensuring consistent, accessible, and user-friendly interface design across all components.

## Design Philosophy

### Core Principles
- **User-Centered Design**: All decisions prioritize user needs and workflows
- **Clarity & Simplicity**: Clear visual hierarchy and minimal cognitive load
- **Consistency**: Uniform patterns, behaviors, and visual elements
- **Accessibility**: WCAG 2.1 AA compliance and inclusive design
- **Performance**: Responsive interactions and efficient resource usage

### Design Values
- **Efficiency**: Minimize clicks and steps to complete tasks
- **Discoverability**: Features are easy to find and understand
- **Forgiveness**: Easy error recovery and undo capabilities
- **Progressive Disclosure**: Advanced features don't overwhelm beginners
- **Cross-Platform Consistency**: Native feel while maintaining brand consistency

## Visual Design System

### Color Palette

#### Primary Colors
```css
/* Primary Brand Colors */
--primary-blue: #0078D4;      /* Primary actions, links */
--primary-blue-hover: #106EBE; /* Hover states */
--primary-blue-pressed: #005A9E; /* Pressed states */

/* Secondary Colors */
--secondary-gray: #605E5C;     /* Secondary text, icons */
--accent-green: #107C10;       /* Success states */
--accent-red: #D13438;         /* Error states */
--accent-orange: #FF8C00;      /* Warning states */
```

#### Neutral Colors
```css
/* Background Colors */
--background-primary: #FFFFFF;   /* Main background */
--background-secondary: #F3F2F1; /* Secondary background */
--background-tertiary: #FAFAFA;  /* Cards, panels */

/* Text Colors */
--text-primary: #323130;         /* Primary text */
--text-secondary: #605E5C;       /* Secondary text */
--text-tertiary: #A19F9D;        /* Tertiary text, placeholders */
--text-disabled: #C8C6C4;        /* Disabled text */

/* Border Colors */
--border-primary: #D2D0CE;       /* Primary borders */
--border-secondary: #EDEBE9;     /* Secondary borders */
```

#### Dark Theme Support
```css
/* Dark Theme Overrides */
--background-primary-dark: #1E1E1E;
--background-secondary-dark: #252526;
--text-primary-dark: #FFFFFF;
--text-secondary-dark: #CCCCCC;
--border-primary-dark: #3C3C3C;
```

### Typography

#### Font System
```css
/* Primary Font Stack */
font-family: "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif;

/* Font Sizes */
--font-size-xs: 11px;    /* Captions, metadata */
--font-size-sm: 12px;    /* Body text small */
--font-size-base: 14px;  /* Base body text */
--font-size-lg: 16px;    /* Emphasized text */
--font-size-xl: 20px;    /* Section headers */
--font-size-2xl: 24px;   /* Page headers */

/* Font Weights */
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* Line Heights */
--line-height-tight: 1.25;  /* Headers */
--line-height-base: 1.5;    /* Body text */
--line-height-loose: 1.75;  /* Long form content */
```

#### Typography Scale
- **H1 (Page Title)**: 24px, semibold, tight line-height
- **H2 (Section Header)**: 20px, semibold, tight line-height
- **H3 (Subsection)**: 16px, medium, base line-height
- **Body Text**: 14px, regular, base line-height
- **Small Text**: 12px, regular, base line-height
- **Caption**: 11px, regular, tight line-height

### Spacing System

#### Spacing Scale
```css
--space-xs: 4px;    /* Tight spacing */
--space-sm: 8px;    /* Small spacing */
--space-base: 16px; /* Base spacing unit */
--space-lg: 24px;   /* Large spacing */
--space-xl: 32px;   /* Extra large spacing */
--space-2xl: 48px;  /* Section spacing */
```

#### Layout Grid
- **Base Unit**: 8px grid system
- **Component Padding**: 16px (2 units)
- **Section Margins**: 32px (4 units)
- **Page Margins**: 48px (6 units)

### Component Library

#### Buttons

##### Primary Button
```python
# Primary action button
class PrimaryButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #C8C6C4;
                color: #A19F9D;
            }
        """)
```

##### Secondary Button
```python
# Secondary action button
class SecondaryButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0078D4;
                border: 1px solid #0078D4;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #F3F2F1;
            }
            QPushButton:pressed {
                background-color: #EDEBE9;
            }
        """)
```

#### Form Controls

##### Text Input
```python
# Standard text input field
class TextInput(QLineEdit):
    def __init__(self, placeholder: str = ""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D2D0CE;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078D4;
                padding: 7px 11px; /* Adjust for thicker border */
            }
            QLineEdit:disabled {
                background-color: #F3F2F1;
                color: #A19F9D;
            }
        """)
```

##### File Selection Widget
```python
# File selection with browse button
class FileSelectWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        self.path_input = TextInput("Select file or folder...")
        self.browse_btn = SecondaryButton("Browse...")
        
        layout.addWidget(self.path_input, 1)
        layout.addWidget(self.browse_btn)
        layout.setSpacing(8)
        self.setLayout(layout)
```

#### Status Indicators

##### Progress Bar
```python
# Progress indication with status text
class ProgressIndicator(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D2D0CE;
                border-radius: 4px;
                background-color: #F3F2F1;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #605E5C; font-size: 12px;")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.setSpacing(4)
        self.setLayout(layout)
```

##### Status Badge
```python
# Status indication badges
class StatusBadge(QLabel):
    def __init__(self, status: str, text: str):
        super().__init__(text)
        self.status = status
        self._update_style()
    
    def _update_style(self):
        styles = {
            'success': 'background-color: #DFF6DD; color: #107C10; border: 1px solid #92C5F7;',
            'error': 'background-color: #FDE7E9; color: #D13438; border: 1px solid #F1BBBB;',
            'warning': 'background-color: #FFF4CE; color: #797775; border: 1px solid #FFE066;',
            'info': 'background-color: #DEECF9; color: #323130; border: 1px solid #92C5F7;'
        }
        
        base_style = """
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        """
        
        self.setStyleSheet(base_style + styles.get(self.status, styles['info']))
```

## Layout Patterns

### Main Application Layout

#### Window Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Title Bar                                        [_][□][X] │
├─────────────────────────────────────────────────────────────┤
│ Menu Bar: File  Edit  View  Tools  Help                   │
├─────────────────────────────────────────────────────────────┤
│ Toolbar: [Folder] [Refresh] [Settings] [Help]             │
├─────────────────────────────────────────────────────────────┤
│ Main Content Area                                          │
│ ┌─────────────────┐ ┌─────────────────────────────────────┐ │
│ │ Source Panel    │ │ Conversion Panel                    │ │
│ │                 │ │                                     │ │
│ │                 │ │                                     │ │
│ └─────────────────┘ └─────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Status Bar: Ready | 0 files selected | Last: Never        │
└─────────────────────────────────────────────────────────────┘
```

#### Panel Organization

##### Source Panel (Left)
- **Directory Selection**: Folder browser with recent locations
- **File List**: Searchable, filterable file list with checkboxes
- **File Details**: Selected file information and preview

##### Conversion Panel (Right)
- **Conversion Options**: Format settings and preferences
- **Progress Tracking**: Real-time conversion progress
- **Results Log**: Conversion history and status messages
- **Actions**: Primary conversion controls

### Responsive Behavior

#### Window Size Adaptation
- **Minimum Window Size**: 800x600px
- **Preferred Size**: 1200x800px
- **Panel Ratios**: Source panel 40%, Conversion panel 60%
- **Collapsible Panels**: Side panels can collapse to icons

#### Content Reflow
- **Small Windows**: Stack panels vertically
- **Large Windows**: Show additional detail columns
- **Ultra-wide**: Show preview pane alongside main content

## Interaction Patterns

### Navigation

#### Primary Navigation
- **Menu Bar**: Traditional menu structure for all features
- **Toolbar**: Quick access to common actions
- **Context Menus**: Right-click actions on files and lists
- **Keyboard Shortcuts**: Standard shortcuts for all actions

#### Secondary Navigation
- **Breadcrumbs**: Directory path navigation
- **Tabs**: Multiple views or document types
- **Accordion**: Collapsible sections for settings

### User Input

#### File Selection
- **Drag & Drop**: Primary method for adding files
- **File Browser**: Traditional file dialog backup
- **Bulk Selection**: Checkbox lists for batch operations
- **Smart Filters**: Auto-filter by supported file types

#### Form Interaction
- **Immediate Feedback**: Real-time validation and suggestions
- **Progressive Enhancement**: Show advanced options on demand
- **Keyboard Navigation**: Full keyboard accessibility
- **Auto-completion**: Smart suggestions where applicable

### Feedback & Communication

#### Progress Communication
- **Determinate Progress**: Show percentage and time estimates
- **Indeterminate Progress**: Use spinners for unknown duration
- **Background Operations**: Non-blocking with notification system
- **Cancellation**: Always provide cancel option for long operations

#### Error Communication
- **Inline Errors**: Show errors next to relevant fields
- **Error Summary**: Collect and show multiple errors
- **Recovery Suggestions**: Provide actionable solutions
- **Error Reporting**: Option to report bugs automatically

## Accessibility

### WCAG 2.1 AA Compliance

#### Visual Accessibility
- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Color Independence**: Don't rely solely on color for information
- **Focus Indicators**: Clear, high-contrast focus rings
- **Text Scaling**: Support 200% zoom without horizontal scrolling

#### Motor Accessibility
- **Target Size**: Minimum 44x44px touch targets
- **Keyboard Navigation**: Full keyboard access to all features
- **Mouse Independence**: All features work with keyboard only
- **Timing Controls**: Allow users to extend or disable time limits

#### Cognitive Accessibility
- **Clear Language**: Simple, direct instructions
- **Consistent Patterns**: Predictable interface behavior
- **Error Prevention**: Validation and confirmation for destructive actions
- **Help Context**: Contextual help and documentation

### Implementation Guidelines

#### Screen Reader Support
```python
# Proper labeling for screen readers
class AccessibleWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set accessible name and description
        self.setAccessibleName("File conversion list")
        self.setAccessibleDescription("Select files to convert to Markdown")
        
        # Use proper roles and states
        self.setAttribute(Qt.WA_AcceptsFocus, True)
```

#### Keyboard Navigation
```python
# Keyboard shortcut implementation
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        # Standard shortcuts
        QShortcut(QKeySequence.Open, self).activated.connect(self.open_folder)
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(self.select_all_files)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.deselect_all_files)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_files)
        
        # Custom shortcuts
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.start_conversion)
```

## Theme System

### Theme Structure
```python
# Theme configuration
class ThemeConfig:
    def __init__(self):
        self.colors = {
            'primary': '#0078D4',
            'background': '#FFFFFF',
            'text': '#323130',
            'border': '#D2D0CE'
        }
        
        self.fonts = {
            'family': 'Segoe UI',
            'size_base': 14,
            'weight_regular': 400
        }
        
        self.spacing = {
            'base': 16,
            'small': 8,
            'large': 24
        }

# Theme application
def apply_theme(widget: QWidget, theme: ThemeConfig):
    stylesheet = generate_stylesheet(theme)
    widget.setStyleSheet(stylesheet)
```

### Dark Mode Support
- **Automatic Detection**: Follow system dark mode preference
- **Manual Toggle**: User preference override
- **Smooth Transition**: Animated theme switching
- **Persistent Settings**: Remember user preference

## Performance Guidelines

### UI Performance
- **60 FPS Target**: Smooth animations and scrolling
- **Lazy Loading**: Load content on demand for large lists
- **Virtual Scrolling**: Handle thousands of files efficiently
- **Background Processing**: Non-blocking operations

### Memory Management
- **Resource Cleanup**: Proper widget disposal
- **Image Optimization**: Efficient preview loading
- **Cache Management**: LRU cache for frequently accessed data
- **Memory Monitoring**: Track and prevent memory leaks

## Testing UI Components

### Visual Testing
```python
# Screenshot testing for visual regression
def test_main_window_appearance(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Take screenshot for comparison
    screenshot = window.grab()
    screenshot.save("test_main_window.png")
    
    # Compare with baseline
    assert compare_images("test_main_window.png", "baseline_main_window.png")
```

### Accessibility Testing
```python
# Test keyboard navigation
def test_keyboard_navigation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Test tab order
    first_widget = window.focusWidget()
    qtbot.keyClick(window, Qt.Key_Tab)
    second_widget = window.focusWidget()
    
    assert first_widget != second_widget
    assert second_widget.isVisible()
```

## Related Documentation

- 🎨 [Theme System](theming.md) - Custom themes and styling
- ♿ [Accessibility](accessibility.md) - Accessibility implementation
- 🌍 [Internationalization](i18n.md) - Multi-language support
- 🧪 [Testing Guide](testing.md) - UI testing strategies

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
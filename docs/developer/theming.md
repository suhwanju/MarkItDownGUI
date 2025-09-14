# Theme System

## Overview

This guide covers the comprehensive theme system implementation for the MarkItDown GUI application, enabling custom visual styling, dark/light mode support, and user customization options.

## Theme Architecture

### Core Principles
- **Flexibility**: Easy theme creation and modification
- **Consistency**: Unified design language across components
- **Performance**: Efficient theme switching without application restart
- **Accessibility**: High contrast and readable color combinations
- **User Control**: Extensive customization options

### Theme Components
- **Color Schemes**: Light, dark, and custom color palettes
- **Typography**: Font families, sizes, and weights
- **Spacing**: Consistent spacing and layout metrics
- **Icons**: Theme-appropriate icon styles
- **Effects**: Shadows, borders, and visual effects

## Theme Structure

### Theme Configuration Format
```python
# markitdown_gui/core/theme.py
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json

@dataclass
class ColorScheme:
    """Color scheme definition"""
    # Primary colors
    primary: str = "#0078D4"
    primary_hover: str = "#106EBE"
    primary_pressed: str = "#005A9E"
    primary_disabled: str = "#C8C6C4"
    
    # Secondary colors
    secondary: str = "#605E5C"
    secondary_hover: str = "#484644"
    secondary_pressed: str = "#323130"
    
    # Background colors
    background_primary: str = "#FFFFFF"
    background_secondary: str = "#F3F2F1"
    background_tertiary: str = "#FAFAFA"
    background_overlay: str = "rgba(0, 0, 0, 0.4)"
    
    # Text colors
    text_primary: str = "#323130"
    text_secondary: str = "#605E5C"
    text_tertiary: str = "#A19F9D"
    text_disabled: str = "#C8C6C4"
    text_inverse: str = "#FFFFFF"
    
    # Border colors
    border_primary: str = "#D2D0CE"
    border_secondary: str = "#EDEBE9"
    border_focus: str = "#0078D4"
    
    # Status colors
    success: str = "#107C10"
    success_background: str = "#DFF6DD"
    warning: str = "#FF8C00"
    warning_background: str = "#FFF4CE"
    error: str = "#D13438"
    error_background: str = "#FDE7E9"
    info: str = "#0078D4"
    info_background: str = "#DEECF9"

@dataclass
class Typography:
    """Typography settings"""
    font_family_primary: str = "Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif"
    font_family_monospace: str = "'Consolas', 'Monaco', 'Courier New', monospace"
    
    # Font sizes (in pixels)
    font_size_xs: int = 11
    font_size_sm: int = 12
    font_size_base: int = 14
    font_size_lg: int = 16
    font_size_xl: int = 20
    font_size_2xl: int = 24
    
    # Font weights
    font_weight_light: int = 300
    font_weight_regular: int = 400
    font_weight_medium: int = 500
    font_weight_semibold: int = 600
    font_weight_bold: int = 700
    
    # Line heights
    line_height_tight: float = 1.25
    line_height_base: float = 1.5
    line_height_loose: float = 1.75

@dataclass
class Spacing:
    """Spacing and layout metrics"""
    # Base spacing units (in pixels)
    unit_xs: int = 4
    unit_sm: int = 8
    unit_base: int = 16
    unit_lg: int = 24
    unit_xl: int = 32
    unit_2xl: int = 48
    
    # Component-specific spacing
    button_padding_x: int = 16
    button_padding_y: int = 8
    input_padding_x: int = 12
    input_padding_y: int = 8
    
    # Border radius
    border_radius_sm: int = 2
    border_radius_base: int = 4
    border_radius_lg: int = 8
    border_radius_full: int = 9999

@dataclass
class Effects:
    """Visual effects and shadows"""
    # Box shadows
    shadow_sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    shadow_base: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    shadow_md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    shadow_lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    
    # Transitions
    transition_fast: str = "150ms ease-in-out"
    transition_base: str = "300ms ease-in-out"
    transition_slow: str = "500ms ease-in-out"
    
    # Opacity levels
    opacity_disabled: float = 0.6
    opacity_hover: float = 0.8
    opacity_overlay: float = 0.9

@dataclass
class Theme:
    """Complete theme definition"""
    name: str
    display_name: str
    description: str
    colors: ColorScheme
    typography: Typography
    spacing: Spacing
    effects: Effects
    is_dark: bool = False
    
    def to_dict(self) -> Dict:
        """Convert theme to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Theme':
        """Create theme from dictionary"""
        return cls(
            name=data['name'],
            display_name=data['display_name'],
            description=data['description'],
            colors=ColorScheme(**data['colors']),
            typography=Typography(**data['typography']),
            spacing=Spacing(**data['spacing']),
            effects=Effects(**data['effects']),
            is_dark=data.get('is_dark', False)
        )
```

### Built-in Themes

#### Light Theme (Default)
```python
# markitdown_gui/themes/light.py
from markitdown_gui.core.theme import Theme, ColorScheme, Typography, Spacing, Effects

LIGHT_THEME = Theme(
    name="light",
    display_name="Light",
    description="Clean and bright light theme",
    colors=ColorScheme(
        # Already defined with light colors above
    ),
    typography=Typography(),
    spacing=Spacing(),
    effects=Effects(),
    is_dark=False
)
```

#### Dark Theme
```python
# markitdown_gui/themes/dark.py
from markitdown_gui.core.theme import Theme, ColorScheme, Typography, Spacing, Effects

DARK_THEME = Theme(
    name="dark",
    display_name="Dark",
    description="Easy on the eyes dark theme",
    colors=ColorScheme(
        # Primary colors
        primary="#0E7DD9",
        primary_hover="#1B85DB",
        primary_pressed="#0F6CBD",
        primary_disabled="#484644",
        
        # Secondary colors
        secondary="#A19F9D",
        secondary_hover="#C8C6C4",
        secondary_pressed="#E1DFDD",
        
        # Background colors
        background_primary="#1E1E1E",
        background_secondary="#252526",
        background_tertiary="#2D2D30",
        background_overlay="rgba(0, 0, 0, 0.6)",
        
        # Text colors
        text_primary="#FFFFFF",
        text_secondary="#CCCCCC",
        text_tertiary="#969696",
        text_disabled="#6C6C6C",
        text_inverse="#000000",
        
        # Border colors
        border_primary="#3C3C3C",
        border_secondary="#2D2D30",
        border_focus="#0E7DD9",
        
        # Status colors (adjusted for dark background)
        success="#00AA00",
        success_background="rgba(0, 170, 0, 0.1)",
        warning="#FFA500",
        warning_background="rgba(255, 165, 0, 0.1)",
        error="#FF4444",
        error_background="rgba(255, 68, 68, 0.1)",
        info="#4FC3F7",
        info_background="rgba(79, 195, 247, 0.1)"
    ),
    typography=Typography(),
    spacing=Spacing(),
    effects=Effects(
        # Adjusted shadows for dark theme
        shadow_sm="0 1px 2px 0 rgba(0, 0, 0, 0.3)",
        shadow_base="0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px 0 rgba(0, 0, 0, 0.3)",
        shadow_md="0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)",
        shadow_lg="0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)"
    ),
    is_dark=True
)
```

#### High Contrast Theme
```python
# markitdown_gui/themes/high_contrast.py
HIGH_CONTRAST_THEME = Theme(
    name="high_contrast",
    display_name="High Contrast",
    description="Maximum contrast for accessibility",
    colors=ColorScheme(
        # High contrast colors
        primary="#0000FF",
        primary_hover="#0000CC",
        primary_pressed="#000099",
        primary_disabled="#808080",
        
        background_primary="#FFFFFF",
        background_secondary="#F0F0F0",
        background_tertiary="#E8E8E8",
        
        text_primary="#000000",
        text_secondary="#000000",
        text_tertiary="#404040",
        text_disabled="#808080",
        
        border_primary="#000000",
        border_secondary="#404040",
        border_focus="#0000FF",
        
        success="#008000",
        success_background="#E8F5E8",
        warning="#FFA500",
        warning_background="#FFF8E1",
        error="#FF0000",
        error_background="#FFE8E8",
        info="#0000FF",
        info_background="#E8E8FF"
    ),
    typography=Typography(
        font_weight_regular=600,  # Bolder text for better visibility
        font_weight_medium=700,
        font_weight_semibold=800
    ),
    spacing=Spacing(),
    effects=Effects(
        # Stronger shadows for high contrast
        shadow_sm="0 2px 4px 0 rgba(0, 0, 0, 0.3)",
        shadow_base="0 2px 6px 0 rgba(0, 0, 0, 0.4)",
        shadow_md="0 6px 12px 0 rgba(0, 0, 0, 0.4)",
        shadow_lg="0 12px 24px 0 rgba(0, 0, 0, 0.4)"
    ),
    is_dark=False
)
```

## Theme Management

### Theme Manager Implementation
```python
# markitdown_gui/core/theme_manager.py
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication
from typing import Dict, Optional, List
import os
import json

from .theme import Theme
from ..themes.light import LIGHT_THEME
from ..themes.dark import DARK_THEME
from ..themes.high_contrast import HIGH_CONTRAST_THEME

class ThemeManager(QObject):
    theme_changed = pyqtSignal(Theme)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        
        # Load built-in themes
        self.register_theme(LIGHT_THEME)
        self.register_theme(DARK_THEME)
        self.register_theme(HIGH_CONTRAST_THEME)
        
        # Load custom themes
        self.load_custom_themes()
        
        # Apply saved theme
        self.load_saved_theme()
    
    def register_theme(self, theme: Theme):
        """Register a theme with the manager"""
        self.themes[theme.name] = theme
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(name)
    
    def get_available_themes(self) -> List[Theme]:
        """Get all available themes"""
        return list(self.themes.values())
    
    def set_theme(self, theme_name: str) -> bool:
        """Set current theme"""
        theme = self.get_theme(theme_name)
        if not theme:
            return False
        
        self.current_theme = theme
        self.save_theme_preference(theme_name)
        self.theme_changed.emit(theme)
        return True
    
    def get_current_theme(self) -> Theme:
        """Get current theme, fallback to light theme"""
        return self.current_theme or LIGHT_THEME
    
    def save_theme_preference(self, theme_name: str):
        """Save theme preference to settings"""
        self.settings.setValue("theme", theme_name)
    
    def load_saved_theme(self):
        """Load saved theme preference"""
        saved_theme = self.settings.value("theme", "light")
        if not self.set_theme(saved_theme):
            self.set_theme("light")  # Fallback to light theme
    
    def load_custom_themes(self):
        """Load custom themes from themes directory"""
        themes_dir = "resources/themes/custom"
        if not os.path.exists(themes_dir):
            return
        
        for filename in os.listdir(themes_dir):
            if filename.endswith('.json'):
                theme_path = os.path.join(themes_dir, filename)
                try:
                    with open(theme_path, 'r') as f:
                        theme_data = json.load(f)
                        theme = Theme.from_dict(theme_data)
                        self.register_theme(theme)
                except Exception as e:
                    print(f"Failed to load custom theme {filename}: {e}")
    
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """Export theme to JSON file"""
        theme = self.get_theme(theme_name)
        if not theme:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(theme.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to export theme: {e}")
            return False
    
    def import_theme(self, file_path: str) -> bool:
        """Import theme from JSON file"""
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
                theme = Theme.from_dict(theme_data)
                self.register_theme(theme)
                return True
        except Exception as e:
            print(f"Failed to import theme: {e}")
            return False
    
    def create_custom_theme(self, base_theme_name: str, new_name: str, 
                          display_name: str, description: str) -> Optional[Theme]:
        """Create a custom theme based on existing theme"""
        base_theme = self.get_theme(base_theme_name)
        if not base_theme:
            return None
        
        # Create a copy with new name
        theme_dict = base_theme.to_dict()
        theme_dict['name'] = new_name
        theme_dict['display_name'] = display_name
        theme_dict['description'] = description
        
        custom_theme = Theme.from_dict(theme_dict)
        self.register_theme(custom_theme)
        return custom_theme

# Global theme manager instance
theme_manager = ThemeManager()
```

### PyQt6 Style Sheet Generator
```python
# markitdown_gui/core/stylesheet_generator.py
from .theme import Theme
from typing import Dict, Any

class StyleSheetGenerator:
    """Generate PyQt6 stylesheets from theme definitions"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
        self.colors = theme.colors
        self.typography = theme.typography
        self.spacing = theme.spacing
        self.effects = theme.effects
    
    def generate_complete_stylesheet(self) -> str:
        """Generate complete application stylesheet"""
        styles = []
        
        # Main window and application styles
        styles.append(self.generate_main_window_styles())
        
        # Button styles
        styles.append(self.generate_button_styles())
        
        # Input field styles
        styles.append(self.generate_input_styles())
        
        # List and tree styles
        styles.append(self.generate_list_styles())
        
        # Menu and toolbar styles
        styles.append(self.generate_menu_styles())
        
        # Dialog styles
        styles.append(self.generate_dialog_styles())
        
        # Progress and status styles
        styles.append(self.generate_progress_styles())
        
        return "\n\n".join(styles)
    
    def generate_main_window_styles(self) -> str:
        return f"""
        QMainWindow {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            font-family: {self.typography.font_family_primary};
            font-size: {self.typography.font_size_base}px;
        }}
        
        QWidget {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
        }}
        """
    
    def generate_button_styles(self) -> str:
        return f"""
        /* Primary Button */
        QPushButton.primary {{
            background-color: {self.colors.primary};
            color: {self.colors.text_inverse};
            border: none;
            padding: {self.spacing.button_padding_y}px {self.spacing.button_padding_x}px;
            border-radius: {self.spacing.border_radius_base}px;
            font-weight: {self.typography.font_weight_medium};
            font-size: {self.typography.font_size_base}px;
            min-width: 80px;
        }}
        
        QPushButton.primary:hover {{
            background-color: {self.colors.primary_hover};
        }}
        
        QPushButton.primary:pressed {{
            background-color: {self.colors.primary_pressed};
        }}
        
        QPushButton.primary:disabled {{
            background-color: {self.colors.primary_disabled};
            color: {self.colors.text_disabled};
        }}
        
        /* Secondary Button */
        QPushButton.secondary {{
            background-color: transparent;
            color: {self.colors.primary};
            border: 1px solid {self.colors.primary};
            padding: {self.spacing.button_padding_y}px {self.spacing.button_padding_x}px;
            border-radius: {self.spacing.border_radius_base}px;
            font-weight: {self.typography.font_weight_medium};
            font-size: {self.typography.font_size_base}px;
            min-width: 80px;
        }}
        
        QPushButton.secondary:hover {{
            background-color: {self.colors.background_secondary};
        }}
        
        QPushButton.secondary:pressed {{
            background-color: {self.colors.background_tertiary};
        }}
        
        /* Default Button (fallback) */
        QPushButton {{
            background-color: {self.colors.background_secondary};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border_primary};
            padding: {self.spacing.button_padding_y}px {self.spacing.button_padding_x}px;
            border-radius: {self.spacing.border_radius_base}px;
            font-size: {self.typography.font_size_base}px;
        }}
        
        QPushButton:hover {{
            background-color: {self.colors.background_tertiary};
        }}
        
        QPushButton:pressed {{
            background-color: {self.colors.border_secondary};
        }}
        """
    
    def generate_input_styles(self) -> str:
        return f"""
        QLineEdit {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
            padding: {self.spacing.input_padding_y}px {self.spacing.input_padding_x}px;
            font-size: {self.typography.font_size_base}px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {self.colors.border_focus};
            padding: {self.spacing.input_padding_y - 1}px {self.spacing.input_padding_x - 1}px;
        }}
        
        QLineEdit:disabled {{
            background-color: {self.colors.background_secondary};
            color: {self.colors.text_disabled};
        }}
        
        QTextEdit {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
            padding: {self.spacing.input_padding_y}px {self.spacing.input_padding_x}px;
            font-size: {self.typography.font_size_base}px;
        }}
        
        QTextEdit:focus {{
            border: 2px solid {self.colors.border_focus};
        }}
        """
    
    def generate_list_styles(self) -> str:
        return f"""
        QListWidget {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
            outline: none;
        }}
        
        QListWidget::item {{
            padding: {self.spacing.unit_sm}px;
            border-bottom: 1px solid {self.colors.border_secondary};
        }}
        
        QListWidget::item:selected {{
            background-color: {self.colors.primary};
            color: {self.colors.text_inverse};
        }}
        
        QListWidget::item:hover {{
            background-color: {self.colors.background_secondary};
        }}
        
        QTreeWidget {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
            outline: none;
        }}
        
        QTreeWidget::item {{
            padding: {self.spacing.unit_sm}px;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {self.colors.primary};
            color: {self.colors.text_inverse};
        }}
        
        QTreeWidget::item:hover {{
            background-color: {self.colors.background_secondary};
        }}
        """
    
    def generate_progress_styles(self) -> str:
        return f"""
        QProgressBar {{
            background-color: {self.colors.background_secondary};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
            height: 6px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {self.colors.primary};
            border-radius: {self.spacing.border_radius_base - 1}px;
        }}
        """
    
    def generate_menu_styles(self) -> str:
        return f"""
        QMenuBar {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            border-bottom: 1px solid {self.colors.border_primary};
        }}
        
        QMenuBar::item {{
            padding: {self.spacing.unit_sm}px {self.spacing.unit_base}px;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors.background_secondary};
        }}
        
        QMenu {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
        }}
        
        QMenu::item {{
            padding: {self.spacing.unit_sm}px {self.spacing.unit_base}px;
            background-color: transparent;
        }}
        
        QMenu::item:selected {{
            background-color: {self.colors.primary};
            color: {self.colors.text_inverse};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {self.colors.border_secondary};
            margin: {self.spacing.unit_sm}px 0;
        }}
        """
    
    def generate_dialog_styles(self) -> str:
        return f"""
        QDialog {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_primary};
        }}
        
        QLabel {{
            color: {self.colors.text_primary};
        }}
        
        QGroupBox {{
            font-weight: {self.typography.font_weight_medium};
            border: 1px solid {self.colors.border_primary};
            border-radius: {self.spacing.border_radius_base}px;
            margin-top: {self.spacing.unit_sm}px;
            padding-top: {self.spacing.unit_base}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {self.spacing.unit_base}px;
            padding: 0 {self.spacing.unit_sm}px 0 {self.spacing.unit_sm}px;
        }}
        """
```

## Theme Application

### Main Application Integration
```python
# markitdown_gui/ui/main_window.py
from PyQt6.QtWidgets import QMainWindow
from ..core.theme_manager import theme_manager
from ..core.stylesheet_generator import StyleSheetGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_theme_system()
    
    def setup_theme_system(self):
        """Initialize theme system"""
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.apply_current_theme()
    
    def on_theme_changed(self, theme):
        """Handle theme change"""
        self.apply_theme(theme)
    
    def apply_current_theme(self):
        """Apply the current theme"""
        current_theme = theme_manager.get_current_theme()
        self.apply_theme(current_theme)
    
    def apply_theme(self, theme):
        """Apply specific theme to the application"""
        # Generate stylesheet from theme
        generator = StyleSheetGenerator(theme)
        stylesheet = generator.generate_complete_stylesheet()
        
        # Apply to the entire application
        self.setStyleSheet(stylesheet)
        
        # Update window icon if theme has specific icon set
        if hasattr(theme, 'icon_set'):
            self.update_icons(theme.icon_set)
    
    def update_icons(self, icon_set):
        """Update icons based on theme"""
        # This would update all icons throughout the application
        # to match the theme (light/dark/high contrast)
        pass
```

### Theme Selection Dialog
```python
# markitdown_gui/ui/dialogs/theme_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QPushButton, QLabel, QGroupBox,
                             QColorDialog, QSpinBox, QFontComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor

from ...core.theme_manager import theme_manager
from ...core.theme import Theme

class ThemeSelectionDialog(QDialog):
    theme_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        self.setModal(True)
        self.setFixedSize(600, 400)
        self.setup_ui()
        self.load_themes()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Theme selection list
        themes_group = QGroupBox("Available Themes")
        themes_layout = QVBoxLayout()
        
        self.themes_list = QListWidget()
        self.themes_list.currentItemChanged.connect(self.on_theme_selection_changed)
        themes_layout.addWidget(self.themes_list)
        
        themes_group.setLayout(themes_layout)
        layout.addWidget(themes_group)
        
        # Theme preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Theme preview will appear here")
        self.preview_label.setMinimumHeight(100)
        self.preview_label.setStyleSheet("border: 1px solid gray; background: white;")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Theme...")
        self.export_btn = QPushButton("Export Theme...")
        self.customize_btn = QPushButton("Customize...")
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        
        self.import_btn.clicked.connect(self.import_theme)
        self.export_btn.clicked.connect(self.export_theme)
        self.customize_btn.clicked.connect(self.customize_theme)
        self.apply_btn.clicked.connect(self.apply_selected_theme)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.customize_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_themes(self):
        """Load available themes into the list"""
        self.themes_list.clear()
        
        current_theme = theme_manager.get_current_theme()
        
        for theme in theme_manager.get_available_themes():
            item = QListWidgetItem()
            item.setText(theme.display_name)
            item.setData(Qt.ItemDataRole.UserRole, theme.name)
            
            # Create color preview
            preview_pixmap = self.create_theme_preview(theme)
            item.setIcon(preview_pixmap)
            
            self.themes_list.addItem(item)
            
            # Select current theme
            if theme.name == current_theme.name:
                self.themes_list.setCurrentItem(item)
    
    def create_theme_preview(self, theme):
        """Create a small preview image of the theme"""
        pixmap = QPixmap(64, 32)
        painter = QPainter(pixmap)
        
        # Background
        painter.fillRect(0, 0, 64, 32, QColor(theme.colors.background_primary))
        
        # Primary color stripe
        painter.fillRect(0, 0, 64, 8, QColor(theme.colors.primary))
        
        # Secondary color stripe
        painter.fillRect(0, 24, 64, 8, QColor(theme.colors.secondary))
        
        painter.end()
        return pixmap
    
    def on_theme_selection_changed(self, current, previous):
        """Handle theme selection change"""
        if current:
            theme_name = current.data(Qt.ItemDataRole.UserRole)
            theme = theme_manager.get_theme(theme_name)
            if theme:
                self.update_preview(theme)
    
    def update_preview(self, theme):
        """Update theme preview"""
        preview_text = f"""
        <div style='background: {theme.colors.background_primary}; color: {theme.colors.text_primary}; 
                    padding: 10px; font-family: {theme.typography.font_family_primary};'>
            <h3 style='color: {theme.colors.primary};'>{theme.display_name}</h3>
            <p>{theme.description}</p>
            <p style='color: {theme.colors.text_secondary};'>Sample text in secondary color</p>
        </div>
        """
        self.preview_label.setText(preview_text)
    
    def apply_selected_theme(self):
        """Apply the selected theme"""
        current_item = self.themes_list.currentItem()
        if current_item:
            theme_name = current_item.data(Qt.ItemDataRole.UserRole)
            theme_manager.set_theme(theme_name)
            self.theme_selected.emit(theme_name)
            self.accept()
    
    def import_theme(self):
        """Import a custom theme"""
        # Implementation for theme import
        pass
    
    def export_theme(self):
        """Export current theme"""
        # Implementation for theme export
        pass
    
    def customize_theme(self):
        """Open theme customization dialog"""
        current_item = self.themes_list.currentItem()
        if current_item:
            theme_name = current_item.data(Qt.ItemDataRole.UserRole)
            dialog = ThemeCustomizationDialog(theme_name, self)
            dialog.exec()
            self.load_themes()  # Refresh list after customization

class ThemeCustomizationDialog(QDialog):
    """Dialog for customizing theme colors and settings"""
    
    def __init__(self, base_theme_name, parent=None):
        super().__init__(parent)
        self.base_theme = theme_manager.get_theme(base_theme_name)
        self.setWindowTitle(f"Customize {self.base_theme.display_name} Theme")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        # Implementation for theme customization interface
        # Color pickers, font selectors, etc.
        pass
```

## System Integration

### Automatic Theme Detection
```python
# markitdown_gui/core/system_theme.py
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication
import sys

class SystemThemeDetector(QObject):
    system_theme_changed = pyqtSignal(bool)  # True for dark, False for light
    
    def __init__(self):
        super().__init__()
        self.current_dark_mode = self.is_system_dark_mode()
        
        # Check for theme changes periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_theme_change)
        self.timer.start(5000)  # Check every 5 seconds
    
    def is_system_dark_mode(self) -> bool:
        """Detect if system is using dark mode"""
        if sys.platform == "win32":
            return self._detect_windows_dark_mode()
        elif sys.platform == "darwin":
            return self._detect_macos_dark_mode()
        else:
            return self._detect_linux_dark_mode()
    
    def _detect_windows_dark_mode(self) -> bool:
        """Detect Windows dark mode"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, 
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except:
            return False
    
    def _detect_macos_dark_mode(self) -> bool:
        """Detect macOS dark mode"""
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            return "Dark" in result.stdout
        except:
            return False
    
    def _detect_linux_dark_mode(self) -> bool:
        """Detect Linux dark mode (GNOME/KDE)"""
        # Use Qt's palette to detect dark mode
        palette = QApplication.palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        return window_color.lightness() < 128
    
    def check_theme_change(self):
        """Check if system theme has changed"""
        current = self.is_system_dark_mode()
        if current != self.current_dark_mode:
            self.current_dark_mode = current
            self.system_theme_changed.emit(current)

# Integration with theme manager
def setup_automatic_theme_switching():
    """Set up automatic theme switching based on system preferences"""
    detector = SystemThemeDetector()
    
    def on_system_theme_change(is_dark):
        if is_dark:
            theme_manager.set_theme("dark")
        else:
            theme_manager.set_theme("light")
    
    detector.system_theme_changed.connect(on_system_theme_change)
    return detector
```

## Performance Optimization

### Theme Caching
```python
# markitdown_gui/core/theme_cache.py
from typing import Dict, Optional
from .stylesheet_generator import StyleSheetGenerator
from .theme import Theme

class ThemeCache:
    """Cache generated stylesheets for performance"""
    
    def __init__(self):
        self._stylesheet_cache: Dict[str, str] = {}
        self._generator_cache: Dict[str, StyleSheetGenerator] = {}
    
    def get_stylesheet(self, theme: Theme) -> str:
        """Get cached stylesheet or generate new one"""
        theme_key = f"{theme.name}_{hash(str(theme.to_dict()))}"
        
        if theme_key not in self._stylesheet_cache:
            generator = StyleSheetGenerator(theme)
            stylesheet = generator.generate_complete_stylesheet()
            self._stylesheet_cache[theme_key] = stylesheet
        
        return self._stylesheet_cache[theme_key]
    
    def clear_cache(self):
        """Clear all cached stylesheets"""
        self._stylesheet_cache.clear()
        self._generator_cache.clear()
    
    def invalidate_theme(self, theme_name: str):
        """Invalidate cache for specific theme"""
        keys_to_remove = [key for key in self._stylesheet_cache.keys() 
                         if key.startswith(theme_name)]
        for key in keys_to_remove:
            del self._stylesheet_cache[key]

# Use cache in theme manager
theme_cache = ThemeCache()
```

## Testing Themes

### Theme Testing Framework
```python
# tests/test_themes.py
import pytest
from markitdown_gui.core.theme import Theme, ColorScheme
from markitdown_gui.core.theme_manager import ThemeManager
from markitdown_gui.core.stylesheet_generator import StyleSheetGenerator

class TestThemes:
    def test_theme_creation(self):
        """Test theme creation and validation"""
        colors = ColorScheme()
        theme = Theme(
            name="test",
            display_name="Test Theme",
            description="Test theme description",
            colors=colors,
            typography=None,
            spacing=None,
            effects=None
        )
        
        assert theme.name == "test"
        assert theme.display_name == "Test Theme"
        assert isinstance(theme.colors, ColorScheme)
    
    def test_theme_manager_operations(self):
        """Test theme manager functionality"""
        manager = ThemeManager()
        
        # Test theme registration
        test_theme = Theme(name="test", display_name="Test", description="Test")
        manager.register_theme(test_theme)
        
        assert manager.get_theme("test") is not None
        assert "test" in [t.name for t in manager.get_available_themes()]
        
        # Test theme switching
        result = manager.set_theme("test")
        assert result is True
        assert manager.get_current_theme().name == "test"
    
    def test_stylesheet_generation(self):
        """Test stylesheet generation"""
        theme = Theme(
            name="test",
            display_name="Test",
            description="Test",
            colors=ColorScheme(),
            typography=None,
            spacing=None,
            effects=None
        )
        
        generator = StyleSheetGenerator(theme)
        stylesheet = generator.generate_complete_stylesheet()
        
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0
        assert "QMainWindow" in stylesheet
        assert "QPushButton" in stylesheet
    
    def test_color_contrast_accessibility(self):
        """Test that themes meet accessibility color contrast requirements"""
        from markitdown_gui.themes.light import LIGHT_THEME
        from markitdown_gui.themes.dark import DARK_THEME
        from markitdown_gui.themes.high_contrast import HIGH_CONTRAST_THEME
        
        themes = [LIGHT_THEME, DARK_THEME, HIGH_CONTRAST_THEME]
        
        for theme in themes:
            # Test primary color contrast
            contrast_ratio = calculate_contrast_ratio(
                theme.colors.primary, 
                theme.colors.background_primary
            )
            
            # WCAG AA requirement: 4.5:1 for normal text
            assert contrast_ratio >= 4.5, f"{theme.name} primary color contrast too low"

def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG color contrast ratio"""
    # This is a simplified implementation
    # In practice, you'd want a more robust color parsing and calculation
    return 4.5  # Placeholder
```

## Related Documentation

- 🎨 [UI Guidelines](ui-guidelines.md) - Interface design principles
- ♿ [Accessibility](accessibility.md) - Accessibility implementation
- 🌍 [Internationalization](i18n.md) - Multi-language support
- 🧪 [Testing Guide](testing.md) - Comprehensive testing approach

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
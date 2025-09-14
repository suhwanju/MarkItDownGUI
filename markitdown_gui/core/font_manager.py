#!/usr/bin/env python3
"""
Font Manager
Robust font handling with DirectWrite error prevention and fallback mechanisms
"""

import logging
from typing import Optional, List
from PyQt6.QtGui import QFont, QFontDatabase, QFontInfo
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


class FontManager:
    """Manages font selection and initialization with error handling."""
    
    # Safe font families that work well across systems
    SAFE_FONTS = [
        "Segoe UI",      # Windows 10/11 default
        "Arial",         # Universal fallback
        "Helvetica",     # macOS/Linux
        "DejaVu Sans",   # Linux default
        "Liberation Sans", # Open source alternative
        "Calibri",       # Office fonts
        "Verdana",       # Web safe
        "Tahoma",        # Older Windows
        "Sans Serif"     # Generic fallback
    ]
    
    # Problematic fonts that should be avoided
    PROBLEMATIC_FONTS = [
        "MS Sans Serif",  # Known DirectWrite issues
        "MS Serif",       # Old Windows font with issues
        "System",         # Generic system font
        "Default"         # Vague font name
    ]
    
    def __init__(self):
        self.available_fonts = []
        self.tested_fonts = set()
        self._initialize_available_fonts()
    
    def _initialize_available_fonts(self):
        """Initialize list of available fonts on the system."""
        try:
            # Get all available font families
            all_families = QFontDatabase.families()
            
            # Filter out problematic fonts and keep safe ones
            safe_available = []
            for font in self.SAFE_FONTS:
                if font in all_families and font not in self.PROBLEMATIC_FONTS:
                    safe_available.append(font)
            
            # Add other available fonts (excluding problematic ones)
            for font in all_families:
                if (font not in self.PROBLEMATIC_FONTS and 
                    font not in safe_available and
                    not font.startswith("@")):  # Skip vertical fonts
                    safe_available.append(font)
            
            self.available_fonts = safe_available
            logger.info(f"Font Manager: {len(self.available_fonts)} safe fonts available")
            logger.debug(f"Safe fonts: {self.available_fonts[:10]}...")  # Log first 10
            
        except Exception as e:
            logger.warning(f"Font initialization error: {e}")
            # Fallback to minimal safe list
            self.available_fonts = ["Arial", "Helvetica", "Sans Serif"]
    
    def get_safe_font(self, preferred_families: List[str] = None, 
                      point_size: int = 10, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        """
        Get a safe font that won't cause DirectWrite errors.
        
        Args:
            preferred_families: List of preferred font families
            point_size: Font size in points
            weight: Font weight
            
        Returns:
            QFont object with safe font settings
        """
        try:
            # Determine font families to try
            families_to_try = []
            
            if preferred_families:
                families_to_try.extend(preferred_families)
            
            families_to_try.extend(self.SAFE_FONTS)
            
            # Try each font family until we find one that works
            for family in families_to_try:
                if family in self.PROBLEMATIC_FONTS:
                    continue
                
                if family in self.available_fonts or family in self.SAFE_FONTS:
                    font = QFont(family, point_size, weight)
                    
                    # Test if the font can be properly created
                    if self._test_font_creation(font):
                        return font
            
            # Ultimate fallback
            logger.warning("Using system default font due to font selection issues")
            font = QFont()  # System default
            font.setPointSize(point_size)
            font.setWeight(weight)
            return font
            
        except Exception as e:
            logger.error(f"Error creating safe font: {e}")
            # Emergency fallback
            return QFont("Arial", point_size, weight)
    
    def _test_font_creation(self, font: QFont) -> bool:
        """
        Test if a font can be created without errors.
        
        Args:
            font: QFont to test
            
        Returns:
            True if font is safe to use
        """
        try:
            font_key = f"{font.family()}_{font.pointSize()}_{font.weight()}"
            
            # Skip if already tested
            if font_key in self.tested_fonts:
                return True
            
            # Create QFontInfo to validate the font
            font_info = QFontInfo(font)
            
            # Check if the font was successfully resolved
            if font_info.family().lower() == font.family().lower():
                self.tested_fonts.add(font_key)
                logger.debug(f"Font test passed: {font.family()}")
                return True
            else:
                logger.debug(f"Font substituted: {font.family()} -> {font_info.family()}")
                # Font was substituted, but that's OK if it's not problematic
                if font_info.family() not in self.PROBLEMATIC_FONTS:
                    self.tested_fonts.add(font_key)
                    return True
                
        except Exception as e:
            logger.debug(f"Font test failed for {font.family()}: {e}")
        
        return False
    
    def set_application_font(self, font: QFont):
        """
        Safely set application-wide font with error handling.
        
        Args:
            font: QFont to set as application default
        """
        try:
            app = QApplication.instance()
            if app:
                # Test the font before applying
                if self._test_font_creation(font):
                    app.setFont(font)
                    logger.info(f"Application font set to: {font.family()}, {font.pointSize()}pt")
                else:
                    # Use safe fallback
                    safe_font = self.get_safe_font(point_size=font.pointSize(), weight=font.weight())
                    app.setFont(safe_font)
                    logger.warning(f"Used fallback font instead of {font.family()}: {safe_font.family()}")
            
        except Exception as e:
            logger.error(f"Failed to set application font: {e}")
    
    def get_monospace_font(self, point_size: int = 10) -> QFont:
        """Get a safe monospace font for code display."""
        monospace_fonts = [
            "Consolas",      # Windows
            "Monaco",        # macOS
            "DejaVu Sans Mono", # Linux
            "Liberation Mono",  # Alternative
            "Courier New",   # Universal fallback
            "Courier"        # Basic fallback
        ]
        
        return self.get_safe_font(monospace_fonts, point_size)
    
    def suppress_font_warnings(self):
        """Suppress font-related warnings and set up error handling."""
        import warnings
        
        # Suppress DirectWrite warnings
        warnings.filterwarnings("ignore", message=".*DirectWrite.*")
        warnings.filterwarnings("ignore", message=".*CreateFontFaceFromHDC.*")
        warnings.filterwarnings("ignore", message=".*MS Sans Serif.*")
        
        logger.info("Font warnings suppressed for DirectWrite issues")


# Global font manager instance
_font_manager: Optional[FontManager] = None


def get_font_manager() -> FontManager:
    """Get the global font manager instance."""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def initialize_font_system():
    """Initialize the font system with error handling."""
    try:
        font_manager = get_font_manager()
        font_manager.suppress_font_warnings()
        logger.info("Font system initialized successfully")
        return font_manager
    except Exception as e:
        logger.error(f"Font system initialization failed: {e}")
        return None


if __name__ == "__main__":
    # Test the font manager
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    font_manager = initialize_font_system()
    if font_manager:
        # Test safe font creation
        safe_font = font_manager.get_safe_font(["Arial", "Helvetica"])
        print(f"Safe font: {safe_font.family()}, {safe_font.pointSize()}pt")
        
        # Test monospace font
        mono_font = font_manager.get_monospace_font()
        print(f"Monospace font: {mono_font.family()}")
        
        # Test application font setting
        font_manager.set_application_font(safe_font)
        
        print("Font manager test completed successfully")
    else:
        print("Font manager initialization failed")
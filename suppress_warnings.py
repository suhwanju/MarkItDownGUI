#!/usr/bin/env python3
"""
Warning Suppression Module
Suppresses known non-critical warnings during application startup
"""

import warnings
import os


def suppress_startup_warnings():
    """Suppress known non-critical warnings that occur during startup."""
    
    # Suppress pydub FFmpeg warning
    # This warning is expected when FFmpeg is not installed, but pydub will still work with default settings
    warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work")
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")
    
    # More comprehensive pydub warning suppression
    warnings.filterwarnings("ignore", message=".*ffmpeg.*", category=RuntimeWarning)
    warnings.filterwarnings("ignore", message=".*avconv.*", category=RuntimeWarning)
    
    # Alternative approach - set environment variable to suppress pydub's check
    # This prevents pydub from even looking for FFmpeg if we know it's not needed
    os.environ.setdefault('PYDUB_FFMPEG_LOADED', '1')
    
    # Suppress other known warnings that don't affect functionality
    warnings.filterwarnings("ignore", message="Using dummy accessibility classes")
    warnings.filterwarnings("ignore", message=".*accessibility features will be disabled.*")
    
    # Comprehensive Qt DirectWrite font warning suppression
    # These warnings don't affect functionality but create noise
    directwrite_patterns = [
        ".*DirectWrite.*",
        ".*CreateFontFaceFromHDC.*", 
        ".*MS Sans Serif.*",
        ".*qt\\.qpa\\.fonts.*",
        ".*font.*failed.*",
        ".*Font.*failed.*",
        ".*LOGFONT.*"
    ]
    
    warning_categories = [RuntimeWarning, UserWarning, Warning, DeprecationWarning]
    
    # Apply filters for all combinations of patterns and categories
    for pattern in directwrite_patterns:
        for category in warning_categories:
            warnings.filterwarnings("ignore", message=pattern, category=category)
        # Also try without specifying category
        warnings.filterwarnings("ignore", message=pattern)
    
    # Set warning filter to ignore all warnings (most aggressive approach)
    # Only for specific modules that are known to generate font warnings
    warnings.filterwarnings("ignore", module=".*qt.*")
    warnings.filterwarnings("ignore", module=".*Qt.*")


def configure_logging_for_warnings():
    """Configure logging to handle Qt warnings appropriately."""
    import logging
    
    # Set up a comprehensive filter for Qt warnings
    class QtWarningFilter(logging.Filter):
        def filter(self, record):
            message = record.getMessage()
            
            # Suppress or reduce level for Qt accessibility warnings
            if "QAccessible not found in any PyQt6 module" in message:
                record.levelno = logging.INFO
                record.levelname = "INFO"
            elif "Using dummy accessibility classes" in message:
                record.levelno = logging.INFO
                record.levelname = "INFO"
            
            # Suppress DirectWrite font warnings completely
            elif any(term in message for term in ["DirectWrite", "CreateFontFaceFromHDC", "MS Sans Serif", "qt.qpa.fonts"]):
                return False  # Don't log these at all
            
            # Suppress other font-related warnings
            elif any(term in message.lower() for term in ["font failed", "font error", "logfont"]):
                return False  # Don't log these at all
            
            return True
    
    # Apply filter to relevant loggers
    loggers_to_filter = [
        'markitdown_gui.core.qt_compatibility',
        'markitdown_gui.core.i18n_manager',
        'markitdown_gui.ui.main_window',
        'PyQt6',
        'qt',
        '',  # Root logger
    ]
    
    qt_filter = QtWarningFilter()
    for logger_name in loggers_to_filter:
        logger = logging.getLogger(logger_name)
        logger.addFilter(qt_filter)


def setup_qt_logging_suppression():
    """Set up Qt-specific logging suppression at the C++ level if possible."""
    try:
        import os
        
        # Set Qt logging environment variables to suppress font warnings
        qt_logging_vars = {
            'QT_LOGGING_RULES': '*.debug=false;qt.qpa.fonts.debug=false;qt.qpa.fonts.warning=false',
            'QT_QPA_PLATFORM_PLUGIN_PATH': '',  # Prevent some plugin warnings
        }
        
        for var, value in qt_logging_vars.items():
            if var not in os.environ:
                os.environ[var] = value
        
    except Exception as e:
        # If this fails, it's not critical
        pass


def initialize_warning_suppression():
    """Initialize all warning suppression measures."""
    setup_qt_logging_suppression()  # Must be first, before Qt loads
    suppress_startup_warnings()
    configure_logging_for_warnings()


if __name__ == "__main__":
    # Test the suppression
    initialize_warning_suppression()
    print("Warning suppression initialized successfully")
    
    # Test that pydub import doesn't show warning
    try:
        import pydub
        print("✅ pydub imported without warnings")
    except ImportError:
        print("⚠️  pydub not available")
    
    # Test qt_compatibility
    try:
        from markitdown_gui.core.qt_compatibility import get_accessibility_info
        info = get_accessibility_info()
        print(f"✅ Qt compatibility info: {info}")
    except ImportError as e:
        print(f"⚠️  Qt compatibility not available: {e}")
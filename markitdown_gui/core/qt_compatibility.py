"""
PyQt6 Compatibility Layer
Handles different PyQt6 versions and accessibility module locations.
"""

import logging
import sys
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Compatibility flags
QT_AVAILABLE = False
QACCESSIBLE_AVAILABLE = False
ACCESSIBILITY_MODULE = None

# Accessibility classes - will be populated during import
QAccessible = None
QAccessibleInterface = None
QAccessibleEvent = None


def _try_import_accessibility_from_gui():
    """Try importing accessibility classes from PyQt6.QtGui."""
    global QAccessible, QAccessibleInterface, QAccessibleEvent, ACCESSIBILITY_MODULE
    
    try:
        from PyQt6.QtGui import QAccessible as QA
        QAccessible = QA
        ACCESSIBILITY_MODULE = "PyQt6.QtGui"
        logger.debug("QAccessible imported from PyQt6.QtGui")
        
        try:
            from PyQt6.QtGui import QAccessibleInterface as QAI, QAccessibleEvent as QAE
            QAccessibleInterface = QAI
            QAccessibleEvent = QAE
        except ImportError:
            # Some versions might not have these
            pass
            
        return True
    except ImportError as e:
        logger.debug(f"Cannot import QAccessible from PyQt6.QtGui: {e}")
        return False


def _try_import_accessibility_from_widgets():
    """Try importing accessibility classes from PyQt6.QtWidgets."""
    global QAccessible, QAccessibleInterface, QAccessibleEvent, ACCESSIBILITY_MODULE
    
    try:
        from PyQt6.QtWidgets import QAccessible as QA
        QAccessible = QA
        ACCESSIBILITY_MODULE = "PyQt6.QtWidgets"
        logger.debug("QAccessible imported from PyQt6.QtWidgets")
        
        try:
            from PyQt6.QtWidgets import QAccessibleInterface as QAI, QAccessibleEvent as QAE
            QAccessibleInterface = QAI
            QAccessibleEvent = QAE
        except ImportError:
            pass
            
        return True
    except ImportError as e:
        logger.debug(f"Cannot import QAccessible from PyQt6.QtWidgets: {e}")
        return False


def _try_import_accessibility_from_core():
    """Try importing accessibility classes from PyQt6.QtCore."""
    global QAccessible, QAccessibleInterface, QAccessibleEvent, ACCESSIBILITY_MODULE
    
    try:
        from PyQt6.QtCore import QAccessible as QA
        QAccessible = QA
        ACCESSIBILITY_MODULE = "PyQt6.QtCore"
        logger.debug("QAccessible imported from PyQt6.QtCore")
        return True
    except ImportError as e:
        logger.debug(f"Cannot import QAccessible from PyQt6.QtCore: {e}")
        return False


def _create_dummy_accessibility_classes():
    """Create dummy accessibility classes when PyQt6 is not available."""
    global QAccessible, QAccessibleInterface, QAccessibleEvent, ACCESSIBILITY_MODULE
    
    class DummyQAccessible:
        """Dummy QAccessible class for environments without PyQt6."""
        
        class Role:
            NoRole = 0
            Button = 1
            CheckBox = 2
            ComboBox = 3
            EditableText = 4
            StaticText = 5
            ProgressBar = 6
            Slider = 7
            PageTabList = 8
            Grouping = 9
            Window = 10
            Dialog = 11
            ScrollBar = 12
        
        class State:
            def __init__(self):
                pass
        
        class Event:
            NameChanged = 1
    
    class DummyQAccessibleInterface:
        """Dummy QAccessibleInterface class."""
        pass
    
    class DummyQAccessibleEvent:
        """Dummy QAccessibleEvent class."""
        def __init__(self, event_type, obj, child):
            pass
    
    QAccessible = DummyQAccessible
    QAccessibleInterface = DummyQAccessibleInterface
    QAccessibleEvent = DummyQAccessibleEvent
    ACCESSIBILITY_MODULE = "dummy"
    
    logger.info("Using dummy accessibility classes - accessibility features will be disabled")


def initialize_qt_compatibility():
    """Initialize PyQt6 compatibility layer."""
    global QT_AVAILABLE, QACCESSIBLE_AVAILABLE
    
    # First, check if PyQt6 is available at all
    try:
        import PyQt6
        QT_AVAILABLE = True
        logger.debug(f"PyQt6 available at: {PyQt6.__file__}")
    except ImportError:
        logger.warning("PyQt6 not available - using dummy classes")
        QT_AVAILABLE = False
        _create_dummy_accessibility_classes()
        return
    
    # Try to import accessibility classes from different modules
    # Order matters: try most common locations first
    
    success = False
    
    # Try QtGui first (most common in older versions)
    if not success:
        success = _try_import_accessibility_from_gui()
    
    # Try QtWidgets (some newer versions)
    if not success:
        success = _try_import_accessibility_from_widgets()
    
    # Try QtCore (fallback)
    if not success:
        success = _try_import_accessibility_from_core()
    
    if success:
        QACCESSIBLE_AVAILABLE = True
        logger.info(f"QAccessible successfully imported from {ACCESSIBILITY_MODULE}")
    else:
        logger.info("QAccessible not found in any PyQt6 module - using dummy classes")
        _create_dummy_accessibility_classes()


# Initialize compatibility layer on import
initialize_qt_compatibility()


def get_accessibility_info():
    """Get information about accessibility support."""
    return {
        'qt_available': QT_AVAILABLE,
        'qaccessible_available': QACCESSIBLE_AVAILABLE,
        'accessibility_module': ACCESSIBILITY_MODULE,
        'qaccessible_class': QAccessible.__name__ if QAccessible else None
    }


def is_accessibility_available():
    """Check if accessibility features are available."""
    return QT_AVAILABLE and QACCESSIBLE_AVAILABLE


# Export the classes for use by other modules
__all__ = [
    'QAccessible',
    'QAccessibleInterface', 
    'QAccessibleEvent',
    'get_accessibility_info',
    'is_accessibility_available',
    'QT_AVAILABLE',
    'QACCESSIBLE_AVAILABLE'
]
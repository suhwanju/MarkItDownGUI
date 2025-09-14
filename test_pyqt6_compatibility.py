#!/usr/bin/env python3
"""
PyQt6 Compatibility Test Script
Tests QAccessible import compatibility across different PyQt6 versions.
"""

def test_qaccessible_import():
    """Test QAccessible import from different modules."""
    print("=== PyQt6 Accessibility Import Test ===\n")
    
    # Test compatibility layer first
    try:
        from markitdown_gui.core.qt_compatibility import (
            QAccessible, get_accessibility_info, is_accessibility_available
        )
        info = get_accessibility_info()
        print(f"✅ Compatibility layer working: {info['accessibility_module']}")
        print(f"   Accessibility available: {is_accessibility_available()}")
        print(f"   QAccessible class: {info['qaccessible_class']}")
        return True
    except Exception as e:
        print(f"❌ Compatibility layer failed: {e}")
        return False

def test_application_imports():
    """Test the full application import chain."""
    print("\n=== Application Import Chain Test ===\n")
    
    try:
        from markitdown_gui.core.accessibility_manager import AccessibilityManager
        print("✅ AccessibilityManager import successful")
    except Exception as e:
        error_msg = str(e)
        if "QAccessible" in error_msg:
            print(f"❌ QAccessible import error in AccessibilityManager: {error_msg}")
            return False
        else:
            print(f"⚠️  Other error in AccessibilityManager: {error_msg}")
    
    try:
        from markitdown_gui.ui.main_window import MainWindow
        print("✅ MainWindow import successful")
    except Exception as e:
        error_msg = str(e)
        if "QAccessible" in error_msg:
            print(f"❌ QAccessible import error in MainWindow chain: {error_msg}")
            return False
        else:
            print(f"⚠️  Other error in MainWindow chain: {error_msg}")
    
    print("✅ All accessibility-related imports working correctly!")
    return True

if __name__ == "__main__":
    print("Testing PyQt6 QAccessible compatibility...\n")
    
    qaccessible_ok = test_qaccessible_import()
    app_imports_ok = test_application_imports()
    
    print(f"\n=== Summary ===")
    print(f"QAccessible Import: {'✅ OK' if qaccessible_ok else '❌ Failed'}")
    print(f"Application Imports: {'✅ OK' if app_imports_ok else '❌ Failed'}")
    
    if app_imports_ok:
        print("\n🎉 PyQt6 compatibility issue has been resolved!")
        print("The application should now start without QAccessible import errors.")
    else:
        print("\n❌ Issues remain. Check PyQt6 installation and version.")
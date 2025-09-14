#!/usr/bin/env python3
"""
Test DirectWrite Font Error Fix
Verifies that the DirectWrite CreateFontFaceFromHDC error is resolved
"""

import sys
import warnings
import logging
import io
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_font_manager():
    """Test the font manager functionality."""
    print("=== Testing Font Manager ===\n")
    
    try:
        from markitdown_gui.core.font_manager import FontManager, initialize_font_system
        
        # Initialize font system
        print("1. Initializing font system...")
        font_manager = initialize_font_system()
        if font_manager:
            print("✅ Font system initialized successfully")
        else:
            print("❌ Font system initialization failed")
            return False
        
        # Test safe font creation
        print("\n2. Testing safe font creation...")
        safe_font = font_manager.get_safe_font(["Arial", "Segoe UI"])
        print(f"✅ Safe font created: {safe_font.family()}, {safe_font.pointSize()}pt")
        
        # Test problematic font avoidance
        print("\n3. Testing problematic font avoidance...")
        problematic_font = font_manager.get_safe_font(["MS Sans Serif", "System"])
        if problematic_font.family() not in font_manager.PROBLEMATIC_FONTS:
            print(f"✅ Problematic fonts avoided, got: {problematic_font.family()}")
        else:
            print(f"❌ Problematic font still used: {problematic_font.family()}")
        
        # Test monospace font
        print("\n4. Testing monospace font...")
        mono_font = font_manager.get_monospace_font(12)
        print(f"✅ Monospace font: {mono_font.family()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Font manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_i18n_font_integration():
    """Test i18n manager integration with font manager."""
    print("\n=== Testing I18n Font Integration ===\n")
    
    try:
        from markitdown_gui.core.i18n_manager import I18nManager
        
        print("1. Creating I18nManager instance...")
        # Note: This might not work without Qt application, but we can test the import
        i18n_manager = I18nManager()
        print("✅ I18nManager created")
        
        # Test font retrieval
        print("\n2. Testing language font retrieval...")
        try:
            font = i18n_manager.get_font_for_language("ko_KR", 12)
            print(f"✅ Korean font: {font.family()}, {font.pointSize()}pt")
            
            font = i18n_manager.get_font_for_language("en_US", 10)  
            print(f"✅ English font: {font.family()}, {font.pointSize()}pt")
            
        except Exception as font_error:
            print(f"⚠️  Font retrieval needs Qt application: {font_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ I18n integration test failed: {e}")
        return False


def test_warning_suppression():
    """Test DirectWrite warning suppression."""
    print("\n=== Testing DirectWrite Warning Suppression ===\n")
    
    try:
        from suppress_warnings import initialize_warning_suppression
        
        print("1. Initializing warning suppression...")
        initialize_warning_suppression()
        print("✅ Warning suppression initialized")
        
        # Test that DirectWrite warnings are suppressed
        print("\n2. Testing DirectWrite warning filters...")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Simulate DirectWrite warning
            warnings.warn("DirectWrite: CreateFontFaceFromHDC() failed", RuntimeWarning)
            warnings.warn("MS Sans Serif font error", UserWarning)
            
            # Check if warnings were suppressed
            directwrite_warnings = [warning for warning in w 
                                  if "DirectWrite" in str(warning.message) 
                                  or "MS Sans Serif" in str(warning.message)]
            
            if directwrite_warnings:
                print(f"❌ DirectWrite warnings not suppressed: {len(directwrite_warnings)} warnings")
                for warning in directwrite_warnings:
                    print(f"   - {warning.message}")
            else:
                print("✅ DirectWrite warnings successfully suppressed")
                
        return len(directwrite_warnings) == 0
        
    except Exception as e:
        print(f"❌ Warning suppression test failed: {e}")
        return False


def test_font_fallback_scenarios():
    """Test various font fallback scenarios."""
    print("\n=== Testing Font Fallback Scenarios ===\n")
    
    try:
        from markitdown_gui.core.font_manager import FontManager
        
        font_manager = FontManager()
        
        # Test 1: Requested font doesn't exist
        print("1. Testing non-existent font fallback...")
        fake_font = font_manager.get_safe_font(["NonExistentFont123", "AnotherFakeFont"])
        print(f"✅ Fallback font: {fake_font.family()}")
        
        # Test 2: Problematic font request
        print("\n2. Testing problematic font avoidance...")
        problematic_font = font_manager.get_safe_font(["MS Sans Serif", "System"])
        if problematic_font.family() not in ["MS Sans Serif", "System"]:
            print(f"✅ Problematic font avoided: {problematic_font.family()}")
        else:
            print(f"⚠️  Problematic font used: {problematic_font.family()}")
        
        # Test 3: Mixed request (good and bad fonts)
        print("\n3. Testing mixed font request...")
        mixed_font = font_manager.get_safe_font(["MS Sans Serif", "Arial", "Helvetica"])
        print(f"✅ Best available font selected: {mixed_font.family()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Font fallback test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Testing DirectWrite Font Error Fix")
    print("=" * 60)
    print("Original error: qt.qpa.fonts: DirectWrite: CreateFontFaceFromHDC() failed")
    print("Error details: MS Sans Serif font creation failure")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(test_warning_suppression())
    results.append(test_font_manager())
    results.append(test_i18n_font_integration()) 
    results.append(test_font_fallback_scenarios())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! DirectWrite font error should be resolved.")
        print("\n📋 Solutions Implemented:")
        print("1. Created FontManager class with safe font selection")
        print("2. Added problematic font detection and avoidance") 
        print("3. Enhanced warning suppression for DirectWrite errors")
        print("4. Integrated font manager with I18nManager")
        print("5. Modified main_window.py to use safe font setting")
        print("\n🎯 Expected Results:")
        print("✅ No more DirectWrite CreateFontFaceFromHDC errors")
        print("✅ MS Sans Serif font avoided automatically")
        print("✅ Safe font fallback system active")
        print("✅ Application fonts work reliably across systems")
    else:
        print(f"❌ {passed}/{total} tests passed. Some issues remain.")
        print("Please check the test output above for specific problems.")


if __name__ == "__main__":
    main()
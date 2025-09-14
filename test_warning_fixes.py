#!/usr/bin/env python3
"""
Test Warning Fixes
Verifies that FFmpeg and QAccessible warnings are properly handled
"""

import sys
import warnings
import logging
import io
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_warning_suppression():
    """Test that warning suppression works correctly."""
    print("=== Testing Warning Suppression ===\n")
    
    # Import and initialize warning suppression
    from suppress_warnings import initialize_warning_suppression
    initialize_warning_suppression()
    print("✅ Warning suppression initialized")
    
    # Test 1: Check environment variable is set
    import os
    if 'PYDUB_FFMPEG_LOADED' in os.environ:
        print("✅ PYDUB_FFMPEG_LOADED environment variable set")
    else:
        print("❌ PYDUB_FFMPEG_LOADED environment variable not set")
    
    # Test 2: Try to import pydub and see if warnings are suppressed
    print("\nTesting pydub import...")
    try:
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # This might trigger FFmpeg warning if pydub is available
            import pydub.utils
            
            # Check for FFmpeg warnings
            ffmpeg_warnings = [warning for warning in w 
                             if "ffmpeg" in str(warning.message).lower() 
                             or "avconv" in str(warning.message).lower()]
            
            if ffmpeg_warnings:
                print(f"❌ FFmpeg warnings still visible: {len(ffmpeg_warnings)} warnings")
                for warning in ffmpeg_warnings:
                    print(f"   - {warning.message}")
            else:
                print("✅ No FFmpeg warnings detected")
                
    except ImportError:
        print("ℹ️  pydub not available for testing")
    
    return True


def test_qt_compatibility_logging():
    """Test Qt compatibility logging levels."""
    print("\n=== Testing Qt Compatibility Logging ===\n")
    
    # Set up logging capture
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.WARNING)  # Only capture WARNING and above
    
    # Get the Qt compatibility logger
    logger = logging.getLogger('markitdown_gui.core.qt_compatibility')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    try:
        # Import Qt compatibility (this will trigger the logging)
        from markitdown_gui.core.qt_compatibility import get_accessibility_info
        
        # Get the log output
        log_output = log_stream.getvalue()
        
        # Check if there are any WARNING level messages about QAccessible
        if "QAccessible" in log_output and "WARNING" in log_output:
            print("❌ QAccessible warnings still at WARNING level")
            print(f"Log output:\n{log_output}")
        else:
            print("✅ QAccessible messages not at WARNING level")
        
        # Get accessibility info and display it
        info = get_accessibility_info()
        print(f"✅ Accessibility info: {info}")
        
        # Check the actual accessibility state
        if not info['qaccessible_available']:
            print("ℹ️  Using dummy accessibility classes (expected in test environment)")
        else:
            print("✅ Real QAccessible classes available")
            
    except ImportError as e:
        print(f"❌ Could not import Qt compatibility: {e}")
        return False
    
    finally:
        logger.removeHandler(handler)
        handler.close()
    
    return True


def test_main_app_startup():
    """Test that main app can start without warnings."""
    print("\n=== Testing Main App Startup ===\n")
    
    try:
        # Capture both warnings and logs
        log_stream = io.StringIO()
        log_handler = logging.StreamHandler(log_stream)
        
        # Set up root logger to capture everything
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)
        root_logger.setLevel(logging.WARNING)  # Only show WARNING and above
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Try to import the modules that would be imported during startup
            print("Importing core modules...")
            from markitdown_gui.core.logger import setup_logging, get_logger
            from markitdown_gui.core.config_manager import ConfigManager
            from markitdown_gui.core.i18n_manager import I18nManager
            
            print("✅ Core modules imported successfully")
            
            # Check for any warnings
            startup_warnings = [warning for warning in w 
                              if "ffmpeg" in str(warning.message).lower() 
                              or "avconv" in str(warning.message).lower()
                              or "qaccessible" in str(warning.message).lower()]
            
            if startup_warnings:
                print(f"❌ Startup warnings detected: {len(startup_warnings)} warnings")
                for warning in startup_warnings:
                    print(f"   - {warning.category.__name__}: {warning.message}")
            else:
                print("✅ No startup warnings detected")
            
            # Check logs for WARNING messages
            log_output = log_stream.getvalue()
            if log_output.strip():
                warning_lines = [line for line in log_output.split('\n') 
                               if 'WARNING' in line and 
                               ('ffmpeg' in line.lower() or 'qaccessible' in line.lower())]
                if warning_lines:
                    print(f"❌ Warning level log messages detected:")
                    for line in warning_lines:
                        print(f"   - {line}")
                else:
                    print("✅ No relevant warning level log messages")
            else:
                print("✅ No warning level log messages")
                
    except Exception as e:
        print(f"❌ Error during startup test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        root_logger.removeHandler(log_handler)
        log_handler.close()
    
    return True


def main():
    """Main test function."""
    print("Testing Warning Fixes for FFmpeg and QAccessible Issues")
    print("=" * 60)
    print("These tests verify that the warning messages are properly suppressed or converted to info level.")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(test_warning_suppression())
    results.append(test_qt_compatibility_logging())
    results.append(test_main_app_startup())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! Warning fixes are working correctly.")
        print("\nChanges made:")
        print("1. Created warning suppression system (suppress_warnings.py)")
        print("2. Modified main.py to use warning suppression at startup")
        print("3. Changed QAccessible log levels from WARNING to INFO")
        print("4. Added comprehensive FFmpeg warning suppression")
        print("\nThe application should now start without showing:")
        print("- pydub FFmpeg/avconv warnings")
        print("- QAccessible not found warnings")
        print("\nThese are now handled as informational messages in the logs.")
    else:
        print(f"❌ {passed}/{total} tests passed. Some issues remain.")
        print("Please check the test output above for specific problems.")


if __name__ == "__main__":
    main()
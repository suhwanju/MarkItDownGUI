#!/usr/bin/env python3
"""
Comprehensive test script to verify all accessibility fixes work properly
Tests compilation, functionality, and error handling of the accessibility system
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported without errors"""
    print("Testing imports...")
    
    try:
        from markitdown_gui.core.accessibility_manager import (
            AccessibilityManager, AccessibilitySettings, AccessibilityLevel,
            AccessibilityFeature, init_accessibility_manager, get_accessibility_manager
        )
        print("✓ Accessibility manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import accessibility manager: {e}")
        return False
    
    try:
        from markitdown_gui.core.screen_reader_support import (
            ScreenReaderBridge, AnnouncementQueue, AnnouncementWorker,
            AnnouncementPriority, LiveRegionManager
        )
        print("✓ Screen reader support imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import screen reader support: {e}")
        return False
    
    try:
        from markitdown_gui.core.accessibility_validator import (
            AccessibilityValidator, ValidationResult, ValidationIssue,
            WCAGLevel, ColorContrastValidator
        )
        print("✓ Accessibility validator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import accessibility validator: {e}")
        return False
    
    return True


def test_settings_validation():
    """Test configuration validation and sanitization"""
    print("\nTesting settings validation...")
    
    try:
        from markitdown_gui.core.accessibility_manager import AccessibilitySettings
        
        # Test valid settings
        settings = AccessibilitySettings()
        errors = settings.validate()
        if errors:
            print(f"✗ Valid settings should not have errors: {errors}")
            return False
        print("✓ Valid settings pass validation")
        
        # Test invalid settings
        settings.font_scale = 5.0  # Too large
        settings.min_touch_target_size = 200  # Too large
        settings.focus_ring_color = "invalid_color"
        
        errors = settings.validate()
        if not errors:
            print("✗ Invalid settings should produce errors")
            return False
        print(f"✓ Invalid settings caught: {len(errors)} errors")
        
        # Verify auto-correction
        if not (0.5 <= settings.font_scale <= 3.0):
            print("✗ Font scale not auto-corrected")
            return False
        print("✓ Settings auto-corrected")
        
        return True
    except Exception as e:
        print(f"✗ Settings validation test failed: {e}")
        return False


def test_thread_safety():
    """Test thread safety of the announcement queue"""
    print("\nTesting thread safety...")
    
    try:
        from markitdown_gui.core.screen_reader_support import AnnouncementQueue, Announcement, AnnouncementPriority
        import threading
        import time
        
        queue = AnnouncementQueue(max_size=10)
        results = []
        
        def producer():
            for i in range(5):
                announcement = Announcement(f"Test message {i}", AnnouncementPriority.POLITE)
                queue.enqueue(announcement)
                time.sleep(0.01)
        
        def consumer():
            for _ in range(5):
                announcement = queue.dequeue()
                if announcement:
                    results.append(announcement.message)
                time.sleep(0.01)
        
        # Start threads
        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)
        
        producer_thread.start()
        time.sleep(0.02)  # Small delay to let producer add items
        consumer_thread.start()
        
        producer_thread.join()
        consumer_thread.join()
        
        if len(results) != 5:
            print(f"✗ Expected 5 messages, got {len(results)}")
            return False
        
        print("✓ Thread safety test passed")
        return True
        
    except Exception as e:
        print(f"✗ Thread safety test failed: {e}")
        return False


def test_wcag_validation():
    """Test WCAG validation logic"""
    print("\nTesting WCAG validation...")
    
    try:
        from markitdown_gui.core.accessibility_validator import (
            ColorContrastValidator, ValidationResult, ValidationIssue, 
            WCAGLevel, ValidationSeverity, WCAGPrinciple
        )
        from PyQt6.QtGui import QColor
        
        # Test contrast calculation
        validator = ColorContrastValidator()
        
        # Black on white should have high contrast
        black = QColor(0, 0, 0)
        white = QColor(255, 255, 255)
        contrast = validator.calculate_contrast_ratio(black, white)
        
        if contrast < 20:  # Should be 21:1
            print(f"✗ Black on white contrast too low: {contrast}")
            return False
        print(f"✓ Black on white contrast: {contrast:.1f}:1")
        
        # Test validation result
        issues = [
            ValidationIssue(
                guideline="1.4.3",
                title="Test issue",
                description="Test description",
                severity=ValidationSeverity.CRITICAL,
                level=WCAGLevel.AA,
                principle=WCAGPrinciple.PERCEIVABLE
            )
        ]
        
        result = ValidationResult(
            total_widgets=10,
            tested_widgets=10,
            issues=issues,
            score=75.0
        )
        
        compliance_level = result.get_compliance_level()
        if compliance_level is not None:  # Should be None due to critical issue
            print(f"✗ Compliance level should be None with critical issues, got {compliance_level}")
            return False
        print("✓ Compliance level correctly calculated")
        
        return True
        
    except Exception as e:
        print(f"✗ WCAG validation test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("\nTesting error handling...")
    
    try:
        from markitdown_gui.core.screen_reader_support import WindowsScreenReader
        
        # Test with invalid system (should not crash)
        reader = WindowsScreenReader()
        # This should work even if no screen readers are installed
        available = reader.is_available()
        print(f"✓ Screen reader availability check: {available}")
        
        # Test announcement with invalid message
        result = reader.announce("", AnnouncementPriority.POLITE)
        print(f"✓ Empty message handled gracefully: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


def test_memory_management():
    """Test resource cleanup and memory management"""
    print("\nTesting memory management...")
    
    try:
        from markitdown_gui.core.accessibility_manager import AccessibilitySettings
        from markitdown_gui.core.screen_reader_support import AnnouncementQueue
        
        # Create and destroy objects to test cleanup
        for i in range(100):
            settings = AccessibilitySettings()
            queue = AnnouncementQueue(max_size=5)
            queue.clear()
        
        print("✓ Memory management test completed (no crashes)")
        return True
        
    except Exception as e:
        print(f"✗ Memory management test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and return overall result"""
    print("=" * 60)
    print("ACCESSIBILITY SYSTEM COMPREHENSIVE TESTS")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Settings Validation", test_settings_validation),
        ("Thread Safety", test_thread_safety),
        ("WCAG Validation", test_wcag_validation),
        ("Error Handling", test_error_handling),
        ("Memory Management", test_memory_management),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Accessibility system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
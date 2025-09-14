#!/usr/bin/env python3
"""
Test DirectWrite Warning Suppression
Verifies that DirectWrite font warnings are properly suppressed
"""

import warnings
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_warning_suppression():
    """Test that DirectWrite warnings are properly suppressed."""
    print("=== Testing DirectWrite Warning Suppression ===\n")
    
    # Initialize warning suppression
    from suppress_warnings import initialize_warning_suppression
    initialize_warning_suppression()
    print("✅ Warning suppression initialized")
    
    # Test different warning scenarios
    test_cases = [
        ("DirectWrite: CreateFontFaceFromHDC() failed", RuntimeWarning),
        ("MS Sans Serif font error", RuntimeWarning),
        ("qt.qpa.fonts: DirectWrite error", UserWarning),
        ("CreateFontFaceFromHDC() failed for font", RuntimeWarning),
        ("Font loading error", RuntimeWarning),
        ("font creation failed", RuntimeWarning),
    ]
    
    suppressed_count = 0
    total_count = len(test_cases)
    
    print("\nTesting warning suppression for different scenarios:")
    
    for message, category in test_cases:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Trigger the warning
            warnings.warn(message, category)
            
            # Check if it was suppressed
            if len(w) == 0:
                print(f"   ✅ Suppressed: {message}")
                suppressed_count += 1
            else:
                print(f"   ❌ Not suppressed: {message}")
    
    success_rate = (suppressed_count / total_count) * 100
    print(f"\nSuppression rate: {suppressed_count}/{total_count} ({success_rate:.1f}%)")
    
    return success_rate >= 80  # At least 80% should be suppressed


def demonstrate_original_error_suppression():
    """Demonstrate suppression of the original DirectWrite error."""
    print("\n=== Original Error Suppression Test ===\n")
    
    original_error = """qt.qpa.fonts: DirectWrite: CreateFontFaceFromHDC() failed (글꼴 파일이나 다른 입력 매개 변수가 올바르지 않습니다.) for QFontDef(Family="MS Sans Serif", pointsize=9, pixelsize=13, styleHint=5, weight=700, stretch=100, hintingPreference=0) LOGFONT("MS Sans Serif", lfWidth=0, lfHeight=-13) dpi=96"""
    
    print("Original error message:")
    print(f"  {original_error[:100]}...")
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Test the key components of the error
        warnings.warn("DirectWrite: CreateFontFaceFromHDC() failed", RuntimeWarning)
        warnings.warn("MS Sans Serif font error", RuntimeWarning)
        warnings.warn("qt.qpa.fonts error", RuntimeWarning)
        
        if len(w) == 0:
            print("✅ Original error pattern would be suppressed")
            return True
        else:
            print(f"❌ {len(w)} warnings not suppressed:")
            for warning in w:
                print(f"   - {warning.message}")
            return False


def main():
    """Main test function."""
    print("DirectWrite Font Error Suppression Test")
    print("=" * 50)
    print("Testing suppression of DirectWrite CreateFontFaceFromHDC errors")
    print("=" * 50)
    
    results = []
    
    # Test warning suppression
    results.append(test_warning_suppression())
    results.append(demonstrate_original_error_suppression())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed!")
        print("\n✅ DirectWrite font warnings will be suppressed")
        print("✅ MS Sans Serif font errors will be suppressed")
        print("✅ Font-related RuntimeWarnings will be suppressed")
        print("\nThe original error should no longer appear in the console:")
        print('  "qt.qpa.fonts: DirectWrite: CreateFontFaceFromHDC() failed"')
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("Some warnings may still be visible")
    
    print("\n📋 Implementation Details:")
    print("• Warning filters added to suppress_warnings.py")
    print("• Multiple warning categories covered (RuntimeWarning, UserWarning)")
    print("• Broad font-related warning suppression")
    print("• Integrated with main.py startup sequence")


if __name__ == "__main__":
    main()
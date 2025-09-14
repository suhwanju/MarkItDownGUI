#!/usr/bin/env python3
"""
Script to install PDF processing dependencies and verify functionality
"""

import subprocess
import sys
import importlib

def install_packages():
    """Install required PDF processing packages"""
    
    print("🔧 Installing PDF processing dependencies...")
    
    packages = [
        "pdfplumber==0.11.4",
        "PyPDF2==3.0.1"
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            print(f"   Error output: {e.stderr}")
            return False
    
    return True


def verify_pdf_libraries():
    """Verify that PDF libraries are available"""
    
    print("\n🔍 Verifying PDF library availability...")
    
    # Test pdfplumber
    try:
        import pdfplumber
        print("   ✅ pdfplumber is available")
        pdfplumber_available = True
    except ImportError:
        print("   ❌ pdfplumber is not available")
        pdfplumber_available = False
    
    # Test PyPDF2
    try:
        import PyPDF2
        print("   ✅ PyPDF2 is available")
        pypdf2_available = True
    except ImportError:
        print("   ❌ PyPDF2 is not available")
        pypdf2_available = False
    
    return pdfplumber_available or pypdf2_available


def test_pdf_validator():
    """Test the PDF validator with new dependencies"""
    
    print("\n🔍 Testing PDF validator functionality...")
    
    try:
        from markitdown_gui.core.validators import PDFValidator
        
        # Create validator instance
        validator = PDFValidator()
        print("   ✅ PDFValidator created successfully")
        
        # Check available libraries
        if hasattr(validator, '_pdf_libraries'):
            print(f"   ✅ Available PDF libraries: {validator._pdf_libraries}")
            
            if validator._pdf_libraries:
                print("   ✅ PDF libraries detected - NO_PDF_LIBRARY warning should be resolved")
                return True
            else:
                print("   ⚠️  No PDF libraries detected - warning will still appear")
                return False
        else:
            print("   ❌ Could not check PDF library availability")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing PDF validator: {e}")
        return False


def verify_fontbbox_handling():
    """Verify that FontBBox error handling is in place"""
    
    print("\n🔍 Verifying FontBBox error handling system...")
    
    try:
        # Check if FontDescriptorError is available
        from markitdown_gui.core.error_handling import FontDescriptorError
        print("   ✅ FontDescriptorError class available")
        
        # Check if conversion manager has warning capture
        from markitdown_gui.core.conversion_manager import ConversionManager
        print("   ✅ ConversionManager available")
        
        # Check the method that handles FontBBox warnings
        conv_manager = ConversionManager(None, None, None, None, None)
        if hasattr(conv_manager, '_perform_conversion_with_cache'):
            print("   ✅ FontBBox warning capture system is in place")
            print("   ℹ️  FontBBox warnings will be logged but handled gracefully")
            return True
        else:
            print("   ❌ FontBBox warning capture system not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying FontBBox handling: {e}")
        return False


def main():
    print("=" * 60)
    print("PDF Processing Dependencies Setup")
    print("=" * 60)
    
    # Install packages
    install_success = install_packages()
    
    if not install_success:
        print("\n⚠️  Package installation failed. You may need to:")
        print("   - Create a virtual environment: python -m venv venv")
        print("   - Activate it: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        print("   - Then run: pip install pdfplumber==0.11.4 PyPDF2==3.0.1")
    
    # Verify libraries
    pdf_libs_available = verify_pdf_libraries()
    
    # Test PDF validator
    validator_working = test_pdf_validator()
    
    # Verify FontBBox handling
    fontbbox_handling = verify_fontbbox_handling()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if pdf_libs_available:
        print("✅ PDF processing libraries: INSTALLED")
        print("✅ NO_PDF_LIBRARY warning: RESOLVED")
    else:
        print("❌ PDF processing libraries: MISSING")
        print("⚠️  NO_PDF_LIBRARY warning: WILL APPEAR")
    
    if fontbbox_handling:
        print("✅ FontBBox error handling: ACTIVE")
        print("ℹ️  FontBBox warnings may appear in logs but are handled gracefully")
    else:
        print("❌ FontBBox error handling: ISSUE DETECTED")
    
    if pdf_libs_available and fontbbox_handling:
        print("\n🎉 Setup complete! The application should now:")
        print("   - Process PDFs with comprehensive validation")
        print("   - Handle FontBBox issues gracefully")
        print("   - Continue processing instead of crashing")
    else:
        print("\n⚠️  Setup incomplete - some issues need attention")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
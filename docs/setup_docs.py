#!/usr/bin/env python3
"""
Documentation setup script for MarkItDown GUI
Automatically sets up and validates the Sphinx documentation system
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_virtual_environment():
    """Check if running in virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment. Consider using venv for isolation.")
    return True

def install_dependencies():
    """Install documentation dependencies"""
    print("📦 Installing documentation dependencies...")
    
    requirements = [
        "sphinx>=7.1.0",
        "sphinx-rtd-theme>=1.3.0",
        "myst-parser>=2.0.0",
        "sphinx-autobuild>=2021.3.14"
    ]
    
    try:
        for req in requirements:
            print(f"  Installing {req}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", req
            ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try creating a virtual environment:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate  # Linux/macOS")
        print("   venv\\Scripts\\activate     # Windows")
        return False

def validate_configuration():
    """Validate Sphinx configuration"""
    print("🔍 Validating Sphinx configuration...")
    
    try:
        # Add current directory to path
        docs_path = Path(__file__).parent
        sys.path.insert(0, str(docs_path))
        
        import conf
        
        # Check essential configuration
        assert hasattr(conf, 'project'), "Project name not defined"
        assert hasattr(conf, 'extensions'), "Extensions not defined"
        assert hasattr(conf, 'html_theme'), "Theme not defined"
        
        print(f"✅ Configuration valid")
        print(f"   Project: {conf.project}")
        print(f"   Extensions: {len(conf.extensions)} loaded")
        print(f"   Theme: {conf.html_theme}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def check_project_structure():
    """Check if project structure is correct"""
    print("📁 Checking project structure...")
    
    docs_path = Path(__file__).parent
    project_root = docs_path.parent
    
    required_files = [
        docs_path / "conf.py",
        docs_path / "index.rst",
        docs_path / "Makefile",
        docs_path / "_static" / "custom.css",
        project_root / "markitdown_gui"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Project structure is correct")
    return True

def create_build_info():
    """Create build information file"""
    docs_path = Path(__file__).parent
    build_info = {
        "documentation_system": "Sphinx",
        "theme": "sphinx_rtd_theme",
        "extensions": [
            "sphinx.ext.autodoc",
            "sphinx.ext.autosummary",
            "sphinx.ext.viewcode",
            "sphinx.ext.napoleon",
            "myst_parser"
        ],
        "features": [
            "Automatic API documentation from docstrings",
            "Professional ReadTheDocs theme",
            "Markdown support via MyST parser",
            "Cross-references and navigation",
            "Custom CSS styling",
            "Korean language support",
            "Mobile-responsive design"
        ],
        "build_commands": {
            "html": "make html",
            "clean": "make clean",
            "livehtml": "make livehtml",
            "fullbuild": "make fullbuild"
        }
    }
    
    info_file = docs_path / "build_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(build_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Build information created: {info_file}")

def test_basic_build():
    """Test basic documentation build"""
    print("🔨 Testing basic build (dry run)...")
    
    docs_path = Path(__file__).parent
    
    try:
        # Test configuration loading
        result = subprocess.run([
            sys.executable, "-c", 
            f"import sys; sys.path.insert(0, '{docs_path}'); import conf; print('Config OK')"
        ], capture_output=True, text=True, cwd=docs_path)
        
        if result.returncode == 0:
            print("✅ Configuration test passed")
        else:
            print(f"❌ Configuration test failed: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Build test failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("📚 MarkItDown GUI Documentation System Setup Complete!")
    print("="*60)
    
    print("\n🚀 Quick Start:")
    print("   1. Install dependencies: make install-deps")
    print("   2. Generate API docs:    make apidoc")
    print("   3. Build HTML docs:      make html")
    print("   4. Serve locally:        make serve")
    
    print("\n🔧 Available Commands:")
    print("   make html       - Build HTML documentation")
    print("   make clean      - Clean build directory")
    print("   make livehtml   - Live reload during development")
    print("   make fullbuild  - Complete rebuild with API docs")
    print("   make linkcheck  - Check external links")
    print("   make coverage   - Check documentation coverage")
    
    print("\n📁 Key Files:")
    print("   docs/conf.py              - Sphinx configuration")
    print("   docs/index.rst            - Main documentation index")
    print("   docs/_static/custom.css   - Custom styling")
    print("   docs/autoapi/index.rst    - Auto-generated API docs")
    
    print("\n🌐 Features:")
    print("   ✅ Automatic API documentation from docstrings")
    print("   ✅ Professional ReadTheDocs theme with custom styling")
    print("   ✅ Markdown support via MyST parser")
    print("   ✅ Cross-references and intelligent navigation")
    print("   ✅ Korean language support with proper fonts")
    print("   ✅ Mobile-responsive design")
    print("   ✅ Search functionality")
    print("   ✅ Code syntax highlighting")
    
    print(f"\n📖 Documentation will be built to: docs/_build/html/")
    print(f"🔗 Local server: http://localhost:8000")

def main():
    """Main setup function"""
    print("🚀 Setting up MarkItDown GUI Documentation System")
    print("="*50)
    
    # Run all checks and setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking virtual environment", check_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Validating configuration", validate_configuration),
        ("Checking project structure", check_project_structure),
        ("Creating build info", create_build_info),
        ("Testing basic build", test_basic_build)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print_usage_instructions()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
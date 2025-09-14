#!/usr/bin/env python3
"""
Documentation validation script for MarkItDown GUI API documentation
Validates the completeness and structure of the generated API documentation
"""

import os
import sys
from pathlib import Path
import re

def validate_file_exists(file_path: Path, description: str) -> bool:
    """Validate that a file exists"""
    if file_path.exists():
        print(f"✅ {description}: {file_path.name}")
        return True
    else:
        print(f"❌ {description}: {file_path.name} (missing)")
        return False

def validate_file_content(file_path: Path, required_patterns: list, description: str) -> bool:
    """Validate file contains required content patterns"""
    if not file_path.exists():
        print(f"❌ {description}: {file_path.name} (file missing)")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern in required_patterns:
            if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"⚠️  {description}: {file_path.name} (missing patterns: {missing_patterns})")
            return False
        else:
            print(f"✅ {description}: {file_path.name} (content validated)")
            return True
            
    except Exception as e:
        print(f"❌ {description}: {file_path.name} (error reading: {e})")
        return False

def count_lines_and_estimate_coverage(file_path: Path) -> tuple:
    """Count lines and estimate documentation coverage"""
    if not file_path.exists():
        return 0, 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        doc_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        coverage = (doc_lines / total_lines * 100) if total_lines > 0 else 0
        
        return total_lines, coverage
    except:
        return 0, 0

def main():
    """Main validation function"""
    print("🔍 MarkItDown GUI API Documentation Validation")
    print("=" * 50)
    
    docs_dir = Path(__file__).parent
    api_dir = docs_dir / "api"
    
    validation_results = []
    
    # Core documentation files validation
    print("\n📚 Core API Documentation Files:")
    core_files = [
        (api_dir / "overview.rst", "API Overview"),
        (api_dir / "reference.rst", "API Reference"),
        (api_dir / "core" / "index.rst", "Core Modules Index"),
        (api_dir / "core" / "config_manager.rst", "ConfigManager Documentation"),
        (api_dir / "core" / "models.rst", "Data Models Documentation"),
        (api_dir / "ui" / "index.rst", "UI Modules Index"),
        (api_dir / "ui" / "main_window.rst", "MainWindow Documentation"),
    ]
    
    for file_path, description in core_files:
        result = validate_file_exists(file_path, description)
        validation_results.append(result)
        
        if result:
            lines, coverage = count_lines_and_estimate_coverage(file_path)
            print(f"    📊 {lines} lines, ~{coverage:.1f}% documentation coverage")
    
    # Content validation
    print("\n🔍 Content Validation:")
    
    # Validate overview.rst content
    overview_patterns = [
        r"API 개요",
        r"아키텍처 개요",
        r"graphviz",
        r"Core Modules",
        r"UI Components"
    ]
    result = validate_file_content(
        api_dir / "overview.rst", 
        overview_patterns, 
        "Overview Content"
    )
    validation_results.append(result)
    
    # Validate config_manager.rst content
    config_patterns = [
        r"ConfigManager",
        r"autoclass",
        r"automethod",
        r"예제:",
        r"사용 예제"
    ]
    result = validate_file_content(
        api_dir / "core" / "config_manager.rst", 
        config_patterns, 
        "ConfigManager Content"
    )
    validation_results.append(result)
    
    # Validate models.rst content
    models_patterns = [
        r"models 모듈",
        r"FileInfo",
        r"ConversionResult",
        r"AppConfig",
        r"LLMConfig",
        r"autoclass"
    ]
    result = validate_file_content(
        api_dir / "core" / "models.rst", 
        models_patterns, 
        "Models Content"
    )
    validation_results.append(result)
    
    # Validate main_window.rst content
    main_window_patterns = [
        r"MainWindow",
        r"신호.*Signals",
        r"메인 메서드",
        r"이벤트 핸들러",
        r"사용 예제"
    ]
    result = validate_file_content(
        api_dir / "ui" / "main_window.rst", 
        main_window_patterns, 
        "MainWindow Content"
    )
    validation_results.append(result)
    
    # Configuration validation
    print("\n⚙️  Configuration Validation:")
    
    conf_patterns = [
        r"autodoc.*True",
        r"autosummary.*True", 
        r"napoleon.*True",
        r"extensions.*autodoc",
        r"sphinx_rtd_theme"
    ]
    result = validate_file_content(
        docs_dir / "conf.py",
        conf_patterns,
        "Sphinx Configuration"
    )
    validation_results.append(result)
    
    # Cross-references validation
    print("\n🔗 Cross-references Validation:")
    
    # Check for proper cross-references in overview
    if (api_dir / "overview.rst").exists():
        with open(api_dir / "overview.rst", 'r') as f:
            content = f.read()
            
        xref_count = len(re.findall(r':doc:`[^`]+`', content))
        autoclass_count = len(re.findall(r':class:`[^`]+`', content))
        
        if xref_count > 5:
            print(f"✅ Cross-references: {xref_count} doc references found")
            validation_results.append(True)
        else:
            print(f"⚠️  Cross-references: Only {xref_count} doc references found")
            validation_results.append(False)
    
    # Statistics
    print("\n📊 Documentation Statistics:")
    total_files = len([f for f in core_files if f[0].exists()])
    total_lines = 0
    
    for file_path, _ in core_files:
        if file_path.exists():
            lines, _ = count_lines_and_estimate_coverage(file_path)
            total_lines += lines
    
    print(f"📄 Total API documentation files: {total_files}")
    print(f"📝 Total documentation lines: {total_lines}")
    print(f"📚 Average lines per file: {total_lines / total_files if total_files > 0 else 0:.0f}")
    
    # Final assessment
    print("\n🎯 Validation Summary:")
    passed = sum(validation_results)
    total = len(validation_results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 API Documentation is comprehensive and well-structured!")
        status = 0
    elif success_rate >= 60:
        print("⚠️  API Documentation is good but could use improvements")
        status = 0  
    else:
        print("❌ API Documentation needs significant improvements")
        status = 1
    
    # Recommendations
    print("\n💡 Recommendations for Enhancement:")
    if success_rate < 100:
        print("• Add more detailed examples in method documentation")
        print("• Include performance considerations and best practices")
        print("• Add troubleshooting sections for common issues")
        print("• Consider adding tutorial-style documentation")
    
    print("\n✨ API Documentation Validation Complete!")
    return status

if __name__ == "__main__":
    sys.exit(main())
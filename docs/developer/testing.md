# Testing Guide

## Overview

This guide covers comprehensive testing strategies and practices for the MarkItDown GUI application, ensuring reliability, quality, and maintainability through systematic testing approaches.

## Testing Philosophy

### Core Principles
- **Test-Driven Development**: Write tests before implementation
- **Comprehensive Coverage**: Unit, integration, and end-to-end testing
- **Quality Gates**: Automated testing in CI/CD pipeline
- **User-Focused**: Test from user perspective and scenarios

### Quality Standards
- **Unit Test Coverage**: ≥90% for core business logic
- **Integration Test Coverage**: ≥80% for component interactions
- **E2E Test Coverage**: 100% of critical user workflows
- **Performance Tests**: All conversion operations under performance budgets

## Testing Architecture

### Test Categories

#### 1. Unit Tests
**Scope**: Individual functions, classes, and components in isolation

**Structure**:
```
tests/unit/
├── core/
│   ├── test_file_manager.py
│   ├── test_conversion_manager.py
│   ├── test_config_manager.py
│   └── test_utils.py
├── ui/
│   ├── test_main_window.py
│   ├── test_components/
│   │   ├── test_file_list_widget.py
│   │   ├── test_progress_widget.py
│   │   └── test_log_widget.py
└── models/
    └── test_data_models.py
```

**Tools**: pytest, pytest-qt, unittest.mock

#### 2. Integration Tests
**Scope**: Component interactions and system integration

**Structure**:
```
tests/integration/
├── test_ui_core_integration.py
├── test_file_conversion_workflow.py
├── test_config_persistence.py
└── test_error_handling_flow.py
```

**Focus Areas**:
- UI-backend communication
- File system operations
- Configuration management
- Error propagation

#### 3. End-to-End Tests
**Scope**: Complete user workflows and scenarios

**Structure**:
```
tests/e2e/
├── test_complete_conversion_workflow.py
├── test_batch_conversion_scenarios.py
├── test_error_recovery_workflows.py
└── test_ui_navigation_flows.py
```

**Critical Workflows**:
- Directory selection → File scan → Conversion → Results
- Batch conversion with mixed file types
- Error handling and recovery
- Settings configuration and persistence

### Testing Tools & Frameworks

#### Primary Testing Stack
```python
# Core testing framework
pytest==7.4.0
pytest-qt==4.2.0        # PyQt6 testing utilities
pytest-cov==4.1.0       # Coverage reporting
pytest-mock==3.11.1     # Advanced mocking

# Performance testing
pytest-benchmark==4.0.0

# E2E testing support
pytest-xvfb==3.0.0      # Headless display for CI
```

#### PyQt6 Testing Utilities
```python
from pytestqt import qtbot
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

def test_file_selection_widget(qtbot):
    widget = FileListWidget()
    qtbot.addWidget(widget)
    
    # Simulate user interactions
    qtbot.mouseClick(widget.select_all_btn, Qt.LeftButton)
    
    # Verify state changes
    assert widget.get_selected_count() > 0
```

## Test Implementation

### Unit Testing Patterns

#### 1. Core Business Logic Testing
```python
# tests/unit/core/test_conversion_manager.py
import pytest
from unittest.mock import Mock, patch
from markitdown_gui.core.conversion_manager import ConversionManager

class TestConversionManager:
    def setup_method(self):
        self.manager = ConversionManager()
    
    def test_single_file_conversion_success(self):
        # Arrange
        test_file = "test.docx"
        expected_output = "converted markdown content"
        
        # Act
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_md:
            mock_md.return_value.convert.return_value.text_content = expected_output
            result = self.manager.convert_single_file(test_file)
        
        # Assert
        assert result.success is True
        assert result.content == expected_output
        assert result.error is None
    
    def test_conversion_error_handling(self):
        # Arrange
        test_file = "corrupted.pdf"
        
        # Act & Assert
        with patch('markitdown_gui.core.conversion_manager.MarkItDown') as mock_md:
            mock_md.return_value.convert.side_effect = Exception("Conversion failed")
            
            result = self.manager.convert_single_file(test_file)
            assert result.success is False
            assert "Conversion failed" in result.error
```

#### 2. PyQt6 Widget Testing
```python
# tests/unit/ui/components/test_file_list_widget.py
import pytest
from PyQt6.QtCore import Qt
from markitdown_gui.ui.components.file_list_widget import FileListWidget

class TestFileListWidget:
    def test_file_addition(self, qtbot):
        # Arrange
        widget = FileListWidget()
        qtbot.addWidget(widget)
        
        test_files = ["file1.docx", "file2.pdf", "file3.txt"]
        
        # Act
        for file in test_files:
            widget.add_file(file)
        
        # Assert
        assert widget.rowCount() == 3
        assert widget.get_file_at_row(0) == "file1.docx"
    
    def test_selection_functionality(self, qtbot):
        # Arrange
        widget = FileListWidget()
        qtbot.addWidget(widget)
        widget.add_file("test.docx")
        
        # Act
        qtbot.mouseClick(widget.select_all_btn, Qt.LeftButton)
        
        # Assert
        assert widget.get_selected_count() == 1
        assert widget.is_file_selected(0) is True
```

### Integration Testing Patterns

#### 1. UI-Core Integration
```python
# tests/integration/test_conversion_workflow.py
import pytest
from unittest.mock import patch
from markitdown_gui.ui.main_window import MainWindow
from markitdown_gui.core.conversion_manager import ConversionManager

class TestConversionWorkflow:
    @pytest.fixture
    def main_window(self, qtbot):
        window = MainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_full_conversion_workflow(self, main_window, qtbot, tmp_path):
        # Arrange
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()
        test_file = test_dir / "test.txt"
        test_file.write_text("Test content")
        
        # Act - Directory selection
        main_window.directory_widget.set_directory(str(test_dir))
        
        # Act - File scanning
        qtbot.wait(100)  # Wait for async file scan
        
        # Act - Start conversion
        qtbot.mouseClick(main_window.convert_btn, Qt.LeftButton)
        
        # Assert - Verify results
        qtbot.waitUntil(lambda: main_window.conversion_complete, timeout=5000)
        assert main_window.log_widget.get_success_count() == 1
```

### End-to-End Testing

#### 1. Complete User Scenarios
```python
# tests/e2e/test_user_workflows.py
import pytest
import tempfile
from pathlib import Path
from markitdown_gui.main import main

class TestUserWorkflows:
    def test_complete_document_conversion_workflow(self, qtbot):
        """Test the complete user workflow from start to finish"""
        # This would test:
        # 1. Application startup
        # 2. Directory selection
        # 3. File discovery
        # 4. File selection
        # 5. Conversion process
        # 6. Results verification
        # 7. File download/export
        pass
    
    def test_batch_conversion_mixed_formats(self, qtbot):
        """Test batch conversion with multiple file formats"""
        pass
    
    def test_error_recovery_scenarios(self, qtbot):
        """Test application behavior with corrupted files and errors"""
        pass
```

### Performance Testing

#### 1. Conversion Performance Tests
```python
# tests/performance/test_conversion_performance.py
import pytest
from markitdown_gui.core.conversion_manager import ConversionManager

class TestConversionPerformance:
    def test_single_file_conversion_performance(self, benchmark):
        manager = ConversionManager()
        
        # Benchmark single file conversion
        result = benchmark(manager.convert_single_file, "sample_1mb.docx")
        
        # Assert performance requirements
        assert benchmark.stats.stats.mean < 5.0  # < 5 seconds average
    
    def test_batch_conversion_scalability(self):
        """Test batch conversion performance with varying file counts"""
        pass
    
    @pytest.mark.parametrize("file_count", [10, 50, 100])
    def test_memory_usage_scaling(self, file_count):
        """Test memory usage doesn't exceed limits during batch processing"""
        pass
```

## Test Configuration

### pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=markitdown_gui
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    performance: Performance benchmarks
```

### Coverage Configuration
```ini
# .coveragerc
[run]
source = markitdown_gui
omit = 
    */tests/*
    */venv/*
    setup.py
    main.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y xvfb
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        xvfb-run -a pytest tests/unit/ -v --cov=markitdown_gui
    
    - name: Run integration tests
      run: |
        xvfb-run -a pytest tests/integration/ -v
    
    - name: Run E2E tests
      run: |
        xvfb-run -a pytest tests/e2e/ -v --slow
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
```

## Manual Testing

### Test Scenarios Checklist

#### Basic Functionality
- [ ] Application startup and initialization
- [ ] Directory selection and navigation
- [ ] File type detection and filtering
- [ ] Single file conversion
- [ ] Batch file conversion
- [ ] Progress indication and cancellation
- [ ] Error handling and recovery
- [ ] Settings persistence

#### File Format Testing
- [ ] Office documents (.docx, .xlsx, .pptx)
- [ ] PDF files (text and image-based)
- [ ] Image files (jpg, png, gif, etc.)
- [ ] Audio files (mp3, wav)
- [ ] Web/text formats (html, csv, json, xml)
- [ ] Archive files (zip)
- [ ] E-book formats (epub)

#### Edge Cases
- [ ] Empty directories
- [ ] Very large files (>100MB)
- [ ] Corrupted files
- [ ] Files with special characters in names
- [ ] Network drive files
- [ ] Read-only files
- [ ] Insufficient disk space scenarios

#### User Experience
- [ ] UI responsiveness during operations
- [ ] Keyboard shortcuts and accessibility
- [ ] Window resizing and layout
- [ ] Theme switching
- [ ] Language switching (i18n)
- [ ] Help documentation access

## Debugging & Troubleshooting

### Debug Configuration
```python
# conftest.py
import pytest
import logging

@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@pytest.fixture
def debug_mode():
    """Enable debug mode for detailed test output"""
    import os
    os.environ['MARKITDOWN_DEBUG'] = '1'
    yield
    del os.environ['MARKITDOWN_DEBUG']
```

### Common Issues & Solutions

#### PyQt6 Testing Issues
- **Issue**: Tests hanging in CI/CD
- **Solution**: Use `xvfb-run` for headless testing
- **Issue**: QTimer not working in tests
- **Solution**: Use `qtbot.waitUntil()` for async operations

#### Mock Configuration
- **Issue**: External dependencies in tests
- **Solution**: Mock MarkItDown library calls
- **Issue**: File system operations
- **Solution**: Use `tmp_path` fixture for temporary files

## Related Documentation

- 🔧 [Development Setup](setup.md) - Environment configuration
- 🏗️ [Architecture Overview](architecture.md) - System design principles
- 📋 [Coding Standards](coding-standards.md) - Code quality guidelines
- 🤝 [Contributing Guide](../contributing/contributing.md) - Contribution workflow

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development
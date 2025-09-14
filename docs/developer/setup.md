# Development Setup

Complete guide to setting up a development environment for MarkItDown GUI.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Setup](#testing-setup)
- [IDE Configuration](#ide-configuration)
- [Debugging and Profiling](#debugging-and-profiling)

## Prerequisites

### System Requirements

#### Development Platform Support
- **Primary**: Linux (Ubuntu 20.04+, Fedora 35+)
- **Secondary**: macOS 11+ (Big Sur and later)
- **Supported**: Windows 10/11 (WSL recommended)

#### Required Software

**Core Dependencies:**
```bash
# Python 3.8+ (3.11+ recommended)
python --version  # Should show 3.8.0 or higher

# Git for version control
git --version

# Package managers
pip --version
npm --version  # For documentation tools
```

**Development Tools:**
```bash
# Code editors (choose one)
code --version    # VS Code
pycharm --version # PyCharm
vim --version     # Vim/Neovim

# System libraries (Linux)
sudo apt install build-essential python3-dev
sudo apt install libgl1-mesa-glx libxkbcommon-x11-0
```

### Hardware Recommendations

- **CPU**: 4+ cores (8+ recommended for testing)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Storage**: 20 GB free space (SSD recommended)
- **Display**: 1920x1080+ for UI development

## Development Environment Setup

### 1. Repository Setup

#### Clone the Repository
```bash
# Clone with full history
git clone https://github.com/your-org/markitdown-gui.git
cd markitdown-gui

# Or clone with limited history for faster setup
git clone --depth 1 https://github.com/your-org/markitdown-gui.git
cd markitdown-gui
```

#### Configure Git
```bash
# Set up your identity
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Set up Git hooks (optional)
cp scripts/git-hooks/* .git/hooks/
chmod +x .git/hooks/*
```

### 2. Python Environment Setup

#### Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel
```

#### Alternative: Using conda
```bash
# Create conda environment
conda create -n markitdown-gui python=3.11
conda activate markitdown-gui

# Install pip in conda environment
conda install pip
```

### 3. Dependencies Installation

#### Install Development Dependencies
```bash
# Install all dependencies including development tools
pip install -r requirements-dev.txt

# Or install in development mode
pip install -e ".[dev]"
```

#### Verify Installation
```bash
# Test basic imports
python -c "
import PyQt6
import markitdown
import pytest
import black
import flake8
print('All dependencies imported successfully')
"

# Run basic tests
python -m pytest tests/test_basic.py -v
```

### 4. Configuration Setup

#### Development Configuration
```bash
# Create development config directory
mkdir -p ~/.config/markitdown-gui-dev

# Copy development config template
cp config/dev/config.yaml ~/.config/markitdown-gui-dev/

# Set environment variable
export MARKITDOWN_GUI_ENV=development
```

#### Environment Variables
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export MARKITDOWN_GUI_ENV=development
export MARKITDOWN_GUI_LOG_LEVEL=DEBUG
export MARKITDOWN_GUI_CONFIG_DIR=~/.config/markitdown-gui-dev
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Project Structure

### Directory Layout
```
markitdown-gui/
├── markitdown_gui/           # Main application package
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   ├── converter.py
│   │   ├── i18n_manager.py
│   │   └── logger.py
│   ├── ui/                   # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── dialogs/
│   │   └── widgets/
│   ├── models/               # Data models
│   ├── services/             # Business logic services
│   └── utils/                # Utility functions
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── e2e/                  # End-to-end tests
│   └── fixtures/             # Test data
├── docs/                     # Documentation
├── scripts/                  # Build and utility scripts
├── resources/                # Static resources
│   ├── icons/
│   ├── themes/
│   └── translations/
├── config/                   # Configuration files
│   ├── dev/
│   ├── prod/
│   └── test/
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml           # Project configuration
├── pytest.ini              # Test configuration
└── main.py                  # Application entry point
```

### Key Components

#### Core Module (`markitdown_gui/core/`)
- **config_manager.py**: Application configuration management
- **converter.py**: Document conversion engine interface
- **i18n_manager.py**: Internationalization and localization
- **logger.py**: Logging configuration and utilities

#### UI Module (`markitdown_gui/ui/`)
- **main_window.py**: Primary application window
- **dialogs/**: Modal dialogs and popup windows
- **widgets/**: Reusable UI components

#### Testing Structure
- **unit/**: Fast, isolated component tests
- **integration/**: Multi-component interaction tests
- **e2e/**: Full application workflow tests
- **fixtures/**: Sample files and test data

## Development Workflow

### 1. Development Process

#### Feature Development
```bash
# Create feature branch
git checkout -b feature/new-converter-support

# Make changes with incremental commits
git add .
git commit -m "Add initial PDF converter interface"

# Run tests frequently
python -m pytest tests/unit/test_converter.py -v

# Ensure code quality
black markitdown_gui/
flake8 markitdown_gui/
```

#### Code Quality Checks
```bash
# Format code with black
black markitdown_gui/ tests/

# Check style with flake8
flake8 markitdown_gui/ tests/

# Type checking with mypy
mypy markitdown_gui/

# Import sorting with isort
isort markitdown_gui/ tests/
```

#### Running the Application
```bash
# Run in development mode
python main.py

# Run with debug logging
MARKITDOWN_GUI_LOG_LEVEL=DEBUG python main.py

# Run with specific config
MARKITDOWN_GUI_CONFIG_DIR=config/dev python main.py
```

### 2. Testing Workflow

#### Test Categories
```bash
# Unit tests (fast, isolated)
python -m pytest tests/unit/ -v

# Integration tests (moderate speed)
python -m pytest tests/integration/ -v

# End-to-end tests (slow, comprehensive)
python -m pytest tests/e2e/ -v --slow

# All tests
python -m pytest tests/ -v
```

#### Test Coverage
```bash
# Run with coverage
python -m pytest --cov=markitdown_gui tests/

# Generate HTML coverage report
python -m pytest --cov=markitdown_gui --cov-report=html tests/
firefox htmlcov/index.html  # View coverage report
```

### 3. Build and Package

#### Development Build
```bash
# Install in development mode
pip install -e .

# Create development package
python -m build --wheel
```

#### Distribution Package
```bash
# Clean build
python -c "import shutil; shutil.rmtree('dist', ignore_errors=True)"
python -c "import shutil; shutil.rmtree('build', ignore_errors=True)"

# Build packages
python -m build

# Check package
python -m twine check dist/*
```

## Testing Setup

### Test Framework Configuration

#### pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    -ra
    --cov=markitdown_gui
    --cov-branch
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    gui: marks tests that require GUI components
```

### Test Data Management

#### Creating Test Fixtures
```python
# tests/fixtures/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_docx():
    """Provide sample DOCX file for testing."""
    return Path("tests/fixtures/sample.docx")

@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

#### GUI Testing Setup
```python
# tests/conftest.py
import pytest
from PyQt6.QtWidgets import QApplication
from markitdown_gui.ui.main_window import MainWindow

@pytest.fixture(scope="session")
def qapp():
    """Provide QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def main_window(qapp):
    """Provide MainWindow instance for testing."""
    window = MainWindow()
    window.show()
    yield window
    window.close()
```

## IDE Configuration

### Visual Studio Code

#### Recommended Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "ms-python.isort",
    "ms-toolsai.jupyter",
    "ms-vscode.test-adapter-converter",
    "gruntfuggly.todo-tree"
  ]
}
```

#### VS Code Settings (`.vscode/settings.json`)
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

#### Launch Configuration (`.vscode/launch.json`)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "MarkItDown GUI",
      "type": "python",
      "request": "launch",
      "program": "main.py",
      "console": "integratedTerminal",
      "env": {
        "MARKITDOWN_GUI_ENV": "development",
        "MARKITDOWN_GUI_LOG_LEVEL": "DEBUG"
      }
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm Configuration

#### Project Setup
1. **Open Project**: File → Open → Select project directory
2. **Interpreter**: Settings → Python Interpreter → Add → Existing Environment → Select `venv/bin/python`
3. **Code Style**: Settings → Editor → Code Style → Python → Import Black settings
4. **Testing**: Settings → Tools → Python Integrated Tools → Default test runner → pytest

#### Run Configurations
- **Application**: Configuration → Add → Python → Script path: `main.py`
- **Tests**: Configuration → Add → Python tests → pytest → Target: `tests/`

## Debugging and Profiling

### Debugging Setup

#### Using Python Debugger
```python
# Add breakpoints in code
import pdb; pdb.set_trace()

# Or use ipdb for enhanced debugging
import ipdb; ipdb.set_trace()

# Remote debugging with debugpy
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

#### Qt Debugging
```python
# Enable Qt debug output
import os
os.environ['QT_LOGGING_RULES'] = '*=true'

# Qt Inspector (for UI debugging)
from PyQt6.QtCore import QLoggingCategory
QLoggingCategory.setFilterRules('qt.*=true')
```

### Performance Profiling

#### CPU Profiling
```bash
# Profile with cProfile
python -m cProfile -o profile_output.prof main.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile_output.prof')
p.sort_stats('cumulative').print_stats(20)
"

# Visual profiling with snakeviz
pip install snakeviz
snakeviz profile_output.prof
```

#### Memory Profiling
```bash
# Install memory profiler
pip install memory_profiler psutil

# Profile memory usage
python -m memory_profiler main.py

# Line-by-line memory profiling
# Add @profile decorator to functions
python -m memory_profiler --precision 2 main.py
```

#### GUI Performance
```python
# Qt performance monitoring
from PyQt6.QtCore import QElapsedTimer
timer = QElapsedTimer()
timer.start()
# ... code to measure ...
print(f"Elapsed: {timer.elapsed()}ms")
```

### Log Analysis

#### Development Logging
```python
# Configure detailed logging for development
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='debug.log'
)
```

#### Log Analysis Tools
```bash
# Monitor logs in real-time
tail -f ~/.local/share/markitdown-gui/logs/debug.log

# Search for errors
grep -i error ~/.local/share/markitdown-gui/logs/*.log

# Analyze performance issues
grep -E "(slow|timeout|memory)" ~/.local/share/markitdown-gui/logs/*.log
```

---

**Next Steps:**
- 🏗️ [Architecture Overview](architecture.md) - System design
- 📋 [Coding Standards](coding-standards.md) - Code quality guidelines  
- 🧪 [Testing Guide](testing.md) - Comprehensive testing approach
- 🎨 [UI Guidelines](ui-guidelines.md) - Interface design principles
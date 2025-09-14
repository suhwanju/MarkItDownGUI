"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from markitdown_gui.core.config_manager import ConfigManager
from markitdown_gui.core.file_manager import FileManager
from markitdown_gui.core.conversion_manager import ConversionManager


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def config_manager(temp_dir):
    """Create ConfigManager instance with temporary settings"""
    settings = QSettings(str(temp_dir / "test_settings.ini"), QSettings.Format.IniFormat)
    manager = ConfigManager(settings)
    yield manager
    manager.cleanup()


@pytest.fixture
def file_manager(temp_dir):
    """Create FileManager instance"""
    manager = FileManager()
    manager.root_directory = str(temp_dir)
    yield manager


@pytest.fixture
def conversion_manager(config_manager):
    """Create ConversionManager instance"""
    manager = ConversionManager(config_manager)
    yield manager
    manager.cleanup()


@pytest.fixture
def sample_files(temp_dir):
    """Create sample test files"""
    files = {}
    
    # Create test documents
    doc_file = temp_dir / "test.docx"
    doc_file.write_bytes(b"Test document content")
    files['docx'] = doc_file
    
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b"Test PDF content")
    files['pdf'] = pdf_file
    
    img_file = temp_dir / "test.png"
    img_file.write_bytes(b"Test image content")
    files['image'] = img_file
    
    txt_file = temp_dir / "test.txt"
    txt_file.write_text("Test text content")
    files['text'] = txt_file
    
    # Create subdirectory with files
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    
    sub_file = subdir / "nested.md"
    sub_file.write_text("# Nested markdown")
    files['nested'] = sub_file
    
    return files


@pytest.fixture
def mock_markitdown():
    """Mock MarkItDown library"""
    mock = MagicMock()
    mock.convert.return_value = "# Converted Content\n\nTest content"
    mock.convert_local.return_value = "# Local Converted\n\nLocal test"
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="OCR result"))],
        usage=MagicMock(total_tokens=100)
    )
    return mock
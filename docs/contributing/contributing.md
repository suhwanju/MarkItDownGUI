# Contributing Guide

Welcome to MarkItDown GUI! We're excited to have you contribute to this open-source project.

## Table of Contents

- [Getting Started](#getting-started)
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Guidelines](#documentation-guidelines)
- [Community and Support](#community-and-support)

## Getting Started

### Before You Start

1. **Read the documentation** - Familiarize yourself with the project
2. **Check existing issues** - See if your idea or bug is already reported
3. **Join the community** - Connect with other contributors
4. **Set up development environment** - Follow our [Development Setup](../developer/setup.md) guide

### Ways to Contribute

We welcome various types of contributions:

- 🐛 **Bug reports** - Help us find and fix issues
- 🚀 **Feature requests** - Suggest new functionality
- 💻 **Code contributions** - Fix bugs or implement features
- 📚 **Documentation** - Improve guides, API docs, or examples
- 🌍 **Translations** - Add support for new languages
- 🎨 **UI/UX improvements** - Enhance user experience
- 🧪 **Testing** - Write tests or improve test coverage
- 📦 **Package management** - Help with builds and distributions

## Code of Conduct

### Our Commitment

We are committed to providing a welcoming and inclusive experience for everyone, regardless of:
- Background and experience level
- Gender identity and expression
- Sexual orientation
- Disability status
- Personal appearance
- Race, ethnicity, and nationality
- Age or religion

### Expected Behavior

- **Be respectful** and inclusive in all interactions
- **Be collaborative** and help others learn and grow
- **Be constructive** when giving feedback
- **Be patient** with newcomers and questions
- **Focus on what's best** for the community and project

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or inflammatory language
- Trolling, spamming, or disruptive behavior
- Publishing private information without consent
- Any conduct that could be considered inappropriate in a professional setting

### Enforcement

Project maintainers are responsible for clarifying standards and taking appropriate action in response to unacceptable behavior. Report issues to [maintainers@markitdown-gui.org](mailto:maintainers@markitdown-gui.org).

## How to Contribute

### Reporting Bugs

#### Before Submitting
1. **Check existing issues** - Your bug might already be reported
2. **Use the latest version** - Ensure the bug exists in current version
3. **Isolate the problem** - Create a minimal reproduction case

#### Bug Report Template
```markdown
**Bug Description**
Clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 22.04]
- MarkItDown GUI Version: [e.g. 1.0.0]
- Python Version: [e.g. 3.11.0]

**Additional Context**
Screenshots, logs, or other relevant information.

**Sample Files**
If applicable, attach sample files that reproduce the issue.
```

### Requesting Features

#### Feature Request Guidelines
- **Check existing requests** - Avoid duplicates
- **Explain the use case** - Why is this feature needed?
- **Describe the solution** - What would you like to see?
- **Consider alternatives** - Are there other approaches?
- **Estimate impact** - How many users would benefit?

#### Feature Request Template
```markdown
**Feature Summary**
Brief description of the feature.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
Detailed description of the proposed feature.

**Alternative Solutions**
Other approaches you've considered.

**Additional Context**
Screenshots, mockups, or examples.

**Implementation Notes**
Technical considerations (optional).
```

### Contributing Code

#### Development Workflow
1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Set up development environment** (see [Development Setup](../developer/setup.md))
5. **Make your changes** following our coding standards
6. **Write tests** for your changes
7. **Update documentation** as needed
8. **Commit your changes** with clear messages
9. **Push to your fork** and submit a pull request

#### Pull Request Process
1. **Fill out the PR template** completely
2. **Link related issues** using keywords (fixes #123)
3. **Request review** from maintainers
4. **Address feedback** promptly and professionally
5. **Keep PR updated** with main branch if needed
6. **Wait for approval** from at least one maintainer

#### Pull Request Template
```markdown
**Description**
Brief description of changes made.

**Related Issues**
Fixes #(issue number)

**Type of Change**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

**Testing**
- [ ] Tests added/updated for changes
- [ ] All tests pass locally
- [ ] Manual testing completed

**Screenshots/Videos**
If applicable, add screenshots or videos to help explain your changes.

**Checklist**
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated as needed
- [ ] Changes generate no new warnings
```

## Development Process

### Branch Management

#### Branch Types
- **`main`** - Production-ready code, protected branch
- **`develop`** - Integration branch for new features
- **`feature/*`** - Feature development branches
- **`bugfix/*`** - Bug fix branches
- **`hotfix/*`** - Critical fixes for production
- **`release/*`** - Release preparation branches

#### Naming Conventions
```
feature/add-pdf-ocr-support
bugfix/fix-memory-leak-in-converter
hotfix/critical-security-patch
release/v1.2.0
```

#### Git Workflow
```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Work on feature
git add .
git commit -m "Add feature description"

# Keep feature branch updated
git checkout main
git pull origin main
git checkout feature/your-feature-name
git merge main

# Submit pull request
git push origin feature/your-feature-name
# Create PR via GitHub interface
```

### Commit Guidelines

#### Commit Message Format
```
<type>(<scope>): <description>

<body>

<footer>
```

#### Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or modifying tests
- **chore**: Build process or auxiliary tool changes

#### Examples
```
feat(converter): add OCR support for PDF files

- Implement OCR integration using Tesseract
- Add language selection for OCR processing
- Include confidence scoring for text recognition

Closes #123

fix(ui): resolve memory leak in preview widget

The preview widget was not properly disposing of QPixmap
objects, causing memory usage to grow over time.

Fixes #456

docs(api): update conversion API documentation

- Add examples for batch conversion
- Document new OCR parameters
- Fix typos in method descriptions
```

## Coding Standards

### Python Code Style

#### Formatting
- **Formatter**: Black (line length: 88 characters)
- **Import sorting**: isort with Black compatibility
- **Linting**: flake8 with project configuration

#### Code Quality
```python
# Good: Clear, documented, type-annotated
def convert_file(input_path: Path, output_format: str = 'markdown') -> ConversionResult:
    """Convert a file to the specified format.
    
    Args:
        input_path: Path to the input file
        output_format: Target output format
        
    Returns:
        ConversionResult with conversion details
        
    Raises:
        ValidationError: If input file is invalid
        ConversionError: If conversion fails
    """
    if not input_path.exists():
        raise ValidationError(f"File not found: {input_path}")
    
    # Implementation here
    return ConversionResult(...)

# Bad: No type hints, no docstring, unclear naming
def convert(f, fmt='md'):
    if not f.exists():
        raise Exception("not found")
    return do_conversion(f, fmt)
```

#### Type Annotations
```python
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

# Use specific types
def process_files(files: List[Path]) -> Dict[str, ConversionResult]:
    pass

# Use Union for multiple types
def load_config(source: Union[str, Path, Dict[str, Any]]) -> Config:
    pass

# Use Optional for nullable values
def get_converter(format_type: str) -> Optional[IConverter]:
    pass
```

### Documentation Standards

#### Docstring Format (Google Style)
```python
def complex_function(param1: str, param2: int, param3: Optional[bool] = None) -> Dict[str, Any]:
    """Summary line describing the function.
    
    Longer description providing more details about the function's
    purpose and behavior. This can span multiple lines.
    
    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.
        param3: Optional description of third parameter.
            Defaults to None.
    
    Returns:
        Dictionary containing result data with the following keys:
        - 'status': Processing status
        - 'data': Result data
        - 'errors': List of errors if any
    
    Raises:
        ValueError: If param1 is empty.
        TypeError: If param2 is not an integer.
    
    Example:
        >>> result = complex_function("test", 42, True)
        >>> print(result['status'])
        'success'
    
    Note:
        This function is thread-safe and can be called concurrently.
    """
    pass
```

#### Code Comments
```python
# Good: Explain WHY, not WHAT
# Calculate file hash to detect changes since last conversion
file_hash = hashlib.sha256(file_content).hexdigest()

# Use OCR for scanned documents that don't contain text
if not has_extractable_text(file_path):
    content = ocr_engine.extract_text(file_path)

# Bad: Explain obvious things
# Increment counter by one
counter += 1

# Set variable to True
is_valid = True
```

### UI/Qt Standards

#### Widget Organization
```python
class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self) -> None:
        """Initialize user interface components."""
        self._create_widgets()
        self._create_layouts()
        self._setup_menus()
        self._apply_styles()
    
    def _create_widgets(self) -> None:
        """Create UI widgets."""
        # Group related widget creation
        pass
    
    def _create_layouts(self) -> None:
        """Set up widget layouts."""
        # Organize layout setup
        pass
```

#### Signal/Slot Connections
```python
def connect_signals(self) -> None:
    """Connect Qt signals to slots."""
    # Use lambda for simple connections
    self.convert_button.clicked.connect(lambda: self.start_conversion())
    
    # Use partial for connections with parameters
    from functools import partial
    self.file_list.itemChanged.connect(
        partial(self.on_file_item_changed, source='user')
    )
    
    # Use dedicated methods for complex logic
    self.conversion_engine.conversion_completed.connect(
        self.on_conversion_completed
    )
```

## Testing Requirements

### Test Coverage Goals
- **Unit tests**: 90%+ coverage for core functionality
- **Integration tests**: All major user workflows
- **E2E tests**: Critical paths and edge cases
- **Performance tests**: Key operations under load

### Test Organization
```
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_config.py
│   ├── test_converter.py
│   └── test_file_service.py
├── integration/          # Multi-component tests
│   ├── test_conversion_workflow.py
│   └── test_ui_integration.py
├── e2e/                  # End-to-end tests
│   ├── test_full_conversion.py
│   └── test_batch_processing.py
├── performance/          # Performance benchmarks
│   └── test_conversion_speed.py
└── fixtures/            # Test data
    ├── sample_files/
    └── expected_outputs/
```

### Writing Tests
```python
import pytest
from pathlib import Path
from markitdown_gui.core import ConversionEngine

class TestConversionEngine:
    """Test cases for ConversionEngine."""
    
    def test_can_convert_supported_format(self, conversion_engine):
        """Test that engine recognizes supported formats."""
        pdf_file = Path("test.pdf")
        assert conversion_engine.can_convert(pdf_file)
    
    def test_convert_pdf_to_markdown(self, conversion_engine, sample_pdf):
        """Test PDF to Markdown conversion."""
        job = conversion_engine.create_job(sample_pdf)
        result = conversion_engine.convert(job)
        
        assert result.success
        assert result.output_content is not None
        assert "# " in result.output_content  # Has markdown headers
    
    def test_conversion_with_invalid_file(self, conversion_engine):
        """Test error handling for invalid files."""
        invalid_file = Path("nonexistent.pdf")
        
        with pytest.raises(ValidationError):
            conversion_engine.create_job(invalid_file)
    
    @pytest.mark.parametrize("file_format,expected_converter", [
        (".pdf", "PDFConverter"),
        (".docx", "WordConverter"),
        (".pptx", "PowerPointConverter"),
    ])
    def test_converter_selection(self, conversion_engine, file_format, expected_converter):
        """Test correct converter selection by file format."""
        # Test parametrized across multiple formats
        pass
```

### Test Fixtures
```python
# conftest.py
@pytest.fixture
def config():
    """Provide test configuration."""
    return Config(
        theme='light',
        language='en',
        max_file_size=10 * 1024 * 1024  # 10MB for tests
    )

@pytest.fixture
def conversion_engine(config, logger):
    """Provide configured conversion engine."""
    engine = ConversionEngine(config, logger)
    return engine

@pytest.fixture
def sample_pdf(tmp_path):
    """Provide sample PDF file for testing."""
    pdf_path = tmp_path / "sample.pdf"
    # Create minimal PDF for testing
    create_sample_pdf(pdf_path)
    return pdf_path
```

## Documentation Guidelines

### Documentation Types

#### User Documentation
- **Clear and concise** language
- **Task-oriented** approach
- **Screenshots and examples**
- **Multiple skill levels** (beginner to advanced)

#### Developer Documentation
- **Technical accuracy** with code examples
- **API references** with complete signatures
- **Architecture explanations** with diagrams
- **Setup instructions** that work reliably

#### Code Documentation
- **Docstrings** for all public interfaces
- **Inline comments** for complex logic
- **Type annotations** for better tooling
- **Examples** in docstrings

### Writing Style

#### Language Guidelines
- Use **clear, simple language**
- Write in **active voice** when possible
- **Be specific** rather than vague
- **Use consistent terminology**
- **Include examples** for complex concepts

#### Structure Guidelines
- Start with **overview and objectives**
- Use **hierarchical headings** (H1, H2, H3)
- Include **table of contents** for long documents
- Add **cross-references** to related sections
- End with **next steps** or related links

### Documentation Updates

#### When to Update Documentation
- **New features** require user guide updates
- **API changes** need reference documentation updates
- **Bug fixes** may need troubleshooting guide updates
- **Configuration changes** require setup guide updates

#### Review Process
1. **Technical accuracy** review by maintainers
2. **Language and clarity** review by documentation team
3. **User testing** with actual users when possible
4. **Integration** with existing documentation structure

## Community and Support

### Communication Channels

#### GitHub
- **Issues** - Bug reports and feature requests
- **Discussions** - General questions and community discussion
- **Pull Requests** - Code contributions and reviews

#### Documentation
- **User Guide** - Complete usage instructions
- **Developer Docs** - Technical implementation details
- **API Reference** - Complete interface documentation
- **FAQ** - Common questions and solutions

### Getting Help

#### For Users
1. Check the [User Manual](../user-guide/user-manual.md)
2. Review [FAQ](../user-guide/faq.md)
3. Search existing GitHub issues
4. Create new issue with detailed information

#### For Contributors
1. Review [Development Setup](../developer/setup.md)
2. Check [Architecture Overview](../developer/architecture.md)
3. Ask questions in GitHub Discussions
4. Join development discussions

### Recognition

#### Contributors
We recognize contributions in several ways:
- **Contributors list** in README and documentation
- **Release notes** credit for significant contributions
- **GitHub badges** for different types of contributions
- **Community highlights** for exceptional contributions

#### Types of Recognition
- 🐛 **Bug Hunter** - Reported significant bugs
- 🚀 **Feature Champion** - Implemented major features
- 📚 **Documentation Hero** - Improved documentation significantly
- 🌍 **Translation Master** - Added language support
- 🎨 **Design Guru** - Enhanced UI/UX
- 🧪 **Test Engineer** - Improved test coverage
- 💬 **Community Helper** - Helped other contributors

---

**Thank you for contributing to MarkItDown GUI!**

Your contributions make this project better for everyone. Whether you're fixing a typo, adding a feature, or helping other users, every contribution matters.

**Questions?**
- 📖 [Development Setup](../developer/setup.md)
- 🏗️ [Architecture Overview](../developer/architecture.md)
- 🐛 [Issue Templates](issue-templates.md)
- 💬 GitHub Discussions
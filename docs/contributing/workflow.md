# Development Workflow

**Last Updated:** 2025-01-13  
**Version:** 1.0.0

This document outlines the development workflow for the MarkItDown GUI project.

## Table of Contents

1. [Branch Strategy](#branch-strategy)
2. [Development Process](#development-process)
3. [Commit Guidelines](#commit-guidelines)
4. [Pull Request Workflow](#pull-request-workflow)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Requirements](#documentation-requirements)
7. [Release Process](#release-process)

## Branch Strategy

### Main Branches

- **`main`**: Production-ready code
  - Always stable and deployable
  - Protected branch requiring PR approval
  - All commits must pass CI/CD pipeline

- **`develop`**: Integration branch for features
  - Latest development changes
  - Feature branches merge here first
  - Regular integration testing

### Supporting Branches

#### Feature Branches
```
feature/issue-number-short-description
feature/123-add-dark-theme-support
```

- Created from: `develop`
- Merge back to: `develop`
- Naming: `feature/issue-number-description`
- Lifetime: Until feature completion

#### Hotfix Branches
```
hotfix/issue-number-critical-fix
hotfix/456-security-vulnerability-fix
```

- Created from: `main`
- Merge back to: `main` and `develop`
- Naming: `hotfix/issue-number-description`
- Lifetime: Until fix is deployed

#### Release Branches
```
release/version-number
release/1.2.0
```

- Created from: `develop`
- Merge back to: `main` and `develop`
- Naming: `release/version-number`
- Lifetime: Until release is complete

## Development Process

### 1. Issue Creation
```markdown
## Issue Template
**Type**: [Bug/Feature/Enhancement/Documentation]
**Priority**: [Critical/High/Medium/Low]
**Components**: [UI/Core/API/Documentation]

**Description**:
Clear description of the issue or feature request

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Technical Notes**:
Any technical considerations or constraints
```

### 2. Branch Creation
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/123-add-dark-theme

# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/456-security-fix
```

### 3. Development Cycle
```bash
# Regular commits during development
git add .
git commit -m "feat: add dark theme color palette

- Add dark theme color constants
- Implement theme switching logic
- Update UI components for theme support

Closes #123"

# Push to remote branch
git push origin feature/123-add-dark-theme
```

### 4. Testing Requirements
```bash
# Run all tests before pushing
python -m pytest tests/ -v
python -m pytest tests/ui/ --qt-log-level=WARNING
python -m pytest tests/integration/ --slow

# Check code coverage
python -m pytest --cov=src --cov-report=html
```

### 5. Documentation Updates
- Update relevant documentation files
- Add docstrings for new functions/classes
- Update API documentation if applicable
- Add examples for new features

## Commit Guidelines

### Commit Message Format
```
type(scope): brief description

Optional longer description explaining the change in more detail.
Include motivation for the change and contrast with previous behavior.

Closes #issue-number
```

### Commit Types
- **feat**: New feature for the user
- **fix**: Bug fix for the user
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring without changing functionality
- **test**: Adding or updating tests
- **chore**: Changes to build process or auxiliary tools

### Examples
```bash
# Feature commit
git commit -m "feat(ui): add dark theme support

Implement comprehensive dark theme with:
- Dark color palette constants
- Theme switching in settings
- Updated component styling
- Theme persistence in user preferences

Closes #123"

# Bug fix commit
git commit -m "fix(converter): handle empty file conversion

Fix crash when attempting to convert empty files:
- Add file size validation
- Improve error messaging
- Add unit tests for edge case

Fixes #456"

# Documentation commit
git commit -m "docs(api): update plugin development guide

- Add new plugin interface examples
- Update security requirements
- Fix broken internal links

Closes #789"
```

## Pull Request Workflow

### 1. PR Creation
```markdown
## Pull Request Template

### Description
Brief description of changes and motivation

### Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Code coverage maintained/improved

### Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or properly documented)
```

### 2. PR Requirements
- **Title**: Clear, descriptive title
- **Description**: Detailed explanation of changes
- **Tests**: All tests must pass
- **Documentation**: Updated as needed
- **Reviews**: At least one approval required
- **CI/CD**: All checks must pass

### 3. Review Process
```yaml
Review Checklist:
  Code Quality:
    - Follows coding standards
    - Proper error handling
    - No code smells or duplications
    - Appropriate abstractions
  
  Functionality:
    - Meets acceptance criteria
    - No breaking changes
    - Proper input validation
    - Edge cases handled
  
  Testing:
    - Adequate test coverage
    - Tests are meaningful
    - No flaky tests
    - Performance impact considered
  
  Documentation:
    - Code is well-documented
    - API changes documented
    - User-facing changes explained
    - Examples provided where needed
```

### 4. Merge Strategy
```bash
# Squash and merge for feature branches
git checkout develop
git merge --squash feature/123-add-dark-theme
git commit -m "feat(ui): add comprehensive dark theme support (#123)"

# Regular merge for hotfixes to preserve history
git checkout main
git merge --no-ff hotfix/456-security-fix
```

## Testing Requirements

### Pre-Push Testing
```bash
# Complete test suite
make test-all

# Or individual test categories
make test-unit
make test-integration
make test-ui
make test-performance
```

### Test Coverage Requirements
- **Unit Tests**: ≥90% line coverage
- **Integration Tests**: All critical paths covered
- **UI Tests**: Key user workflows tested
- **Performance Tests**: No regression in key metrics

### Testing Checklist
- [ ] All existing tests pass
- [ ] New functionality has tests
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Performance impact assessed
- [ ] UI accessibility tested

## Documentation Requirements

### Code Documentation
```python
def convert_document(file_path: str, output_format: str) -> ConversionResult:
    """Convert document to specified format.
    
    Args:
        file_path: Path to input document
        output_format: Target format (pdf, html, markdown, etc.)
    
    Returns:
        ConversionResult with success status and output path
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        UnsupportedFormatError: If output format not supported
        ConversionError: If conversion fails
    
    Example:
        >>> result = convert_document("input.docx", "pdf")
        >>> if result.success:
        ...     print(f"Converted to: {result.output_path}")
    """
```

### API Documentation
- Update OpenAPI specs for API changes
- Include request/response examples
- Document error conditions and codes
- Provide SDK examples

### User Documentation
- Update user guides for new features
- Add screenshots for UI changes
- Update FAQ with common issues
- Provide migration guides for breaking changes

## Release Process

### Version Numbering
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] Changelog updated
- [ ] Release notes prepared
- [ ] Security review completed
- [ ] Performance benchmarks run
- [ ] Deployment tested in staging

## Tools and Automation

### Development Tools
```bash
# Code formatting
black src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/
pylint src/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

### CI/CD Pipeline
```yaml
# GitHub Actions workflow
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints consistently
- Write self-documenting code
- Keep functions small and focused
- Use meaningful variable names

### Git Practices
- Make atomic commits
- Write descriptive commit messages
- Keep feature branches small
- Rebase feature branches before merging
- Use meaningful branch names

### Collaboration
- Be respectful in code reviews
- Provide constructive feedback
- Ask questions when unclear
- Share knowledge in discussions
- Document decisions and rationale

---

For questions about the development workflow, please:
- Check the [Code Review Guidelines](code-review.md)
- Review the [Release Process](release-process.md)
- Open an issue for workflow improvements
- Contact the development team via project communication channels
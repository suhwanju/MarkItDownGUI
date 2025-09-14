# Release Process

**Last Updated:** 2025-01-13  
**Version:** 1.0.0

This document outlines the comprehensive release process for the MarkItDown GUI project, ensuring consistent, reliable, and secure software delivery.

## Table of Contents

1. [Release Strategy](#release-strategy)
2. [Version Management](#version-management)
3. [Release Types](#release-types)
4. [Pre-Release Process](#pre-release-process)
5. [Release Execution](#release-execution)
6. [Post-Release Process](#post-release-process)
7. [Rollback Procedures](#rollback-procedures)
8. [Release Automation](#release-automation)

## Release Strategy

### Release Philosophy
- **Regular Cadence**: Predictable release schedule
- **Quality First**: Never compromise quality for timeline
- **User Impact**: Minimize disruption to users
- **Transparency**: Clear communication about changes
- **Feedback Integration**: Rapid response to user feedback

### Release Schedule
```yaml
Release Cadence:
  Major Releases: Quarterly (every 3 months)
  Minor Releases: Monthly (feature releases)
  Patch Releases: As needed (bug fixes)
  Hotfixes: Emergency releases (within 24 hours)

Release Windows:
  Major: First Tuesday of quarter (March, June, September, December)
  Minor: Second Tuesday of each month
  Patch: Any Tuesday (with 3-day advance notice)
  Hotfix: Any time (with immediate notification)
```

### Release Environments
```yaml
Development Environment:
  Purpose: Active development and integration
  Branch: develop
  Deployment: Continuous
  Testing: Automated unit and integration tests

Staging Environment:
  Purpose: Pre-production testing and validation
  Branch: release/x.y.z
  Deployment: Release candidates
  Testing: Full test suite + manual testing

Production Environment:
  Purpose: Live user-facing application
  Branch: main
  Deployment: Stable releases only
  Testing: Smoke tests + monitoring
```

## Version Management

### Semantic Versioning
Following [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILDMETADATA]
```

- **MAJOR**: Breaking changes, incompatible API changes
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, backward-compatible fixes
- **PRERELEASE**: alpha, beta, rc (release candidate)
- **BUILDMETADATA**: Build information, commit hash

### Version Examples
```yaml
Production Releases:
  - 1.0.0    # Initial release
  - 1.1.0    # New features added
  - 1.1.1    # Bug fixes
  - 2.0.0    # Breaking changes

Pre-Releases:
  - 1.2.0-alpha.1    # Alpha version
  - 1.2.0-beta.1     # Beta version
  - 1.2.0-rc.1       # Release candidate
  - 1.2.0-rc.2       # Second release candidate
```

### Version File Management
```python
# src/markitdown_gui/version.py
__version__ = "1.1.0"
__build__ = "2025.01.13"
__commit__ = "a1b2c3d4"

# Version information class
class VersionInfo:
    """Application version information."""
    
    MAJOR = 1
    MINOR = 1
    PATCH = 0
    PRERELEASE = None
    BUILD = "2025.01.13"
    
    @classmethod
    def get_version(cls) -> str:
        """Get formatted version string."""
        version = f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"
        if cls.PRERELEASE:
            version += f"-{cls.PRERELEASE}"
        return version
    
    @classmethod
    def get_full_version(cls) -> str:
        """Get full version with build information."""
        version = cls.get_version()
        return f"{version}+{cls.BUILD}.{__commit__[:7]}"
```

## Release Types

### Major Releases (X.0.0)

#### Criteria
- Breaking API changes
- Significant architectural changes
- New major features
- UI/UX overhauls
- Dependency major version updates

#### Planning Timeline
```yaml
Timeline: 12 weeks before release
  Week 1-2:   Requirements gathering and planning
  Week 3-6:   Development and implementation
  Week 7-8:   Alpha testing and feedback
  Week 9-10:  Beta testing and refinement
  Week 11:    Release candidate and final testing
  Week 12:    Production release

Stakeholders:
  - Product Owner: Requirements and priorities
  - Development Team: Implementation and testing
  - QA Team: Quality assurance and validation
  - DevOps Team: Infrastructure and deployment
  - Support Team: Documentation and training
```

#### Breaking Changes Management
```yaml
Breaking Changes Process:
  1. Document all breaking changes
  2. Provide migration guides
  3. Offer backward compatibility where possible
  4. Create migration tools/scripts
  5. Communicate changes well in advance
  6. Provide support during transition

Migration Guide Template:
  - What Changed: Clear description of changes
  - Impact: Who is affected and how
  - Action Required: Steps users must take
  - Timeline: When changes take effect
  - Support: Where to get help
```

### Minor Releases (X.Y.0)

#### Criteria
- New backward-compatible features
- Performance improvements
- Enhanced functionality
- New configuration options
- Dependency minor updates

#### Process
```yaml
Timeline: 4 weeks
  Week 1:   Feature development and unit testing
  Week 2:   Integration testing and documentation
  Week 3:   Release candidate and user testing
  Week 4:   Production release

Quality Gates:
  - All tests pass (>95% coverage)
  - Performance benchmarks maintained
  - Security scan clean
  - Documentation updated
  - Backward compatibility verified
```

### Patch Releases (X.Y.Z)

#### Criteria
- Bug fixes
- Security patches
- Performance fixes
- Minor documentation updates
- Dependency patch updates

#### Process
```yaml
Timeline: 1-2 weeks
  Days 1-3:  Development and testing
  Days 4-5:  Validation and preparation
  Day 6:     Release candidate
  Day 7:     Production release

Expedited Process (Critical):
  - Same day for security issues
  - 24-48 hours for critical bugs
  - Skip non-essential processes
  - Immediate notification to users
```

### Hotfix Releases

#### Criteria
- Critical security vulnerabilities
- Data corruption bugs
- Application crashes
- Service outages
- Compliance issues

#### Emergency Process
```yaml
Immediate Response (0-4 hours):
  - Incident assessment and triage
  - Fix development and testing
  - Emergency review process
  - Hotfix deployment preparation

Rapid Deployment (4-24 hours):
  - Deploy to staging for validation
  - Smoke tests and verification
  - Production deployment
  - User notification and monitoring

Follow-up (24-48 hours):
  - Root cause analysis
  - Process improvement
  - Communication to stakeholders
  - Documentation updates
```

## Pre-Release Process

### Release Planning
```yaml
Release Planning Meeting:
  Attendees: Product Owner, Tech Lead, QA Lead, DevOps Lead
  Agenda:
    - Review completed features
    - Assess release readiness
    - Identify potential risks
    - Plan release timeline
    - Assign responsibilities

Release Readiness Criteria:
  Development:
    - [ ] All planned features completed
    - [ ] Code review completed for all changes
    - [ ] Unit tests pass (>95% coverage)
    - [ ] Integration tests pass
    - [ ] No critical or high-severity bugs

  Quality Assurance:
    - [ ] Functional testing completed
    - [ ] Performance testing passed
    - [ ] Security testing completed
    - [ ] Usability testing feedback incorporated
    - [ ] Compatibility testing passed

  Documentation:
    - [ ] User documentation updated
    - [ ] API documentation updated
    - [ ] Release notes prepared
    - [ ] Migration guides created (if needed)
    - [ ] Known issues documented

  Infrastructure:
    - [ ] Deployment scripts tested
    - [ ] Database migrations tested
    - [ ] Rollback procedures verified
    - [ ] Monitoring and alerting configured
    - [ ] Performance baselines established
```

### Feature Freeze
```yaml
Feature Freeze Timeline:
  Major Release: 2 weeks before release date
  Minor Release: 1 week before release date
  Patch Release: 3 days before release date

After Feature Freeze:
  Allowed:
    - Bug fixes
    - Documentation updates
    - Test improvements
    - Performance optimizations (non-risky)

  Not Allowed:
    - New features
    - Refactoring (unless fixing bugs)
    - Dependency updates (unless critical)
    - UI changes (unless fixing bugs)
```

### Testing Strategy
```yaml
Testing Phases:
  Unit Testing:
    - Automated test suite execution
    - Code coverage verification (>95%)
    - Performance unit tests
    - Mock integration points

  Integration Testing:
    - API endpoint testing
    - Database integration testing
    - External service integration
    - Cross-component interaction testing

  System Testing:
    - End-to-end workflow testing
    - Performance and load testing
    - Security penetration testing
    - Compatibility testing

  User Acceptance Testing:
    - Feature validation with stakeholders
    - Usability testing with real users
    - Accessibility testing
    - Mobile device testing

Testing Environments:
  Development: Continuous testing during development
  Integration: Automated testing on every commit
  Staging: Full test suite execution
  Production: Smoke tests and monitoring
```

## Release Execution

### Release Candidate Process
```yaml
RC Creation:
  1. Create release branch from develop
     git checkout develop
     git pull origin develop
     git checkout -b release/1.2.0

  2. Update version numbers
     - Update src/markitdown_gui/version.py
     - Update setup.py or pyproject.toml
     - Update documentation version references

  3. Generate changelog
     python scripts/generate_changelog.py --version 1.2.0

  4. Create release candidate
     git add .
     git commit -m "chore: prepare release 1.2.0-rc.1"
     git tag -a v1.2.0-rc.1 -m "Release candidate 1.2.0-rc.1"

  5. Deploy to staging
     git push origin release/1.2.0
     git push origin v1.2.0-rc.1
```

### Release Validation
```yaml
RC Validation Checklist:
  Functionality:
    - [ ] All features work as expected
    - [ ] No regressions identified
    - [ ] Performance meets benchmarks
    - [ ] Error handling works correctly

  Integration:
    - [ ] Database operations function correctly
    - [ ] External APIs respond properly
    - [ ] File operations work as expected
    - [ ] UI components render correctly

  Security:
    - [ ] Authentication works properly
    - [ ] Authorization controls function
    - [ ] Input validation prevents attacks
    - [ ] Sensitive data is protected

  Performance:
    - [ ] Application startup time acceptable
    - [ ] Memory usage within limits
    - [ ] Response times meet requirements
    - [ ] Resource cleanup works properly
```

### Production Deployment
```yaml
Deployment Process:
  Pre-Deployment:
    1. Verify staging environment matches production
    2. Create database backup (if applicable)
    3. Prepare rollback plan
    4. Notify stakeholders of deployment window
    5. Disable non-critical scheduled tasks

  Deployment Steps:
    1. Merge release branch to main
       git checkout main
       git merge --no-ff release/1.2.0
       git tag -a v1.2.0 -m "Release version 1.2.0"

    2. Build and package application
       python setup.py sdist bdist_wheel
       docker build -t markitdown-gui:1.2.0 .

    3. Deploy to production
       # Using deployment automation
       ./scripts/deploy.sh --version 1.2.0 --environment production

    4. Run database migrations (if needed)
       python manage.py migrate --settings=production

    5. Restart application services
       systemctl restart markitdown-gui
       systemctl restart markitdown-gui-worker

  Post-Deployment:
    1. Verify application is running
    2. Run smoke tests
    3. Check monitoring dashboards
    4. Enable scheduled tasks
    5. Notify stakeholders of successful deployment
```

### Smoke Tests
```python
# smoke_tests.py - Critical functionality verification
import requests
import pytest
from pathlib import Path

def test_application_startup():
    """Verify application starts and responds."""
    response = requests.get("http://localhost:8080/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_basic_conversion():
    """Test basic document conversion functionality."""
    test_file = Path("tests/fixtures/sample.txt")
    
    with open(test_file, "rb") as f:
        files = {"file": f}
        data = {"output_format": "pdf"}
        
        response = requests.post(
            "http://localhost:8080/convert",
            files=files,
            data=data
        )
    
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]

def test_user_interface_loads():
    """Verify main UI components load."""
    from src.markitdown_gui.main_window import MainWindow
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    
    assert window.windowTitle() == "MarkItDown GUI"
    assert window.isVisible() is False  # Not shown in test
    
    window.show()
    assert window.isVisible() is True
```

## Post-Release Process

### Release Announcement
```markdown
# Release Announcement Template

## MarkItDown GUI v1.2.0 Released

We're excited to announce the release of MarkItDown GUI v1.2.0! This release includes several new features, improvements, and bug fixes.

### New Features
- **Dark Theme Support**: New dark theme option in preferences
- **Batch Conversion**: Convert multiple files simultaneously
- **Progress Tracking**: Real-time conversion progress indicators

### Improvements
- **Performance**: 40% faster PDF conversion
- **Memory Usage**: Reduced memory consumption by 25%
- **User Interface**: Improved accessibility and keyboard navigation

### Bug Fixes
- Fixed crash when converting empty files
- Resolved memory leak in long-running conversions
- Fixed UI freezing during large file processing

### Breaking Changes
None in this release.

### Download
- [Windows Installer](https://releases.example.com/v1.2.0/MarkItDown-GUI-1.2.0-win64.exe)
- [macOS Package](https://releases.example.com/v1.2.0/MarkItDown-GUI-1.2.0-macos.pkg)
- [Linux AppImage](https://releases.example.com/v1.2.0/MarkItDown-GUI-1.2.0-linux.AppImage)

### Support
For questions or issues, please:
- Check the [User Guide](../user-guide/user-manual.md)
- Report bugs on [GitHub Issues](https://github.com/example/markitdown-gui/issues)
- Join our [Community Forum](https://forum.example.com/markitdown-gui)
```

### Release Monitoring
```yaml
Post-Release Monitoring:
  Immediate (0-2 hours):
    - Application startup and basic functionality
    - Error rate monitoring
    - Performance baseline verification
    - User feedback monitoring

  Short-term (2-24 hours):
    - Feature usage analytics
    - Performance trend analysis
    - Support ticket volume
    - User sentiment tracking

  Medium-term (1-7 days):
    - Crash report analysis
    - Performance degradation detection
    - Feature adoption rates
    - User feedback analysis

  Long-term (1-4 weeks):
    - Overall stability assessment
    - Performance improvement validation
    - User satisfaction surveys
    - Feature usage patterns
```

### Release Metrics
```yaml
Key Performance Indicators:
  Deployment Metrics:
    - Deployment success rate: >99%
    - Deployment time: <30 minutes
    - Rollback frequency: <5%

  Quality Metrics:
    - Post-release defect rate: <2%
    - Critical bug frequency: <0.5%
    - User-reported issues: <10 per week

  Performance Metrics:
    - Application availability: >99.9%
    - Response time degradation: <10%
    - Memory usage increase: <15%

  User Experience:
    - User adoption rate: >80% within 30 days
    - Support ticket increase: <20%
    - User satisfaction score: >4.0/5.0
```

## Rollback Procedures

### Rollback Triggers
```yaml
Automatic Rollback Triggers:
  - Application fails to start
  - Error rate >5% within first hour
  - Critical functionality broken
  - Data corruption detected
  - Security breach identified

Manual Rollback Triggers:
  - Performance degradation >50%
  - User-reported critical issues >10/hour
  - Major feature completely broken
  - Business impact assessment requires rollback
```

### Rollback Process
```yaml
Emergency Rollback (0-15 minutes):
  1. Identify issue severity
  2. Make rollback decision
  3. Execute rollback procedure
  4. Verify system stability
  5. Communicate to stakeholders

Rollback Steps:
  1. Stop current application
     systemctl stop markitdown-gui
     systemctl stop markitdown-gui-worker

  2. Revert to previous version
     docker pull markitdown-gui:1.1.0
     ./scripts/deploy.sh --version 1.1.0 --environment production

  3. Rollback database (if needed)
     python manage.py migrate app_name 0001 --settings=production

  4. Restart services
     systemctl start markitdown-gui
     systemctl start markitdown-gui-worker

  5. Verify rollback success
     ./scripts/smoke_test.sh
     curl -f http://localhost:8080/health

Post-Rollback:
  - Document rollback reason and process
  - Analyze root cause of issues
  - Plan hotfix or next release
  - Communicate resolution plan
```

### Rollback Validation
```python
# rollback_validation.py
def validate_rollback():
    """Validate successful rollback to previous version."""
    
    # Check application version
    response = requests.get("http://localhost:8080/version")
    version = response.json()["version"]
    assert version == "1.1.0", f"Expected version 1.1.0, got {version}"
    
    # Check basic functionality
    health_response = requests.get("http://localhost:8080/health")
    assert health_response.status_code == 200
    
    # Check database consistency
    db_response = requests.get("http://localhost:8080/api/status")
    assert db_response.json()["database"] == "connected"
    
    print("Rollback validation successful")
```

## Release Automation

### CI/CD Pipeline
```yaml
# .github/workflows/release.yml
name: Release Pipeline

on:
  push:
    tags:
      - 'v*'

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
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: 3.11
      - name: Build application
        run: |
          pip install build
          python -m build
      - name: Create distribution
        run: python scripts/create_distribution.py --os ${{ matrix.os }}
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: distributions-${{ matrix.os }}
          path: dist/

  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
          draft: false
          prerelease: ${{ contains(github.ref, '-') }}
```

### Automated Testing
```python
# scripts/automated_release_test.py
import subprocess
import sys
from pathlib import Path

def run_release_tests():
    """Run comprehensive release validation tests."""
    
    test_suites = [
        "pytest tests/unit/ -v",
        "pytest tests/integration/ -v",
        "pytest tests/ui/ --qt-log-level=WARNING",
        "pytest tests/performance/ --benchmark-only",
        "pytest tests/security/ -v"
    ]
    
    for test_suite in test_suites:
        print(f"Running: {test_suite}")
        result = subprocess.run(test_suite.split(), capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Test suite failed: {test_suite}")
            print(f"Error: {result.stderr}")
            return False
        
        print(f"✓ Passed: {test_suite}")
    
    print("All release tests passed!")
    return True

if __name__ == "__main__":
    success = run_release_tests()
    sys.exit(0 if success else 1)
```

### Release Scripts
```bash
#!/bin/bash
# scripts/create_release.sh - Automated release creation script

set -e

VERSION=$1
RELEASE_TYPE=${2:-"minor"}

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version> [release_type]"
    echo "Example: $0 1.2.0 minor"
    exit 1
fi

echo "Creating release $VERSION ($RELEASE_TYPE)"

# Validate current state
echo "Validating repository state..."
git fetch origin
git status --porcelain | grep -q . && echo "Working directory not clean" && exit 1

# Create release branch
echo "Creating release branch..."
git checkout develop
git pull origin develop
git checkout -b "release/$VERSION"

# Update version files
echo "Updating version files..."
python scripts/update_version.py --version "$VERSION"

# Generate changelog
echo "Generating changelog..."
python scripts/generate_changelog.py --version "$VERSION"

# Run tests
echo "Running release tests..."
python scripts/automated_release_test.py

# Create release commit
echo "Creating release commit..."
git add .
git commit -m "chore: prepare release $VERSION"

# Create and push tag
echo "Creating release tag..."
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "release/$VERSION"
git push origin "v$VERSION"

echo "Release $VERSION created successfully!"
echo "Monitor CI/CD pipeline: https://github.com/example/markitdown-gui/actions"
```

## Release Communication

### Stakeholder Notification
```yaml
Communication Plan:
  Pre-Release (1 week):
    - Development team: Release candidate available
    - QA team: Final testing request
    - Product team: Release notes review
    - Support team: Documentation review

  Release Day:
    - All teams: Release deployment notification
    - Users: Release announcement
    - Partners: API changes notification (if any)
    - Community: Social media and forum posts

  Post-Release (24-48 hours):
    - Stakeholders: Release status update
    - Users: Success metrics and feedback request
    - Support team: Known issues and workarounds
    - Development team: Post-mortem scheduling
```

### Release Documentation
```yaml
Required Documentation:
  Release Notes:
    - New features and improvements
    - Bug fixes and resolved issues
    - Breaking changes and migration guides
    - Known issues and workarounds

  Technical Documentation:
    - API changes documentation
    - Configuration changes
    - Database schema updates
    - Deployment procedure updates

  User Documentation:
    - Feature usage guides
    - Updated screenshots and examples
    - FAQ updates
    - Troubleshooting guides
```

---

For questions about the release process, please:
- Review the [Development Workflow](workflow.md) for development procedures
- Check the [Code Review Guidelines](code-review.md) for quality standards
- Contact the release team for specific release concerns
- Escalate critical issues to the development team lead
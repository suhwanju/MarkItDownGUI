# Deployment Guide

Complete guide for deploying MarkItDown GUI in production environments.

## Table of Contents

- [Deployment Overview](#deployment-overview)
- [Preparation](#preparation)
- [Deployment Methods](#deployment-methods)
- [Environment Configuration](#environment-configuration)
- [Security Considerations](#security-considerations)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Deployment Overview

### Deployment Models

#### Standalone Application
- **Distribution**: Pre-built executables for Windows, macOS, Linux
- **Installation**: User installs locally on their machine
- **Updates**: Manual download or auto-update mechanism
- **Best for**: Individual users, small teams

#### Enterprise Installation
- **Distribution**: MSI/PKG/DEB packages for IT deployment
- **Configuration**: Centralized configuration management
- **Updates**: Managed through enterprise update systems
- **Best for**: Large organizations, managed environments

#### Portable Version
- **Distribution**: Self-contained archive (ZIP/TAR)
- **Installation**: Extract and run, no system integration
- **Configuration**: Local configuration files
- **Best for**: Temporary use, restricted environments

## Preparation

### Build Requirements

#### Development Environment
```bash
# Required tools
python 3.8+
PyQt6
cx_Freeze or PyInstaller
NSIS (Windows) / pkgbuild (macOS) / dpkg (Linux)

# Build dependencies
pip install build wheel setuptools
pip install cx_Freeze pyinstaller
```

#### Build Scripts
```bash
# scripts/build.py
#!/usr/bin/env python3
"""Build script for MarkItDown GUI."""

import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build standalone executable."""
    if sys.platform == "win32":
        build_windows()
    elif sys.platform == "darwin":
        build_macos()
    else:
        build_linux()

def build_windows():
    """Build Windows executable."""
    subprocess.run([
        "pyinstaller",
        "--windowed",
        "--onefile",
        "--name=MarkItDown-GUI",
        "--icon=resources/icons/app_icon.ico",
        "main.py"
    ])

def build_macos():
    """Build macOS app bundle."""
    subprocess.run([
        "pyinstaller",
        "--windowed",
        "--onefile",
        "--name=MarkItDown-GUI",
        "--icon=resources/icons/app_icon.icns",
        "main.py"
    ])

def build_linux():
    """Build Linux executable."""
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--name=markitdown-gui",
        "main.py"
    ])

if __name__ == "__main__":
    build_executable()
```

### Asset Preparation

#### Application Icons
```
resources/icons/
├── app_icon.ico     # Windows icon (16x16 to 256x256)
├── app_icon.icns    # macOS icon bundle
├── app_icon.png     # Linux icon (various sizes)
└── installer_icon.* # Installer-specific icons
```

#### Documentation Bundle
```
resources/docs/
├── README.txt       # Plain text version
├── LICENSE.txt      # License text
├── CHANGELOG.txt    # Version history
└── THIRD_PARTY.txt  # Third-party licenses
```

## Deployment Methods

### Method 1: PyInstaller Build

#### Configuration (`markitdown-gui.spec`)
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('markitdown_gui/ui/themes', 'markitdown_gui/ui/themes'),
        ('markitdown_gui/locales', 'markitdown_gui/locales'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'markitdown',
        'PIL',
        'python-magic'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MarkItDown-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico'
)
```

#### Build Process
```bash
# Clean previous builds
rm -rf build/ dist/

# Build executable
pyinstaller markitdown-gui.spec

# Test executable
./dist/MarkItDown-GUI

# Create installer (platform-specific)
scripts/create_installer.sh
```

### Method 2: cx_Freeze Build

#### Setup Configuration (`setup_freeze.py`)
```python
import sys
from cx_Freeze import setup, Executable

# Dependencies to include
build_options = {
    'packages': [
        'PyQt6',
        'markitdown',
        'PIL',
        'yaml',
        'chardet'
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy'
    ],
    'include_files': [
        ('resources/', 'resources/'),
        ('markitdown_gui/locales/', 'markitdown_gui/locales/'),
        ('markitdown_gui/ui/themes/', 'markitdown_gui/ui/themes/'),
    ]
}

# Executable configuration
if sys.platform == 'win32':
    executables = [
        Executable(
            'main.py',
            base='Win32GUI',
            target_name='MarkItDown-GUI.exe',
            icon='resources/icons/app_icon.ico'
        )
    ]
elif sys.platform == 'darwin':
    executables = [
        Executable(
            'main.py',
            base='Console',
            target_name='MarkItDown-GUI',
            icon='resources/icons/app_icon.icns'
        )
    ]
else:
    executables = [
        Executable(
            'main.py',
            base='Console',
            target_name='markitdown-gui'
        )
    ]

setup(
    name='MarkItDown GUI',
    version='1.0.0',
    description='Document conversion tool with GUI',
    options={'build_exe': build_options},
    executables=executables
)
```

### Method 3: Package Distribution

#### Python Package (`setup.py`)
```python
from setuptools import setup, find_packages
from pathlib import Path

# Read README and requirements
README = (Path(__file__).parent / "README.md").read_text()
REQUIREMENTS = (Path(__file__).parent / "requirements.txt").read_text().splitlines()

setup(
    name="markitdown-gui",
    version="1.0.0",
    description="GUI application for MarkItDown document converter",
    long_description=README,
    long_description_content_type="text/markdown",
    author="MarkItDown GUI Team",
    author_email="team@markitdown-gui.org",
    url="https://github.com/your-org/markitdown-gui",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'markitdown_gui': [
            'ui/themes/*.qss',
            'locales/*.qm',
            'resources/icons/*.png',
            'resources/icons/*.ico',
            'resources/icons/*.icns',
        ]
    },
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': [
            'pytest>=7.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.950',
            'pytest-cov>=3.0',
            'pytest-qt>=4.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'markitdown-gui=markitdown_gui.main:main',
        ],
        'gui_scripts': [
            'markitdown-gui=markitdown_gui.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
)
```

## Environment Configuration

### Production Configuration

#### Configuration Template (`config/production.yaml`)
```yaml
# Production configuration for MarkItDown GUI
app:
  name: "MarkItDown GUI"
  version: "1.0.0"
  environment: "production"
  debug: false

ui:
  theme: "auto"
  language: "auto"
  check_updates: true
  telemetry_enabled: false

conversion:
  default_output_format: "markdown"
  max_file_size: 104857600  # 100MB
  worker_threads: 4
  enable_ocr: true
  ocr_language: "eng"
  cache_enabled: true
  cache_size: 50

logging:
  level: "INFO"
  file: "logs/markitdown-gui.log"
  max_file_size: 10485760  # 10MB
  backup_count: 5
  console_output: false

security:
  allowed_extensions:
    - ".pdf"
    - ".docx"
    - ".pptx"
    - ".xlsx"
    - ".html"
    - ".txt"
  scan_files: true
  quarantine_suspicious: true

updates:
  check_interval: 86400  # 24 hours
  auto_download: false
  update_url: "https://updates.markitdown-gui.org/"
```

### Environment Variables

#### Production Environment
```bash
# Application settings
export MARKITDOWN_GUI_ENV=production
export MARKITDOWN_GUI_CONFIG_FILE=/etc/markitdown-gui/config.yaml
export MARKITDOWN_GUI_DATA_DIR=/var/lib/markitdown-gui
export MARKITDOWN_GUI_LOG_DIR=/var/log/markitdown-gui

# Performance settings
export MARKITDOWN_GUI_WORKER_THREADS=4
export MARKITDOWN_GUI_MAX_FILE_SIZE=104857600

# Security settings
export MARKITDOWN_GUI_ENABLE_TELEMETRY=false
export MARKITDOWN_GUI_AUTO_UPDATE=false

# Debugging (development only)
export MARKITDOWN_GUI_DEBUG=false
export MARKITDOWN_GUI_LOG_LEVEL=INFO
```

### Directory Structure

#### Production Layout
```
/opt/markitdown-gui/          # Application installation
├── bin/
│   └── markitdown-gui        # Main executable
├── lib/                      # Application libraries
├── share/
│   ├── icons/               # Application icons
│   ├── themes/              # UI themes
│   ├── translations/        # Language files
│   └── docs/                # Documentation

/etc/markitdown-gui/          # Configuration
├── config.yaml              # Main configuration
├── logging.conf             # Logging configuration
└── security.policy         # Security policies

/var/lib/markitdown-gui/      # Application data
├── cache/                   # Conversion cache
├── temp/                    # Temporary files
└── user-data/              # User-specific data

/var/log/markitdown-gui/      # Log files
├── application.log          # Main application log
├── conversion.log           # Conversion operations
└── security.log            # Security events
```

## Security Considerations

### Application Security

#### Code Signing

**Windows Code Signing:**
```powershell
# Sign executable with certificate
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com MarkItDown-GUI.exe

# Verify signature
signtool verify /pa MarkItDown-GUI.exe
```

**macOS Code Signing:**
```bash
# Sign application bundle
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" MarkItDown-GUI.app

# Verify signature
codesign --verify --verbose MarkItDown-GUI.app
spctl -a -v MarkItDown-GUI.app
```

**Linux Package Signing:**
```bash
# Sign Debian package
debsign -k YOUR_GPG_KEY package.deb

# Verify signature
dpkg-sig --verify package.deb
```

#### Sandboxing

**Application Sandboxing (macOS):**
```xml
<!-- Info.plist entitlements -->
<key>com.apple.security.app-sandbox</key>
<true/>
<key>com.apple.security.files.user-selected.read-write</key>
<true/>
<key>com.apple.security.network.client</key>
<true/>
```

**Security Policies:**
```python
# security_manager.py
class SecurityManager:
    """Application security manager."""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.html'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate file for security."""
        # Check extension
        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            return False
        
        # Check size
        if file_path.stat().st_size > self.MAX_FILE_SIZE:
            return False
        
        # Scan for malware (if available)
        if self.antivirus_available():
            return self.scan_file(file_path)
        
        return True
```

### Data Protection

#### Privacy Protection
```python
# privacy_manager.py
class PrivacyManager:
    """Protect user privacy and data."""
    
    def anonymize_logs(self, log_content: str) -> str:
        """Remove sensitive information from logs."""
        import re
        
        # Remove file paths
        log_content = re.sub(r'/[^\s]+', '[PATH_REDACTED]', log_content)
        
        # Remove potential email addresses
        log_content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                           '[EMAIL_REDACTED]', log_content)
        
        return log_content
    
    def secure_temp_files(self) -> None:
        """Ensure temporary files are properly secured."""
        import tempfile
        import stat
        
        # Create secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix='markitdown_secure_')
        
        # Set restrictive permissions (owner only)
        os.chmod(temp_dir, stat.S_IRWXU)
        
        return temp_dir
```

## Monitoring and Maintenance

### Health Monitoring

#### Application Health Check
```python
# health_monitor.py
class HealthMonitor:
    """Monitor application health and performance."""
    
    def __init__(self):
        self.metrics = {}
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'available_memory': psutil.virtual_memory().available
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Verify critical dependencies are available."""
        dependencies = {}
        
        try:
            import PyQt6
            dependencies['PyQt6'] = True
        except ImportError:
            dependencies['PyQt6'] = False
        
        try:
            import markitdown
            dependencies['markitdown'] = True
        except ImportError:
            dependencies['markitdown'] = False
        
        return dependencies
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_resources': self.check_system_resources(),
            'dependencies': self.check_dependencies(),
            'application_status': 'healthy'  # Based on checks
        }
```

### Logging and Analytics

#### Structured Logging
```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'structured': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s | %(pathname)s:%(lineno)d'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'structured',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/markitdown-gui.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

### Update Management

#### Auto-Update System
```python
# update_manager.py
class UpdateManager:
    """Handle application updates."""
    
    def __init__(self, config: Config):
        self.config = config
        self.update_url = config.update_url
        self.current_version = config.version
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """Check for available updates."""
        try:
            import requests
            response = requests.get(f"{self.update_url}/version.json")
            version_info = response.json()
            
            if self._is_newer_version(version_info['version']):
                return version_info
        except Exception as e:
            logger.error(f"Update check failed: {e}")
        
        return None
    
    def download_update(self, update_info: Dict[str, Any]) -> Optional[Path]:
        """Download update package."""
        import requests
        
        download_url = update_info['download_url']
        filename = update_info['filename']
        
        # Download to temp directory
        temp_dir = Path(tempfile.gettempdir())
        download_path = temp_dir / filename
        
        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        return download_path
```

## Troubleshooting

### Common Deployment Issues

#### Permission Problems
```bash
# Linux: Fix executable permissions
chmod +x /opt/markitdown-gui/bin/markitdown-gui

# Linux: Fix directory permissions
chown -R markitdown:markitdown /var/lib/markitdown-gui
chmod 755 /var/lib/markitdown-gui

# Windows: Run as administrator for system-wide installation
# macOS: Remove quarantine for downloaded applications
xattr -d com.apple.quarantine MarkItDown-GUI.app
```

#### Missing Dependencies
```bash
# Check for missing system libraries (Linux)
ldd markitdown-gui

# Install missing Qt libraries
sudo apt install qt6-base-dev qt6-tools-dev

# Windows: Redistribute Visual C++ runtime
# Include vcredist_x64.exe in installer

# macOS: Check for missing frameworks
otool -L MarkItDown-GUI
```

#### Configuration Issues
```bash
# Reset configuration to defaults
rm ~/.config/markitdown-gui/config.yaml

# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Validate configuration values
markitdown-gui --validate-config
```

### Performance Optimization

#### Resource Usage
```bash
# Monitor resource usage
top -p $(pgrep markitdown-gui)
htop -p $(pgrep markitdown-gui)

# Check memory usage
ps aux | grep markitdown-gui
pmap $(pgrep markitdown-gui)

# Analyze startup time
time markitdown-gui --help
strace -c markitdown-gui --help  # Linux
```

#### Optimization Settings
```yaml
# Performance-optimized configuration
conversion:
  worker_threads: 8      # Increase for faster processing
  cache_enabled: true    # Enable result caching
  cache_size: 100       # Larger cache for frequent files

ui:
  hardware_acceleration: true
  reduce_animations: false
  lazy_loading: true

logging:
  level: "WARNING"      # Reduce log verbosity
  async_logging: true   # Non-blocking logging
```

---

**Related Documentation:**
- ⚙️ [Configuration Management](configuration.md) - Settings and options
- 🔒 [Security Guidelines](security.md) - Security best practices
- 📊 [Performance Tuning](performance.md) - Optimization strategies
- 📋 [Monitoring](monitoring.md) - System monitoring and alerts
# Installation Guide

Complete installation instructions for MarkItDown GUI across different platforms and scenarios.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Advanced Installation](#advanced-installation)
- [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements

- **Operating System**: 
  - Windows 10 (Build 19041) or Windows 11
  - macOS 11.0 (Big Sur) or later
  - Linux distributions with glibc 2.28+ (Ubuntu 20.04+, CentOS 8+, Fedora 32+)
- **Python**: 3.10 or higher (aligned with markitdown core requirements)
- **Memory**: 4 GB RAM (8 GB recommended for large document processing)
- **Storage**: 1 GB available space (includes dependencies and temp files)
- **Display**: 1024x768 resolution minimum
- **Network**: Internet connection for initial setup and updates

### Recommended Requirements

- **Operating System**: Latest stable versions with security updates
- **Python**: 3.11 or 3.12 (best performance and compatibility)
- **Memory**: 8 GB RAM or more (16 GB for enterprise use)
- **Storage**: 2 GB available space (allows for document cache and logs)
- **Display**: 1920x1080 or higher resolution (4K/Retina supported)
- **Graphics**: Hardware acceleration support for smooth UI
- **CPU**: Multi-core processor for concurrent document processing

### Dependencies

#### Core Dependencies (Automatically Installed)
- **PyQt6** (≥6.5.0): Modern GUI framework with native look and feel
- **markitdown** (≥0.0.1a2): Microsoft's document conversion engine
- **Pillow** (≥10.0.0): Advanced image processing and format support
- **keyring** (≥24.0.0): Secure credential storage for API keys
- **aiohttp** (≥3.8.0): Asynchronous HTTP client for LLM integration

#### Optional Dependencies for Enhanced Features
- **pdf2image** (≥3.1.0): High-quality PDF rendering and conversion
- **pytesseract** (≥0.3.10): OCR support for scanned documents
- **python-pptx**: Advanced PowerPoint processing
- **mammoth**: Enhanced Word document conversion
- **pandas & openpyxl**: Excel and spreadsheet processing
- **pdfminer.six**: Advanced PDF text extraction
- **SpeechRecognition & pydub**: Audio transcription capabilities

#### System Dependencies (Platform-Specific)
- **Tesseract OCR**: Required for OCR functionality
- **Poppler utilities**: For PDF processing (pdf2image)
- **FFmpeg**: For audio/video processing (optional)

## Installation Methods

Choose the installation method that best fits your needs and technical expertise.

### Method 1: Package Manager (Recommended for Most Users)

#### Using pip (Python Package Index)
```bash
# Basic installation with core features
pip install markitdown-gui

# Install with all optional features (recommended)
pip install markitdown-gui[all]

# Install specific feature sets
pip install markitdown-gui[ocr,audio]  # OCR + audio transcription
pip install markitdown-gui[enterprise]  # Enterprise features

# Install specific version
pip install markitdown-gui==1.0.0

# Upgrade existing installation
pip install --upgrade markitdown-gui

# Install for current user only (no admin required)
pip install --user markitdown-gui
```

#### Using conda (Anaconda/Miniconda)
```bash
# Install from conda-forge channel
conda install -c conda-forge markitdown-gui

# Create dedicated environment (recommended)
conda create -n markitdown python=3.11
conda activate markitdown
conda install -c conda-forge markitdown-gui

# Install with specific features
conda install -c conda-forge markitdown-gui[all]
```

#### Using pipx (Isolated Installation)
```bash
# Install pipx if not available
pip install pipx

# Install MarkItDown GUI in isolated environment
pipx install markitdown-gui

# Install with optional features
pipx install markitdown-gui[all]

# Upgrade
pipx upgrade markitdown-gui
```

### Method 2: From Source (For Developers)

#### Prerequisites
- **Git**: Version control system
- **Python**: 3.10+ with pip
- **Build tools**: Platform-specific (see platform sections)

#### Clone and Install
```bash
# Clone the repository
git clone https://github.com/microsoft/markitdown-gui.git
cd markitdown-gui

# Create and activate virtual environment
python -m venv markitdown-env

# Activate virtual environment
# Windows:
markitdown-env\Scripts\activate
# macOS/Linux:
source markitdown-env/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install in development mode with all features
pip install -e .[all,dev]

# Or install production version
pip install -r requirements.txt
pip install .
```

#### Development Installation
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify installation
pytest tests/

# Launch in development mode
python main.py
```

### Method 3: Standalone Executable (No Python Required)

Download pre-built executables from the [releases page](https://github.com/microsoft/markitdown-gui/releases):

#### Available Downloads
- **Windows x64**: `MarkItDown-GUI-v1.0.0-windows-x64.exe`
- **Windows x86**: `MarkItDown-GUI-v1.0.0-windows-x86.exe`
- **Windows Installer**: `MarkItDown-GUI-v1.0.0-setup.msi`
- **macOS Intel**: `MarkItDown-GUI-v1.0.0-macos-intel.dmg`
- **macOS Apple Silicon**: `MarkItDown-GUI-v1.0.0-macos-arm64.dmg`
- **Linux x64**: `MarkItDown-GUI-v1.0.0-linux-x86_64.AppImage`
- **Linux ARM**: `MarkItDown-GUI-v1.0.0-linux-aarch64.AppImage`

#### Installation Steps
1. **Download**: Select the appropriate version for your system
2. **Verify**: Check file integrity using provided checksums
3. **Install**: Follow platform-specific instructions below
4. **Launch**: Run the application from your system's applications menu

## Platform-Specific Instructions

### Windows

#### Prerequisites Installation
```powershell
# Open PowerShell as Administrator
# Install Python via winget (Windows 10 1709+)
winget install Python.Python.3.12

# Alternatively, install via Chocolatey
choco install python312

# Or download from python.org
# https://www.python.org/downloads/windows/

# Install system dependencies for enhanced features
winget install Git.Git
winget install 7zip.7zip  # For archive handling
# Optional: Install Tesseract for OCR
winget install UB-Mannheim.TesseractOCR
```

#### Method 1: Windows Installer (Easiest)
1. **Download**: Get `MarkItDown-GUI-v1.0.0-setup.msi` from releases
2. **Run**: Double-click installer or run as administrator
3. **Install**: Follow installation wizard
   - Choose installation directory (default: `C:\Program Files\MarkItDown GUI`)
   - Select components (Core, OCR support, Desktop shortcut)
   - Configure file associations (optional)
4. **Launch**: Use Start Menu or desktop shortcut

#### Method 2: Standalone Executable
```powershell
# Download the executable
Invoke-WebRequest -Uri "https://github.com/microsoft/markitdown-gui/releases/download/v1.0.0/MarkItDown-GUI-v1.0.0-windows-x64.exe" -OutFile "MarkItDown-GUI.exe"

# Verify download (optional)
Get-FileHash MarkItDown-GUI.exe -Algorithm SHA256

# Run the application
.\MarkItDown-GUI.exe
```

#### Method 3: Package Manager Installation
```powershell
# Using pip
pip install markitdown-gui[all]

# Create desktop shortcut
python -m markitdown_gui --create-shortcut

# Add to Windows PATH (if needed)
$env:PATH += ";$env:USERPROFILE\AppData\Local\Programs\Python\Python312\Scripts"
```

#### Windows-Specific Configuration

##### File Associations Setup
```powershell
# Register file associations (run as administrator)
markitdown-gui --register-file-types

# Supported file types that can be associated:
# .docx, .doc, .pptx, .ppt, .xlsx, .xls, .pdf, .txt, .md, .html
```

##### Windows Defender Configuration
```powershell
# Add exclusion for MarkItDown GUI (if needed)
Add-MpPreference -ExclusionPath "C:\Program Files\MarkItDown GUI"
Add-MpPreference -ExclusionProcess "MarkItDown-GUI.exe"
```

##### System Environment Variables
```powershell
# Add Python Scripts to PATH permanently
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$env:USERPROFILE\AppData\Local\Programs\Python\Python312\Scripts", [EnvironmentVariableTarget]::User)

# Set Tesseract path for OCR (if installed)
[Environment]::SetEnvironmentVariable("TESSDATA_PREFIX", "C:\Program Files\Tesseract-OCR\tessdata", [EnvironmentVariableTarget]::User)
```

#### Windows Troubleshooting
- **Issue**: "Python not found" → Install Python from python.org or Microsoft Store
- **Issue**: "Access denied" → Run PowerShell/Command Prompt as administrator
- **Issue**: "msvcp140.dll missing" → Install Visual C++ Redistributable
- **Issue**: "Windows Defender blocks executable" → Add exclusion or download from official source

### macOS

#### Prerequisites Installation
```bash
# Install Xcode Command Line Tools (if not installed)
xcode-select --install

# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Install system dependencies for enhanced features
brew install git
brew install tesseract  # For OCR support
brew install poppler    # For PDF processing
brew install ffmpeg     # For audio/video processing (optional)
```

#### Method 1: DMG Installer (Recommended)
1. **Download**: Get appropriate DMG from releases page
   - Intel Macs: `MarkItDown-GUI-v1.0.0-macos-intel.dmg`
   - Apple Silicon: `MarkItDown-GUI-v1.0.0-macos-arm64.dmg`
2. **Mount**: Double-click the DMG file
3. **Install**: Drag MarkItDown GUI to Applications folder
4. **Launch**: Open from Launchpad, Applications, or Spotlight

#### Method 2: Homebrew Installation
```bash
# Add our tap (when available)
brew tap microsoft/markitdown-gui

# Install MarkItDown GUI
brew install markitdown-gui

# Or install with cask for GUI applications
brew install --cask markitdown-gui
```

#### Method 3: Package Manager Installation
```bash
# Using pip3
pip3 install markitdown-gui[all]

# Create application bundle for Finder
python3 -m markitdown_gui --create-app-bundle

# Add to PATH (if needed)
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### macOS-Specific Configuration

##### Gatekeeper and Security
```bash
# If application is blocked by Gatekeeper:
# Method 1: Right-click → Open (one-time bypass)
# Method 2: System Preferences bypass
sudo spctl --master-disable  # Temporarily disable Gatekeeper
# Re-enable after first run:
sudo spctl --master-enable

# Remove quarantine attribute (if needed)
sudo xattr -r -d com.apple.quarantine "/Applications/MarkItDown GUI.app"
```

##### File System Permissions
```bash
# Grant Full Disk Access (if needed for system files)
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add MarkItDown GUI to the list

# Terminal access configuration
tccutil reset SystemPolicyAllFiles com.microsoft.markitdown-gui
```

##### Launch Services Registration
```bash
# Register file associations
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "/Applications/MarkItDown GUI.app"

# Reset Launch Services database (if file associations broken)
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user
```

#### macOS Troubleshooting
- **Issue**: "App is damaged" → Remove quarantine with `xattr -d com.apple.quarantine`
- **Issue**: "Permission denied" → Grant Full Disk Access in Security & Privacy
- **Issue**: "Command not found" → Add Python to PATH or use full path
- **Issue**: "Tesseract not found" → Install via Homebrew: `brew install tesseract`

### Linux

#### Ubuntu/Debian Systems

##### Prerequisites Installation
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install python3.12 python3.12-pip python3.12-venv python3.12-dev

# Install system dependencies
sudo apt install python3-pyqt6 python3-pyqt6-dev
sudo apt install build-essential libgl1-mesa-glx libglib2.0-0

# Install optional dependencies for enhanced features
sudo apt install tesseract-ocr tesseract-ocr-eng  # OCR support
sudo apt install poppler-utils                     # PDF processing
sudo apt install ffmpeg                           # Audio/video processing
sudo apt install git curl wget                    # Development tools
```

##### Installation Methods
```bash
# Method 1: Package manager installation
pip3 install markitdown-gui[all]

# Method 2: System package (when available)
sudo apt install markitdown-gui

# Method 3: Snap package (when available)
sudo snap install markitdown-gui

# Create desktop entry and file associations
markitdown-gui --install-desktop
markitdown-gui --register-file-types
```

#### CentOS/RHEL/Fedora Systems

##### Prerequisites Installation
```bash
# Fedora 38+
sudo dnf install python3.12 python3.12-pip python3.12-devel
sudo dnf install python3-qt6 python3-qt6-devel
sudo dnf install gcc gcc-c++ make

# RHEL/CentOS (with EPEL enabled)
sudo dnf install epel-release
sudo dnf install python312 python312-pip python312-devel
sudo dnf install qt6-qtbase-devel

# Install optional dependencies
sudo dnf install tesseract tesseract-langpack-eng
sudo dnf install poppler-utils
sudo dnf install ffmpeg
```

##### Installation
```bash
# Install MarkItDown GUI
pip3.12 install markitdown-gui[all]

# Create desktop integration
markitdown-gui --install-desktop
```

#### Arch Linux Systems

##### Prerequisites Installation
```bash
# Update system
sudo pacman -Syu

# Install Python and dependencies
sudo pacman -S python python-pip python-pyqt6
sudo pacman -S base-devel qt6-base

# Install optional dependencies
sudo pacman -S tesseract tesseract-data-eng
sudo pacman -S poppler
sudo pacman -S ffmpeg
```

##### Installation Methods
```bash
# Method 1: AUR installation (when available)
yay -S markitdown-gui-git

# Method 2: Manual installation
pip install markitdown-gui[all]

# Method 3: Build from source
git clone https://github.com/microsoft/markitdown-gui.git
cd markitdown-gui
makepkg -si
```

#### openSUSE Systems

##### Prerequisites Installation
```bash
# Install Python and dependencies
sudo zypper install python312 python312-pip python312-devel
sudo zypper install python3-qt6 python3-qt6-devel
sudo zypper install gcc gcc-c++ make

# Install optional dependencies
sudo zypper install tesseract-ocr tesseract-ocr-traineddata-english
sudo zypper install poppler-tools
sudo zypper install ffmpeg
```

#### Universal Linux Installation (AppImage)

##### Download and Setup
```bash
# Download AppImage
wget https://github.com/microsoft/markitdown-gui/releases/download/v1.0.0/MarkItDown-GUI-v1.0.0-linux-x86_64.AppImage

# Verify download integrity
wget https://github.com/microsoft/markitdown-gui/releases/download/v1.0.0/SHA256SUMS
sha256sum -c SHA256SUMS --ignore-missing

# Make executable
chmod +x MarkItDown-GUI-v1.0.0-linux-x86_64.AppImage

# Optional: Move to system location
sudo mv MarkItDown-GUI-v1.0.0-linux-x86_64.AppImage /usr/local/bin/markitdown-gui

# Create desktop entry
cat > ~/.local/share/applications/markitdown-gui.desktop << EOF
[Desktop Entry]
Type=Application
Name=MarkItDown GUI
Comment=Convert documents to Markdown
Exec=/usr/local/bin/markitdown-gui
Icon=markitdown-gui
Categories=Office;TextEditor;
MimeType=application/pdf;application/msword;application/vnd.openxmlformats-officedocument.wordprocessingml.document;
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

#### Linux-Specific Configuration

##### Desktop Integration
```bash
# Install XDG utilities (if not present)
sudo apt install xdg-utils  # Ubuntu/Debian
sudo dnf install xdg-utils  # Fedora
sudo pacman -S xdg-utils    # Arch

# Register MIME types and file associations
xdg-mime default markitdown-gui.desktop application/pdf
xdg-mime default markitdown-gui.desktop application/msword
xdg-mime default markitdown-gui.desktop application/vnd.openxmlformats-officedocument.wordprocessingml.document

# Set default browser for links (optional)
xdg-settings set default-web-browser firefox.desktop
```

##### System Service Integration (Optional)
```bash
# Create systemd user service for background processing
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/markitdown-gui.service << EOF
[Unit]
Description=MarkItDown GUI Background Service
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/local/bin/markitdown-gui --daemon
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF

# Enable and start service
systemctl --user enable markitdown-gui.service
systemctl --user start markitdown-gui.service
```

#### Linux Troubleshooting
- **Issue**: "Qt platform plugin could not be initialized" → Install Qt6 system packages
- **Issue**: "No module named 'PyQt6'" → Use system package manager for PyQt6
- **Issue**: "Permission denied" → Use `--user` flag with pip or run with sudo
- **Issue**: "libGL error" → Install Mesa OpenGL libraries
- **Issue**: "Tesseract not found" → Install tesseract-ocr package
- **Issue**: "AppImage won't run" → Install fuse2: `sudo apt install fuse2`

## Verification

### Installation Verification

#### Basic Verification
```bash
# Check if MarkItDown GUI is installed and accessible
markitdown-gui --version

# Verify all dependencies are satisfied
markitdown-gui --check-dependencies

# Test core functionality without GUI
markitdown-gui --test-conversion

# Quick system diagnostic
markitdown-gui --diagnostics
```

#### Expected Output
```
MarkItDown GUI v1.0.0
Python: 3.12.0 (main, Oct  2 2023, 10:00:00)
PyQt6: 6.6.0
Platform: Linux-6.2.0-39-generic-x86_64
Architecture: x86_64
Installation Method: pip

Dependencies Status:
✓ markitdown (0.0.1a2) - Core conversion engine
✓ PyQt6 (6.6.0) - GUI framework
✓ Pillow (10.1.0) - Image processing
✓ keyring (24.2.0) - Credential storage
✓ aiohttp (3.9.0) - HTTP client
✓ pdf2image (3.1.0) - PDF rendering
✓ pytesseract (0.3.10) - OCR support
✓ Tesseract OCR (5.3.0) - OCR engine

System Features:
✓ GUI components loaded
✓ Conversion engine ready
✓ OCR support available
✓ PDF processing enabled
✓ Audio transcription ready
✓ LLM integration configured
```

#### Functional Testing

##### Test Basic Conversion
```bash
# Create a test document
echo "# Test Document\nThis is a **test** for MarkItDown GUI." > test.md

# Test command-line conversion
markitdown-gui --input test.md --output test.html --format html

# Verify output
cat test.html
```

##### Test GUI Launch
```bash
# Launch GUI application
markitdown-gui

# Or launch with specific file
markitdown-gui test.docx

# Launch with debug mode
markitdown-gui --debug --verbose
```

##### Test File Format Support
```bash
# Test supported input formats
markitdown-gui --list-formats

# Test specific format conversion
markitdown-gui --test-format pdf
markitdown-gui --test-format docx
markitdown-gui --test-format pptx
```

### Performance Verification

#### System Performance Check
```bash
# Run performance benchmark
markitdown-gui --benchmark

# Test with large file
markitdown-gui --test-large-file

# Memory usage test
markitdown-gui --test-memory
```

#### Expected Performance Metrics
```
Performance Benchmark Results:
Document Processing Speed:
  Small files (<1MB): ~500ms
  Medium files (1-10MB): ~2-5s
  Large files (10-50MB): ~10-30s

Memory Usage:
  Baseline: ~80MB
  During processing: ~150-300MB
  Peak usage: ~500MB (large documents)

GUI Responsiveness:
  Startup time: <3s
  File loading: <1s (typical)
  UI interactions: <100ms
```

### Troubleshooting Verification Issues

#### Common Installation Problems

##### Import Errors
```bash
# Test Python environment
python -c "import sys; print(sys.path)"
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import markitdown; print('markitdown OK')"

# Check for conflicting installations
pip list | grep -i pyqt
pip list | grep -i markitdown
```

##### Path Issues
```bash
# Check executable location
which markitdown-gui
echo $PATH

# Test Python module import
python -c "import markitdown_gui; print('Module found')"

# Verify entry points
pip show markitdown-gui | grep -A 5 "Entry-points"
```

##### Permission Issues
```bash
# Check file permissions
ls -la $(which markitdown-gui)

# Test write permissions
markitdown-gui --test-permissions

# Verify configuration directory
markitdown-gui --show-config-dir
```

#### Platform-Specific Verification

##### Windows Verification
```powershell
# Check Windows-specific dependencies
python -c "import win32gui; print('Win32 OK')" 2>$null || echo "Win32 not available"

# Test Windows file associations
assoc .docx
ftype Word.Document.12

# Verify Windows registry entries
reg query "HKEY_CURRENT_USER\Software\Microsoft\MarkItDown GUI" 2>$null || echo "Registry not found"
```

##### macOS Verification
```bash
# Check macOS-specific features
python -c "import Foundation; print('Foundation OK')" 2>/dev/null || echo "Foundation not available"

# Test application bundle
ls -la "/Applications/MarkItDown GUI.app"

# Verify code signing (if applicable)
codesign -v "/Applications/MarkItDown GUI.app" 2>/dev/null || echo "Not code signed"
```

##### Linux Verification
```bash
# Check Linux desktop integration
ls -la ~/.local/share/applications/markitdown-gui.desktop

# Test X11/Wayland compatibility
echo $XDG_SESSION_TYPE
echo $DISPLAY

# Verify system libraries
ldd $(which markitdown-gui) | grep -E "(Qt|PyQt)" || echo "Libraries not found"
```

## Troubleshooting

### Common Installation Issues

#### Python Environment Issues

##### Python Version Conflicts
```bash
# Check all Python versions available
ls /usr/bin/python*  # Linux/macOS
where python*        # Windows

# Check specific Python version
python3.12 --version
python3.11 --version

# Use specific Python version for installation
python3.12 -m pip install markitdown-gui

# Check which Python pip is using
python -m pip --version
```

##### Virtual Environment Issues
```bash
# Create clean virtual environment
python3.12 -m venv markitdown-clean
source markitdown-clean/bin/activate  # Linux/macOS
# markitdown-clean\Scripts\activate   # Windows

# Upgrade pip in virtual environment
python -m pip install --upgrade pip setuptools wheel

# Install in clean environment
pip install markitdown-gui[all]
```

##### PATH and Environment Issues
```bash
# Check Python executable location
which python
which pip

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Fix common PATH issues
export PATH="$HOME/.local/bin:$PATH"  # Linux/macOS
# Add to ~/.bashrc or ~/.zshrc for persistence
```

#### Dependency Installation Issues

##### PyQt6 Installation Problems
```bash
# Install PyQt6 separately
pip install --upgrade PyQt6

# On Linux, use system package manager (often more reliable)
sudo apt install python3-pyqt6 python3-pyqt6-dev  # Ubuntu/Debian
sudo dnf install python3-qt6 python3-qt6-devel    # Fedora
sudo pacman -S python-pyqt6                       # Arch

# Check PyQt6 installation
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

##### markitdown Core Installation Issues
```bash
# Install markitdown separately
pip install --upgrade markitdown

# Install with specific features
pip install "markitdown[all]"

# Check markitdown installation
python -c "import markitdown; print(f'markitdown {markitdown.__version__}')"
```

##### OCR Dependencies Issues
```bash
# Install Tesseract system-wide
# Ubuntu/Debian:
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-script-latn

# Fedora:
sudo dnf install tesseract tesseract-langpack-eng

# macOS:
brew install tesseract

# Windows:
# Download from https://github.com/UB-Mannheim/tesseract/wiki

# Test Tesseract installation
tesseract --version
python -c "import pytesseract; print('OCR OK')"
```

#### Permission and Access Issues

##### Permission Denied Errors
```bash
# Install for current user only (no admin required)
pip install --user markitdown-gui

# Fix pip permissions on Linux/macOS
sudo chown -R $(whoami) ~/.local/lib/python*/site-packages/

# Use virtual environment to avoid permission issues
python -m venv ~/markitdown-venv
source ~/markitdown-venv/bin/activate
pip install markitdown-gui
```

##### File System Access Issues
```bash
# Check file permissions
ls -la $(which markitdown-gui)

# Fix executable permissions
chmod +x ~/.local/bin/markitdown-gui

# Test write access to config directory
markitdown-gui --test-permissions
```

### Platform-Specific Issues

#### Windows-Specific Problems

##### Microsoft Visual C++ Issues
```powershell
# Install Visual C++ Redistributable
winget install Microsoft.VCRedist.2015+.x64

# Or download from Microsoft website
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

##### Windows Defender Issues
```powershell
# Add exclusion for Python Scripts directory
Add-MpPreference -ExclusionPath "$env:USERPROFILE\AppData\Local\Programs\Python\Python312\Scripts"

# Add exclusion for installation directory
Add-MpPreference -ExclusionPath "$env:PROGRAMFILES\MarkItDown GUI"
```

##### Windows PATH Issues
```powershell
# Add Python Scripts to PATH permanently
$oldPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
$newPath = "$oldPath;$env:USERPROFILE\AppData\Local\Programs\Python\Python312\Scripts"
[Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::User)

# Refresh current session
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
```

#### macOS-Specific Problems

##### Gatekeeper Issues
```bash
# Bypass Gatekeeper for specific app
sudo xattr -r -d com.apple.quarantine "/Applications/MarkItDown GUI.app"

# Temporarily disable Gatekeeper (not recommended)
sudo spctl --master-disable
# Re-enable after first run:
sudo spctl --master-enable
```

##### Code Signing Issues
```bash
# Check code signing status
codesign -v -v "/Applications/MarkItDown GUI.app"

# Self-sign for development (if building from source)
codesign --force --deep --sign - "/Applications/MarkItDown GUI.app"
```

##### Permission Issues
```bash
# Grant Terminal full disk access
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add Terminal to the list

# Reset TCC permissions
tccutil reset SystemPolicyAllFiles com.microsoft.markitdown-gui
```

#### Linux-Specific Problems

##### Display Server Issues
```bash
# Check display server type
echo $XDG_SESSION_TYPE

# For Wayland compatibility issues
export QT_QPA_PLATFORM=wayland
# Or fallback to X11
export QT_QPA_PLATFORM=xcb

# Test GUI with minimal dependencies
python -c "from PyQt6.QtWidgets import QApplication; app = QApplication([]); print('GUI OK')"
```

##### System Library Issues
```bash
# Install missing system libraries
sudo apt install libgl1-mesa-glx libxkbcommon-x11-0 libxcb-xinerama0 libxcb-cursor0

# For audio processing
sudo apt install libpulse-dev libasound2-dev

# Check library dependencies
ldd $(python -c "import PyQt6; print(PyQt6.__file__)")
```

##### Desktop Integration Issues
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications/

# Clear icon cache
gtk-update-icon-cache ~/.local/share/icons/

# Reset MIME associations
rm ~/.local/share/applications/mimeapps.list
```

### Advanced Troubleshooting

#### Debug Mode and Logging
```bash
# Run with maximum verbosity
markitdown-gui --debug --verbose --log-level DEBUG

# Enable Qt debug output
export QT_LOGGING_RULES="*.debug=true"
markitdown-gui

# Save debug output to file
markitdown-gui --debug --log-file ~/markitdown-debug.log
```

#### Network and Proxy Issues
```bash
# Configure proxy for pip (if needed)
pip install --proxy http://proxy.example.com:8080 markitdown-gui

# Test network connectivity
python -c "import urllib.request; urllib.request.urlopen('https://pypi.org')"

# Configure for corporate environments
pip install --trusted-host pypi.org --trusted-host pypi.python.org markitdown-gui
```

#### Clean Installation Reset
```bash
# Completely remove existing installation
pip uninstall markitdown-gui markitdown PyQt6 -y

# Clear pip cache
pip cache purge

# Remove configuration files
rm -rf ~/.config/markitdown-gui  # Linux/macOS
# Remove %APPDATA%\markitdown-gui  # Windows

# Fresh installation
pip install --no-cache-dir markitdown-gui[all]
```

## Advanced Installation

### Enterprise and Corporate Environments

#### Corporate Proxy Configuration
```bash
# Configure pip for corporate proxy
pip config set global.proxy http://proxy.company.com:8080
pip config set global.trusted-host pypi.org
pip config set global.trusted-host pypi.python.org

# Install with proxy
pip install --proxy http://proxy.company.com:8080 markitdown-gui

# For NTLM authentication
pip install --proxy http://username:password@proxy.company.com:8080 markitdown-gui
```

#### Offline Installation
```bash
# Download packages for offline installation
pip download markitdown-gui[all] --dest ./offline-packages

# Transfer offline-packages directory to target machine
# Install from offline packages
pip install markitdown-gui[all] --no-index --find-links ./offline-packages
```

#### Custom Installation Locations
```bash
# Install to custom directory
pip install --target /custom/path markitdown-gui

# Use custom installation in Python
export PYTHONPATH="/custom/path:$PYTHONPATH"
python -c "import markitdown_gui; print('Custom install OK')"
```

### Docker Installation

#### Official Docker Image
```bash
# Pull official Docker image
docker pull microsoft/markitdown-gui:latest

# Run GUI application with X11 forwarding (Linux)
docker run -it --rm \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  -v $HOME/Documents:/workspace \
  microsoft/markitdown-gui:latest

# Run with VNC (cross-platform)
docker run -it --rm \
  -p 5901:5901 \
  -v $HOME/Documents:/workspace \
  microsoft/markitdown-gui:vnc
```

#### Custom Docker Build
```dockerfile
# Dockerfile for custom build
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pyqt6 \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install MarkItDown GUI
RUN pip install markitdown-gui[all]

# Set up user
RUN useradd -m markitdown
USER markitdown
WORKDIR /home/markitdown

# Entry point
ENTRYPOINT ["markitdown-gui"]
```

### Development Installation

#### Development Environment Setup
```bash
# Clone repository
git clone https://github.com/microsoft/markitdown-gui.git
cd markitdown-gui

# Create development environment
python -m venv dev-env
source dev-env/bin/activate

# Install development dependencies
pip install -e .[dev,test,docs]

# Install pre-commit hooks
pre-commit install

# Set up IDE configuration
python setup_dev.py --ide vscode  # or --ide pycharm
```

#### Building from Source
```bash
# Build wheel package
python -m build

# Install built package
pip install dist/markitdown_gui-*.whl

# Build documentation
cd docs
make html

# Run development server
python -m markitdown_gui.dev_server
```

## Uninstallation

### Complete pip Uninstallation

#### Standard Removal
```bash
# Uninstall MarkItDown GUI and dependencies
pip uninstall markitdown-gui -y

# Remove optional dependencies (if not used by other packages)
pip uninstall markitdown PyQt6 Pillow pdf2image pytesseract -y

# Verify removal
pip list | grep -i markitdown
```

#### Thorough Cleanup
```bash
# Remove all related packages
pip freeze | grep -E "(markitdown|pyqt)" | xargs pip uninstall -y

# Clear pip cache
pip cache purge

# Remove user-installed packages
rm -rf ~/.local/lib/python*/site-packages/*markitdown*
rm -rf ~/.local/lib/python*/site-packages/*pyqt*

# Remove configuration and data
rm -rf ~/.config/markitdown-gui      # Linux
rm -rf ~/Library/Preferences/MarkItDown\ GUI  # macOS
# Remove %APPDATA%\markitdown-gui     # Windows
# Remove %LOCALAPPDATA%\markitdown-gui # Windows
```

### System Installation Removal

#### Windows Uninstallation
```powershell
# Method 1: Use Add/Remove Programs
Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*MarkItDown*" } | ForEach-Object { $_.Uninstall() }

# Method 2: Run uninstaller
& "C:\Program Files\MarkItDown GUI\uninstall.exe"

# Method 3: Manual removal
Remove-Item "C:\Program Files\MarkItDown GUI" -Recurse -Force
Remove-Item "$env:APPDATA\markitdown-gui" -Recurse -Force
Remove-Item "$env:LOCALAPPDATA\markitdown-gui" -Recurse -Force

# Clean registry entries
Remove-Item "HKCU:\Software\Microsoft\MarkItDown GUI" -Recurse -Force

# Remove file associations
cmd /c "assoc .docx="
cmd /c "assoc .pdf="
```

#### macOS Uninstallation
```bash
# Remove application bundle
rm -rf "/Applications/MarkItDown GUI.app"

# Remove user data and preferences
rm -rf ~/Library/Application\ Support/MarkItDown\ GUI
rm -rf ~/Library/Preferences/com.microsoft.markitdown-gui.plist
rm -rf ~/Library/Caches/com.microsoft.markitdown-gui

# Remove Launch Services entries
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -u "/Applications/MarkItDown GUI.app"

# Remove from PATH (if added)
sed -i '' '/markitdown-gui/d' ~/.zshrc ~/.bashrc
```

#### Linux Uninstallation
```bash
# Remove AppImage
rm -f ~/Applications/MarkItDown-GUI-*.AppImage
rm -f /usr/local/bin/markitdown-gui

# Remove desktop integration
rm -f ~/.local/share/applications/markitdown-gui.desktop
rm -f /usr/share/applications/markitdown-gui.desktop

# Remove MIME associations
sed -i '/markitdown-gui/d' ~/.local/share/applications/mimeapps.list

# Remove configuration and data
rm -rf ~/.config/markitdown-gui
rm -rf ~/.local/share/markitdown-gui

# Update desktop database
update-desktop-database ~/.local/share/applications/

# Remove system packages (if installed via package manager)
sudo apt remove markitdown-gui          # Ubuntu/Debian
sudo dnf remove markitdown-gui          # Fedora
sudo pacman -R markitdown-gui           # Arch
sudo snap remove markitdown-gui         # Snap
```

### Verification of Removal
```bash
# Check if any traces remain
which markitdown-gui
pip list | grep -i markitdown
find / -name "*markitdown*" 2>/dev/null | head -10

# Test that command is no longer available
markitdown-gui --version 2>&1 | grep "command not found"
```

---

## Support and Resources

### Getting Help

#### Documentation
- 📋 **[Quick Start Guide](quick-start.md)** - Get up and running in 5 minutes
- 📖 **[User Manual](user-manual.md)** - Comprehensive usage documentation
- 🔧 **[Configuration Guide](configuration.md)** - Customize your installation
- 📚 **[API Documentation](api-reference.md)** - Developer reference
- ❓ **[FAQ](faq.md)** - Frequently asked questions

#### Community and Support
- 🐛 **[Issue Tracker](https://github.com/microsoft/markitdown-gui/issues)** - Report bugs and request features
- 💬 **[Discussions](https://github.com/microsoft/markitdown-gui/discussions)** - Community support and questions
- 📢 **[Release Notes](https://github.com/microsoft/markitdown-gui/releases)** - Latest updates and changes
- 🏠 **[Project Homepage](https://github.com/microsoft/markitdown-gui)** - Source code and project information

#### Contact Information
- **Email**: markitdown-support@microsoft.com
- **Documentation Issues**: Create issue with "documentation" label
- **Security Issues**: Follow [security policy](https://github.com/microsoft/markitdown-gui/security/policy)

### Installation Summary Checklist

Use this checklist to ensure successful installation:

#### ✅ Pre-Installation
- [ ] System meets minimum requirements (Python 3.10+, 4GB RAM)
- [ ] Internet connection available for downloads
- [ ] Administrative privileges available (if needed)
- [ ] Previous versions uninstalled (if applicable)

#### ✅ Installation Process
- [ ] Installation method selected (pip/conda/executable/source)
- [ ] Dependencies installed successfully
- [ ] Platform-specific requirements met
- [ ] Optional features configured (OCR, audio, etc.)

#### ✅ Post-Installation Verification
- [ ] `markitdown-gui --version` shows correct version
- [ ] GUI launches successfully
- [ ] Basic document conversion works
- [ ] File associations configured (if desired)
- [ ] Desktop integration complete (Linux/macOS)

#### ✅ Troubleshooting Ready
- [ ] Know how to check logs (`--debug --verbose`)
- [ ] Understand common error solutions
- [ ] Have uninstallation procedure available
- [ ] Know where to get help

### Quick Reference Commands

```bash
# Installation
pip install markitdown-gui[all]                    # Full installation
pip install --user markitdown-gui                  # User-only installation
pip install --upgrade markitdown-gui               # Update existing

# Verification
markitdown-gui --version                           # Check version
markitdown-gui --check-dependencies                # Verify setup
markitdown-gui --test-conversion                   # Test functionality

# Usage
markitdown-gui                                      # Launch GUI
markitdown-gui document.docx                       # Open specific file
markitdown-gui --input file.pdf --output file.md   # Command-line conversion

# Troubleshooting
markitdown-gui --debug --verbose                   # Debug mode
markitdown-gui --diagnostics                       # System diagnostic
pip install --force-reinstall markitdown-gui       # Reinstall

# Uninstallation
pip uninstall markitdown-gui                       # Remove package
rm -rf ~/.config/markitdown-gui                    # Remove config
```

---

**🎉 Installation Complete!**

You're now ready to start converting documents with MarkItDown GUI. Choose your next step:

- **New Users**: Start with the [Quick Start Guide](quick-start.md) for a guided introduction
- **Power Users**: Explore the [User Manual](user-manual.md) for advanced features  
- **Developers**: Check the [API Documentation](api-reference.md) for integration options
- **Need Help**: Visit our [FAQ](faq.md) or [community discussions](https://github.com/microsoft/markitdown-gui/discussions)

**Happy converting! 🚀**
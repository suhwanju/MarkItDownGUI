# Troubleshooting Guide

Comprehensive problem-solving guide for MarkItDown GUI with step-by-step solutions, diagnostic tools, and recovery procedures.

## Table of Contents

- [Quick Diagnosis](#quick-diagnosis)
- [Installation Issues](#installation-issues)
- [Application Startup Problems](#application-startup-problems)
- [File Processing Issues](#file-processing-issues)
- [Performance Problems](#performance-problems)
- [Output Quality Issues](#output-quality-issues)
- [System Integration Problems](#system-integration-problems)
- [Network and Connectivity Issues](#network-and-connectivity-issues)
- [Security and Permissions](#security-and-permissions)
- [Advanced Troubleshooting](#advanced-troubleshooting)
- [Emergency Recovery Procedures](#emergency-recovery-procedures)
- [Professional Support](#professional-support)

## Quick Diagnosis

### Problem Severity Classification

| Severity | Symptoms | Impact | Response Time |
|----------|----------|--------|---------------|
| **Critical** | App won't start, data loss, crashes | Cannot use application | Immediate |
| **High** | Major features broken, frequent errors | Significantly impaired | 2-4 hours |
| **Medium** | Performance issues, minor bugs | Moderately impaired | 1-2 days |
| **Low** | Cosmetic issues, enhancement requests | Minimally impaired | 1-2 weeks |

### Problem Categories Matrix

| Symptom | Likely Cause | Quick Fix | Severity | Time to Fix |
|---------|--------------|-----------|----------|-------------|
| Application won't start | Missing dependencies | Reinstall application | Critical | 15-30 min |
| Crashes on launch | System compatibility | Check system requirements | Critical | 30-60 min |
| Slow processing | Resource limits | Increase memory/close apps | Medium | 5-15 min |
| Poor output quality | Wrong settings | Adjust quality settings | Medium | 5-10 min |
| File won't open | Format/permission issue | Check file type/permissions | High | 10-20 min |
| Missing features | Outdated version | Update application | Low | 5-10 min |
| Memory errors | Insufficient RAM | Reduce batch size | High | Immediate |
| Network errors | Connectivity issues | Check internet connection | High | 5-30 min |
| Permission errors | Access restrictions | Run as administrator | High | 2-5 min |
| Configuration errors | Corrupted settings | Reset configuration | Medium | 5-10 min |

### Diagnostic Decision Tree

```
🔍 Issue Identified
├── Application Level
│   ├── Won't Start → [Installation Issues](#installation-issues)
│   ├── Crashes → [Startup Problems](#application-startup-problems)
│   └── Slow/Unresponsive → [Performance Problems](#performance-problems)
├── File Level
│   ├── Won't Process → [File Processing Issues](#file-processing-issues)
│   ├── Poor Quality → [Output Quality Issues](#output-quality-issues)
│   └── Access Denied → [Security and Permissions](#security-and-permissions)
├── System Level
│   ├── Integration → [System Integration](#system-integration-problems)
│   ├── Network → [Network Issues](#network-and-connectivity-issues)
│   └── Resources → [Performance Problems](#performance-problems)
└── Unknown → [Advanced Troubleshooting](#advanced-troubleshooting)
```

### Emergency First Steps Checklist

**⚡ Critical Issues (Application won't start):**
1. ✅ **Check running processes** - Kill any hung MarkItDown processes
2. ✅ **Verify system requirements** - Ensure compatibility
3. ✅ **Check error messages** - Note specific error codes
4. ✅ **Try safe mode** - Launch with `--safe-mode` flag
5. ✅ **Emergency config reset** - Backup and reset configuration

**🔧 High Priority Issues (Major malfunction):**
1. ✅ **Restart application** - Clear temporary issues
2. ✅ **Check system resources** - Ensure adequate memory/disk space
3. ✅ **Verify file integrity** - Test with known good files
4. ✅ **Review recent changes** - Software updates, new files, settings changes
5. ✅ **Check logs** - Look for patterns in error logs

**📊 Medium Priority Issues (Performance/Quality):**
1. ✅ **Monitor resource usage** - CPU, memory, disk I/O
2. ✅ **Test with different files** - Isolate file-specific issues
3. ✅ **Adjust settings** - Try different quality/performance settings
4. ✅ **Clear cache** - Remove temporary files and cache
5. ✅ **Update application** - Ensure latest version

### Quick Diagnostic Commands

**System Information Collection:**
```bash
# Collect system diagnostics (Linux/macOS)
markitdown-gui --diagnose > diagnosis.txt

# Windows equivalent
markitdown-gui.exe --system-info > system-info.txt

# Test core functionality
markitdown-gui --test-installation

# Check dependencies
markitdown-gui --check-deps
```

**Log Analysis:**
```bash
# View recent errors (Linux/macOS)
tail -f ~/.local/share/markitdown-gui/logs/error.log

# Windows equivalent
type "%APPDATA%\markitdown-gui\logs\error.log"

# Filter by error level
grep "ERROR\|CRITICAL" ~/.local/share/markitdown-gui/logs/app.log
```

**Resource Monitoring:**
```bash
# Monitor resource usage during processing
# Linux
htop -p $(pgrep markitdown-gui)

# macOS
top -pid $(pgrep markitdown-gui)

# Windows PowerShell
Get-Process markitdown-gui | Format-Table Name,CPU,WorkingSet
```

## Installation Issues

### Python/Dependency Problems

#### "Python not found" Error
**Symptoms:**
- Command not recognized
- Import errors
- Missing module warnings

**Solutions:**
```bash
# Windows
# 1. Install Python from python.org
# 2. Add Python to PATH
# 3. Reinstall application

# macOS
brew install python@3.11
pip3 install markitdown-gui

# Linux
sudo apt update
sudo apt install python3 python3-pip
pip3 install markitdown-gui
```

#### PyQt6 Installation Failures
**Symptoms:**
- "No module named PyQt6"
- GUI components fail to load
- Blank application window

**Solutions:**
```bash
# Install PyQt6 separately
pip install PyQt6

# System package approach (Linux)
sudo apt install python3-pyqt6  # Ubuntu/Debian
sudo dnf install python3-qt6    # Fedora
```

#### Permission Errors During Installation
**Symptoms:**
- "Access denied" messages
- Installation fails partway
- Files locked or in use

**Solutions:**
```bash
# Install for current user only
pip install --user markitdown-gui

# Use virtual environment
python -m venv markitdown-env
source markitdown-env/bin/activate  # Linux/macOS
# markitdown-env\Scripts\activate   # Windows
pip install markitdown-gui
```

### Platform-Specific Installation Issues

#### Windows Issues

**🛡️ Security Software Interference**

*Issue*: "Windows Defender blocking execution"
- **Root Cause**: Antivirus false positive detection
- **Immediate Solution**: 
  1. Windows Security → Virus & threat protection → Add exclusion
  2. Add both installation directory and executable file
  3. Add MarkItDown GUI folder to real-time protection exclusions
- **Permanent Solution**: 
  1. Submit file to Microsoft for analysis
  2. Use digitally signed version when available
  3. Consider enterprise antivirus exemption policies
- **Verification**: `markitdown-gui --version` should work without warnings

*Issue*: "SmartScreen prevented an unrecognized app from starting"
- **Solution**: 
  1. Click "More info" → "Run anyway"
  2. Right-click executable → Properties → Unblock
  3. For enterprise: Add to SmartScreen allowlist

**📚 Runtime Library Issues**

*Issue*: "DLL load failed" or "MSVCP140.dll not found"
- **Root Cause**: Missing Visual C++ Runtime
- **Solution**: 
  1. Download Microsoft Visual C++ 2019+ Redistributable (x64)
  2. Install both x86 and x64 versions if unsure
  3. Restart system after installation
- **Alternative**: Use conda/miniconda installation method
- **Verification**: 
  ```cmd
  # Check installed redistributables
  wmic product where name="Microsoft Visual C++" get name,version
  ```

**🔧 PATH and Environment Issues**

*Issue*: "Python not found" or "Command not found"
- **Root Cause**: Python not in system PATH
- **Solution**: 
  1. System Properties → Environment Variables → Edit PATH
  2. Add Python installation directory
  3. Add Python Scripts directory
  4. Restart command prompt/terminal
- **Quick Fix**: Use full path to python executable
  ```cmd
  C:\Python311\python.exe -m markitdown_gui
  ```
- **Verification**: `python --version` and `pip --version` should work

**💾 Installation Location Issues**

*Issue*: "Access denied" during installation
- **Causes**: 
  - Installing to Program Files without admin rights
  - Antivirus blocking write access
  - User account restrictions
- **Solutions**: 
  1. Run command prompt as Administrator
  2. Use `--user` flag: `pip install --user markitdown-gui`
  3. Use virtual environment
  4. Change installation directory

#### macOS Issues

**🔒 Gatekeeper and Security Issues**

*Issue*: "App is damaged and can't be opened"
- **Root Cause**: Gatekeeper quarantine on downloaded files
- **Solution**: 
  ```bash
  # Remove quarantine attribute
  xattr -d com.apple.quarantine /Applications/MarkItDown-GUI.app
  
  # If app bundle doesn't exist, try:
  xattr -d com.apple.quarantine /usr/local/bin/markitdown-gui
  ```
- **Alternative**: System Preferences → Security & Privacy → Allow app
- **Enterprise**: Configure Gatekeeper policies

*Issue*: "markitdown-gui cannot be opened because the developer cannot be verified"
- **Solution**: 
  1. Control-click app → Open → Open (confirms exception)
  2. System Preferences → Security & Privacy → Open Anyway
  3. For command line: `spctl --assess --verbose /path/to/app`

**🐍 Python Environment Issues**

*Issue*: "Command not found" after pip installation
- **Root Cause**: Python Scripts not in PATH
- **Solution**: 
  ```bash
  # Add to ~/.zshrc or ~/.bash_profile
  export PATH="$HOME/Library/Python/3.x/bin:$PATH"
  
  # Or use full path
  ~/Library/Python/3.x/bin/markitdown-gui
  ```
- **Verification**: `which markitdown-gui` should return path

*Issue*: Multiple Python versions conflict
- **Solution**: 
  ```bash
  # Use specific Python version
  python3.11 -m pip install markitdown-gui
  
  # Or use pyenv for version management
  pyenv install 3.11.0
  pyenv global 3.11.0
  ```

**🖥️ Display and Graphics Issues**

*Issue*: "PyQt6 GUI not displaying correctly"
- **Solution**: 
  ```bash
  # Install Qt6 dependencies
  brew install qt6
  
  # Set Qt plugin path if needed
  export QT_PLUGIN_PATH=/opt/homebrew/plugins
  ```

#### Linux Issues

**🎨 Qt and Graphics Dependencies**

*Issue*: "Qt platform plugin could not be initialized"
- **Root Cause**: Missing Qt6 platform plugins
- **Solution by Distribution**: 
  ```bash
  # Ubuntu/Debian
  sudo apt update
  sudo apt install qt6-base-dev qt6-wayland libqt6gui6
  
  # Fedora/RHEL
  sudo dnf install qt6-qtbase-devel qt6-qtwayland
  
  # Arch Linux
  sudo pacman -S qt6-base qt6-wayland
  
  # openSUSE
  sudo zypper install qt6-base-devel qt6-wayland
  ```
- **Alternative**: Use Flatpak or AppImage version

*Issue*: "No module named '_tkinter'"
- **Solution**: 
  ```bash
  # Ubuntu/Debian
  sudo apt install python3-tk python3-dev
  
  # Fedora/RHEL
  sudo dnf install tkinter python3-devel
  
  # Arch Linux
  sudo pacman -S tk python-tkinter
  ```

**📦 Package Management Issues**

*Issue*: "pip installation fails with permission errors"
- **Solutions**: 
  ```bash
  # Use --user flag
  pip install --user markitdown-gui
  
  # Or use virtual environment
  python3 -m venv markitdown-env
  source markitdown-env/bin/activate
  pip install markitdown-gui
  
  # Or use system package manager
  # Check if available in distribution repos
  apt search markitdown  # Ubuntu/Debian
  dnf search markitdown  # Fedora
  ```

**🔍 Dependency Resolution**

*Issue*: "Conflicting dependencies" or "Version conflicts"
- **Diagnosis**: 
  ```bash
  # Check for conflicts
  pip check
  
  # List installed packages
  pip list | grep -E "(PyQt|markitdown|qt)"
  
  # Check specific package info
  pip show markitdown-gui
  ```
- **Solution**: 
  ```bash
  # Create clean environment
  python3 -m venv clean-env
  source clean-env/bin/activate
  pip install --upgrade pip
  pip install markitdown-gui
  ```

**🖼️ Display Server Issues**

*Issue*: "Cannot connect to X11 display" or Wayland issues
- **X11 Solution**: 
  ```bash
  # Ensure X11 forwarding (SSH)
  ssh -X user@host
  
  # Or set display
  export DISPLAY=:0
  ```
- **Wayland Solution**: 
  ```bash
  # Install Wayland support
  sudo apt install qt6-wayland
  
  # Force Wayland platform
  export QT_QPA_PLATFORM=wayland
  
  # Or force X11 on Wayland
  export QT_QPA_PLATFORM=xcb
  ```

### Universal Installation Recovery

**🔄 Complete Clean Installation**

When all else fails, perform a complete clean installation:

```bash
# Step 1: Complete removal
pip uninstall markitdown-gui
pip cache purge

# Step 2: Remove configuration
# Linux/macOS
rm -rf ~/.config/markitdown-gui
rm -rf ~/.local/share/markitdown-gui
rm -rf ~/.cache/markitdown-gui

# Windows
# Delete: %APPDATA%\markitdown-gui
# Delete: %LOCALAPPDATA%\markitdown-gui

# Step 3: Fresh installation
pip install --upgrade pip setuptools wheel
pip install markitdown-gui

# Step 4: Verify installation
markitdown-gui --version
markitdown-gui --test-installation
```

**📋 Installation Verification Checklist**

✅ **Post-Installation Verification:**
1. **Version check**: `markitdown-gui --version`
2. **Dependency check**: `markitdown-gui --check-deps`
3. **GUI test**: Launch application and check interface
4. **File test**: Convert a simple test file
5. **Configuration test**: Access settings menu
6. **Log check**: Verify log files are created
7. **Uninstall test**: Ensure clean removal works

## Application Startup Problems

### Application Won't Launch

#### Dependency Check
```bash
# Verify installation
markitdown-gui --version

# Test dependencies
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import markitdown; print('MarkItDown OK')"
```

#### Configuration Reset
```bash
# Remove configuration files (backup first)
# Windows: %APPDATA%\markitdown-gui
# macOS: ~/Library/Application Support/MarkItDown GUI
# Linux: ~/.config/markitdown-gui

# Create backup
cp -r ~/.config/markitdown-gui ~/.config/markitdown-gui.backup

# Reset configuration
rm -rf ~/.config/markitdown-gui
```

#### Clean Reinstallation
```bash
# Complete removal and reinstall
pip uninstall markitdown-gui
pip cache purge
pip install markitdown-gui
```

### Startup Crashes

#### Memory Issues
**Symptoms:**
- Application starts then immediately closes
- "Out of memory" errors
- System freezes during launch

**Solutions:**
1. **Close other applications** to free memory
2. **Increase virtual memory** (Windows)
3. **Check available RAM** - minimum 4GB recommended
4. **Disable startup programs** consuming memory

#### Graphics/Display Issues
**Symptoms:**
- Blank window
- Corrupted display
- Wrong window size

**Solutions:**
1. **Update graphics drivers**
2. **Reset window settings**
3. **Try different display scaling**
4. **Disable hardware acceleration** (if available)

#### Permission Problems
**Symptoms:**
- "Access denied" on startup
- Cannot write to directories
- Configuration file errors

**Solutions:**
1. **Run as administrator** (Windows) temporarily
2. **Check file permissions** on config directories
3. **Move to user directory** if installed system-wide
4. **Create directories manually** if missing

## File Processing Issues

### Files Won't Open

#### File Format Problems
**Symptoms:**
- "Unsupported format" error
- File appears in list but won't process
- Partial content extraction

**Diagnosis:**
```bash
# Check file type
file document.pdf
# or
file -i document.pdf  # MIME type
```

**Solutions:**
1. **Verify file extension** matches content
2. **Try opening in original application** first
3. **Convert to supported format** (e.g., DOC → DOCX)
4. **Check file corruption** by opening elsewhere

#### Permission Issues
**Symptoms:**
- "Access denied" errors
- Files locked or in use
- Network file problems

**Solutions:**
1. **Check file permissions** - ensure read access
2. **Close files in other applications**
3. **Copy files locally** if on network drive
4. **Run as administrator** if system files

#### Advanced File Corruption Detection

**🔍 Comprehensive File Integrity Analysis**

*Symptoms of Corruption:*
- Random errors during processing
- Incomplete or garbled output
- Application crashes on specific files
- Unexpected processing timeouts
- Memory access violations

*Multi-Stage Diagnosis Process:*

**Stage 1: Basic Integrity Checks**
```bash
# Check file size and basic properties
ls -la suspicious_file.pdf
file suspicious_file.pdf

# Verify file headers
hexdump -C suspicious_file.pdf | head
file --mime-type suspicious_file.pdf
```

**Stage 2: Format-Specific Validation**
```bash
# PDF validation
qpdf --check suspicious_file.pdf
pdfinfo suspicious_file.pdf

# Office document validation
unzip -t suspicious_file.docx  # Test ZIP structure

# Image validation
identify -verbose suspicious_file.jpg
exiftool suspicious_file.jpg
```

**Stage 3: Content Analysis**
```bash
# Extract and analyze content
strings suspicious_file.pdf | head -20

# Check for binary corruption
od -c suspicious_file.pdf | head

# Verify encoding
file -i suspicious_file.txt
```

**Stage 4: Comparative Analysis**
1. **Test with known good files** of same format
2. **Compare file structures** using hex editors
3. **Analyze processing patterns** across similar files
4. **Check source of files** (email, download, transfer)

**🛠️ File Recovery and Repair**

*PDF Recovery:*
```bash
# Attempt PDF repair
gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress damaged.pdf

# Alternative repair tools
qpdf --qdf --object-streams=disable input.pdf output.pdf
```

*Office Document Recovery:*
```bash
# Extract and rebuild DOCX
mkdir temp_docx
unzip suspicious.docx -d temp_docx/
# Edit/fix content in temp_docx/
cd temp_docx && zip -r ../repaired.docx *
```

*Image Recovery:*
```bash
# ImageMagick repair attempt
convert damaged.jpg -strip repaired.jpg

# GIMP batch repair
gimp --no-interface --batch='(repair-image "damaged.jpg" "repaired.jpg")' --batch='(gimp-quit 0)'
```

**📋 File Health Assessment Matrix**

| File Type | Health Check Command | Repair Method | Success Rate |
|-----------|---------------------|---------------|-------------|
| PDF | `qpdf --check file.pdf` | Ghostscript repair | 70-85% |
| DOCX | `unzip -t file.docx` | Extract/rebuild | 80-90% |
| XLSX | `unzip -t file.xlsx` | Extract/rebuild | 75-85% |
| PPTX | `unzip -t file.pptx` | Extract/rebuild | 70-80% |
| JPG/PNG | `identify file.jpg` | ImageMagick | 60-75% |
| TIFF | `tiffinfo file.tif` | libtiff tools | 65-80% |

**⚠️ Prevention Strategies**

*File Transfer Best Practices:*
1. **Use checksums** to verify file integrity
2. **Avoid email attachments** for large files
3. **Use reliable transfer methods** (cloud storage, SFTP)
4. **Verify files immediately** after transfer
5. **Keep original backups** before processing

*Storage Best Practices:*
1. **Regular disk health checks**
2. **Use error-correcting file systems** (ZFS, BTRFS)
3. **Implement backup strategies** (3-2-1 rule)
4. **Monitor storage device health**
5. **Avoid processing from failing drives**

### Conversion Failures

#### Advanced OCR Troubleshooting

**🔤 Text Recognition Quality Issues**

*Detailed Symptom Analysis:*
- **Poor accuracy**: >20% character errors
- **Missing text blocks**: Entire sections not recognized
- **Garbled output**: Nonsensical character combinations
- **Inconsistent results**: Different results on same file
- **Language confusion**: Wrong language detected
- **Layout disruption**: Text order scrambled

*Root Cause Analysis Matrix:*

| Symptom | Likely Cause | Diagnostic Test | Solution Priority |
|---------|--------------|-----------------|------------------|
| Low accuracy | Poor image quality | Check DPI/resolution | High |
| Missing text | Wrong language setting | Test with correct language | Critical |
| Garbled output | Font issues | Test with standard fonts | High |
| Layout issues | Complex formatting | Simplify source layout | Medium |
| Inconsistent results | OCR engine limits | Try different engines | Medium |
| Performance issues | Resource constraints | Monitor system resources | High |

**📊 Image Quality Optimization**

*Pre-processing Pipeline:*
```bash
# Enhance image quality for OCR
# Increase resolution
convert input.jpg -density 300 -quality 100 enhanced.jpg

# Improve contrast
convert input.jpg -normalize -contrast-stretch 0.1%x0.1% contrast.jpg

# Remove noise
convert input.jpg -despeckle -noise 1 cleaned.jpg

# Deskew if needed
convert input.jpg -deskew 40% deskewed.jpg

# Comprehensive preprocessing
convert input.jpg \
  -density 300 \
  -colorspace Gray \
  -normalize \
  -contrast-stretch 0.1%x0.1% \
  -despeckle \
  -noise 1 \
  -deskew 40% \
  optimized.jpg
```

*Quality Assessment Tools:*
```bash
# Check image properties
identify -verbose image.jpg | grep -E "(Resolution|Quality|Depth)"

# Measure image sharpness
convert image.jpg -colorspace Gray -format "%[fx:100*image.standard_deviation]" info:

# Check text detectability
tesseract image.jpg - --psm 0  # Page segmentation info
```

**🌐 Language and Localization Issues**

*Multi-language OCR Configuration:*
```bash
# Install additional language packs
# Ubuntu/Debian
sudo apt install tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-fra

# Check available languages
tesseract --list-langs

# Test language detection
tesseract image.jpg - -l eng+spa+fra --psm 1
```

*Language-Specific Optimization:*
- **English**: Default settings usually work well
- **Chinese/Japanese/Korean**: Require specific models and vertical text support
- **Arabic/Hebrew**: Right-to-left text handling needed
- **European**: Accent and special character support
- **Mixed languages**: Use multiple language models

**⚙️ OCR Engine Selection and Tuning**

*Engine Comparison Matrix:*

| Engine | Best For | Accuracy | Speed | Resource Use |
|--------|----------|----------|-------|--------------|
| Tesseract 5 | General text | 85-95% | Medium | Low |
| ABBYY FineReader | Professional docs | 95-98% | Fast | High |
| Google Cloud Vision | Cloud processing | 90-96% | Fast | API-dependent |
| AWS Textract | Forms/tables | 88-94% | Fast | API-dependent |
| Azure Cognitive | Modern layouts | 90-95% | Fast | API-dependent |

*Tesseract Optimization:*
```bash
# Page segmentation modes
--psm 0   # Orientation and script detection
--psm 1   # Automatic page segmentation with OSD
--psm 3   # Fully automatic page segmentation (default)
--psm 6   # Uniform block of text
--psm 8   # Single word
--psm 13  # Raw line. Treat image as single text line

# OCR Engine modes
--oem 0   # Legacy engine only
--oem 1   # Neural nets LSTM engine only
--oem 2   # Legacy + LSTM engines
--oem 3   # Default, based on what's available

# Advanced configuration
tesseract image.jpg output \
  -l eng \
  --psm 6 \
  --oem 1 \
  -c preserve_interword_spaces=1 \
  -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

**🔧 Advanced OCR Configuration**

*Custom Training for Specific Fonts:*
1. **Collect training data**: 100+ samples of target font
2. **Create ground truth**: Manually verified text
3. **Train custom model**: Use Tesseract training tools
4. **Validate accuracy**: Test on held-out samples
5. **Deploy model**: Integrate with MarkItDown GUI

*Layout Analysis Optimization:*
```python
# Custom layout analysis
import cv2
import numpy as np

def optimize_layout(image_path):
    # Load and preprocess
    img = cv2.imread(image_path, 0)
    
    # Detect text regions
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    grad = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
    
    # Find contours (text blocks)
    contours, _ = cv2.findContours(grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort by reading order (top to bottom, left to right)
    contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    
    return contours
```

**📈 OCR Quality Metrics and Monitoring**

*Automated Quality Assessment:*
```bash
# Character accuracy measurement
# Compare OCR output with ground truth
python -c "
import difflib
with open('ground_truth.txt') as f: truth = f.read()
with open('ocr_output.txt') as f: output = f.read()
accuracy = difflib.SequenceMatcher(None, truth, output).ratio()
print(f'Accuracy: {accuracy*100:.2f}%')
"
```

*Performance Monitoring:*
- **Processing time per page**
- **Accuracy by document type**
- **Error patterns by language**
- **Resource utilization trends**
- **User satisfaction scores**

**🚨 OCR Failure Recovery Procedures**

*When OCR Completely Fails:*
1. **Manual text extraction**: Copy-paste from original application
2. **Alternative OCR services**: Try cloud-based services
3. **Hybrid approach**: OCR + manual correction
4. **Document recreation**: Retype if critical
5. **Format conversion**: Convert to text-friendly format first

*Partial Failure Recovery:*
1. **Block-by-block processing**: Process sections individually
2. **Multi-pass OCR**: Different settings for different regions
3. **Interactive correction**: Manual review and correction
4. **Template matching**: Use templates for repeated layouts
5. **Machine learning**: Train custom models for specific document types

#### Memory/Resource Exhaustion
**Symptoms:**
- Process stops partway
- "Out of memory" errors
- System becomes unresponsive

**Solutions:**
1. **Reduce batch size** - process fewer files at once
2. **Increase virtual memory/swap**
3. **Close other applications**
4. **Process files individually**
5. **Restart application** to clear memory

#### Timeout Issues
**Symptoms:**
- "Operation timed out" messages
- Long-running processes never complete
- Partial conversions

**Solutions:**
1. **Increase timeout values** in settings
2. **Break large files** into smaller sections
3. **Check system performance** - ensure adequate resources
4. **Process overnight** for large batches

## Performance Problems

### Slow Processing

#### System Resource Analysis
```bash
# Monitor resource usage during processing
# Windows: Task Manager
# macOS: Activity Monitor
# Linux: htop, top, or system monitor
```

#### Memory Optimization
**Symptoms:**
- Slow conversion speed
- High memory usage
- System lag during processing

**Solutions:**
1. **Increase available RAM**
   - Close unnecessary applications
   - Increase virtual memory
   - Add physical RAM if possible

2. **Optimize settings**
   - Reduce quality settings
   - Disable preview during batch processing
   - Limit concurrent operations

3. **File management**
   - Process smaller batches
   - Use local storage (not network)
   - Clear temporary files regularly

#### CPU Optimization
**Symptoms:**
- High CPU usage
- Fan noise increase
- Other applications slow

**Solutions:**
1. **Adjust processing priority**
   - Lower application priority
   - Limit CPU usage percentage
   - Enable background processing mode

2. **Parallel processing**
   - Reduce concurrent threads
   - Balance CPU cores usage
   - Consider single-threaded mode

#### Storage Performance
**Symptoms:**
- Slow file loading
- Delayed output saving
- High disk usage

**Solutions:**
1. **Use faster storage**
   - SSD vs HDD
   - Local vs network storage
   - Adequate free space (20%+ recommended)

2. **Optimize disk usage**
   - Clear temporary files
   - Defragment disk (Windows)
   - Check disk health

### Application Responsiveness

#### UI Freezing
**Symptoms:**
- Interface becomes unresponsive
- Progress bars stop updating
- Cannot cancel operations

**Solutions:**
1. **Enable background processing**
2. **Reduce UI update frequency**
3. **Use batch mode** instead of real-time preview
4. **Process files overnight** unattended

#### Memory Leaks
**Symptoms:**
- Memory usage increases over time
- Application slows after extended use
- System performance degrades

**Solutions:**
1. **Restart application** periodically
2. **Clear cache** regularly
3. **Update to latest version**
4. **Report bug** if persistent

## Output Quality Issues

### Text Recognition Problems

#### Poor OCR Accuracy
**Common Causes:**
- Low source image resolution
- Poor image quality (blur, noise)
- Incorrect language settings
- Complex fonts or layouts

**Improvement Strategies:**
1. **Source optimization**
   - Use 300+ DPI images
   - Ensure high contrast
   - Remove background noise
   - Use standard fonts when possible

2. **OCR configuration**
   - Set correct language
   - Enable multiple language support
   - Adjust recognition confidence
   - Use appropriate OCR engine

3. **Post-processing**
   - Manual text review and correction
   - Find and replace common errors
   - Spell check final output
   - Compare with original document

#### Formatting Issues
**Symptoms:**
- Lost formatting in output
- Incorrect table structure
- Missing links or references

**Solutions:**
1. **Adjust conversion settings**
   - Enable formatting preservation
   - Choose appropriate output format
   - Configure style mapping

2. **Source preparation**
   - Simplify complex formatting
   - Use standard styles
   - Remove unnecessary elements

3. **Post-processing**
   - Manual formatting correction
   - Template-based formatting
   - Style sheet application

### Structure Recognition Problems

#### Table Extraction Issues
**Symptoms:**
- Tables converted to plain text
- Missing table borders/structure
- Incorrect cell alignment

**Solutions:**
1. **Source optimization**
   - Use clear table borders
   - Ensure adequate spacing
   - Avoid merged cells if possible

2. **Processing settings**
   - Enable table detection
   - Adjust table recognition sensitivity
   - Use structured output format

#### Header/Footer Problems
**Symptoms:**
- Headers/footers mixed with content
- Missing page structure
- Duplicate information

**Solutions:**
1. **Configure header/footer handling**
2. **Manual removal** if necessary
3. **Use content filtering** options

## System Integration Problems

### File Association Issues

#### Default Application Settings
**Problem**: MarkItDown GUI doesn't open files when double-clicked
**Solutions:**
1. **Windows**: Right-click file → Open with → Choose default program
2. **macOS**: Right-click file → Get Info → Open with → Change All
3. **Linux**: Update MIME type associations

#### Context Menu Integration
**Problem**: Missing "Convert with MarkItDown" in context menu
**Solutions:**
1. **Reinstall application** with context menu option
2. **Manual registry edit** (Windows) - advanced users only
3. **Use drag-and-drop** alternative

### External Tool Integration

#### Text Editor Integration
**Problem**: Cannot open results in preferred editor
**Solutions:**
1. **Configure external editor** in settings
2. **Check editor path** and permissions
3. **Use system default** as fallback

#### Cloud Storage Sync Issues
**Problem**: Files not syncing or causing conflicts
**Solutions:**
1. **Pause sync** during processing
2. **Use local processing** directory
3. **Configure sync exclusions**

## Advanced Troubleshooting

### Diagnostic Information Collection

#### System Information
```bash
# Collect system info for support
markitdown-gui --system-info > system-info.txt

# Manual collection
python --version
pip list | grep -E "(PyQt|markitdown)"
uname -a  # Linux/macOS
systeminfo  # Windows
```

#### Log File Analysis
**Location of log files:**
- **Windows**: `%APPDATA%\markitdown-gui\logs\`
- **macOS**: `~/Library/Logs/MarkItDown GUI/`
- **Linux**: `~/.local/share/markitdown-gui/logs/`

**Common log patterns:**
- `ERROR`: Critical issues requiring attention
- `WARNING`: Potential problems or suboptimal conditions
- `INFO`: Normal operation information
- `DEBUG`: Detailed diagnostic information

#### Memory Dump Analysis
For persistent crashes:
1. **Enable crash reporting**
2. **Collect memory dumps** when crashes occur
3. **Submit to support** with steps to reproduce

### Performance Profiling

#### Resource Monitoring
```bash
# Monitor during processing
# Linux
htop -p $(pgrep -f markitdown-gui)

# Windows PowerShell
Get-Process markitdown-gui | Format-Table Name,CPU,WorkingSet

# macOS
top -pid $(pgrep -f markitdown-gui)
```

#### Bottleneck Identification
1. **CPU bottleneck**: High CPU usage, normal memory
2. **Memory bottleneck**: High memory usage, possible swapping
3. **I/O bottleneck**: High disk/network usage, low CPU
4. **Application bottleneck**: Low resource usage, slow processing

### Recovery Procedures

#### Corrupted Configuration Recovery
```bash
# Backup current config
cp -r ~/.config/markitdown-gui ~/.config/markitdown-gui.backup

# Reset to defaults
rm -rf ~/.config/markitdown-gui

# Restore partial settings if needed
mkdir -p ~/.config/markitdown-gui
# Copy specific config files back
```

#### Cache Cleanup
```bash
# Clear application cache
rm -rf ~/.cache/markitdown-gui

# Clear temporary files
rm -rf /tmp/markitdown-*  # Linux/macOS
# Delete %TEMP%\markitdown-* # Windows
```

#### Complete Application Reset
```bash
# Full reset (backup important data first)
pip uninstall markitdown-gui
rm -rf ~/.config/markitdown-gui
rm -rf ~/.local/share/markitdown-gui
rm -rf ~/.cache/markitdown-gui
pip install markitdown-gui
```

---

## Network and Connectivity Issues

### Cloud Service Integration Problems

**☁️ Cloud Storage Access Issues**

*Google Drive Integration:*
```bash
# Test Google Drive connectivity
curl -I "https://www.googleapis.com/drive/v3/files"

# Check authentication
markitdown-gui --test-google-auth

# Re-authenticate if needed
markitdown-gui --reauth-google
```

*Common Solutions:*
- **API key expired**: Refresh authentication tokens
- **Rate limiting**: Implement exponential backoff
- **Network firewall**: Configure proxy/firewall rules
- **Permission issues**: Verify cloud service permissions

**🌐 LLM Service Connectivity**

*API Connection Diagnostics:*
```bash
# Test OpenAI connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "https://api.openai.com/v1/models"

# Test Azure OpenAI
curl -H "api-key: $AZURE_OPENAI_KEY" \
     "https://your-resource.openai.azure.com/openai/deployments"

# Test local LLM connectivity
curl "http://localhost:11434/api/tags"  # Ollama
```

*Troubleshooting Steps:*
1. **Verify API credentials** in settings
2. **Check service status** on provider websites
3. **Test network connectivity** to service endpoints
4. **Review rate limits** and usage quotas
5. **Configure proxy settings** if behind corporate firewall

### Proxy and Firewall Configuration

**🔧 Corporate Network Setup**

*Proxy Configuration:*
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com

# Configure in application
markitdown-gui --set-proxy http://proxy.company.com:8080
```

*Firewall Rules:*
- **Outbound HTTPS (443)**: For cloud services
- **Outbound HTTP (80)**: For some API services
- **Custom ports**: For local LLM services (11434, 8080, etc.)

**🛡️ SSL/TLS Certificate Issues**

*Certificate Validation Problems:*
```bash
# Test SSL connectivity
openssl s_client -connect api.openai.com:443

# Check certificate chain
curl -vI https://api.openai.com

# Disable SSL verification (temporary)
markitdown-gui --no-ssl-verify
```

*Enterprise Certificate Solutions:*
1. **Install corporate root certificates**
2. **Configure certificate bundle path**
3. **Use internal certificate authority**
4. **Implement certificate pinning**

## Security and Permissions

### File System Permissions

**📁 Access Control Issues**

*Permission Diagnosis:*
```bash
# Check file permissions
ls -la problem_file.pdf

# Check directory permissions
ls -ld /path/to/directory

# Test read access
test -r problem_file.pdf && echo "Readable" || echo "Not readable"

# Test write access to output directory
test -w /output/directory && echo "Writable" || echo "Not writable"
```

*Permission Repair:*
```bash
# Fix file permissions
chmod 644 file.pdf  # Read for user, group; no access for others
chmod 755 directory  # Read/execute for all, write for user

# Fix ownership
sudo chown user:group file.pdf

# Recursive permission fix
find /path/to/files -type f -exec chmod 644 {} \;
find /path/to/files -type d -exec chmod 755 {} \;
```

**🔐 Elevated Privileges**

*When to Use Administrator/Root:*
- ✅ Installing system-wide dependencies
- ✅ Accessing system-protected files
- ✅ Modifying system configuration
- ❌ Regular file processing (security risk)
- ❌ Running the application normally

*Safe Privilege Escalation:*
```bash
# Linux/macOS: Use sudo for specific commands only
sudo chmod 644 /protected/file.pdf
markitdown-gui  # Run as normal user

# Windows: Run specific operations as administrator
# Use "Run as administrator" only when necessary
```

### Security Best Practices

**🛡️ Secure Configuration**

*API Key Management:*
1. **Environment variables**: Store keys outside application
2. **Key rotation**: Regularly update API keys
3. **Scope limitation**: Use minimum required permissions
4. **Audit logging**: Monitor API key usage
5. **Secure storage**: Use system keyring/vault

*File Processing Security:*
1. **Sandbox mode**: Isolate file processing
2. **Input validation**: Verify file types and sizes
3. **Temporary file cleanup**: Secure deletion of temp files
4. **Network isolation**: Disable unnecessary network access
5. **Resource limits**: Prevent resource exhaustion attacks

## Emergency Recovery Procedures

### Data Recovery

**💾 Configuration Recovery**

*Backup and Restore Configuration:*
```bash
# Create configuration backup
cp -r ~/.config/markitdown-gui ~/.config/markitdown-gui.backup.$(date +%Y%m%d)

# Restore from backup
cp -r ~/.config/markitdown-gui.backup.20240315 ~/.config/markitdown-gui

# Export settings for migration
markitdown-gui --export-settings settings.json

# Import settings
markitdown-gui --import-settings settings.json
```

*Configuration Validation:*
```bash
# Validate configuration file
markitdown-gui --validate-config

# Test configuration
markitdown-gui --test-config

# Reset to defaults if corrupted
markitdown-gui --reset-config
```

**📄 Processed File Recovery**

*Automatic Backup Recovery:*
```bash
# Check for automatic backups
ls ~/.local/share/markitdown-gui/backups/

# Restore specific backup
cp ~/.local/share/markitdown-gui/backups/file.md.20240315 ./file.md

# Bulk restore
find ~/.local/share/markitdown-gui/backups/ -name "*.md" -newer reference_file |
  while read backup; do
    cp "$backup" "./$(basename "$backup" | sed 's/\.[0-9]\{8\}$//')"
  done
```

*Version History Recovery:*
- **Git integration**: If enabled, recover from git history
- **Cloud sync**: Restore from cloud storage version history
- **Manual backups**: Check user-created backup locations

### System Recovery

**🔄 Complete Application Reset**

*Nuclear Option - Complete Reset:*
```bash
#!/bin/bash
# COMPLETE RESET SCRIPT - USE WITH CAUTION

echo "Starting complete MarkItDown GUI reset..."

# 1. Stop all instances
pkill -f markitdown-gui

# 2. Backup current state
backup_dir="markitdown-backup-$(date +%Y%m%d-%H%M%S)"
mkdir "$backup_dir"
cp -r ~/.config/markitdown-gui "$backup_dir/config" 2>/dev/null
cp -r ~/.local/share/markitdown-gui "$backup_dir/data" 2>/dev/null
cp -r ~/.cache/markitdown-gui "$backup_dir/cache" 2>/dev/null

# 3. Complete removal
pip uninstall -y markitdown-gui
rm -rf ~/.config/markitdown-gui
rm -rf ~/.local/share/markitdown-gui
rm -rf ~/.cache/markitdown-gui

# 4. Clean pip cache
pip cache purge

# 5. Fresh installation
pip install --upgrade pip
pip install markitdown-gui

# 6. Verify installation
if markitdown-gui --version; then
    echo "Reset successful! Backup saved to: $backup_dir"
else
    echo "Reset failed! Restore from backup if needed."
fi
```

**🏥 Disaster Recovery Plan**

*Recovery Priority Matrix:*

| Priority | Data Type | Recovery Method | RTO* | RPO** |
|----------|-----------|-----------------|------|-------|
| Critical | User settings | Config backup | 5 min | 1 day |
| High | Processing queue | Session restore | 15 min | 1 hour |
| Medium | Cache data | Rebuild cache | 30 min | 1 day |
| Low | Log files | Regenerate | 60 min | 1 week |

*RTO = Recovery Time Objective, RPO = Recovery Point Objective

*Business Continuity:*
1. **Alternative processing**: Use cloud services temporarily
2. **Manual processing**: Convert critical files manually
3. **Rollback plan**: Revert to previous working version
4. **Escalation**: Contact support for critical business needs

## Professional Support

### Support Tiers

**🆓 Community Support**
- **GitHub Issues**: Bug reports and feature requests
- **Discussion Forums**: Community help and tips
- **Documentation**: Self-service troubleshooting
- **Video Tutorials**: Visual learning resources
- **Response Time**: Best effort, 24-72 hours

**💼 Professional Support**
- **Email Support**: Direct access to developers
- **Priority Handling**: Faster response times
- **Remote Assistance**: Screen sharing and direct help
- **Custom Solutions**: Tailored troubleshooting
- **Response Time**: 4-8 hours business days

**🏢 Enterprise Support**
- **Dedicated Support Manager**: Single point of contact
- **Phone Support**: Direct phone access
- **On-site Support**: Physical presence if needed
- **Custom Development**: Feature development services
- **Response Time**: 1-2 hours, 24/7 for critical issues

### When to Escalate

**🚨 Immediate Escalation (Critical Issues)**
- Data loss or corruption
- Security vulnerabilities discovered
- Application completely unusable
- Business operations significantly impacted
- Suspected malware or security breach

**⚠️ Standard Escalation (High Priority)**
- Major features not working
- Performance severely degraded
- Workarounds not available
- Multiple users affected
- Compliance requirements at risk

**📋 Information to Provide**

*Essential Information:*
```bash
# System information
markitdown-gui --system-info > system_info.txt

# Error logs
cp ~/.local/share/markitdown-gui/logs/error.log ./

# Configuration (remove sensitive data)
cp ~/.config/markitdown-gui/config.ini config_sanitized.ini

# Steps to reproduce
echo "1. Launch application
2. Load file: example.pdf
3. Click Convert
4. Error occurs" > reproduction_steps.txt
```

*Additional Context:*
- When did the problem start?
- What changed recently?
- How many users affected?
- Business impact level
- Preferred resolution timeline
- Available maintenance windows

**📞 Contact Information**

- **Community**: GitHub Issues and Discussions
- **Professional**: support@markitdown-gui.com
- **Enterprise**: enterprise@markitdown-gui.com
- **Security**: security@markitdown-gui.com
- **Emergency**: +1-555-SUPPORT (Enterprise only)

---

**Getting Additional Help:**
- 📖 [User Manual](user-manual.md) - Complete usage guide
- ❓ [FAQ](faq.md) - Frequently asked questions
- 🐛 [Report Issues](../contributing/issue-templates.md) - Bug reporting
- 💬 Community support forums
- 📧 Professional support email
- 🆘 Emergency support hotline (Enterprise)
- 🎓 [Step-by-Step Tutorials](tutorials.md) - Comprehensive learning materials
- 🚀 [Quick Start Guide](quick-start.md) - Get up and running quickly
- 🗂️ [File Formats Guide](file-formats.md) - Format compatibility reference
- 🔧 [Installation Guide](installation.md) - Setup and configuration help
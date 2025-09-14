# MarkItDown GUI - Quick Start Guide

**⚡ Get up and running in 5 minutes or less!**

Welcome to MarkItDown GUI - the fastest way to convert any document to clean, professional Markdown. This quick start guide will have you converting files like a pro in just a few steps.

## What You'll Accomplish

By the end of this 5-minute guide, you'll:
- ✅ Have MarkItDown GUI installed and running
- ✅ Convert your first document successfully  
- ✅ Understand the basic interface and workflow
- ✅ Know where to go for advanced features

**Time Investment**: 5 minutes | **Skill Level**: Complete beginner

---

## Table of Contents

1. [Prerequisites](#prerequisites) - What you need before starting
2. [Installation](#installation) - Get the software installed  
3. [First Launch](#first-launch) - Initial setup and orientation
4. [Your First Conversion](#your-first-conversion) - Convert a document in under 60 seconds
5. [Essential Features](#essential-features) - Core capabilities overview
6. [Next Steps](#next-steps) - Where to go from here

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- **PyQt6** support (automatically installed)
- **Sufficient disk space** for document processing
- **Internet connection** for initial setup

## Installation

### Option 1: Quick Install (Recommended)
```bash
# Download and run the installer
pip install markitdown-gui

# Launch the application
markitdown-gui
```

### Option 2: From Source
```bash
# Clone the repository
git clone https://github.com/your-org/markitdown-gui.git
cd markitdown-gui

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

For detailed installation instructions, see the [Installation Guide](installation.md).

## First Launch

1. **Launch the Application**
   - Double-click the desktop shortcut, or
   - Run `markitdown-gui` from command line

2. **Initial Setup**
   - Select your preferred language
   - Choose a theme (Light/Dark/Auto)
   - Configure default output directory

3. **Interface Overview**
   ```
   ┌─────────────────────────────────────────┐
   │ File  Edit  View  Tools  Help          │ Menu Bar
   ├─────────────────────────────────────────┤
   │ [📁] [🔄] [⚙️] [?]                      │ Toolbar
   ├─────────────────────────────────────────┤
   │                                         │
   │ Drag & Drop Files Here                  │ Main Area
   │ or Click to Browse                      │
   │                                         │
   ├─────────────────────────────────────────┤
   │ Ready | 0 files processed              │ Status Bar
   └─────────────────────────────────────────┘
   ```

## Your First Conversion

**🎯 Goal**: Convert a document to Markdown in under 60 seconds

### Step-by-Step Process

**Step 1: Add Your File** *(10 seconds)*
```
Two easy methods:
Method A (Recommended): Drag any document into the window
Method B: Click the 📁 "Open Files" button
```

**Step 2: Verify Settings** *(5 seconds)*
- Output format: ✅ Markdown (.md) ← Perfect default
- Output location: ✅ Same folder as input ← Good to go
- Processing quality: ✅ Balanced ← Ideal for most files

**Step 3: Convert** *(30 seconds)*
```
Click the big 🔄 "Convert" button
Watch the progress bar fill up
Status shows "Processing..." then "Complete!"
```

**Step 4: Review Results** *(15 seconds)*
- Preview appears automatically in the right panel
- Scroll through to verify content looks good
- Click "Save" if you're happy with the results

**🎉 Success!** You've just converted your first document!

### What Just Happened?

MarkItDown GUI automatically:
- ✅ Detected your file type and chose optimal settings
- ✅ Extracted text while preserving formatting structure  
- ✅ Converted to clean, readable Markdown
- ✅ Made it available for preview and saving

---

## Essential Features

### What Can You Convert?

**📄 Documents**: PDF, Word, PowerPoint, Excel  
**🌐 Web Content**: HTML, EPUB, XML  
**🖼️ Images**: JPG, PNG (with text recognition)  
**📝 Text Files**: TXT, LOG, Markdown, JSON

### Key Features at a Glance

**Batch Processing**: Convert multiple files at once
```
Drop 10 PDFs → Click "Batch Convert" → Get 10 Markdown files
Takes just a few minutes!
```

**OCR (Text Recognition)**: Extract text from images and scanned PDFs
```
Scanned document → Enable OCR → Get editable text
Works in 100+ languages!
```

**Quality Control**: Multiple quality settings
```
🚀 Fast: Quick conversions for drafts
⚖️ Balanced: Good quality, reasonable speed  
🔬 High: Maximum accuracy for important docs
```

**Smart Preview**: See results before saving
```
Original document ↔ Converted Markdown
Side-by-side comparison for quality checking
```

---

## Essential Shortcuts

**⌨️ Master These 5 Shortcuts**:
- `Ctrl+O` → Open files quickly
- `F5` → Start conversion  
- `Ctrl+S` → Save results
- `F1` → Get help when stuck
- `Escape` → Cancel if something goes wrong

---

## Next Steps

**🚀 Ready to Become a Power User?**

### Immediate Next Steps (Choose Your Path)

**📊 For Business Users**:
- Set up [batch processing](tutorials.md#tutorial-7-efficient-batch-workflows) for multiple files
- Configure [custom templates](user-manual.md#format-templates) for consistent output
- Learn [quality control](user-manual.md#quality-control) workflows

**🎓 For Students/Researchers**:
- Master [OCR for scanned documents](tutorials.md#tutorial-5-ocr-and-image-processing)
- Set up [academic document processing](tutorials.md#tutorial-11-academic-and-research-documents)
- Learn [citation preservation](user-manual.md#academic-document-settings)

**⚙️ For Developers/Technical Users**:
- Explore [command line integration](user-manual.md#command-line-integration)
- Set up [Git workflow automation](tutorials.md#tutorial-10-integration-with-external-tools)
- Configure [API integration](user-manual.md#api-integration)

### Learning Resources

**📚 Complete Documentation Suite**:
- 📖 [**User Manual**](user-manual.md) - Complete feature reference (45min read)
- 📝 [**Step-by-Step Tutorials**](tutorials.md) - 15 hands-on tutorials with examples
- 🔧 [**Installation Guide**](installation.md) - Advanced setup and configuration
- 🗂️ [**File Formats Guide**](file-formats.md) - Detailed format support information
- 🆘 [**Troubleshooting Guide**](troubleshooting.md) - Problem-solving reference
- ❓ [**FAQ**](faq.md) - Common questions and expert answers

### Quick Wins (Try These Next!)

**🎯 5-Minute Improvements**:
1. **Customize Your Workspace**: Tools → Preferences → Set your preferred theme and defaults
2. **Create a Template**: Design a custom output format for your documents
3. **Set Up Batch Processing**: Convert 5+ files at once for efficiency
4. **Enable OCR**: Try converting a scanned PDF or image with text

**🎯 15-Minute Power Features**:
1. **Watch Folder Automation**: Auto-convert files dropped in a specific folder
2. **Quality Control Setup**: Configure validation and review workflows
3. **Keyboard Shortcuts**: Master the 10 most useful shortcuts
4. **Integration Setup**: Connect with your text editor or cloud storage

### Common Next Questions

**Q: "How do I convert 50 PDFs at once?"**  
→ See [Batch Processing Tutorial](tutorials.md#tutorial-7-efficient-batch-workflows)

**Q: "Can I automate this for my team?"**  
→ Check [Workflow Automation](tutorials.md#tutorial-9-watch-folder-setup)

**Q: "How do I get better OCR results?"**  
→ Read [OCR Optimization Guide](tutorials.md#tutorial-5-ocr-and-image-processing)

**Q: "What about very large files?"**  
→ See [Performance Optimization](user-manual.md#performance-optimization)

---

## Quick Reference Card

**🔥 Essential Knowledge** *(Print This!)*

**File Support**: PDF, Word, Excel, PowerPoint, HTML, Images + OCR  
**Output**: Markdown, HTML, Plain Text, JSON + Custom Templates  
**Batch**: Unlimited files, smart queuing, progress tracking  
**Quality**: 3 levels (Fast/Balanced/High) + Custom settings  

**⌨️ Must-Know Shortcuts**:
- `Ctrl+O` → Open files | `F5` → Convert | `Ctrl+S` → Save
- `F1` → Help | `Escape` → Cancel | `Ctrl+,` → Settings

**🆘 Getting Help**:
- Help menu (`F1`) for built-in documentation
- Error messages link to specific troubleshooting steps  
- Status bar shows detailed progress and tips
- Email support: support@markitdown-gui.com

---

## 🎉 Congratulations!

You're now ready to convert documents like a pro! Remember:

✅ **Start Simple**: Master basic conversions first  
✅ **Experiment**: Try different file types and settings  
✅ **Batch Process**: Group similar files for efficiency  
✅ **Quality Check**: Always preview important conversions  
✅ **Automate**: Set up workflows that save time  

**Happy Converting!** 🚀

*Need help? Check the [complete documentation library](user-manual.md#additional-resources) or reach out to our friendly support team.*
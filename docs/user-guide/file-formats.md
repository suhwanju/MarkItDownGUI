# File Format Support

Comprehensive guide to supported input and output formats in MarkItDown GUI.

## Table of Contents

- [Supported Input Formats](#supported-input-formats)
- [Output Format Options](#output-format-options)
- [Format-Specific Notes](#format-specific-notes)
- [Conversion Quality Matrix](#conversion-quality-matrix)
- [Troubleshooting Format Issues](#troubleshooting-format-issues)

## Supported Input Formats

### Document Formats

#### Microsoft Office Documents
| Format | Extension | Support Level | Notes |
|--------|-----------|---------------|-------|
| Word Document | `.docx` | ✅ Full | Modern format, best support |
| Word 97-2003 | `.doc` | ⚠️ Limited | Legacy format, reduced features |
| Rich Text | `.rtf` | ✅ Good | Cross-platform compatibility |

**Features Supported:**
- Text content and formatting
- Headers and footers
- Tables and lists
- Embedded images
- Hyperlinks and cross-references
- Comments and track changes (optional)

#### PDF Documents
| Format | Extension | Support Level | OCR Required |
|--------|-----------|---------------|--------------|
| Text-based PDF | `.pdf` | ✅ Full | No |
| Image-based PDF | `.pdf` | ⚠️ OCR | Yes |
| Secured PDF | `.pdf` | ❌ Limited | Password required |

**Features Supported:**
- Selectable text extraction
- Basic formatting preservation
- Table structure detection
- Image extraction
- Metadata preservation

#### OpenDocument Formats
| Format | Extension | Support Level | Notes |
|--------|-----------|---------------|-------|
| OpenDocument Text | `.odt` | ✅ Good | LibreOffice/OpenOffice |
| OpenDocument Presentation | `.odp` | ⚠️ Basic | Slide content only |
| OpenDocument Spreadsheet | `.ods` | ⚠️ Basic | Table data extraction |

### Presentation Formats

#### Microsoft PowerPoint
| Format | Extension | Support Level | Content Extracted |
|--------|-----------|---------------|-------------------|
| PowerPoint | `.pptx` | ✅ Good | Slides, speaker notes |
| PowerPoint 97-2003 | `.ppt` | ⚠️ Limited | Basic slide content |

**Features Supported:**
- Slide titles and content
- Speaker notes
- Slide transitions (as text)
- Embedded images
- Charts and diagrams (as images)

### Spreadsheet Formats

#### Microsoft Excel
| Format | Extension | Support Level | Data Extraction |
|--------|-----------|---------------|----------------|
| Excel Workbook | `.xlsx` | ✅ Good | All sheets, formulas |
| Excel 97-2003 | `.xls` | ⚠️ Limited | Basic data only |
| CSV Files | `.csv` | ✅ Full | Complete data |

**Features Supported:**
- Multiple worksheets
- Cell data and formulas
- Basic formatting
- Charts (as descriptions)
- Data validation rules

### Web and Markup Formats

#### Web Documents
| Format | Extension | Support Level | Content Type |
|--------|-----------|---------------|--------------|
| HTML | `.html`, `.htm` | ✅ Full | Web pages |
| XML | `.xml` | ⚠️ Basic | Structured data |
| EPUB | `.epub` | ✅ Good | E-books |

**Features Supported:**
- Text content and structure
- Hyperlinks and anchors
- Basic styling information
- Embedded images
- Metadata extraction

### Image Formats (OCR)

#### Supported Image Types
| Format | Extension | OCR Support | Quality |
|--------|-----------|-------------|---------|
| PNG | `.png` | ✅ Excellent | High |
| JPEG | `.jpg`, `.jpeg` | ✅ Good | Medium-High |
| TIFF | `.tiff`, `.tif` | ✅ Excellent | High |
| BMP | `.bmp` | ⚠️ Basic | Medium |
| GIF | `.gif` | ⚠️ Limited | Low |

**OCR Requirements:**
- Minimum 150 DPI resolution
- Clear, high-contrast text
- Standard fonts preferred
- Language configuration required

### Plain Text Formats

#### Text Documents
| Format | Extension | Support Level | Encoding |
|--------|-----------|---------------|----------|
| Plain Text | `.txt` | ✅ Full | Auto-detect |
| Log Files | `.log` | ✅ Full | UTF-8, ASCII |
| Markdown | `.md` | ✅ Full | UTF-8 |
| JSON | `.json` | ⚠️ Structure | UTF-8 |
| YAML | `.yaml`, `.yml` | ⚠️ Structure | UTF-8 |

## Output Format Options

### Primary Output Format

#### Markdown (.md)
- **Best for**: Documentation, wikis, GitHub
- **Features**: 
  - Full formatting preservation
  - Table support
  - Code blocks
  - Links and references
  - Image embedding
- **Quality**: Excellent

### Alternative Output Formats

#### Plain Text (.txt)
- **Best for**: Simple content, legacy systems
- **Features**:
  - Clean text extraction
  - Minimal formatting
  - Universal compatibility
  - Small file size
- **Quality**: Good

#### HTML (.html)
- **Best for**: Web publishing, rich formatting
- **Features**:
  - Rich formatting support
  - Embedded styles
  - Image integration
  - Hyperlink preservation
- **Quality**: Excellent

#### JSON (.json)
- **Best for**: Data processing, API integration
- **Features**:
  - Structured data output
  - Metadata inclusion
  - Programmatic access
  - Schema validation
- **Quality**: Good (for data)

### Custom Output Templates

#### Template System
- **User-defined templates**: Create custom output formats
- **Variable substitution**: Dynamic content insertion
- **Conditional formatting**: Content-based formatting rules
- **Multi-format export**: Single source, multiple outputs

## Format-Specific Notes

### Microsoft Office Documents

#### DOCX Files
**Excellent Support:**
- Text formatting (bold, italic, fonts)
- Paragraph styles and headings
- Lists (numbered and bulleted)
- Tables with complex structures
- Images and diagrams
- Headers and footers

**Limited Support:**
- Complex layouts (text boxes, columns)
- Advanced formatting (WordArt, shapes)
- Embedded objects (Excel charts, etc.)
- Form fields and controls

#### Excel Files
**Well Supported:**
- Cell data and text
- Multiple worksheets
- Basic formulas (results only)
- Simple tables and ranges

**Not Supported:**
- Complex formulas (as formulas)
- Macros and VBA code
- Charts and graphs (content only)
- Pivot tables (data only)

### PDF Documents

#### Text-Based PDFs
**Advantages:**
- Fast processing
- High accuracy
- Preserves structure
- No additional setup

**Best Results With:**
- Standard fonts
- Simple layouts
- Clear text
- Minimal graphics overlay

#### Image-Based PDFs
**OCR Processing:**
- Requires OCR engine
- Slower processing
- Language-dependent accuracy
- May need manual review

**Optimization Tips:**
- Configure correct language
- Use high-quality source
- Review OCR results
- Consider manual corrections

### Web Formats

#### HTML Documents
**Supported Elements:**
- Text content and structure
- Headings and paragraphs
- Lists and tables
- Links and anchors
- Basic styling (converted to Markdown)

**Ignored Elements:**
- JavaScript and dynamic content
- Complex CSS layouts
- Form elements
- Embedded media (videos, audio)

#### EPUB E-books
**Extracted Content:**
- Chapter structure
- Text content
- Table of contents
- Basic formatting
- Metadata (title, author, etc.)

**Limitations:**
- DRM-protected files not supported
- Complex layouts simplified
- Interactive elements removed

## Conversion Quality Matrix

### Quality Ratings

| Input Format | Text Quality | Formatting | Tables | Images | Overall |
|--------------|--------------|------------|--------|--------|---------|
| DOCX | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| PDF (text) | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| PDF (image) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| PPTX | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| XLSX | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| HTML | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| ODT | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Image (OCR) | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### Factors Affecting Quality

#### Source Document Quality
- **Resolution**: Higher resolution = better OCR results
- **Font Clarity**: Standard fonts convert better
- **Layout Complexity**: Simple layouts preserve better
- **File Integrity**: Corrupted files produce poor results

#### Processing Settings
- **Quality vs Speed**: Higher quality takes more time
- **OCR Language**: Correct language improves accuracy
- **Memory Allocation**: More memory = better processing
- **Format Preservation**: More preservation = larger output

## Troubleshooting Format Issues

### Common Problems and Solutions

#### "Format Not Supported" Error
**Causes:**
- File extension not recognized
- Corrupted file header
- Unsupported file version

**Solutions:**
1. Check file extension matches content
2. Try opening file in original application
3. Convert to supported format first
4. Update MarkItDown GUI to latest version

#### Poor OCR Results
**Causes:**
- Low image resolution
- Wrong language setting
- Poor image quality
- Complex layout

**Solutions:**
1. Increase source image DPI (300+ recommended)
2. Configure correct OCR language
3. Enhance image contrast/brightness
4. Break complex documents into sections

#### Missing Content
**Causes:**
- Content in unsupported elements
- Hidden or protected content
- Complex formatting structures

**Solutions:**
1. Save source in simpler format
2. Remove document protection
3. Simplify formatting in source
4. Manual review and editing

#### Slow Processing
**Causes:**
- Large file size
- Complex formatting
- OCR requirements
- Limited system resources

**Solutions:**
1. Break large files into smaller pieces
2. Increase memory allocation
3. Close other applications
4. Use batch processing overnight

### Format-Specific Troubleshooting

#### PDF Issues
- **Password protected**: Remove protection or provide password
- **Scanned images**: Enable OCR processing
- **Complex layouts**: May need manual formatting adjustment
- **Embedded fonts**: Install fonts on system if possible

#### Office Document Issues
- **Compatibility mode**: Save in modern format (.docx vs .doc)
- **Embedded objects**: May appear as placeholders
- **Custom fonts**: Install fonts or accept substitutions
- **Track changes**: Accept or reject changes before conversion

#### Image Processing Issues
- **Multiple columns**: May need manual column detection
- **Mathematical formulas**: Consider specialized OCR tools
- **Handwritten text**: Very limited support
- **Mixed languages**: Configure multiple language support

---

**Related Documentation:**
- 📖 [User Manual](user-manual.md) - Complete usage guide
- 🆘 [Troubleshooting](troubleshooting.md) - Problem solving
- ⚙️ Configuration - Settings and optimization
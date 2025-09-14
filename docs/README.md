# MarkItDown GUI Documentation System

Complete Sphinx documentation system with automatic API generation for the MarkItDown GUI project.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

2. **Install documentation dependencies:**
```bash
pip install -r requirements-docs.txt
```

3. **Build documentation:**
```bash
make fullbuild
```

4. **Serve locally:**
```bash
make serve
# Visit http://localhost:8000
```

## 📁 Project Structure

```
docs/
├── conf.py                 # Sphinx configuration
├── index.rst               # Main documentation index
├── Makefile                # Build automation
├── make.bat                # Windows build script
├── requirements-docs.txt   # Documentation dependencies
├── setup_docs.py          # Automated setup script
├── _static/
│   └── custom.css         # Custom styling
├── _templates/
│   ├── module.rst         # Module template
│   └── class.rst          # Class template
├── api/
│   └── overview.rst       # API documentation overview
├── autoapi/
│   └── index.rst          # Auto-generated API docs
└── user-guide/
    ├── installation.rst   # Installation guide
    ├── quick-start.rst    # Quick start guide
    ├── features.rst       # Feature documentation
    ├── configuration.rst  # Configuration guide
    └── troubleshooting.rst # Troubleshooting guide
```

## 🔧 Build Commands

### Basic Commands
```bash
make html           # Build HTML documentation
make clean          # Clean build directory
make help           # Show all available commands
```

### Development Commands
```bash
make livehtml       # Live reload during development
make watch          # Watch for changes and rebuild
make apidoc         # Generate API documentation
make fullbuild      # Complete rebuild with API docs
```

### Quality Commands
```bash
make linkcheck      # Check external links
make coverage       # Check documentation coverage
make spellcheck     # Check spelling (requires sphinxcontrib-spelling)
```

### Deployment Commands
```bash
make github-pages   # Build for GitHub Pages
make pdf            # Build PDF documentation
```

## ✨ Features

### 🤖 Automatic API Documentation
- **Docstring Extraction**: Automatically generates documentation from Python docstrings
- **Cross-References**: Intelligent linking between modules, classes, and functions
- **Type Hints**: Displays type annotations and return types
- **Source Code Links**: Direct links to source code on each documented item

### 🎨 Professional Styling
- **ReadTheDocs Theme**: Modern, responsive documentation theme
- **Custom CSS**: Enhanced styling for better readability
- **Korean Font Support**: Proper Korean typography and font rendering
- **Mobile Responsive**: Optimized for all device sizes
- **Dark Mode Ready**: CSS prepared for dark mode themes

### 📝 Content Integration
- **Markdown Support**: Full MyST parser integration for Markdown files
- **Existing Docs**: Seamless integration with existing documentation
- **Rich Content**: Support for tables, code blocks, diagrams, and more
- **Navigation**: Intelligent table of contents and cross-references

### 🌍 Internationalization
- **Korean Language**: Primary language support with proper encoding
- **Multi-language**: Ready for additional language translations
- **RTL Support**: Right-to-left language support when needed

## 📚 Documentation Structure

### User Documentation
- **Installation Guide**: Complete setup and installation instructions
- **Quick Start**: Get started quickly with basic usage
- **Features**: Comprehensive feature documentation
- **Configuration**: Detailed configuration options
- **Troubleshooting**: Common issues and solutions

### Developer Documentation
- **API Reference**: Complete API documentation from source code
- **Architecture**: System architecture and design patterns
- **Coding Standards**: Development guidelines and best practices
- **Testing**: Testing strategies and implementation guides

### API Documentation
- **Core Modules**: Configuration, logging, i18n, accessibility
- **UI Components**: Main window, widgets, dialogs, and controls
- **Utilities**: Helper functions and utility modules
- **Auto-Generated**: Comprehensive API docs from docstrings

## 🔄 Continuous Integration

### GitHub Actions Ready
The documentation system is prepared for CI/CD integration:

```yaml
# Example GitHub Actions workflow
name: Documentation
on: [push, pull_request]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: pip install -r docs/requirements-docs.txt
      - run: cd docs && make fullbuild
      - uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/_build/html/
```

## 🎯 Quality Standards

### Documentation Coverage
- **Comprehensive**: All public APIs documented
- **Examples**: Code examples for major features
- **Testing**: Documentation tested for accuracy
- **Links**: All external links validated

### Code Quality
- **Type Hints**: Full type annotation support
- **Docstring Standards**: Google/NumPy style docstrings
- **Cross-References**: Intelligent linking system
- **Search**: Full-text search functionality

## 🛠️ Customization

### Theme Customization
The documentation uses a customized ReadTheDocs theme with:
- Enhanced code block styling
- Improved table formatting
- Korean font optimization
- Professional color scheme
- Mobile-responsive design

### Adding Content
1. **New Pages**: Add `.rst` or `.md` files and update `index.rst`
2. **API Docs**: Add docstrings to Python code - automatically included
3. **Cross-References**: Use Sphinx cross-reference syntax
4. **Custom Styling**: Modify `_static/custom.css`

### Configuration
Key configuration options in `conf.py`:
- `project`: Project name and metadata
- `extensions`: Sphinx extensions
- `html_theme_options`: Theme customization
- `autodoc_default_options`: API documentation options

## 📊 Analytics and Monitoring

### Build Metrics
- **Build Time**: Optimized for fast builds
- **File Coverage**: Track documentation completeness
- **Link Health**: Monitor external link status
- **Search Indexing**: Full-text search optimization

### Performance
- **Incremental Builds**: Only rebuild changed content
- **Caching**: Intelligent caching for faster builds
- **Parallel Processing**: Multi-threaded generation
- **Optimization**: Minified CSS and optimized images

## 🤝 Contributing

### Documentation Guidelines
1. **Write Clear**: Use clear, concise language
2. **Add Examples**: Include practical code examples
3. **Test Links**: Verify all external links work
4. **Update Index**: Add new pages to navigation

### Development Workflow
1. **Edit Content**: Modify `.rst` or `.md` files
2. **Local Testing**: Use `make livehtml` for live preview
3. **Build Check**: Run `make fullbuild` to verify
4. **Link Check**: Run `make linkcheck` before commit

## 📞 Support

For documentation system issues:
- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share ideas
- **Wiki**: Community-maintained documentation guides

---

**Built with ❤️ using Sphinx, ReadTheDocs Theme, and MyST Parser**
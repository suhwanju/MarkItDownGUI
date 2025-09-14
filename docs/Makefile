# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Custom targets for MarkItDown GUI documentation

# Install documentation dependencies
install-deps:
	pip install -r requirements-docs.txt

# Clean build directory
clean:
	rm -rf $(BUILDDIR)
	rm -rf autoapi/generated
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Build HTML documentation
html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

# Build HTML documentation with auto-reload (for development)
livehtml:
	sphinx-autobuild -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" --host 0.0.0.0 --port 8000

# Build PDF documentation
pdf: latexpdf
	@echo "Building PDF documentation..."

# Build documentation and check for warnings
htmlstrict:
	@echo "Building HTML documentation with strict warning checking..."
	@$(SPHINXBUILD) -W -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Build documentation and check links
linkcheck:
	@echo "Checking external links..."
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)

# Build documentation in multiple formats
all: clean html pdf
	@echo "Documentation built in multiple formats."

# Generate API documentation
apidoc:
	@echo "Generating API documentation..."
	sphinx-apidoc -f -o autoapi/generated ../markitdown_gui
	@echo "API documentation generated."

# Full rebuild including API documentation
fullbuild: clean apidoc html
	@echo "Full documentation build completed."

# Serve documentation locally
serve:
	@echo "Serving documentation at http://localhost:8000"
	cd $(BUILDDIR)/html && python -m http.server 8000

# Check documentation coverage
coverage:
	@echo "Checking documentation coverage..."
	@$(SPHINXBUILD) -b coverage "$(SOURCEDIR)" "$(BUILDDIR)/coverage" $(SPHINXOPTS) $(O)
	@echo "Coverage report generated in $(BUILDDIR)/coverage."

# Spell check documentation
spellcheck:
	@echo "Checking spelling..."
	@$(SPHINXBUILD) -b spelling "$(SOURCEDIR)" "$(BUILDDIR)/spelling" $(SPHINXOPTS) $(O)

# Build for GitHub Pages
github-pages: clean fullbuild
	@echo "Building for GitHub Pages..."
	touch $(BUILDDIR)/html/.nojekyll
	@echo "GitHub Pages build completed."

# Watch for changes and rebuild
watch:
	@echo "Watching for changes..."
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --ignore "*.swp" --ignore "*.pyc"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
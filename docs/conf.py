# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

# Add the project root to the Python path for autodoc
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'markitdown_gui'))

project = 'AIAgentDocument - MarkItDown GUI'
copyright = '2024, MarkItDown GUI Team'
author = 'MarkItDown GUI Team'
release = '0.1.0'
version = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',           # Automatic documentation from docstrings
    'sphinx.ext.autosummary',       # Generate autodoc summaries
    'sphinx.ext.viewcode',          # Add source code links
    'sphinx.ext.napoleon',          # Support for Google and NumPy style docstrings
    'sphinx.ext.intersphinx',       # Cross-reference other projects
    'sphinx.ext.todo',              # Support for todo items
    'sphinx.ext.coverage',          # Coverage checker
    'sphinx.ext.mathjax',           # Math support
    'sphinx.ext.ifconfig',          # Conditional content
    'sphinx.ext.githubpages',       # GitHub Pages support
    'sphinx.ext.linkcode',          # Link to source code
    'myst_parser',                  # Markdown support
    'sphinx_rtd_theme',             # ReadTheDocs theme
    'sphinx.ext.graphviz',          # Graphviz diagrams
]

# Add support for Markdown files
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Language settings
language = 'ko'  # Korean as primary language
locale_dirs = ['_locale/']
gettext_compact = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# The master toctree document
master_doc = 'index'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_logo = None
html_favicon = None

# -- Options for autodoc extension ------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
    'inherited-members': True,
}

# Automatically extract typehints
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
autodoc_typehints_format = 'short'

# Mock imports for PyQt6 and other dependencies that might not be available during doc build
autodoc_mock_imports = [
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'markitdown',
    'openai',
    'keyring',
]

# Include private members that start with underscore but not dunder methods
autodoc_class_signature = 'mixed'

# -- Options for autosummary extension --------------------------------------

autosummary_generate = True
autosummary_imported_members = False

# -- Options for Napoleon extension -----------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx extension --------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'PyQt6': ('https://www.riverbankcomputing.com/static/Docs/PyQt6/', None),
    'pytest': ('https://docs.pytest.org/en/stable/', None),
}

# -- Options for todo extension ---------------------------------------------

todo_include_todos = True

# -- Options for coverage extension -----------------------------------------

coverage_show_missing_items = True

# -- Options for MyST parser ------------------------------------------------

myst_enable_extensions = [
    "deflist",
    "tasklist",
    "fieldlist",
    "attrs_inline",
    "colon_fence",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
]

myst_heading_anchors = 3
myst_title_to_header = True

# -- Custom configuration ---------------------------------------------------

# Add custom roles and directives
def setup(app):
    app.add_css_file('custom.css')

# Suppress warnings for missing references to external modules
suppress_warnings = ['ref.any', 'ref.python']

# Enable cross-references
nitpicky = False
nitpick_ignore = [
    ('py:class', 'PyQt6.QtWidgets.QWidget'),
    ('py:class', 'PyQt6.QtCore.QObject'),
    ('py:class', 'PyQt6.QtGui.QFont'),
]
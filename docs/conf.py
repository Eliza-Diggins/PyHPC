# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PyHPC'
copyright = '2023, Eliza C. Diggins'
author = 'Eliza C. Diggins'
release = '2023'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.napoleon',
    "myst_parser",
    'sphinx.ext.mathjax',
    "sphinx_copybutton",
    "sphinxcontrib.blockdiag",
    "sphinxcontrib.mermaid"
    ]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Autosummary settings
# ------------------------------------------------------------------------------------------------------------ #
autosummary_generate = True

# Auto doc settings
# ------------------------------------------------------------------------------------------------------------ #
autodoc_docstring_signature = True
autodoc_typehints = "none"
# Blockdiag
# ------------------------------------------------------------------------------------------------------------ #
blockdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Stratego+Word Golf'
copyright = '2025, Eduardo Matos and Guillermo Myers'
author = 'Eduardo Matos and Guillermo Myers'

import os
import sys

# Add the other doc related files.
sys.path.insert(0, os.path.abspath('.'))

# The '..' navigates up one level from the docs directory to the project root.
sys.path.insert(0, os.path.abspath('..')) 

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
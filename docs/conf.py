# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# To build:
#
#   * Enter venv.
#   * pip install sphinx
#   * sphinx-build -M html docs docs/_build
#   * firefox docs/_build/html/index.html
#

project = 'pipcl'
copyright = '2026, Artifex'
author = 'Julian Smith'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.autosummary',
        'autodocsumm',
        
        # Understand Google-style doc-comments. See
        # https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
        #
        'sphinx.ext.napoleon',
        ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

import os
import sys
import subprocess

root = os.path.normpath(f'{__file__}/../..')

subprocess.run(f'pip install autodocsumm', shell=1, check=1)
subprocess.run(f'pip install {root}', shell=1, check=1)

autoclass_content = 'both'
maximum_signature_line_length = 40
default_role = 'any'

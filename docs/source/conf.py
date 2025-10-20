# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from unittest.mock import MagicMock

# Add the parent directory (containing tb_lint package) to the path
# The tb_lint directory itself IS the package, so we need to add its parent
project_root = os.path.abspath('../../..')  # Go up to /home/vbesyakov/project
sys.path.insert(0, project_root)

# The tb_lint directory IS the package, so we need to ensure Python
# imports it as a package, not the tb_lint.py script file
# We'll handle this by mocking problematic dependencies first

# Mock modules that have external dependencies or cause import issues
# This prevents Sphinx from failing when verible is not installed
class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()

# Mock external dependencies
MOCK_MODULES = []
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# Prevent verible linter from exiting during import by mocking shutil.which
# and subprocess calls
import shutil
import subprocess

original_which = shutil.which
original_run = subprocess.run

def mock_which(cmd, *args, **kwargs):
    """Mock shutil.which to prevent VeribleLinter from exiting"""
    if cmd == "verible-verilog-lint":
        return "/usr/bin/verible-verilog-lint"  # Return fake path
    return original_which(cmd, *args, **kwargs)

def mock_run(*args, **kwargs):
    """Mock subprocess.run to prevent actual execution"""
    class MockResult:
        returncode = 0
        stdout = ""
        stderr = ""
    return MockResult()

shutil.which = mock_which
subprocess.run = mock_run

# Also mock sys.exit to prevent linters from killing the documentation build
original_exit = sys.exit

def mock_exit(code=0):
    """Prevent sys.exit from actually exiting during import"""
    if code != 0:
        # Just raise an exception instead of exiting
        raise ImportError(f"Module tried to exit with code {code}")
    return original_exit(code)

sys.exit = mock_exit

project = 'tb_lint'
copyright = '2025, BTA Design Services'
author = 'BTA'
release = '3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # Core Sphinx library for html generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
    'sphinx.ext.viewcode',     # Add links to highlighted source code
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
]

# Generate autodoc stubs with summaries from code
autosummary_generate = True

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Don't skip __init__ methods
autodoc_mock_imports = []

# Continue on import errors
autodoc_warningiserror = False

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # ReadTheDocs theme
html_static_path = ['_static']

"""
tb_lint: A simple Python linting toolkit.
"""

__version__ = "3.0.1"
__author__  = "Victor Besyakov"
__license__ = "MIT"

# What `import tb_lint` will expose:
__all__ = [
    "core",
    "linters",
    "rules",
    "UnifiedLinter",
    "VerilogSyntax",
]

# Subpackages
from . import core
from . import linters
from . import rules

# Top-level modules
from .tb_lint import UnifiedLinter
from .verible_verilog_syntax import VerilogSyntax


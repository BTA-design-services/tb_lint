"""
NaturalDocs Linter Implementation

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Adapter for NaturalDocs documentation linting using Verible AST
"""

import os
import sys
import shutil
from typing import List, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_linter import BaseLinter
from core.linter_registry import register_linter
from rules.naturaldocs import (
    FileHeaderRule, CompanyFieldRule, AuthorFieldRule,
    IncludeGuardsRule, IncludeGuardFormatRule,
    PackageDocsRule, ClassDocsRule, FunctionDocsRule,
    TaskDocsRule, ConstraintDocsRule, TypedefDocsRule,
    VariableDocsRule, ParameterDocsRule
)

# Try to import verible_verilog_syntax
try:
    import verible_verilog_syntax
    VERIBLE_AVAILABLE = True
except ImportError:
    VERIBLE_AVAILABLE = False
    # Don't print warning here - will be handled during initialization


@dataclass
class ASTContext:
    """Context object containing AST and file data"""
    tree: any
    file_bytes: bytes


@register_linter
class NaturalDocsLinter(BaseLinter):
    """
    NaturalDocs documentation linter using Verible AST parser
    
    This linter checks SystemVerilog files for proper NaturalDocs
    documentation using Abstract Syntax Tree analysis for high accuracy.

    Notes:
        - Requires the ``verible-verilog-syntax`` binary and Python bindings to
          be available. The docstring documents this dependency so API consumers
          can plan deployments accordingly.
        - Configuration is read from the ``file_header`` section of the linter
          config when present, matching the examples in the new API reference.
    """
    
    @property
    def name(self) -> str:
        return "naturaldocs"
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.sv', '.svh']
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize NaturalDocs linter
        
        Args:
            config: Configuration dictionary
        """
        # Mark as unavailable if Python module is missing (before calling super().__init__)
        self.is_available = VERIBLE_AVAILABLE
        
        # Initialize base class (which calls _register_rules)
        super().__init__(config)
        
        # If not available, skip Verible binary check
        if not self.is_available:
            return
        
        # Find Verible binary
        self.verible_bin = self._find_verible_binary()
        if not self.verible_bin:
            self.is_available = False
            return
    
    def _find_verible_binary(self) -> Optional[str]:
        """Find verible-verilog-syntax binary using environment variables"""
        # First try PATH
        verible_bin = shutil.which("verible-verilog-syntax")
        if verible_bin:
            return verible_bin
        
        # Try VERIBLE_HOME environment variable
        verible_home = os.environ.get('VERIBLE_HOME')
        if verible_home:
            verible_bin = os.path.join(verible_home, 'bin', 'verible-verilog-syntax')
            if os.path.exists(verible_bin):
                return verible_bin
        
        return None
    
    def _register_rules(self):
        """Register all NaturalDocs rules"""
        # Skip if linter is not available
        if not self.is_available:
            return
            
        # Get file header config
        file_header_cfg = self.config.get('file_header', {})
        
        # File header rules
        self.add_rule(FileHeaderRule(file_header_cfg))
        self.add_rule(CompanyFieldRule(file_header_cfg))
        self.add_rule(AuthorFieldRule(file_header_cfg))
        
        # Include guard rules
        self.add_rule(IncludeGuardsRule())
        self.add_rule(IncludeGuardFormatRule())
        
        # Code element documentation rules
        self.add_rule(PackageDocsRule())
        self.add_rule(ClassDocsRule())
        self.add_rule(FunctionDocsRule())
        self.add_rule(TaskDocsRule())
        self.add_rule(ConstraintDocsRule())
        self.add_rule(TypedefDocsRule())
        self.add_rule(VariableDocsRule())
        self.add_rule(ParameterDocsRule())
    
    def prepare_context(self, file_path: str, file_content: str) -> Optional[ASTContext]:
        """
        Prepare AST context by parsing file with Verible
        
        Args:
            file_path: Path to file
            file_content: Content of file
        
        Returns:
            ASTContext with parsed AST tree, or None on failure
        """
        # Check if linter is available
        if not self.is_available:
            return None
        
        try:
            # Read file as bytes for offset calculations
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            # Parse with Verible
            parser = verible_verilog_syntax.VeribleVerilogSyntax(executable=self.verible_bin)
            tree_data = parser.parse_files([file_path], options={'gen_tree': True})
            
            if file_path not in tree_data:
                return None
            
            file_data = tree_data[file_path]
            
            if not hasattr(file_data, 'tree') or file_data.tree is None:
                return None
            
            return ASTContext(tree=file_data.tree, file_bytes=file_bytes)
            
        except Exception as e:
            # Don't print error - just return None and let the linter skip the file
            return None


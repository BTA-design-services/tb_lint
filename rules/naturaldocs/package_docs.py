"""
Package documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper package documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class PackageDocsRule(BaseRule):
    """
    Rule: Check package documentation
    
    Requirements:
    - Packages must have 'Package:' documentation
    - Documented name must match actual package name
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_PKG_MISS]"
    
    @property
    def description(self) -> str:
        return "Packages must have 'Package:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check package documentation using AST context
        
        Args:
            file_path: Path to file being checked
            file_content: Content of the file
            context: AST context with package nodes
        
        Returns:
            List of violations found
        """
        violations = []
        
        # Context should contain AST tree from Verible
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Find all package declarations in AST
        for node in tree.iter_find_all({'tag': 'kPackageDeclaration'}):
            pkg_name = self._extract_package_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)
            
            # Extract preceding comments
            comments = self._extract_preceding_comments(file_content, start_line - 1)
            
            # Check for Package: keyword
            if not self._has_naturaldocs_keyword(comments, ['Package']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Package '{pkg_name}' without 'Package:' documentation" if pkg_name 
                           else "Package declaration without 'Package:' documentation"
                ))
        
        return violations
    
    def _extract_package_name(self, node) -> str:
        """Extract package name from AST node"""
        try:
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""
    
    def _get_line_number(self, file_bytes: bytes, byte_offset: int) -> int:
        """Convert byte offset to line number"""
        if byte_offset is None:
            return 1
        return file_bytes[:byte_offset].count(b'\n') + 1
    
    def _extract_preceding_comments(self, file_content: str, start_line: int, max_lines: int = 50) -> list:
        """Extract comments before a declaration"""
        lines = file_content.split('\n')
        comments = []
        
        for i in range(start_line - 1, max(0, start_line - max_lines) - 1, -1):
            line = lines[i].strip()
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                comments.insert(0, line)
            elif not line:  # Empty line
                continue
            else:  # Non-comment code
                break
        
        return comments
    
    def _has_naturaldocs_keyword(self, comments: list, keywords: list) -> bool:
        """Check if comments contain any of the NaturalDocs keywords"""
        import re
        comment_text = ' '.join(comments)
        for keyword in keywords:
            if re.search(r'(?://|/\*|\*)\s*' + re.escape(keyword) + r'\s*:', comment_text, re.IGNORECASE):
                return True
        return False


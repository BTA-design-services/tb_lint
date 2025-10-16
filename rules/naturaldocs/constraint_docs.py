"""
Constraint documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper constraint documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class ConstraintDocsRule(BaseRule):
    """
    Rule: Check constraint documentation
    
    Requirements:
    - Constraints should have 'define:' or 'Variable:' documentation
    - Both formats are acceptable per codebase standards
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_CONST_MISS]"
    
    @property
    def description(self) -> str:
        return "Constraints should have 'define:' or 'Variable:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check constraint documentation using AST context
        """
        violations = []
        
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Find all constraint declarations
        for node in tree.iter_find_all({'tag': 'kConstraintDeclaration'}):
            constraint_name = self._extract_constraint_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)
            comments = self._extract_preceding_comments(file_content, start_line - 1)
            
            # Check for accepted keywords: 'define' or 'Variable'
            if not self._has_naturaldocs_keyword(comments, ['define', 'Variable']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Constraint '{constraint_name}' without 'define:' or 'Variable:' documentation"
                           if constraint_name else "Constraint without documentation"
                ))
        
        return violations
    
    def _extract_constraint_name(self, node) -> str:
        """Extract constraint name from AST node"""
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
            elif not line:
                continue
            else:
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


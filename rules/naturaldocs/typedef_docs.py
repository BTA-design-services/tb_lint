"""
Typedef documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper typedef documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class TypedefDocsRule(BaseRule):
    """
    Rule: Check typedef documentation
    
    Requirements:
    - Typedefs can be documented with 'Typedef:', 'Type:', or 'Variable:'
    - Documentation is optional for typedefs (this rule can be configured to WARNING)
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_TYPEDEF_MISS]"
    
    @property
    def description(self) -> str:
        return "Typedefs should have 'Typedef:', 'Type:', or 'Variable:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        # Typedefs are often optional to document
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check typedef documentation using AST context
        """
        violations = []
        
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Find all type declarations (typedefs)
        for node in tree.iter_find_all({'tag': 'kTypeDeclaration'}):
            typedef_name = self._extract_typedef_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)
            comments = self._extract_preceding_comments(file_content, start_line - 1)
            
            # Check for accepted keywords
            if not self._has_naturaldocs_keyword(comments, ['Typedef', 'Type', 'Variable']):
                # Only report if rule is enabled (typedefs are often optional)
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Typedef '{typedef_name}' without documentation"
                           if typedef_name else "Typedef without documentation"
                ))
        
        return violations
    
    def _extract_typedef_name(self, node) -> str:
        """Extract typedef name from AST node"""
        import re
        try:
            node_text = node.text.strip()
            # Match typedef name: word before semicolon, after any closing brace or keyword
            match = re.search(r'\}\s*(\w+)\s*;|typedef\s+\w+(?:\s*\[.*?\])?\s*(\w+)\s*;', node_text)
            if match:
                return match.group(1) if match.group(1) else match.group(2)
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


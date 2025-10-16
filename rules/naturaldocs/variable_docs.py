"""
Variable documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper variable documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class VariableDocsRule(BaseRule):
    """
    Rule: Check variable documentation
    
    Requirements:
    - Variables can be documented with 'Variable:' keyword
    - Documentation is optional for most variables
    - Only checks member variables (not local variables)
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_VAR_MISS]"
    
    @property
    def description(self) -> str:
        return "Variables can have 'Variable:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        # Variables are typically optional to document
        return RuleSeverity.INFO
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check variable documentation using AST context
        
        Only checks member variables, not local variables
        """
        violations = []
        
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Collect function/task body ranges to identify local variables
        function_task_ranges = []
        for node in tree.iter_find_all({'tag': ['kFunctionDeclaration', 'kTaskDeclaration', 
                                                 'kFunctionPrototype', 'kTaskPrototype',
                                                 'kClassConstructorPrototype']}):
            function_task_ranges.append((node.start, node.end))
        
        # Check data declarations (skip local variables)
        for node in tree.iter_find_all({'tag': 'kDataDeclaration'}):
            # Check if this is a local variable (inside function/task)
            is_local = any(node.start >= start and node.end <= end 
                          for start, end in function_task_ranges)
            
            if not is_local:
                # This is a member variable
                var_name = self._extract_variable_name(node)
                start_line = self._get_line_number(context.file_bytes, node.start)
                comments = self._extract_preceding_comments(file_content, start_line - 1)
                
                # Check for Variable: keyword (optional, so only INFO level)
                if not self._has_naturaldocs_keyword(comments, ['Variable']):
                    # Since variables are optional, we may not want to report this
                    # Uncomment below to enable reporting:
                    # violations.append(self.create_violation(
                    #     file_path=file_path,
                    #     line=start_line,
                    #     message=f"Variable '{var_name}' without 'Variable:' documentation"
                    #            if var_name else "Variable without documentation"
                    # ))
                    pass
        
        return violations
    
    def _extract_variable_name(self, node) -> str:
        """Extract variable name from AST node"""
        import re
        try:
            node_text = node.text.strip()
            # Match variable name: identifier before semicolon or equals
            match = re.search(r'\b(\w+)\s*(?:;|=)', node_text)
            if match:
                return match.group(1)
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


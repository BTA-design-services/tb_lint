"""
Parameter documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper parameter documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class ParameterDocsRule(BaseRule):
    """
    Rule: Check parameter documentation
    
    Requirements:
    - Parameters can be documented with 'Constant:' or 'Property:' keywords
    - Documentation is optional for parameters
    - Skip type parameters in class headers (documented in Parameters: section)
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_PARAM_MISS]"
    
    @property
    def description(self) -> str:
        return "Parameters can have 'Constant:' or 'Property:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        # Parameters are typically optional to document
        return RuleSeverity.INFO
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check parameter documentation using AST context
        """
        violations = []
        
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Find all parameter declarations
        for node in tree.iter_find_all({'tag': 'kParamDeclaration'}):
            param_name = self._extract_parameter_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)
            comments = self._extract_preceding_comments(file_content, start_line, context=context)
            
            # Skip type parameters in class headers (they have Class: keyword)
            if self._has_naturaldocs_keyword(comments, ['Class', 'Classes']):
                continue
            
            # Check for accepted keywords (optional)
            if not self._has_naturaldocs_keyword(comments, ['Constant', 'Property']):
                # Since parameters are optional, we may not want to report this
                # Uncomment below to enable reporting:
                # violations.append(self.create_violation(
                #     file_path=file_path,
                #     line=start_line,
                #     message=f"Parameter '{param_name}' without documentation"
                #            if param_name else "Parameter without documentation"
                # ))
                pass
        
        return violations
    
    def _extract_parameter_name(self, node) -> str:
        """Extract parameter name from AST node"""
        import re
        try:
            node_text = node.text.strip()
            # Match parameter name: identifier after type, before equals or semicolon
            match = re.search(r'\bparameter\b.*?\b(\w+)\s*(?:=|;)', node_text)
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
    
    


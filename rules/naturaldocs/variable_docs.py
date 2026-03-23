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
    - Member variables use a preceding block with the 'Variable:' keyword
    - Only checks member variables (not locals in function/task/initial/always)
    - Default severity is ERROR (overridable via NaturalDocs rule_severity map)
    """
    @property
    def rule_id(self) -> str:
        return "[ND_VAR_MISS]"
    
    @property
    def description(self) -> str:
        return "Variables can have 'Variable:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        # Aligns with naturaldocs.common.json "[ND_VAR_MISS]": "ERROR" when config omits override
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check variable documentation using AST context
        
        Only checks member variables, not local variables
        """
        violations = []
        
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Ranges where data declarations are procedural/locals (not class/interface members).
        local_scope_ranges = []
        for node in tree.iter_find_all({'tag': ['kFunctionDeclaration', 'kTaskDeclaration',
                                                 'kFunctionPrototype', 'kTaskPrototype',
                                                 'kClassConstructorPrototype',
                                                 # e.g. automatic variables in interface/module initial/always
                                                 'kInitialStatement', 'kAlwaysStatement']}):
            local_scope_ranges.append((node.start, node.end))
        
        # Check data declarations (skip local variables)
        for node in tree.iter_find_all({'tag': 'kDataDeclaration'}):
            # Local if inside function/task/initial/always (see local_scope_ranges)
            is_local = any(node.start >= start and node.end <= end 
                          for start, end in local_scope_ranges)
            
            if not is_local:
                # This is a member variable
                var_name = self._extract_variable_name(node)
                start_line = self._get_line_number(context.file_bytes, node.start)
                # Use nearest comment block only; accumulated historical comments
                # can hide invalid local keywords.
                comments = self._extract_comments_from_text(file_content, start_line)
                keyword_check = self._validate_naturaldocs_keyword(
                    comments,
                    ['Variable', 'Variables', 'Var', 'Vars', 'Field', 'Fields', 'Property', 'Properties', 'Constant', 'Constants'],
                    'variable'
                )
                if keyword_check:
                    violations.append(RuleViolation(
                        file=file_path,
                        line=start_line,
                        column=0,
                        severity=RuleSeverity.ERROR,
                        message=keyword_check['message'],
                        rule_id=keyword_check['rule_id']
                    ))
                
                # Check for Variable: keyword (mandatory)
                if not self._has_naturaldocs_keyword(comments, ['Variable']):
                    violations.append(self.create_violation(
                        file_path=file_path,
                        line=start_line,
                        message=f"Variable '{var_name}' without 'Variable:' documentation"
                               if var_name else "Variable without documentation"
                    ))
        
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
    
    


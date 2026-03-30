"""
Class documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper class documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class ClassDocsRule(BaseRule):
    """
    Rule: Check class documentation
    
    Requirements:
    - Classes must have 'Class:' documentation
    - Documented name must match actual class name
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_CLASS_MISS]"
    
    @property
    def description(self) -> str:
        return "Classes must have 'Class:' documentation"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check class documentation using AST context
        
        Args:
            file_path: Path to file being checked
            file_content: Content of the file
            context: AST context with class nodes
        
        Returns:
            List of violations found
        """
        violations = []
        
        # Context should contain AST tree from Verible
        if not context or not hasattr(context, 'tree'):
            return violations
        
        tree = context.tree
        
        # Find all class declarations in AST
        for node in tree.iter_find_all({'tag': 'kClassDeclaration'}):
            class_name = self._extract_class_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)
            
            # Use nearest comment block only.
            comments = self._extract_comments_from_text(file_content, start_line)
            keyword_check = self._validate_naturaldocs_keyword(comments, ['Class'], 'class')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=RuleSeverity.ERROR,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))
            
            # Check for Class: keyword
            if not self._has_naturaldocs_keyword(comments, ['Class']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Class '{class_name}' without 'Class:' documentation" if class_name
                           else "Class declaration without 'Class:' documentation"
                ))
                continue

            # Reuse centralised helper from BaseRule
            mismatch = self._check_name_mismatch(
                comments, ['Class'], class_name, 'class', file_path, start_line
            )
            if mismatch:
                violations.append(mismatch)
        
        return violations
    
    def _extract_class_name(self, node) -> str:
        """Extract class name from AST node"""
        try:
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""
    



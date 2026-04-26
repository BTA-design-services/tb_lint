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
    Requirements:
    - Constraints must have 'Constraint:' documentation
    - Documented name must match actual constraint name
    """
    @property
    def rule_id(self) -> str:
        return "[ND_CONST_MISS]"
    
    @property
    def description(self) -> str:
        return "Constraints must have 'Constraint:' documentation"
    
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
            # Use nearest comment block only to avoid accidental matches from earlier comments.
            comments = self._extract_comments_from_text(file_content, start_line)

            keyword_check = self._validate_naturaldocs_keyword(comments, ['constraint', 'constraints'], 'constraint')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=self.severity,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))
                continue

            if not self._has_naturaldocs_keyword(comments, ['constraint', 'constraints']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Constraint '{constraint_name}' without 'Constraint:' documentation"
                           if constraint_name else "Constraint without documentation"
                ))
                continue

            # Reuse centralised helper from BaseRule
            mismatch = self._check_name_mismatch(
                comments, ['constraint', 'constraints'],
                constraint_name, 'constraint', file_path, start_line,
            )
            if mismatch:
                violations.append(mismatch)

        return violations

    def _extract_constraint_name(self, node) -> str:
        """Extract constraint name from AST node"""
        try:
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""
    



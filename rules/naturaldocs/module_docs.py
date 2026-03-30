"""
Module documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper module documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class ModuleDocsRule(BaseRule):
    """
    Rule: Check module documentation

    Requirements:
    - Modules must have 'Module:' documentation
    - Documented name must match actual module name
    """

    @property
    def rule_id(self) -> str:
        return "[ND_MODULE_MISS]"

    @property
    def description(self) -> str:
        return "Modules must have 'Module:' documentation"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check module documentation using AST context."""
        violations = []

        if not context or not hasattr(context, 'tree'):
            return violations

        tree = context.tree

        for node in tree.iter_find_all({'tag': 'kModuleDeclaration'}):
            mod_name = self._extract_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)

            comments = self._extract_comments_from_text(file_content, start_line)
            keyword_check = self._validate_naturaldocs_keyword(comments, ['Module'], 'module')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=RuleSeverity.ERROR,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))

            if not self._has_naturaldocs_keyword(comments, ['Module']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Module '{mod_name}' without 'Module:' documentation" if mod_name
                           else "Module declaration without 'Module:' documentation"
                ))
                continue

            mismatch = self._check_name_mismatch(
                comments, ['Module'], mod_name, 'module', file_path, start_line
            )
            if mismatch:
                violations.append(mismatch)

        return violations

    def _extract_name(self, node) -> str:
        """Extract module name from AST node (first SymbolIdentifier)."""
        try:
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""

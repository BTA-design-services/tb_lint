"""
Interface documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper interface documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class InterfaceDocsRule(BaseRule):
    """
    Rule: Check interface documentation

    Requirements:
    - Interfaces must have 'Interface:' documentation
    - Documented name must match actual interface name
    """

    @property
    def rule_id(self) -> str:
        return "[ND_IFACE_MISS]"

    @property
    def description(self) -> str:
        return "Interfaces must have 'Interface:' documentation"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check interface documentation using AST context."""
        violations = []

        if not context or not hasattr(context, 'tree'):
            return violations

        tree = context.tree

        for node in tree.iter_find_all({'tag': 'kInterfaceDeclaration'}):
            iface_name = self._extract_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)

            comments = self._extract_comments_from_text(file_content, start_line)
            keyword_check = self._validate_naturaldocs_keyword(comments, ['Interface'], 'interface')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=RuleSeverity.ERROR,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))

            if not self._has_naturaldocs_keyword(comments, ['Interface']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Interface '{iface_name}' without 'Interface:' documentation" if iface_name
                           else "Interface declaration without 'Interface:' documentation"
                ))
                continue

            mismatch = self._check_name_mismatch(
                comments, ['Interface'], iface_name, 'interface', file_path, start_line
            )
            if mismatch:
                violations.append(mismatch)

        return violations

    def _extract_name(self, node) -> str:
        """Extract interface name from AST node (first SymbolIdentifier)."""
        try:
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""

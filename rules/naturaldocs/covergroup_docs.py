"""
Covergroup documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper covergroup documentation
"""

from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class CovergroupDocsRule(BaseRule):
    """
    Rule: Check covergroup documentation

    Requirements:
    - Covergroups must have 'Variable:' documentation (NaturalDocs has no
      native covergroup keyword; Variable is the chosen convention)
    - Documented name must match actual covergroup name
    """

    @property
    def rule_id(self) -> str:
        return "[ND_COVERGROUP_MISS]"

    @property
    def description(self) -> str:
        return "Covergroups must have 'Variable:' documentation"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check covergroup documentation using AST context."""
        violations = []

        if not context or not hasattr(context, 'tree'):
            return violations

        tree = context.tree

        for node in tree.iter_find_all({'tag': 'kCovergroupDeclaration'}):
            cg_name = self._extract_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)

            comments = self._extract_comments_from_text(file_content, start_line)
            # NaturalDocs has no native 'Covergroup' keyword; use Variable family
            cg_keywords = ['Variable', 'Variables', 'Var', 'Vars']
            keyword_check = self._validate_naturaldocs_keyword(comments, cg_keywords, 'covergroup')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=RuleSeverity.ERROR,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))

            if not self._has_naturaldocs_keyword(comments, cg_keywords):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Covergroup '{cg_name}' without 'Variable:' documentation" if cg_name
                           else "Covergroup declaration without 'Variable:' documentation"
                ))
                continue

            mismatch = self._check_name_mismatch(
                comments, cg_keywords, cg_name, 'covergroup', file_path, start_line
            )
            if mismatch:
                violations.append(mismatch)

        return violations

    def _extract_name(self, node) -> str:
        """Extract covergroup name from AST node (first SymbolIdentifier)."""
        try:
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""

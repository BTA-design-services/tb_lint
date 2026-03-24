"""
Constraint documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper constraint documentation
"""

import re
from typing import List, Optional

from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class ConstraintDocsRule(BaseRule):
    """
    Rule: Require NaturalDocs immediately before each constraint declaration.

    Emit [ND_CONST_MISS] (default ERROR; override via severity_levels) when a
    ``constraint`` block has no preceding comment block containing ``Define:``
    or ``Variable:`` (same line/discipline as other NaturalDocs rules).

    When the block includes ``Define: <name>``, ``<name>`` must match the SV
    constraint identifier; otherwise [ND_NAME_MISMATCH] is reported (was not
    checked before, so wrong labels like ``Define: b`` above ``constraint c`` passed).

    Enable/disable via naturaldocs ``linter_rules["[ND_CONST]"]`` (default on if omitted).
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
            # Use nearest comment block only to avoid accidental matches from earlier comments.
            comments = self._extract_comments_from_text(file_content, start_line)

            keyword_check = self._validate_naturaldocs_keyword(comments, ['define', 'Variable'], 'constraint')
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

            # Check for accepted keywords: 'define' or 'Variable'
            if not self._has_naturaldocs_keyword(comments, ['define', 'Variable']):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Constraint '{constraint_name}' without 'define:' or 'Variable:' documentation"
                           if constraint_name else "Constraint without documentation"
                ))
                continue

            # If Define: documents an identifier, it must match the constraint name.
            documented = self._extract_define_documented_name(comments)
            if (
                documented
                and constraint_name
                and documented != constraint_name
            ):
                violations.append(
                    RuleViolation(
                        file=file_path,
                        line=start_line,
                        column=0,
                        severity=self.severity,
                        rule_id="[ND_NAME_MISMATCH]",
                        message=(
                            f"Define: documents '{documented}' but constraint is named "
                            f"'{constraint_name}'"
                        ),
                    )
                )

        return violations

    def _extract_define_documented_name(self, comments: List[str]) -> Optional[str]:
        """First ``Define: <id>`` identifier in the preceding comment block, if any."""
        for line in comments:
            m = re.search(r"(?i)\bDefine\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if m:
                return m.group(1)
        return None

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
    
    


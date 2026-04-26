"""
Covergroup documentation rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper covergroup documentation
"""

from typing import List, Optional
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class CovergroupDocsRule(BaseRule):
    """
    Rule: Check covergroup documentation

    Requirements:
    - Covergroups must have 'covergroup:' documentation
    - Documented name must match actual covergroup name
    """

    @property
    def rule_id(self) -> str:
        return "[ND_COVERGROUP_MISS]"

    @property
    def description(self) -> str:
        return "Covergroups must have 'covergroup:' documentation"

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
            # Use 'covergroup' keyword for covergroups
            cg_keywords = ['covergroup', 'covergroups']
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
                    message=f"Covergroup '{cg_name}' without 'covergroup:' documentation" if cg_name
                           else "Covergroup declaration without 'covergroup:' documentation"
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


class CoverpointDocsRule(BaseRule):
    """
    Rule: Check coverpoint documentation
    """
    @property
    def rule_id(self) -> str:
        return "[ND_COVERPOINT_MISS]"

    @property
    def description(self) -> str:
        return "Coverpoints must have 'coverpoint:' documentation"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check coverpoint documentation using AST context."""
        violations = []

        if not context or not hasattr(context, 'tree'):
            return violations

        tree = context.tree

        for node in tree.iter_find_all({'tag': 'kCoverPoint'}):
            cp_name = self._extract_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)

            comments = self._extract_comments_from_text(file_content, start_line)
            cp_keywords = ['coverpoint', 'coverpoints']
            keyword_check = self._validate_naturaldocs_keyword(comments, cp_keywords, 'coverpoint')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=RuleSeverity.ERROR,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))

            if not self._has_naturaldocs_keyword(comments, cp_keywords):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Coverpoint '{cp_name}' without 'coverpoint:' documentation" if cp_name
                           else "Coverpoint without 'coverpoint:' documentation"
                ))
                continue

            if cp_name:
                # For coverpoints, if unnamed, the name is the expression.
                # We match the full documented string to be consistent with crosses.
                documented = self._extract_documented_full_string(comments, cp_keywords)
                
                # Normalize for comparison
                norm_doc = documented.replace(" ", "") if documented else ""
                norm_actual = cp_name.replace(" ", "")

                if norm_doc and norm_actual and norm_doc != norm_actual:
                    violations.append(RuleViolation(
                        file=file_path,
                        line=start_line,
                        column=0,
                        severity=self.severity,
                        rule_id="[ND_NAME_MISMATCH]",
                        message=f"Coverpoint docs name '{documented}' does not match coverpoint '{cp_name}'"
                    ))

        return violations

    def _extract_name(self, node) -> str:
        """Extract name or expression from AST node."""
        try:
            # Check for label (cp_name: coverpoint ...)
            # We collect all symbols. If labelled, first is name. If unlabelled, first is expression item.
            # For coverpoints, usually one identifier is enough.
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                return identifier.text
        except:
            pass
        return ""

    def _extract_documented_full_string(self, comments: list, keywords: list) -> Optional[str]:
        """Extract everything after the keyword colon."""
        import re
        for line in comments:
            for keyword in keywords:
                # Account for comment markers
                pattern = r'(?i)^\s*(?://|/\*|\*|)\s*' + re.escape(keyword) + r'\s*:\s*(.*?)\s*(?:\*/)?$'
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None


class CrossDocsRule(BaseRule):
    """
    Rule: Check cross documentation
    """
    @property
    def rule_id(self) -> str:
        return "[ND_CROSS_MISS]"

    @property
    def description(self) -> str:
        return "Crosses must have 'cross:' documentation"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check cross documentation using AST context."""
        violations = []

        if not context or not hasattr(context, 'tree'):
            return violations

        tree = context.tree

        for node in tree.iter_find_all({'tag': 'kCoverCross'}):
            cross_name = self._extract_name(node)
            start_line = self._get_line_number(context.file_bytes, node.start)

            comments = self._extract_comments_from_text(file_content, start_line)
            cross_keywords = ['cross', 'crosses']
            keyword_check = self._validate_naturaldocs_keyword(comments, cross_keywords, 'cross')
            if keyword_check:
                violations.append(RuleViolation(
                    file=file_path,
                    line=start_line,
                    column=0,
                    severity=RuleSeverity.ERROR,
                    message=keyword_check['message'],
                    rule_id=keyword_check['rule_id']
                ))

            if not self._has_naturaldocs_keyword(comments, cross_keywords):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=start_line,
                    message=f"Cross '{cross_name}' without 'cross:' documentation" if cross_name
                           else "Cross without 'cross:' documentation"
                ))
                continue

            if cross_name:
                # For crosses, we want to match the full documented string (e.g. "valid, ready")
                # because unnamed crosses use the item list as their documentation name.
                documented = self._extract_documented_full_string(comments, cross_keywords)
                # Normalize both for comparison (remove spaces after commas)
                norm_doc = documented.replace(" ", "") if documented else ""
                norm_actual = cross_name.replace(" ", "")

                if norm_doc and norm_actual and norm_doc != norm_actual:
                    violations.append(RuleViolation(
                        file=file_path,
                        line=start_line,
                        column=0,
                        severity=self.severity,
                        rule_id="[ND_NAME_MISMATCH]",
                        message=f"Cross docs name '{documented}' does not match cross '{cross_name}'"
                    ))

        return violations

    def _extract_name(self, node) -> str:
        """Extract name or item list from AST node."""
        try:
            # Check for label (cp_name: cross ...)
            # In Verible, a label is a child of the parent or sometimes inside.
            # If there's a SymbolIdentifier that is NOT an item, it's the name.
            # For simplicity, we'll collect all symbols.
            # If there are multiple, it's an unnamed cross (valid, ready).
            # If there's only one, and it's before 'cross', it's the name?
            # Actually, let's just collect all and join with ", ".
            symbols = []
            for identifier in node.iter_find_all({'tag': 'SymbolIdentifier'}):
                symbols.append(identifier.text)
            
            if symbols:
                return ", ".join(symbols)
        except:
            pass
        return ""

    def _extract_documented_full_string(self, comments: list, keywords: list) -> Optional[str]:
        """Extract everything after the keyword colon."""
        import re
        for line in comments:
            # Use the pre-existing cleaned comments if possible, but here we strip markers manually
            # to ensure we get the full content after the colon.
            for keyword in keywords:
                # Account for comment markers
                pattern = r'(?i)^\s*(?://|/\*|\*|)\s*' + re.escape(keyword) + r'\s*:\s*(.*?)\s*(?:\*/)?$'
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None

"""
Named end-block rule

Company: Copyright (c) 2025  BTA Design Services
         Licensed under the MIT License.

Description: Require optional SystemVerilog end labels (e.g. endmodule : foo).
"""

import re
from typing import List

from core.base_rule import BaseRule, RuleViolation, RuleSeverity

# End keywords that accept an optional trailing ": identifier" in IEEE 1800.
# Omitted: endgenerate, endspecify, endtable (no standard label), endif (preprocessor).
_END_SUFFIXES = (
    "module",
    "package",
    "interface",
    "class",
    "function",
    "task",
    "program",
    "property",
    "sequence",
    "group",
    "checker",
    "config",
    "primitive",
)

# Whole line is only an unnamed end (e.g. "endmodule" or "endmodule ;")
_UNNAMED_END_LINE_RE = re.compile(
    rf"^\s*end(?:{'|'.join(_END_SUFFIXES)})\b(?!\s*:)(?:\s*;)?\s*$",
    re.IGNORECASE,
)
# Same line as other code (e.g. "module m; endmodule")
_UNNAMED_END_ANYWHERE_RE = re.compile(
    rf"(?<![\w$])end(?:{'|'.join(_END_SUFFIXES)})\b(?!\s*:)\s*(?:;|$)",
    re.IGNORECASE,
)


def _code_without_slash_comment(line: str) -> str:
    """Strip // comments; naive (does not parse strings)."""
    if "//" not in line:
        return line
    return line.split("//", 1)[0].rstrip()


class NamedEndBlocksRule(BaseRule):
    """
    Rule: endmodule / endclass / … should repeat the block name (": name").

    Line-based check after removing // comments. Block comments on the same line
    as the end keyword are not handled.
    """

    @property
    def rule_id(self) -> str:
        return "[ND_END_NAMED_MISS]"

    @property
    def description(self) -> str:
        return "end* closing statements should include a : name label"

    def default_severity(self) -> RuleSeverity:
        # Matches naturaldocs.common.json when severity_levels omits an override
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        lines = file_content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            code = _code_without_slash_comment(line)
            if not code.strip():
                continue
            # One violation per line; first unnamed end* on the line.
            m_line = _UNNAMED_END_LINE_RE.match(code)
            m_any = None if m_line else _UNNAMED_END_ANYWHERE_RE.search(code)
            matched = m_line or m_any
            if not matched:
                continue
            inner = re.search(
                rf"(end(?:{'|'.join(_END_SUFFIXES)})\b)",
                matched.group(0),
                flags=re.IGNORECASE,
            )
            kw = inner.group(1) if inner else "end…"
            violations.append(
                self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"'{kw}' should be named (e.g. {kw} : <identifier>)",
                    context=line.strip(),
                )
            )

        return violations

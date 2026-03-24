"""
Naming convention rules (NaturalDocs linter family)

Company: Copyright (c) 2025  BTA Design Services
         Licensed under the MIT License.

Description:
  Enforces project naming conventions not covered by documentation-only rules:
  - class member variables must start with "m_" or "is_"
    (virtual interface handles may be "vif" or "*_vif")
  - typedef names must end with "_t"
  - user-defined port handles must end with "_port"
  - env/agent handle names must end with "_env"/"_agent" based on handle type
"""

from typing import List, Set, Tuple
import re

from core.base_rule import BaseRule, RuleViolation, RuleSeverity


def _line_from_offset(file_bytes: bytes, byte_offset: int) -> int:
    """Convert byte offset to 1-indexed line number."""
    if byte_offset is None:
        return 1
    return file_bytes[:byte_offset].count(b"\n") + 1


def _collect_ranges(tree, tags: List[str]) -> List[Tuple[int, int]]:
    """Collect [start, end] byte ranges for AST node tags."""
    ranges: List[Tuple[int, int]] = []
    for node in tree.iter_find_all({"tag": tags}):
        ranges.append((node.start, node.end))
    return ranges


def _in_any_range(node_start: int, node_end: int, ranges: List[Tuple[int, int]]) -> bool:
    """True when node byte range is fully inside one of ranges."""
    return any(node_start >= start and node_end <= end for start, end in ranges)


def _class_member_data_nodes(tree) -> List:
    """Return kDataDeclaration nodes that are class members (not locals)."""
    class_ranges = _collect_ranges(tree, ["kClassDeclaration"])
    local_ranges = _collect_ranges(
        tree,
        [
            "kFunctionDeclaration",
            "kTaskDeclaration",
            "kFunctionPrototype",
            "kTaskPrototype",
            "kClassConstructorPrototype",
            "kInitialStatement",
            "kAlwaysStatement",
        ],
    )
    members = []
    for node in tree.iter_find_all({"tag": "kDataDeclaration"}):
        if _in_any_range(node.start, node.end, class_ranges) and not _in_any_range(
            node.start, node.end, local_ranges
        ):
            members.append(node)
    return members


def _non_local_data_nodes(tree) -> List:
    """Return kDataDeclaration nodes that are not procedural/local declarations."""
    local_ranges = _collect_ranges(
        tree,
        [
            "kFunctionDeclaration",
            "kTaskDeclaration",
            "kFunctionPrototype",
            "kTaskPrototype",
            "kClassConstructorPrototype",
            "kInitialStatement",
            "kAlwaysStatement",
        ],
    )
    nodes = []
    for node in tree.iter_find_all({"tag": "kDataDeclaration"}):
        if not _in_any_range(node.start, node.end, local_ranges):
            nodes.append(node)
    return nodes


def _extract_type_identifiers(node) -> List[str]:
    """
    Extract type identifiers from a data declaration.

    kUnqualifiedId/kQualifiedId nodes generally represent declared type references.
    """
    type_ids: List[str] = []
    for type_node in node.iter_find_all({"tag": ["kQualifiedId", "kUnqualifiedId"]}):
        text = getattr(type_node, "text", "")
        if text:
            type_ids.append(text)
            # kUnqualifiedId can contain parameterized text like:
            # "uvm_analysis_port #(bta_transaction_c)". Extract identifier tokens
            # so SymbolIdentifier filtering can drop type symbols reliably.
            type_ids.extend(re.findall(r"\b[A-Za-z_]\w*\b", text))
    return type_ids


def _extract_declared_variable_names(node) -> List[str]:
    """
    Extract variable names from kDataDeclaration.

    In Verible AST, SymbolIdentifier list for data declarations usually contains:
    - one or more variable identifiers
    - plus a type identifier (for user-defined type declarations)

    We remove known type identifiers and keep declaration identifiers.
    """
    symbols = [sym.text for sym in node.iter_find_all({"tag": "SymbolIdentifier"}) if getattr(sym, "text", "")]
    if not symbols:
        return []

    type_ids = set(_extract_type_identifiers(node))
    vars_only = [name for name in symbols if name not in type_ids]

    # Fallback: if filtering removed everything, keep first symbol (best-effort).
    return vars_only if vars_only else [symbols[0]]


def _extract_virtual_interface_names(node) -> List[str]:
    """
    Extract handle names from a virtual interface declaration.

    For common AST shape, SymbolIdentifier list is:
      [<interface_type>, <var1>, <var2>, ...]
    """
    symbols = [sym.text for sym in node.iter_find_all({"tag": "SymbolIdentifier"}) if getattr(sym, "text", "")]
    if len(symbols) >= 2:
        return symbols[1:]
    return _extract_declared_variable_names(node)


class ClassMemberPrefixRule(BaseRule):
    """
    Rule: Class member variables must start with "m_" or "is_".

    Applies only to class properties (kDataDeclaration inside class declaration and
    outside function/task/procedural scopes).
    Special case for virtual interfaces:
      - "vif" is allowed
      - "*_vif" is allowed
    """

    @property
    def rule_id(self) -> str:
        return "[ND_MEMBER_PREFIX_MISS]"

    @property
    def description(self) -> str:
        return "Class member names use m_/is_ (virtual interfaces: vif/*_vif)"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        if not context or not hasattr(context, "tree"):
            return violations

        for node in _class_member_data_nodes(context.tree):
            line = _line_from_offset(context.file_bytes, node.start)
            is_virtual_if_decl = bool(re.search(r"\bvirtual\b", node.text))
            is_port_type_decl = self._is_port_type(_extract_type_identifiers(node))
            declared_names = (
                _extract_virtual_interface_names(node)
                if is_virtual_if_decl
                else _extract_declared_variable_names(node)
            )
            for name in declared_names:
                # Virtual interface handles can be generic "vif" or descriptive "*_vif".
                if is_virtual_if_decl:
                    if name == "vif" or name.endswith("_vif"):
                        continue
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line,
                            message=(
                                f"Virtual interface member '{name}' should be 'vif' "
                                f"or use '_vif' suffix"
                            ),
                            context=node.text.strip(),
                        )
                    )
                    continue

                # Port handles are covered by UserPortSuffixRule (must end with _port).
                # Do not force m_/is_ prefix on port handles.
                if is_port_type_decl and name.endswith("_port"):
                    continue

                if not (name.startswith("m_") or name.startswith("is_")):
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line,
                            message=f"Class member '{name}' should use 'm_' or 'is_' prefix",
                            context=node.text.strip(),
                        )
                    )
        return violations

    def _is_port_type(self, type_ids: List[str]) -> bool:
        """True if any declared type identifier ends with '_port'."""
        for type_id in type_ids:
            base = type_id.split("::")[-1]
            if base.endswith("_port"):
                return True
        return False


class TypedefSuffixRule(BaseRule):
    """Rule: typedef-defined user types must end with '_t'."""

    @property
    def rule_id(self) -> str:
        return "[ND_TYPE_SUFFIX_MISS]"

    @property
    def description(self) -> str:
        return "Typedef names must end with '_t'"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        if not context or not hasattr(context, "tree"):
            return violations

        for node in context.tree.iter_find_all({"tag": "kTypeDeclaration"}):
            line = _line_from_offset(context.file_bytes, node.start)
            typedef_name = self._extract_typedef_name(node)
            if typedef_name and not typedef_name.endswith("_t"):
                violations.append(
                    self.create_violation(
                        file_path=file_path,
                        line=line,
                        message=f"Typedef '{typedef_name}' should use '_t' suffix",
                        context=node.text.strip(),
                    )
                )
        return violations

    def _extract_typedef_name(self, node) -> str:
        """Best-effort typedef name extraction from AST symbols."""
        symbols = [sym.text for sym in node.iter_find_all({"tag": "SymbolIdentifier"}) if getattr(sym, "text", "")]
        return symbols[0] if symbols else ""


class EnvAgentInstanceSuffixRule(BaseRule):
    """
    Rule: env/agent handle instance names must end with '_env'/'_agent'.

    For declarations where declared type ends with _env or _agent, enforce the
    corresponding suffix on declared handle names.
    """

    @property
    def rule_id(self) -> str:
        return "[ND_ENV_AGENT_INSTANCE_SUFFIX_MISS]"

    @property
    def description(self) -> str:
        return "Type *_env/*_agent handles must use *_env/*_agent instance suffix"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        if not context or not hasattr(context, "tree"):
            return violations

        for node in _non_local_data_nodes(context.tree):
            line = _line_from_offset(context.file_bytes, node.start)
            type_ids = _extract_type_identifiers(node)
            required_suffix = self._required_suffix(type_ids)
            if not required_suffix:
                continue

            for name in _extract_declared_variable_names(node):
                if not name.endswith(required_suffix):
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line,
                            message=(
                                f"Instance '{name}' should end with '{required_suffix}' "
                                f"because its type is {required_suffix}"
                            ),
                            context=node.text.strip(),
                        )
                    )
        return violations

    def _required_suffix(self, type_ids: List[str]) -> str:
        """Return required handle suffix based on declared type."""
        for type_id in type_ids:
            base = type_id.split("::")[-1]
            if base.endswith("_env"):
                return "_env"
            if base.endswith("_agent"):
                return "_agent"
        return ""


class UserPortSuffixRule(BaseRule):
    """
    Rule: user-defined port handle names must end with "_port".

    For declarations where the type name ends with "_port" (for example
    uvm_analysis_port or custom foo_port), enforce "_port" suffix on declared
    handle names.
    """

    @property
    def rule_id(self) -> str:
        return "[ND_PORT_SUFFIX_MISS]"

    @property
    def description(self) -> str:
        return "Type *_port handles must use *_port instance suffix"

    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR

    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        if not context or not hasattr(context, "tree"):
            return violations

        for node in _non_local_data_nodes(context.tree):
            line = _line_from_offset(context.file_bytes, node.start)
            type_ids = _extract_type_identifiers(node)
            if not self._is_port_type(type_ids):
                continue

            for name in _extract_declared_variable_names(node):
                if not name.endswith("_port"):
                    violations.append(
                        self.create_violation(
                            file_path=file_path,
                            line=line,
                            message=(
                                f"Port handle '{name}' should end with '_port' "
                                f"because its type is *_port"
                            ),
                            context=node.text.strip(),
                        )
                    )
        return violations

    def _is_port_type(self, type_ids: List[str]) -> bool:
        """True if any declared type identifier ends with '_port'."""
        for type_id in type_ids:
            base = type_id.split("::")[-1]
            if base.endswith("_port"):
                return True
        return False

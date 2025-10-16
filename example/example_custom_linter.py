#!/usr/bin/env python3
"""
Example: Custom Linter Implementation

This file demonstrates how to create a custom linter for the modular framework.

Company: Copyright (c) 2025 BTA Design Services  
         Licensed under the MIT License.

Description:
    This example shows how to create a custom linter that can be integrated
    into the unified linting framework. This linter checks for simple patterns
    in SystemVerilog files.
"""

import sys
import os
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_linter import BaseLinter, LinterResult
from core.linter_registry import register_linter
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


# ============================================================================
# Example Rules for Custom Linter
# ============================================================================

class NoTrailingWhitespaceRule(BaseRule):
    """
    Example Rule: Check for trailing whitespace on lines
    
    This is a simple example that checks each line for trailing spaces or tabs.
    """
    
    @property
    def rule_id(self) -> str:
        return "[CUSTOM_TRAILING_WS]"
    
    @property
    def description(self) -> str:
        return "Checks for trailing whitespace on lines"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check for trailing whitespace"""
        violations = []
        lines = file_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Check if line ends with whitespace (excluding newline)
            if line and line[-1] in [' ', '\t']:
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"Line has trailing whitespace",
                    context=f"{line[:50]}..." if len(line) > 50 else line
                ))
        
        return violations


class MaxLineLengthRule(BaseRule):
    """
    Example Rule: Check for lines exceeding maximum length
    
    This rule is configurable - the max length can be set in the config file.
    
    Configuration example:
        {
            "rules": {
                "[CUSTOM_LINE_LENGTH]": {
                    "enabled": true,
                    "severity": "WARNING",
                    "max_length": 120
                }
            }
        }
    """
    
    @property
    def rule_id(self) -> str:
        return "[CUSTOM_LINE_LENGTH]"
    
    @property
    def description(self) -> str:
        return "Checks for lines exceeding maximum length"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check line lengths"""
        violations = []
        
        # Get max length from config (default: 120)
        max_length = self.config.get('max_length', 120)
        
        lines = file_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            if len(line) > max_length:
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"Line exceeds {max_length} characters (current: {len(line)})",
                    context=f"{line[:50]}..."
                ))
        
        return violations


class NoTabsRule(BaseRule):
    """
    Example Rule: Check for tab characters (prefer spaces)
    
    Many coding standards prefer spaces over tabs for indentation.
    """
    
    @property
    def rule_id(self) -> str:
        return "[CUSTOM_NO_TABS]"
    
    @property
    def description(self) -> str:
        return "Checks for tab characters (prefer spaces)"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.INFO
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check for tab characters"""
        violations = []
        lines = file_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            if '\t' in line:
                tab_count = line.count('\t')
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"Line contains {tab_count} tab character(s), use spaces instead",
                    context=line.strip()[:50]
                ))
        
        return violations


# ============================================================================
# Custom Linter Implementation
# ============================================================================

@register_linter
class StyleCheckLinter(BaseLinter):
    """
    Example Custom Linter: Style Checking Linter
    
    This linter performs simple style checks on SystemVerilog files:
    - Trailing whitespace
    - Line length
    - Tab characters
    
    To use this linter:
    1. This file is already in the example/ directory
    2. To activate it, import it in unified_linter.py:
       from example.example_custom_linter import StyleCheckLinter
    3. Create a config file: configs/stylecheck.json
    4. Add to lint_config_hierarchical.json:
       "stylecheck": {
           "enabled": true,
           "config_file": "configs/stylecheck.json"
       }
    """
    
    @property
    def name(self) -> str:
        """Unique name for this linter"""
        return "stylecheck"
    
    @property
    def supported_extensions(self) -> List[str]:
        """File extensions this linter can process"""
        return ['.sv', '.svh', '.v', '.vh']
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the style check linter
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # You can initialize any linter-specific settings here
        self.max_line_length = self.config.get('max_line_length', 120)
        
        if self.verbose:
            print(f"StyleCheckLinter initialized with max line length: {self.max_line_length}")
    
    def prepare_context(self, file_path: str, file_content: str) -> any:
        """
        Prepare context for rule checking
        
        For this simple linter, we don't need special context.
        More complex linters might parse the file here and return an AST.
        
        Args:
            file_path: Path to the file
            file_content: Content of the file
        
        Returns:
            Context object (None for this simple linter)
        """
        # For a simple linter, no special context is needed
        # The rules will work directly with the file content
        return None
    
    def _register_rules(self):
        """
        Register all rules for this linter
        
        This is where you add all the rules that this linter will run.
        Each rule is instantiated with its configuration.
        """
        # Get rule-specific configurations from the linter config
        rules_config = self.config.get('rules', {})
        
        # Register the trailing whitespace rule
        trailing_ws_config = rules_config.get('[CUSTOM_TRAILING_WS]', {})
        self.add_rule(NoTrailingWhitespaceRule(trailing_ws_config))
        
        # Register the line length rule (with max_length from config)
        line_length_config = rules_config.get('[CUSTOM_LINE_LENGTH]', {})
        # Pass max_length from linter config if not in rule config
        if 'max_length' not in line_length_config and 'max_line_length' in self.config:
            line_length_config['max_length'] = self.config['max_line_length']
        self.add_rule(MaxLineLengthRule(line_length_config))
        
        # Register the no tabs rule
        no_tabs_config = rules_config.get('[CUSTOM_NO_TABS]', {})
        self.add_rule(NoTabsRule(no_tabs_config))


# ============================================================================
# Example Usage / Testing
# ============================================================================

if __name__ == '__main__':
    """
    This allows testing the linter directly:
    
    python3 example/example_custom_linter.py test_file.sv
    """
    
    if len(sys.argv) < 2:
        print("Usage: python3 example_custom_linter.py <file.sv>")
        print("\nExample:")
        print("  python3 example/example_custom_linter.py test/good_example.sv")
        sys.exit(1)
    
    test_file = sys.argv[1]
    
    if not os.path.exists(test_file):
        print(f"ERROR: File '{test_file}' not found")
        sys.exit(1)
    
    print("="*80)
    print("Testing StyleCheckLinter")
    print("="*80)
    
    # Create linter with example config
    config = {
        'max_line_length': 100,
        'rules': {
            '[CUSTOM_TRAILING_WS]': {'enabled': True, 'severity': 'WARNING'},
            '[CUSTOM_LINE_LENGTH]': {'enabled': True, 'severity': 'WARNING'},
            '[CUSTOM_NO_TABS]': {'enabled': True, 'severity': 'INFO'}
        }
    }
    
    linter = StyleCheckLinter(config)
    
    # Run linter
    result = linter.lint_files([test_file])
    
    # Print results
    print(f"\nFiles checked: {result.files_checked}")
    print(f"Violations found: {len(result.violations)}")
    print(f"  - Errors: {result.error_count}")
    print(f"  - Warnings: {result.warning_count}")
    print(f"  - Info: {result.info_count}")
    
    if result.violations:
        print(f"\nViolations:")
        for v in result.violations:
            print(f"  Line {v.line}: {v.rule_id} [{v.severity.value}] {v.message}")
    
    print("\n" + "="*80)
    print("To integrate this linter into the framework:")
    print("="*80)
    print("1. Import in unified_linter.py:")
    print("   from example.example_custom_linter import StyleCheckLinter")
    print("")
    print("2. Create config file: configs/stylecheck.json")
    print("   {")
    print('     "max_line_length": 120,')
    print('     "rules": {')
    print('       "[CUSTOM_TRAILING_WS]": {"enabled": true, "severity": "WARNING"},')
    print('       "[CUSTOM_LINE_LENGTH]": {"enabled": true, "severity": "WARNING"},')
    print('       "[CUSTOM_NO_TABS]": {"enabled": true, "severity": "INFO"}')
    print("     }")
    print("   }")
    print("")
    print("3. Add to lint_config_hierarchical.json:")
    print("   {")
    print('     "linters": {')
    print('       "stylecheck": {')
    print('         "enabled": true,')
    print('         "config_file": "configs/stylecheck.json"')
    print("       }")
    print("     }")
    print("   }")
    print("")
    print("4. Run: python3 unified_linter.py --linter stylecheck -f files.txt")
    print("="*80)


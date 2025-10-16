#!/usr/bin/env python3
"""
Example: Custom Rule Implementation

This file demonstrates how to create a custom linting rule
for the modular framework.

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

"""

import re
from typing import List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class TodoCommentRule(BaseRule):
    """
    Example Rule: Detect TODO comments in code
    
    This rule finds all TODO comments and reports them as INFO level violations.
    It's a simple example showing how to create a custom rule.
    
    To use this rule:
    1. Copy this class to rules/naturaldocs/todo_comments.py
    2. Add to rules/naturaldocs/__init__.py
    3. Register in linters/naturaldocs_linter.py
    4. Add to lint_config_modular.json
    """
    
    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule"""
        return "[ND_TODO_FOUND]"
    
    @property
    def description(self) -> str:
        """Human-readable description"""
        return "Detects TODO comments that may need resolution"
    
    def default_severity(self) -> RuleSeverity:
        """Default severity (can be overridden in config)"""
        return RuleSeverity.INFO
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check for TODO comments in file
        
        Args:
            file_path: Path to file being checked
            file_content: Content of the file as string
            context: Additional context (not used in this simple rule)
        
        Returns:
            List of RuleViolation objects
        """
        violations = []
        lines = file_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Check for TODO in comments (both // and /* */ style)
            if re.search(r'(?://|/\*).*TODO', line, re.IGNORECASE):
                # Extract the TODO text
                todo_match = re.search(r'TODO[:\s]+(.*?)(?:\*\/|$)', line, re.IGNORECASE)
                todo_text = todo_match.group(1).strip() if todo_match else "TODO found"
                
                # Create violation
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"TODO comment: {todo_text}",
                    context=line.strip()
                ))
        
        return violations


class FixmeCommentRule(BaseRule):
    """
    Example Rule: Detect FIXME comments (more severe than TODO)
    
    FIXME comments indicate bugs or issues that need immediate attention.
    This rule treats them as WARNING level.
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_FIXME_FOUND]"
    
    @property
    def description(self) -> str:
        return "Detects FIXME comments indicating bugs or issues"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check for FIXME comments"""
        violations = []
        lines = file_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            if re.search(r'(?://|/\*).*FIXME', line, re.IGNORECASE):
                fixme_match = re.search(r'FIXME[:\s]+(.*?)(?:\*\/|$)', line, re.IGNORECASE)
                fixme_text = fixme_match.group(1).strip() if fixme_match else "FIXME found"
                
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"FIXME comment requiring attention: {fixme_text}",
                    context=line.strip()
                ))
        
        return violations


class LineLengthRule(BaseRule):
    """
    Example Rule: Check line length
    
    Configurable line length checking. The max length can be set in configuration.
    
    Configuration example:
        {
            "max_length": 100
        }
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_LINE_LENGTH]"
    
    @property
    def description(self) -> str:
        return "Checks for lines exceeding maximum length"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check line lengths"""
        violations = []
        
        # Get max length from config (default: 100)
        max_length = self.config.get('max_length', 100)
        
        lines = file_content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Check line length (excluding newline)
            if len(line) > max_length:
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message=f"Line exceeds {max_length} characters ({len(line)} chars)",
                    context=f"{line[:50]}..." if len(line) > 50 else line
                ))
        
        return violations


# Example: Test the rules directly
if __name__ == '__main__':
    """
    This allows testing the rule directly:
    
    python3 example_custom_rule.py test_file.sv
    """
    
    if len(sys.argv) < 2:
        print("Usage: python3 example_custom_rule.py <file.sv>")
        sys.exit(1)
    
    test_file = sys.argv[1]
    
    if not os.path.exists(test_file):
        print(f"ERROR: File '{test_file}' not found")
        sys.exit(1)
    
    # Read file
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Test TODO rule
    print("=" * 80)
    print("Testing TodoCommentRule")
    print("=" * 80)
    todo_rule = TodoCommentRule()
    todo_violations = todo_rule.check(test_file, content, None)
    print(f"Found {len(todo_violations)} TODO comments:\n")
    for v in todo_violations:
        print(f"  Line {v.line}: {v.message}")
    
    # Test FIXME rule
    print("\n" + "=" * 80)
    print("Testing FixmeCommentRule")
    print("=" * 80)
    fixme_rule = FixmeCommentRule()
    fixme_violations = fixme_rule.check(test_file, content, None)
    print(f"Found {len(fixme_violations)} FIXME comments:\n")
    for v in fixme_violations:
        print(f"  Line {v.line}: {v.message}")
    
    # Test line length rule
    print("\n" + "=" * 80)
    print("Testing LineLengthRule (max=100)")
    print("=" * 80)
    length_rule = LineLengthRule({'max_length': 100})
    length_violations = length_rule.check(test_file, content, None)
    print(f"Found {len(length_violations)} lines exceeding 100 characters:\n")
    for v in length_violations:
        print(f"  Line {v.line}: {v.message}")
    
    print("\n" + "=" * 80)
    print(f"Total violations: {len(todo_violations) + len(fixme_violations) + len(length_violations)}")
    print("=" * 80)


"""
Include guards rule

Company: Copyright (c) 2025  BTA Design Services  
         Licensed under the MIT License.

Description: Checks for proper include guards
"""

import re
import os
from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class IncludeGuardsRule(BaseRule):
    """
    Rule: Check for proper include guards
    
    Requirements:
    - Format: `ifndef FILENAME_SV
    - Format: `define FILENAME_SV
    - Format: `endif // FILENAME_SV (or any comment)
    - Package files: Include guards are optional
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_GUARD_MISS]"
    
    @property
    def description(self) -> str:
        return "Include guards must follow proper format"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check for proper include guards
        
        Args:
            file_path: Path to file being checked
            file_content: Content of the file
            context: Not used for this rule
        
        Returns:
            List of violations found
        """
        violations = []
        
        # Check if file contains a package declaration
        # Package files don't require include guards
        if re.search(r'^\s*package\s+\w+', file_content, re.MULTILINE):
            return violations  # No violations for package files
        
        filename = os.path.basename(file_path)
        guard_name = filename.replace('.', '_').upper()
        
        lines = file_content.split('\n')
        
        # Check first 20 lines for ifndef/define
        header = '\n'.join(lines[:20])
        
        if not re.search(r'`ifndef\s+' + guard_name, header):
            violations.append(self.create_violation(
                file_path=file_path,
                line=1,
                message=f"Missing or incorrect include guard (`ifndef {guard_name})"
            ))
        elif not re.search(r'`define\s+' + guard_name, header):
            violations.append(self.create_violation(
                file_path=file_path,
                line=1,
                message=f"Missing `define {guard_name} in include guard"
            ))
        
        # Check last 5 lines for endif with comment
        footer = '\n'.join(lines[-5:])
        if not re.search(r'`endif', footer):
            violations.append(self.create_violation(
                file_path=file_path,
                line=len(lines),
                message=f"Missing `endif for include guard"
            ))
        
        return violations


class IncludeGuardFormatRule(BaseRule):
    """
    Rule: Check include guard format details
    
    Separate rule for format warnings (not as severe as missing guards)
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_GUARD_FMT]"
    
    @property
    def description(self) -> str:
        return "Include guard `endif should have a comment"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check include guard format"""
        violations = []
        
        # Skip package files
        if re.search(r'^\s*package\s+\w+', file_content, re.MULTILINE):
            return violations
        
        lines = file_content.split('\n')
        footer = '\n'.join(lines[-5:])
        
        # Check if endif has a comment
        if re.search(r'`endif', footer) and not re.search(r'`endif\s*//.*', footer):
            violations.append(self.create_violation(
                file_path=file_path,
                line=len(lines),
                message="`endif should have a comment"
            ))
        
        return violations


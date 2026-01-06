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
    
    def _find_first_verilog_statement(self, lines: List[str]) -> int:
        """
        Find the line number (1-indexed) of the first Verilog statement.
        
        Skips:
        - Blank lines
        - Comment lines (// or /* */)
        - Preprocessor directives (lines starting with `)
        
        Args:
            lines: List of file lines
        
        Returns:
            Line number (1-indexed) of first Verilog statement, or len(lines)+1 if not found
        """
        in_multiline_comment = False
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Skip blank lines
            if not stripped:
                continue
            
            # Handle multi-line comments
            if in_multiline_comment:
                if '*/' in stripped:
                    # Find where comment ends on this line
                    comment_end = stripped.find('*/')
                    remaining = stripped[comment_end + 2:].strip()
                    if remaining:
                        # There's content after the comment ends, check it
                        stripped = remaining
                        in_multiline_comment = False
                    else:
                        # Comment ends on this line, reset flag and skip this line
                        in_multiline_comment = False
                        continue
                else:
                    # Still in comment, skip this line
                    continue
            
            # Check for multi-line comment start
            if '/*' in stripped:
                comment_start = stripped.find('/*')
                # Check if comment ends on same line
                if '*/' in stripped[comment_start:]:
                    # Single-line multi-line comment, skip
                    continue
                else:
                    # Multi-line comment starts, skip rest of line
                    in_multiline_comment = True
                    continue
            
            # Skip single-line comments
            if stripped.startswith('//'):
                continue
            
            # Skip preprocessor directives (include guards, includes, etc.)
            if stripped.startswith('`'):
                continue
            
            # This is the first Verilog statement
            return i
        
        # No Verilog statement found
        return len(lines) + 1
    
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
        
        # Find the first Verilog statement (not comment, not preprocessor)
        first_stmt_line = self._find_first_verilog_statement(lines)
        
        # Get all content before the first Verilog statement
        # This should contain the include guard
        header_lines = lines[:first_stmt_line - 1] if first_stmt_line > 1 else []
        header = '\n'.join(header_lines)
        
        # Check for ifndef before first statement
        ifndef_match = re.search(r'`ifndef\s+' + re.escape(guard_name), header)
        if not ifndef_match:
            violations.append(self.create_violation(
                file_path=file_path,
                line=1,
                message=f"Missing or incorrect include guard (`ifndef {guard_name}) - must appear before first Verilog statement"
            ))
        else:
            # Check for define after ifndef
            ifndef_pos = ifndef_match.start()
            content_after_ifndef = header[ifndef_pos:]
            if not re.search(r'`define\s+' + re.escape(guard_name), content_after_ifndef):
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


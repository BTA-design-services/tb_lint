"""
Verible Linter Implementation

Company: Copyright (c) 2025  BTA Design Services
         Licensed under the MIT License.

Description: Adapter for Verible style and syntax linting
"""

import os
import sys
import shutil
import subprocess
import re
from typing import List, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_linter import BaseLinter, LinterResult
from core.base_rule import RuleViolation, RuleSeverity
from core.linter_registry import register_linter


@register_linter
class VeribleLinter(BaseLinter):
    """
    Verible syntax and style linter

    This linter wraps the verible-verilog-lint tool and converts
    its output into the unified format.
    """

    @property
    def name(self) -> str:
        return "verible"

    @property
    def supported_extensions(self) -> List[str]:
        return ['.sv', '.svh', '.v', '.vh']

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize Verible linter

        Args:
            config: Configuration dictionary
        """
        # Initialize base class first
        super().__init__(config)

        # Find Verible binary
        self.verible_bin = self._find_verible_binary()

        # Get config file path
        self.config_file = self._find_config_file()

    def check_availability(self) -> tuple[bool, str]:
        """
        Check if Verible is available

        Returns:
            Tuple of (is_available, error_message)
        """
        if self.verible_bin:
            return True, ""

        msg = "ERROR: verible-verilog-lint not found.\n"
        verible_env = os.environ.get('VERIBLE_EXECUTABLE')
        verible_home = os.environ.get('VERIBLE_HOME')
        
        if verible_env:
            msg += f"  VERIBLE_EXECUTABLE was set to: '{verible_env}'\n"
            if not os.path.exists(verible_env):
                msg += "  But this file does not exist.\n"
        elif verible_home:
            msg += f"  VERIBLE_HOME was set to: '{verible_home}'\n"
            msg += "  Searched for 'verible-verilog-lint' in:\n"
            msg += f"    - {os.path.join(verible_home, 'bin')}\n"
            msg += f"    - {verible_home}\n"
        else:
            msg += "  Searched in PATH and VERIBLE_HOME.\n"
        msg += "  Please set 'tb_lint.veriblePath' in VS Code settings or ensure it is in your PATH."
        
        return False, msg



    def _find_verible_binary(self) -> Optional[str]:
        """Find verible-verilog-lint binary using environment variables"""
        # Try explicit path from env first
        verible_exec = os.environ.get('VERIBLE_EXECUTABLE')
        if verible_exec and os.path.exists(verible_exec):
            return verible_exec

        # First try PATH
        verible_bin = shutil.which("verible-verilog-lint")
        if verible_bin:
            return verible_bin

        # Try VERIBLE_HOME environment variable
        verible_home = os.environ.get('VERIBLE_HOME')
        if verible_home:
            # Try bin subdirectory first (Unix-style installation)
            for bin_name in ['verible-verilog-lint', 'verible-verilog-lint.exe']:
                verible_bin = os.path.join(verible_home, 'bin', bin_name)
                if os.path.exists(verible_bin):
                    return verible_bin

            # Try root directory (some Windows installations)
            for bin_name in ['verible-verilog-lint', 'verible-verilog-lint.exe']:
                verible_bin = os.path.join(verible_home, bin_name)
                if os.path.exists(verible_bin):
                    return verible_bin

        return None

    def _find_config_file(self) -> Optional[str]:
        """Find Verible rules config file"""
        # Check if config specifies a rules file
        if 'rules_file' in self.config:
            rules_file = self.config['rules_file']
            if os.path.exists(rules_file):
                return rules_file

        # Look for default config in script directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_config = os.path.join(script_dir, '.rules.verible_lint')

        if os.path.exists(default_config):
            return default_config

        return None

    def _register_rules(self):
        """
        Register Verible rules

        Note: Verible is an external tool, so rules are not registered
        individually in our framework. This method is required by the
        base class but doesn't do anything for Verible.
        """
        pass

    def prepare_context(self, file_path: str, file_content: str) -> Optional[any]:
        """
        Prepare context for Verible

        For Verible, we don't need to prepare any context since it's
        an external tool. We just return a dummy context.

        Returns:
            Empty dict (Verible doesn't need context preparation)
        """
        return {}

    def lint_file(self, file_path: str) -> LinterResult:
        """
        Lint a single file using Verible

        Override the base method to call verible-verilog-lint directly

        Args:
            file_path: Path to file to lint

        Returns:
            LinterResult containing violations found
        """
        result = LinterResult(linter_name=self.name)

        if not os.path.exists(file_path):
            result.add_error(file_path, "File not found")
            return result

        # Build command
        cmd = [self.verible_bin]

        # Add config file if available
        if self.config_file:
            cmd.append(f"--rules_config={self.config_file}")

        # Add file
        cmd.append(file_path)

        try:
            # Run Verible
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Parse output
            violations = self._parse_verible_output(proc.stdout, file_path)
            for violation in violations:
                result.add_violation(violation)

            result.files_checked = 1

        except Exception as e:
            result.add_error(file_path, f"Failed to run Verible: {str(e)}")

        return result

    def _parse_verible_output(self, output: str, file_path: str) -> List[RuleViolation]:
        """
        Parse Verible output into RuleViolation objects

        Verible output format:
        path/to/file.sv:line:col-range: message [Style: category] [rule-name]

        Args:
            output: Verible stdout
            file_path: Path to file being checked

        Returns:
            List of RuleViolation objects
        """
        violations = []

        # Get configuration - matches NaturalDocs structure
        linter_rules = self.config.get('linter_rules', {})
        severity_levels = self.config.get('severity_levels', {})

        for line in output.split('\n'):
            if not line.strip():
                continue

            # Match Verible's output format
            match = re.match(
                r'^([^:]+):(\d+):(\d+(?:-\d+)?):\s*(.+?)\s*\[([^\]]+)\]\s*\[([^\]]+)\]',
                line
            )

            if match:
                file_name = match.group(1)
                line_num = int(match.group(2))
                col_str = match.group(3)  # Could be "32" or "32-33"
                message = match.group(4).strip()
                category = match.group(5).strip()  # e.g., "Style: trailing-spaces"
                rule_name = match.group(6).strip()  # e.g., "no-trailing-spaces"

                # Create rule ID
                rule_id = f"[VB_{rule_name.upper().replace('-', '_')}]"

                # Check if rule is enabled (like NaturalDocs linter_rules)
                if rule_id in linter_rules and not linter_rules[rule_id]:
                    # Rule is disabled, skip it
                    continue

                # Extract column start
                column = int(col_str.split('-')[0])

                # Get severity from severity_levels (like NaturalDocs)
                severity_str = severity_levels.get(rule_id, 'WARNING')
                severity = RuleSeverity[severity_str]

                violation = RuleViolation(
                    file=file_name,
                    line=line_num,
                    column=column,
                    severity=severity,
                    message=message,
                    rule_id=rule_id
                )

                violations.append(violation)

        return violations


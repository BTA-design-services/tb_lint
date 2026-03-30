#!/usr/bin/env python3
"""
Unified Linter - Modular Linting Framework

Company: Copyright (c) 2025  BTA Design Services
         Licensed under the MIT License.

Description: Flexible, plugin-based linting system supporting multiple linters

Usage:
    python3 tb_lint.py [options] <file.sv> [<file2.sv> ...]

Options:
    --help              Show this help message
    --config FILE       Configuration file (JSON)
    --base-config FILE  Common/base configuration file (JSON)
    --linter NAME       Run specific linter (default: all)
    --list-linters      List available linters
    --strict            Treat warnings as errors
    --json              Output in JSON format
    --color             Enable colored output
    -f FILE_LIST        File containing list of files (one per line)
    -o OUTPUT_FILE      Output file for results

Environment:
    TB_LINT_PROJECT_CONFIG   Directory for project lint_config.json when --config is omitted.
                             If unset, a warning is printed (stdout by default, stderr with --json)
                             and defaults to <tb_lint>/configs.

Examples:
    # Run all linters
    python3 tb_lint.py -f file_list.txt

    # Run only NaturalDocs linter
    python3 tb_lint.py --linter naturaldocs file.sv

    # Use custom config
    python3 tb_lint.py --config my_config.json -f files.txt

    # Use common + project config (project overrides common)
    python3 tb_lint.py --base-config common.json --config project.json -f files.txt
"""

import sys
import os
import json
import argparse
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add script directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from core import (
    ConfigManager,
    LinterRegistry,
    get_registry,
    BaseLinter,
    LinterResult,
    RuleSeverity
)

# Import linters to register them
from linters import NaturalDocsLinter, VeribleLinter


class Colors:
    """ANSI color codes"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'


class UnifiedLinter:
    """
    Unified linting orchestrator

    Manages multiple linters and aggregates results
    """

    def __init__(self, config_file: Optional[str] = None, base_config_file: Optional[str] = None,
                 use_color: bool = False, strict_mode: bool = False, json_mode: bool = False):
        """
        Initialize unified linter

        Args:
            config_file: Path to configuration file
            base_config_file: Optional path to common/base configuration file
            use_color: Enable colored output
            strict_mode: Treat warnings as errors
            json_mode: If True, suppress all non-JSON output
        """
        self.config_manager = ConfigManager(config_file, base_config_file)
        self.registry = get_registry()
        self.use_color = use_color and sys.stdout.isatty()
        self.strict_mode = strict_mode
        self.json_mode = json_mode

    def _color(self, color: str, text: str) -> str:
        """Apply color if enabled"""
        if self.use_color:
            return f"{color}{text}{Colors.NC}"
        return text

    def list_linters(self) -> List[str]:
        """Get list of available linters"""
        return self.registry.list_linters()

    def get_exclude_patterns(self) -> List[str]:
        """Get file/path exclude patterns from config."""
        patterns = self.config_manager.get_global_setting('exclude_paths', [])
        if not isinstance(patterns, list):
            return []
        return [str(p).strip() for p in patterns if str(p).strip()]

    def match_exclude_pattern(self, file_path: str, exclude_patterns: List[str]) -> Optional[str]:
        """
        Return the first global.exclude_paths entry that matches file_path, else None.
        """
        if not exclude_patterns:
            return None
        normalized = os.path.normpath(file_path)
        normalized_slash = normalized.replace("\\", "/")
        for pattern in exclude_patterns:
            p_norm = os.path.normpath(pattern)
            p_slash = p_norm.replace("\\", "/")
            if fnmatch.fnmatch(normalized_slash, p_slash) or fnmatch.fnmatch(
                normalized_slash, f"*{p_slash}*"
            ):
                return pattern
            if p_slash in normalized_slash:
                return pattern
        return None

    def should_exclude_file(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """
        Check whether file should be excluded from linting.

        Supports exact/prefix path fragments and glob patterns.
        """
        return self.match_exclude_pattern(file_path, exclude_patterns) is not None

    def print_exclude_report(
        self,
        exclude_patterns: List[str],
        excluded_files: List[Dict[str, str]],
        output_file=None,
    ) -> None:
        """
        Human-readable summary of configured exclude_paths and files skipped (not linted).
        """
        out = output_file if output_file else sys.stdout
        if not exclude_patterns and not excluded_files:
            return
        if exclude_patterns:
            print(
                f"\n{self._color(Colors.YELLOW, 'global.exclude_paths patterns:')}",
                file=out,
            )
            for p in exclude_patterns:
                print(f"  {p}", file=out)
        if excluded_files:
            print(
                f"\n{self._color(Colors.YELLOW, 'Excluded from linting (not parsed):')}",
                file=out,
            )
            for e in excluded_files:
                print(f"  {e['path']}", file=out)
                print(f"    matched pattern: {e['matched_pattern']}", file=out)

    def run_linter(self, linter_name: str, file_paths: List[str]) -> LinterResult:
        """
        Run a specific linter on files

        Args:
            linter_name: Name of linter to run
            file_paths: List of files to check

        Returns:
            LinterResult with violations found
        """
        # Get linter configuration
        linter_config = self.config_manager.get_linter_config(linter_name)

        # Get linter instance
        linter = self.registry.get_linter(linter_name, linter_config)

        if not linter:
            print(f"ERROR: Linter '{linter_name}' not found", file=sys.stderr)
            return LinterResult(linter_name=linter_name)

        # Run linter
        if hasattr(linter, 'check_availability'):
            is_available, error_msg = linter.check_availability()
            if not is_available:
                print(error_msg, file=sys.stderr)
                sys.exit(1)

        return linter.lint_files(file_paths)

    def run_all_linters(self, file_paths: List[str]) -> dict:
        """
        Run all enabled linters on files

        Args:
            file_paths: List of files to check

        Returns:
            Dictionary mapping linter names to results
        """
        results = {}

        for linter_name in self.list_linters():
            # Check if linter is enabled in configuration
            if not self.config_manager.is_linter_enabled(linter_name):
                # Suppress non-JSON output when in JSON mode
                if not self.json_mode:
                    print(f"\n{self._color(Colors.YELLOW, f'Skipping {linter_name} linter (disabled in config)')}")
                continue

            # Suppress separator lines and progress messages when in JSON mode
            if not self.json_mode:
                print(f"\n{self._color(Colors.CYAN, '='*80)}")
                print(f"{self._color(Colors.CYAN, f'Running {linter_name} linter...')}")
                print(f"{self._color(Colors.CYAN, '='*80)}\n")

            result = self.run_linter(linter_name, file_paths)
            results[linter_name] = result

        return results

    def print_result(self, result: LinterResult, output_file=None):
        """
        Print linter results in human-readable format

        Args:
            result: LinterResult to print
            output_file: File handle for output (default: stdout)
        """
        out = output_file if output_file else sys.stdout

        # Print violations grouped by file
        violations_by_file = {}
        for violation in result.violations:
            if violation.file not in violations_by_file:
                violations_by_file[violation.file] = []
            violations_by_file[violation.file].append(violation)

        # Print each file's violations
        for file_path, violations in violations_by_file.items():
            print(f"\n{self._color(Colors.CYAN, f'File: {file_path}')}", file=out)

            for violation in sorted(violations, key=lambda v: v.line):
                if violation.severity == RuleSeverity.ERROR:
                    color = Colors.RED
                    level = "ERROR"
                elif violation.severity == RuleSeverity.WARNING:
                    color = Colors.YELLOW
                    level = "WARNING"
                else:
                    color = Colors.BLUE
                    level = "INFO"

                print(self._color(color,
                    f"  {file_path}:{violation.line}:{violation.column}: "
                    f"{violation.rule_id} {level}: {violation.message}"),
                    file=out)

        # Print file errors
        for file_path, error_msg in result.errors.items():
            print(self._color(Colors.RED, f"\nX {file_path}: {error_msg}"), file=out)

        # Print summary
        print(f"\n{self._color(Colors.CYAN, '='*80)}", file=out)
        print(f"{self._color(Colors.CYAN, f'{result.linter_name} Summary')}", file=out)
        print(f"{self._color(Colors.CYAN, '='*80)}", file=out)
        print(f"Files checked: {result.files_checked}", file=out)
        if result.files_failed > 0:
            print(self._color(Colors.RED, f"Files failed: {result.files_failed}"), file=out)
        print(self._color(Colors.RED, f"Errors: {result.error_count}"), file=out)
        print(self._color(Colors.YELLOW, f"Warnings: {result.warning_count}"), file=out)
        print(self._color(Colors.BLUE, f"Info: {result.info_count}"), file=out)

    def print_json(
        self,
        results: dict,
        output_file=None,
        excluded: Optional[Dict[str, Any]] = None,
    ):
        """
        Print results in JSON format

        Args:
            results: Dictionary of linter results
            output_file: File handle for output (default: stdout)
            excluded: Optional {'patterns': [...], 'files': [{'path','matched_pattern'}, ...]}
        """
        out = output_file if output_file else sys.stdout

        output: Dict[str, Any] = {
            "excluded": excluded
            if excluded is not None
            else {"patterns": [], "files": []},
            "linters": {},
            "summary": {
                "total_files_checked": 0,
                "total_files_failed": 0,
                "total_errors": 0,
                "total_warnings": 0,
                "total_info": 0,
            },
        }

        for linter_name, result in results.items():
            output['linters'][linter_name] = {
                'files_checked': result.files_checked,
                'files_failed': result.files_failed,
                'errors': result.error_count,
                'warnings': result.warning_count,
                'info': result.info_count,
                'violations': [
                    {
                        'file': v.file,
                        'line': v.line,
                        'column': v.column,
                        'severity': v.severity.value,
                        'message': v.message,
                        'rule_id': v.rule_id
                    }
                    for v in result.violations
                ],
                'errors': result.errors
            }

            output['summary']['total_files_checked'] += result.files_checked
            output['summary']['total_files_failed'] += result.files_failed
            output['summary']['total_errors'] += result.error_count
            output['summary']['total_warnings'] += result.warning_count
            output['summary']['total_info'] += result.info_count

        print(json.dumps(output, indent=2), file=out)

    def print_command_info(self, args, files_to_check: List[str], output_file=None):
        """
        Print command line information for tb_lint and each enabled linter

        Args:
            args: Command line arguments
            files_to_check: List of files to check
            output_file: File handle for output (default: stdout)
        """
        out = output_file if output_file else sys.stdout

        # Print header
        print(f"{self._color(Colors.CYAN, '='*80)}", file=out)
        print(f"{self._color(Colors.CYAN, 'TB_LINT - Unified Linter Framework')}", file=out)
        print(f"{self._color(Colors.CYAN, '='*80)}", file=out)

        # Print unified linter command
        cmd_parts = ["python3 tb_lint.py"]
        if getattr(args, 'base_config', None):
            cmd_parts.append(f"--base-config {args.base_config}")
        if args.config:
            cmd_parts.append(f"--config {args.config}")
        if args.linter:
            cmd_parts.append(f"--linter {args.linter}")
        if args.strict:
            cmd_parts.append("--strict")
        if args.json:
            cmd_parts.append("--json")
        if args.color:
            cmd_parts.append("--color")
        if args.file_list:
            cmd_parts.append(f"-f {args.file_list}")
        if args.output:
            cmd_parts.append(f"-o {args.output}")
        if args.files:
            cmd_parts.extend(args.files)

        print(f"\n{self._color(Colors.BOLD, 'Unified Linter Command:')}", file=out)
        print(f"  {' '.join(cmd_parts)}", file=out)

        # Print config file
        config_display = self.config_manager.config_file or 'configs/lint_config.json (default)'
        print(f"\n{self._color(Colors.BOLD, 'Configuration:')}", file=out)
        print(f"  {config_display}", file=out)
        if self.config_manager.base_config_file:
            print(f"  base: {self.config_manager.base_config_file}", file=out)

        # Print enabled linters and their equivalent commands
        print(f"\n{self._color(Colors.BOLD, 'Enabled Linters:')}", file=out)
        for linter_name in self.list_linters():
            if self.config_manager.is_linter_enabled(linter_name):
                linter_config = self.config_manager.get_linter_config(linter_name)
                linter = self.registry.get_linter(linter_name, linter_config)

                # Generate linter-specific command
                if linter_name == "verible":
                    verible_bin = linter.verible_bin if hasattr(linter, 'verible_bin') else 'verible-verilog-lint'
                    cmd = f"{verible_bin}"

                    # Add config file if present
                    config_file_path = linter_config.get('config_file', '')
                    if config_file_path:
                        cmd += f" [config: {config_file_path}]"

                    # Add file list
                    if args.file_list:
                        cmd += f" $(cat {args.file_list})"
                    elif len(files_to_check) <= 3:
                        cmd += f" {' '.join(files_to_check)}"
                    else:
                        cmd += f" {files_to_check[0]} ... ({len(files_to_check)} files)"

                    print(f"  - {self._color(Colors.GREEN, linter_name)}:", file=out)
                    print(f"    {cmd}", file=out)

                elif linter_name == "naturaldocs":
                    verible_bin = linter.verible_bin if hasattr(linter, 'verible_bin') else 'verible-verilog-syntax'
                    cmd = f"{verible_bin} --export_json"

                    # Add config file if present
                    config_file_path = linter_config.get('config_file', '')
                    if config_file_path:
                        cmd += f" [config: {config_file_path}]"

                    # Add file list
                    if args.file_list:
                        cmd += f" $(cat {args.file_list})"
                    elif len(files_to_check) <= 3:
                        cmd += f" {' '.join(files_to_check)}"
                    else:
                        cmd += f" {files_to_check[0]} ... ({len(files_to_check)} files)"

                    print(f"  - {self._color(Colors.GREEN, linter_name)}:", file=out)
                    print(f"    {cmd}", file=out)
                    print(f"    Note: AST-based linting using Verible parser", file=out)
                else:
                    print(f"  - {self._color(Colors.GREEN, linter_name)}", file=out)

        print(f"{self._color(Colors.CYAN, '='*80)}", file=out)
        print("", file=out)

    def print_final_summary(self, results: dict, output_file=None):
        """
        Print final TB_LINT summary with individual linter status

        Args:
            results: Dictionary of linter results
            output_file: File handle for output (default: stdout)
        """
        out = output_file if output_file else sys.stdout

        # Calculate totals that must fail the run
        total_errors = sum(r.error_count for r in results.values())
        total_files_failed = sum(r.files_failed for r in results.values())

        # Print separator line
        print("", file=out)
        print("=" * 80, file=out)

        # Print individual linter status
        print(self._color(Colors.BOLD, "Linters Status:"), file=out)
        print("-" * 80, file=out)

        for linter_name, result in results.items():
            # Determine linter pass/fail status.
            # File-level failures (e.g. "Failed to prepare context") are hard failures.
            if result.error_count > 0 or result.files_failed > 0:
                status = self._color(Colors.RED, "FAILED")
                # Use ASCII 'X' instead of unicode cross mark to avoid encoding errors on Windows
                status_symbol = "X"
            else:
                status = self._color(Colors.GREEN, "PASSED")
                # Use ASCII 'V' instead of unicode check mark to avoid encoding errors on Windows
                status_symbol = "V"

            # Format linter name with padding
            linter_display = f"{linter_name:20}"

            # Print linter status with error/warning counts
            print(f"  {status_symbol} {linter_display} : {status}  "
                  f"(Errors: {result.error_count}, "
                  f"Files failed: {result.files_failed}, "
                  f"Warnings: {result.warning_count})",
                  file=out)

        print("=" * 80, file=out)

        # Determine overall pass/fail status.
        # Any file-level failure should mark TB_LINT as failed.
        if total_errors > 0 or total_files_failed > 0:
            status_msg = self._color(Colors.RED, "TB_LINT : FAILED")
        else:
            status_msg = self._color(Colors.GREEN, "TB_LINT : PASSED")

        print(status_msg, file=out)
        print("=" * 80, file=out)

    def get_exit_code(self, results: dict) -> int:
        """
        Determine exit code based on results

        Args:
            results: Dictionary of linter results

        Returns:
            0 if all passed, 1 if violations found
        """
        total_errors = sum(r.error_count for r in results.values())
        total_files_failed = sum(r.files_failed for r in results.values())
        total_warnings = sum(r.warning_count for r in results.values())

        if total_errors > 0 or total_files_failed > 0:
            return 1
        elif total_warnings > 0 and self.strict_mode:
            return 1
        return 0


def main():
    """Main entry point"""
    # Parse config arguments first to get project info for epilog
    import sys
    config_file = None
    base_config_file = None
    for i, arg in enumerate(sys.argv):
        if arg in ['-c', '--config'] and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]
        if arg == '--base-config' and i + 1 < len(sys.argv):
            base_config_file = sys.argv[i + 1]

    # Load config to get project info for epilog
    temp_config = ConfigManager(config_file, base_config_file)
    project_info = temp_config.get_project_info()
    company = project_info.get('company', '')
    project_name = project_info.get('name', '')
    epilog_text = f"{company} - {project_name}" if company and project_name else None

    parser = argparse.ArgumentParser(
        description='Unified Linting Framework',
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter if epilog_text else argparse.HelpFormatter
    )

    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('-f', '--file-list', help='File containing list of files')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('-c', '--config', help='Project/root configuration file (JSON)')
    parser.add_argument('--base-config', help='Common/base configuration file (JSON). Project config overrides base.')
    parser.add_argument('--linter', help='Run specific linter (default: all)')
    parser.add_argument('--list-linters', action='store_true', help='List available linters')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--color', action='store_true', help='Enable colored output')

    args = parser.parse_args()

    # Create unified linter
    unified = UnifiedLinter(
        config_file=args.config,
        base_config_file=args.base_config,
        use_color=args.color,
        strict_mode=args.strict,
        json_mode=args.json
    )

    # List linters if requested
    if args.list_linters:
        print("Available linters:")
        for linter_name in unified.list_linters():
            print(f"  - {linter_name}")
        return 0

    # Collect files to check
    files_to_check = []

    if args.files:
        # Check if any positional arguments look like file lists (.txt files)
        # and provide helpful error message
        for file_arg in args.files:
            if file_arg.endswith('.txt') and os.path.exists(file_arg):
                # Check if it's a file list by looking at first line
                with open(file_arg, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#') or first_line.endswith('.sv') or first_line.endswith('.svh'):
                        print(f"ERROR: '{file_arg}' appears to be a file list.", file=sys.stderr)
                        print(f"Use: python3 tb_lint.py -f {file_arg}", file=sys.stderr)
                        print(f"Not: python3 tb_lint.py {file_arg}", file=sys.stderr)
                        return 1
        files_to_check.extend(args.files)

    if args.file_list:
        if not os.path.exists(args.file_list):
            print(f"ERROR: File list '{args.file_list}' not found", file=sys.stderr)
            return 1

        with open(args.file_list, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    files_to_check.append(line)

    if not files_to_check:
        parser.print_help()
        print("\nERROR: No files specified", file=sys.stderr)
        print("\nTip: Use -f flag for file lists:", file=sys.stderr)
        print("  python3 tb_lint.py -f file_list.txt", file=sys.stderr)
        return 1

    # Apply config-based excludes (global.exclude_paths: path fragments / globs)
    exclude_patterns = unified.get_exclude_patterns()
    excluded_files: List[Dict[str, str]] = []
    if exclude_patterns:
        kept: List[str] = []
        for file_path in files_to_check:
            matched = unified.match_exclude_pattern(file_path, exclude_patterns)
            if matched is not None:
                excluded_files.append(
                    {
                        "path": os.path.abspath(file_path),
                        "matched_pattern": matched,
                    }
                )
            else:
                kept.append(file_path)
        files_to_check = kept

    excluded_meta: Dict[str, Any] = {
        "patterns": list(exclude_patterns),
        "files": excluded_files,
    }

    if not files_to_check:
        if args.json:
            print(
                json.dumps(
                    {
                        "excluded": excluded_meta,
                        "linters": {},
                        "summary": {
                            "total_files_checked": 0,
                            "total_files_failed": 0,
                            "total_errors": 0,
                            "total_warnings": 0,
                            "total_info": 0,
                        },
                    },
                    indent=2,
                )
            )
        else:
            if exclude_patterns:
                unified.print_exclude_report(exclude_patterns, excluded_files)
            print("Info: All input files were excluded by config.")
        return 0

    # Print command info (not for JSON output)
    if not args.json:
        if exclude_patterns:
            unified.print_exclude_report(exclude_patterns, excluded_files)
            if excluded_files:
                print(
                    f"Info: Skipped {len(excluded_files)} file(s) by global.exclude_paths "
                    "(see list above)."
                )
        unified.print_command_info(args, files_to_check)

    # Run linter(s)
    if args.linter:
        # Run specific linter
        result = unified.run_linter(args.linter, files_to_check)
        results = {args.linter: result}
    else:
        # Run all linters
        results = unified.run_all_linters(files_to_check)

    # Output results
    try:
        if args.output:
            with open(args.output, 'w') as out_f:
                if args.json:
                    unified.print_json(results, out_f, excluded=excluded_meta)
                else:
                    if exclude_patterns:
                        unified.print_exclude_report(
                            exclude_patterns, excluded_files, out_f
                        )
                        if excluded_files:
                            print(
                                f"Info: Skipped {len(excluded_files)} file(s) by "
                                f"global.exclude_paths (see list above).",
                                file=out_f,
                            )
                    # Print command info to file
                    unified.print_command_info(args, files_to_check, out_f)
                    for linter_name, result in results.items():
                        unified.print_result(result, out_f)
                    # Print final summary
                    unified.print_final_summary(results, out_f)
        else:
            if args.json:
                unified.print_json(results, excluded=excluded_meta)
            else:
                for linter_name, result in results.items():
                    unified.print_result(result)
                # Print final summary
                unified.print_final_summary(results)
    except Exception as e:
        print(f"ERROR writing output: {e}", file=sys.stderr)
        return 1

    # Return appropriate exit code
    return unified.get_exit_code(results)


if __name__ == '__main__':
    sys.exit(main())


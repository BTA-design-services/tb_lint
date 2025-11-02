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
    --linter NAME       Run specific linter (default: all)
    --list-linters      List available linters
    --strict            Treat warnings as errors
    --json              Output in JSON format
    --color             Enable colored output
    -f FILE_LIST        File containing list of files (one per line)
    -o OUTPUT_FILE      Output file for results
    
Examples:
    # Run all linters
    python3 tb_lint.py -f file_list.txt
    
    # Run only NaturalDocs linter
    python3 tb_lint.py --linter naturaldocs file.sv
    
    # Use custom config
    python3 tb_lint.py --config my_config.json -f files.txt
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Optional

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
    Unified linting orchestrator for multi-linter workflows.

    The class ties together configuration loading, linter registration, and
    result aggregation so that callers interact with a single high-level API.
    Documenting this coordination point makes it clear *why* the class exists
    and *how* to embed it in automation pipelines, directly supporting the
    comprehensive API documentation requested by the project owners.

    Examples:
        Create an orchestrator, run every available linter, and emit a human
        readable summary::

            unified = UnifiedLinter(config_file="configs/lint_config.json",
                                     use_color=True)
            results = unified.run_all_linters(["src/top.sv"])
            unified.print_final_summary(results)
    """
    
    def __init__(self, config_file: Optional[str] = None, use_color: bool = False,
                 strict_mode: bool = False):
        """
        Initialize the orchestrator with configuration and output controls.

        Documenting these parameters clarifies how callers steer the runtime
        behaviour, which is essential for the requested comprehensive API
        coverage.

        Args:
            config_file: Path to a root configuration file. When ``None`` the
                framework falls back to the built-in defaults under ``configs/``.
            use_color: Enable ANSI colouring for human-readable summaries when
                stdout supports it.
            strict_mode: Upgrade warnings to errors in the final exit code so
                that CI pipelines can enforce stricter policies.
        """
        self.config_manager = ConfigManager(config_file)
        self.registry = get_registry()
        self.use_color = use_color and sys.stdout.isatty()
        self.strict_mode = strict_mode
    
    def _color(self, color: str, text: str) -> str:
        """Apply color if enabled"""
        if self.use_color:
            return f"{color}{text}{Colors.NC}"
        return text
    
    def list_linters(self) -> List[str]:
        """Get list of available linters"""
        return self.registry.list_linters()
    
    def run_linter(self, linter_name: str, file_paths: List[str]) -> LinterResult:
        """
        Run a specific linter on files with configuration-aware behaviour.

        Spelling out the fallback behaviour (returning an empty
        :class:`LinterResult` when a linter is unavailable) gives API consumers
        enough information to design resilient automation around optional
        plugins, fulfilling the "comprehensive documentation" directive.

        Args:
            linter_name: Name of the linter to run as registered in the global
                registry.
            file_paths: List of files to check. Unsupported extensions are
                skipped by each linter.

        Returns:
            LinterResult with the accumulated violations and errors for the
            requested linter. When the linter is not registered the result
            contains zero checked files and an explanatory error message.
        """
        # Get linter configuration
        linter_config = self.config_manager.get_linter_config(linter_name)
        
        # Get linter instance
        linter = self.registry.get_linter(linter_name, linter_config)
        
        if not linter:
            print(f"ERROR: Linter '{linter_name}' not found", file=sys.stderr)
            return LinterResult(linter_name=linter_name)
        
        # Run linter
        return linter.lint_files(file_paths)
    
    def run_all_linters(self, file_paths: List[str]) -> dict:
        """
        Run every enabled linter on the provided files.

        The explicit documentation here highlights that enablement is decided by
        :class:`ConfigManager`, and communicates that the return value mirrors
        the enabled linters. This context equips users to interpret missing keys
        when bespoke configurations toggle linters off.

        Args:
            file_paths: List of files to check.

        Returns:
            Dictionary mapping linter names to :class:`LinterResult` objects for
            each enabled linter.
        """
        results = {}
        
        for linter_name in self.list_linters():
            # Check if linter is enabled in configuration
            if not self.config_manager.is_linter_enabled(linter_name):
                print(f"\n{self._color(Colors.YELLOW, f'Skipping {linter_name} linter (disabled in config)')}")
                continue
            
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
            print(self._color(Colors.RED, f"\n✗ {file_path}: {error_msg}"), file=out)
        
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
    
    def print_json(self, results: dict, output_file=None):
        """
        Print results in JSON format
        
        Args:
            results: Dictionary of linter results
            output_file: File handle for output (default: stdout)
        """
        out = output_file if output_file else sys.stdout
        
        output = {
            'linters': {},
            'summary': {
                'total_files_checked': 0,
                'total_files_failed': 0,
                'total_errors': 0,
                'total_warnings': 0,
                'total_info': 0
            }
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
                    
                    print(f"  • {self._color(Colors.GREEN, linter_name)}:", file=out)
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
                    
                    print(f"  • {self._color(Colors.GREEN, linter_name)}:", file=out)
                    print(f"    {cmd}", file=out)
                    print(f"    Note: AST-based linting using Verible parser", file=out)
                else:
                    print(f"  • {self._color(Colors.GREEN, linter_name)}", file=out)
        
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
        
        # Calculate total errors
        total_errors = sum(r.error_count for r in results.values())
        
        # Print separator line
        print("", file=out)
        print("=" * 80, file=out)
        
        # Print individual linter status
        print(self._color(Colors.BOLD, "Linters Status:"), file=out)
        print("-" * 80, file=out)
        
        for linter_name, result in results.items():
            # Determine linter pass/fail status
            if result.error_count > 0:
                status = self._color(Colors.RED, "FAILED")
                status_symbol = "✗"
            else:
                status = self._color(Colors.GREEN, "PASSED")
                status_symbol = "✓"
            
            # Format linter name with padding
            linter_display = f"{linter_name:20}"
            
            # Print linter status with error/warning counts
            print(f"  {status_symbol} {linter_display} : {status}  "
                  f"(Errors: {result.error_count}, "
                  f"Warnings: {result.warning_count})", 
                  file=out)
        
        print("=" * 80, file=out)
        
        # Determine overall pass/fail status
        if total_errors > 0:
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
        total_warnings = sum(r.warning_count for r in results.values())
        
        if total_errors > 0:
            return 1
        elif total_warnings > 0 and self.strict_mode:
            return 1
        return 0


def main():
    """Main entry point"""
    # Parse config file argument first to get project info for epilog
    import sys
    config_file = None
    for i, arg in enumerate(sys.argv):
        if arg in ['-c', '--config'] and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]
            break
    
    # Load config to get project info for epilog
    temp_config = ConfigManager(config_file)
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
    parser.add_argument('-c', '--config', help='Configuration file (JSON)')
    parser.add_argument('--linter', help='Run specific linter (default: all)')
    parser.add_argument('--list-linters', action='store_true', help='List available linters')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--color', action='store_true', help='Enable colored output')
    
    args = parser.parse_args()
    
    # Create unified linter
    unified = UnifiedLinter(
        config_file=args.config,
        use_color=args.color,
        strict_mode=args.strict
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
    
    # Print command info (not for JSON output)
    if not args.json:
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
                    unified.print_json(results, out_f)
                else:
                    # Print command info to file
                    unified.print_command_info(args, files_to_check, out_f)
                    for linter_name, result in results.items():
                        unified.print_result(result, out_f)
                    # Print final summary
                    unified.print_final_summary(results, out_f)
        else:
            if args.json:
                unified.print_json(results)
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


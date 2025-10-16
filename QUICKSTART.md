# TB Lint - Quick Start Guide

**BTA Design Services | DV Environment**  
**Version:** 3.0-hierarchical  
**Date:** October 16, 2025

---

## Quick Start (30 seconds)

```bash
# Navigate to directory
cd /home/vbesyakov/project/tb_lint

# Option 1: One-line script (simplest)
./run_all_tests.sh

# Option 2: Run linter directly
python3 unified_linter.py -f test/test_files.txt --color

# Option 3: Use custom configuration
python3 unified_linter.py -c configs/lint_config.json -f test/test_files.txt --color
```

---

## Common Commands

| Command | Description |
|---------|-------------|
| `./run_all_tests.sh` | **One-liner**: Run all tests |
| `python3 unified_linter.py --help` | Show help |
| `python3 unified_linter.py --list-linters` | List available linters |
| `python3 unified_linter.py -f files.txt` | Check files from list |
| `python3 unified_linter.py file.sv` | Check single file |
| `python3 unified_linter.py --linter naturaldocs -f files.txt` | Run specific linter |
| `python3 unified_linter.py --json -f files.txt -o report.json` | Generate JSON report |
| `python3 unified_linter.py --strict --color -f files.txt` | Strict mode with colors |

---

##  Configuration Structure

### Hierarchical Configuration (Recommended)

The framework uses a **hierarchical configuration** system:

**Root Config** (`configs/lint_config.json`) - Controls which linters are enabled:
```json
{
  "linters": {
    "naturaldocs": {
      "enabled": true,
      "config_file": "configs/naturaldocs.json"
    },
    "verible": {
      "enabled": false,
      "config_file": "configs/verible.json"
    }
  }
}
```

**Individual Linter Config** (`configs/naturaldocs.json`):
```json
{
  "file_header": {
    "company_name": "BTA Design Services",
    "email_domain": "@btadesignservices.com"
  },
  "severity_levels": {
    "[ND_FILE_HDR_MISS]": "ERROR",
    "[ND_CLASS_MISS]": "ERROR"
  }
}
```

**Note:** The actual `configs/naturaldocs.json` is the original `lint_naturaldocs.json` file moved to the configs directory.

**Benefits:**
-  Enable/disable linters from root config
-  Separate linter-specific settings
-  Easy to maintain and share configs
-  Team can customize individual linters

**Usage:**
```bash
# Default (automatically uses configs/lint_config.json)
python3 unified_linter.py -f files.txt

# Explicit config file
python3 unified_linter.py -c configs/lint_config.json -f files.txt
```

---

##  Basic Usage Patterns

### Check Files from List

```bash
# Create file list
echo "test/good_example.sv" > my_files.txt
echo "test/bad_example.sv" >> my_files.txt

# Run linter
python3 unified_linter.py -f my_files.txt
```

### Check Individual Files

```bash
python3 unified_linter.py test/good_example.sv test/bad_example.sv
```

### Run Specific Linter Only

```bash
# NaturalDocs only (documentation checks)
python3 unified_linter.py --linter naturaldocs -f files.txt

# Verible only (style checks)
python3 unified_linter.py --linter verible -f files.txt
```

### Generate Reports

```bash
# Text report
python3 unified_linter.py -f files.txt -o report.txt

# JSON report (for CI/CD)
python3 unified_linter.py --json -f files.txt -o report.json
```

### Run Test Suite

```bash
# Run all tests with verbose output
python3 run_tests.py --verbose

# Run tests with JSON report
python3 run_tests.py --json --output test/reports

# Run specific linter tests only
python3 run_tests.py --linter naturaldocs --summary
```

---

##  Correct vs  Wrong Usage

### Correct

```bash
# Use -f flag for file lists
python3 unified_linter.py -f sv_files.txt

# Specify config explicitly
python3 unified_linter.py -c lint_config_hierarchical.json -f files.txt

# Check individual files directly
python3 unified_linter.py file1.sv file2.sv
```

### Common Mistakes

```bash
# Missing -f flag (will show helpful error)
python3 unified_linter.py sv_files.txt
# Error: 'sv_files.txt' appears to be a file list.
# Use: python3 unified_linter.py -f sv_files.txt
```

---

## Setup Environment

```bash
export PATH=<verible>/bin:$PATH
```

---

## Understanding Output

### Human-Readable Format (Default)

```
================================================================================
Running naturaldocs linter...
================================================================================

File: test/bad_example.sv
  test/bad_example.sv:1:0: [ND_FILE_HDR_MISS] ERROR: Missing 'File:' keyword
  test/bad_example.sv:17:0: [ND_PKG_MISS] ERROR: Package without documentation

================================================================================
naturaldocs Summary
================================================================================
Files checked: 1
Errors: 2
Warnings: 0
Info: 0
```

### JSON Format (for automation)

```json
{
  "linters": {
    "naturaldocs": {
      "files_checked": 1,
      "errors": 2,
      "violations": [
        {
          "file": "test/bad_example.sv",
          "line": 1,
          "severity": "ERROR",
          "rule_id": "[ND_FILE_HDR_MISS]",
          "message": "Missing 'File:' keyword"
        }
      ]
    }
  }
}
```

---

## Next Steps

### For Users
1. Run linter on your files: `python3 unified_linter.py -f your_files.txt`
2. Review violations and fix code
3. Integrate into your workflow

### For Developers
1. Read [example/README.md](example/README.md) - How to add linters and rules
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. Study examples in `example/example_custom_rule.py`

### Advanced Configuration
1. Create hierarchical config for your team
2. Customize rule severity levels
3. Enable/disable specific linters or rules

---

## Configuration Examples

### Disable a Linter

In `lint_config_hierarchical.json`:
```json
{
  "linters": {
    "verible": {
      "enabled": false,
      "config_file": "configs/verible.json"
    }
  }
}
```

### Disable a Specific Rule

In `configs/naturaldocs.json`:
```json
{
  "rules": {
    "[ND_TYPEDEF_MISS]": {
      "enabled": false,
      "severity": "WARNING"
    }
  }
}
```

### Change Rule Severity

```json
{
  "rules": {
    "[ND_CLASS_MISS]": {
      "enabled": true,
      "severity": "WARNING"  // Changed from ERROR
    }
  }
}
```

---

##  File Organization

```
tb_lint/
├── unified_linter.py           # Main linter script
├── run_tests.py                # Test runner script
├── lint_config_modular.json    # Monolithic config (all-in-one)
├── lint_config_hierarchical.json  # Root hierarchical config
├── configs/                    # Individual linter configs
│   ├── naturaldocs.json
│   └── verible.json
├── example/                    # Examples and guides
│   ├── README.md              # How to add linters/rules
│   └── example_custom_rule.py # Example custom rules
├── test/                       # Test files
│   ├── test_files.txt         # Test batch file
│   ├── good_example.sv
│   └── bad_example.sv
└── core/                       # Core framework
    └── ...
```

---

##  Pro Tips

1. **Use hierarchical configs** for team projects - easier to manage
2. **Use --color** during development for better readability
3. **Use --json** for CI/CD integration
4. **Use --strict** to treat warnings as errors in pre-commit hooks
5. **Create custom batch files** for different test scenarios
6. **Run test suite regularly** with `python3 run_tests.py`

---

##  Troubleshooting

### Error: Verible not found
```bash
export PATH=<verible>/bin:$PATH
```

### Error: Config file not found
```bash
# Use absolute path or verify file exists
ls -la lint_config_hierarchical.json
```

### Error: No files specified
```bash
# Use -f flag for file lists
python3 unified_linter.py -f files.txt
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| **QUICKSTART.md** (this file) | Quick reference and common usage |
| **example/README.md** | How to add linters and rules |
| **ARCHITECTURE.md** | System design and structure |
| **README_MODULAR.md** | Complete framework documentation |
| **README.md** | Documentation index |

---

## Quick Links

- **Add Rules/Linters**: [example/README.md](example/README.md)
- **System Design**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Full Documentation**: [README_MODULAR.md](README_MODULAR.md)
- **Documentation Index**: [README.md](README.md)

---

Copyright (c) 2025 **BTA Design Services** | October 2025  
**Version:** 3.0-hierarchical


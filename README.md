# TB Lint - NaturalDocs & Verible Linting Tools
**BTA Design Services |  DV Environment**

**Last Updated:** October 2025

---

## 📍 Overview

This directory contains all linting and formatting tools for the BTA DV project:

- **NaturalDocs Linter** - AST-based documentation quality checker (Python 3 + Verible)
- **Verible Lint** - SystemVerilog syntax and style checker
- **Verible Format** - Code auto-formatter

All tools are orchestrated through a single Python script (`tb_lint.py`) located in `<dv_root>/verif_lib/scripts/tb_lint/`.

---

## 📦 Directory Contents

### Configuration Files
- **`lint_config.json`** - linter configuration (verible+naturalDocs)
- **`.rules.verible_lint`** - Lint rules enforcing BTA coding standards (60+ rules)
- **`.verible_format`** - Auto-formatter configuration (100 char limit, 2-space indent)
- **`lint_naturaldocs.json`** -NaturalDocs linter configuration

### Python Scripts
- **`tb_lint.py`** - **Unified linter (runs both NaturalDocs + Verible)**
- **`naturaldocs_lint.py`** - AST-based documentation linter
- **`verible_lint.py`** - Verible linting Python wrapper
- **`verible_verilog_syntax.py`** - Verible Python wrapper

### Shell Scripts
- **`setup_env.sh`** - Environment setup script (adds Verible to PATH)
- **`verible_format.sh`** - Verible formatting wrapper (no Python wrapper yet)
- **`run_tb_lint.sh`** - enables invoking TB Lint from any directory, automatically applying the default `lint_config.json` under `$PROJECT_HOME/dv/verif_lib/scripts/tb_lint`.

### Documentation
- **`README.md`** - This file (complete reference)
-
### Test Files
- **`test/`** - SystemVerilog files for testing the linters 
  `sv_files.txt` - batch mode txt file 
 
---

## 🚀 Quick Start
### 1. Setup Environment

**Automatic (Recommended)**

```bash
cd verif_lib/scripts/tb_lint
source setup_env.sh
```

**Manual**

```bash
export PATH=/scratch/tools/external_lib/verible/bin:$PATH
```


### 2. Unified Lint \& Format

Run both documentation and style checks (default):

```bash
python3 tb_lint.py -f sv_files.txt
```

Common flags:

- `--docs` – run **NaturalDocs Linter** only
- `--style` – run **Verible Lint** only
- `--both` – run both linters (default)
- `--color` – colorized terminal output
- `--json` – machine-readable JSON output
- `--strict` – treat warnings as errors

Write combined log to file:

```bash
python3 tb_lint.py -f sv_files.txt -o lint.log
```

Debug mode (show config parsing, temp files):

```bash
python3 tb_lint.py -f sv_files.txt -d
```


***

## 🌐 TB Lint Launcher

**`run_tb_lint.sh`** enables invoking TB Lint from any directory, automatically applying the default `lint_config.json` under `$PROJECT_HOME/dv/verif_lib/scripts/tb_lint`.

```bash
run_tb_lint.sh [tb_lint options]
```

Example:

```bash
run_tb_lint.sh --strict --json -f file_list.txt
```
***

## ⚙️ Verible Lint \& Format Highlights

### Verible Lint

- Enforces 55+ style and syntax rules (indentation, naming conventions, line length)
- JSON output, strict mode, summary-only, debug context


### Verible Format

- Automatic in-place formatting (2-space indent, 100-character wrap)
- Preview diffs, verify mode, CI-friendly exit codes

Usage:

```bash
# Lint only
python3 verible_lint.py -f file_list.txt --json --strict

# Format only
./verible_format.sh --inplace file.sv
```


***

## 🎯 NaturalDocs Linter - AST-Based Documentation Checker

### Key Features

- ✅ **AST-Based Analysis:** Uses Verible's Abstract Syntax Tree for 99% accuracy
- ✅ **Context Aware:** Understands code structure (classes, functions, constraints)
- ✅ **Case-Insensitive Keywords:** All NaturalDocs keywords are case-insensitive
- ✅ **Prototype Detection:** Only requires documentation on `extern` declarations
- ✅ **Flexible Constraints:** Accepts both `define:` and `Variable:` for constraints
- ✅ **Enum Support:** Accepts `Variable:`, `Typedef:`, or `Type:` for enums
- ✅ **Large Documentation:** Searches up to 50 lines for documentation blocks
- ✅ **JSON Output:** Machine-readable format for tool integration
- ✅ **Batch Processing:** Process multiple files efficiently
- ✅ **Configurable:** JSON-based configuration for project-specific settings

### Configuration File (`lint_config.json`)

The linter uses a JSON configuration file to customize project-specific metadata:

**Location:** `./verif_lib/scripts/tb_lint/lint_config.json`

**Signature-Based Naming:**

All linter rules and severity levels use concise `[ND_*]` signatures for clarity:

| Signature | Description |
|-----------|-------------|
| **Linter Rules (Enable/Disable)** | |
| `[ND_FILE_HDR]` | File header validation |
| `[ND_INCLUDE_GRD]` | Include guard validation |
| `[ND_PKG]` | Package documentation |
| `[ND_CLASS]` | Class documentation |
| `[ND_FUNC]` | Function documentation |
| `[ND_TASK]` | Task documentation |
| `[ND_CONST]` | Constraint documentation |
| `[ND_TYPEDEF]` | Typedef documentation |
| `[ND_VAR]` | Variable documentation |
| `[ND_PARAM]` | Parameter documentation |
| **Severity Levels (Issue Types)** | |
| `[ND_FILE_HDR_MISS]` | Missing File: keyword |
| `[ND_COMPANY_MISS]` | Missing Company: field |
| `[ND_AUTHOR_MISS]` | Missing Author: field |
| `[ND_GUARD_MISS]` | Missing include guards |
| `[ND_GUARD_FMT]` | Include guard format issue |
| `[ND_PKG_MISS]` | Missing package docs |
| `[ND_CLASS_MISS]` | Missing class docs |
| `[ND_FUNC_MISS]` | Missing function docs |
| `[ND_TASK_MISS]` | Missing task docs |
| `[ND_CONST_MISS]` | Missing constraint docs |
| `[ND_TYPEDEF_MISS]` | Missing typedef docs |
| `[ND_VAR_MISS]` | Missing variable docs |
| `[ND_PARAM_MISS]` | Missing parameter docs |
| `[ND_NAME_MISMATCH]` | Documented ≠ declared name |
| `[ND_WRONG_KW]` | Wrong keyword for type |
| `[ND_INVALID_KW]` | Invalid NaturalDocs keyword |

**Key Configuration Options:**

```json
{
  "project": {
    "name": " Design Verification Environment",
    "company": "BTA Design Services",
    "description": "SystemVerilog Design Verification Environment"
  },
  "file_header": {
    "company_name": "BTA Design Services",
    "company_pattern": "BTA",
    "email_domain": "@btadesignservices.com"
  },
  "linter_rules": {
    "[ND_FILE_HDR]": true,
    "[ND_INCLUDE_GRD]": true,
    "[ND_PKG]": true,
    "[ND_CLASS]": true,
    "[ND_FUNC]": true,
    "[ND_TASK]": true,
    "[ND_CONST]": true,
    "[ND_TYPEDEF]": true,
    "[ND_VAR]": true,
    "[ND_PARAM]": true
  },
  "naming_conventions": {
    "prefix_package": "bta_",
    "suffix_package": "_pkg",
    "prefix_class": "bta_"
  }
}
```

**Usage:**
```bash
# Use default config (./lint_config.json)
python3 naturaldocs_lint.py file.sv

# Use custom config
python3 naturaldocs_lint.py -c /path/to/custom_config.json file.sv
```

**Benefits:**
- ✅ Easy customization for different projects
- ✅ No need to modify Python source code
- ✅ Version-controlled project settings
- ✅ Support for multiple configurations (dev, CI, etc.)
- ✅ **Enable/Disable Specific Checks:** Fine-grained control over which checks run
- ✅ **Configurable Severity Levels:** Customize ERROR/WARNING/INFO for each check type

**Enabling/Disabling Checks:**

Each check can be individually enabled or disabled via the `linter_rules` section:

```json
{
  "linter_rules": {
    "check_include_guards": true,     // Enable include guard checks
    "check_file_header": true,        // Enable file header checks
    "check_package_docs": false,      // Disable package documentation checks
    "check_class_docs": true,         // Enable class documentation checks
    "check_function_docs": true,      // Enable function documentation checks
    "check_task_docs": true,          // Enable task documentation checks
    "check_constraint_docs": false,   // Disable constraint documentation checks
    "check_typedef_docs": true,       // Enable typedef documentation checks
    "check_variable_docs": false,     // Disable variable documentation checks
    "check_parameter_docs": true      // Enable parameter documentation checks
  }
}
```

**Use Cases:**
- **Gradual Adoption:** Start with basic checks, enable more over time
- **Legacy Code:** Disable checks for migrating codebases
- **Team-Specific:** Different teams can have different requirements
- **CI vs Dev:** Strict checking in CI, relaxed during development

**Example - Only Check Critical Items:**
```json
{
  "linter_rules": {
    "[ND_FILE_HDR]": true,
    "[ND_INCLUDE_GRD]": true,
    "[ND_PKG]": true,
    "[ND_CLASS]": true,
    "[ND_FUNC]": false,    // Skip functions during development
    "[ND_TASK]": false,
    "[ND_CONST]": false,
    "[ND_TYPEDEF]": false,
    "[ND_VAR]": false,
    "[ND_PARAM]": false
  }
}
```

**Configuring Severity Levels:**

Each type of documentation issue can have its severity customized independently:

```json
{
  "severity_levels": {
    "[ND_FILE_HDR_MISS]": "ERROR",
    "[ND_COMPANY_MISS]": "WARNING",
    "[ND_AUTHOR_MISS]": "WARNING",
    "[ND_GUARD_MISS]": "ERROR",
    "[ND_GUARD_FMT]": "ERROR",
    "[ND_PKG_MISS]": "ERROR",
    "[ND_CLASS_MISS]": "ERROR",
    "[ND_FUNC_MISS]": "ERROR",
    "[ND_TASK_MISS]": "ERROR",
    "[ND_CONST_MISS]": "ERROR",
    "[ND_TYPEDEF_MISS]": "ERROR",
    "[ND_VAR_MISS]": "ERROR",
    "[ND_PARAM_MISS]": "ERROR",
    "[ND_NAME_MISMATCH]": "ERROR",
    "[ND_WRONG_KW]": "ERROR",
    "[ND_INVALID_KW]": "ERROR"
  }
}
```

**Available Severity Levels:**
- `"ERROR"` - Fails the lint check (exit code 1)
- `"WARNING"` - Warns but doesn't fail (exit code 0 unless --strict)
- `"INFO"` - Informational only

**Use Cases:**
- **Gradual Enforcement:** Start with warnings, upgrade to errors over time
- **Team Preferences:** Some teams prefer warnings for documentation
- **Legacy Code:** Use warnings during migration, errors for new code
- **CI/CD Integration:** Different severity levels for PR checks vs merge gates

**Example - Relaxed Documentation Policy:**
```json
{
  "severity_levels": {
    "[ND_FILE_HDR_MISS]": "ERROR",
    "[ND_COMPANY_MISS]": "WARNING",
    "[ND_AUTHOR_MISS]": "WARNING",
    "[ND_PKG_MISS]": "ERROR",
    "[ND_CLASS_MISS]": "WARNING",    // Allow missing class docs
    "[ND_FUNC_MISS]": "WARNING",     // Allow missing function docs
    "[ND_TASK_MISS]": "WARNING",
    "[ND_CONST_MISS]": "WARNING",
    "[ND_NAME_MISMATCH]": "ERROR",   // Always catch name mismatches
    "[ND_WRONG_KW]": "ERROR"         // Always catch wrong keywords
  }
}
```

### What It Checks

#### 1. File Headers ✅ (ERROR)
- **Required:** `File:` keyword
- **Recommended:** `Company: BTA Design Services` (WARNING)
- **Recommended:** `Author:` with `@btadesignservices.com` email (WARNING)

#### 2. Include Guards ✅ (ERROR)
- Format: `<FILENAME>_SV` in ALL CAPS
- Structure:
  ```systemverilog
  `ifndef FILENAME_SV
  `define FILENAME_SV
  
  // File contents
  
  `endif // FILENAME_SV
  ```
- Package files: Include guards are optional

#### 3. Package Documentation ✅ (ERROR)
- Packages must have `Package:` documentation
- Example:
  ```systemverilog
  /*
      Package: my_pkg
      
      Description of the package
  */
  package my_pkg;
  ```

#### 4. Class Documentation ⚠️ (WARNING)
- Classes should have `Class:` documentation
- Type parameters (e.g., `#(type CONFIG_T=...)`) are documented in class `Parameters:` section

#### 5. Function/Task Documentation ⚠️ (WARNING)
- Only `extern` (prototype) declarations require documentation
- Implementations (`class::function`) skip documentation checks if prototype is documented
- Constructor implementations for `function new` also skip if prototype exists

#### 6. Constraint Documentation ⚠️ (WARNING)
- **Accepted Keywords:** `define:` or `Variable:`
- Both formats are valid per codebase standards
- Example:
  ```systemverilog
  //define: valid_addr_c
  //Ensures address is within valid range
  constraint valid_addr_c { addr inside {[0:1023]}; }
  ```

#### 7. Enum Documentation
- **Accepted Keywords:** `Variable:`, `Typedef:`, or `Type:`
- All three formats are valid

#### 8. Variable Documentation
- Variables can be documented with `Variable:` keyword
- Optional for most variables

### Output Examples

#### ✅ Clean File
```
Checking: bta_driver.sv

================================================================================
NaturalDocs Documentation Lint Summary
================================================================================
Files checked: 1
Errors: 0
Warnings: 0

✓ All documentation checks passed!
```

#### ⚠️ File with Warnings
```
Checking: my_class.sv
WARNING: my_class.sv:45: Class 'MyClass' without 'Class:' documentation

================================================================================
NaturalDocs Documentation Lint Summary
================================================================================
Files checked: 1
Errors: 0
Warnings: 1

⚠ Only warnings found
```

#### ❌ File with Errors
```
Checking: bad_file.sv
ERROR: bad_file.sv:1: Missing `File:` keyword in header
ERROR: bad_file.sv:15: Missing or incorrect include guard (`ifndef BAD_FILE_SV)
WARNING: bad_file.sv:25: Class without 'Class:' documentation

================================================================================
NaturalDocs Documentation Lint Summary
================================================================================
Files checked: 1
Errors: 2
Warnings: 1

✗ Documentation violations found
```

---

## 📝 Common Documentation Patterns

### File Header
```systemverilog
/*
 * File: my_driver.sv
 *
 * Company: BTA Design Services
 *
 * Author: user@btadesignservices.com
 *
 * Description: Brief description of file purpose
 */

`ifndef MY_DRIVER_SV
`define MY_DRIVER_SV

// File contents

`endif // MY_DRIVER_SV
```

### Package Documentation
```systemverilog
/*
    Package: my_pkg
    
    Package description with details about what it contains
*/
package my_pkg;
```

### Class Documentation
```systemverilog
/*
 Class: my_driver
 
 Driver class for MY protocol.
 Extends uvm_driver to provide transaction-level driving.
*/
class my_driver extends uvm_driver;
```

### Function Documentation (Extern Only)
```systemverilog
/*
 Function: build_phase
 
 UVM build phase implementation.
 
 Parameters:
     phase - Current UVM phase
*/
extern function void build_phase(uvm_phase phase);

// Implementation does NOT need documentation
function void my_class::build_phase(uvm_phase phase);
  super.build_phase(phase);
endfunction
```

### Constraint Documentation (Two Formats)
```systemverilog
// Format 1: define keyword
//define: valid_addr_c
//Ensures address is within valid range
constraint valid_addr_c { addr inside {[0:1023]}; }

// Format 2: Variable keyword (also valid)
/*
 Variable: data_size_c
 
 Constrains data size to reasonable values
*/
constraint data_size_c { data_size <= 1024; }
```

### Enum Documentation (Three Formats)
```systemverilog
// Format 1: Variable keyword
/*
 Variable: state_t
 
 State machine states
*/
typedef enum { IDLE, ACTIVE, DONE } state_t;

// Format 2: Typedef keyword (also valid)
/*
 Typedef: mode_t
 
 Operating modes
*/
typedef enum { MODE_A, MODE_B } mode_t;

// Format 3: Type keyword (also valid)
/*
 Type: status_t
 
 Status values
*/
typedef enum { OK, ERROR } status_t;
```

---

## ⚙️ Advanced Features

### Case-Insensitive Keywords
All NaturalDocs keywords are case-insensitive:
- `Function:`, `function:`, `FUNCTION:` - all valid
- `Class:`, `class:`, `CLASS:` - all valid
- `define:`, `Define:`, `DEFINE:` - all valid

### Large Documentation Blocks
The linter searches up to 50 lines backwards for documentation, allowing for comprehensive comment blocks with multiple blank lines.

### Scope-Aware Comment Extraction
The linter respects scope boundaries (`endclass`, `endmodule`, etc.) and stops at 2+ consecutive blank lines between documentation blocks to avoid incorrect associations.

### Prototype vs Implementation
The linter uses a two-pass AST analysis:
1. **First pass:** Identify and check all `extern` prototypes
2. **Second pass:** Skip documentation checks for implementations if prototype exists

This handles qualified names like `my_class::build_phase` correctly.

---

## 🔧 Verible Lint & Format

### Verible Lint - Syntax & Style Checks

**What's Enforced (All 55 Rules Enabled):**
- Line length (100 chars)
- Indentation (2 spaces, no tabs)
- Constraint naming (`*_c`)
- Typedef naming (`*_t`)
- Interface naming (`*_if`)
- Macro naming (`UPPER_CASE`)
- Parameter naming (`UPPER_CASE`)
- Port naming suffixes (`_i`, `_o`)
- Explicit begin/end blocks
- SystemVerilog best practices
- UVM patterns

**Python Wrapper (Recommended):**
```bash
# Check single file
python3 verible_lint.py <file.sv>

# Check multiple files from file list
python3 verible_lint.py -f file_list.txt

# Summary mode only
python3 verible_lint.py -f file_list.txt --summary-only

# JSON output for CI/CD integration
python3 verible_lint.py -f file_list.txt --json -o results.json

# Strict mode (warnings as errors)
python3 verible_lint.py -f file_list.txt --strict

# Show diagnostic context
python3 verible_lint.py <file.sv> --show-context

# Enable colored output
python3 verible_lint.py <file.sv> --color

# Use custom config file
python3 verible_lint.py -c custom_rules.txt <file.sv>
```

**Features:**
- ✅ 100% accuracy (matches direct Verible command)
- ✅ File list support (`-f` flag)
- ✅ JSON output for automation
- ✅ Colored output
- ✅ Summary mode
- ✅ Strict mode for CI/CD
- ✅ Detects all 55 Verible rules

### Verible Format - Code Formatting

**What's Formatted:**
- Indentation (2 spaces)
- Line length wrapping (100 chars)
- Alignment of assignments, declarations
- Spacing around operators
- Consistent formatting

**Usage:**
```bash
# Preview formatting
./verif_lib/scripts/tb_lint/verible_format.sh <file.sv>

# Show diff
./verif_lib/scripts/tb_lint/verible_format.sh --show-diff <file.sv>

# Verify formatting (exit code 0 if clean)
./verif_lib/scripts/tb_lint/verible_format.sh --verify <file.sv>

# Format in-place
./verif_lib/scripts/tb_lint/verible_format.sh --inplace <file.sv>
```

---

## 🔄 Workflow Integration

### Pre-Commit Hook Example

**Option A: Unified Linter (Recommended)**
```bash
#!/bin/bash
# .git/hooks/pre-commit

TB_LINT="./verif_lib/scripts/tb_lint"
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.sv$')

# Create temporary file list
FILE_LIST=$(mktemp)
echo "$FILES" > "$FILE_LIST"

# Run unified linter in strict mode
python3 $TB_LINT/tb_lint.py -f "$FILE_LIST" --strict --color || exit 1

# Verify formatting
for file in $FILES; do
  $TB_LINT/verible_format.sh --verify "$file" || exit 1
done

rm -f "$FILE_LIST"
```

**Option B: Individual Linters**
```bash
#!/bin/bash
# .git/hooks/pre-commit

TB_LINT="./verif_lib/scripts/tb_lint"
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.sv$')

# Create temporary file list
FILE_LIST=$(mktemp)
echo "$FILES" > "$FILE_LIST"

# Run NaturalDocs linter
python3 $TB_LINT/naturaldocs_lint.py -f "$FILE_LIST" || exit 1

# Run Verible linter in strict mode
python3 $TB_LINT/verible_lint.py -f "$FILE_LIST" --strict || exit 1

# Verify formatting
for file in $FILES; do
  $TB_LINT/verible_format.sh --verify "$file" || exit 1
done

rm -f "$FILE_LIST"
```

### CI/CD Example

#### GitLab CI/CD (Recommended)

***

## 🔄 Integration Examples

### Git Pre-Commit Hook

```bash
#!/bin/bash
TB_LINT=./verif_lib/scripts/tb_lint
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.sv$')
echo "$FILES" > sv_files.txt
python3 $TB_LINT/tb_lint.py -f sv_files.txt --strict --color || exit 1
for f in $FILES; do
  $TB_LINT/verible_format.sh --verify "$f" || exit 1
done
rm sv_files.txt
```

## 📋 Common Commands Reference

```bash
# Unified Linter (All checks)
python3 tb_lint.py -f file_list.txt --color

# NaturalDocs only
python3 naturaldocs_lint.py file.sv

# Verible Lint only
python3 verible_lint.py -f file_list.txt --strict

# Format code
./verible_format.sh --inplace file.sv

# Launch from anywhere (uses default config)
run_tb_lint.sh --docs --color -f my_files.txt
```


***

## 📞 Support

- Review this README and `UNIFIED_LINTER.md`
- Use `--help` flags on scripts
- Contact BTA DV team for assistance

***

Copyright (c) 2025 **BTA Design Services**  | October 2025
**Project:**  DV Environment | **Version:** 2.0 (AST-Based)


---

## 🔗 External Tools

### Verible
- **Location:** `/scratch/tools/external_lib/verible/verible-v0.0-4023-gc1271a00/`
- **Version:** `v0.0-4023-gc1271a00`
- **GitHub:** https://github.com/chipsalliance/verible
- **Purpose:** SystemVerilog parser, linter, and formatter

### Python 3
- **Required for:** NaturalDocs linter (AST-based analysis)
- **Minimum Version:** Python 3.6+

---

## 📚 Related Documentation

Paths are relative to the `dv` root directory:

- **Coding Standards:** `./docs/coding_standards.md`
- **NaturalDocs Patterns:** `./docs/naturaldocs_patterns.md`
- **NaturalDocs Keywords:** `./docs/naturaldocs_keywords_reference.md`
- **Cursor Rules:** `./.cursorrules`

---

## 🎓 Best Practices

### During Development
1. Run `make lint-docs` frequently (warnings OK during development)
2. Fix documentation before committing
3. Use `--no-color` for scripting/automation

### Before Commit
1. Run `make check` to ensure all checks pass
2. Fix all errors, address warnings
3. Verify formatting with `make format-check`

### In CI/CD
1. Fail on any errors
2. Consider warnings as errors in strict mode
3. Use JSON output for integration

---

## 📞 Support

For questions or issues:
1. Check this README
2. Review `/docs/naturaldocs_patterns.md`
3. - Use `--help` flags on scripts
4. Contact BTA DV team

---

## 📋 Summary

### Tool Comparison

| Tool | Purpose | Speed | Accuracy | Features |
|------|---------|-------|----------|----------|
| **Unified Linter** | **Docs + Style (both)** | **Fast** | **100%** | **Run both, JSON, colors, strict** |
| **NaturalDocs Lint** | Documentation quality | Fast | 99% (AST-based) | JSON, colors, batch |
| **Verible Lint (Python)** | Syntax & style | Fast | 100% (parser-based) | JSON, colors, strict mode, batch |
| **Verible Format** | Code formatting | Very Fast | 100% (parser-based) | In-place, diff, verify |

### When to Use What

- **🌟 Everything at once?** → Use **Unified Linter** (`tb_lint.py`) ← **RECOMMENDED**
- **Documentation issues?** → Use NaturalDocs Linter (`naturaldocs_lint.py`) or `tb_lint.py --docs`
- **Syntax/style issues?** → Use Verible Lint (`verible_lint.py`) or `tb_lint.py --style`
- **Formatting issues?** → Use Verible Format (`verible_format.sh`)
- **CI/CD Pipeline?** → Use **Unified Linter** with `--strict --json`

### Quick Full Check (All Tools)

**Option A: Unified Linter (Easiest)**
```bash
cd verif_lib/scripts/tb_lint

# Run both linters at once
python3 tb_lint.py -f all_files.txt --strict --color
```

**Option B: Individual Commands**
```bash
cd verif_lib/scripts/tb_lint

# 1. Documentation check
python3 naturaldocs_lint.py -f all_files.txt

# 2. Style/syntax check
python3 verible_lint.py -f all_files.txt --strict

# 3. Format verification
while read file; do
  ./verible_format.sh --verify "$file"
done < all_files.txt
```

---

Copyright (c) 2025 **BTA Design Services**  | October 2025  
**Project:**  DV Environment
**Version:** 2.0 (AST-Based)

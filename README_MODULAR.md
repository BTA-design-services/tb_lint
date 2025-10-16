# Modular Linting Framework - Documentation

**BTA Design Services |  DV Environment**

**Created:** October 2025  
**Version:** 3.0-hierarchical  
**Updated:** October 16, 2025

---

##  Overview

This is a **modular, plugin-based linting framework** that provides a flexible architecture for adding and managing multiple linters and rules.

### Key Features

✅ **Modular Architecture** - Each rule is in its own file
✅ **Plugin System** - Easy to add new linters
✅ **Configuration-Driven** - Enable/disable rules via JSON
✅ **Unified Interface** - Consistent API across all linters
✅ **Per-Rule Configuration** - Fine-grained control over severity and behavior
✅ **Extensible** - Simple to add custom rules and linters

---

## Architecture

### Directory Structure

```
tb_lint/
├── configs/                       # Configuration files
│   ├── lint_config.json          # Root config (default, hierarchical)
│   ├── naturaldocs.json          # NaturalDocs linter config
│   └── verible.json              # Verible linter config
│
├── core/                          # Core framework
│   ├── __init__.py
│   ├── base_rule.py              # Abstract base for rules
│   ├── base_linter.py            # Abstract base for linters
│   ├── linter_registry.py        # Plugin registry
│   └── config_manager.py         # Configuration management (hierarchical)
│
├── linters/                       # Linter implementations
│   ├── __init__.py
│   ├── naturaldocs_linter.py     # NaturalDocs linter adapter (AST-based)
│   └── verible_linter.py         # Verible linter adapter (external tool)
│
├── rules/                         # Rule implementations
│   ├── naturaldocs/              # NaturalDocs rules (one per file)
│   │   ├── __init__.py
│   │   ├── file_header.py        # File header rules
│   │   ├── include_guards.py     # Include guard rules
│   │   ├── package_docs.py       # Package documentation
│   │   ├── class_docs.py         # Class documentation
│   │   ├── function_docs.py      # Function documentation
│   │   ├── task_docs.py          # Task documentation
│   │   ├── constraint_docs.py    # Constraint documentation
│   │   ├── typedef_docs.py       # Typedef documentation
│   │   ├── variable_docs.py      # Variable documentation
│   │   └── parameter_docs.py     # Parameter documentation
│   │
│   └── verible/                  # Verible rules (external tool)
│       └── .gitkeep
│
├── example/                       # Examples for developers
│   ├── example_custom_rule.py    # Example: Custom rule
│   ├── example_custom_linter.py  # Example: Custom linter
│   └── README.md                 # Developer guide
│
├── test/                          # Test files
│   ├── good_example.sv           # Valid SystemVerilog
│   ├── bad_example*.sv           # Invalid SystemVerilog examples
│   ├── *_violations_test.sv      # Intentional violation tests
│   ├── sv_files.txt              # File list (8 files)
│   └── test_files.txt            # File list (2 files)
│
├── unified_linter.py              # Main entry point
├── run_all_tests.sh               # One-line test runner
├── verible_verilog_syntax.py      # Verible syntax wrapper
├── QUICKSTART.md                  # Quick start guide
├── ARCHITECTURE.md                # Architecture documentation
├── README_MODULAR.md              # Complete user guide (this file)
└── README.md                      # Main documentation index
```

---

##  Quick Start

### Basic Usage

```bash
# Run all linters on files
python3 unified_linter.py -f file_list.txt

# Run specific linter
python3 unified_linter.py --linter naturaldocs file.sv

# Use custom configuration
python3 unified_linter.py --config my_config.json -f files.txt

# Enable colored output
python3 unified_linter.py --color -f files.txt

# Strict mode (warnings as errors)
python3 unified_linter.py --strict -f files.txt

# JSON output
python3 unified_linter.py --json -f files.txt

# List available linters
python3 unified_linter.py --list-linters
```

### Output to File

```bash
python3 unified_linter.py -f files.txt -o results.txt
```

---

## ⚙️ Configuration

### Configuration Approaches

The framework supports two configuration approaches:

#### Option 1: Monolithic Configuration (Simple)

All settings in one file (`lint_config_modular.json`):

```json
{
  "project": {
    "name": "Project Name",
    "company": "Company Name"
  },
  "global": {
    "strict_mode": false,
    "use_color": true
  },
  "linters": {
    "naturaldocs": {
      "enabled": true,
      "file_header": {
        "company_pattern": "BTA",
        "email_domain": "@btadesignservices.com"
      },
      "rules": {
        "[ND_FILE_HDR_MISS]": {
          "enabled": true,
          "severity": "ERROR"
        }
      }
    }
  }
}
```

#### Option 2: Hierarchical Configuration (Recommended)

Root config links to individual linter configs for better organization.

**Root Config** (`lint_config_hierarchical.json`):
```json
{
  "project": {
    "name": "Design Verification Environment",
    "company": "BTA Design Services"
  },
  "global": {
    "strict_mode": false,
    "use_color": true
  },
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
    "company_pattern": "BTA",
    "email_domain": "@btadesignservices.com"
  },
  "rules": {
    "[ND_FILE_HDR_MISS]": {
      "enabled": true,
      "severity": "ERROR"
    },
    "[ND_CLASS_MISS]": {
      "enabled": true,
      "severity": "WARNING"
    }
  }
}
```

**Benefits of Hierarchical:**
- ✅ Easy to enable/disable linters from root config
- ✅ Separate linter-specific settings into dedicated files
- ✅ Teams can customize individual linters independently
- ✅ Better organization for large projects
- ✅ Settings from linked configs are merged automatically

### Per-Rule Configuration

Each rule can be configured independently:

```json
"rules": {
  "[ND_FILE_HDR_MISS]": {
    "enabled": true,           // Enable/disable this rule
    "severity": "ERROR"        // ERROR, WARNING, or INFO
  },
  "[ND_CLASS_MISS]": {
    "enabled": false,          // Disable this rule
    "severity": "WARNING"
  }
}
```

---

## 🔧 Adding a New Rule

### Step 1: Create Rule File

Create a new file in `rules/naturaldocs/my_new_rule.py`:

```python
"""
My new rule description

Company: BTA Design Services
"""

from core.base_rule import BaseRule, RuleViolation, RuleSeverity

class MyNewRule(BaseRule):
    """Check for my custom requirement"""
    
    @property
    def rule_id(self) -> str:
        return "[ND_MY_RULE]"
    
    @property
    def description(self) -> str:
        return "Description of what this rule checks"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.ERROR
    
    def check(self, file_path: str, file_content: str, context: any) -> list:
        """Implement your checking logic here"""
        violations = []
        
        # Your checking logic
        if some_condition:
            violations.append(self.create_violation(
                file_path=file_path,
                line=line_number,
                message="Violation message"
            ))
        
        return violations
```

### Step 2: Register Rule

Add to `rules/naturaldocs/__init__.py`:

```python
from .my_new_rule import MyNewRule

__all__ = [..., 'MyNewRule']
```

### Step 3: Add to Linter

Add to `linters/naturaldocs_linter.py` in `_register_rules()`:

```python
def _register_rules(self):
    # ... existing rules ...
    self.add_rule(MyNewRule())
```

### Step 4: Update Configuration

Add to `lint_config_modular.json`:

```json
"rules": {
  "[ND_MY_RULE]": {
    "enabled": true,
    "severity": "ERROR"
  }
}
```

That's it! Your new rule is now integrated.

---

##  Adding a New Linter

### Step 1: Create Linter Class

Create `linters/my_linter.py`:

```python
"""
My Custom Linter

Company: BTA Design Services
"""

from core.base_linter import BaseLinter
from core.linter_registry import register_linter

@register_linter
class MyLinter(BaseLinter):
    """My custom linter implementation"""
    
    @property
    def name(self) -> str:
        return "mylinter"
    
    @property
    def supported_extensions(self) -> list:
        return ['.sv', '.svh']
    
    def _register_rules(self):
        """Register rules for this linter"""
        # Add your rules here
        self.add_rule(MyRule1())
        self.add_rule(MyRule2())
    
    def prepare_context(self, file_path: str, file_content: str):
        """Prepare context for rules (e.g., parse AST)"""
        # Your preparation logic
        return context_object
```

### Step 2: Register Linter

Add to `linters/__init__.py`:

```python
from .my_linter import MyLinter

__all__ = [..., 'MyLinter']
```

### Step 3: Add Configuration

Add to `lint_config_modular.json`:

```json
"linters": {
  "mylinter": {
    "enabled": true,
    "rules": {
      // Your linter-specific rules
    }
  }
}
```

The linter is automatically discovered and can be used immediately!

---

##  Output Formats

### Human-Readable Output

```
================================================================================
Running naturaldocs linter...
================================================================================

File: my_file.sv
  my_file.sv:1:0: [ND_FILE_HDR_MISS] ERROR: Missing 'File:' keyword in header
  my_file.sv:45:0: [ND_CLASS_MISS] WARNING: Class 'my_class' without 'Class:' documentation

================================================================================
naturaldocs Summary
================================================================================
Files checked: 1
Errors: 1
Warnings: 1
Info: 0
```

### JSON Output

```json
{
  "linters": {
    "naturaldocs": {
      "files_checked": 1,
      "files_failed": 0,
      "errors": 1,
      "warnings": 1,
      "info": 0,
      "violations": [
        {
          "file": "my_file.sv",
          "line": 1,
          "column": 0,
          "severity": "ERROR",
          "message": "Missing 'File:' keyword in header",
          "rule_id": "[ND_FILE_HDR_MISS]"
        }
      ]
    }
  },
  "summary": {
    "total_files_checked": 1,
    "total_errors": 1,
    "total_warnings": 1
  }
}
```

---

##  Rule Naming Convention

Rules follow a consistent naming pattern:

- **Prefix:** `[ND_*]` for NaturalDocs, `[VB_*]` for Verible
- **Format:** `[PREFIX_CATEGORY_TYPE]`
- **Examples:**
  - `[ND_FILE_HDR_MISS]` - NaturalDocs file header missing
  - `[ND_CLASS_MISS]` - NaturalDocs class documentation missing
  - `[VB_LINE_LENGTH]` - Verible line length violation

---
---

##  Testing

### Test a Single Rule

```python
# Create a simple test script
from rules.naturaldocs.file_header import FileHeaderRule

rule = FileHeaderRule({'company_pattern': 'BTA'})
violations = rule.check('test.sv', file_content, None)
print(f"Found {len(violations)} violations")
```

### Test a Linter

```python
from linters.naturaldocs_linter import NaturalDocsLinter

config = {'file_header': {'company_pattern': 'BTA'}}
linter = NaturalDocsLinter(config)
result = linter.lint_file('test.sv')
print(f"Errors: {result.error_count}, Warnings: {result.warning_count}")
```

---

## API Reference

### BaseRule

All rules inherit from `BaseRule`:

```python
class MyRule(BaseRule):
    @property
    def rule_id(self) -> str:
        """Unique identifier like '[ND_MY_RULE]'"""
        
    @property  
    def description(self) -> str:
        """Human-readable description"""
        
    def default_severity(self) -> RuleSeverity:
        """Default severity (ERROR, WARNING, INFO)"""
        
    def check(self, file_path, file_content, context) -> List[RuleViolation]:
        """Implement checking logic"""
```

### BaseLinter

All linters inherit from `BaseLinter`:

```python
class MyLinter(BaseLinter):
    @property
    def name(self) -> str:
        """Linter name"""
        
    @property
    def supported_extensions(self) -> List[str]:
        """File extensions this linter handles"""
        
    def _register_rules(self):
        """Register rules: self.add_rule(MyRule())"""
        
    def prepare_context(self, file_path, file_content):
        """Prepare context for rules (e.g., AST)"""
```

---

##  Best Practices

### Rule Development

1. **Single Responsibility** - Each rule checks one thing
2. **Clear Messages** - Violation messages should be actionable
3. **Efficient** - Avoid redundant parsing or processing
4. **Configurable** - Use config for thresholds and patterns
5. **Well-Documented** - Include docstrings and comments

### Linter Development

1. **Reuse Core** - Leverage base classes and utilities
2. **Error Handling** - Gracefully handle parse failures
3. **Performance** - Cache expensive operations
4. **Testing** - Test with various file types
5. **Configuration** - Support flexible configuration

### Configuration Management

1. **Defaults** - Provide sensible defaults
2. **Documentation** - Document all config options
3. **Validation** - Validate config on load
4. **Versioning** - Track config format versions
5. **Examples** - Provide example configurations

---


##  Related Files

- **Legacy Documentation:** `README.md`
- **Configuration:** `lint_config_modular.json`
- **Core Framework:** `core/`
- **Rules:** `rules/naturaldocs/`
- **Linters:** `linters/`

---

Copyright (c) 2025 **BTA Design Services**  | October 2025
**Project:**  DV Environment
**Version:** 2.0-modular


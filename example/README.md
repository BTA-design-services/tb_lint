# Adding Linters and Rules - Complete Guide

**BTA Design Services | DV Environment**  
**Version:** 3.0-hierarchical  
**Date:** October 16, 2025

---

##  Table of Contents

1. [Overview](#overview)
2. [Adding a New Rule](#adding-a-new-rule)
3. [Adding a New Linter](#adding-a-new-linter)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Best Practices](#best-practices)

---

## Overview

This guide provides step-by-step instructions for extending the modular linting framework with custom rules and linters.

### Framework Architecture

```
tb_lint/
├── core/                    # Core framework (don't modify)
│   ├── base_rule.py        # Base class for rules
│   ├── base_linter.py      # Base class for linters
│   ├── linter_registry.py  # Plugin registry system
│   └── config_manager.py   # Configuration loader
├── linters/                 # Linter implementations
│   ├── naturaldocs_linter.py
│   └── verible_linter.py
├── rules/                   # Rule implementations
│   ├── naturaldocs/        # Rules for NaturalDocs linter
│   └── verible/            # Rules for Verible linter (future)
└── example/                # Examples and guides (you are here!)
    ├── example_custom_rule.py
    └── README.md
```

---

## Adding a New Rule

### Step 1: Understand the Rule Interface

Every rule must inherit from `BaseRule` and implement:

```python
from core.base_rule import BaseRule, RuleViolation, RuleSeverity

class MyCustomRule(BaseRule):
    @property
    def rule_id(self) -> str:
        """Unique identifier (e.g., '[ND_MY_RULE]')"""
        return "[ND_MY_RULE]"
    
    @property
    def description(self) -> str:
        """Human-readable description"""
        return "Checks for specific pattern in code"
    
    def default_severity(self) -> RuleSeverity:
        """Default severity level"""
        return RuleSeverity.ERROR  # or WARNING, INFO
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """
        Check the file and return violations
        
        Args:
            file_path: Path to file being checked
            file_content: Content of file as string
            context: Additional context (AST, parsed data, etc.)
        
        Returns:
            List of RuleViolation objects
        """
        violations = []
        # Your checking logic here
        return violations
```

### Step 2: Create the Rule File

Create a new file in the appropriate rules directory:

**Example: `rules/naturaldocs/my_custom_rule.py`**

```python
"""
Custom rule for checking specific patterns

Company: Copyright (c) 2025 BTA Design Services  
         Licensed under the MIT License.

Description: Detailed description of what this rule checks
"""

import re
from typing import List
from core.base_rule import BaseRule, RuleViolation, RuleSeverity


class MyCustomRule(BaseRule):
    """
    Check for specific patterns in SystemVerilog files
    
    This rule ensures that all classes follow a specific naming convention.
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_CUSTOM_CHECK]"
    
    @property
    def description(self) -> str:
        return "Checks for custom naming conventions"
    
    def default_severity(self) -> RuleSeverity:
        return RuleSeverity.WARNING
    
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        """Check for custom patterns"""
        violations = []
        
        # Example: Check each line
        lines = file_content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            # Your checking logic
            if self._has_issue(line):
                violations.append(self.create_violation(
                    file_path=file_path,
                    line=line_num,
                    message="Custom rule violation found",
                    context=line.strip()
                ))
        
        return violations
    
    def _has_issue(self, line: str) -> bool:
        """Helper method to check for issues"""
        # Your logic here
        return False
```

### Step 3: Register the Rule

Add your rule to `rules/naturaldocs/__init__.py`:

```python
"""Rules for NaturalDocs linter"""

from .file_header import FileHeaderRule, CompanyFieldRule, AuthorFieldRule
from .include_guards import IncludeGuardsRule, IncludeGuardFormatRule
from .package_docs import PackageDocsRule
from .class_docs import ClassDocsRule
from .function_docs import FunctionDocsRule
from .task_docs import TaskDocsRule
from .constraint_docs import ConstraintDocsRule
from .typedef_docs import TypedefDocsRule
from .variable_docs import VariableDocsRule
from .parameter_docs import ParameterDocsRule
from .my_custom_rule import MyCustomRule  # ADD THIS LINE

__all__ = [
    'FileHeaderRule',
    'CompanyFieldRule',
    'AuthorFieldRule',
    'IncludeGuardsRule',
    'IncludeGuardFormatRule',
    'PackageDocsRule',
    'ClassDocsRule',
    'FunctionDocsRule',
    'TaskDocsRule',
    'ConstraintDocsRule',
    'TypedefDocsRule',
    'VariableDocsRule',
    'ParameterDocsRule',
    'MyCustomRule',  # ADD THIS LINE
]
```

### Step 4: Add Rule to Linter

Update the linter to use your rule in `linters/naturaldocs_linter.py`:

```python
# Add import at top
from rules.naturaldocs import (
    FileHeaderRule, CompanyFieldRule, AuthorFieldRule,
    IncludeGuardsRule, IncludeGuardFormatRule,
    PackageDocsRule, ClassDocsRule, FunctionDocsRule,
    TaskDocsRule, ConstraintDocsRule, TypedefDocsRule,
    VariableDocsRule, ParameterDocsRule,
    MyCustomRule  # ADD THIS LINE
)

# In _register_rules method, add:
def _register_rules(self):
    """Register all NaturalDocs rules"""
    # ... existing rules ...
    
    # Add your custom rule
    self.add_rule(MyCustomRule())
```

### Step 5: Configure the Rule

Add configuration in your config JSON file (e.g., `lint_config_modular.json`):

```json
{
  "linters": {
    "naturaldocs": {
      "enabled": true,
      "rules": {
        "[ND_CUSTOM_CHECK]": {
          "enabled": true,
          "severity": "WARNING"
        }
      }
    }
  }
}
```

### Step 6: Test the Rule

```bash
# Test on a single file
python3 tb_lint.py --linter naturaldocs test/test_file.sv

# Test with your config
python3 tb_lint.py -c my_config.json --linter naturaldocs -f files.txt
```

---

## Adding a New Linter

### Step 1: Understand the Linter Interface

Every linter must inherit from `BaseLinter` and implement:

```python
from core.base_linter import BaseLinter, LinterResult
from core.linter_registry import register_linter

@register_linter  # This decorator registers your linter automatically
class MyLinter(BaseLinter):
    @property
    def name(self) -> str:
        """Unique name for this linter"""
        return "mylinter"
    
    @property
    def supported_extensions(self) -> List[str]:
        """File extensions this linter can process"""
        return ['.sv', '.svh', '.v']
    
    def prepare_context(self, file_path: str, file_content: str) -> any:
        """
        Prepare context for rules (optional)
        This could be AST parsing, preprocessing, etc.
        """
        return None
    
    def _register_rules(self):
        """Register all rules for this linter"""
        self.add_rule(MyRule1())
        self.add_rule(MyRule2())
```

### Step 2: Create the Linter File

Create `linters/my_linter.py`:

```python
"""
My Custom Linter Implementation

Company: Copyright (c) 2025 BTA Design Services  
         Licensed under the MIT License.

Description: Custom linter for specific checks
"""

import os
import sys
from typing import List, Optional

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_linter import BaseLinter
from core.linter_registry import register_linter


@register_linter
class MyLinter(BaseLinter):
    """
    Custom linter for specific SystemVerilog checks
    
    This linter performs specialized checks not covered by other linters.
    """
    
    @property
    def name(self) -> str:
        return "mylinter"
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.sv', '.svh']
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the linter"""
        super().__init__(config)
        # Add any initialization here
    
    def prepare_context(self, file_path: str, file_content: str) -> any:
        """
        Prepare context for rule checking
        
        This could involve:
        - Parsing the file (AST)
        - Running external tools
        - Preprocessing
        """
        # Simple example: no special context
        return None
        
        # Advanced example: parse and return AST
        # ast = parse_file(file_content)
        # return ast
    
    def _register_rules(self):
        """Register all rules for this linter"""
        # Import and register your rules
        from rules.mylinter import MyRule1, MyRule2
        
        self.add_rule(MyRule1())
        self.add_rule(MyRule2())
```

### Step 3: Export the Linter

Update `linters/__init__.py`:

```python
"""Linter implementations"""

from .naturaldocs_linter import NaturalDocsLinter
from .verible_linter import VeribleLinter
from .my_linter import MyLinter  # ADD THIS LINE

__all__ = [
    'NaturalDocsLinter',
    'VeribleLinter',
    'MyLinter',  # ADD THIS LINE
]
```

### Step 4: Configure the Linter

Add to your config JSON file:

```json
{
  "linters": {
    "mylinter": {
      "enabled": true,
      "custom_setting": "value",
      "rules": {
        "[MY_RULE_1]": {
          "enabled": true,
          "severity": "ERROR"
        },
        "[MY_RULE_2]": {
          "enabled": true,
          "severity": "WARNING"
        }
      }
    }
  }
}
```

### Step 5: Import in Main Script

Update `tb_lint.py` to import your linter:

```python
# Add to imports section (around line 56)
from linters import NaturalDocsLinter, VeribleLinter, MyLinter
```

### Step 6: Test the Linter

```bash
# List linters (should show your new linter)
python3 tb_lint.py --list-linters

# Run your linter
python3 tb_lint.py --linter mylinter -f files.txt
```

---

## Configuration

### Configuration Structure

The hierarchical configuration structure supports:

```json
{
  "project": {
    "name": "Project Name",
    "company": "Company Name",
    "description": "Project description"
  },
  "global": {
    "strict_mode": false,
    "use_color": true
  },
  "linters": {
    "linter_name": {
      "enabled": true,
      "custom_config_file": "path/to/linter_specific.json",
      "custom_setting": "value",
      "rules": {
        "[RULE_ID]": {
          "enabled": true,
          "severity": "ERROR",
          "custom_param": "value"
        }
      }
    }
  }
}
```

### Accessing Configuration in Rules

```python
class MyRule(BaseRule):
    def check(self, file_path: str, file_content: str, context: any) -> List[RuleViolation]:
        # Access rule-specific configuration
        max_length = self.config.get('max_length', 100)
        custom_pattern = self.config.get('pattern', r'default_pattern')
        
        # Use in your logic
        if len(line) > max_length:
            violations.append(...)
        
        return violations
```

### Accessing Configuration in Linters

```python
class MyLinter(BaseLinter):
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        
        # Access linter-specific configuration
        self.custom_setting = self.config.get('custom_setting', 'default')
        self.external_tool = self.config.get('external_tool_path', '/usr/bin/tool')
```

---

## Testing

### Test Your Rule Standalone

Create a test file: `test_my_rule.py`

```python
#!/usr/bin/env python3
"""Test script for custom rule"""

import sys
sys.path.insert(0, '..')

from rules.naturaldocs.my_custom_rule import MyCustomRule

# Test file
test_content = """
// Test content here
class MyClass;
endclass
"""

rule = MyCustomRule()
violations = rule.check('test.sv', test_content, None)

print(f"Found {len(violations)} violations:")
for v in violations:
    print(f"  Line {v.line}: {v.message}")
```

Run:
```bash
cd example
python3 test_my_rule.py
```

### Test with Batch Files

Create a test batch file: `test/my_tests.txt`

```
# Test files for my custom rule
test/good_example.sv
test/bad_example.sv
test/edge_case.sv
```

Run:
```bash
python3 tb_lint.py --linter mylinter -f test/my_tests.txt
```

---

## Best Practices

### Rule Development

1. **Single Responsibility**: Each rule should check one specific thing
2. **Clear Messages**: Violation messages should be actionable
3. **Performance**: Avoid expensive operations in loops
4. **Documentation**: Add detailed comments explaining the check
5. **Testing**: Test with both valid and invalid cases

### Linter Development

1. **Focused Scope**: Each linter should handle related checks
2. **Error Handling**: Handle parse errors gracefully
3. **Configuration**: Make behavior configurable
4. **Context Preparation**: Do expensive operations once in `prepare_context`
5. **External Tools**: Check tool availability and provide helpful errors

### Configuration

1. **Sensible Defaults**: Provide reasonable default values
2. **Documentation**: Document all configuration options
3. **Validation**: Validate configuration values
4. **Hierarchical**: Use nested structure for organization

### File Organization

```
rules/
└── mylinter/
    ├── __init__.py          # Export all rules
    ├── rule_category1.py    # Related rules grouped
    ├── rule_category2.py
    └── helpers.py           # Shared helper functions

linters/
├── __init__.py
└── mylinter.py              # One file per linter
```

### Code Style

```python
# Good: Clear, documented, with examples
class FileHeaderRule(BaseRule):
    """
    Check for file header documentation
    
    This rule ensures that every file has a proper header with:
    - File: keyword
    - Company: field
    - Author: field with valid email
    
    Example valid header:
        /*
         * File: my_file.sv
         * Company: BTA Design Services
         * Author: John Doe <jdoe@btadesignservices.com>
         */
    """
    
    @property
    def rule_id(self) -> str:
        return "[ND_FILE_HDR_MISS]"
    
    # ... implementation
```

### Error Messages

```python
# Good: Specific, actionable
violations.append(self.create_violation(
    file_path=file_path,
    line=line_num,
    message=f"Class '{class_name}' missing documentation comment. "
            f"Add /** Class: {class_name} */ before class declaration.",
    context=line.strip()
))

# Bad: Vague, not actionable
violations.append(self.create_violation(
    file_path=file_path,
    line=line_num,
    message="Missing docs",
    context=""
))
```

---

## Examples

### Example 1: Simple Text-Based Rule

See `example/example_custom_rule.py` - `TodoCommentRule`

This rule scans for TODO comments using regex:
- Simple text pattern matching
- No AST required
- Good for comment-based checks

### Example 2: AST-Based Rule

See `rules/naturaldocs/class_docs.py` - `ClassDocsRule`

This rule uses Verible AST:
- Finds class declarations in AST
- Checks for documentation before class
- More accurate than text search

### Example 3: Complete Custom Linter

See `example/example_custom_linter.py` - `StyleCheckLinter`

This linter demonstrates:
- Creating a complete custom linter with multiple rules
- Trailing whitespace detection
- Line length checking
- Tab character detection
- Configurable parameters
- Direct testing capability

### Example 4: External Tool Wrapper

See `linters/verible_linter.py` - `VeribleLinter`

This linter wraps an external tool:
- Runs verible-verilog-lint
- Parses output
- Converts to framework format

---

## Quick Reference

### Rule Checklist

- [ ] Created rule file in `rules/lintername/`
- [ ] Implemented all required methods
- [ ] Added to `rules/lintername/__init__.py`
- [ ] Registered in linter's `_register_rules()`
- [ ] Added configuration in JSON
- [ ] Tested standalone
- [ ] Tested with linter
- [ ] Documented in comments

### Linter Checklist

- [ ] Created linter file in `linters/`
- [ ] Used `@register_linter` decorator
- [ ] Implemented all required methods
- [ ] Added to `linters/__init__.py`
- [ ] Imported in `tb_lint.py`
- [ ] Added configuration in JSON
- [ ] Created rules for linter
- [ ] Tested with `--list-linters`
- [ ] Tested running linter
- [ ] Documented behavior

---

## Support

### Documentation

- **This Guide**: Complete how-to for adding linters/rules
- **QUICKSTART_MODULAR.md**: Quick start guide
- **README_MODULAR.md**: Full framework documentation
- **ARCHITECTURE.md**: System design details

### Example Code

- **example/example_custom_rule.py**: Three example rules
- **rules/naturaldocs/**: Production rule examples
- **linters/naturaldocs_linter.py**: AST-based linter example
- **linters/verible_linter.py**: External tool wrapper example

---

Copyright (c) 2025 **BTA Design Services** | October 2025  
**Version:** 2.0-modular


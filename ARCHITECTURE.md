# Modular Linting Framework - Architecture Overview

**BTA Design Services |  DV Environment**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      unified_linter.py                          │
│                  (Main Orchestrator)                            │
│  - Command-line interface                                       │
│  - Result aggregation                                           │
│  - Output formatting (JSON/Human-readable)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    core/config_manager.py                        │
│              (Hierarchical Configuration Management)             │
│  - Load root config (configs/lint_config.json)                  │
│  - Link to individual linter configs                            │
│  - Per-linter settings (enable/disable)                         │
│  - Per-rule settings (severity, enabled)                        │
│  - Environment variable support (VERIBLE_HOME, etc.)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  core/linter_registry.py                         │
│                    (Plugin Registry)                            │
│  - Discover linters via @register_linter                        │
│  - Create linter instances                                      │
│  - Manage linter lifecycle                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐      ┌─────────────────────┐
│  NaturalDocsLinter  │      │   VeribleLinter     │
│  (naturaldocs)      │      │   (verible)         │
├─────────────────────┤      ├─────────────────────┤
│ - Verible AST       │      │ - External tool     │
│ - 13 rules          │      │ - Output parsing    │
│ - Context prep      │      │ - Config mapping    │
└──────────┬──────────┘      └──────────┬──────────┘
           │                            │
           ▼                            ▼
    ┌──────────┐                 ┌──────────┐
    │  Rules   │                 │  Native  │
    │  (13)    │                 │  Rules   │
    └──────────┘                 └──────────┘
```

---

##  Component Diagram

```
┌──────────────────────── CORE FRAMEWORK ────────────────────────┐
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │   BaseRule      │  │  BaseLinter     │  │  ConfigManager │ │
│  ├─────────────────┤  ├─────────────────┤  ├────────────────┤ │
│  │ + rule_id       │  │ + name          │  │ + load_config  │ │
│  │ + description   │  │ + extensions    │  │ + get_linter   │ │
│  │ + severity      │  │ + lint_files()  │  │ + get_rule     │ │
│  │ + check()       │  │ + register()    │  │ + get_setting  │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │             LinterRegistry (Plugin System)                 ││
│  ├────────────────────────────────────────────────────────────┤│
│  │ - Automatic discovery via decorator                        ││
│  │ - Global registry: _global_registry                        ││
│  │ - get_linter(name) → returns instance                      ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌────────────────────── LINTER LAYER ────────────────────────────┐
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           @register_linter                              │   │
│  │           class NaturalDocsLinter(BaseLinter)           │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  - Verible AST parsing                                  │   │
│  │  - Context preparation (AST context)                    │   │
│  │  - Rule registration (_register_rules)                  │   │
│  │  - Supported: .sv, .svh files                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           @register_linter                              │   │
│  │           class VeribleLinter(BaseLinter)               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  - Wraps verible-verilog-lint                           │   │
│  │  - Output parsing and conversion                        │   │
│  │  - Config file management                               │   │
│  │  - Supported: .sv, .svh, .v, .vh files                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────── RULE LAYER ──────────────────────────────┐
│                                                                 │
│  NaturalDocs Rules (rules/naturaldocs/)                        │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐ │
│  │FileHeaderRule│IncludeGuards │PackageDocRule│ClassDocRule │ │
│  ├──────────────┼──────────────┼──────────────┼─────────────┤ │
│  │   3 rules    │   2 rules    │   1 rule     │   1 rule    │ │
│  └──────────────┴──────────────┴──────────────┴─────────────┘ │
│                                                                 │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐ │
│  │FunctionDoc   │TaskDocRule   │ConstraintDoc │TypedefDoc   │ │
│  ├──────────────┼──────────────┼──────────────┼─────────────┤ │
│  │   1 rule     │   1 rule     │   1 rule     │   1 rule    │ │
│  └──────────────┴──────────────┴──────────────┴─────────────┘ │
│                                                                 │
│  ┌──────────────┬──────────────┐                               │
│  │VariableDoc   │ParameterDoc  │                               │
│  ├──────────────┼──────────────┤                               │
│  │   1 rule     │   1 rule     │                               │
│  └──────────────┴──────────────┘                               │
│                                                                 │
│  Total: 13 individual rule implementations                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
1. USER INPUT
   ↓
   python3 unified_linter.py -f files.txt --linter naturaldocs

2. CONFIGURATION LOADING
   ↓
   ConfigManager loads lint_config_modular.json
   - Global settings
   - Linter-specific settings
   - Per-rule settings

3. LINTER DISCOVERY
   ↓
   LinterRegistry finds registered linters
   - @register_linter decorator auto-registers
   - Returns NaturalDocsLinter instance

4. RULE REGISTRATION
   ↓
   NaturalDocsLinter._register_rules()
   - Creates rule instances with config
   - Each rule checks if enabled
   - Severity set from config or default

5. FILE PROCESSING (per file)
   ↓
   a) Read file content
   b) prepare_context() - Parse with Verible → AST
   c) For each enabled rule:
      - rule.check(file, content, AST) → violations[]
   d) Collect all violations

6. RESULT AGGREGATION
   ↓
   LinterResult contains:
   - files_checked, files_failed
   - violations[] (line, severity, message, rule_id)
   - errors{} (parse failures)

7. OUTPUT FORMATTING
   ↓
   UnifiedLinter formats results:
   - Human-readable (colored text)
   - JSON (machine-readable)

8. EXIT CODE
   ↓
   0 = success (no errors)
   1 = failures found (or warnings in strict mode)
```

---

##  Plugin System

### Registration Mechanism

```python
# Step 1: Decorator registers class
@register_linter
class MyLinter(BaseLinter):
    @property
    def name(self) -> str:
        return "mylinter"
    
    # ... implement required methods

# Step 2: Auto-discovery
# When module imports, decorator runs
# Adds MyLinter to global registry

# Step 3: Retrieval
registry = get_registry()
linter = registry.get_linter("mylinter", config)
```

### Registration Flow

```
┌─────────────────────────────────────────┐
│  linters/my_linter.py                   │
│  @register_linter                       │
│  class MyLinter(BaseLinter): ...        │
└──────────────┬──────────────────────────┘
               │ (import time)
               ▼
┌─────────────────────────────────────────┐
│  core/linter_registry.py                │
│  _global_registry.register(MyLinter)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Registry Storage                       │
│  {'mylinter': MyLinter}                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  unified_linter.py                      │
│  linter = registry.get_linter('mylinter')│
└─────────────────────────────────────────┘
```

---

## 📋 Rule Execution Flow

```
┌──────────────────────────────────────────────────────┐
│  User runs: unified_linter.py -f files.txt          │
└──────────────────┬───────────────────────────────────┘
                   ▼
         ┌─────────────────────┐
         │  Load Configuration │
         │  - lint_config.json │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  Get Linter Instance│
         │  - NaturalDocsLinter│
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  Register Rules     │
         │  - 13 rules created │
         └──────────┬──────────┘
                    ▼
    ┌───────────────────────────────────┐
    │  For each file in files.txt:      │
    └───────────┬───────────────────────┘
                ▼
    ┌───────────────────────┐
    │  Read file            │
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │  Prepare Context      │
    │  - Parse with Verible │
    │  - Generate AST       │
    └───────────┬───────────┘
                ▼
    ┌───────────────────────────────────┐
    │  For each enabled rule:           │
    │                                   │
    │  1. FileHeaderRule.check()        │
    │     → violations[]                │
    │                                   │
    │  2. IncludeGuardsRule.check()     │
    │     → violations[]                │
    │                                   │
    │  3. PackageDocsRule.check()       │
    │     → violations[]                │
    │                                   │
    │  ... (all 13 rules)               │
    │                                   │
    │  Collect all violations           │
    └───────────┬───────────────────────┘
                ▼
    ┌───────────────────────┐
    │  Aggregate Results    │
    │  - LinterResult       │
    │  - violations[]       │
    │  - errors{}           │
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │  Format Output        │
    │  - Human-readable or  │
    │  - JSON format        │
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │  Display Results      │
    └───────────────────────┘
```

---

##  Key Design Patterns

### 1. **Plugin Architecture**
- Linters register themselves via decorator
- No hard-coded linter list
- Add new linters without modifying core

### 2. **Strategy Pattern**
- Each rule is a separate strategy
- Rules implement common interface (BaseRule)
- Easy to swap/add/remove rules

### 3. **Template Method**
- BaseLinter defines workflow
- Subclasses implement specific steps
- Consistent behavior across linters

### 4. **Factory Pattern**
- LinterRegistry creates linter instances
- ConfigManager provides configuration
- Centralized object creation

### 5. **Decorator Pattern**
- @register_linter adds registration logic
- Clean separation of concerns
- No boilerplate in linter classes

---

## Configuration Hierarchy

```
lint_config_modular.json
├── project {}                    # Project metadata
├── global {}                     # Global settings
│   ├── strict_mode
│   └── use_color
└── linters {}                    # Per-linter config
    ├── naturaldocs {}
    │   ├── enabled
    │   ├── file_header {}        # Linter-specific settings
    │   │   ├── company_pattern
    │   │   └── email_domain
    │   └── rules {}              # Per-rule settings
    │       ├── [ND_FILE_HDR_MISS] {}
    │       │   ├── enabled
    │       │   └── severity
    │       ├── [ND_CLASS_MISS] {}
    │       │   ├── enabled
    │       │   └── severity
    │       └── ... (all rules)
    └── verible {}
        ├── enabled
        ├── rules_file
        └── rules {}
```

---

## Extensibility Points

### Add New Rule
1. Create `rules/naturaldocs/my_rule.py`
2. Inherit from `BaseRule`
3. Implement 4 required methods/properties
4. Register in `__init__.py`
5. Add to linter's `_register_rules()`
6. Configure in `lint_config_modular.json`

### Add New Linter
1. Create `linters/my_linter.py`
2. Inherit from `BaseLinter`
3. Use `@register_linter` decorator
4. Implement 4 required methods/properties
5. Configure in `lint_config_modular.json`
6. Done! Auto-discovered

### Add New Output Format
1. Modify `unified_linter.py`
2. Add new method (e.g., `print_xml()`)
3. Add command-line option
4. Format `LinterResult` data

---

##  Comparison with Legacy

| Aspect | Legacy | Modular |
|--------|--------|---------|
| Lines of code | 1565 (monolithic) | ~100-150 per file |
| Rules | Embedded in linter | Separate files |
| Add rule | Edit large file | Create new file |
| Linters | Hard-coded | Plugin-based |
| Configuration | Single-level | Hierarchical |
| Testing | Complex | Per-rule/per-linter |
| Extensibility | Difficult | Simple |
| Maintainability | Hard | Easy |

---

##  Architecture Benefits

### Modularity
- Small, focused files
- Clear responsibilities
- Easy to understand

### Flexibility
- Plugin system
- Configuration-driven
- Multiple output formats

### Extensibility
- Add rules easily
- Add linters easily
- Add features easily

### Maintainability
- Small files to edit
- Clear structure
- Well-documented

### Testability
- Test rules individually
- Test linters individually
- Mock dependencies

---

Copyright (c) 2025 **BTA Design Services** | October 16, 2025  
**Version:** 3.0-hierarchical


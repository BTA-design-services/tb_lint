# Modular Linting Framework - Documentation Index

**BTA Design Services |  DV Environment**  
**Version:** 3.0-hierarchical | **Date:** October 16, 2025

---

## 📚 Documentation Overview

This index provides quick navigation to all documentation for the modular linting framework.

---

## 🚀 Getting Started

### For Users
1. **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide (START HERE)
   - 30-second quick start
   - Common commands
   - Configuration options (monolithic vs hierarchical)
   - Usage patterns and examples
   - Test runner usage

2. **[README_MODULAR.md](README_MODULAR.md)** - Complete user guide
   - Full feature documentation
   - Hierarchical configuration reference
   - Adding rules and linters
   - API reference
   - Best practices

3. **[example/README.md](example/README.md)** - Developer guide
   - Step-by-step guide to add rules
   - Step-by-step guide to add linters
   - Configuration examples
   - Testing procedures
   - Best practices

### For Developers
1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
   - Component diagrams
   - Data flow diagrams
   - Design patterns
   - Extensibility points

2. **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - Migration guide
   - What was created
   - Benefits of modular system
   - Comparison with legacy
   - Migration path

---

## 📁 File Organization

### Core Framework (`core/`)

| File | Purpose | Key Classes |
|------|---------|-------------|
| `base_rule.py` | Abstract base for rules | `BaseRule`, `RuleViolation`, `RuleSeverity` |
| `base_linter.py` | Abstract base for linters | `BaseLinter`, `LinterResult` |
| `linter_registry.py` | Plugin registry | `LinterRegistry`, `@register_linter` |
| `config_manager.py` | Configuration management | `ConfigManager` |
| `__init__.py` | Package exports | - |

### Linter Implementations (`linters/`)

| File | Purpose | Supported Files |
|------|---------|-----------------|
| `naturaldocs_linter.py` | NaturalDocs adapter | `.sv`, `.svh` |
| `verible_linter.py` | Verible adapter | `.sv`, `.svh`, `.v`, `.vh` |
| `__init__.py` | Package exports | - |

### Rules (`rules/naturaldocs/`)

| File | Rules | Description |
|------|-------|-------------|
| `file_header.py` | 3 rules | File header documentation |
| `include_guards.py` | 2 rules | Include guard validation |
| `package_docs.py` | 1 rule | Package documentation |
| `class_docs.py` | 1 rule | Class documentation |
| `function_docs.py` | 1 rule | Function documentation |
| `task_docs.py` | 1 rule | Task documentation |
| `constraint_docs.py` | 1 rule | Constraint documentation |
| `typedef_docs.py` | 1 rule | Typedef documentation |
| `variable_docs.py` | 1 rule | Variable documentation |
| `parameter_docs.py` | 1 rule | Parameter documentation |
| `__init__.py` | - | Package exports |

**Total: 13 individual rules**

### Main Scripts

| File | Purpose |
|------|---------|
| `unified_linter.py` | Main orchestrator for modular system |
| `run_all_tests.sh` | **One-line script** to run all tests |
| `example/example_custom_rule.py` | Example custom rule implementation |
| `example/example_custom_linter.py` | Example custom linter implementation |

### Configuration

| File | Purpose |
|------|---------|
| `lint_config_hierarchical.json` | **Recommended** - Root config linking individual linter configs |
| `lint_config_modular.json` | Monolithic configuration (all-in-one) |
| `configs/naturaldocs.json` | Individual NaturalDocs config (moved from `lint_naturaldocs.json`) |
| `configs/verible.json` | Individual Verible configuration |
| `lint_config_default.json` | Default BTA configuration (legacy) |
| `lint_config.json` | Legacy configuration (preserved) |

### Documentation

| File | Purpose |
|------|---------|
| `INDEX.md` | This file - documentation index |
| `QUICKSTART.md` | **START HERE** - Quick start guide with hierarchical config |
| `example/README.md` | **Developer guide** - How to add linters and rules |
| `README_MODULAR.md` | Complete documentation (updated for v3.0) |
| `ARCHITECTURE.md` | System architecture |
| `MIGRATION_SUMMARY.md` | Migration guide from legacy |
| `README.md` | Legacy documentation (preserved) |

---

## 🎯 Quick Navigation

### I want to...

#### **Use the linter**
→ Start with [QUICKSTART.md](QUICKSTART.md)

#### **Understand the architecture**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

#### **Add a new rule**
→ Read [example/README.md](example/README.md) - Complete guide
→ Study `example/example_custom_rule.py`

#### **Add a new linter**
→ Read [example/README.md](example/README.md) - Complete guide
→ Study `linters/naturaldocs_linter.py`

#### **Configure the linter**
→ See "Configuration" in [README_MODULAR.md](README_MODULAR.md)
→ Edit `lint_config_modular.json`

#### **Migrate from legacy**
→ Read [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)

#### **Understand design decisions**
→ Read "Design Patterns" in [ARCHITECTURE.md](ARCHITECTURE.md)

#### **See examples**
→ Check `example_custom_rule.py`
→ Review rules in `rules/naturaldocs/`

---

## 📖 Documentation by Topic

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
  - Component diagrams
  - Data flow
  - Design patterns
  - Plugin system

### Usage & Configuration
- [QUICKSTART_MODULAR.md](QUICKSTART_MODULAR.md) - Quick start
  - Basic commands
  - Common use cases
  - Quick configuration
  
- [README_MODULAR.md](README_MODULAR.md) - Complete guide
  - Full feature list
  - Configuration reference
  - Output formats
  - Best practices

### Development & Extension
- [README_MODULAR.md](README_MODULAR.md) - Developer guide
  - Adding rules
  - Adding linters
  - API reference
  - Testing

- [ARCHITECTURE.md](ARCHITECTURE.md) - Design reference
  - Extensibility points
  - Design patterns
  - Component interaction

### Migration & Comparison
- [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Migration guide
  - What changed
  - Benefits
  - Comparison tables
  - Migration path

---

## 🔍 Code Reference

### Core Classes

```
BaseRule (core/base_rule.py)
├── rule_id: str
├── description: str
├── default_severity() → RuleSeverity
├── check(file, content, context) → List[RuleViolation]
└── create_violation(...) → RuleViolation

BaseLinter (core/base_linter.py)
├── name: str
├── supported_extensions: List[str]
├── _register_rules()
├── prepare_context(file, content) → context
└── lint_files(files) → LinterResult

LinterRegistry (core/linter_registry.py)
├── register(linter_class)
├── get_linter(name, config) → BaseLinter
├── get_all_linters(config) → List[BaseLinter]
└── list_linters() → List[str]

ConfigManager (core/config_manager.py)
├── get_linter_config(name) → dict
├── get_rule_config(linter, rule) → dict
├── is_rule_enabled(linter, rule) → bool
└── get_rule_severity(linter, rule) → str
```

### Example Rules

See `rules/naturaldocs/*.py` for complete implementations:
- `file_header.py` - Simple text-based checks
- `class_docs.py` - AST-based checks
- `function_docs.py` - Complex logic with prototypes

### Example Linters

- `linters/naturaldocs_linter.py` - AST-based linter
- `linters/verible_linter.py` - External tool wrapper

---

## 📊 Statistics

### Code Organization
- **Core framework:** 5 files (~600 lines)
- **Linter implementations:** 2 files (~400 lines)
- **Rule implementations:** 10 files (~1200 lines)
- **Main orchestrator:** 1 file (~300 lines)
- **Documentation:** 5 files (~2000 lines)

### Comparison with Legacy
- **Legacy monolithic:** 1 file (1565 lines)
- **Modular average:** 100-150 lines per file
- **Total modular:** ~2500 lines (more features, better organized)

---

## 🎓 Learning Path

### Beginner
1. Read [QUICKSTART_MODULAR.md](QUICKSTART_MODULAR.md)
2. Try basic commands
3. Review `lint_config_modular.json`
4. Run `unified_linter.py --list-linters`

### Intermediate
1. Read [README_MODULAR.md](README_MODULAR.md)
2. Study `example_custom_rule.py`
3. Modify a rule configuration
4. Create a simple custom rule

### Advanced
1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Study core framework (`core/*.py`)
3. Examine existing rules
4. Create a custom linter

---

## 🔗 External References

### Verible
- **Location:** `/scratch/tools/external_lib/verible/`
- **Documentation:** https://github.com/chipsalliance/verible
- **Purpose:** SystemVerilog parser and linter

### Python
- **Required:** Python 3.6+
- **Modules:** `verible_verilog_syntax`

### Related Docs
- `docs/coding_standards.md` - Coding standards
- `docs/naturaldocs_patterns.md` - NaturalDocs patterns
- `docs/naturaldocs_keywords_reference.md` - Valid keywords

---

## 📞 Support

### For Questions
1. Check this index for relevant documentation
2. Review appropriate documentation file
3. Study example code
4. Contact BTA DV team

### For Issues
1. Check [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) for known issues
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design rationale
3. Study source code
4. Report to BTA DV team

---

## 🗺️ File Location Map

```
tb_lint/
│
├── 📘 Documentation (You are here!)
│   ├── INDEX.md                    ← Navigation hub
│   ├── QUICKSTART_MODULAR.md       ← Start here
│   ├── README_MODULAR.md           ← Complete guide
│   ├── ARCHITECTURE.md             ← System design
│   ├── MIGRATION_SUMMARY.md        ← Migration info
│   └── README.md                   ← Legacy docs
│
├── ⚙️ Configuration
│   ├── lint_config_modular.json    ← Use this
│   ├── lint_config.json            ← Legacy
│   └── lint_naturaldocs.json       ← Legacy
│
├── 🔧 Core Framework
│   └── core/
│       ├── base_rule.py
│       ├── base_linter.py
│       ├── linter_registry.py
│       ├── config_manager.py
│       └── __init__.py
│
├── 🔌 Linters
│   └── linters/
│       ├── naturaldocs_linter.py
│       ├── verible_linter.py
│       └── __init__.py
│
├── 📋 Rules
│   └── rules/
│       └── naturaldocs/
│           ├── file_header.py
│           ├── include_guards.py
│           ├── package_docs.py
│           ├── class_docs.py
│           ├── function_docs.py
│           ├── task_docs.py
│           ├── constraint_docs.py
│           ├── typedef_docs.py
│           ├── variable_docs.py
│           ├── parameter_docs.py
│           └── __init__.py
│
├── 🚀 Main Scripts
│   ├── unified_linter.py           ← Use this
│   ├── example_custom_rule.py      ← Learn from this
│   ├── naturaldocs_lint.py         ← Legacy
│   ├── verible_lint.py             ← Legacy
│   └── tb_lint.py                  ← Legacy
│
└── 🧪 Test Files
    └── test/
        └── ... (test files)
```

---

## ✅ Checklist: I Want To...

### Use the System
- [ ] Read [QUICKSTART_MODULAR.md](QUICKSTART_MODULAR.md)
- [ ] Run `python3 unified_linter.py --list-linters`
- [ ] Run `python3 unified_linter.py -f files.txt`
- [ ] Review results

### Add a Rule
- [ ] Read "Adding a New Rule" in [README_MODULAR.md](README_MODULAR.md)
- [ ] Study `example_custom_rule.py`
- [ ] Create rule in `rules/naturaldocs/`
- [ ] Register in `__init__.py`
- [ ] Add to linter
- [ ] Configure in `lint_config_modular.json`
- [ ] Test

### Add a Linter
- [ ] Read "Adding a New Linter" in [README_MODULAR.md](README_MODULAR.md)
- [ ] Study `linters/naturaldocs_linter.py`
- [ ] Create linter class
- [ ] Use `@register_linter`
- [ ] Implement required methods
- [ ] Configure in `lint_config_modular.json`
- [ ] Test

### Understand the System
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Study component diagrams
- [ ] Review data flow
- [ ] Examine design patterns
- [ ] Explore source code

---

Copyright (c) 2025 **BTA Design Services**  | October 2025
**Version:** 2.0-modular

**Navigation:** You are at the documentation index. Use the links above to navigate to specific topics.


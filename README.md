# TB_LINT - Modular Linting Framework

**BTA Design Services | DV Environment**  
**Version:** 3.0-hierarchical | **Date:** October 16, 2025

---
## Acknowledgements

This project builds on the work of [Srinivasan Venkataramanan](https://www.linkedin.com/in/svenka3) and AsFigo. Their pioneering efforts in open‑source SystemVerilog linting, particularly the BYOL (“Build Your Own Linter”) philosophy and [SVALint](https://github.com/AsFigo/SVALint), inspired this project.

The syntax and style checks in this linter are built on [Verible](https://github.com/chipsalliance/verible), the open‑source SystemVerilog parsing and linting engine maintained by Google and the CHIPS Alliance community..

---
## License

Released under the MIT License. See [LICENSE](https://github.com/BTA-design-services/tb_lint/blob/main/LICENSE) file for details.

---
## Included Linters

**NaturalDocs Linter**
Validates [NaturalDocs-style](https://en.wikipedia.org/wiki/Natural_Docs) comments in SystemVerilog (modules, classes, functions, tasks, typedefs, parameters, constraints), flagging missing or mismatched tags and descriptions.

**Verible Linter**
Uses [Verible’s](https://chipsalliance.github.io/verible/) AST to enforce SystemVerilog syntax and style (indentation, line length, naming, formatting) with precise rule-based reporting

---

##  Documentation Overview

This index provides quick navigation to all documentation for the modular linting framework.

---
## Getting Started

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
---

## File Organization

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
| `unified_linter.py` | Main orchestrator - shows command lines, TB_LINT summary |
| `run_all_tests.sh` | **One-line script** to run all .sv files in test/ |
| `example/example_custom_rule.py` | Example custom rule implementation |
| `example/example_custom_linter.py` | Example custom linter implementation |
| `verible_verilog_syntax.py` | Verible Python wrapper for AST parsing |

### Configuration

| File | Purpose |
|------|---------|
| `configs/lint_config.json` | **Default** - Root config linking individual linter configs |
| `configs/naturaldocs.json` | Individual NaturalDocs config (supports all rule controls) |
| `configs/verible.json` | Individual Verible configuration (rule enable/disable, severity) |
| `lint_config_modular.json` | Alternative monolithic configuration (all-in-one) - deprecated |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | **This file** - Main documentation index |
| `QUICKSTART.md` | **START HERE** - Quick start guide with hierarchical config |
| `example/README.md` | **Developer guide** - How to add linters and rules |
| `README_MODULAR.md` | Complete documentation (updated for v3.0) |
| `ARCHITECTURE.md` | System architecture and design patterns |

---

## Quick Navigation

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


#### **Understand design decisions**
→ Read "Design Patterns" in [ARCHITECTURE.md](ARCHITECTURE.md)

#### **See examples**
→ Check `example_custom_rule.py`
→ Review rules in `rules/naturaldocs/`

---

## Documentation by Topic

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

---

## Code Reference

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



##  External References

### Verible
- **Location:** https://github.com/chipsalliance/verible
- **Documentation:** https://chipsalliance.github.io/verible/
- **Purpose:** SystemVerilog parser and linter

### NaturalDocs
- **Location:** https://www.naturaldocs.org/
- **Documentation:** https://www.naturaldocs.org/reference/
- **Purpose:** Natural Docs is an open source documentation generator for multiple programming languages

### Python
- **Required:** Python 3.6+
- **Modules:** `verible_verilog_syntax`

---

## Support

### For Questions
1. Check this index for relevant documentation
2. Review appropriate documentation file
3. Study example code
4. Open [Issue](https://github.com/BTA-design-services/tb_lint/issues)


### For Issues
1. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design rationale
2. Study source code
3. Open [Issue](https://github.com/BTA-design-services/tb_lint/issues)

---
---

## Checklist: I Want To...

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

Copyright (c) 2025 **BTA Design Services** | October 16, 2025  
**Version:** 3.0-hierarchical

**Navigation:** You are at the main documentation index. Use the links above to navigate to specific topics.


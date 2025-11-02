API Reference
=============

The unified linting framework exposes a small, well-structured surface area for
automation, customization, and integration. This page collects the public APIs,
their responsibilities, and concrete usage patterns so that you can embed
``tb_lint`` inside Python workflows, drive it from the command line, or extend
it with new linters and rules.

.. contents::
   :local:
   :depth: 2


Unified Linter CLI and Embedding
--------------------------------

``tb_lint.py`` acts as both the canonical command-line entry point and the
home of :class:`tb_lint.UnifiedLinter`, the orchestration class that aggregates
individual linters. Use the CLI when you need an end-to-end lint run from a
shell or CI job.

Typical CLI workflows:

- Run all configured linters over a file list (recommended for large projects).
- Target a single linter when you are iterating on a specific ruleset.
- Emit JSON for machine-readable reporting or dashboards.

.. code-block:: shell

   # Run all linters on the files enumerated in sv_files.txt
   python3 tb_lint.py -f test/sv_files.txt --color

   # Focus on the NaturalDocs linter while writing documentation comments
   python3 tb_lint.py --linter naturaldocs test/good_example.sv

Embedding the orchestrator inside Python is equally straightforward. Construct
the :class:`UnifiedLinter` with configuration options, then call
:meth:`UnifiedLinter.run_all_linters` or :meth:`UnifiedLinter.run_linter`.

.. code-block:: python

   from tb_lint import UnifiedLinter

   files = ["test/good_example.sv", "test/bad_example.sv"]
   unified = UnifiedLinter(config_file="configs/lint_config.json",
                           use_color=True,
                           strict_mode=True)

   results = unified.run_all_linters(files)
   unified.print_final_summary(results)

   # Fail fast in CI when errors or (in strict mode) warnings exist
   exit_code = unified.get_exit_code(results)

.. autoclass:: tb_lint.UnifiedLinter
   :members: __init__, list_linters, run_linter, run_all_linters, print_result,
             print_json, print_command_info, print_final_summary, get_exit_code
   :show-inheritance:


Core Abstractions
-----------------

The :mod:`tb_lint.core` package defines the building blocks that every linter
interacts with: results containers, abstract base classes, configuration
management, and the shared registry.

.. autoclass:: tb_lint.core.base_linter.LinterResult
   :members: add_violation, add_error, error_count, warning_count, info_count
   :show-inheritance:

.. autoclass:: tb_lint.core.base_linter.BaseLinter
   :members: __init__, name, supported_extensions, lint_file, lint_files,
             add_rule, prepare_context
   :show-inheritance:

.. autoclass:: tb_lint.core.base_rule.BaseRule
   :members: __init__, rule_id, description, default_severity, check, enabled,
             severity, create_violation
   :show-inheritance:

.. autoclass:: tb_lint.core.base_rule.RuleViolation
   :members:
   :show-inheritance:

.. autoclass:: tb_lint.core.base_rule.RuleSeverity
   :members:

.. autoclass:: tb_lint.core.config_manager.ConfigManager
   :members: __init__, get_linter_config, is_linter_enabled, get_rule_config,
             is_rule_enabled, get_rule_severity, get_global_setting,
             get_project_info, save_config
   :show-inheritance:

.. autoclass:: tb_lint.core.linter_registry.LinterRegistry
   :members: register, get_linter, get_all_linters, list_linters, is_registered
   :show-inheritance:

.. autofunction:: tb_lint.core.linter_registry.register_linter

.. autofunction:: tb_lint.core.linter_registry.get_registry


Working with hierarchical configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use :class:`ConfigManager` whenever you need to read or author lint
configuration programmatically. The manager understands hierarchical linking
between a root ``lint_config.json`` file and per-linter overrides.

.. code-block:: python

   from tb_lint.core import ConfigManager

   manager = ConfigManager("configs/lint_config_hierarchical.json")

   if manager.is_linter_enabled("naturaldocs"):
       nd_cfg = manager.get_linter_config("naturaldocs")
       header_settings = nd_cfg.get("file_header", {})
       print("Company pattern:", header_settings.get("company_pattern", "<unset>"))


Built-in Linters
----------------

Two linters ship with the framework: an AST-aware NaturalDocs documentation
checker and a Verible wrapper for syntax/style analysis.

.. autoclass:: tb_lint.linters.naturaldocs_linter.NaturalDocsLinter
   :members: __init__, supported_extensions, prepare_context
   :show-inheritance:

.. autoclass:: tb_lint.linters.verible_linter.VeribleLinter
   :members: __init__, supported_extensions, lint_file, prepare_context
   :show-inheritance:


NaturalDocs rule catalog
------------------------

The NaturalDocs linter composes a suite of structural rules. Each rule can be
independently enabled, disabled, or re-severitized via configuration.

.. list-table:: Rule overview
   :widths: 18 30 12 40
   :header-rows: 1

   * - Rule ID
     - Class
     - Default severity
     - Summary
   * - ``[ND_FILE_HDR_MISS]``
     - :class:`rules.naturaldocs.file_header.FileHeaderRule`
     - ERROR
     - Validates that the first lines of a file contain a NaturalDocs ``File:`` header and other configured metadata fields.
   * - ``[ND_COMPANY_MISS]``
     - :class:`rules.naturaldocs.file_header.CompanyFieldRule`
     - WARNING
     - Warns when the ``Company:`` header is missing or does not match the configured regular expression.
   * - ``[ND_AUTHOR_MISS]``
     - :class:`rules.naturaldocs.file_header.AuthorFieldRule`
     - WARNING
     - Warns when the ``Author:`` header is absent or the email does not use the expected domain suffix.
   * - ``[ND_GUARD_MISS]``
     - :class:`rules.naturaldocs.include_guards.IncludeGuardsRule`
     - ERROR
     - Requires consistent ``ifndef``/``define``/``endif`` include guards for non-package files.
   * - ``[ND_GUARD_FMT]``
     - :class:`rules.naturaldocs.include_guards.IncludeGuardFormatRule`
     - ERROR
     - Checks that the ``endif`` terminator carries an explanatory comment.
   * - ``[ND_PKG_MISS]``
     - :class:`rules.naturaldocs.package_docs.PackageDocsRule`
     - ERROR
     - Ensures package declarations have a matching ``Package:`` NaturalDocs block.
   * - ``[ND_CLASS_MISS]``
     - :class:`rules.naturaldocs.class_docs.ClassDocsRule`
     - ERROR
     - Enforces ``Class:`` documentation whose declared name matches the SystemVerilog class.
   * - ``[ND_FUNC_MISS]``
     - :class:`rules.naturaldocs.function_docs.FunctionDocsRule`
     - ERROR
     - Requires ``Function:`` documentation for prototypes and implementations without a documented prototype.
   * - ``[ND_TASK_MISS]``
     - :class:`rules.naturaldocs.task_docs.TaskDocsRule`
     - ERROR
     - Mirrors function requirements for tasks (NaturalDocs uses ``Function:`` labels for tasks).
   * - ``[ND_CONST_MISS]``
     - :class:`rules.naturaldocs.constraint_docs.ConstraintDocsRule`
     - ERROR
     - Ensures constraints are preceded by ``define:`` or ``Variable:`` annotations.
   * - ``[ND_TYPEDEF_MISS]``
     - :class:`rules.naturaldocs.typedef_docs.TypedefDocsRule`
     - WARNING
     - Flags typedefs that are missing ``Typedef:``, ``Type:``, or ``Variable:`` documentation.
   * - ``[ND_VAR_MISS]``
     - :class:`rules.naturaldocs.variable_docs.VariableDocsRule`
     - INFO
     - Tracks member variables that lack a ``Variable:`` block; informational by default.
   * - ``[ND_PARAM_MISS]``
     - :class:`rules.naturaldocs.parameter_docs.ParameterDocsRule`
     - INFO
     - Tracks parameters without ``Constant:``/``Property:`` documentation while allowing exemptions for class headers.


Extending the framework
-----------------------

Creating a custom linter involves three steps: subclass
:class:`BaseLinter`, implement :meth:`BaseLinter.prepare_context`, and
register the linter with :func:`register_linter`. Each rule you add should be a
subclass of :class:`BaseRule` with a unique ``rule_id``.

The sample implementation below demonstrates a style-checking linter shipped in
``example/example_custom_linter.py``. It shows how to register multiple rules
and expose configuration knobs.

.. literalinclude:: ../../example/example_custom_linter.py
   :lines: 158-247
   :caption: ``StyleCheckLinter`` skeleton

To activate a custom linter in the orchestrator:

1. Import the linter so that the :func:`register_linter` decorator runs.
2. Provide a per-linter JSON configuration file.
3. Reference the linter from ``lint_config.json`` or a hierarchical root file.
4. Run ``tb_lint.py --linter <name>`` to validate your integration.

Refer to ``example/example_custom_rule.py`` for a more granular rule authoring
walkthrough.


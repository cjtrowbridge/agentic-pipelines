# tests

This directory owns tests assets.

## Source inventory

- `test_api_primitive.py`: Regression tests for ApiPrimitiveTests.
- `test_architecture.py`: Regression tests for ArchitectureTests.
- `test_bootstrap.py`: Regression tests for BootstrapTests.
- `test_config.py`: Regression tests for ConfigTests.
- `test_contracts.py`: Regression tests for ContractTests.
- `test_documentation.py`: Regression tests for DocumentationTests.
- `test_governance_evidence.py`: Regression tests for GovernanceEvidenceTests.
- `test_host_bootstrap_example.py`: Exercise the non-installable host bootstrap example in an isolated directory.
- `test_ollama_context_aliases.py`: Deterministic checks for Docker Ollama alias provisioning without Ollama.
- `test_package.py`: Regression tests for PackageTests.
- `test_packets.py`: Regression tests for PacketTests.
- `test_playbooks.py`: Regression tests for PlaybookTests.
- `test_prompt_catalog.py`: Regression tests for PromptCatalogTests.
- `test_reference_pipeline.py`: Regression tests for ReferencePipelineTests.
- `test_render_markdown_pdf.py`: Run with the renderer virtual environment; no system fonts or browser required.
- `test_router.py`: Regression tests for RouterTests.
- `test_runner.py`: Regression tests for RunnerTests.
- `test_source_hooks.py`: Exercise staged pre-commit enforcement and preservation of existing hooks.
- `test_source_languages.py`: Exercise language accounting at the 400-line boundary and adversarial literals.
- `test_source_repository.py`: Verify repository source, documentation and staged-snapshot gates.
- `test_state.py`: Regression tests for StateTests.
- `test_vscode_entrypoint_examples.py`: Regression tests for VSCodeEntrypointExampleTests.

- `test_software_build_entrypoints.py`: Verify host software-build VS Code examples and their shared failing gate.

- `test_source_host_contracts.py`: Verify exact root launchers and HTML comments against size, inventory, staged and build gates.

- `test_source_go.py`: Regress Go parser grammar, real compressed statements, raw literals and line accounting.
- `test_source_go_repository.py`: Verify staged Go parsing and retained size/inventory enforcement.
- `test_go_layout_migration.py`: Regress initializer scope, branch/loop behavior, comments, literals and no source execution.

- `test_source_javascript.py`: Regress JS literals, grammar, real violations, physical counts and no inspected-code execution.

- `test_source_dependencies.py`: Verify exact third-party manifest identity while retaining unlisted-source and inventory enforcement.

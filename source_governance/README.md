# source_governance

This directory owns source governance assets.

## Source inventory

- `__init__.py`: Expose deterministic source governance independently of model execution.
- `checker.py`: Combine source inventory, documentation and language validation for a repository.
- `configuration.py`: Load only public code governance from YAML and validate fail-closed invariants.
- `python_source.py`: Validate Python statement layout and count physical code with tokenize and AST.
- `snapshot.py`: Read repository or staged-index data without executing candidate source.
- `text_source.py`: Lex comments and quoted literals for shell, PowerShell and C-style source.

- `html_source.py`: Parse actual HTML comments while preserving embedded source accounting and layout enforcement.

- `go_source.py`: Gate the trusted parser build and validate Go syntax, layout and lexical line accounting.
- `go_layout.py`: Prepare syntax-validated, nonoverlapping Go migration candidates without writing host files.

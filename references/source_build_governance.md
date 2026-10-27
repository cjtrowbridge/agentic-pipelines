# Source and build governance

This is the canonical source-code and software-build policy. Agentic Pipelines
supplies reusable instructions, templates and helpers; the submodule itself is not
a pipeline. Hosts own their environment, pipeline type and executable commands.
Source rules apply to first-party implementation, tooling, examples and tests,
including reusable framework code. Software-build integration applies when the
host actually includes a software-build stage, not merely because it imports this
submodule. A data-analysis pipeline need not invent a software build.
Updating a submodule pointer does not by itself migrate a host's source or builds.

## Source organization

Declare every source root in `api.yaml` under `code.roots`. Roots are repository-root
directories such as `src`, `scripts`, `tests`, or `pipeline_runtime`, not `.` or
individual files. All first-party source must be inside a declared root, except
exact host launchers declared under `code.entrypoints` as described below. Nested
directories are allowed. Tests, examples, launchers, and generated first-party
source are not blanket exceptions. Git submodules are separately governed repos;
ignored dependency installations and build products are not first-party source.

Every directory in each source root must contain `README.md`, briefly describing
its purpose and every directly contained source file. Use the exact backticked
filename followed by a nonempty description (`- `filename.py`: responsibility`).
Keep inventories current when adding, moving, deleting, or decomposing files.

Every source file must start with a language-appropriate multiline explanatory
comment (a module docstring in Python). Explain responsibilities, interfaces,
dependencies, and side effects. A language without block comments uses contiguous
line comments. A shebang, encoding declaration, or mandatory language directive
may precede the header. Presence is checked mechanically; correctness and coverage
are review responsibilities. Do not generate meaningless filler to satisfy the gate.

## Size and composition

Each source file has a maximum of **400 counted physical lines**: 400 passes and
401 fails. Blank lines and recognized comment-only lines, including multiline
comments, do not count. A code line with an inline comment counts. Continuation
lines count. Executable multiline strings (SQL, templates, fixtures) count;
delimiters inside strings cannot turn code into comments. Python true docstrings
are comments for this accounting, not arbitrary triple-quoted strings.

Decompose over-limit files by responsibility and compose explicit interfaces.
Preserve behavior and service/process boundaries. Do not use dynamic source
loading, compressed lines, generated wrappers, or miscellaneous chunks to evade
the limit. Each new component must have a coherent name, header, and README entry.

## One action per line

Use one logical statement per line. No semicolon-separated actions, chained
assignments, assignment expressions, or assignments embedded in comparisons or
conditions. Put a branch/loop header and its body on separate lines. Ordinary
assignment of a function's result and tuple unpacking are single statements.
For-loop grammar separators are not separate actions. Avoid nested side effects
and expressions that hide multiple responsibilities even when syntactically legal.
Language-specific checks establish syntax properties only; review establishes
whether a statement is appropriately simple. Unsupported language adapters must
fail explicitly, never silently certify source they cannot parse.

## Configuration and canonical check

Track the public `code` mapping in `api.sample.yaml`; copy the same mapping into
ignored local `api.yaml`. The checker uses the tracked mapping for reproducible local checks and compares
an existing local mapping against it. A missing or different local mapping fails;
it must not weaken policy. It never reads or prints endpoint credentials and
needs no model service. Configure `comment_pattern` for each extension/adapter.
Only parser-recognized comments matching that pattern are excluded. A pattern
that matches ordinary code cannot remove code lines from the count.

Run `python agentic-pipelines/scripts/check_source_governance.py --repo-root .`
from a host; omit the submodule prefix within the framework. The recursive check
reports every failure and exits nonzero. Use `--staged` for the Git index. Staged
checks read staged data using the trusted installed checker; they never execute
staged scripts or materialize staged symlinks. Fix violations; do not add a bypass.

## Mandatory commit and software-build gates

Run the source check before commits. Install the reusable pre-commit integration
with `python agentic-pipelines/scripts/install_source_governance_hook.py --repo-root .`.
It checks staged content and preserves existing hooks; host bootstrap owns its
installation/check. Local hooks are bypassable, so agents must also obey the policy.

**Every software-build pipeline created or maintained using this framework must
include the source check and fail to build if it fails.** This covers each actual
software compile, bundle, package, release or container build in the host's chosen
environment. A data transformation, analysis or document render is not automatically
a software build. Do not invent a build stage for a pipeline that has none.

Within a software-build pipeline, bootstrap declared prerequisites, check source,
then invoke the host's build command only on success. Recheck generated first-party
source before compiling it. Preserve nonzero statuses and controlled interruption;
never make the source gate advisory or run it in parallel with the protected build.
Use `python agentic-pipelines/scripts/governed_build.py --repo-root . -- COMMAND ARG...`
or an equivalent host-owned call to the canonical checker that propagates failure.
The reusable wrapper supplies the gate; the host selects all tools and arguments.

## Host VS Code integration

Each host-declared pipeline action must appear in host `.vscode/tasks.json`.
The canonical ordinary pipeline must also be exposed in `.vscode/launch.json`.
Both enter the same host-owned native prerequisite/bootstrap path and execute the
operation once. When that operation includes a software build, both paths must
reach the failing source gate before that build. A separate source-check task is
useful but is not sufficient: the build itself must depend on a passing check.
For a mixed pipeline, gate its software-build stage without inventing software
build requirements for unrelated analysis stages.

Use `playbooks/how_to_set_up_pipeline_entrypoints_in_vscode.md` and adapt
`templates/vscode/software-build.*` only when the host needs software building.
These are examples, not a pipeline installed in the framework or a replacement
for existing host files. Preserve the host's selected canonical operation and
merge its VS Code configuration; do not overwrite other tasks or launch entries.

No GitHub Actions integration, hosted workflow, required remote check or branch
protection is supplied or required by this policy. Do not create them as a side
effect of building a host pipeline. The source checker validates source, not an
invented workflow registry or the semantics of arbitrary build scripts.

Adoption includes applicable source decomposition, documentation, configuration,
hook setup and the host's actual software-build entrypoints. Verify with a local
regression that invalid source prevents build execution through the shared path,
and that valid source permits it while preserving the build's status. Record exact
remaining host work; a pointer refresh alone does not establish compliance.

## Exact host entrypoint contracts and HTML

A stable root launcher may be declared by exact filename under
`code.entrypoints`, for example:

```yaml
entrypoints:
  bootstrap.sh:
    purpose: Stable operator dispatcher
    delegate: scripts/bootstrap.sh
```

Only individual root `.sh`, `.ps1` or `.py` files are supported; no globs,
path escapes or blanket root exemptions. The delegate must exist under a
declared source root with a configured language. The declaration records
the interface; review must verify actual delegation, not infer it from a
filename. The launcher still receives ordinary language, header, 400-line
and layout checks and must be inventoried in root `README.md`. The target
receives its normal checks. Undeclared root source remains an error. Local
configuration parity and staged checking include the entire contract.

Configure `.html` with `adapter: html` and `comment_pattern: '<!--[\s\S]*?-->'`.
Only parser-recognized HTML comments matching that pattern are excluded;
comment-like strings inside attributes/script/style count as source. A
multiline responsibility comment may follow the HTML doctype. Embedded
script/style bytes count conservatively and receive existing C-style layout
checks. Inline handlers, executable URLs and inline style attributes must
move to governed source; malformed comments/unclosed embedded content fail.
This is source governance, not an HTML validator or browser security audit.

## Go source

Use `adapter: go` and `comment_pattern: '(?://[^\n]*|(?s:/\*.*?\*/))'`
for Go hosts. The installed Go standard parser distinguishes composite data
literals from executable statement blocks. For-clause separators and type-switch
bindings are grammar; inline function/block bodies and multiple statements on a
line still fail. An if initializer plus condition remains separate actions under
this policy. Raw strings count as executable data, and source line directives
cannot alter physical line accounting. Syntax errors fail closed.

The adapter compiles only its trusted framework helper, once per checker process,
after the framework's own canonical source gate passes. The helper deliberately
uses the conservative C-style adapter in framework configuration to avoid a
recursive parser build. Installed local Go is required; automatic toolchain
fetching and host workspace selection are disabled. No inspected source is
compiled or executed. Missing toolchains and failed prerequisite checks block.

## Authorized Go layout migration

`source_governance.go_layout.candidate(text)` prepares an explicit migration
candidate without writing or executing inspected source. Its trusted helper
is source-gated before compilation. Header initializers move into an enclosing
lexical block spanning the entire if/else or switch; for-clause grammar and
type-switch bindings remain intact. Statement whitespace edits use physical
AST positions, not regex substitutions over literals. Overlaps and invalid
syntax fail closed. Comment-bearing headers require manual review.

Use only under an approved host source-migration task. Inspect candidates and
retain before/after evidence before adoption; the ordinary checker never
automatically fixes files. Passing source checks are not runtime regression
proof. Preserve the host's full build/test and publication requirements.

# Release Readiness

## Verified implementation

- `AGENTS.md` is the sole root instruction file and routes tasks to concise playbooks.
- Pipeline design is deterministic-first; every configured LLM stage requires a justification, minimal declared inputs, strict output schema, finite attempts, evidence, and fail-closed routing.
- Prompt lint validates 24 prompt contracts, substantive schemas, identities, roles, and authority boundaries.
- Schema-v2 definitions connect prompt identity and content hashes to execution and requeue entities after a contract change.
- The shared API adapter is the only provider HTTP boundary and captures redacted success/failure threads.
- The runner implements snapshots, byte bounds, SQLite migrations, attempts, locks, leases, stale recovery, deterministic validation, optional semantic stages, repair, adjudication, quarantine, safe promotion, and hash-checked rollback.
- Reports contain deterministic cohorts and performance metrics. Optional LLM analysis is nested as `advisory_only`; retry remains an explicit cohort command.
- `examples/markdown_repair/` is a complete staged package validated and exercised with a fake provider.

## Verification commands

```powershell
python -m compileall -q pipeline_runtime scripts tests
python scripts/lint_prompts.py
python scripts/validate_pipeline_package.py examples/markdown_repair
python -m unittest discover -s tests -v
python scripts/regenerate_plan_indexes.py --check
```

The 20-test automated suite currently covers strict prompt inputs/outputs, redaction, remote-endpoint opt-in, architecture boundaries, package validation, progressive playbook structure, Markdown accept/repair/quarantine/analysis/retry behavior, prompt-change invalidation, source-change protection, promotion rollback, lock exclusion, and stale-lease recovery. CLI inspection also confirms a missing `api.yaml` fails immediately with instructions to copy the sample and supply local endpoint/model credentials.

## Remaining release gates

- Run the bounded reference fixtures against the operator's actual local Ollama model and measure schema compliance and semantic false accepts/rejects.
- Choose and implement explicit thread/artifact retention, optional compression, cleanup audit, and evidence-integrity policy; the current safe default retains evidence.
- Add one end-to-end process-interruption/resume case and one configured adjudicator case beyond unit-level state recovery.
- Apply one reviewed remediation to a failing cohort, rerun its representative sample, and demonstrate improvement without golden-set regression.
- Review and create the repository's first baseline commit; all current files remain untracked until the user approves that Git checkpoint.

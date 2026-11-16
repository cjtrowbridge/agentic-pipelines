# References

Load a reference only when a selected playbook names it.

- `prompt_authoring.md` owns the reusable rules for deciding whether an LLM is necessary and writing a terse, bounded prompt.
- `deterministic_and_semantic_authority.md` owns the epistemic boundary between exact computation, semantic judgment, heuristics, and human decisions.
- `run_evidence_and_continuous_improvement.md` owns the rationale and durable evidence contract for reconstructing runs and eliminating avoidable retry loops.

- `ollama_performance_optimizations.md` owns the Ollama cache-effectiveness metric contract, structural prompt/serialization optimizations, telemetry field requirements, controlled benchmark suite, and structural diagnostic classification. It does not own VS Code Chat inference-timeout or Q8 KV-cache configuration; those remain in `vscode_ollama_configuration.md`.

- `deliverable_driven_simplicity.md` owns outcome-based planning, justified implementation mechanisms and bounded review-driven improvement.

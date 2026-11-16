# Playbook: Optimize Ollama Cache and Performance

## Use when

Diagnosing or improving Ollama prefix-cache reuse, prefill throughput, KV-cache effectiveness, or disk-cache behavior across one host or a fleet. Do not use this playbook for VS Code Chat inference-timeout tuning; use `how_to_optimize_vscode_and_ollama.md`.

## Load

`references/ollama_performance_optimizations.md` (sole authority for depth), the host's Ollama version, model digest and quantization, KV-cache configuration, MTP settings, runner lifecycle, and any existing telemetry. Preserve host-owned credentials and configuration.

## Required behavior

Distinguish theoretical reusable prefix from actual reused tokens; never convert a missing `prompt_eval_cached_count` to zero. Apply structural optimizations in reference order, run each optimization's verification test, and record pass/fail evidence. Record remaining blockers without claiming unsupported success.

## Procedure

1. Read the reference in full; it owns metric definitions, telemetry fields, fingerprinting rules, diagnostic classification, and the benchmark suite.
2. Identify the actual host, provider version, model, KV configuration, and workload before changing anything.
3. Apply the structural optimizations in reference order. Preserve host settings; never overwrite host-owned configuration.
4. Run each optimization's verification test and record the result. Do not report a pass without the referenced evidence.
5. Report the result, the exact remaining blocker, and whether the gap is a software defect, configuration mismatch, or normal memory pressure.

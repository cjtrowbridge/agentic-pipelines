# Playbook: Create Ollama Context Aliases

## Use when

A host needs context variants in a local Docker Ollama instance.

## Load

The host's model, container, local inference settings, measured stage budgets, `references/docker_ollama_context_alias_contract.md`, and `playbooks/how_to_create_and_maintain_host_bootstrap.md`. Load `playbooks/how_to_configure_local_inference.md` when connecting the pipeline. Do not display credentials.

## Procedure

1. Confirm the exact base model, published context limit, Docker container, and host memory. Record a lower operating cap if the full model context cannot run.
2. Measure each stage's complete session plus completion reserve. Choose the smallest context preset that fits; retain separate declared `num_ctx` and `num_predict` values.
3. Use aliases named `[hostname]-[context]-[model name]`, for example `cj-desktop-96k-qwen3.8:27b`. Follow the linked reference for hostname normalization, 1k/4k/64k/96k/upper-preset examples, context units, conflict behavior, and runtime `num_ctx` precedence.
4. Add `scripts/ensure_ollama_context_aliases.py` to the host's selected versioned bootstrap. Pass the base model and each wanted context; use `--check` in its read-only probe and omit it in its repair. For example:

   ```text
   python agentic-pipelines/scripts/ensure_ollama_context_aliases.py --container ollama --model qwen3.8:27b --context 1k --context 4k --context 96k --check
   ```

5. Run the host bootstrap and verify each alias, model offloading, and representative latency. A missing base or conflicting existing alias requires an explicit host decision; the script never pulls or replaces it. Align the selected alias with the request-level `num_ctx`.

## Output and stop conditions

Record the base identity, selected contexts, script arguments, check/apply results, and stage mapping. Stop on unavailable Docker/Ollama, unsupported context, unverifiable alias, or request budget that exceeds the effective context.

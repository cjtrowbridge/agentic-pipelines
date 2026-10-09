# Reference: Docker Ollama Context Alias Contract

Naming, sizing, and provisioning details for `playbooks/how_to_create_ollama_context_aliases.md`. The host owns the selected model, contexts, container, and measured stage budgets. A host-declared tier set, naming grammar, base allowlist, or bootstrap generator overrides these framework defaults; use that existing scheme exclusively, never provision a competing alias set. For another Ollama-compatible provider, use its supported configuration mechanism instead. Ollama documents its [model API](https://docs.ollama.com/api/create), [model details](https://docs.ollama.com/api-reference/show-model-details), and [context length](https://docs.ollama.com/context-length).

Context aliases must preserve the complete selected model definition. For MTP models such as Qwen3.8, inspect every model/draft component exposed by the installed backend; do not require exactly one FROM entry or validate only the first weight source. Some versions expose multiple FROM entries, while others expose FROM plus DRAFT. Create the alias from the existing named model so its complete definition is inherited, override only the intended context parameter, and verify all source components and the existing MTP parameters remain intact. Do not reconstruct it from one blob or disable MTP to make verification pass.

## Procedure

1. Identify the exact base model tag and local Docker Ollama container. Check the model's current published context limit. Record the model tag or digest used, the limit's source, available memory, and the host's chosen largest operating context. If the base is missing, add its authorized acquisition to the host bootstrap; the alias script does not pull models. A model's published limit, Ollama's hardware-dependent default allocation, and a host's chosen cap are different values.
2. Measure each stage's largest complete assembled request, retained session context, and completion reserve. Include template and tool overhead. Select the smallest alias whose `num_ctx` fits that measured total. Do not select a 1k or 4k alias just because the individual new input is short. Keep the stage's declared `num_ctx` and `num_predict` explicit.
3. When adopting framework defaults, use the alias name `[hostname]-[context]-[model name]`. The script lowercases the machine hostname and replaces runs of non-alphanumeric characters with `-`; it preserves the selected model's Ollama name and tag. For hostname `cj-desktop` and base `qwen3.8:27b`, the names are:

   | Context argument | Alias | `num_ctx` |
   | --- | --- | ---: |
   | `1k` | `cj-desktop-1k-qwen3.8:27b` | 1024 |
   | `4k` | `cj-desktop-4k-qwen3.8:27b` | 4096 |
   | `16k` | `cj-desktop-16k-qwen3.8:27b` | 16384 |
   | `32k` | `cj-desktop-32k-qwen3.8:27b` | 32768 |
   | `64k` | `cj-desktop-64k-qwen3.8:27b` | 65536 |
   | `96k` | `cj-desktop-96k-qwen3.8:27b` | 98304 |
   | `256k` | `cj-desktop-256k-qwen3.8:27b` | 262144 |

   `k` means 1024 tokens. An exact token count divisible by 1024 normalizes to the same `k` label; other counts use a `t` suffix. As of 2026-10-05, [Ollama lists `qwen3.8:27b`](https://ollama.com/library/qwen3.8/tags) at 256K. Around 232K can be a host operating cap or input budget after reserving completion space; it is not the published model maximum. The script checks the selected contexts against the base model's inspected limit. Choose a lower largest context if host hardware cannot support 256K.
4. For hosts adopting framework defaults, add the script to the host's selected versioned bootstrap inventory. Use the same arguments for the read-only probe and repair; only the probe adds `--check`. For example, from a host repository with this framework at `./agentic-pipelines`:

   ```text
   python agentic-pipelines/scripts/ensure_ollama_context_aliases.py --container ollama --model qwen3.8:27b --context 1k --context 4k --context 16k --context 32k --context 64k --context 96k --context 256k --check
   python agentic-pipelines/scripts/ensure_ollama_context_aliases.py --container ollama --model qwen3.8:27b --context 1k --context 4k --context 16k --context 32k --context 64k --context 96k --context 256k
   ```

   The first command is the bootstrap probe; the second is its repair, invoked only through `scripts/bootstrap.py`. The script requires a running local Docker container with port 11434 published on a usable local host port. It creates only missing aliases through the Ollama API, then verifies them. An existing alias with a different context or source fails visibly and is never overwritten. A missing base, unreachable container, or context above the model limit is also a failure. Pin or record the base model version so a later base update does not silently change the meaning of an alias.
5. Run a bounded, non-sensitive request through each alias actually used by the pipeline. Check `ollama ps` while it is loaded to confirm the allocated context and model offloading. Record resource use and representative latency on the host before claiming a speed gain. Larger contexts require more memory; switching among presets can also incur model load costs.
6. Configure each host stage to use the intended alias **and** a matching declared request-level `num_ctx`. Ollama API requests may supply runtime options. This framework's API adapter sends `num_ctx` from `api.yaml` or an explicit per-request override; that value governs the call even if the alias Modelfile declares another value. The reference runner currently uses one configured model and generation setting for its stages, so stage-specific alias selection requires a host runner that implements it or separate configurations/runs. Reject a configuration that exceeds its selected preset or the verified model/hardware limit. Keep the completion limit `num_predict` separate.

## Output

- Reproducible host-owned script arguments and recorded base model identity.
- A stage-to-alias map with measured request, completion reserve, declared `num_ctx`, and verification result.
- Host-local evidence of loaded context and any measured resource or latency benefit, without credentials or protected inputs.

## Stop conditions

The base model or published limit cannot be verified; a chosen preset exceeds the model or available memory; the alias cannot load; or a stage's assembled request plus completion reserve does not fit its effective request-level context.

# Playbook: Optimize VS Code and Ollama

## Use when

Setting up or tuning VS Code Chat with a local Ollama model, especially when repeated requests include a large system/tool prefix. This playbook mandates Q8 KV caching and 45-minute inference timeouts.

## Load

Host bootstrap, Ollama deployment configuration, installed VS Code provider/version, effective editor settings, selected model/context alias and measured request budgets. Use the host-bootstrap and Ollama context-alias playbooks for implementation.

## Required settings

Ollama must explicitly use Q8 KV cache for both the target model and every active MTP/draft context. The target setting alone does not configure the separate draft cache. For backends exposing the following verified draft controls:

```yaml
environment:
  OLLAMA_KV_CACHE_TYPE: q8_0
```

Flash Attention is mandatory only where appropriate: the selected hardware and backend must support it and be able to compile the FA kernel, or use a verified prebuilt kernel. On unsupported platforms, leave Flash Attention disabled, record the incompatibility, and continue verifying the remaining requirements. Lack of Flash Attention alone is not a stop condition and does not prove Q8 is unsupported. Add it to the same environment block on supported platforms:

```yaml
  OLLAMA_FLASH_ATTENTION: "1"
  LLAMA_ARG_SPEC_DRAFT_CACHE_TYPE_K: q8_0
  LLAMA_ARG_SPEC_DRAFT_CACHE_TYPE_V: q8_0
```

Persist these settings in the host-owned server/container bootstrap configuration. Inspect the installed backend's help for supported draft controls; other versions may require different controls. Verify the running worker environment and the separate target and MTP/draft allocation logs each show `q8_0` for both K and V caches. Do not infer draft quantization from target flags or environment alone, and preserve MTP — test successful inference, draft acceptance and generation latency rather than disabling MTP or a draft cache to pass. A model's weight quantization or an alias name does not establish its KV cache type. A restart alone does not update an existing Docker container's environment; recreate it through the approved host bootstrap. Do not silently accept an f16 target or draft fallback. [Ollama KV cache documentation](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache)

VS Code's Ollama inference timeout must be **45 minutes**, equivalent to **2700 seconds / 2700000 milliseconds**. For the official Ollama extension, merge this entry into the appropriate host-owned VS Code settings scope:

```json
{
  "ollama.inferenceTimeoutMinutes": 45
}
```

Verify the installed extension exposes this key and that the effective value is 45, including workspace/remote overrides. For other providers, use their documented equivalent in the correct units. Do not invent a universal VS Code timeout key. In versions without configurable inference timeouts, record the incompatibility and use an approved provider/version that supports the requirement. The official extension describes this setting as the wait for inference to begin; it is not a guaranteed total-generation deadline. Check any proxy, HTTP header/body or client timeout that could abort inference sooner, and give those inference waits the same 45-minute budget. Keep discovery/health probes bounded separately and preserve immediate user cancellation. [Official extension setting](https://github.com/ollama/ollama-vscode/blob/main/package.json), [timeout conversion](https://github.com/ollama/ollama-vscode/blob/main/src/inferenceTimeout.ts)

The required outcomes are Q8 KV caching and 45-minute inference waits. Their implementation must follow the actual project, machine, provider version and model format; this playbook does not prescribe one universal bootstrap or deployment layout.

Q8 target and active draft K/V cache verification remains mandatory regardless
of Flash Attention eligibility. If the actual backend cannot meet that cache
requirement without Flash Attention, report the demonstrated Q8 incompatibility
and stop for that reason; do not infer it solely from GPU architecture.

Context aliases must preserve the complete selected model definition. For MTP models such as Qwen3.8, inspect every model/draft component exposed by the installed backend; do not require exactly one FROM entry or validate only the first weight source. Some versions expose multiple FROM entries, while others expose FROM plus DRAFT. Create the alias from the existing named model so its complete definition is inherited, override only the intended context parameter, and verify all source components and the existing MTP parameters remain intact. Do not reconstruct it from one blob or disable MTP to make verification pass.

## Procedure

1. Record model identity, effective context, reasoning setting, GPU offload, provider version and timeout settings. Size context for the full system/tool prompt, conversation and completion reserve. The operator reports roughly 20K tokens of repeated VS Code system prompt per request in the target workflow; measure the actual installed client's request rather than assuming all VS Code configurations have that size.
2. Encode Q8/Flash Attention probes and authorized repairs in the host bootstrap. Configure and verify the 45-minute editor timeout. Apply through the host entrypoint; keep credentials and full prompts out of logs.
3. Preserve a warm runner between interactive requests so matching prefix state can be reused. Avoid unnecessary model/alias switches, context-size changes, reloads and prompt-prefix changes. Inspect request-level `keep_alive`: zero unloads the runner after each response and prevents reuse across requests. Configure a host-approved nonzero residency interval suitable for the chat session; request-level values override server defaults. This interactive optimization does not authorize changing a shared runtime's existing immediate-release or scheduling policy. [Ollama residency controls](https://docs.ollama.com/faq#how-do-i-keep-a-model-loaded-in-memory-or-make-it-unload-immediately)
4. Run an authorized, sanitized cold request, followed by a warm follow-up with the same system/tool prefix, model and context. Compare time to first token, `load_duration`, `prompt_eval_count` and `prompt_eval_duration`; inspect backend cache/prefix-reuse logs where available. Record actual reuse and resource use. Q8 reduces cache memory; it does not by itself guarantee prefix reuse or faster generation. Matching cached prefixes can substantially reduce repeated prefill work, but claim a speedup only from the measured comparison.
5. Verify the effective timeout and its units, that no shorter transport timeout masks it, and that cancellation still stops inference. Use controlled fixtures where available rather than waiting 45 minutes solely to test the setting. Save a short configuration/measurement report without source or prompt payloads.

## Output and stop conditions

Record separate target and MTP/draft Q8 K/V runner evidence, effective 45-minute provider/transport settings, model/context/residency configuration, draft acceptance and cold-versus-warm timings. Configuration-only verification is not a live performance result.

Stop and report demonstrated unsupported Q8 caching, an unconfigurable shorter inference timeout, insufficient context/memory, or a residency change outside host authority. Unsupported Flash Attention alone is not a blocker; leave it disabled and continue. Do not silently downgrade Q8 caching or 45-minute inference waits.

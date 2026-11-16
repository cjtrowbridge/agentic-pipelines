# Reference: Ollama Cache and Performance Optimizations

Load this reference when `playbooks/how_to_optimize_ollama_performance.md` names it. This reference is the sole authority for depth. The playbook remains the thin router.

This reference is advisory: it defines the metric contract, the structural optimizations, the verification tests, and the diagnostic classification. It does not prescribe a fleet deployment layout, a specific proxy implementation, or a specific monitoring stack. Hosts own their deployment; this reference names what the host's telemetry must record and how to verify each optimization.

## Scope boundary

- `playbooks/how_to_optimize_vscode_and_ollama.md` owns VS Code Chat inference timeouts and Q8 KV-cache requirements for that path.
- This reference owns cache-effectiveness measurement, structural prompt/serialization optimizations, telemetry field contract, metric formulas, and the controlled benchmark suite.
- `references/vscode_ollama_configuration.md` owns the configuration examples and evidence requirements for the VS Code path.

## 1. What maximally effective caching means

Maximum reuse is not 100% of the request. It is 100% of the eligible reusable prefix, subject to implementation constraints.

Three metrics, computed separately:

| Metric | Definition | Why it matters |
| --- | --- | --- |
| Theoretical reusable prefix | Longest identical token prefix between the current request and an eligible previous request | Establishes the best possible reuse |
| Actual reused tokens | Tokens whose computation was actually skipped using cached state | Measures implementation effectiveness |
| Cache efficiency | Actual reused ÷ theoretically reusable | Identifies avoidable cache misses |

Example: a 21,000-token prompt with a 20,000-token reusable prefix, where Ollama reuses only 8,000 tokens, has cache efficiency 40%. That triggers investigation.

Crucially, telemetry must distinguish:

- Theoretical reuse (best possible with unlimited cache)
- Reuse possible with the actual cache capacity and eviction policy
- Actual reuse

Otherwise it incorrectly classifies normal memory pressure as a software defect.

## 2. Telemetry field contract

The host's telemetry must record, per request:

| Category | Required fields |
| --- | --- |
| Request | Timestamp, request ID, client, session, endpoint |
| Host | Machine ID, Ollama version, runner version |
| Model | Model digest, quantization, architecture |
| Configuration | Context length, KV type, MTP settings, parallelism |
| Cache | Total tokens, cached tokens, uncached tokens |
| Performance | Prefill duration, generation duration, first-token latency |
| Prefix | Stable hashes of prompt segments, longest matching prefix |
| Lifecycle | Model loads, unloads, runner restarts, cache resets |
| System | GPU memory, utilization, CPU, RAM, disk I/O |
| Scheduling | Queue duration, concurrent requests, runner identity |

Without the prefix fields, the host knows a cache miss occurred but not necessarily why.

### Prompt fingerprints

The telemetry proxy must produce keyed hashes of the canonical token sequence, preferably after the model's chat template has been applied.

Record fingerprints at token positions:

```
1, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768
```

Compare each request with previously seen requests for the same model and compatible runtime configuration. The analyzer determines whether the first divergence occurred near token 1, token 512, or token 16,384.

Also record message-boundary and segment fingerprints for:

- System instructions
- Tool definitions
- Repository instructions
- Conversation history
- Current query

**Implementation limitation:** hashing raw JSON or chat-message text is useful for diagnosis, but it does not prove token-level equality. A definitive comparison requires the actual serialized prompt and model tokenizer. The proxy may not know every internal formatting detail, so the host must label estimates separately from verified token-level comparisons.

**Privacy:** use keyed HMAC fingerprints rather than storing plaintext prompts by default. This protects potentially sensitive repository content and client documents.

## 3. Structural optimizations

Apply in reference order. Each entry has a `Verify` test that the host must run and record.

### O1: Dynamic content after static prefix

**What:** timestamps, request IDs, session IDs, and other changing metadata must appear after the stable system instructions and tool definitions, not before them.

**Why:** a changing token near the beginning of the prompt destroys nearly all prefix reuse, even when the remaining 20,000+ tokens are identical.

**Apply:** inspect the prompt assembly order in the host's client (VS Code extension, Open WebUI, custom client, or pipeline). Move dynamic segments to the end of the message list. Preserve the stable instructions and tool definitions as the first segments.

**Verify (T1):** send the same long prompt twice with only the leading timestamp differing. The first divergence must occur within the opening segment; the analyzer must report the first divergence position and confirm that the 20,000+ subsequent tokens are identical but not reusable through ordinary prefix caching. Move the timestamp after the stable instructions and re-run; the first divergence must now occur after the stable prefix, and cache efficiency must rise to near 100% of the eligible prefix.

### O2: Stable tool definitions and serialization

**What:** tool definitions and message serialization must be byte-stable across requests that are semantically equivalent.

**Why:** changing tool ordering or schema formatting produces different token fingerprints for equivalent messages, defeating prefix reuse.

**Apply:** canonicalize tool ordering (e.g., by name) and schema key order. Use the same serializer for every request. Do not reorder or reformat tools between requests.

**Verify (T2):** send two semantically equivalent prompts that differ only in tool ordering. The analyzer must report the same segment fingerprints for the tool segment after canonicalization, and cache efficiency must not drop due to tool ordering alone.

### O3: Message serialization stability

**What:** equivalent messages must yield identical token fingerprints.

**Why:** template or serialization drift (e.g., a library upgrade that changes whitespace or role names) silently breaks prefix reuse.

**Apply:** pin the chat-template serializer version in the host's dependency manifest. Do not upgrade the serializer between comparable benchmark runs.

**Verify (T3):** send the same message list twice through the same serializer version. Token fingerprints must match at every sampled position. Upgrade the serializer and re-run; record the fingerprint delta as evidence of the serializer change, not as a cache defect.

### O4: Context truncation policy

**What:** prompt length must stay below `num_ctx` with sufficient headroom for the completion budget.

**Why:** when prompt length approaches the context limit, early tokens are dropped, destroying prefix reuse.

**Apply:** measure the maximum request size (static template + assembled request) and set `num_ctx` to the measured maximum plus the completion budget. Do not set `num_ctx` to a value that forces truncation of the stable prefix.

**Verify (T4):** send prompts at 1k, 4k, 8k, 16k, 32k, and 64k tokens (where supported). Record the first divergence position for each. Cache efficiency must not degrade as prompt length approaches `num_ctx`; if it does, the truncation policy is dropping early tokens.

### O5: KV-cache capacity and concurrency

**What:** the KV-cache capacity must be sufficient for the concurrent workload, and the eviction policy must not drop the stable prefix under normal load.

**Why:** identical prompts with low reuse after competing requests indicate eviction, not a prompt defect.

**Apply:** measure the KV-cache capacity in tokens and compare it to the sum of the stable prefixes of all concurrent sessions. Increase capacity or reduce concurrency if the stable prefix is being evicted.

**Verify (T5):** interleave requests from several clients with a shared 20k-token stable prefix. Record the actual reused tokens for each request. If reuse drops below the established baseline under concurrency, the capacity or eviction policy is the cause; increase capacity or reduce concurrency and re-run.

### O6: Runner residency and session affinity

**What:** the model runner must remain resident for the duration of a session, and identical prompts must be routed to the same runner.

**Why:** cache misses correlated with runner restarts or reassignment indicate a scheduling defect, not a prompt defect.

**Apply:** enable runner residency (do not unload the model between requests in a session). Use session affinity so identical prompts alternate to the same runner.

**Verify (T6):** send a long prompt, restart the model runner, and repeat the prompt. Record whether reuse survives. It must survive if disk-backed prompt-state caching is enabled and supported; if it does not, the runner is not persisting state. Then interleave two sessions and verify that identical prompts alternate to the same runner; if they alternate between runners, enable session affinity.

### O7: Model and configuration matching

**What:** the same text must use the same model digest and KV configuration across comparable requests.

**Why:** identical prompts with different model digests or KV configurations cannot share a cache pool.

**Apply:** do not mix model digests or KV configurations within a cache pool. Normalize the model digest and KV type for comparable benchmark runs.

**Verify (T7):** send the same prompt with two different KV configurations (e.g., `q8_0` and `f16`). Record the cache efficiency for each. The two runs must use separate cache pools; a drop in efficiency is expected and is not a defect. Re-run with the same KV configuration and verify that efficiency matches the baseline.

### O8: Disk-backed prompt-state caching

**What:** the host must distinguish in-memory KV reuse from disk-backed prompt-state persistence.

**Why:** a repeated request that is faster after a container restart may be faster because of retained GPU KV state, warm model weights, filesystem page cache, or reduced model-loading overhead. It is not proof of successful disk-cache restoration.

**Apply:** verify that the Ollama runner actually supports `--prompt-cache` (or the equivalent) and that the cache file is written and restored. Do not infer successful disk-cache restoration simply because a repeated request is faster.

**Verify (T8):** send a long prompt, stop the Ollama container, restart it, and repeat the prompt. Record the actual reused tokens and the cache read/write duration. If the runner supports disk-backed prompt-state caching, the cache file identifier must be present and the restored token count must match the original. If the runner does not support it, record the incompatibility; the speedup is from a different cause and must be classified separately.

## 4. Metric formulas

For recent Ollama versions that expose `prompt_eval_cached_count`:

```python
total = response["prompt_eval_count"]
cached = response.get("prompt_eval_cached_count")

if cached is not None:
    uncached = total - cached
    hit_rate = cached / total if total else None
    duration = response["prompt_eval_duration"] / 1e9
    prefill_tps = (
        uncached / duration
        if duration > 0 else None
    )
else:
    # Unknown cache reuse, not necessarily zero.
    uncached = None
    hit_rate = None
    prefill_tps = None
```

**Critical:** recent Ollama releases measure `prompt_eval_duration` against uncached prompt evaluation. Dividing the total prompt tokens by that duration can dramatically overstate prefill throughput when caching is effective. Always divide `uncached` by `prompt_eval_duration` for prefill throughput.

**Critical:** `prompt_eval_cached_count` absence is not zero. The Python client has had reported issues dropping this field from typed responses even when the server returns it. Capture the raw HTTP response until the installed client version is verified.

Additional metrics to store:

- **Time to first token:** measured by the proxy, including queueing, model loading, cache restoration, and prefill.
- **Cold prefill throughput:** uncached tokens per second with the cache deliberately cold.
- **Warm request latency:** time to first token with a verified reusable prefix.
- **Time saved:** estimated by comparing matched cold and warm requests, not by multiplying tokens by a nominal throughput.
- **Cache effectiveness:** actual cached tokens divided by the verified eligible prefix.
- **Cache persistence:** whether reuse survives runner restarts or model unloads.

For MTP, maintain separate measurements for draft-token generation, acceptance rate, target-model verification, and any MTP-specific cache behavior. Standard Ollama API metrics alone may not expose those internal details; additional runner instrumentation may be necessary.

## 5. Controlled benchmark suite

Run after an Ollama upgrade, model change, or KV-cache configuration change. Repeat each test several times and record variance. Compare machines only when the model, quantization, context configuration, and workload are equivalent.

| Test | Procedure | Expected behavior |
| --- | --- | --- |
| Identical prompt | Send the same long prompt twice | Near-maximal eligible prefix reuse |
| Different suffix | Preserve 20k-token prefix; change final query | Reuse approximately the common prefix |
| Early divergence | Change one token near the beginning | Sharp reduction in ordinary prefix reuse |
| Late divergence | Change one token near the end | Most of the prefix remains reusable |
| Concurrent sessions | Interleave requests from several clients | Quantify contention and eviction |
| Runner restart | Restart model runner and repeat | Determine whether state survives |
| Container restart | Restart Ollama container | Test persistence rather than assuming it |
| KV quantization | Repeat using supported KV types | Compare memory, reuse, latency, and quality |
| MTP enabled/disabled | Run matched prompts and generation lengths | Separate cache gains from speculative decoding gains |
| Long-context pressure | Increase prompt length toward `num_ctx` | Detect truncation and cache degradation |

For the long-prefix benchmark, test 1k, 4k, 8k, 16k, 32k, and 64k tokens where supported.

A useful regression criterion: flag a machine when actual cache reuse falls more than five percentage points below its established baseline under an identical controlled workload. That is a starting alert threshold, not a universal performance requirement.

## 6. Structural diagnostic classification

The analyzer must classify each avoidable miss into a likely cause, with evidence and confidence. Do not label everything a cache failure.

| Problem | Diagnostic evidence | Likely corrective action |
| --- | --- | --- |
| Dynamic content before system prompt | First divergence occurs very early | Move timestamps, IDs, and changing metadata after static instructions |
| Changing tool definitions | Stable system instructions but divergent tool segment | Canonicalize tool ordering and schemas |
| Message serialization changes | Equivalent messages yield different token fingerprints | Stabilize templates and serialization |
| Context truncation | Prompt length approaches context limit; early tokens disappear | Increase context or change truncation policy |
| Cache eviction | Prefix unchanged but reuse disappears after competing requests | Increase available capacity or reduce concurrency |
| Runner restart | Cache misses correlate with process restarts | Improve runner residency |
| Model/config mismatch | Same text, different model digest or KV configuration | Separate cache pools and normalize configurations |
| Routing instability | Identical prompts alternate between fleet nodes | Use session affinity |
| Disk-cache restore failure | Misses after restart despite saved cache artifacts | Verify actual restore support and compatibility |

These are diagnostic hypotheses, not definitive causes. For example, identical prompts with low reuse can indicate eviction, runner reassignment, or an implementation limitation.

A good diagnostic report says:

> The first divergence occurs within the opening prompt segment. Approximately 20,000 subsequent tokens are identical, but cannot be reused through ordinary prefix caching because the prefix is different. Move the dynamic timestamp after the stable instructions.

That is substantially more useful than reporting a 0% cache-hit rate.

## 7. Verification summary table

| # | Optimization | Test | Expected result |
| --- | --- | --- | --- |
| O1 | Dynamic content after static prefix | T1 | First divergence moves from opening segment to after stable prefix; cache efficiency rises to near 100% |
| O2 | Stable tool definitions and serialization | T2 | Same tool-segment fingerprints; no efficiency drop from tool ordering |
| O3 | Message serialization stability | T3 | Identical token fingerprints at every sampled position |
| O4 | Context truncation policy | T4 | No efficiency degradation as prompt length approaches `num_ctx` |
| O5 | KV-cache capacity and concurrency | T5 | Reuse stays at baseline under concurrency; eviction is the identified cause if it drops |
| O6 | Runner residency and session affinity | T6 | Reuse survives runner restart; identical prompts route to the same runner |
| O7 | Model and configuration matching | T7 | Same KV configuration matches baseline; different KV configurations use separate pools |
| O8 | Disk-backed prompt-state caching | T8 | Cache file identifier present; restored token count matches original; incompatibility recorded if unsupported |

## 8. Acceptance checklist

The implementation is complete when:

- [ ] Every Ollama request produces a persistent telemetry record, including streaming and failed requests.
- [ ] Cached-token counts are captured without silently converting missing values to zero.
- [ ] The system estimates reusable prefixes and distinguishes estimates from verified token-level matches.
- [ ] Long-prompt cache misses can be traced to their earliest divergence when sufficient prompt data is available.
- [ ] Runner restarts, model reloads, and configuration changes are correlated with cache misses.
- [ ] A controlled benchmark validates caching across model and context configurations.
- [ ] MTP and ordinary KV-cache performance are measured separately.
- [ ] Prompts and client documents are protected from unnecessary storage.
- [ ] Dashboards compare actual reuse against the theoretical opportunity and historical baseline.
- [ ] Telemetry failures do not interrupt inference or cause excessive latency.

The most valuable outcome is not just knowing that a machine has a 43% cache-hit rate. It is being able to explain:

> The machine received 14 requests sharing an identical 24,000-token system prefix. Eleven requests should have reused nearly the entire prefix, but seven lost their cache state after runner reassignment under concurrent load. Estimated avoidable prefill was 168,000 tokens. Recommended action: investigate runner residency and scheduling before changing the prompt format.

That is the level of observability to aim for.

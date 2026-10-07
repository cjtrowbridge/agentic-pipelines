# Playbook: Configure Local Inference

## Use when
Connecting a host pipeline to its local Ollama-compatible endpoint.

For a host using Ollama directly, first create and verify the needed named context presets with `playbooks/how_to_create_ollama_context_aliases.md`. The configured model name and request-level `num_ctx` must agree for each stage.

For VS Code Chat using Ollama, also follow `playbooks/how_to_optimize_vscode_and_ollama.md`: q8_0 KV cache and 45-minute inference timeouts are mandatory.

## Load
`api.sample.yaml`, the host pipeline definition, and `scripts/pipeline.py` preflight help. Do not load or display existing credentials unnecessarily.

## Procedure
1. Confirm `api.yaml` is ignored; copy the sample manually or with explicit operator approval.
2. Set a loopback/private endpoint, model or context alias, optional local-gateway credential/header, timeouts, TLS policy, generation defaults, and redaction values. A non-private endpoint requires explicit `allow_remote_endpoint: true` approval. The reference runner sends configured `num_ctx` on each request and uses one configured model for its stages; an alias alone does not determine its effective context.
3. Run preflight and correct schema/connectivity failures without logging secrets.
4. Run one bounded sanitized smoke request when authorized.
5. Confirm thread capture redaction and Git exclusion before processing entities.

## Stop conditions
Missing credentials, nonlocal/cloud fallback, failed redaction, untrusted TLS change, or tracked runtime evidence.

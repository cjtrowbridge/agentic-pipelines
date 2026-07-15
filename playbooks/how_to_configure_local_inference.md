# Playbook: Configure Local Inference

## Use when
Connecting a host pipeline to its local Ollama-compatible endpoint.

## Load
`api.sample.yaml`, the host pipeline definition, and `scripts/pipeline.py` preflight help. Do not load or display existing credentials unnecessarily.

## Procedure
1. Confirm `api.yaml` is ignored; copy the sample manually or with explicit operator approval.
2. Set a loopback/private endpoint, model, optional local-gateway credential/header, timeouts, TLS policy, generation defaults, and redaction values. A non-private endpoint requires explicit `allow_remote_endpoint: true` approval.
3. Run preflight and correct schema/connectivity failures without logging secrets.
4. Run one bounded sanitized smoke request when authorized.
5. Confirm thread capture redaction and Git exclusion before processing entities.

## Stop conditions
Missing credentials, nonlocal/cloud fallback, failed redaction, untrusted TLS change, or tracked runtime evidence.

# Markdown Repair Reference Pipeline

This is the proving case for the framework contract. Deterministic code discovers files, snapshots sources, validates front matter, protected content, code fences, and change bounds, manages state, and promotes artifacts. The worker is used only for ambiguous repairs that require interpreting which Markdown structure was intended; review and repair calls are optional bounded gates.

Run with the fake provider through the test suite. A real Ollama run is opt-in and uses ignored `api.yaml`.

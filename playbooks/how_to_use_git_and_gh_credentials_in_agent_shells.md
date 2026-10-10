# Playbook: Use git and gh Credentials in Agent Shells

## Use when

An agent shell cannot push, pull, or `gh`-write against GitHub; a push fails with `fatal: unable to get password ...` or `terminal prompts disabled`; an operator is about to be asked for credentials repeatedly; or an agent is tempted to disable `credential.interactive` or `safe.bareRepository` to "fix" the failure.

## Load

`AGENTS.md`; the failing command and its exact error; `git config --global --show-origin`; `gh auth status`; the affected host repository's `.gitignore` and `api.sample.yaml`. Do not load pipeline playbooks for this task.

## Facts

- Per `AGENTS.md`, authentication (including every `gh`/Git authenticated command) must run in the host terminal outside the agent sandbox, using the host's existing credential store or keyring. A sandbox failure or a `context deadline exceeded` device flow is not evidence that the credential is broken; never ask the operator to log in again on that basis — verify on the host first.
- Agent shells are additionally constrained by injected, non-negotiable settings: `credential.interactive=never` and `GIT_TERMINAL_PROMPT=0`. Git therefore never opens a terminal prompt and fails fast instead. `safe.bareRepository=explicit` and `core.fsmonitor=false` are unrelated to credentials; do not change them.
- A stored credential (e.g. `~/.config/gh/hosts.yml`) is host-scoped and persistent once created; VS Code's interactive IDE prompt does not create one for the shell. Solving it once for one repository solves it for every repository the operator owns or can access.
- Permission is per-repository: an account may have push on one repository and only pull on another (e.g. the host repository vs. the `agentic-pipelines` framework repository). A 403 after a successful read proves a permission gap, not a credential defect — fix the collaborator role, do not re-authenticate.
- Never disable `credential.interactive=never`, `GIT_TERMINAL_PROMPT`, or `safe.bareRepository` to make a push succeed. That masks the real defect and weakens the non-interactive guarantee.

## Procedure

1. Prove the failure signature. Record the exact command, the exact error, and `git config --global --show-origin | grep -Ei 'credential|terminal_prompt|bareRepository'`. Confirm the failure is `credential.interactive=never`/`terminal prompts disabled`, not a network, DNS, or permission error. If it is the latter, this playbook does not apply.
2. Inventory existing credentials before asking anyone for anything. Run, in order, and stop at the first positive:
   - `gh auth status` — if authenticated, skip to step 5.
   - `git config --global --get-all credential.https://github.com.helper` — if a helper is configured, try the failing command once; if it still fails, the helper has no stored token, so proceed to step 3.
   - `test -f ~/.config/gh/hosts.yml` and `test -f ~/.git-credentials` — note existence only; do not print secrets.
3. Obtain a credential using the least-secret, most-durable path. Prefer the device flow because it requires no secret to be pasted into chat:
   - `gh auth login --hostname github.com --git-protocol https --web`
   - The command prints a short-lived, single-use code and a URL. Hand the URL and code to the operator exactly once and wait. If the code expires (`context deadline exceeded`), re-run the same command to issue a fresh one; do not reuse the expired code.
   - If the operator has no browser path, fall back to a fine-grained or classic token and paste it into `gh auth login` when prompted for the token, keeping the token out of the chat transcript.
4. Register `gh` as the git credential helper and verify:
   - `gh auth setup-git`
   - `gh auth status`
   - `git config --global --get-all credential.https://github.com.helper` must show `!gh auth git-credential`.
   - Prove read: `git ls-remote https://github.com/<owner>/<repo>.git HEAD` returns a SHA.
5. Re-run the originally failing operation (e.g. `git push`) in the host terminal and confirm success. If the remote URL is SSH while the credential is HTTPS-based, either keep using the HTTPS remote or install SSH with `gh ssh-key` plus the agent's `ssh-add` step; do not mix an unconfigured SSH remote with an HTTPS credential and expect one to satisfy the other. A `Permission ... denied` (403) after a successful read means the account lacks push on that specific repository: add it as a collaborator with Write, or push from an account that has it — do not re-authenticate and do not treat the sandbox as the cause.
6. Guard the credential. Confirm `~/.config/gh/hosts.yml`, `~/.git-credentials`, `api.yaml`, private keys, and any `.env` are all ignored (`git check-ignore -v <path>` for each) and never staged. If any is untracked and not ignored, add it to `.gitignore` in the same checkpoint; never commit it.

## Outputs

- The exact failure signature and the credential inventory that led to the chosen path.
- `gh auth status`, the resulting `credential.https://github.com.helper`, and a successful `git ls-remote` and push (or the specific remaining blocker).
- `.gitignore` coverage evidence for every credential and host-local secret file.

## Stop conditions

- The failure is network/DNS/permission rather than credential-driven.
- The operator cannot complete the device flow and declines token entry.
- A repository remote requires a credential type this host cannot provide (for example a Gitea/`gitea.io` token on a GitHub-only `gh` host).
- Storing the credential would require writing to a path outside the operator's home or bypassing the injected non-interactive constraints.

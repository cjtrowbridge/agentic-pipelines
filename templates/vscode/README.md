# VS Code Entrypoint Examples

These files illustrate the required host-owned shape; they are not installable framework defaults. Replace every `REPLACE_...` and `PATH_TO_...` value from the host's reviewed entrypoint, prerequisite, and platform contracts. Merge approved fields into existing host files instead of replacing them.

- `tasks.example.json` demonstrates one task per example entrypoint, argument arrays, visible foreground terminals, inputs, and Windows versus Linux/macOS native dispatch.
- `launch.example.json` demonstrates one primary play action that invokes one native wrapper once. It uses VS Code's built-in JavaScript Debug Terminal (`node-terminal`) only to expose an arbitrary terminal command through the play button; it does not make Node.js a pipeline prerequisite.
- `bootstrap.example.ps1` and `bootstrap.example.sh` demonstrate locating the host's Python interpreter, invoking its stable `scripts/bootstrap.py` once, and delegating only after success. Their relative paths assume these wrappers are adapted into host `.vscode/`; adjust them for the host layout. They intentionally do not install software themselves.

Schema basis checked 2026-08-04: [VS Code tasks schema](https://code.visualstudio.com/docs/reference/tasks-appendix), [platform-specific launch properties](https://code.visualstudio.com/docs/debugtest/debugging-configuration#_platformspecific-properties), and the official [`node-terminal` command option](https://github.com/microsoft/vscode-js-debug/blob/main/OPTIONS.md#node-terminal-launch).

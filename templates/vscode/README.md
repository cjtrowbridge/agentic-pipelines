# VS Code Entrypoint Examples

These files illustrate the required host-owned shape; they are not installable framework defaults. Replace every `REPLACE_...` and `PATH_TO_...` value from the host's reviewed entrypoint, prerequisite, and platform contracts. Merge approved fields into existing host files instead of replacing them.

- `tasks.example.json` demonstrates one task per example entrypoint, argument arrays, visible foreground terminals, inputs, and Windows versus Linux/macOS native dispatch.
- `launch.example.json` demonstrates one primary play action that invokes one native wrapper once. It uses VS Code's built-in JavaScript Debug Terminal (`node-terminal`) only to expose an arbitrary terminal command through the play button; it does not make Node.js a pipeline prerequisite.
- `bootstrap.example.ps1` and `bootstrap.example.sh` demonstrate visible prerequisite checks and delegation. They intentionally do not install software.

Schema basis checked 2026-08-04: [VS Code tasks schema](https://code.visualstudio.com/docs/reference/tasks-appendix), [platform-specific launch properties](https://code.visualstudio.com/docs/debugtest/debugging-configuration#_platformspecific-properties), and the official [`node-terminal` command option](https://github.com/microsoft/vscode-js-debug/blob/main/OPTIONS.md#node-terminal-launch).

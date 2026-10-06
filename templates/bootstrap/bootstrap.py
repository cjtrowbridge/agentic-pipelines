#!/usr/bin/env python3
"""Stable host bootstrap entrypoint; keep this path across user-selected versions."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


SELECTED_VERSION = "v1"  # Change only when the host user chooses a new version.


def main() -> int:
    implementation = Path(__file__).resolve().with_name(f"bootstrap-{SELECTED_VERSION}.py")
    if not implementation.is_file():
        print(f"bootstrap: missing selected implementation: {implementation.name}", file=sys.stderr)
        return 1
    try:
        return subprocess.call([sys.executable, "-B", str(implementation), *sys.argv[1:]])
    except KeyboardInterrupt:
        print("bootstrap: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

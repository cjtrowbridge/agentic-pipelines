#!/usr/bin/env python3
"""Install declared pipeline dependencies into an ignored host-local directory."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Sequence


def within(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path must stay within host root: {path}") from exc
    return resolved


def fingerprint(requirements: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    digest.update(sys.version.encode("utf-8"))
    for requirement in requirements:
        digest.update(str(requirement).encode("utf-8"))
        digest.update(requirement.read_bytes())
    return digest.hexdigest()


def dependencies_available(target: Path, modules: Sequence[str]) -> bool:
    original = list(sys.path)
    try:
        sys.path.insert(0, str(target))
        return all(importlib.util.find_spec(module) is not None for module in modules)
    finally:
        sys.path[:] = original


def bootstrap(host_root: Path, target: Path, requirements: Sequence[Path], modules: Sequence[str]) -> bool:
    metadata = target.parent / "bootstrap.json"
    expected = fingerprint(requirements)
    if metadata.exists() and dependencies_available(target, modules):
        recorded = json.loads(metadata.read_text(encoding="utf-8"))
        if recorded.get("fingerprint") == expected:
            print(f"bootstrap: dependencies are current in {target.relative_to(host_root)}")
            return False
    target.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--target", str(target)]
    for requirement in requirements:
        command.extend(["-r", str(requirement)])
    print(f"bootstrap: installing declared dependencies in {target.relative_to(host_root)}")
    subprocess.run(command, check=True)
    if not dependencies_available(target, modules):
        raise RuntimeError("declared dependencies installed but required modules are unavailable")
    metadata.write_text(json.dumps({"fingerprint": expected, "requirements": [str(path.relative_to(host_root)) for path in requirements]}, indent=2) + "\n", encoding="utf-8")
    print("bootstrap: dependencies are ready")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap declared pipeline dependencies into a host-local directory.")
    parser.add_argument("--host-root", type=Path, default=Path.cwd())
    parser.add_argument("--target", type=Path, default=Path(".agentic-pipelines/dependencies"))
    parser.add_argument("--requirements", type=Path, action="append", required=True)
    parser.add_argument("--check-module", action="append", default=[])
    args = parser.parse_args()
    host_root = args.host_root.resolve()
    target = within(host_root, host_root / args.target)
    requirements = [within(host_root, host_root / requirement) for requirement in args.requirements]
    missing = [path for path in requirements if not path.is_file()]
    if missing:
        parser.error("missing requirements file(s): " + ", ".join(str(path) for path in missing))
    bootstrap(host_root, target, requirements, args.check_module)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

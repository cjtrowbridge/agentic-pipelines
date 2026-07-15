#!/usr/bin/env python3
"""Validate a staged package without configuring inference or starting work."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
if str(FRAMEWORK_ROOT) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_ROOT))

from pipeline_runtime.package import PackageError, validate_package


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_package(args.package), indent=2))
        return 0
    except (PackageError, OSError, ValueError) as exc:
        print(f"PACKAGE INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

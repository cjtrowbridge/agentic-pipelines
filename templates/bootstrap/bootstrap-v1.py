#!/usr/bin/env python3
"""Example requirement checks; replace the marker with reviewed host requirements."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_MARKER = ROOT / ".agentic-pipelines" / "bootstrap-example.ready"


@dataclass(frozen=True)
class Requirement:
    name: str
    probe: Callable[[], tuple[bool, str]]
    repair: Callable[[], None] | None = None


def probe_example_marker() -> tuple[bool, str]:
    if not EXAMPLE_MARKER.is_file():
        return False, "example marker is missing"
    if EXAMPLE_MARKER.read_text(encoding="utf-8") != "ready\n":
        return False, "example marker has unexpected content"
    return True, "example marker is current"


def repair_example_marker() -> None:
    EXAMPLE_MARKER.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLE_MARKER.write_text("ready\n", encoding="utf-8")


def requirements() -> list[Requirement]:
    # Replace this demonstration requirement with every declared host requirement.
    # A service probe must check application health, not just process/container state.
    return [Requirement("example local state", probe_example_marker, repair_example_marker)]


def run(checks: Sequence[Requirement], *, check_only: bool) -> int:
    if not checks:
        print("FAIL requirement inventory: no host requirements declared")
        print("TOTAL pass=0 fail=1")
        return 1
    passed = failed = 0
    for item in checks:
        try:
            healthy, detail = item.probe()
            repaired = False
            if not healthy and not check_only and item.repair is not None:
                item.repair()
                repaired = True
                healthy, detail = item.probe()
            if healthy:
                passed += 1
                print(f"PASS {item.name}: {detail}" + (" (repaired)" if repaired else ""))
            else:
                failed += 1
                print(f"FAIL {item.name}: {detail}")
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            failed += 1
            print(f"FAIL {item.name}: {type(exc).__name__}: {exc}")
    print(f"TOTAL pass={passed} fail={failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or repair declared host requirements.")
    parser.add_argument("--check", action="store_true", help="Report every requirement without changes")
    args = parser.parse_args()
    try:
        return run(requirements(), check_only=args.check)
    except KeyboardInterrupt:
        print("bootstrap: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

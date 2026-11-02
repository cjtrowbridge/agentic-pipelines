#!/usr/bin/env python3
"""
Run the canonical source check against a repository or its Git index.
Delegate to trusted framework validators, print diagnostics and propagate failure.
No model configuration, credentials or inspected source execution is required.
"""

import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from source_governance.checker import check
from source_governance.snapshot import Snapshot


def main():
    parser = argparse.ArgumentParser(description="Check mandatory source governance")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    print("source governance: inspecting staged index" if args.staged else "source governance: inspecting source tree")
    try:
        snapshot = Snapshot(args.repo_root, args.staged)
        if args.staged:
            changed = snapshot.git("diff", "--cached", "--name-only", "-z").split("\0")
            entries = snapshot.git("ls-files", "--stage", "-z").split("\0")
            gitlinks = {entry.split("\t", 1)[1] for entry in entries if entry.startswith("160000 ")}
            docs_only = all(Path(name).suffix.lower() == ".md" or name in gitlinks for name in changed if name)
            if docs_only:
                print("source governance: no staged source/policy changes; runtime API files not required")
                return 0
        counts, issues = check(snapshot)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"source governance: FAIL: {error}", file=sys.stderr)
        return 1
    for issue in issues:
        print(issue, file=sys.stderr)
    print(f"source governance: {len(counts)} source files; {len(issues)} failures")
    return int(bool(issues))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("source governance: interrupted", file=sys.stderr)
        raise SystemExit(130)

"""
Validate Go with the installed standard parser rather than C-style heuristics.
Compile only the trusted framework helper after its own canonical source gate.
Inspected source travels over stdin and is never compiled, imported or executed.
"""

import atexit
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


FRAMEWORK = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def parser_binary():
    # Retain the temporary directory for this checker process's lifetime.
    temporary = tempfile.TemporaryDirectory(prefix="source-go-parser-")
    checked = subprocess.run(
        [sys.executable, str(FRAMEWORK / "scripts/check_source_governance.py"),
         "--repo-root", str(FRAMEWORK)],
        capture_output=True, text=True, timeout=60, check=False,
    )
    if checked.returncode:
        temporary.cleanup()
        raise ValueError("trusted Go parser build blocked by framework source gate")
    binary = Path(temporary.name) / "parser"
    environment = dict(os.environ)
    environment.update(GOTOOLCHAIN="local", GOWORK="off", GOENV="off", GO111MODULE="off", GOFLAGS="")
    built = subprocess.run(
        ["go", "build", "-o", str(binary), str(FRAMEWORK / "source_governance/go_parser/main.go")],
        capture_output=True, text=True, timeout=120, check=False,
        cwd=temporary.name, env=environment,
    )
    if built.returncode:
        temporary.cleanup()
        raise ValueError("trusted Go parser build failed; verify installed Go toolchain")
    atexit.register(temporary.cleanup)
    return temporary, binary


def inspect_go(text, pattern):
    _, binary = parser_binary()
    parsed = subprocess.run(
        [str(binary)], input=text, capture_output=True, text=True, timeout=20, check=False,
    )
    if parsed.returncode:
        raise ValueError("Go parser process failed")
    report = json.loads(parsed.stdout)
    if report["Error"]:
        raise ValueError(report["Error"])
    rows = set()
    header = []
    before_code = True
    for token in report["Tokens"] or []:
        value = token["Text"]
        if token["Comment"]:
            if before_code:
                header.append(value)
            if re.fullmatch(pattern, value, re.DOTALL):
                continue
        else:
            before_code = False
        rows.update(range(token["Line"], token["Line"] + value.count("\n") + 1))
    issues = report["Issues"] or []
    explanatory = "\n".join(header)
    if len(explanatory.splitlines()) < 2 or not any(char.isalpha() for char in explanatory):
        issues.append("1: missing multiline responsibility header")
    return len(rows), issues

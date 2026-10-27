"""
Prepare reviewable Go layout candidates for explicitly authorized migrations.
Apply only nonoverlapping parser-proposed edits and validate with gofmt.
Never write host files or execute the inspected source; callers own adoption.
"""

import json
import subprocess

from .go_source import parser_binary


def candidate(text):
    _, binary = parser_binary("go_layout")
    proposed = subprocess.run(
        [str(binary)], input=text, capture_output=True, text=True, timeout=20, check=False,
    )
    if proposed.returncode:
        raise ValueError("Go migration input is invalid")
    report = json.loads(proposed.stdout)
    edits = report["Edits"] or []
    source = text.encode("utf-8")
    ranges = sorted((edit["Start"], edit["End"]) for edit in edits if edit["Start"] != edit["End"])
    previous_end = 0
    for start, end in ranges:
        if start < previous_end or end < start or end > len(source):
            raise ValueError("overlapping or invalid Go migration edits")
        previous_end = end
    for edit in edits:
        start = edit["Start"]
        end = edit["End"]
        if start < 0 or end < start or end > len(source):
            raise ValueError("invalid Go migration edit bounds")
        if start == end and any(left < start < right for left, right in ranges):
            raise ValueError("Go migration insertion overlaps a replacement")
    for edit in sorted(edits, key=lambda item: (item["Start"], item["End"]), reverse=True):
        source = source[:edit["Start"]] + edit["Text"].encode("utf-8") + source[edit["End"]:]
    formatted = subprocess.run(
        ["gofmt"], input=source, capture_output=True, timeout=20, check=False,
    )
    if formatted.returncode:
        raise ValueError("Go migration candidate failed syntax validation")
    return formatted.stdout.decode("utf-8"), report["Manual"] or []

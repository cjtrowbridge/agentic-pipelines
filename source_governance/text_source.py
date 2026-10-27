"""
Lex comments and quoted literals for shell, PowerShell and C-style source.
Count only recognized comments matching the configured pattern as excluded.
Report compressed actions conservatively; semantic simplicity remains review work.
"""

import re

from source_governance.shell_literals import consume_bodies, heredoc_at


def inspect_text(text, adapter, pattern, *, counted_rows=None):
    if adapter not in {"shell", "powershell", "cstyle"}:
        raise ValueError(f"unsupported source adapter: {adapter}")
    comment_start = {"shell": "#", "powershell": "#", "cstyle": "//"}[adapter]
    block = {"powershell": ("<#", "#>"), "cstyle": ("/*", "*/")}.get(adapter)
    offset = 0
    row = 1
    code = set()
    issues = []
    header_comments = []
    before_code = True
    visible = []
    pending = []
    while offset < len(text):
        char = text[offset]
        if char.isspace():
            visible.append(char)
            row += char.count("\n")
            offset += 1
            if char == "\n" and pending:
                offset, next_row, payload_rows = consume_bodies(text, offset, row, pending)
                code.update(payload_rows)
                visible.append("\n" * (next_row - row))
                row = next_row
                pending.clear()
            continue
        if offset == 0 and text.startswith("#!"):
            end = text.find("\n", offset)
            if end < 0:
                break
            offset = end
            continue
        if block and text.startswith(block[0], offset):
            end = text.find(block[1], offset + len(block[0]))
            if end < 0:
                raise ValueError(f"{row}: unterminated block comment")
            end += len(block[1])
            value = text[offset:end]
            if not re.fullmatch(pattern, value, re.DOTALL):
                code.update(range(row, row + value.count("\n") + 1))
            if before_code:
                header_comments.append(value)
            visible.append("\n" * value.count("\n"))
            row += value.count("\n")
            offset = end
            continue
        if text.startswith(comment_start, offset):
            end = text.find("\n", offset)
            if end < 0:
                end = len(text)
            value = text[offset:end]
            if not re.fullmatch(pattern, value, re.DOTALL):
                code.add(row)
            if before_code:
                header_comments.append(value)
            offset = end
            continue
        before_code = False
        code.add(row)
        if adapter == "shell" and text.startswith("<<<", offset):
            visible.append("0")
            offset += 3
            continue
        if adapter == "shell" and text.startswith("<<", offset):
            heredoc = heredoc_at(text, offset)
            if heredoc:
                delimiter, offset = heredoc
                pending.append(delimiter)
                visible.append("0")
                continue
        if char in {'"', "'", "`"}:
            quote = char
            end = offset + 1
            while end < len(text):
                if text[end] == "\\":
                    end += 2
                    continue
                if text[end] == quote:
                    break
                end += 1
            if end >= len(text):
                raise ValueError(f"{row}: unterminated quoted literal")
            value = text[offset:end + 1]
            visible.append("0" + "\n" * value.count("\n"))
            code.update(range(row, row + value.count("\n") + 1))
            row += value.count("\n")
            offset = end + 1
            continue
        visible.append(char)
        offset += 1
    if pending:
        raise ValueError("unterminated shell heredoc declaration")
    header = "\n".join(header_comments)
    if len(header.splitlines()) < 2 or not any(c.isalpha() for c in header):
        issues.append("1: missing multiline responsibility header")
    issues.extend(inspect_layout("".join(visible), adapter))
    if counted_rows is not None:
        counted_rows.update(code)
    return len(code), issues


def inspect_layout(visible, adapter):
    issues = []
    for row, line in enumerate(visible.splitlines(), 1):
        if adapter == "shell":
            if "<<" in line:
                issues.append(f"{row}: heredoc syntax needs a dedicated language adapter")
            simple = re.sub(r";\s*(?:then|do)\s*$", "", line)
            if simple.strip() in {";;", ";&", ";;&"}:
                continue
            if ";" in simple:
                issues.append(f"{row}: split shell actions onto separate lines")
        else:
            simple = re.sub(r"\bfor\s*\([^)]*\)", "for ()", line)
            if re.search(r";\s*[^\s}]+", simple):
                issues.append(f"{row}: semicolon combines actions")
            if re.search(r"\b(?:if|while)\s*\([^)]*(?<![=!<>])=(?!=)", simple):
                issues.append(f"{row}: assignment inside condition combines actions")
            if re.search(r"\{\s*[^\s}]+.*\}", simple):
                issues.append(f"{row}: put block body on its own line")
    return issues

"""Recognize bounded shell heredoc syntax without executing shell input.
Retain literal payload rows in source-size accounting and reject incomplete bodies.
"""

import re


def heredoc_at(text, offset):
    """Return a simple delimiter and the end of its redirection token.

    Complex delimiter expressions remain unsupported and fail through the caller.
    Here-strings are handled separately because they have no following body.
    """
    match = re.match(r"<<(-?)[ \t]*(?:'([A-Za-z_][A-Za-z_0-9]*)'|\"([A-Za-z_][A-Za-z_0-9]*)\"|([A-Za-z_][A-Za-z_0-9]*))", text[offset:])
    if not match:
        return None
    end = offset + match.end()
    if end < len(text) and text[end] not in " \t\r\n;|&)":
        return None
    delimiter = next(value for value in match.groups()[1:] if value is not None)
    return (delimiter, bool(match.group(1)), match.group(4) is None), end


def consume_bodies(text, offset, row, pending):
    """Consume queued heredoc bodies in shell redirection order.

    Return the next source position and every physical payload/delimiter row.
    The caller keeps newlines so later action diagnostics retain source locations.
    """
    first = row
    for delimiter, strip_tabs, quoted in pending:
        while offset < len(text):
            end = text.find("\n", offset)
            if end < 0:
                end = len(text)
            line = text[offset:end]
            candidate = line.lstrip("\t") if strip_tabs else line
            offset = end + int(end < len(text))
            row += 1
            if candidate == delimiter:
                break
            if not quoted and ("$(" in line or "`" in line):
                raise ValueError(f"{row - 1}: executable heredoc substitution needs a dedicated adapter")
        else:
            raise ValueError(f"{first}: unterminated shell heredoc {delimiter}")
        if candidate != delimiter:
            raise ValueError(f"{first}: unterminated shell heredoc {delimiter}")
    return offset, row, set(range(first, row))

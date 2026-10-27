"""Inspect JavaScript syntax with SpiderMonkey and tokenize physical source lines.
Never execute inspected application code; reject missing parser dependencies.
Use AST statements so regexes, templates, objects and arrow grammar are not actions.
"""

import json
from pathlib import Path
import re
import subprocess
import tempfile


PARSE_SCRIPT = """
const Gio = imports.gi.Gio;
const ByteArray = imports.byteArray;
const file = Gio.File.new_for_path(ARGV[0]);
const [, data] = file.load_contents(null);
print(JSON.stringify(Reflect.parse(ByteArray.toString(data), {loc: true})));
"""


def parse_javascript(text):
    with tempfile.TemporaryDirectory(prefix="source-javascript-") as folder:
        source = Path(folder) / "input.js"
        source.write_text(text, encoding="utf-8")
        try:
            result = subprocess.run(
                ["gjs", "-c", PARSE_SCRIPT, str(source)],
                capture_output=True, text=True, timeout=20, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise ValueError("JavaScript parser unavailable; declare and install GJS") from None
    if result.returncode:
        raise ValueError("invalid JavaScript source; SpiderMonkey parse failed")
    return json.loads(result.stdout)


def inspect_javascript(text, pattern):
    try:
        import esprima
    except ImportError:
        raise ValueError("JavaScript tokenizer unavailable; install declared esprima dependency") from None
    tree = parse_javascript(text)
    try:
        tokens = esprima.tokenize(text, {"loc": True, "range": True, "comment": True})
    except Exception:
        raise ValueError("JavaScript tokenization failed; cannot certify source") from None
    rows = set()
    header = []
    before_code = True
    for token in tokens:
        value = text[token.range[0]:token.range[1]]
        comment = token.type in {"LineComment", "BlockComment"}
        if comment and before_code:
            header.append(value)
        if not comment:
            before_code = False
        if comment and re.fullmatch(pattern, value, re.DOTALL):
            continue
        rows.update(range(token.loc.start.line, token.loc.end.line + 1))
    issues = layout_issues(tree)
    description = "\n".join(header)
    if len(description.splitlines()) < 2 or not any(char.isalpha() for char in description):
        issues.append("1: missing multiline responsibility header")
    return len(rows), issues


def layout_issues(tree):
    issues = []
    seen = set()

    def visit(node, parent=None, field=None):
        if isinstance(node, list):
            for item in node:
                visit(item, parent, field)
            return
        if not isinstance(node, dict):
            return
        kind = node.get("type", "")
        location = node.get("loc")
        if location:
            line = location["start"]["line"]
            statement = kind.endswith("Statement") or kind in {"VariableDeclaration", "FunctionDeclaration", "ClassDeclaration"}
            grammar = parent and parent.get("type") in {"ForStatement", "ForInStatement", "ForOfStatement"} and field in {"init", "left", "update"}
            if statement and kind not in {"BlockStatement", "EmptyStatement"} and not grammar:
                if line in seen:
                    issues.append(f"{line}: multiple statements on one line")
                seen.add(line)
            if kind == "BlockStatement" and node.get("body"):
                if node["body"][0]["loc"]["start"]["line"] == line:
                    issues.append(f"{line}: put block body on its own line")
            if kind == "AssignmentExpression":
                standalone = parent and parent.get("type") == "ExpressionStatement"
                loop_clause = parent and parent.get("type") == "ForStatement" and field in {"init", "update"}
                if not standalone and not loop_clause:
                    issues.append(f"{line}: embedded assignment combines actions")
        for key, value in node.items():
            if key != "loc":
                visit(value, node, key)

    visit(tree)
    return issues

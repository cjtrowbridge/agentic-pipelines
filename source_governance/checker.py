"""
Combine source inventory, documentation and language validation for a repository.
Check all owned source recursively from a trusted worktree or staged snapshot.
Return actionable diagnostics and counts; no candidate code is executed.
"""

from pathlib import PurePosixPath
import re

from .configuration import SOURCE_SUFFIXES, load_configuration
from .python_source import inspect_python
from .text_source import inspect_text
from .html_source import inspect_html
from .go_source import inspect_go


def check(snapshot):
    config = load_configuration(snapshot)
    snapshot.include_roots(config["roots"])
    issues = []
    counts = {}
    directories = set(snapshot.directories)
    sources = {}
    roots = set(config["roots"])
    languages = config["languages"]
    entrypoints = config.get("entrypoints", {})
    if entrypoints:
        directories.add(".")
    for name in sorted(snapshot.files):
        path = PurePosixPath(name)
        if path.parts[0] in roots:
            for parent in path.parents:
                if str(parent) != ".":
                    directories.add(str(parent))
        extension = path.suffix.lower()
        if extension not in SOURCE_SUFFIXES and extension not in languages:
            if not extension and path.name not in {"TODO", "LICENSE", "Makefile", "Dockerfile", "Jenkinsfile"}:
                try:
                    if snapshot.read(name).startswith("#!"):
                        issues.append(f"{name}: source launcher needs a configured language extension and code root")
                except UnicodeError:
                    pass
            continue
        if name not in entrypoints and (path.parts[0] not in roots or len(path.parts) == 1):
            issues.append(f"{name}: source is outside declared root directories")
            continue
        if extension not in languages:
            issues.append(f"{name}: no configured language/comment pattern")
            continue
        sources.setdefault(str(path.parent), []).append(path.name)
        try:
            text = snapshot.read(name)
            language = languages[extension]
            if language["adapter"] == "python":
                count, findings = inspect_python(text, language["comment_pattern"])
            elif language["adapter"] == "go":
                count, findings = inspect_go(text, language["comment_pattern"])
            elif language["adapter"] == "html":
                count, findings = inspect_html(text, language["comment_pattern"])
            else:
                count, findings = inspect_text(text, language["adapter"], language["comment_pattern"])
            counts[name] = count
            if count > config["max_lines"]:
                issues.append(f"{name}: {count} code lines exceeds 400; decompose by responsibility")
            issues.extend(f"{name}:{finding}" for finding in findings)
        except (ValueError, SyntaxError, OSError) as error:
            issues.append(f"{name}: invalid source: {error}")
    for directory in sorted(directories):
        prefix = "" if directory == "." else directory + "/"
        readme = prefix + "README.md"
        if readme not in snapshot.files:
            issues.append(f"{directory}: missing README.md source inventory")
            continue
        text = snapshot.read(readme)
        entries = dict(re.findall(r"^- `([^`]+)`:\s*(.+)$", text, re.MULTILINE))
        for filename in sources.get(directory, []):
            if filename not in entries or not entries[filename].strip():
                issues.append(f"{readme}: missing description for {filename}")
        for filename in entries:
            if prefix + filename not in snapshot.files:
                issues.append(f"{readme}: stale inventory entry {filename}")
    return counts, issues

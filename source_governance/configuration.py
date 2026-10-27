"""
Load only public code governance from YAML and validate fail-closed invariants.
Local inference values are neither interpreted nor returned in diagnostics.
Public templates establish reproducible source policy and local parity.
"""

from pathlib import PurePosixPath
import re
import yaml


ADAPTERS = {"python", "shell", "powershell", "cstyle", "html", "go"}
SOURCE_SUFFIXES = {
    ".py", ".pyw", ".sh", ".bash", ".ps1", ".psm1", ".go", ".rs",
    ".js", ".jsx", ".ts", ".tsx", ".c", ".h", ".cc", ".cpp", ".hpp",
    ".java", ".cs", ".rb", ".swift", ".kt", ".lua", ".php", ".r",
    ".m", ".mm", ".sql", ".vue", ".svelte", ".bat", ".cmd", ".pl",
    ".ex", ".exs", ".erl", ".fs", ".fsx", ".scala", ".dart", ".html", ".css",
}


def mapping(text):
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError:
        raise ValueError("invalid YAML configuration; values withheld") from None
    if not isinstance(value, dict) or not isinstance(value.get("code"), dict):
        raise ValueError("configuration needs a code mapping")
    return value["code"]


def load_configuration(snapshot):
    config = mapping(snapshot.read("api.sample.yaml"))
    if config.get("max_lines") != 400:
        raise ValueError("code.max_lines must be 400")
    roots = config.get("roots")
    if not isinstance(roots, list) or not roots:
        raise ValueError("code.roots must be a nonempty list")
    for root in roots:
        if not isinstance(root, str) or len(PurePosixPath(root).parts) != 1:
            raise ValueError("code roots must be top-level directories")
        if root in {".", ".."} or "/" in root or "\\" in root or root.startswith("."):
            raise ValueError(f"invalid code root: {root}")
        if not any(name.startswith(root + "/") for name in snapshot.files):
            raise ValueError(f"missing or empty code root: {root}")
    languages = config.get("languages")
    if not isinstance(languages, dict) or not languages:
        raise ValueError("code.languages must be a nonempty mapping")
    for extension, language in languages.items():
        if not isinstance(extension, str) or not extension.startswith("."):
            raise ValueError("language keys must be file extensions")
        if not isinstance(language, dict) or language.get("adapter") not in ADAPTERS:
            raise ValueError(f"unsupported adapter for {extension}")
        pattern = language.get("comment_pattern")
        if not isinstance(pattern, str) or not pattern:
            raise ValueError(f"missing comment_pattern for {extension}")
        try:
            re.compile(pattern)
        except re.error:
            raise ValueError(f"invalid comment_pattern for {extension}") from None
    validate_entrypoints(config, snapshot)
    if not snapshot.staged and (snapshot.root / "api.yaml").exists():
        local = mapping((snapshot.root / "api.yaml").read_text(encoding="utf-8-sig"))
        if local != config:
            raise ValueError("local api.yaml code mapping differs from tracked api.sample.yaml")
    return config


def validate_entrypoints(config, snapshot):
    entries = config.get("entrypoints", {})
    if not isinstance(entries, dict):
        raise ValueError("code.entrypoints must be an exact filename mapping")
    for name, contract in entries.items():
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.(?:sh|ps1|py)", name):
            raise ValueError("entrypoints must name individual root shell, PowerShell or Python files")
        if name not in snapshot.files:
            raise ValueError(f"missing declared entrypoint: {name}")
        if not isinstance(contract, dict) or set(contract) != {"purpose", "delegate"}:
            raise ValueError(f"entrypoint {name} needs purpose and delegate only")
        if not isinstance(contract["purpose"], str) or not contract["purpose"].strip():
            raise ValueError(f"entrypoint {name} needs a nonempty purpose")
        delegate = contract["delegate"]
        if not isinstance(delegate, str):
            raise ValueError(f"entrypoint {name} delegate must be a path")
        path = PurePosixPath(delegate)
        if path.is_absolute() or ".." in path.parts or "\\" in delegate:
            raise ValueError(f"entrypoint {name} delegate must stay inside a declared root")
        if len(path.parts) < 2 or path.parts[0] not in config["roots"] or delegate not in snapshot.files:
            raise ValueError(f"entrypoint {name} delegate must exist in a declared root")
        if path.suffix not in config.get("languages", {}):
            raise ValueError(f"entrypoint {name} delegate needs a configured source language")

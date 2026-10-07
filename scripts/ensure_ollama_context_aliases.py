#!/usr/bin/env python3
"""Ensure selected context aliases exist in a local Docker-hosted Ollama.

This command is intended to be called by a host's versioned bootstrap. It never
pulls a base model or replaces an existing alias with unexpected contents.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from typing import Any
from urllib import error, request
from urllib.parse import urlsplit


MODEL_PART_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\Z")
NAMESPACE_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*\Z")
CONTAINER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
CONTEXT_RE = re.compile(r"([1-9][0-9]*)([kK]?)\Z")
NUM_CTX_RE = re.compile(r"\s*num_ctx\s+([0-9]+)\s*", re.IGNORECASE)
SOURCE_RE = re.compile(r"\s*(FROM|DRAFT)\s+(\S+)\s*", re.IGNORECASE)
LOCAL_OPENER = request.build_opener(request.ProxyHandler({}))


class AliasError(RuntimeError):
    """A visible, non-secret provisioning failure."""


def hostname_label(hostname: str) -> str:
    label = re.sub(r"[^a-z0-9]+", "-", hostname.lower()).strip("-")
    if not label or len(label) > 40:
        raise AliasError("hostname cannot be represented as a short Ollama alias prefix")
    return label


def parse_context(value: str) -> tuple[str, int]:
    match = CONTEXT_RE.fullmatch(value)
    if not match:
        raise AliasError(f"invalid context {value!r}; use a positive token count such as 4096 or 96k")
    count = int(match.group(1)) * (1024 if match.group(2) else 1)
    if count < 1024:
        raise AliasError("context must be at least 1024 tokens")
    label = f"{count // 1024}k" if count % 1024 == 0 else f"{count}t"
    return label, count


def alias_name(hostname: str, context_label: str, model: str) -> str:
    if model.count(":") > 1:
        raise AliasError(f"invalid local Ollama model name: {model!r}")
    name, separator, tag = model.partition(":")
    parts = name.split("/")
    if (len(parts) not in {1, 2} or not MODEL_PART_RE.fullmatch(parts[-1])
            or (len(parts) == 2 and not NAMESPACE_RE.fullmatch(parts[0]))
            or (separator and not MODEL_PART_RE.fullmatch(tag))):
        raise AliasError(f"invalid local Ollama model name: {model!r}")
    alias = f"{hostname_label(hostname)}-{context_label}-{model}"
    alias_name_parts = alias.partition(":")[0].split("/")
    if any(len(part) > 80 for part in alias_name_parts) or (separator and len(tag) > 80):
        raise AliasError("alias name component exceeds Ollama's 80-character limit")
    return alias


def canonical_name(name: str) -> str:
    return name if ":" in name.rsplit("/", 1)[-1] else name + ":latest"


def local_docker_host(value: str) -> bool:
    if value.startswith(("npipe://", "unix://")):
        return True
    parsed = urlsplit(value)
    return parsed.scheme == "tcp" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}


def docker_endpoint(container: str, *, timeout: int) -> str:
    if not CONTAINER_RE.fullmatch(container):
        raise AliasError("container name must contain only letters, digits, dot, underscore, or hyphen")
    try:
        configured_host = os.environ.get("DOCKER_HOST")
        if configured_host and not local_docker_host(configured_host):
            raise AliasError("DOCKER_HOST points to a nonlocal Docker daemon")
        context = subprocess.run(
            ["docker", "context", "inspect", "--format", "{{json .Endpoints.docker.Host}}"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if context.returncode != 0:
            raise AliasError(f"Docker context cannot be inspected: {context.stderr.strip() or 'inspect failed'}")
        try:
            context_host = json.loads(context.stdout.strip())
        except ValueError as exc:
            raise AliasError("Docker context returned an invalid endpoint") from exc
        if not isinstance(context_host, str) or not local_docker_host(context_host):
            raise AliasError("Docker context points to a nonlocal daemon")
        state = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Running}}", container],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if state.returncode != 0:
            raise AliasError(f"Docker container {container!r} is unavailable: {state.stderr.strip() or 'inspect failed'}")
        if state.stdout.strip() != "true":
            raise AliasError(f"Docker container {container!r} is not running")
        ports = subprocess.run(
            ["docker", "port", container, "11434/tcp"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except FileNotFoundError as exc:
        raise AliasError("Docker CLI is unavailable") from exc
    except subprocess.TimeoutExpired as exc:
        raise AliasError("Docker inspection timed out") from exc
    if ports.returncode != 0:
        raise AliasError(f"Docker container {container!r} does not publish Ollama port 11434/tcp")
    for line in ports.stdout.splitlines():
        match = re.fullmatch(r"(?:127\.0\.0\.1|0\.0\.0\.0|\[::1\]|\[::\]|::):([0-9]{1,5})", line.strip())
        if match and 0 < int(match.group(1)) <= 65535:
            return f"http://127.0.0.1:{int(match.group(1))}"
    raise AliasError(f"Docker container {container!r} has no usable local published Ollama port")


def api_json(endpoint: str, path: str, payload: dict[str, Any] | None, *, timeout: int) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {} if body is None else {"Content-Type": "application/json"}
    req = request.Request(endpoint + path, data=body, headers=headers, method="GET" if body is None else "POST")
    try:
        with LOCAL_OPENER.open(req, timeout=timeout) as response:
            result = json.load(response)
    except (error.URLError, TimeoutError, ValueError) as exc:
        raise AliasError(f"Ollama {path} request failed: {exc}") from exc
    if not isinstance(result, dict):
        raise AliasError(f"Ollama {path} returned a non-object response")
    return result


def model_limit(show: dict[str, Any]) -> int:
    info = show.get("model_info")
    if not isinstance(info, dict):
        raise AliasError("base model has no inspectable context-limit metadata")
    architecture = info.get("general.architecture")
    limit = info.get(f"{architecture}.context_length") if isinstance(architecture, str) else None
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise AliasError("base model context limit is not inspectable")
    return limit


def from_source(show: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """Retain every model/draft source instead of assuming a single weight model.

    MTP definitions may expose multiple FROM entries or a separate DRAFT entry.
    Compare their complete ordered identity so a dropped/changed draft fails.
    """
    modelfile = show.get("modelfile")
    if not isinstance(modelfile, str):
        raise AliasError("model source cannot be verified: Ollama show omitted modelfile")
    sources = tuple((match.group(1).upper(), match.group(2))
                    for line in modelfile.splitlines()
                    if (match := SOURCE_RE.fullmatch(line)))
    if not any(kind == "FROM" for kind, _ in sources):
        raise AliasError("model source cannot be verified: missing FROM source")
    return sources


def verify_alias(show: dict[str, Any], *, base_source: tuple[tuple[str, str], ...], context: int) -> None:
    parameters = show.get("parameters")
    if not isinstance(parameters, str):
        raise AliasError("alias has no inspectable parameters")
    contexts = [int(match.group(1)) for line in parameters.splitlines() if (match := NUM_CTX_RE.fullmatch(line))]
    if contexts != [context]:
        raise AliasError(f"alias context mismatch: expected {context}, found {contexts or 'none'}")
    if from_source(show) != base_source:
        raise AliasError("alias base model source does not match the selected base")


def ensure_aliases(container: str, model: str, contexts: list[str], *, check_only: bool, timeout: int, hostname: str) -> int:
    requested: dict[str, int] = {}
    for value in contexts:
        label, count = parse_context(value)
        requested[label] = count
    aliases = [(alias_name(hostname, label, model), count) for label, count in requested.items()]
    endpoint = docker_endpoint(container, timeout=timeout)
    tags = api_json(endpoint, "/api/tags", None, timeout=timeout).get("models")
    if not isinstance(tags, list):
        raise AliasError("Ollama model list is malformed")
    names = {entry.get("name") for entry in tags if isinstance(entry, dict) and isinstance(entry.get("name"), str)}
    if canonical_name(model) not in names:
        raise AliasError(f"base model {model!r} is missing from container {container!r}; provision it through host bootstrap")
    base = api_json(endpoint, "/api/show", {"model": model}, timeout=timeout)
    limit = model_limit(base)
    source = from_source(base)
    if any(count > limit for count in requested.values()):
        raise AliasError(f"requested context exceeds base model limit of {limit} tokens")

    passed = failed = created = 0
    for alias, count in aliases:
        try:
            if canonical_name(alias) in names:
                existing = api_json(endpoint, "/api/show", {"model": alias}, timeout=timeout)
                verify_alias(existing, base_source=source, context=count)
                print(f"PASS {alias}: present, context={count}")
            elif check_only:
                raise AliasError("missing (check mode; no changes made)")
            else:
                result = api_json(endpoint, "/api/create", {"model": alias, "from": model, "parameters": {"num_ctx": count}, "stream": False}, timeout=timeout)
                if result.get("status") != "success":
                    raise AliasError(f"creation did not report success: {result.get('status')!r}")
                verified = api_json(endpoint, "/api/show", {"model": alias}, timeout=timeout)
                verify_alias(verified, base_source=source, context=count)
                created += 1
                print(f"PASS {alias}: created, context={count}")
            passed += 1
        except AliasError as exc:
            failed += 1
            print(f"FAIL {alias}: {exc}")
    print(f"TOTAL pass={passed} fail={failed} created={created}")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ensure context aliases in a local Docker Ollama container.")
    parser.add_argument("--container", default="ollama", help="local Docker container name (default: ollama)")
    parser.add_argument("--model", required=True, help="existing base Ollama model, including its tag when needed")
    parser.add_argument("--context", action="append", required=True, help="requested context, e.g. 1k or 96k; repeat for multiple aliases")
    parser.add_argument("--check", action="store_true", help="inspect only; never create aliases")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="finite Docker/API timeout (default: 300)")
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    try:
        return ensure_aliases(args.container, args.model, args.context, check_only=args.check, timeout=args.timeout_seconds, hostname=socket.gethostname())
    except KeyboardInterrupt:
        print("aliases: interrupted", file=sys.stderr)
        return 130
    except AliasError as exc:
        print(f"aliases: {exc}", file=sys.stderr)
        print("TOTAL pass=0 fail=1 created=0")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

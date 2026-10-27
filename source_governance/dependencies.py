"""Verify exact vendored dependency files against declared upstream manifests.
No directory exclusion is permitted; unlisted or modified source stays governed.
Retain inventory checks while preserving unmodified third-party distribution bytes.
"""

import hashlib
import json
from pathlib import PurePosixPath
import re
from urllib.parse import urlparse


def pinned_dependencies(snapshot, config):
    manifests = config.get("vendored_dependencies", [])
    if not isinstance(manifests, list) or any(not isinstance(item, str) for item in manifests):
        raise ValueError("vendored_dependencies must list exact manifest paths")
    if len(set(manifests)) != len(manifests):
        raise ValueError("vendored_dependencies must list distinct exact manifest paths")
    verified = set()
    for manifest in manifests:
        if not isinstance(manifest, str):
            raise ValueError("dependency manifest path must be text")
        path = PurePosixPath(manifest)
        if path.is_absolute() or ".." in path.parts or "vendor" not in path.parts:
            raise ValueError("dependency manifests must be exact paths under a vendor directory")
        if path.parts[0] not in config["roots"] or path.suffix != ".json":
            raise ValueError("dependency manifest must be JSON inside a declared source root")
        record = json.loads(snapshot.read(manifest))
        if not isinstance(record, dict):
            raise ValueError("dependency manifest must be an object")
        for field in ("name", "version", "source", "distribution", "license"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"dependency manifest requires {field}")
        for field in ("source", "distribution"):
            url = urlparse(record[field])
            if url.scheme != "https" or not url.hostname or url.username or url.password:
                raise ValueError("dependency provenance must be an HTTPS URL without credentials")
        files = record.get("files")
        if not isinstance(files, dict) or not files:
            raise ValueError("dependency manifest requires exact file hashes")
        for name, digest in files.items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts or "\\" in name or not name:
                raise ValueError("dependency file must stay beside its manifest")
            if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                raise ValueError("dependency file requires an exact sha256 digest")
            filename = str(path.parent / relative)
            if filename in verified:
                raise ValueError("dependency file is declared more than once")
            actual = "sha256:" + hashlib.sha256(snapshot.read_bytes(filename)).hexdigest()
            if actual != digest:
                raise ValueError(f"vendored dependency digest mismatch: {filename}")
            verified.add(filename)
    return verified

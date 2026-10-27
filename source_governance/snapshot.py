"""
Read repository or staged-index data without executing candidate source.
Snapshot supplies paths, modes and UTF-8 contents to the governance validators.
Git commands are read-only; symlinks and unmerged entries fail closed.
"""

from pathlib import Path, PurePosixPath
import os
import subprocess


class Snapshot:
    def __init__(self, root: Path, staged: bool = False):
        self.root = root.resolve()
        self.staged = staged
        self.modes = {}
        output = self.git("ls-files", "--stage", "-z")
        for entry in output.split("\0"):
            if not entry:
                continue
            metadata, name = entry.split("\t", 1)
            mode, object_id, stage = metadata.split()
            if stage != "0":
                raise ValueError(f"unmerged index entry: {name}")
            if mode != "160000":
                self.modes[name] = mode
        if not staged:
            names = self.git("ls-files", "--others", "--exclude-standard", "-z")
            for name in names.split("\0"):
                if name:
                    self.modes[name] = "100644"
        self.files = set(self.modes)
        self.directories = set()

    def include_roots(self, roots):
        if self.staged:
            return
        for root in roots:
            base = self.root / root
            if base.is_symlink():
                raise ValueError(f"source root is a symlink: {root}")
            for directory, children, files in os.walk(base, followlinks=False):
                parent = Path(directory)
                self.directories.add(parent.relative_to(self.root).as_posix())
                children[:] = [name for name in children if name not in {".git", "__pycache__"}]
                for name in children:
                    if (parent / name).is_symlink():
                        raise ValueError(f"source directory is a symlink: {parent / name}")
                for name in files:
                    path = (parent / name).relative_to(self.root).as_posix()
                    self.files.add(path)
                    self.modes.setdefault(path, "100644")

    def git_bytes(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            check=True,
        )
        return result.stdout

    def git(self, *args):
        return self.git_bytes(*args).decode("utf-8")

    def read(self, name):
        return self.read_bytes(name).decode("utf-8-sig")

    def read_bytes(self, name):
        parts = PurePosixPath(name).parts
        if not parts or ".." in parts or PurePosixPath(name).is_absolute():
            raise ValueError(f"unsafe repository path: {name}")
        if name not in self.files:
            raise ValueError(f"missing repository file: {name}")
        if self.modes[name] == "120000":
            raise ValueError(f"symlink is not permitted for governed input: {name}")
        if self.staged:
            return self.git_bytes("show", f":{name}")
        path = self.root / name
        if not path.resolve().is_relative_to(self.root):
            raise ValueError(f"path escapes repository: {name}")
        for parent in [path, *path.parents]:
            if parent == self.root:
                break
            if parent.is_symlink():
                raise ValueError(f"symlink is not permitted for governed input: {name}")
        return path.read_bytes()

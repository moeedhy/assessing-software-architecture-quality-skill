#!/usr/bin/env python3
"""Read-only, standard-library digest of the declared distributable package."""

import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys


ROOT_FILES = ("SKILL.md", "README.md", "CHANGELOG.md", "requirements-dev.txt")
ROOT_DIRS = ("references", "schemas", "examples", "agents", "scripts", "tests")
EXCLUDED_DIRS = frozenset({".git", ".idea", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"})
FORMAT = "architecture-skill-package-sha256-v1"


def package_digest(root: Path) -> dict:
    """Hash sorted POSIX paths and exact bytes, independent of mtimes/modes/root."""
    root = Path(root).absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"Package root must be a real directory: {root}")
    files = []

    def visit(path: Path) -> None:
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"Symlink in distributable input: {path.relative_to(root)}")
        if stat.S_ISDIR(mode):
            if path.name in EXCLUDED_DIRS:
                return
            for child in path.iterdir():
                visit(child)
        elif stat.S_ISREG(mode):
            if path.suffix not in {".pyc", ".pyo"}:
                files.append(path)
        else:
            raise ValueError(f"Non-regular distributable input: {path.relative_to(root)}")

    if not (root / "SKILL.md").is_file():
        raise ValueError(f"Missing SKILL.md in package: {root}")
    for name in (*ROOT_FILES, *ROOT_DIRS):
        path = root / name
        if path.exists() or path.is_symlink():
            visit(path)

    digest = hashlib.sha256()
    digest.update((FORMAT + "\0").encode("ascii"))
    manifest = []
    for path in sorted(files, key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        encoded_path = relative.encode("utf-8")
        content = path.read_bytes()
        # Fixed-width lengths make spaces, Unicode, newlines and concatenations
        # unambiguous. Hash actual read lengths, never stale stat sizes.
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
        manifest.append({"path": relative, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    return {"format": FORMAT, "digest": "sha256:" + digest.hexdigest(), "file_count": len(manifest), "files": manifest}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--compare", type=Path, help="Compare another package; exit 1 on mismatch")
    args = parser.parse_args(argv)
    try:
        result = package_digest(args.root)
        if args.compare is not None:
            other = package_digest(args.compare)
            result["comparison"] = {"digest": other["digest"], "match": result["digest"] == other["digest"]}
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if args.compare is None or result["comparison"]["match"] else 1
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

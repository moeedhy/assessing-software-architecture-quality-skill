# Release and installed-copy verification

The current package is candidate **2.3.0**. Its architecture quality model remains **2.1.0**, with **49 factors across eight domains**. Assessment schema **2.1** adds checkpoint support while retaining acceptance of legacy **2.0** assessments; score-result schema stays **2.0**. Package, model and schema versions describe different contracts and need not move together.

Independent fresh-context behavioral evaluation has **not been run**. Follow [the evaluation protocol](../tests/evals.md) to compare `NO_SKILL`, `BASELINE_V2_1` and `CANDIDATE_V2_3`. Deterministic tests, author review and package validation are not behavioral evaluation. Candidate 2.3.0 must not be advertised as independently behaviorally validated until the documented matrix, blind grading and gates have completed. The 2.2.0 package was not behaviorally validated either; do not treat it as a measured baseline.

## Local release checks

Run from the package root with Python 3.10 or later. Install development requirements in a disposable environment if the schema checker reports a missing dependency.

```sh
python3 scripts/architecture_quality.py validate-package .
python3 scripts/architecture_quality.py sync-model-docs . --check
python3 scripts/validate_schemas.py
python3 -m unittest discover -s tests/unit -p 'test_*.py' -v
python3 scripts/package_digest.py .
```

Record the candidate revision or working-tree identity, versions, exact check commands and observed results. Do not invent green output for commands that were not run. Freeze the digest after the final edit. Save release records and behavioral output outside the distributable tree so those records do not change the package they identify.

## Canonical package digest

`package_digest.py` uses only the Python standard library and performs no mutation. It hashes these declared distribution inputs, when present:

- Root `SKILL.md`, `README.md`, `CHANGELOG.md`, and `requirements-dev.txt`.
- Every regular file recursively inside `references/`, `schemas/`, `examples/`, `agents/`, `scripts/`, and `tests/`.

`SKILL.md` is required. `.git`, `.idea`, Python bytecode, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache` and `.cache` are excluded. Root files and directories outside this declared distribution are excluded, including local evaluation outputs if kept outside these directories. Distribution packaging must use this same declared set; add newly distributable roots to the digest tool and tests before shipping them. Symlinks in included inputs and a symlink package root fail closed; excluded metadata is never followed. Sockets, devices and other non-regular included inputs fail. The tool does not follow links to outside files.

The algorithm is `architecture-skill-package-sha256-v1`: initialize SHA-256 with that ASCII identifier followed by NUL; sort relative POSIX paths lexicographically; for each file append its UTF-8 path byte length as an unsigned eight-byte big-endian integer, its path bytes, its content byte length in the same encoding, then its exact bytes. Length framing makes paths containing spaces, Unicode or newlines unambiguous. Modes, timestamps, absolute root and directory iteration order do not affect the digest. Renaming or changing an included file does. JSON output includes the digest and a sorted per-file manifest with byte counts and individual SHA-256 values.

## Baseline and installation

The recorded v2.1 baseline is Git revision `566ec56`; inspect its `SKILL.md` and resolve its full commit before evaluation. Archive it before exposing a baseline subject to the candidate checkout. The baseline and candidate intentionally have different digests; matching is required between a frozen release and its installed copy, not between different releases.

Installation is a separate user action. Preparing or checking this release does not authorize overwriting a globally installed skill. This protocol does not perform installation. After the user installs the frozen package at their chosen real directory, compare it read-only:

```sh
python3 scripts/package_digest.py /path/to/frozen-release --compare /path/to/installed-skill
```

Exit status is `0` for a match, `1` for a digest mismatch, and `2` for invalid or unreadable input. On mismatch, compare the output manifests and resolve the discrepancy before treating that install as the evaluated package. Then inspect the installed `SKILL.md` metadata for package `2.3.0`, model `2.1.0`, 49 factors and eight domains, and run package validation against that installed directory:

```sh
python3 scripts/architecture_quality.py validate-package /path/to/installed-skill
```

Digest equality proves the declared files match, not runtime activation or behavioral quality. Reload the selected runtime if needed and verify which real installed path it discovers before attributing later behavior to this package. If an installer omits tests or other distributable inputs, it will not match the full package digest; record this difference instead of declaring the copies identical.

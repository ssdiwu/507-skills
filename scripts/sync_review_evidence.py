#!/usr/bin/env python3
"""Maintain one evidence-method source and self-contained skill-package copies."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("common/references/review-evidence.md")
TARGETS = (
    Path("code/507-review/references/evidence.md"),
    Path("code/507-inspect/references/evidence.md"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="check packaged copies without writing (default)")
    mode.add_argument("--write", action="store_true", help="regenerate the two packaged copies")
    args = parser.parse_args()
    source_path = ROOT / SOURCE
    if not source_path.is_file():
        parser.error(f"missing source: {SOURCE}")
    source = source_path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    header = (
        f"<!-- Generated from {SOURCE.as_posix()}; sha256={digest}. "
        "Maintainers regenerate with scripts/sync_review_evidence.py --write. "
        "This packaged file is complete; consumers read it directly. -->\n\n"
    ).encode("utf-8")
    expected = header + source
    drift = []
    for relative in TARGETS:
        target = ROOT / relative
        if target.is_symlink():
            parser.error(f"packaged copy must be a regular file: {relative}")
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
        if not target.is_file() or target.read_bytes() != expected:
            drift.append(relative.as_posix())
    if drift:
        print("Evidence copies missing or stale:\n" + "\n".join(drift))
        print("Run python3 scripts/sync_review_evidence.py --write after editing the source.")
        return 1
    print(f"Evidence method: {len(TARGETS)} self-contained copies match {SOURCE.as_posix()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

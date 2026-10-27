#!/usr/bin/env python3
"""Validate that the committed browser bundle matches its declared source files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    runtime = Path(__file__).resolve().parent.parent / "runtime"
    manifest_path = runtime / "dist" / "build-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 1:
        raise SystemExit("runtime build manifest schemaVersion 无效")
    failures = []
    for item in manifest.get("inputs", []):
        path = (runtime / item["path"]).resolve()
        try:
            path.relative_to(runtime.resolve())
        except ValueError:
            failures.append(f"输入越出 runtime：{item['path']}")
            continue
        if not path.is_file():
            failures.append(f"缺少输入：{item['path']}")
        elif sha256(path) != item.get("sha256"):
            failures.append(f"输入已变化：{item['path']}")
    bundle = manifest.get("bundle") or {}
    bundle_path = runtime / bundle.get("path", "")
    if not bundle_path.is_file():
        failures.append("缺少 runtime bundle")
    else:
        if sha256(bundle_path) != bundle.get("sha256"):
            failures.append("runtime bundle 哈希不一致")
        if bundle_path.stat().st_size != bundle.get("bytes"):
            failures.append("runtime bundle 大小不一致")
    if failures:
        raise SystemExit("runtime bundle 已过期：\n- " + "\n- ".join(failures))
    print(f"runtime bundle passed: {bundle_path} ({bundle_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

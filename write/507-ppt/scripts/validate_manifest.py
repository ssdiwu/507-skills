#!/usr/bin/env python3
"""Validate a portable manifest against the shared content and direction contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from design_system import DIRECTIONS

parser = argparse.ArgumentParser()
parser.add_argument("manifest", type=Path)
args = parser.parse_args()
manifest = args.manifest.resolve()
data = json.loads(manifest.read_text(encoding="utf-8"))
root = manifest.parent
required = ("version", "inputId", "inputSha256", "style", "carrier", "artifact", "pages", "assets", "notices", "verification", "screenshots", "degradations")
for key in required:
    if key not in data:
        raise SystemExit(f"missing manifest field: {key}")
if data["style"] not in DIRECTIONS or data["carrier"] not in ("html", "pptx"):
    raise SystemExit("unknown style/carrier")


def safe_file(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise SystemExit(f"path must stay relative: {value}")
    result = (root / path).resolve()
    repository = root.parent.resolve()
    if repository not in result.parents and result != repository:
        raise SystemExit(f"path escapes repository: {value}")
    return result


artifact = safe_file(data["artifact"])
if not artifact.is_file():
    raise SystemExit("artifact missing")
expected = data.get("sha256", data.get("artifactSha256"))
if not expected or hashlib.sha256(artifact.read_bytes()).hexdigest() != expected:
    raise SystemExit("artifact hash mismatch")
fixture = (root.parent / "scripts" / "fixtures" / f"{data['inputId']}.json").resolve()
if not fixture.is_file() or hashlib.sha256(fixture.read_bytes()).hexdigest() != data["inputSha256"]:
    raise SystemExit("input hash mismatch")
source_slides = json.loads(fixture.read_text(encoding="utf-8")).get("slides") or []
if [page.get("id") for page in data["pages"]] != [slide.get("id") for slide in source_slides]:
    raise SystemExit("page mapping must match input slide order")
asset_ids: set[str] = set()
for asset in data["assets"]:
    if not asset.get("id") or not asset.get("alt") or not asset.get("sha256"):
        raise SystemExit("asset source/alt/hash incomplete")
    path = safe_file(asset["path"])
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
        raise SystemExit(f"asset mismatch: {asset['id']}")
    asset_ids.add(asset["id"])
for page in data["pages"]:
    if not page.get("id") or "notes" not in page or not page.get("altStatus") or "assets" not in page:
        raise SystemExit("page mapping incomplete")
    if not set(page["assets"]).issubset(asset_ids):
        raise SystemExit(f"page asset mapping invalid: {page['id']}")
    if page.get("screenshot") and not safe_file(page["screenshot"]).is_file():
        raise SystemExit(f"page screenshot missing: {page['id']}")
for notice in data["notices"]:
    if not safe_file(notice).is_file():
        raise SystemExit(f"notice missing: {notice}")
for verification in data["verification"]:
    if verification.get("status") != "passed" or not verification.get("evidence"):
        raise SystemExit("verification evidence incomplete")
    if not safe_file(verification["evidence"]).is_file():
        raise SystemExit(f"verification evidence missing: {verification['evidence']}")
for screenshot in data["screenshots"]:
    if not safe_file(screenshot).is_file():
        raise SystemExit(f"screenshot missing: {screenshot}")
if not data.get("capabilities", {}).get("fallbackMatrix") or not safe_file(data["capabilities"]["fallbackMatrix"]).is_file():
    raise SystemExit("fallback matrix evidence missing")
print(f"manifest passed: {args.manifest}")

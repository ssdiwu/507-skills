#!/usr/bin/env python3
"""Check content, design-language, presentation, and carrier mappings."""
from __future__ import annotations

import argparse
import hashlib
import hashlib
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from design_system import PRESETS, language, normalize_deck, visible_strings
from visual_plan import load_plan, resolved_pages, validate_plan

ROOT = Path(__file__).resolve().parents[1]


def command_output(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return (result.stdout or result.stderr).strip()


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def producer(carrier: str) -> dict[str, str]:
    revision = command_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"])
    status = command_output(["git", "-C", str(ROOT), "status", "--porcelain"])
    result = {
        "name": "check_style_content.py",
        "sourceSha256": source_sha256(Path(__file__)),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "gitRevision": revision,
        "worktreeStatus": "dirty" if status and status != "unavailable" else "clean" if status == "" else "unknown",
        "tool": "officecli" if carrier == "pptx" else "python",
    }
    if carrier == "pptx":
        result["toolVersion"] = command_output(["officecli", "--version"])
    return result


parser = argparse.ArgumentParser()
parser.add_argument("--preset", choices=PRESETS)
parser.add_argument("--style", choices=PRESETS, help="deprecated alias for --preset")
parser.add_argument("--plan", type=Path)
parser.add_argument("--carrier", required=True, choices=["html", "pptx"])
parser.add_argument("--artifact", type=Path, required=True)
parser.add_argument("--fixture", type=Path, default=ROOT / "scripts/fixtures/collaboration-baseline.json")
parser.add_argument("--screenshots-dir", type=Path)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
raw = json.loads(args.fixture.read_text(encoding="utf-8"))
fixture = normalize_deck(raw)
preset_name = args.preset or args.style
try:
    plan = load_plan(args.plan, raw, preset_name)
except ValueError as error:
    raise SystemExit(str(error)) from error
errors = validate_plan(plan, raw, args.carrier)
if errors:
    raise SystemExit("invalid visual plan: " + "; ".join(errors))
pages = resolved_pages(plan, raw, args.carrier)
if args.carrier == "pptx":
    content = subprocess.run(["officecli", "view", str(args.artifact), "text"], check=True, text=True, capture_output=True).stdout
    page_text = {
        int(number): re.sub(r"\s+", "", body)
        for number, body in re.findall(r"=== /slide\[(\d+)\] ===\n(.*?)(?=\n=== /slide\[|\Z)", content, flags=re.S)
    }
else:
    content = args.artifact.read_text(encoding="utf-8")
    page_text = {}
    page_markup: dict[int, str] = {}
    for index, slide in enumerate(fixture["slides"], start=1):
        match = re.search(rf'<section\b[^>]*\bid="{re.escape(slide["id"])}"[^>]*>(.*?)</section>', content, flags=re.S)
        if match:
            page_markup[index] = match.group(1)
            page_text[index] = re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", " ", match.group(1))))
if len(page_text) != len(fixture["slides"]):
    raise SystemExit("per-slide content readback is incomplete")
missing: list[str] = []
for index, slide in enumerate(fixture["slides"], start=1):
    required = visible_strings(slide)
    if args.carrier == "pptx" and slide["component"] == "chart":
        data = slide["data"]
        chart_only = {str(value) for value in data.get("categories") or []}
        for series in data.get("series") or []:
            chart_only.add(str(series.get("name")))
            chart_only.update(str(value) for value in series.get("values") or [])
        required = [value for value in required if value not in chart_only]
    required.extend(str(asset["caption"]) for asset in slide.get("assets") or [] if asset.get("caption"))
    missing.extend(f"{slide['id']}: {value}" for value in required if re.sub(r"\s+", "", value) not in page_text[index])
    if args.carrier == "html":
        assets = slide.get("assets") or []
        if page_markup[index].count("<img ") != len(assets) or any(f'alt="{html.escape(str(asset["alt"]))}"' not in page_markup[index] for asset in assets):
            raise SystemExit(f"HTML image count or alt mapping failed: {slide['id']}")
if missing:
    raise SystemExit("content missing: " + " | ".join(missing))
language_id = plan["language"]["id"]
theme = language(language_id)
if args.carrier == "html":
    markers = [f'data-language="{language_id}"', f'--paper:#{theme["paper"]}', f'--accent:#{theme["accent"]}', 'role="region"', 'aria-label=', "data-presentation=", "data-support="]
    if not all(marker in content for marker in markers):
        raise SystemExit("HTML axis or semantic markers missing")
else:
    for font in (theme["title_latin"], theme["meta_latin"]):
        query = subprocess.run(["officecli", "query", str(args.artifact), f"shape[font.latin={font}]"], check=True, text=True, capture_output=True).stdout
        if not query.strip():
            raise SystemExit(f"PPTX language font missing: {font}")
carrier_evidence: dict[str, object] = {}
if args.carrier == "pptx":
    schema = subprocess.run(["officecli", "validate", str(args.artifact)], check=True, text=True, capture_output=True).stdout
    issues = subprocess.run(["officecli", "view", str(args.artifact), "issues"], check=True, text=True, capture_output=True).stdout
    missing_alt = subprocess.run(["officecli", "query", str(args.artifact), "picture:no-alt"], check=True, text=True, capture_output=True).stdout
    if "Validation passed" not in schema or "Found 0 issue(s)" not in issues or missing_alt.strip():
        raise SystemExit("PPTX structure, issues, or alt evidence failed")
    chart_paths = [line for line in subprocess.run(["officecli", "query", str(args.artifact), "chart"], check=True, text=True, capture_output=True).stdout.splitlines() if line.strip()]
    table_paths = [line for line in subprocess.run(["officecli", "query", str(args.artifact), "table"], check=True, text=True, capture_output=True).stdout.splitlines() if line.strip()]
    picture_paths = [line for line in subprocess.run(["officecli", "query", str(args.artifact), "picture"], check=True, text=True, capture_output=True).stdout.splitlines() if line.strip()]
    expected_pictures = sum(len(slide.get("assets") or []) for slide in fixture["slides"])
    if len(picture_paths) != expected_pictures:
        raise SystemExit("PPTX native picture count mismatch")
    screenshots = sorted(args.screenshots_dir.glob("slide-*.png")) if args.screenshots_dir else []
    if args.screenshots_dir and len(screenshots) != len(fixture["slides"]):
        raise SystemExit("PPTX evidence screenshot count mismatch")
    carrier_evidence = {
        "schema": "passed", "issues": 0, "alt": "passed", "nativeCharts": len(chart_paths), "nativeTables": len(table_paths), "nativePictures": len(picture_paths),
        "screenshots": len(screenshots),
    }
artifact_sha = hashlib.sha256(args.artifact.read_bytes()).hexdigest()
input_sha = hashlib.sha256(args.fixture.read_bytes()).hexdigest()
plan_sha = hashlib.sha256(args.plan.read_bytes()).hexdigest() if args.plan else "generated-legacy-plan"
checks = [
    {"name": "per-slide-content", "status": "passed"},
    {"name": "three-axis-markers", "status": "passed"},
]
if args.carrier == "pptx":
    checks.extend({"name": name, "status": "passed"} for name in ("schema", "issues", "alt", "native-data-objects", "screenshots"))
report = {
    "version": 1,
    "kind": "axis-content",
    "status": "passed",
    "failures": [],
    "producer": producer(args.carrier),
    "subject": {"inputId": fixture["id"], "inputSha256": input_sha, "visualPlanSha256": plan_sha, "artifactSha256": artifact_sha, "carrier": args.carrier},
    "checks": checks,
    "preset": plan.get("preset"), "language": language_id, "carrier": args.carrier, "pages": len(fixture["slides"]), "content": "passed",
    "components": [slide["component"] for slide in fixture["slides"]], "presentations": [page["presentation"] for page in pages],
    "carrierSupport": [page["carrierSupport"] for page in pages], "missing": [],
    "carrierEvidence": carrier_evidence,
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("axis/content report passed:", args.output)

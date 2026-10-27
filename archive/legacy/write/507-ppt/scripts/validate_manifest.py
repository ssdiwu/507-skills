#!/usr/bin/env python3
"""Validate portable manifest v2 while retaining legacy v1 readback."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from artifact_evidence import validate_artifact, validate_png
from design_system import DESIGN_LANGUAGES, PRESETS, normalize_deck
from verification_report import validate_report
from visual_plan import expected_degradations, resolved_manifest_pages, text_flow_limits, validate_plan

parser = argparse.ArgumentParser()
parser.add_argument("manifest", type=Path)
args = parser.parse_args()
manifest = args.manifest.resolve()
data = json.loads(manifest.read_text(encoding="utf-8"))
root = manifest.parent


def safe_file(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise SystemExit(f"path must stay relative: {value}")
    result = (root / path).resolve()
    repository = root.parent.resolve()
    if repository not in result.parents and result != repository:
        raise SystemExit(f"path escapes repository: {value}")
    return result


def require_file(value: str, label: str) -> Path:
    result = safe_file(value)
    if not result.is_file():
        raise SystemExit(f"{label} missing: {value}")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_for(input_id: str) -> Path:
    fixture = (root.parent / "scripts" / "fixtures" / f"{input_id}.json").resolve()
    if not fixture.is_file():
        raise SystemExit("input fixture missing")
    return fixture


def validate_common(required: tuple[str, ...], *, require_bound_input: bool = False) -> tuple[Path, dict]:
    for key in required:
        if key not in data:
            raise SystemExit(f"missing manifest field: {key}")
    if data["carrier"] not in ("html", "pptx"):
        raise SystemExit("unknown carrier")
    artifact = require_file(data["artifact"], "artifact")
    try:
        validate_artifact(artifact, data["carrier"])
    except ValueError as error:
        raise SystemExit(str(error)) from error
    expected = data.get("sha256", data.get("artifactSha256"))
    if not expected or digest(artifact) != expected:
        raise SystemExit("artifact hash mismatch")
    fixture = require_file(data["input"], "input") if require_bound_input else fixture_for(data["inputId"])
    if digest(fixture) != data["inputSha256"]:
        raise SystemExit("input hash mismatch")
    source = json.loads(fixture.read_text(encoding="utf-8"))
    normalized = normalize_deck(source)
    if [page.get("id") for page in data["pages"]] != [slide.get("id") for slide in normalized["slides"]]:
        raise SystemExit("page mapping must match input slide order")
    return fixture, source


def validate_assets_and_evidence(matrix_key: str) -> None:
    asset_ids: set[str] = set()
    for asset in data["assets"]:
        if not asset.get("id") or not asset.get("alt") or not asset.get("sha256"):
            raise SystemExit("asset source/alt/hash incomplete")
        path = require_file(asset["path"], f"asset {asset['id']}")
        if digest(path) != asset["sha256"]:
            raise SystemExit(f"asset mismatch: {asset['id']}")
        asset_ids.add(asset["id"])
    for page in data["pages"]:
        if not page.get("id") or "assets" not in page:
            raise SystemExit("page mapping incomplete")
        if not set(page["assets"]).issubset(asset_ids):
            raise SystemExit(f"page asset mapping invalid: {page['id']}")
        if page.get("screenshot"):
            screenshot = require_file(page["screenshot"], f"page screenshot {page['id']}")
            try:
                validate_png(screenshot, f"page {page['id']} screenshot")
            except ValueError as error:
                raise SystemExit(str(error)) from error
    for notice in data["notices"]:
        require_file(notice, "notice")
    for verification in data["verification"]:
        if verification.get("status") != "passed" or not verification.get("evidence"):
            raise SystemExit("verification evidence incomplete")
        evidence = require_file(verification["evidence"], "verification evidence")
        if verification.get("evidenceSha256") and digest(evidence) != verification["evidenceSha256"]:
            raise SystemExit("verification evidence hash mismatch")
    for screenshot in data["screenshots"]:
        screenshot_path = require_file(screenshot, "screenshot")
        try:
            validate_png(screenshot_path, "screenshot")
        except ValueError as error:
            raise SystemExit(str(error)) from error
    matrix = data.get("capabilities", {}).get(matrix_key)
    if not matrix:
        raise SystemExit(f"{matrix_key} evidence missing")
    require_file(matrix, matrix_key)


version = data.get("version")
if version == 1:
    _, source = validate_common(("version", "inputId", "inputSha256", "style", "carrier", "artifact", "pages", "assets", "notices", "verification", "screenshots", "degradations"))
    if data["style"] not in PRESETS:
        raise SystemExit("unknown legacy style")
    for page in data["pages"]:
        if "notes" not in page or not page.get("altStatus"):
            raise SystemExit("legacy page mapping incomplete")
    validate_assets_and_evidence("fallbackMatrix")
elif version == 2:
    _, source = validate_common(("version", "inputId", "input", "inputSha256", "carrier", "artifact", "sha256", "visualPlan", "visualPlanSha256", "language", "prototypeStatus", "prototypeEvidence", "pages", "assets", "notices", "verification", "screenshots", "degradations"), require_bound_input=True)
    language_id = (data.get("language") or {}).get("id")
    if language_id not in DESIGN_LANGUAGES:
        raise SystemExit("unknown design language")
    plan_path = require_file(data["visualPlan"], "visual plan")
    if digest(plan_path) != data["visualPlanSha256"]:
        raise SystemExit("visual plan hash mismatch")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_errors = validate_plan(plan, source, data["carrier"])
    if plan_errors:
        raise SystemExit("invalid visual plan: " + "; ".join(plan_errors))
    if data["prototypeStatus"] != (plan.get("prototype") or {}).get("status"):
        raise SystemExit("prototype status mismatch")
    if data["language"] != plan.get("language"):
        raise SystemExit("manifest language differs from visual plan")
    normalized = normalize_deck(source)
    expected_pages = resolved_manifest_pages(plan, source, data["carrier"])
    for page, expected, slide in zip(data["pages"], expected_pages, normalized["slides"], strict=True):
        required_page = ("component", "presentation", "treatment", "carrierSupport", "suppressedDecorations", "textFlowStatus", "notesStatus", "altStatus", "screenshotSha256")
        if any(key not in page for key in required_page):
            raise SystemExit(f"manifest v2 page incomplete: {page['id']}")
        if any(page.get(key) != value for key, value in expected.items()):
            raise SystemExit(f"manifest v2 page differs from resolver output: {page['id']}")
        if page["textFlowStatus"] != "screenshot-verified" or not page.get("screenshot") or page["screenshot"] not in data["screenshots"]:
            raise SystemExit(f"manifest v2 page lacks screenshot-verified text flow: {page['id']}")
        screenshot_path = require_file(page["screenshot"], f"page screenshot {page['id']}")
        if digest(screenshot_path) != page["screenshotSha256"]:
            raise SystemExit(f"manifest v2 page screenshot hash mismatch: {page['id']}")
        expected_notes = "provided" if slide.get("notes") else "declared-none"
        expected_assets = [asset["id"] for asset in slide.get("assets") or []]
        if page["notesStatus"] != expected_notes or page["altStatus"] != ("provided" if expected_assets else "not-applicable") or page["assets"] != expected_assets:
            raise SystemExit(f"manifest v2 notes, alt, or asset mapping differs from content: {page['id']}")
    if data["degradations"] != expected_degradations(plan, source, data["carrier"]):
        raise SystemExit("manifest degradations differ from resolver output")
    prototype_evidence = data["prototypeEvidence"]
    if plan["prototype"]["status"] == "approved":
        if not isinstance(prototype_evidence, list) or {item.get("kind") for item in prototype_evidence} != {"prototype-manifest", "prototype-contact-sheet"}:
            raise SystemExit("approved prototype evidence is incomplete")
        prototype_hashes: dict[str, str] = {}
        for item in prototype_evidence:
            path = require_file(item.get("path") or "", item.get("kind") or "prototype evidence")
            if digest(path) != item.get("sha256"):
                raise SystemExit("prototype evidence hash mismatch")
            if item.get("kind") == "prototype-contact-sheet":
                try:
                    validate_png(path, "prototype contact-sheet evidence")
                except ValueError as error:
                    raise SystemExit(str(error)) from error
            prototype_hashes[item["kind"]] = item["sha256"]
        approved_path = (Path(__file__).resolve().parents[1] / plan["prototype"]["manifest"]).resolve()
        approved = json.loads(approved_path.read_text(encoding="utf-8"))
        if prototype_hashes.get("prototype-manifest") != plan["prototype"]["manifestSha256"] or prototype_hashes.get("prototype-contact-sheet") != approved.get("evidenceSha256"):
            raise SystemExit("prototype evidence differs from visual plan approval chain")
    elif prototype_evidence != []:
        raise SystemExit("skipped prototype must not claim approval evidence")
    expected_subject = {
        "inputId": data["inputId"], "inputSha256": data["inputSha256"], "visualPlanSha256": data["visualPlanSha256"],
        "artifactSha256": data["sha256"], "carrier": data["carrier"],
    }
    browser_report = None
    browser_report_path = None
    for verification in data["verification"]:
        evidence = require_file(verification["evidence"], "verification evidence")
        try:
            report = validate_report(
                evidence,
                expected_subject,
                [slide["id"] for slide in normalized["slides"]],
                text_flow_limits(plan),
                {slide["id"]: slide["component"] for slide in normalized["slides"]},
                sum(len(slide.get("assets") or []) for slide in normalized["slides"]),
            )
        except ValueError as error:
            raise SystemExit(str(error)) from error
        if verification.get("kind") != report["kind"] or verification.get("status") != report["status"] or digest(evidence) != verification.get("evidenceSha256"):
            raise SystemExit("verification manifest entry differs from report")
        if report["kind"] == "html-browser":
            browser_report = report
            browser_report_path = evidence
    required_kinds = {"axis-content", "html-browser"} if data["carrier"] == "html" else {"axis-content"}
    if not required_kinds.issubset({item.get("kind") for item in data["verification"]}):
        raise SystemExit("required verification report kinds are missing")
    if data["carrier"] == "html" and browser_report is not None and browser_report_path is not None:
        for page, browser_page in zip(data["pages"], browser_report["pages"], strict=True):
            manifest_screenshot = require_file(page["screenshot"], "manifest page screenshot")
            browser_screenshot = (browser_report_path.parent / browser_page["screenshot"]).resolve()
            if manifest_screenshot != browser_screenshot or page["screenshotSha256"] != browser_page["screenshotSha256"]:
                raise SystemExit(f"HTML manifest screenshot differs from browser report: {page['id']}")
    matrix_path = require_file((data.get("capabilities") or {}).get("supportMatrix") or "", "supportMatrix")
    if digest(matrix_path) != (data.get("capabilities") or {}).get("supportMatrixSha256"):
        raise SystemExit("support matrix hash mismatch")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix_pages = (((matrix.get("carriers") or {}).get(data["carrier"]) or {}).get("pages") or [])
    normalized_matrix_pages = [{key: page.get(key) for key in expected} for page, expected in zip(matrix_pages, expected_pages, strict=False)]
    if len(matrix_pages) != len(expected_pages) or normalized_matrix_pages != expected_pages:
        raise SystemExit("support matrix differs from resolver output")
    validate_assets_and_evidence("supportMatrix")
else:
    raise SystemExit("manifest version must be 1 or 2")

print(f"manifest passed: {args.manifest} (v{version})")

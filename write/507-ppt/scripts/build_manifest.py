#!/usr/bin/env python3
"""Build manifest v2 from validated content, visual plan, and artifact evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from design_system import normalize_deck
from verification_report import validate_report
from visual_plan import expected_degradations, resolved_manifest_pages, text_flow_limits, validate_plan

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--carrier", choices=("html", "pptx"), required=True)
    parser.add_argument("--screenshots-dir", type=Path, required=True)
    parser.add_argument("--verification", type=Path, action="append", required=True)
    parser.add_argument("--support-matrix", type=Path)
    parser.add_argument("--fallback-matrix", type=Path, help="deprecated alias for --support-matrix")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    support_matrix = args.support_matrix or args.fallback_matrix
    if support_matrix is None:
        raise SystemExit("--support-matrix is required")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    content = normalize_deck(raw)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    errors = validate_plan(plan, raw, args.carrier)
    if errors:
        raise SystemExit("invalid visual plan: " + "; ".join(errors))
    page_contracts = resolved_manifest_pages(plan, raw, args.carrier)
    try:
        matrix = json.loads(support_matrix.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit("support matrix is unreadable") from error
    matrix_pages = (((matrix.get("carriers") or {}).get(args.carrier) or {}).get("pages") or [])
    normalized_matrix_pages = [{key: page.get(key) for key in contract} for page, contract in zip(matrix_pages, page_contracts, strict=False)]
    if matrix.get("inputId") != content["id"] or matrix.get("language") != plan["language"] or len(matrix_pages) != len(page_contracts) or normalized_matrix_pages != page_contracts:
        raise SystemExit("support matrix differs from resolver output")
    output_root = args.output.parent.resolve()

    def relative(path: Path) -> str:
        return os.path.relpath(path.resolve(), output_root)

    assets: list[dict[str, str]] = []
    asset_ids: set[str] = set()
    for slide in content["slides"]:
        for asset in slide.get("assets") or []:
            raw_path = asset.get("path")
            candidates = [(ROOT / str(raw_path)).resolve(), (args.input.parent / str(raw_path)).resolve()] if raw_path else []
            path = next((candidate for candidate in candidates if candidate.is_file()), None)
            if path is None:
                raise SystemExit(f"asset file missing: {raw_path}")
            if asset["id"] in asset_ids:
                raise SystemExit(f"duplicate asset id: {asset['id']}")
            assets.append({"id": asset["id"], "path": relative(path), "alt": asset["alt"], "sha256": digest(path)})
            asset_ids.add(asset["id"])
    pages: list[dict[str, object]] = []
    degradations = expected_degradations(plan, raw, args.carrier)
    screenshots: list[str] = []
    for index, (slide, contract) in enumerate(zip(content["slides"], page_contracts, strict=True), start=1):
        screenshot = args.screenshots_dir / f"slide-{index}.png"
        if not screenshot.is_file():
            raise SystemExit(f"visual evidence missing for page {slide['id']}: {screenshot}")
        screenshot_value = relative(screenshot)
        screenshots.append(screenshot_value)
        page_assets = [asset["id"] for asset in slide.get("assets") or [] if asset.get("id") in asset_ids]
        page = dict(contract)
        page.update({
            "textFlowStatus": "screenshot-verified",
            "notesStatus": "provided" if slide.get("notes") else "declared-none",
            "altStatus": "provided" if page_assets else "not-applicable",
            "assets": page_assets,
        })
        page["screenshot"] = screenshot_value
        page["screenshotSha256"] = digest(screenshot)
        pages.append(page)
    expected_subject = {
        "inputId": content["id"], "inputSha256": digest(args.input), "visualPlanSha256": digest(args.plan),
        "artifactSha256": digest(args.artifact), "carrier": args.carrier,
    }
    verification = []
    for path in args.verification:
        try:
            report = validate_report(path, expected_subject, [slide["id"] for slide in content["slides"]], text_flow_limits(plan))
        except ValueError as error:
            raise SystemExit(str(error)) from error
        verification.append({"name": path.stem, "kind": report["kind"], "status": report["status"], "evidence": relative(path), "evidenceSha256": digest(path)})
    required_kinds = {"axis-content", "html-browser"} if args.carrier == "html" else {"axis-content"}
    if not required_kinds.issubset({item["kind"] for item in verification}):
        raise SystemExit("required verification report kinds are missing")
    prototype_evidence: list[dict[str, str]] = []
    if plan["prototype"]["status"] == "approved":
        prototype_manifest = (ROOT / plan["prototype"]["manifest"]).resolve()
        approved = json.loads(prototype_manifest.read_text(encoding="utf-8"))
        contact_sheet = prototype_manifest.parent / approved["evidence"]
        prototype_evidence = [
            {"kind": "prototype-manifest", "path": relative(prototype_manifest), "sha256": digest(prototype_manifest)},
            {"kind": "prototype-contact-sheet", "path": relative(contact_sheet), "sha256": digest(contact_sheet)},
        ]
    manifest = {
        "version": 2, "inputId": content["id"], "inputSha256": digest(args.input), "carrier": args.carrier,
        "artifact": relative(args.artifact), "sha256": digest(args.artifact), "visualPlan": relative(args.plan), "visualPlanSha256": digest(args.plan),
        "language": plan["language"], "prototypeStatus": plan["prototype"]["status"], "prototypeEvidence": prototype_evidence, "pages": pages, "assets": assets,
        "notices": [relative(ROOT / "third-party-notices.md")],
        "verification": verification,
        "screenshots": screenshots, "degradations": degradations, "capabilities": {"supportMatrix": relative(support_matrix), "supportMatrixSha256": digest(support_matrix)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest v2 built: {args.output}")


if __name__ == "__main__":
    main()

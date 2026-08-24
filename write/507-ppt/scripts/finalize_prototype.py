#!/usr/bin/env python3
"""Bind a user-selected prototype candidate and visual evidence into an approved manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from artifact_evidence import validate_artifact, validate_png


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--selected", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--mixed-from", action="append")
    parser.add_argument("--merged-artifact", type=Path)
    parser.add_argument("--merged-plan", type=Path)
    parser.add_argument("--merged-evidence", type=Path)
    parser.add_argument("--pptx-artifact", type=Path)
    parser.add_argument("--pptx-evidence-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.manifest.read_text(encoding="utf-8"))
    if source.get("status") != "awaiting-user-selection":
        raise SystemExit("prototype manifest must be awaiting-user-selection")
    candidates = source.get("candidates") or []
    selected = next((item for item in candidates if item.get("id") == args.selected), None)
    if selected is None:
        raise SystemExit("selected candidate not found")
    root = args.manifest.parent
    mixed_from = list(dict.fromkeys(args.mixed_from or []))
    merged_values = (args.merged_artifact, args.merged_plan, args.merged_evidence)
    if mixed_from:
        candidate_ids = {item.get("id") for item in candidates}
        if not 2 <= len(mixed_from) <= 3 or not set(mixed_from).issubset(candidate_ids) or args.selected not in mixed_from:
            raise SystemExit("mixed prototype requires 2-3 distinct candidates including --selected")
        if not all(merged_values):
            raise SystemExit("mixed prototype requires --merged-artifact, --merged-plan, and --merged-evidence")
    elif any(merged_values):
        raise SystemExit("merged prototype files require at least two --mixed-from candidate ids")
    if args.evidence.resolve().parent != root.resolve() or args.output.resolve().parent != root.resolve():
        raise SystemExit("approved prototype manifest, evidence, and candidate package must share one directory")
    for candidate in candidates:
        for field, hash_field in (("artifact", "artifactSha256"), ("visualPlan", "visualPlanSha256")):
            path = root / candidate[field]
            if not path.is_file() or digest(path) != candidate.get(hash_field):
                raise SystemExit(f"prototype candidate evidence mismatch: {candidate.get('id')} {field}")
    if not args.evidence.is_file():
        raise SystemExit("prototype contact-sheet evidence missing")
    try:
        validate_png(args.evidence, "prototype contact-sheet evidence")
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if bool(args.pptx_artifact) != bool(args.pptx_evidence_dir):
        raise SystemExit("PPTX prototype artifact and evidence directory must be provided together")
    merged_prototype: dict[str, str] | None = None
    if mixed_from and args.merged_artifact and args.merged_plan and args.merged_evidence:
        for path in (args.merged_artifact, args.merged_plan, args.merged_evidence):
            if path.resolve().parent != root.resolve() or not path.is_file():
                raise SystemExit("merged prototype files must remain inside the candidate package")
        try:
            validate_artifact(args.merged_artifact, "html")
            validate_png(args.merged_evidence, "merged prototype evidence")
        except ValueError as error:
            raise SystemExit(str(error)) from error
        try:
            json.loads(args.merged_plan.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit("merged prototype visual plan is unreadable") from error
        merged_prototype = {
            "artifact": args.merged_artifact.name, "artifactSha256": digest(args.merged_artifact),
            "visualPlan": args.merged_plan.name, "visualPlanSha256": digest(args.merged_plan),
            "evidence": args.merged_evidence.name, "evidenceSha256": digest(args.merged_evidence),
        }
    html_evidence = merged_prototype or {
        "artifact": selected["artifact"], "artifactSha256": selected["artifactSha256"],
        "visualPlan": selected["visualPlan"], "visualPlanSha256": selected["visualPlanSha256"],
        "evidence": args.evidence.name, "evidenceSha256": digest(args.evidence),
    }
    target_evidence: dict[str, object] = {
        "html": {
            "artifact": html_evidence["artifact"], "artifactSha256": html_evidence["artifactSha256"],
            "visualPlan": html_evidence["visualPlan"], "visualPlanSha256": html_evidence["visualPlanSha256"],
            "contactSheet": html_evidence["evidence"], "contactSheetSha256": html_evidence["evidenceSha256"],
        }
    }
    if args.pptx_artifact and args.pptx_evidence_dir:
        if args.pptx_artifact.resolve().parent != root.resolve() or args.pptx_evidence_dir.resolve().parent != root.resolve() or not args.pptx_artifact.is_file():
            raise SystemExit("PPTX prototype artifact and evidence must remain inside the candidate package")
        screenshots = sorted(args.pptx_evidence_dir.glob("slide-*.png"), key=lambda path: int(path.stem.split("-")[1]))
        if len(screenshots) != len(source["representativeSlides"]):
            raise SystemExit("PPTX prototype screenshot count must match representative slides")
        try:
            validate_artifact(args.pptx_artifact, "pptx")
            for screenshot in screenshots:
                validate_png(screenshot, "PPTX prototype screenshot")
        except ValueError as error:
            raise SystemExit(str(error)) from error
        pptx_plan = merged_prototype or selected
        target_evidence["pptx"] = {
            "artifact": args.pptx_artifact.name, "artifactSha256": digest(args.pptx_artifact),
            "visualPlan": pptx_plan["visualPlan"], "visualPlanSha256": pptx_plan["visualPlanSha256"],
            "screenshots": [{"path": f"{args.pptx_evidence_dir.name}/{path.name}", "sha256": digest(path)} for path in screenshots],
        }
    approved = dict(source)
    approved.update({
        "status": "approved",
        "selectedCandidate": args.selected,
        "selectedArtifact": selected["artifact"],
        "selectedArtifactSha256": selected["artifactSha256"],
        "selectedVisualPlan": selected["visualPlan"],
        "selectedVisualPlanSha256": selected["visualPlanSha256"],
        "evidence": args.evidence.name,
        "evidenceSha256": digest(args.evidence),
        "targetEvidence": target_evidence,
    })
    if mixed_from and merged_prototype:
        approved["mixedFrom"] = mixed_from
        approved["mergedPrototype"] = merged_prototype
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(approved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("approved prototype manifest built:", args.output)


if __name__ == "__main__":
    main()

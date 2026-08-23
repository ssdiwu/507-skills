#!/usr/bin/env python3
"""Bind a user-selected prototype candidate and visual evidence into an approved manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--selected", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
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
    if args.evidence.resolve().parent != root.resolve() or args.output.resolve().parent != root.resolve():
        raise SystemExit("approved prototype manifest, evidence, and candidate package must share one directory")
    for candidate in candidates:
        for field, hash_field in (("artifact", "artifactSha256"), ("visualPlan", "visualPlanSha256")):
            path = root / candidate[field]
            if not path.is_file() or digest(path) != candidate.get(hash_field):
                raise SystemExit(f"prototype candidate evidence mismatch: {candidate.get('id')} {field}")
    if not args.evidence.is_file():
        raise SystemExit("prototype contact-sheet evidence missing")
    if bool(args.pptx_artifact) != bool(args.pptx_evidence_dir):
        raise SystemExit("PPTX prototype artifact and evidence directory must be provided together")
    target_evidence: dict[str, object] = {
        "html": {
            "artifact": selected["artifact"], "artifactSha256": selected["artifactSha256"],
            "visualPlan": selected["visualPlan"], "visualPlanSha256": selected["visualPlanSha256"],
            "contactSheet": args.evidence.name, "contactSheetSha256": digest(args.evidence),
        }
    }
    if args.pptx_artifact and args.pptx_evidence_dir:
        if args.pptx_artifact.resolve().parent != root.resolve() or args.pptx_evidence_dir.resolve().parent != root.resolve() or not args.pptx_artifact.is_file():
            raise SystemExit("PPTX prototype artifact and evidence must remain inside the candidate package")
        screenshots = sorted(args.pptx_evidence_dir.glob("slide-*.png"), key=lambda path: int(path.stem.split("-")[1]))
        if len(screenshots) != len(source["representativeSlides"]):
            raise SystemExit("PPTX prototype screenshot count must match representative slides")
        target_evidence["pptx"] = {
            "artifact": args.pptx_artifact.name, "artifactSha256": digest(args.pptx_artifact),
            "visualPlan": selected["visualPlan"], "visualPlanSha256": selected["visualPlanSha256"],
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
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(approved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("approved prototype manifest built:", args.output)


if __name__ == "__main__":
    main()

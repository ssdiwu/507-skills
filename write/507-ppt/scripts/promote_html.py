#!/usr/bin/env python3
"""Promote a browser-verified HTML candidate and its evidence without destroying the previous output on failure."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path

from design_system import normalize_deck
from verification_report import digest, validate_report
from visual_plan import text_flow_limits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--evidence-source", type=Path, required=True)
    parser.add_argument("--report-name", default="browser-report.json")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.candidate.suffix.lower() != ".html" or not args.candidate.is_file():
        raise SystemExit("candidate must be an existing HTML file")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    content = normalize_deck(raw)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    report_path = args.evidence_source / args.report_name
    subject = {
        "inputId": content["id"], "inputSha256": digest(args.input), "visualPlanSha256": digest(args.plan),
        "artifactSha256": digest(args.candidate), "carrier": "html",
    }
    try:
        validate_report(report_path, subject, [slide["id"] for slide in content["slides"]], text_flow_limits(plan))
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if args.evidence_dir.exists():
        raise SystemExit("evidence-dir already exists; use a versioned empty destination")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{args.output.stem}-promote-", dir=args.output.parent) as temporary:
        candidate_copy = Path(temporary) / args.output.name
        evidence_copy = Path(temporary) / args.evidence_dir.name
        shutil.copy2(args.candidate, candidate_copy)
        shutil.copytree(args.evidence_source, evidence_copy)
        os.replace(evidence_copy, args.evidence_dir)
        try:
            os.replace(candidate_copy, args.output)
        except Exception:
            shutil.rmtree(args.evidence_dir, ignore_errors=True)
            raise
    print(f"HTML promoted: {args.output}; evidence: {args.evidence_dir}")


if __name__ == "__main__":
    main()

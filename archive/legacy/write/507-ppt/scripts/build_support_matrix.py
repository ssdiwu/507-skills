#!/usr/bin/env python3
"""Build a reviewable component/presentation/carrier support report."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from design_system import normalize_deck
from visual_plan import resolved_pages, validate_plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    content = normalize_deck(raw)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    errors = validate_plan(plan, raw)
    if errors:
        raise SystemExit("invalid visual plan: " + "; ".join(errors))
    carriers: dict[str, object] = {}
    for carrier in ("html", "pptx"):
        resolved = resolved_pages(plan, raw, carrier)
        pages = []
        counts: Counter[str] = Counter()
        for slide, visual in zip(content["slides"], resolved, strict=True):
            counts[visual["carrierSupport"]] += 1
            pages.append({
                "id": slide["id"],
                "component": slide["component"],
                "presentation": visual["presentation"],
                "treatment": visual.get("treatment", "default"),
                "compatibility": visual["compatibility"],
                "carrierSupport": visual["carrierSupport"],
                "suppressedDecorations": visual.get("suppressions") or [],
            })
        carriers[carrier] = {"summary": dict(sorted(counts.items())), "pages": pages}
    report = {
        "version": 1,
        "inputId": content["id"],
        "language": plan["language"],
        "prototypeStatus": plan["prototype"]["status"],
        "carriers": carriers,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("support matrix built:", args.output)


if __name__ == "__main__":
    main()

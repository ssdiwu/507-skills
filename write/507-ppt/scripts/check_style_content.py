#!/usr/bin/env python3
"""Check visible content and direction tokens against a generated carrier."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from design_system import DIRECTIONS, direction, visible_strings

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--style", required=True, choices=DIRECTIONS)
parser.add_argument("--carrier", required=True, choices=["html", "pptx"])
parser.add_argument("--artifact", type=Path, required=True)
parser.add_argument("--fixture", type=Path, default=ROOT / "scripts/fixtures/collaboration-baseline.json")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
required = [value for slide in fixture["slides"] for value in visible_strings(slide)]
if args.carrier == "pptx":
    content = subprocess.run(["officecli", "view", str(args.artifact), "text"], check=True, text=True, capture_output=True).stdout
else:
    content = args.artifact.read_text(encoding="utf-8")
missing = [value for value in required if value not in content]
if missing:
    raise SystemExit("content missing: " + " | ".join(missing))
theme = direction(args.style)
if args.carrier == "html":
    markers = [f'data-direction="{args.style}"', f'--paper:#{theme["paper"]}', f'--accent:#{theme["accent"]}', 'role="region"', 'aria-label=']
    if not all(marker in content for marker in markers):
        raise SystemExit("HTML direction or semantic markers missing")
else:
    for font in (theme["title_latin"], theme["meta_latin"]):
        query = subprocess.run(["officecli", "query", str(args.artifact), f"shape[font.latin={font}]"], check=True, text=True, capture_output=True).stdout
        if not query.strip():
            raise SystemExit(f"PPTX direction font missing: {font}")
report = {"style": args.style, "carrier": args.carrier, "pages": len(fixture["slides"]), "content": "passed", "direction": theme["label"], "components": [slide["kind"] for slide in fixture["slides"]], "missing": []}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("style/content report passed:", args.output)

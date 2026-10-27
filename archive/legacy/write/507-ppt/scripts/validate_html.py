#!/usr/bin/env python3
"""Static contract checks for a generated offline 507-ppt HTML deck."""
from __future__ import annotations

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("file", type=Path)
args = parser.parse_args()
content = args.file.read_text(encoding="utf-8")

required = (
    'role="region"', 'aria-live="polite"', "touchstart", "wheel",
    "prefers-reduced-motion", '<main id="deck"', "flex:0 0 100vw", ".js #deck",
    "data-component=", "data-presentation=", "data-language=", "data-support=",
    ".phrase{white-space:nowrap}", "prefer-single-line-intent", "fitPhrases()", "checkOverflow()", "addEventListener('resize'",
    'class="speaker-notes" hidden', ".instant #deck{transition:none}", "params.has('instant')", ".bar-group",
    'id="audit-report"', "auditSnapshot()", ".suppress-background-grid::before{background:none!important}",
)
for token in required:
    if token not in content:
        raise SystemExit(f"missing {token}")
if "http://" in content or "https://" in content:
    raise SystemExit("remote resource found")
if content.count('role="region"') < 1:
    raise SystemExit("no semantic slide regions")
print("HTML static contract passed:", args.file)

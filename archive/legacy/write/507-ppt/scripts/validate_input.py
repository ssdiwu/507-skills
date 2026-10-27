#!/usr/bin/env python3
"""Validate the shared mature-slide-content contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from design_system import normalize_deck, validate_deck

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
raw = json.loads(args.input.read_text(encoding="utf-8"))
errors = validate_deck(raw)
if errors:
    print(json.dumps({"status": "return-stage", "reason": "; ".join(errors)}, ensure_ascii=False))
    raise SystemExit(1)
normalized = normalize_deck(raw)
print(json.dumps({"status": "ready", "carrierInput": "mature-slide-content", "contentVersion": 3, "legacyNormalized": raw.get("version") != 3, "slides": len(normalized["slides"])}, ensure_ascii=False))

#!/usr/bin/env python3
"""Validate the shared mature-slide-content contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from design_system import validate_deck

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
errors = validate_deck(json.loads(args.input.read_text(encoding="utf-8")))
if errors:
    print(json.dumps({"status": "return-stage", "reason": "; ".join(errors)}, ensure_ascii=False))
    raise SystemExit(1)
print(json.dumps({"status": "ready", "carrierInput": "mature-slide-content"}, ensure_ascii=False))

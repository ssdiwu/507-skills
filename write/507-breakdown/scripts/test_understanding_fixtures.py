#!/usr/bin/env python3
"""Validate saved MiniMax-M3 understanding fixtures against the semantic contract.

These fixtures are static semantic-contract samples saved without API keys.
This test validates output structure only; it does not prove a live API call.

Run: python3 scripts/test_understanding_fixtures.py
Exit 0 = PASS, non-zero = FAIL.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "assets" / "fixtures"


def validate_understanding(data: dict, name: str) -> None:
    if not isinstance(data.get("videoThesis"), str) or not data["videoThesis"].strip():
        raise SystemExit(f"FAIL {name}: videoThesis missing or empty")
    if not isinstance(data.get("videoTypeHint"), str) or not data["videoTypeHint"].strip():
        raise SystemExit(f"FAIL {name}: videoTypeHint missing or empty")
    units = data.get("semanticUnits", [])
    if not units:
        raise SystemExit(f"FAIL {name}: empty semanticUnits")
    required = {"id", "meaning", "spokenAnchors", "visualAnchors", "referencePosition", "referenceTimeHint", "status"}
    for i, unit in enumerate(units):
        missing = required - set(unit)
        if missing:
            raise SystemExit(f"FAIL {name}: unit[{i}] missing: {missing}")
        if not isinstance(unit["id"], str) or not unit["id"].strip():
            raise SystemExit(f"FAIL {name}: unit[{i}].id not non-empty string")
        if not isinstance(unit["meaning"], str) or not unit["meaning"].strip():
            raise SystemExit(f"FAIL {name}: unit[{i}].meaning not non-empty string")
        if not isinstance(unit["spokenAnchors"], list) or not all(isinstance(x, str) for x in unit["spokenAnchors"]):
            raise SystemExit(f"FAIL {name}: unit[{i}].spokenAnchors not string array")
        if not isinstance(unit["visualAnchors"], list) or not all(isinstance(x, str) for x in unit["visualAnchors"]):
            raise SystemExit(f"FAIL {name}: unit[{i}].visualAnchors not string array")
        if not isinstance(unit["referencePosition"], str):
            raise SystemExit(f"FAIL {name}: unit[{i}].referencePosition not string")
        if not isinstance(unit["referenceTimeHint"], str):
            raise SystemExit(f"FAIL {name}: unit[{i}].referenceTimeHint not string")
        if unit["status"] != "unlocalized":
            raise SystemExit(f"FAIL {name}: unit[{i}] status={unit['status']} (expected unlocalized)")
    prov = data.get("provenance", {})
    print(f"PASS {name}: {len(units)} units, provenance source={prov.get('source', 'unspecified')}")


def main() -> int:
    fixtures = [
        "m3_understanding_synthetic.json",
        "m3_understanding_9router.json",
    ]
    for name in fixtures:
        path = FIXTURES / name
        if not path.exists():
            raise SystemExit(f"FAIL: fixture not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_understanding(data, name)
    print("\n=== all fixture validations PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
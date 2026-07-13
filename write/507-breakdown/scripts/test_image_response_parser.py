#!/usr/bin/env python3
"""Regression test for fenced MiniMax key-frame image JSON."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from video_describe_key_frames import parse_image_result

anchors = ["solid red", "no text"]
fenced = """```json
{
  "description": "A solid red field without text.",
  "anchorChecks": [
    {"anchor": "solid red", "visible": true, "evidence": "The full frame is red."},
    {"anchor": "no text", "visible": true, "evidence": "No characters are present."}
  ]
}
```"""

result = parse_image_result(fenced, anchors)
assert result["description"] == "A solid red field without text."
assert [item["anchor"] for item in result["anchorChecks"]] == anchors

try:
    parse_image_result(fenced, ["solid red"])
except RuntimeError:
    pass
else:
    raise AssertionError("anchor mismatch accepted")

print("PASS: key-frame image parser accepts fenced JSON and validates anchors")

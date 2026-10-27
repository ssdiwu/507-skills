#!/usr/bin/env python3
"""Regression tests for fenced/prose-wrapped MiniMax JSON output."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from video_understand_minimax import parse_json_lenient

cases = [
    ('{"meaning":"literal { brace } in text","nested":{"ok":true}}', "literal { brace } in text"),
    ('model preface\n```json\n{"meaning":"escaped quote: \\" and }","nested":{}}\n```\n', 'escaped quote: " and }'),
    ('prose before {"meaning":"{inside}","nested":{}} prose after', '{inside}'),
]
for raw, expected in cases:
    assert parse_json_lenient(raw)["meaning"] == expected
try:
    parse_json_lenient('prose {"meaning":"unfinished"')
except RuntimeError:
    pass
else:
    raise AssertionError("unterminated object accepted")
print("PASS: MiniMax JSON parser handles braces/escapes and rejects unterminated objects")

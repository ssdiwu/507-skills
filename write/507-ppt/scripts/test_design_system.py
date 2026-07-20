#!/usr/bin/env python3
"""Regression checks for the public component and design-direction registry."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from design_system import COMPONENTS, DIRECTIONS, validate_deck

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "scripts/fixtures/system-showcase.json"


class DesignSystemTests(unittest.TestCase):
    def test_showcase_covers_every_public_component(self) -> None:
        data = json.loads(SHOWCASE.read_text(encoding="utf-8"))
        self.assertEqual(validate_deck(data), [])
        self.assertEqual({slide["kind"] for slide in data["slides"]}, set(COMPONENTS))

    def test_directions_have_complete_distinct_tokens(self) -> None:
        self.assertGreaterEqual(len(DIRECTIONS), 6)
        combinations = {(item["paper"], item["accent"], item["title_latin"], item["radius"], item["density"]) for item in DIRECTIONS.values()}
        self.assertEqual(len(combinations), len(DIRECTIONS))
        for name, item in DIRECTIONS.items():
            self.assertTrue(all(item[key] for key in ("paper", "ink", "accent", "title_ea", "title_latin", "meta_latin", "radius", "density")), name)

    def test_html_renders_all_components_for_every_direction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            for name in DIRECTIONS:
                output = Path(temporary) / f"{name}.html"
                subprocess.run(["python3", str(ROOT / "scripts/generate_html.py"), "--style", name, "--input", str(SHOWCASE), "--output", str(output)], check=True)
                html = output.read_text(encoding="utf-8")
                self.assertIn(f'data-direction="{name}"', html)
                for component in COMPONENTS:
                    self.assertIn(f'data-component="{component}"', html)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Regression tests for validated, atomic PPTX publication."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_pptx as generator
import validate_pptx as validator


class GeneratePptxTests(unittest.TestCase):
    def publish(self, output: Path) -> None:
        generator.publish_pptx(
            {"deck": {"title": "Test"}, "slides": []},
            SCRIPT_DIR / "fixtures" / "collaboration-baseline.json",
            "swiss",
            output,
        )

    def test_generation_failure_preserves_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as tmp:
            output = Path(tmp) / "deck.pptx"
            output.write_bytes(b"old")

            def fail_after_create(_data: dict, _theme: dict, candidate: Path) -> None:
                candidate.write_bytes(b"partial")
                raise RuntimeError("synthetic generation failure")

            with (
                patch.object(generator, "render_deck", side_effect=fail_after_create),
                patch.object(generator, "close_quietly"),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic generation failure"):
                    self.publish(output)

            self.assertEqual(output.read_bytes(), b"old")
            self.assertEqual([path for path in output.parent.iterdir() if path.is_dir()], [])

    def test_candidate_validation_includes_per_slide_screenshots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as tmp:
            candidate = Path(tmp) / "deck.pptx"
            with patch.object(generator.subprocess, "run") as run:
                generator.validate_candidate(
                    candidate,
                    SCRIPT_DIR / "fixtures" / "collaboration-baseline.json",
                    "swiss",
                )

            command = run.call_args.args[0]
            self.assertIn("--screenshots-dir", command)
            screenshots = Path(command[command.index("--screenshots-dir") + 1])
            self.assertEqual(screenshots, candidate.parent / "screenshots")

    def test_screenshot_content_validation_accepts_theme_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-visual-") as tmp:
            screenshot = Path(tmp) / "slide.png"
            theme = generator.direction("swiss")
            image = Image.new("RGB", (1280, 720), f"#{theme['paper']}")
            draw = ImageDraw.Draw(image)
            draw.rectangle((40, 40, 360, 260), fill=f"#{theme['ink']}")
            draw.rectangle((400, 40, 520, 160), fill=f"#{theme['accent']}")
            image.save(screenshot)

            validator.validate_screenshot(screenshot, theme)

    def test_screenshot_content_validation_rejects_blank_image(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-visual-") as tmp:
            screenshot = Path(tmp) / "slide.png"
            Image.new("RGB", (1280, 720), "white").save(screenshot)

            with self.assertRaisesRegex(SystemExit, "视觉内容为空白"):
                validator.validate_screenshot(screenshot, generator.direction("swiss"))

    def test_validation_failure_preserves_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as tmp:
            output = Path(tmp) / "deck.pptx"
            output.write_bytes(b"old")

            def render(_data: dict, _theme: dict, candidate: Path) -> None:
                candidate.write_bytes(b"candidate")

            with (
                patch.object(generator, "render_deck", side_effect=render),
                patch.object(generator, "validate_candidate", side_effect=RuntimeError("synthetic validation failure")),
                patch.object(generator, "close_quietly"),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic validation failure"):
                    self.publish(output)

            self.assertEqual(output.read_bytes(), b"old")

    def test_validated_candidate_replaces_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as tmp:
            output = Path(tmp) / "deck.pptx"
            output.write_bytes(b"old")

            def render(_data: dict, _theme: dict, candidate: Path) -> None:
                candidate.write_bytes(b"candidate")

            with (
                patch.object(generator, "render_deck", side_effect=render),
                patch.object(generator, "validate_candidate"),
                patch.object(generator, "close_quietly"),
            ):
                self.publish(output)

            self.assertEqual(output.read_bytes(), b"candidate")
            self.assertEqual([path for path in output.parent.iterdir() if path.is_dir()], [])

    def test_publish_failure_preserves_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as tmp:
            output = Path(tmp) / "deck.pptx"
            output.write_bytes(b"old")

            def render(_data: dict, _theme: dict, candidate: Path) -> None:
                candidate.write_bytes(b"candidate")

            with (
                patch.object(generator, "render_deck", side_effect=render),
                patch.object(generator, "validate_candidate"),
                patch.object(generator.os, "replace", side_effect=OSError("synthetic publish failure")),
                patch.object(generator, "close_quietly"),
            ):
                with self.assertRaisesRegex(OSError, "synthetic publish failure"):
                    self.publish(output)

            self.assertEqual(output.read_bytes(), b"old")
            self.assertEqual([path for path in output.parent.iterdir() if path.is_dir()], [])


if __name__ == "__main__":
    unittest.main()

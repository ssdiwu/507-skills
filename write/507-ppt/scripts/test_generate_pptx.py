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
from visual_plan import plan_for_preset


class GeneratePptxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.input = SCRIPT_DIR / "fixtures/collaboration-baseline.json"
        import json
        self.data = json.loads(self.input.read_text(encoding="utf-8"))
        self.plan = plan_for_preset(self.data, "swiss")

    def fake_validation(self, _candidate: Path, _input: Path, _preset: str | None, _plan: Path | None, screenshots: Path) -> None:
        screenshots.mkdir(parents=True)
        (screenshots / "slide-1.png").write_bytes(b"evidence")

    def publish(self, output: Path, evidence: Path) -> Path:
        return generator.publish_pptx(self.data, self.plan, self.input, output, preset_name="swiss", evidence_dir=evidence)

    def test_generation_failure_preserves_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as temporary:
            output = Path(temporary) / "deck.pptx"
            evidence = Path(temporary) / "evidence"
            output.write_bytes(b"old")

            def fail(_data, _plan, _input, candidate):
                candidate.write_bytes(b"partial")
                raise RuntimeError("synthetic generation failure")

            with patch.object(generator, "render_deck", side_effect=fail), patch.object(generator, "close_quietly"):
                with self.assertRaisesRegex(RuntimeError, "synthetic generation failure"):
                    self.publish(output, evidence)
            self.assertEqual(output.read_bytes(), b"old")
            self.assertFalse(evidence.exists())

    def test_candidate_validation_includes_screenshots_and_plan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as temporary:
            candidate = Path(temporary) / "deck.pptx"
            screenshots = Path(temporary) / "screens"
            plan = Path(temporary) / "plan.json"
            with patch.object(generator.subprocess, "run") as run:
                generator.validate_candidate(candidate, self.input, None, plan, screenshots)
            command = run.call_args.args[0]
            self.assertEqual(Path(command[command.index("--screenshots-dir") + 1]), screenshots)
            self.assertEqual(Path(command[command.index("--plan") + 1]), plan)

    def test_candidate_validation_is_explicitly_scoped(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as temporary:
            candidate = Path(temporary) / "deck.pptx"
            screenshots = Path(temporary) / "screens"
            plan = Path(temporary) / "plan.json"
            with patch.object(generator.subprocess, "run") as run:
                generator.validate_candidate(candidate, self.input, None, plan, screenshots, allow_candidate=True)
            self.assertIn("--allow-candidate", run.call_args.args[0])

    def test_media_layout_covers_every_declared_asset(self) -> None:
        for count in (1, 2, 3):
            layout = generator.media_layout(count, "photo-led")
            self.assertEqual(len(layout), count)
            self.assertEqual(len({item[0] for item in layout}), count)

    def test_missing_picture_never_falls_back_to_project_placeholder(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-asset-") as temporary:
            with self.assertRaisesRegex(FileNotFoundError, "missing-client-shot"):
                generator.add_picture(Path(temporary) / "deck.pptx", 1, {"id": "client", "path": "missing-client-shot.png", "alt": "client"}, self.input, "1cm", "1cm", "5cm", "3cm")

    def test_dense_treatment_changes_pptx_typographic_density(self) -> None:
        theme = generator.language("precision-modern", "dense")
        with patch.object(generator, "run") as run:
            generator.add_shape(Path("deck.pptx"), 1, "密集页", "1cm", "1cm", "5cm", "1cm", 20, theme["ink"], theme)
        command = run.call_args.args
        size_props = [command[index + 1] for index, value in enumerate(command[:-1]) if value == "--prop" and command[index + 1].startswith("size=")]
        self.assertIn("size=18", size_props)

    def test_relationship_node_bodies_are_rendered(self) -> None:
        slide = {
            "id": "relation", "component": "relationship", "title": "关系", "notes": "说明",
            "nodes": [{"id": "a", "label": "甲", "body": "甲节点解释"}, {"id": "b", "label": "乙", "body": "乙节点解释"}],
            "edges": [{"from": "a", "to": "b", "label": "关联"}],
        }
        visual = {"presentation": "schematic-led", "treatment": "default", "textFlow": {}}
        with patch.object(generator, "add_shape") as add_shape, patch.object(generator, "add_header"), patch.object(generator, "add_note"):
            generator.render_slide(Path("deck.pptx"), 1, slide, visual, "precision-modern", "关系测试", 1, self.input)
        rendered = [call.args[2] for call in add_shape.call_args_list]
        self.assertIn("甲节点解释", rendered)
        self.assertIn("乙节点解释", rendered)

    def test_screenshot_validation_accepts_language_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-visual-") as temporary:
            screenshot = Path(temporary) / "slide.png"
            theme = generator.language("precision-modern")
            image = Image.new("RGB", (1280, 720), f"#{theme['paper']}")
            draw = ImageDraw.Draw(image)
            draw.rectangle((40, 40, 360, 260), fill=f"#{theme['ink']}")
            draw.rectangle((400, 40, 520, 160), fill=f"#{theme['accent']}")
            image.save(screenshot)
            validator.validate_screenshot(screenshot, theme)

    def test_screenshot_validation_rejects_blank_image(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-visual-") as temporary:
            screenshot = Path(temporary) / "slide.png"
            Image.new("RGB", (1280, 720), "white").save(screenshot)
            with self.assertRaisesRegex(SystemExit, "视觉内容为空白"):
                validator.validate_screenshot(screenshot, generator.language("precision-modern"))

    def test_validation_failure_preserves_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as temporary:
            output = Path(temporary) / "deck.pptx"
            evidence = Path(temporary) / "evidence"
            output.write_bytes(b"old")

            def render(_data, _plan, _input, candidate):
                candidate.write_bytes(b"candidate")

            with patch.object(generator, "render_deck", side_effect=render), patch.object(generator, "validate_candidate", side_effect=RuntimeError("synthetic validation failure")), patch.object(generator, "close_quietly"):
                with self.assertRaisesRegex(RuntimeError, "synthetic validation failure"):
                    self.publish(output, evidence)
            self.assertEqual(output.read_bytes(), b"old")
            self.assertFalse(evidence.exists())

    def test_validated_candidate_replaces_output_and_preserves_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as temporary:
            output = Path(temporary) / "deck.pptx"
            evidence = Path(temporary) / "evidence"
            output.write_bytes(b"old")

            def render(_data, _plan, _input, candidate):
                candidate.write_bytes(b"candidate")

            with patch.object(generator, "render_deck", side_effect=render), patch.object(generator, "validate_candidate", side_effect=self.fake_validation), patch.object(generator, "close_quietly"):
                result = self.publish(output, evidence)
            self.assertEqual(output.read_bytes(), b"candidate")
            self.assertEqual(result, evidence)
            self.assertEqual((evidence / "slide-1.png").read_bytes(), b"evidence")

    def test_publish_failure_removes_staged_evidence_and_preserves_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pptx-atomic-") as temporary:
            output = Path(temporary) / "deck.pptx"
            evidence = Path(temporary) / "evidence"
            output.write_bytes(b"old")

            def render(_data, _plan, _input, candidate):
                candidate.write_bytes(b"candidate")

            original_replace = generator.os.replace

            def replace(source, destination):
                if Path(destination) == output:
                    raise OSError("synthetic publish failure")
                return original_replace(source, destination)

            with patch.object(generator, "render_deck", side_effect=render), patch.object(generator, "validate_candidate", side_effect=self.fake_validation), patch.object(generator.os, "replace", side_effect=replace), patch.object(generator, "close_quietly"):
                with self.assertRaisesRegex(OSError, "synthetic publish failure"):
                    self.publish(output, evidence)
            self.assertEqual(output.read_bytes(), b"old")
            self.assertFalse(evidence.exists())


if __name__ == "__main__":
    unittest.main()

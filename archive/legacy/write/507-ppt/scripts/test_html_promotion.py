#!/usr/bin/env python3
"""Regression checks for browser-evidence-gated HTML promotion."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "scripts/fixtures/presentation-pairwise.json"
PLAN = ROOT / "scripts/fixtures/presentation-pairwise.visual-plan.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_test_png(path: Path, label: str) -> None:
    image = Image.new("RGB", (640, 360), "#eef2f6")
    draw = ImageDraw.Draw(image)
    draw.rectangle((32, 32, 608, 328), fill="#234d6f")
    draw.text((64, 64), label, fill="white")
    image.save(path, format="PNG")


class HtmlPromotionTests(unittest.TestCase):
    def scaffold(self, *, failed_page: int | None = None) -> tuple[Path, Path, Path, Path]:
        temporary = tempfile.TemporaryDirectory(prefix="html-promote-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        candidate = root / "candidate.html"
        subprocess.run([
            "python3", "-B", str(ROOT / "scripts/generate_html.py"), "--input", str(INPUT), "--plan", str(PLAN),
            "--candidate-only", "--output", str(candidate),
        ], check=True, capture_output=True, text=True)
        evidence = root / "candidate-evidence"
        evidence.mkdir()
        slide_ids = [slide["id"] for slide in json.loads(INPUT.read_text(encoding="utf-8"))["slides"]]
        plan_slides = {slide["id"]: slide for slide in json.loads(PLAN.read_text(encoding="utf-8"))["slides"]}
        pages = []
        for index, slide_id in enumerate(slide_ids, start=1):
            screenshot = evidence / f"slide-{index}.png"
            write_test_png(screenshot, f"slide {index}")
            status = "failed" if failed_page == index else "passed"
            pages.append({
                "id": slide_id, "currentId": slide_id, "statusText": f"{index} / {len(slide_ids)}", "settled": True,
                "transitionMs": 0, "offsetErrorPx": 0, "overflow": "pass", "phraseOverflow": [], "screenshot": screenshot.name,
                "screenshotSha256": digest(screenshot), "status": status,
                "tableBackground": None,
                "textFlows": {path: {"lines": min(1, spec["maxLines"]), "maxLines": spec["maxLines"], "status": "passed"} for path, spec in (plan_slides[slide_id].get("textFlow") or {}).items() if isinstance(spec.get("maxLines"), int)},
            })
        profiles = {
            "desktop": {"status": "passed"},
            "mobile": {"status": "passed", "overflow": "pass", "responsive": "pass", "phraseOverflow": []},
            "reducedMotion": {"status": "passed", "motion": "reduced", "transitionMs": 0, "staticClass": False},
            "failureFallback": {"status": "passed", "staticClass": True, "visible": len(slide_ids), "deckTransform": "none", "currentId": slide_ids[min(1, len(slide_ids) - 1)], "statusText": f"{min(1, len(slide_ids) - 1) + 1} / {len(slide_ids)}"},
            "resizeRecovery": {"status": "passed", "narrowLines": 2, "wideLines": 1},
            "noJavaScript": {"status": "passed", "visible": len(slide_ids), "scrollHeight": 900 * len(slide_ids), "viewport": 900, "pagesHaveViewportHeight": True, "containsTitle": True, "screenshot": "no-javascript.png"},
            "interactions": {"status": "passed", "button": True, "keyboard": True, "wheel": True, "touch": True, "focus": True},
        }
        no_javascript = evidence / "no-javascript.png"
        write_test_png(no_javascript, "no javascript")
        profiles["noJavaScript"]["screenshotSha256"] = digest(no_javascript)
        report = {
            "version": 1, "kind": "html-browser", "status": "passed", "failures": [],
            "producer": {"name": "html_browser_evidence.py", "sourceSha256": digest(ROOT / "scripts/html_browser_evidence.py"), "browser": "test-browser", "browserVersion": "1", "generatedAt": "2026-08-24T00:00:00Z", "gitRevision": "test"},
            "subject": {"inputId": "presentation-pairwise", "inputSha256": digest(INPUT), "visualPlanSha256": digest(PLAN), "artifactSha256": digest(candidate), "carrier": "html"},
            "checks": [{"name": "pages", "status": "passed"}], "profiles": profiles, "pages": pages,
        }
        (evidence / "browser-report.json").write_text(json.dumps(report), encoding="utf-8")
        return root, candidate, evidence, root / "final.html"

    def run_promote(self, candidate: Path, evidence: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([
            "python3", "-B", str(ROOT / "scripts/promote_html.py"), "--candidate", str(candidate), "--input", str(INPUT), "--plan", str(PLAN),
            "--evidence-source", str(evidence), "--evidence-dir", str(output.with_name("final-evidence")), "--output", str(output),
        ], text=True, capture_output=True, check=False)

    def test_failed_page_preserves_previous_output(self) -> None:
        _, candidate, evidence, output = self.scaffold(failed_page=3)
        output.write_bytes(b"old")
        result = self.run_promote(candidate, evidence, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"old")
        self.assertFalse(output.with_name("final-evidence").exists())

    def test_valid_report_promotes_candidate_and_evidence(self) -> None:
        _, candidate, evidence, output = self.scaffold()
        output.write_bytes(b"old")
        result = self.run_promote(candidate, evidence, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_bytes(), candidate.read_bytes())
        self.assertTrue((output.with_name("final-evidence") / "browser-report.json").is_file())

    def test_stale_artifact_hash_preserves_previous_output(self) -> None:
        _, candidate, evidence, output = self.scaffold()
        output.write_bytes(b"old")
        candidate.write_text("changed after browser review", encoding="utf-8")
        result = self.run_promote(candidate, evidence, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"old")

    def test_failed_profile_fields_cannot_hide_behind_passed_status(self) -> None:
        _, candidate, evidence, output = self.scaffold()
        output.write_bytes(b"old")
        report = evidence / "browser-report.json"
        data = json.loads(report.read_text(encoding="utf-8"))
        data["profiles"]["mobile"]["overflow"] = "fail"
        report.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_promote(candidate, evidence, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"old")

    def test_non_image_screenshot_preserves_previous_output(self) -> None:
        _, candidate, evidence, output = self.scaffold()
        output.write_bytes(b"old")
        report = evidence / "browser-report.json"
        data = json.loads(report.read_text(encoding="utf-8"))
        screenshot = evidence / data["pages"][0]["screenshot"]
        screenshot.write_bytes(b"not a png")
        data["pages"][0]["screenshotSha256"] = digest(screenshot)
        report.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_promote(candidate, evidence, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"old")
        self.assertIn("PNG", result.stderr)

    def test_zero_line_text_flow_cannot_be_reported_as_passed(self) -> None:
        _, candidate, evidence, output = self.scaffold()
        output.write_bytes(b"old")
        report = evidence / "browser-report.json"
        data = json.loads(report.read_text(encoding="utf-8"))
        page = next(item for item in data["pages"] if item["textFlows"])
        next(iter(page["textFlows"].values()))["lines"] = 0
        report.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_promote(candidate, evidence, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"old")
        self.assertIn("text-flow", result.stderr)


if __name__ == "__main__":
    unittest.main()

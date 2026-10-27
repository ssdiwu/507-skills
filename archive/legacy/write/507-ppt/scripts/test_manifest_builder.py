#!/usr/bin/env python3
"""Public CLI regressions for manifest construction and input portability."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = ROOT / "examples/system-prototypes"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ManifestBuilderTests(unittest.TestCase):
    def scaffold(self) -> tuple[Path, Path, Path, Path, Path, Path]:
        temporary = tempfile.TemporaryDirectory(prefix="manifest-builder-")
        self.addCleanup(temporary.cleanup)
        package = Path(temporary.name) / "package"
        fixtures = package / "scripts/fixtures"
        examples = package / "examples"
        evidence = examples / "evidence"
        fixtures.mkdir(parents=True)
        evidence.mkdir(parents=True)
        content = json.loads((PROTOTYPE / "prototype-content.json").read_text(encoding="utf-8"))
        input_path = fixtures / "builder-fixture.json"
        input_path.write_text(json.dumps(content), encoding="utf-8")
        fixture_assets = fixtures / "assets"
        fixture_assets.mkdir()
        shutil.copyfile(ROOT / "assets/workbench.svg", fixture_assets / "workbench.svg")
        plan_path = examples / "builder.visual-plan.json"
        plan = json.loads((PROTOTYPE / "candidate-a-swiss.visual-plan.json").read_text(encoding="utf-8"))
        plan["prototype"] = {"mode": "deterministic-regression", "status": "skipped", "skipReason": "manifest builder fixture"}
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        artifact = examples / "builder.pptx"
        shutil.copyfile(PROTOTYPE / "candidate-a-swiss.pptx", artifact)
        for screenshot in sorted((PROTOTYPE / "candidate-a-swiss-pptx-evidence").glob("slide-*.png")):
            shutil.copyfile(screenshot, evidence / screenshot.name)
        matrix = examples / "support.json"
        result = subprocess.run([
            "python3", "-B", str(ROOT / "scripts/build_support_matrix.py"), "--input", str(input_path),
            "--plan", str(plan_path), "--output", str(matrix),
        ], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = examples / "axis.json"
        result = subprocess.run([
            "python3", "-B", str(ROOT / "scripts/check_style_content.py"), "--fixture", str(input_path), "--plan", str(plan_path),
            "--carrier", "pptx", "--artifact", str(artifact), "--screenshots-dir", str(evidence), "--output", str(report),
        ], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return examples, input_path, plan_path, artifact, evidence, report

    def run_builder(self, examples: Path, input_path: Path, plan_path: Path, artifact: Path, evidence: Path, report: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([
            "python3", "-B", str(ROOT / "scripts/build_manifest.py"), "--input", str(input_path), "--plan", str(plan_path),
            "--artifact", str(artifact), "--carrier", "pptx", "--screenshots-dir", str(evidence),
            "--verification", str(report), "--support-matrix", str(examples / "support.json"),
            "--output", str(examples / "builder.pptx.manifest.json"),
        ], text=True, capture_output=True, check=False)

    def test_builder_records_real_input_and_produces_a_valid_manifest(self) -> None:
        examples, input_path, plan_path, artifact, evidence, report = self.scaffold()
        result = self.run_builder(examples, input_path, plan_path, artifact, evidence, report)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = examples / "builder.pptx.manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(data["input"], "../scripts/fixtures/builder-fixture.json")
        validation = subprocess.run(["python3", "-B", str(ROOT / "scripts/validate_manifest.py"), str(manifest)], text=True, capture_output=True, check=False)
        self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_builder_rejects_html_disguised_as_pptx_carrier(self) -> None:
        examples, input_path, plan_path, _artifact, evidence, report = self.scaffold()
        artifact = examples / "builder.html"
        artifact.write_text('<!doctype html><main id="deck"><section class="slide">x</section></main>', encoding="utf-8")
        report_data = json.loads(report.read_text(encoding="utf-8"))
        report_data["subject"]["artifactSha256"] = digest(artifact)
        report.write_text(json.dumps(report_data), encoding="utf-8")
        result = self.run_builder(examples, input_path, plan_path, artifact, evidence, report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact format", result.stderr)

    def test_builder_rejects_input_outside_manifest_package(self) -> None:
        examples, input_path, plan_path, artifact, evidence, report = self.scaffold()
        outside = examples.parents[1] / "outside-input.json"
        outside.write_bytes(input_path.read_bytes())
        result = self.run_builder(examples, outside, plan_path, artifact, evidence, report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("input must stay within manifest package root", result.stderr)

    def test_builder_failure_preserves_existing_manifest(self) -> None:
        examples, input_path, plan_path, artifact, evidence, report = self.scaffold()
        first = self.run_builder(examples, input_path, plan_path, artifact, evidence, report)
        self.assertEqual(first.returncode, 0, first.stderr)
        output = examples / "builder.pptx.manifest.json"
        previous = output.read_bytes()
        (evidence / "slide-1.png").write_bytes(b"not a png")
        failed = self.run_builder(examples, input_path, plan_path, artifact, evidence, report)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(output.read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()

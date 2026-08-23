#!/usr/bin/env python3
"""Regression tests for legacy manifest v1 and resolver-bound manifest v2."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from design_system import normalize_deck
from visual_plan import expected_degradations, resolved_manifest_pages

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "scripts/fixtures/system-showcase.json"
SHOWCASE_PLAN = ROOT / "scripts/fixtures/system-showcase.visual-plan.json"
LEGACY = ROOT / "scripts/fixtures/collaboration-baseline.json"
APPROVED = ROOT / "examples/system-prototypes/approved-prototype-manifest.json"
CONTACT = ROOT / "examples/system-prototypes/contact-sheet.png"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ManifestContractTests(unittest.TestCase):
    def scaffold(self, source: Path) -> tuple[Path, Path, dict]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name) / "deck"
        fixtures = repository / "scripts/fixtures"
        examples = repository / "examples"
        fixtures.mkdir(parents=True)
        examples.mkdir()
        fixture = fixtures / source.name
        shutil.copyfile(source, fixture)
        artifact = examples / "showcase.html"
        artifact.write_text("<!doctype html><title>showcase</title>", encoding="utf-8")
        (examples / "report.txt").write_text("passed\n", encoding="utf-8")
        (examples / "matrix.txt").write_text("passed\n", encoding="utf-8")
        return examples, fixture, json.loads(source.read_text(encoding="utf-8"))

    def validate(self, manifest: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", "-B", str(ROOT / "scripts/validate_manifest.py"), str(manifest)], text=True, capture_output=True, check=False)

    def valid_v2(self) -> tuple[Path, dict]:
        examples, fixture, raw = self.scaffold(SHOWCASE)
        artifact = examples / "showcase.html"
        plan_path = examples / "showcase.visual-plan.json"
        shutil.copyfile(SHOWCASE_PLAN, plan_path)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        content = normalize_deck(raw)
        expected = resolved_manifest_pages(plan, raw, "pptx")
        screenshots: list[str] = []
        pages = []
        for index, (slide, contract) in enumerate(zip(content["slides"], expected, strict=True), start=1):
            screenshot = f"slide-{index}.png"
            (examples / screenshot).write_bytes(b"png")
            screenshots.append(screenshot)
            page = dict(contract)
            page.update({
                "textFlowStatus": "screenshot-verified", "notesStatus": "provided" if slide.get("notes") else "declared-none",
                "altStatus": "provided" if slide.get("assets") else "not-applicable", "assets": [asset["id"] for asset in slide.get("assets") or []],
                "screenshot": screenshot, "screenshotSha256": digest(examples / screenshot),
            })
            pages.append(page)
        assets_dir = examples.parent / "assets"
        assets_dir.mkdir()
        asset_path = assets_dir / "workbench.svg"
        shutil.copyfile(ROOT / "assets/workbench.svg", asset_path)
        assets = [{"id": "workbench", "path": "../assets/workbench.svg", "alt": "包含文件、编辑器和预览区域的抽象工作台示意图", "sha256": digest(asset_path)}]
        prototype_manifest = examples / "approved-prototype-manifest.json"
        contact = examples / "contact-sheet.png"
        shutil.copyfile(APPROVED, prototype_manifest)
        shutil.copyfile(CONTACT, contact)
        support = examples / "support.json"
        support.write_text(json.dumps({"version": 1, "inputId": "system-showcase", "language": plan["language"], "carriers": {"pptx": {"pages": [{**page, "compatibility": "preferred"} for page in expected]}}}), encoding="utf-8")
        subject = {"inputId": "system-showcase", "inputSha256": digest(fixture), "visualPlanSha256": digest(plan_path), "artifactSha256": digest(artifact), "carrier": "pptx"}
        report = examples / "report.json"
        report.write_text(json.dumps({"version": 1, "kind": "axis-content", "status": "passed", "failures": [], "subject": subject, "checks": [{"name": "contract", "status": "passed"}]}), encoding="utf-8")
        approved_data = json.loads(APPROVED.read_text(encoding="utf-8"))
        manifest = {
            "version": 2, "inputId": "system-showcase", "inputSha256": digest(fixture), "carrier": "pptx", "artifact": "showcase.html", "sha256": digest(artifact),
            "visualPlan": "showcase.visual-plan.json", "visualPlanSha256": digest(plan_path), "language": plan["language"], "prototypeStatus": "approved",
            "prototypeEvidence": [
                {"kind": "prototype-manifest", "path": prototype_manifest.name, "sha256": plan["prototype"]["manifestSha256"]},
                {"kind": "prototype-contact-sheet", "path": contact.name, "sha256": approved_data["evidenceSha256"]},
            ],
            "pages": pages, "assets": assets, "notices": [],
            "verification": [{"name": "contract", "kind": "axis-content", "status": "passed", "evidence": report.name, "evidenceSha256": digest(report)}],
            "screenshots": screenshots, "degradations": expected_degradations(plan, raw, "pptx"),
            "capabilities": {"supportMatrix": support.name, "supportMatrixSha256": digest(support)},
        }
        return examples, manifest

    def test_legacy_v1_still_validates(self) -> None:
        examples, fixture, raw = self.scaffold(LEGACY)
        artifact = examples / "showcase.html"
        manifest = {
            "version": 1, "inputId": "collaboration-baseline", "inputSha256": digest(fixture), "style": "forest", "carrier": "html",
            "artifact": "showcase.html", "sha256": digest(artifact),
            "pages": [{"id": slide["id"], "notes": True, "assets": [], "altStatus": "not-applicable"} for slide in raw["slides"]],
            "assets": [], "notices": [], "verification": [{"name": "contract", "status": "passed", "evidence": "report.txt"}],
            "screenshots": [], "degradations": [], "capabilities": {"fallbackMatrix": "matrix.txt"},
        }
        path = examples / "legacy.manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.validate(path)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_v2_validates_resolver_and_evidence_contracts(self) -> None:
        examples, manifest = self.valid_v2()
        path = examples / "v2.manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.validate(path)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_v2_rejects_support_suppression_and_degradation_tampering(self) -> None:
        mutations = (
            (lambda data: data["pages"][1].update(carrierSupport="native"), "resolver output"),
            (lambda data: data["pages"][-1].update(suppressedDecorations=[]), "resolver output"),
            (lambda data: data.update(degradations=[]), "degradations"),
            (lambda data: data["degradations"].append({"pageId": "cover", "reason": "fake"}), "degradations"),
        )
        for mutation, expected in mutations:
            with self.subTest(expected=expected):
                examples, manifest = self.valid_v2()
                mutation(manifest)
                path = examples / "broken.manifest.json"
                path.write_text(json.dumps(manifest), encoding="utf-8")
                result = self.validate(path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_v2_rejects_failed_verification_report(self) -> None:
        examples, manifest = self.valid_v2()
        report = examples / manifest["verification"][0]["evidence"]
        report_data = json.loads(report.read_text(encoding="utf-8"))
        report_data["checks"][0]["status"] = "failed"
        report.write_text(json.dumps(report_data), encoding="utf-8")
        manifest["verification"][0]["evidenceSha256"] = digest(report)
        path = examples / "broken-report.manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.validate(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checks", result.stderr)

    def test_v2_rejects_stale_support_matrix(self) -> None:
        examples, manifest = self.valid_v2()
        matrix = examples / manifest["capabilities"]["supportMatrix"]
        matrix_data = json.loads(matrix.read_text(encoding="utf-8"))
        matrix_data["carriers"]["pptx"]["pages"][0]["carrierSupport"] = "adapted"
        matrix.write_text(json.dumps(matrix_data), encoding="utf-8")
        manifest["capabilities"]["supportMatrixSha256"] = digest(matrix)
        path = examples / "broken-matrix.manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.validate(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("support matrix", result.stderr)


if __name__ == "__main__":
    unittest.main()

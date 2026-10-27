#!/usr/bin/env python3
"""Public CLI regressions for prototype generation and mixed approval evidence."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "scripts/fixtures/system-showcase.json"


def write_png(path: Path, label: str) -> None:
    image = Image.new("RGB", (960, 540), "#ede9df")
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 920, 500), fill="#1f3449")
    draw.text((80, 80), label, fill="white")
    image.save(path, format="PNG")


class PrototypeWorkflowTests(unittest.TestCase):
    def package(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="prototype-workflow-")
        self.addCleanup(temporary.cleanup)
        package = Path(temporary.name) / "package"
        subprocess.run([
            "python3", "-B", str(ROOT / "scripts/generate_prototypes.py"),
            "--input", str(INPUT), "--output-dir", str(package),
        ], check=True, capture_output=True, text=True)
        return package

    def test_mixed_approval_binds_real_merged_artifact_plan_and_evidence(self) -> None:
        package = self.package()
        merged_artifact = package / "merged.html"
        merged_plan = package / "merged.visual-plan.json"
        merged_evidence = package / "merged-contact-sheet.png"
        contact_sheet = package / "contact-sheet.png"
        merged_pptx = package / "merged.pptx"
        merged_pptx_evidence = package / "merged-pptx-evidence"
        merged_artifact.write_bytes((package / "candidate-a-swiss.html").read_bytes())
        merged_plan.write_bytes((package / "candidate-a-swiss.visual-plan.json").read_bytes())
        write_png(merged_evidence, "merged")
        write_png(contact_sheet, "all candidates")
        shutil.copyfile(ROOT / "examples/system-prototypes/candidate-a-swiss.pptx", merged_pptx)
        shutil.copytree(ROOT / "examples/system-prototypes/candidate-a-swiss-pptx-evidence", merged_pptx_evidence)
        output = package / "approved.json"
        result = subprocess.run([
            "python3", "-B", str(ROOT / "scripts/finalize_prototype.py"),
            "--manifest", str(package / "prototype-manifest.json"), "--selected", "A",
            "--mixed-from", "A", "--mixed-from", "B", "--merged-artifact", str(merged_artifact),
            "--merged-plan", str(merged_plan), "--merged-evidence", str(merged_evidence),
            "--pptx-artifact", str(merged_pptx), "--pptx-evidence-dir", str(merged_pptx_evidence),
            "--evidence", str(contact_sheet), "--output", str(output),
        ], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        approved = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(approved["mixedFrom"], ["A", "B"])
        self.assertEqual(approved["mergedPrototype"]["artifact"], merged_artifact.name)
        self.assertEqual(approved["targetEvidence"]["html"]["artifact"], merged_artifact.name)
        self.assertEqual(approved["targetEvidence"]["pptx"]["visualPlan"], merged_plan.name)
        self.assertEqual(approved["targetEvidence"]["pptx"]["visualPlanSha256"], approved["mergedPrototype"]["visualPlanSha256"])

    def test_mixed_approval_rejects_missing_merged_evidence(self) -> None:
        package = self.package()
        contact_sheet = package / "contact-sheet.png"
        write_png(contact_sheet, "all candidates")
        result = subprocess.run([
            "python3", "-B", str(ROOT / "scripts/finalize_prototype.py"),
            "--manifest", str(package / "prototype-manifest.json"), "--selected", "A",
            "--mixed-from", "A", "--mixed-from", "B", "--evidence", str(contact_sheet),
            "--output", str(package / "approved.json"),
        ], text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("merged-artifact", result.stderr)


if __name__ == "__main__":
    unittest.main()

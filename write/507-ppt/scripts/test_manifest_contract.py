#!/usr/bin/env python3
"""Regression test: manifests accept every public direction and arbitrary input length."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "scripts/fixtures/system-showcase.json"


class ManifestContractTests(unittest.TestCase):
    def test_showcase_manifest_accepts_extended_direction_and_page_mapping(self) -> None:
        data = json.loads(SHOWCASE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "deck"
            fixtures = repository / "scripts/fixtures"
            examples = repository / "examples"
            fixtures.mkdir(parents=True)
            examples.mkdir()
            fixture = fixtures / "system-showcase.json"
            shutil.copyfile(SHOWCASE, fixture)
            artifact = examples / "showcase.html"
            artifact.write_text("<!doctype html><title>showcase</title>", encoding="utf-8")
            for evidence in ("report.txt", "matrix.txt"):
                (examples / evidence).write_text("passed\n", encoding="utf-8")
            manifest = {
                "version": 1,
                "inputId": "system-showcase",
                "inputSha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
                "style": "forest",
                "carrier": "html",
                "artifact": "showcase.html",
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "pages": [{"id": slide["id"], "notes": True, "assets": [], "altStatus": "not-applicable"} for slide in data["slides"]],
                "assets": [],
                "notices": [],
                "verification": [{"name": "contract", "status": "passed", "evidence": "report.txt"}],
                "screenshots": [],
                "degradations": [],
                "capabilities": {"fallbackMatrix": "matrix.txt"},
            }
            manifest_path = examples / "showcase.manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(["python3", str(ROOT / "scripts/validate_manifest.py"), str(manifest_path)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

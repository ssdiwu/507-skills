"""Verify real maintenance entrypoints remain reachable after the layout move."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LayoutTests(unittest.TestCase):
    def test_current_and_archived_roots_are_unambiguous(self):
        for name in ('next', 'common', 'code', 'write', 'archive'):
            self.assertFalse((ROOT / name).exists(), name)
        self.assertTrue((ROOT / 'packages.json').is_file())
        self.assertTrue((ROOT / 'skills/README.md').is_file())

    def test_ci_uses_the_real_current_maintenance_entrypoints(self):
        workflow = (ROOT / '.github/workflows/tests.yml').read_text()
        self.assertIn('python scripts/package_skills.py check', workflow)
        self.assertIn('unittest discover -s tests -v', workflow)
        self.assertIn('python scripts/test_all.py', workflow)
        self.assertNotIn('next/', workflow)


class ResourceMapTests(unittest.TestCase):
    def test_command_examples_resolve_against_shared_library(self):
        import re
        documents = [*(ROOT / 'skills').rglob('*.md'), *(ROOT / 'lib/components/tools').rglob('*.md')]
        for document in documents:
            for relative in re.findall(r'<共有库>/([\w./-]+\.(?:py|mjs|md|tsx|json))\b', document.read_text()):
                with self.subTest(document=document, relative=relative):
                    self.assertTrue((ROOT / 'lib' / relative).is_file())

    def test_all_skill_resource_map_matches_current_contracts_and_manifest(self):
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT/'scripts/resource_map.py'), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

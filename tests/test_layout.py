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
        self.assertIn('gitleaks" git', workflow)
        self.assertIn('--log-opts=-m', workflow)
        self.assertIn('--redact=100', workflow)
        self.assertIn('fetch-depth: 0', workflow)
        self.assertIn('gitleaks_8.30.1_linux_x64.tar.gz', workflow)
        self.assertIn('551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb', workflow)
        self.assertIn('Scan commit history for secrets', workflow)
        self.assertIn('python3 scripts/test_gitleaks_history.py', workflow)
        self.assertLess(workflow.index('Scan commit history for secrets'),
                        workflow.index('python scripts/package_skills.py check'))
        security = (ROOT / 'SECURITY.md').read_text()
        self.assertIn('gitleaks dir --redact=100 --no-banner --no-color .', security)
        self.assertIn('不检查索引里的独立版本', security)
        self.assertIn('python scripts/package_skills.py check', workflow)
        self.assertLess(workflow.index('pip install -r requirements-package.txt'),
                        workflow.index('python scripts/package_skills.py check'))
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

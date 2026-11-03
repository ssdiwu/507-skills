"""Verify real maintenance entrypoints remain reachable after the layout move."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LayoutTests(unittest.TestCase):
    def test_current_and_archived_roots_are_unambiguous(self):
        for name in ('next', 'common', 'code', 'write'):
            self.assertFalse((ROOT / name).exists(), name)
        self.assertTrue((ROOT / 'packages.json').is_file())
        self.assertTrue((ROOT / 'skills/README.md').is_file())
        for group in ('common', 'code', 'write'):
            self.assertTrue((ROOT / 'archive/legacy' / group).is_dir())

    def test_every_legacy_regression_still_has_its_cwd_and_script(self):
        spec = importlib.util.spec_from_file_location('layout_test_runner', ROOT / 'scripts/test_all.py')
        runner = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = runner
        spec.loader.exec_module(runner)
        checks = runner.checks()
        self.assertGreaterEqual(len(checks), 30)
        for check in checks:
            with self.subTest(check=check.name):
                self.assertTrue(check.cwd.is_dir(), check.cwd)
                for value in check.command[1:]:
                    if '*' in value:
                        self.assertTrue(list(check.cwd.glob(value)), value)
                        continue
                    if value.endswith(('.py', '.sh')):
                        path = Path(value)
                        self.assertTrue((path if path.is_absolute() else check.cwd / path).is_file(), value)

    def test_ci_uses_the_real_current_maintenance_entrypoints(self):
        workflow = (ROOT / '.github/workflows/tests.yml').read_text()
        self.assertIn('python scripts/package_skills.py check', workflow)
        self.assertIn('unittest discover -s tests -v', workflow)
        self.assertNotIn('next/', workflow)


class ResourceMapTests(unittest.TestCase):
    def test_all_skill_resource_map_matches_current_contracts_and_manifest(self):
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT/'scripts/resource_map.py'), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

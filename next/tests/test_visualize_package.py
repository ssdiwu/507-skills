"""Exercise same-name current/legacy lookup using only isolated consumer files."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class VisualizeLookupTests(unittest.TestCase):
    def test_current_visualize_wins_without_losing_legacy_or_claiming_runtime(self):
        consumer = ROOT / 'next/skills/skill-design'
        with tempfile.TemporaryDirectory() as directory:
            isolated = Path(directory)
            script = isolated / 'query.py'
            index = isolated / 'index.md'
            shutil.copy2(consumer / 'scripts/library_view.py', script)
            shutil.copy2(consumer / 'references/shared/skill-entry-index.md', index)
            result = subprocess.run(
                [sys.executable, str(script), '--index-file', str(index),
                 '--lookup', '507-visualize'], cwd=isolated,
                capture_output=True, text=True, check=True)
            value = json.loads(result.stdout)
            self.assertEqual(value['status'], 'CURRENT_DECLARATION_FOUND')
            self.assertEqual([(x['name'], x['role']) for x in value['currentCandidates']],
                             [('507-visualize', 'secondary')])
            self.assertEqual(value['legacyOrigin']['source'], 'common/507-visualize/SKILL.md')
            self.assertEqual(value['runtimeAvailability'], 'NOT_CHECKED')
            self.assertEqual(value['actionAuthority'], 'UNCHANGED')
            self.assertEqual(set(p.name for p in isolated.iterdir()), {'query.py', 'index.md'})

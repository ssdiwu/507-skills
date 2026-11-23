"""Exercise same-name current/legacy lookup using only isolated consumer files."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VisualizeLookupTests(unittest.TestCase):
    def test_repository_map_connects_current_contracts_and_historical_names(self):
        result = subprocess.run(
            [sys.executable, '-B', 'lib/components/tools/projections/library_view.py',
             '--source-root', '.', '--packages', 'packages.json',
             '--catalog', 'lib/catalog/catalog.json',
             '--dispositions', 'lib/catalog/registry/skill-dispositions.json', '--library-map'],
            cwd=ROOT, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)['data']
        cards = {card['name']: card for card in data['skills']}
        entries = json.loads((ROOT / 'packages.json').read_text())['skills']
        self.assertCountEqual(cards, [entry['name'] for entry in entries])
        self.assertEqual([entry['role'] for entry in entries].count('main'), 11)
        self.assertEqual([entry['role'] for entry in entries].count('secondary'), 13)
        for entry in entries:
            name = entry['name']
            primary = entry['role'] == 'main'
            with self.subTest(name=name):
                self.assertRegex(name, r'^507-[a-z]+$' if primary else r'^507-[a-z]+-[a-z]+$')
                self.assertRegex(cards[name]['displayName'], r'^507-[一-鿿]{3}$' if primary else r'^507-[一-鿿]{4}$')
        historical = {row['id']: row for row in data['legacy']}
        for old, current in [('507-why', '507-explain'), ('507-do', '507-build'),
                             ('skill-design', '507-skill'), ('507-fix', '507-build'),
                             ('507-visualize', '507-visual-explain')]:
            self.assertIn(current, historical[old]['consumers'])
            self.assertIn(old, cards[current]['aliases'])
        self.assertEqual(historical['507-coach']['decision'], 'drop')
        self.assertEqual(historical['507-coach']['consumers'], [])
        self.assertNotIn('507-coach', cards)

    def test_current_explain_wins_without_losing_legacy_or_claiming_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            isolated = Path(directory)
            script = isolated / 'query.py'
            index = isolated / 'index.md'
            shutil.copy2(ROOT / 'lib/components/tools/projections/library_view.py', script)
            shutil.copy2(ROOT / 'lib/catalog/registry/skill-entry-index.md', index)
            result = subprocess.run(
                [sys.executable, str(script), '--index-file', str(index),
                 '--lookup', '507-explain'], cwd=isolated,
                capture_output=True, text=True, check=True)
            value = json.loads(result.stdout)
            self.assertEqual(value['status'], 'CURRENT_DECLARATION_FOUND')
            self.assertEqual([(x['name'], x['role']) for x in value['currentCandidates']],
                             [('507-explain', 'main')])
            self.assertEqual(value['legacyOrigin']['source'], 'archive/legacy/common/507-explain/SKILL.md')
            self.assertEqual(value['legacyOrigin']['sourceRevision'], 'a4c28d19bfea418333ff1487a958d33b797f2308')
            self.assertEqual(value['runtimeAvailability'], 'NOT_CHECKED')
            self.assertEqual(value['actionAuthority'], 'UNCHANGED')
            self.assertEqual(set(p.name for p in isolated.iterdir()), {'query.py', 'index.md'})

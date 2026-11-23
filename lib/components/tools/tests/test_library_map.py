import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / 'lib/components/tools/projections/library_view.py'
GUIDE = Path('lib/catalog/registry/library-map.json')
METHOD = 'lib/methods/engineering/engineering-evidence.md'


class LibraryMapTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.guide = json.loads((ROOT / GUIDE).read_text())
        self.put(GUIDE, self.guide)
        self.put(METHOD, '# 核验')
        entries = []
        for name in self.guide['cards']:
            base = f'skills/{name}'
            entries.append({'name': name, 'role': 'main', 'source': base, 'resources': 'RESOURCES.md'})
            self.put(f'{base}/SKILL.md', f'---\nname: {name}\ndescription: "{name} 用途"\n---')
            self.put(f'{base}/agents/openai.yaml', f'interface:\n  display_name: "{name} 中文"\n')
            declaration = {'schema': 1, 'files': ['SKILL.md', 'agents/openai.yaml', 'RESOURCES.md'],
                           'uses': [METHOD] if name == '507-build' else []}
            self.put(f'{base}/RESOURCES.md', '```json\n' + json.dumps(declaration) + '\n```\n')
        self.put('packages.json', {'schema': 3, 'skills': entries})
        self.catalog = {'methods': [{'source': METHOD, 'title': '核验', 'consumers': ['507-build']}], 'components': []}
        self.put('catalog.json', self.catalog)
        history = []
        for name, consumers in [('507-fix', ['507-build']), ('507-coach', [])]:
            archived = f'archive/legacy/common/{name}/SKILL.md'
            self.put(archived, f'---\nname: {name}\n---')
            history.append({'id': name, 'source': archived, 'group': 'common', 'reason': name,
                            'decision': 'merge' if consumers else 'drop', 'consumers': consumers,
                            'targets': [METHOD] if consumers else [], 'retained': consumers, 'dropped': [],
                            'verification': 'source fixture'})
        self.put('decisions.json', {'legacy': history, 'date': '2026-11-23', 'historicalPlanning': {}, 'pending': []})

    def put(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))

    def run_cli(self, *extra):
        return subprocess.run([sys.executable, '-B', str(CLI), '--source-root', '.', '--packages', 'packages.json',
                               '--catalog', 'catalog.json', '--dispositions', 'decisions.json', '--library-map', *extra],
                              cwd=self.root, capture_output=True, text=True, check=False)

    def assert_error(self, fragment):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(result.stdout, '')
        self.assertIn(fragment, json.loads(result.stderr)['error'])

    def test_source_to_renderer_model_and_backlinks(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        model = json.loads(result.stdout)
        self.assertEqual(model['kind'], 'library-map')
        data = model['data']
        self.assertEqual(set(data), {'lanes', 'crosscutting', 'recipes', 'skills', 'resources', 'legacy', 'previousLabels'})
        self.assertEqual(data['previousLabels']['507-执行'], '507-build')
        self.assertEqual((len(data['lanes']), len(data['recipes']), len(data['skills'])), (4, 6, 24))
        self.assertEqual(set(data['crosscutting']), {'507-peer-review', '507-visual-explain'})
        by_name = {row['name']: row for row in data['skills']}
        build = by_name['507-build']
        self.assertEqual(set(build), {'name', 'displayName', 'description', 'skip', 'input', 'authority', 'stop',
                                      'example', 'upstream', 'downstream', 'resources', 'aliases'})
        self.assertEqual((build['description'], build['displayName']), ('507-build 用途', '507-build 中文'))
        self.assertEqual(build['aliases'], ['507-fix'])
        self.assertEqual(build['resources'], [METHOD])
        self.assertEqual(data['resources'], [{'source': METHOD, 'title': '核验', 'consumers': ['507-build']}])
        self.assertIn({'id': '507-coach', 'reason': '507-coach', 'decision': 'drop', 'consumers': []}, data['legacy'])
        for recipe in data['recipes']:
            for before, after in zip(recipe['steps'], recipe['steps'][1:]):
                self.assertIn(after, by_name[before]['downstream'])
                self.assertIn(before, by_name[after]['upstream'])

    def test_unknown_step_rejected(self):
        self.guide['recipes'][0]['steps'][1] = '507-do'
        self.put(GUIDE, self.guide)
        self.assert_error('unknown or missing map skill')

    def test_duplicate_lane_membership_rejected(self):
        self.guide['lanes'][0]['skills'][0] = self.guide['crosscutting'][0]
        self.put(GUIDE, self.guide)
        self.assert_error('partition')

    def test_missing_card_and_empty_example_rejected(self):
        self.guide['cards']['507-build']['example'] = ' '
        self.put(GUIDE, self.guide)
        self.assert_error('invalid map card')
        del self.guide['cards']['507-build']
        self.put(GUIDE, self.guide)
        self.assert_error('map cards differ')

    def test_stale_consumers_and_missing_method_rejected(self):
        self.catalog['methods'][0]['consumers'] = []
        self.put('catalog.json', self.catalog)
        self.assert_error('resource consumers differ')
        self.catalog['methods'][0]['consumers'] = ['507-build']
        self.put('catalog.json', self.catalog)
        (self.root / METHOD).unlink()
        self.assert_error('missing source')

    def test_index_mode_remains_separate(self):
        result = self.run_cli('--emit-index')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')

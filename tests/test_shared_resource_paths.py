"""Read real shared references through the documented collection contract."""
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOW = Path('skills/507-design/SKILL.md')
NESTED = Path('skills/507-design/references/solution-design.md')
RESOURCE = Path('lib/methods/evidence-and-decisions/alternatives.md')
CONTRACT = Path('lib/README.md')
INTERACTION = Path('lib/methods/engineering/interaction.md')


class SharedResourcePathsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='507 how paths ')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.collection = self.base / 'relocated collection'
        entries = [p.relative_to(ROOT) for p in (ROOT / 'skills').glob('*/SKILL.md')]
        for relative in [*entries, NESTED, RESOURCE, CONTRACT, INTERACTION]:
            destination = self.collection / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        self.alias = self.base / 'host' / 'skills' / 'collection'
        self.alias.parent.mkdir(parents=True)
        self.alias.symlink_to(self.collection / 'skills', target_is_directory=True)
        snippet = re.search(r'```sh\n([^\n]+)\n```', (ROOT / CONTRACT).read_text()).group(1)
        self.command = shlex.split(snippet)
        self.command[0] = sys.executable
        self.expected = (self.collection / RESOURCE).resolve()

    def resolve_reference(self, document, link):
        result = subprocess.run([*self.command[:-2], str(document), link],
                                cwd=self.base, text=True, capture_output=True)
        return result

    def read_reference(self, document):
        link = re.search(r'\[候选与反证\]\(([^)]+)\)', document.read_text()).group(1)
        return self.resolve_reference(document, link)

    def assert_resource(self, document):
        result = self.read_reference(document)
        self.assertEqual(result.returncode, 0, result.stderr)
        target = Path(result.stdout.strip())
        self.assertEqual(target, self.expected)
        self.assertEqual(target.read_bytes(), (ROOT / RESOURCE).read_bytes())

    def test_real_document_in_relocated_collection(self):
        self.assert_resource(self.collection / HOW)

    def test_host_collection_symlink_resolves_shared_sibling(self):
        self.assertFalse((self.alias / 'lib/methods/evidence-and-decisions/alternatives.md').exists())
        self.assertFalse((self.alias.parent / 'lib/methods/evidence-and-decisions/alternatives.md').exists())
        self.assert_resource(self.alias / '507-design/SKILL.md')

    def test_nested_reference_uses_its_own_real_document(self):
        self.assert_resource(self.collection / NESTED)
        self.assert_resource(self.alias / '507-design/references/solution-design.md')

    def test_missing_resource_is_an_error_not_a_fallback(self):
        self.expected.unlink()
        result = self.read_reference(self.alias / '507-design/SKILL.md')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertIn('alternatives.md', result.stderr)

    def test_all_installed_entries_find_the_same_shared_contract(self):
        for entry in sorted((self.collection / 'skills').glob('*/SKILL.md')):
            with self.subTest(skill=entry.parent.name):
                document = self.alias / entry.parent.name / entry.name
                bootstrap = re.search(r'`([^`\n]*<本文件路径>[^`\n]*)`', entry.read_text()).group(1)
                result = subprocess.run(['sh', '-c', bootstrap.replace('<本文件路径>', shlex.quote(str(document)))],
                                        cwd=self.base, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, (self.collection / CONTRACT).read_text())
                link = re.search(r'\[共有资源合同\]\(([^)]+)\)', entry.read_text()).group(1)
                result = self.resolve_reference(document, link)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(Path(result.stdout.strip()).samefile(self.collection / CONTRACT))

    def test_invalid_document_does_not_read_a_contract_from_working_directory(self):
        entry = self.collection / 'skills/507-adapt/SKILL.md'
        bootstrap = re.search(r'`([^`\n]*<本文件路径>[^`\n]*)`', entry.read_text()).group(1)
        for invalid in [self.alias / 'absent/SKILL.md', self.alias / '507-adapt']:
            with self.subTest(document=str(invalid)):
                result = subprocess.run(['sh', '-c', bootstrap.replace('<本文件路径>', shlex.quote(str(invalid)))],
                                        cwd=entry.parent, text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')

    def test_adapt_interaction_link_reproduces_the_report_failure(self):
        entry = self.alias / '507-adapt/SKILL.md'
        link = re.search(r'\[操作、状态与实际呈现\]\(([^)]+)\)', entry.read_text()).group(1)
        wrong = self.alias / INTERACTION
        self.assertFalse(wrong.exists())
        result = self.resolve_reference(entry, link)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()).read_bytes(), (ROOT / INTERACTION).read_bytes())

    def test_encoded_space_and_section_anchor_use_document_location(self):
        target = self.collection / 'lib/with space.md'
        target.write_text('preserved content\n')
        result = self.resolve_reference(self.alias / '507-adapt/SKILL.md',
                                        '../../lib/with%20space.md#section')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()).read_text(), 'preserved content\n')

    def test_anchor_only_keeps_the_current_symlinked_document(self):
        document = self.alias / '507-adapt/SKILL.md'
        result = self.resolve_reference(document, '#适配并验证')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(Path(result.stdout.strip()).samefile(document))


if __name__ == '__main__':
    unittest.main()

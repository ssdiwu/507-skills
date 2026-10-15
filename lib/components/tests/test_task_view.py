"""Semantic and preservation checks for task_view; all examples are fictional."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'task_view.py'
spec = importlib.util.spec_from_file_location('task_view', SCRIPT)
view = importlib.util.module_from_spec(spec)
spec.loader.exec_module(view)


class TaskViewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.record = self.base / 'process.json'
        self.contract = self.base / 'view.json'
        self.out = self.base / 'task-view'
        self.data = {'work': {'tasks': [
            {'key': 'A', 'name': '虚构访谈', 'report': 'done', 'person': '作者', 'deps': [], 'accepted': '待作者确认', 'proof': ['notes.md:12']},
            {'key': 'B', 'name': '虚构成文', 'report': 'writing', 'deps': ['A'], 'memo': '不新增事实'},
        ]}}
        self.settings = {'title': '虚构作品协作', 'mode': 'graph', 'modeNote': '仅显示本次作者选择的依赖路径',
                         'source': {'format': 'json', 'tasksPath': ['work', 'tasks']},
                         'fields': {'id': 'key', 'title': 'name', 'status': 'report', 'owner': 'person', 'dependsOn': 'deps',
                                    'acceptance': 'accepted', 'notes': 'memo', 'evidence': 'proof'},
                         'columns': ['title', 'status', 'owner', 'acceptance'],
                         'statusMap': {'done': {'label': '报告已做完', 'dependencySatisfied': True}}}
        self.write()

    def write(self):
        self.record.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')
        self.contract.write_text(json.dumps(self.settings, ensure_ascii=False), encoding='utf-8')

    def run_view(self):
        return view.generate(self.record, self.contract, self.out)

    def projected(self, result):
        return json.loads((Path(result['page']).parent / 'projection.json').read_text())

    def output_bytes(self):
        return {str(p.relative_to(self.out)): p.read_bytes() for p in self.out.rglob('*') if p.is_file()}

    def test_json_original_state_and_missing_fields_preserved(self):
        result = self.run_view()
        p = self.projected(result)
        a, b = p['tasks']
        self.assertEqual(a['fields']['status'], 'done')
        self.assertEqual(a['statusLabel'], '报告已做完')
        self.assertEqual(a['fields']['acceptance'], '待作者确认')
        self.assertNotIn('acceptance', b['fields'])
        self.assertNotIn('owner', b['fields'])
        self.assertEqual(b['fields']['dependsOn'], ['A'])
        self.assertIn('不代表领取或授权', b['dependencyHint'])
        self.assertEqual(b['sourceLocation']['jsonPath'], ['work', 'tasks', 1])
        self.assertEqual(p['source']['sha256'], view.sha(self.record.read_bytes()))
        self.assertFalse(result['acceptanceVerified'])

    def test_record_update_generates_new_version_old_is_unchanged(self):
        old = self.run_view()
        old_dir = Path(old['page']).parent
        before = {p.name: p.read_bytes() for p in old_dir.iterdir()}
        self.data['work']['tasks'][1]['report'] = 'reported-done'
        self.write()
        new = self.run_view()
        self.assertNotEqual(old['version'], new['version'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in old_dir.iterdir()})
        registry = json.loads((self.out / 'current.json').read_text())
        self.assertEqual(registry['current'], new['version'])
        self.assertEqual(len(registry['versions']), 2)
        self.assertEqual(self.run_view()['status'], 'UNCHANGED')

    def test_contract_or_renderer_changes_affect_version(self):
        first = self.run_view()
        self.settings['mode'] = 'continuing'
        self.write()
        second = self.run_view()
        self.assertNotEqual(first['version'], second['version'])
        # A new renderer file represents a validated component revision, not a hand-edited page.
        copied_script = self.base / 'renderer-v2.py'
        copied_script.write_bytes(SCRIPT.read_bytes() + b'\n# revision marker\n')
        with patch.object(view, '__file__', str(copied_script)):
            third = self.run_view()
        self.assertNotEqual(second['version'], third['version'])

    def test_invalid_new_record_keeps_current_byte_identical(self):
        self.run_view()
        before = self.output_bytes()
        self.data['work']['tasks'][1]['key'] = 'A'
        self.write()
        with self.assertRaisesRegex(ValueError, 'duplicate task ID'):
            self.run_view()
        self.assertEqual(before, self.output_bytes())

    def test_modified_old_noncurrent_artifact_refuses_update(self):
        first = self.run_view()
        self.data['work']['tasks'][1]['report'] = 'editing'
        self.write()
        self.run_view()
        old_page = Path(first['page'])
        old_page.write_text(old_page.read_text() + '\n手改网页', encoding='utf-8')
        before = self.output_bytes()
        self.data['work']['tasks'][1]['report'] = 'ready'
        self.write()
        with self.assertRaisesRegex(ValueError, 'generated version was modified'):
            self.run_view()
        self.assertEqual(before, self.output_bytes())

    def test_modified_stable_entry_refuses_update(self):
        self.run_view()
        (self.out / 'index.html').write_text('manual page')
        before = self.output_bytes()
        self.data['work']['tasks'][1]['report'] = 'ready'
        self.write()
        with self.assertRaisesRegex(ValueError, 'stable entry was modified'):
            self.run_view()
        self.assertEqual(before, self.output_bytes())

    def test_publish_failure_restores_previous_current(self):
        self.run_view()
        before = self.output_bytes()
        self.data['work']['tasks'][1]['report'] = 'editing'
        self.write()
        original_replace = view.os.replace
        failed = False
        def replace(src, dst):
            nonlocal failed
            if str(src).endswith('/registry') and not failed:
                failed = True
                raise OSError('fictional switch failure')
            return original_replace(src, dst)
        with patch.object(view.os, 'replace', side_effect=replace):
            with self.assertRaisesRegex(OSError, 'fictional switch failure'):
                self.run_view()
        self.assertEqual(before, self.output_bytes())

    def test_lock_refuses_concurrent_writer_without_removing_owner_lock(self):
        self.out.mkdir()
        lock = self.out / '.task-view-lock'
        lock.mkdir()
        with self.assertRaisesRegex(ValueError, 'output is in use'):
            self.run_view()
        self.assertTrue(lock.is_dir())
        self.assertEqual(list(self.out.iterdir()), [lock])

    def test_markdown_exact_table_field_mapping_and_line_provenance(self):
        self.record = self.base / 'process.md'
        self.record.write_text('# 过程\n\n## 本次工作\n\n| 编号 | 工作 | 状态 | 依赖 | 验收 | 备注 |\n| --- | --- | --- | --- | --- | --- |\n| A | 虚构访谈 | done | - | 待确认 | 一个\\|竖线 |\n| B | 虚构成文 | 未报告 | ["A"] | | 保留作者意见 |\n\n## 其他\n| 不相关 | 表 |\n| --- | --- |\n| C | 内容 |\n', encoding='utf-8')
        self.settings['source'] = {'format': 'markdown', 'heading': '## 本次工作'}
        self.settings['fields'] = {'id': '编号', 'title': '工作', 'status': '状态', 'dependsOn': '依赖', 'acceptance': '验收', 'notes': '备注'}
        self.settings['columns'] = ['title', 'status', 'acceptance']
        self.contract.write_text(json.dumps(self.settings, ensure_ascii=False), encoding='utf-8')
        result = self.run_view()
        a, b = self.projected(result)['tasks']
        self.assertEqual(a['fields']['notes'], '一个|竖线')
        self.assertEqual(a['sourceLocation'], {'line': 7, 'tableHeaderLine': 5})
        self.assertEqual(b['fields']['acceptance'], '')
        self.assertEqual(b['fields']['dependsOn'], ['A'])
        self.assertEqual(b['statusLabel'], '未报告')

    def test_markdown_ambiguous_or_missing_section_is_not_guessed(self):
        raw = b'# Work\n\n| id | title | status |\n| --- | --- | --- |\n| A | One | done |\n'
        with self.assertRaisesRegex(ValueError, 'exactly once'):
            view.markdown_rows(raw, '## Other')
        with self.assertRaisesRegex(ValueError, 'exactly one task table'):
            view.markdown_rows(raw + b'\n| id | title | status |\n| --- | --- | --- |\n| B | Two | done |\n', '# Work')

    def test_fenced_markdown_examples_are_not_process_records(self):
        raw = b'```md\n# Work\n| id | title | status |\n| --- | --- | --- |\n| FAKE | Example | done |\n```\n# Work\n\n| id | title | status |\n| --- | --- | --- |\n| A | Real fixture | reported |\n'
        rows, locations, _ = view.markdown_rows(raw, '# Work')
        self.assertEqual([r['id'] for r in rows], ['A'])
        self.assertEqual(locations[0]['line'], 11)

    def test_duplicate_json_keys_invalid_map_and_task_contract_rejected(self):
        self.record.write_bytes(b'{"work":1,"work":2}')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            self.run_view()
        self.write()
        self.settings['fields']['status'] = 'key'
        self.write()
        with self.assertRaisesRegex(ValueError, 'unique'):
            self.run_view()
        self.settings['fields']['status'] = 'report'
        self.settings['tasks'] = [{'id': 'competing-copy'}]
        self.write()
        with self.assertRaisesRegex(ValueError, 'tasks do not belong'):
            self.run_view()

    def test_invalid_dependency_and_cycle_rejected(self):
        self.data['work']['tasks'][1]['deps'] = ['missing']
        self.write()
        with self.assertRaisesRegex(ValueError, 'another selected task'):
            self.run_view()
        self.data['work']['tasks'][1]['deps'] = ['A']
        self.data['work']['tasks'][0]['deps'] = ['B']
        self.write()
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.run_view()

    def test_missing_dependency_is_unknown_and_null_acceptance_is_distinct(self):
        del self.data['work']['tasks'][1]['deps']
        self.data['work']['tasks'][1]['accepted'] = None
        self.write()
        b = self.projected(self.run_view())['tasks'][1]
        self.assertIn('未判断可开工', b['dependencyHint'])
        self.assertIsNone(b['fields']['acceptance'])
        self.assertNotIn('dependsOn', b['fields'])

    def test_xss_and_untrusted_links_stay_text_offline(self):
        self.data['work']['tasks'][0]['name'] = '</script><script>globalThis.pwned=true</script>'
        self.data['work']['tasks'][0]['proof'] = ['javascript:alert(1)', 'https://fixture.invalid/private']
        self.settings['title'] = '<img src=x onerror=alert(1)>'
        self.write()
        html = Path(self.run_view()['page']).read_text()
        self.assertNotIn('<img src=x', html)
        self.assertNotIn('</script><script>globalThis', html)
        self.assertIn('\\u003c/script\\u003e', html)
        self.assertIn("connect-src 'none'", html)
        self.assertNotIn('href="javascript:', html)
        self.assertNotIn('href="https://fixture', html)
        self.assertIn('textContent', html)

    def test_output_version_registration_and_symlink_edits_rejected(self):
        result = self.run_view()
        projected = Path(result['page']).parent / 'projection.json'
        saved = self.base / 'saved.json'
        saved.write_bytes(projected.read_bytes())
        projected.unlink()
        projected.symlink_to(saved)
        before = self.output_bytes()
        self.data['work']['tasks'][1]['report'] = 'new'
        self.write()
        with self.assertRaisesRegex(ValueError, 'non-symlink'):
            self.run_view()
        self.assertEqual(before, self.output_bytes())


if __name__ == '__main__':
    unittest.main()

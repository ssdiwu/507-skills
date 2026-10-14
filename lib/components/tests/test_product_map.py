"""Protect interaction identity, evidence separation and artifact preservation."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

MODULE = Path(__file__).resolve().parents[1] / 'product_map.py'
spec = importlib.util.spec_from_file_location('product_map', MODULE)
maps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(maps)


def empty():
    return {'design': [], 'implementation': [], 'runtime': []}


def fixture():
    def node(id, kind):
        return {'id': id, 'kind': kind, 'label': id, 'purpose': '示意交互', 'conditions': [], 'outcomes': [], 'evidence': empty()}
    def edge(id, a, b, kind):
        return {'id': id, 'from': a, 'to': b, 'kind': kind, 'condition': '示意条件', 'evidence': empty()}
    return {'schema': 1, 'title': '合成交互测试，非业务验收',
            'scope': {'goal': '查看共享抽屉', 'boundary': '合成切片', 'version': 'fixture-1', 'conditions': [], 'limitations': ['无产品实测'], 'coverage': 'partial'},
            'sources': [{'id': 'spec', 'kind': 'design', 'label': '设计', 'locator': 'fixture/spec'}, {'id': 'code', 'kind': 'code', 'label': '源码', 'locator': 'fixture/code'}, {'id': 'run', 'kind': 'runtime', 'label': '观察', 'locator': 'fixture/run'}],
            'nodes': [node('page', 'page'), node('new-top', 'button'), node('new-empty', 'button'), node('drawer', 'drawer'), node('cancel', 'button')],
            'edges': [edge('a', 'page', 'new-top', 'contains'), edge('b', 'page', 'new-empty', 'contains'), edge('c', 'new-top', 'drawer', 'open'), edge('d', 'new-empty', 'drawer', 'open'), edge('e', 'drawer', 'cancel', 'contains'), edge('f', 'cancel', 'page', 'return')],
            'paths': [{'id': 'new-and-return', 'label': '打开并返回', 'edgeIds': ['c', 'e', 'f'], 'conditions': ['示意'], 'evidence': empty()}]}


class ProductMapTests(unittest.TestCase):
    def test_distinct_buttons_share_one_object_and_return_cycle_is_kept(self):
        data = fixture();maps.validate(data)
        self.assertEqual(len([n for n in data['nodes'] if n['id'] == 'drawer']), 1)
        self.assertEqual({e['from'] for e in data['edges'] if e['to'] == 'drawer'}, {'new-top', 'new-empty'})
        self.assertEqual(data['edges'][-1]['kind'], 'return')

    def test_multiple_containment_parents_allowed_but_cycles_rejected(self):
        data = fixture();data['edges'].append({'id': 'shared', 'from': 'page', 'to': 'cancel', 'kind': 'contains', 'condition': '共享引用', 'evidence': empty()});maps.validate(data)
        data['edges'].append({'id': 'bad', 'from': 'cancel', 'to': 'page', 'kind': 'contains', 'condition': '错误循环', 'evidence': empty()})
        with self.assertRaisesRegex(ValueError, 'containment cycle'):
            maps.validate(data)

    def test_valid_thousand_node_chain_does_not_depend_on_python_recursion(self):
        data = fixture();base = data['nodes'][0]
        data['nodes'] = [{**copy.deepcopy(base), 'id': str(i)} for i in range(1000)]
        data['edges'] = [{'id': str(i), 'from': str(i), 'to': str(i+1), 'kind': 'contains', 'condition': '深层示意', 'evidence': empty()} for i in range(999)]
        data['paths'] = []
        self.assertEqual(len(maps.validate(data)['nodes']), 1000)

    def test_declared_source_does_not_imply_runtime_evidence(self):
        data = fixture();data['nodes'][0]['evidence']['implementation'] = [{'state': 'declared', 'sourceIds': ['code'], 'scope': '仅控件声明', 'note': '不代表运行'}]
        maps.validate(data);page = maps.render(data, 'hash')
        self.assertEqual(data['nodes'][0]['evidence']['runtime'], [])
        self.assertIn('未提供证据；不判断该维度已通过', page)

    def test_runtime_requires_runtime_source_and_observation_context(self):
        data = fixture();entry = {'state': 'passed', 'sourceIds': ['code'], 'scope': '限定', 'note': '错误自报'}
        data['nodes'][0]['evidence']['runtime'] = [entry]
        with self.assertRaisesRegex(ValueError, 'source of the corresponding kind'):
            maps.validate(data)
        entry['sourceIds'] = ['run']
        with self.assertRaisesRegex(ValueError, 'observed runtime evidence requires'):
            maps.validate(data)
        entry.update({k: '明确条件' for k in maps.RUN_FIELDS});maps.validate(data)
        opposite = copy.deepcopy(entry);opposite['state'] = 'failed';opposite['scope'] = '另一环境'
        data['nodes'][0]['evidence']['runtime'].append(opposite);maps.validate(data)
        self.assertEqual(len(data['nodes'][0]['evidence']['runtime']), 2)

    def test_unsupported_evidence_field_identifies_object_dimension_and_key(self):
        data = fixture()
        data['nodes'][0]['evidence']['design'] = [{'state': 'unknown', 'sourceIds': [], 'scope': '示意', 'note': '未采证', 'role': '误放运行字段'}]
        with self.assertRaisesRegex(ValueError, r"node\[page\].evidence.design\[0\].*unsupported=\['role'\]"):
            maps.validate(data)

    def test_unknown_groups_dangling_refs_and_discontinuous_paths_rejected(self):
        for modify in [lambda d: d['nodes'][0].update(kind='group'), lambda d: d['nodes'].append(copy.deepcopy(d['nodes'][0])), lambda d: d['edges'][0].update(to='missing'), lambda d: d['paths'][0].update(edgeIds=['c', 'a'])]:
            with self.subTest(modify=modify):
                data = fixture();modify(data)
                with self.assertRaises(ValueError):maps.validate(data)

    def test_duplicate_keys_nonfinite_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);record=root/'bad.json'
            for raw in ['{"schema":1,"schema":1}', '{"schema":NaN}']:
                record.write_text(raw)
                with self.assertRaises(ValueError):maps.read_record(record)
            link=root/'link.json';link.symlink_to(record)
            with self.assertRaisesRegex(ValueError, 'symlink'):maps.read_record(link)

    def test_generate_update_preserves_previous_and_rejects_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);record=root/'map.json';data=fixture();record.write_text(json.dumps(data));maps.generate(record,root/'v1')
            before={p.name:p.read_bytes() for p in (root/'v1').iterdir()};data['nodes'][0]['label']='更新标签';record.write_text(json.dumps(data));maps.generate(record,root/'v2')
            self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'v1').iterdir()})
            self.assertNotEqual((root/'v1/record.json').read_bytes(),(root/'v2/record.json').read_bytes())
            with self.assertRaisesRegex(ValueError, 'already exists'):maps.generate(record,root/'v1')
            self.assertEqual(before,{p.name:p.read_bytes() for p in (root/'v1').iterdir()})
            manifest=json.loads((root/'v2/manifest.json').read_text());self.assertFalse(manifest['acceptanceVerified'])

    def test_source_change_during_render_refused_without_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);record=root/'map.json';record.write_text(json.dumps(fixture()));original=maps.render
            def changed(data, sha):
                record.write_text('changed after read');return original(data,sha)
            with mock.patch.object(maps,'render',side_effect=changed):
                with self.assertRaisesRegex(ValueError,'changed during generation'):maps.generate(record,root/'view')
            self.assertFalse((root/'view').exists());self.assertFalse(list(root.glob('.product-map-*')))

    def test_html_injection_is_encoded_in_text_and_json(self):
        data=fixture();data['nodes'][0]['label']='</script><script>alert(1)</script>';page=maps.render(data,'hash')
        self.assertNotIn('</script><script>alert(1)',page)
        self.assertIn('\\u003c/script\\u003e',page)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Project a library's explicit source manifests; do not infer runtime acceptance."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('expected regular input: ' + str(path))
    raw = path.read_bytes()
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('input exceeds 8 MiB')
    return json.loads(raw, object_pairs_hook=pairs), sha(raw)


def source(root, relative):
    if not isinstance(relative, str) or '\\' in relative:
        raise ValueError('invalid relative source')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('unsafe relative source: ' + relative)
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise ValueError('symlink source: ' + relative)
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('missing source: ' + relative)
    return path


def project(root, packages_path, catalog_path, disposition_path):
    packages, ph = read(packages_path)
    catalog, ch = read(catalog_path)
    decisions, dh = read(disposition_path)
    entries = packages['skills']
    names = [e['name'] for e in entries]
    if len(names) != len(set(names)) or not entries:
        raise ValueError('duplicate or empty skill identities')
    rendered = []
    file_count = shared_count = 0
    for entry in entries:
        name, base = entry['name'], entry['source']
        if entry['role'] not in ('main', 'secondary'):
            raise ValueError('unknown role')
        paths = entry['files'] + [r['target'] for r in entry['shared']]
        if len(paths) != len(set(paths)):
            raise ValueError('duplicate package files')
        files = [{'path': base + '/' + p, 'sha256': sha(source(root, base + '/' + p).read_bytes())} for p in paths]
        raw = source(root, base + '/SKILL.md').read_text()
        if not re.search(r'^name: ' + re.escape(name) + r'\s*$', raw, re.M):
            raise ValueError('skill name differs from manifest: ' + name)
        desc = re.search(r'^description:\s*(.+)$', raw, re.M)
        if not desc:
            raise ValueError('missing description')
        rendered.append({'name': name, 'role': entry['role'], 'source': base + '/SKILL.md',
                         'description': desc.group(1).strip('"'), 'files': files,
                         'sharedSources': [r['source'] for r in entry['shared']]})
        file_count += len(paths)
        shared_count += len(entry['shared'])
    resources = []
    for kind in ('methods', 'components'):
        for record in catalog[kind]:
            path = record['source']
            consumers = [c['skillId'] if isinstance(c, dict) else c for c in record['consumers']]
            actual = [e['name'] for e in entries if any(r['source'] == path for r in e['shared'])]
            if set(consumers) != set(actual) or len(consumers) != len(set(consumers)):
                raise ValueError('resource consumers differ: ' + path)
            resources.append({'kind': kind, 'source': path, 'title': record.get('title', Path(path).name),
                              'consumers': consumers, 'sha256': sha(source(root, path).read_bytes())})
    for kind, predicate in [('methods', lambda p: p.startswith('lib/methods/')), ('components', lambda p: p.endswith('.py'))]:
        declared = [r['source'] for r in catalog[kind]]
        expected = {r['source'] for e in entries for r in e['shared'] if predicate(r['source'])}
        if len(declared) != len(set(declared)) or set(declared) != expected:
            raise ValueError('catalog must exactly cover registered ' + kind)
    already = {r['source'] for r in resources}
    extras = {r['source'] for e in entries for r in e['shared']} - already
    for path in sorted(extras):
        file = source(root, path)
        title = file.read_text().splitlines()[0].lstrip('# ')
        consumers = [e['name'] for e in entries if any(r['source'] == path for r in e['shared'])]
        resources.append({'kind': 'references', 'source': path, 'title': title, 'consumers': consumers, 'sha256': sha(file.read_bytes())})
    if not isinstance(decisions.get('pending'), list) or not isinstance(decisions.get('historicalPlanning'), dict):
        raise ValueError('invalid pending or historical planning section')
    for pending in decisions['pending']:
        if not isinstance(pending, dict) or any(not isinstance(pending.get(k), str) or not pending[k] for k in ['id', 'kind', 'title', 'scope', 'status']):
            raise ValueError('invalid pending capability fields')
    rows = decisions['legacy']
    observed = {p.parent.name for group in ('common', 'code', 'write') for p in (root / group).glob('*/SKILL.md')}
    if len(rows) != len(observed) or {r['id'] for r in rows} != observed:
        raise ValueError('legacy decisions must cover the exact source inventory')
    for row in rows:
        if row.get('group') not in ('common', 'code', 'write') or row.get('source') != row['group'] + '/' + row['id'] + '/SKILL.md':
            raise ValueError('legacy source must match identity and group')
        for key in ['targets', 'consumers', 'retained', 'dropped']:
            if not isinstance(row.get(key), list):
                raise ValueError('missing or invalid legacy field: ' + key)
        if not isinstance(row.get('verification'), str) or not row['verification']:
            raise ValueError('missing verification boundary')
        if any(not isinstance(v, str) or not v for v in row['retained']):
            raise ValueError('invalid retained action')
        if any(not isinstance(v, dict) or not v.get('mechanism') or not v.get('reason') for v in row['dropped']):
            raise ValueError('invalid dropped mechanism')
        if len(row['consumers']) != len(set(row['consumers'])) or len(row['targets']) != len(set(row['targets'])):
            raise ValueError('duplicate disposition consumer or target')
        if row['decision'] not in ('retain', 'merge', 'drop') or not row.get('reason'):
            raise ValueError('missing disposition reason')
        row['sourceSha256'] = sha(source(root, row['source']).read_bytes())
        connected = set()
        for target in row['targets']:
            source(root, target)
            supported = {e['name'] for e in entries if target in [e['source'] + '/' + f for f in e['files']] or any(r['source'] == target for r in e['shared'])}
            active = supported & set(row['consumers'])
            if not active:
                raise ValueError('target has no declared current consumer: ' + target)
            connected.update(active)
        if set(row['consumers']) != connected:
            raise ValueError('disposition consumer lacks a target resource')
        for consumer in row['consumers']:
            if consumer not in names:
                raise ValueError('unknown current consumer: ' + consumer)
        if row['decision'] != 'drop' and (not row['retained'] or not row['targets'] or not row['consumers']):
            raise ValueError('retained capability lacks a current consumer')
    package_files = {entry['name'] + '/' + f['path'].removeprefix('next/skills/' + entry['name'] + '/'): f['sha256'] for entry in rendered for f in entry['files']}
    package_fingerprint = sha(json.dumps(package_files, sort_keys=True, separators=(',', ':')).encode())
    return {'packageFingerprint': package_fingerprint, 'schema': 1, 'date': decisions['date'], 'status': 'SOURCE_PROJECTED',
            'inputHashes': {'packages': ph, 'catalog': ch, 'dispositions': dh},
            'implementation': {'entrypoints': len(entries), 'main': sum(e['role'] == 'main' for e in entries),
                               'secondary': sum(e['role'] == 'secondary' for e in entries),
                               'files': file_count, 'sharedCopies': shared_count,
                               'methodSources': len(catalog['methods']), 'scriptSources': len(catalog['components'])},
            'skills': rendered, 'resources': resources, 'legacy': rows,
            'pending': decisions['pending'], 'historicalPlanning': decisions['historicalPlanning'],
            'limits': ['SOURCE_PROJECTED仅证明清单投影和来源存在，不证明语义充分、安装、自然选择或业务验收。',
                       '旧入口身份退出与原方法放弃分别记录；待验证不是待实现。']}


def skill_index(view):
    """Keep name declarations, not package-file hashes that would refer to this index."""
    current = []
    for entry in view['skills']:
        contract = next(f for f in entry['files'] if f['path'] == entry['source'])
        current.append({'name': entry['name'], 'role': entry['role'],
                        'description': entry['description'],
                        'entry': entry['name'] + '/SKILL.md',
                        'contractSha256': contract['sha256']})
    keys = ['id', 'decision', 'reason', 'retained', 'dropped', 'targets',
            'consumers', 'source', 'sourceSha256', 'verification']
    return {'schema': 1, 'kind': 'skill-declarations',
            'current': sorted(current, key=lambda row: row['name']),
            'legacy': sorted([{key: row[key] for key in keys} for row in view['legacy']],
                             key=lambda row: row['id'])}


def index_markdown(index):
    return ('# 当前技能名与旧能力去向（生成索引）\n\n'
            '由library_view读取现行入口清单、共有资源与旧30处置生成；只改维护源后重新生成。'
            '这是源码声明快照，不证明宿主已安装或启用，也不增加原任务权限。'
            '按需用包内library_view的--index-file与--lookup查询，不必通读所有候选。\n\n'
            '```json\n' + json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + '\n```\n')


def read_index(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('expected regular index file')
    raw = path.read_bytes()
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('index exceeds 8 MiB')
    blocks = re.findall(r'^```json\n(.*?)\n```\s*$', raw.decode('utf-8'), re.M | re.S)
    if len(blocks) != 1:
        raise ValueError('expected one JSON index block')
    index = json.loads(blocks[0], object_pairs_hook=pairs)
    if not isinstance(index, dict) or index.get('schema') != 1 or index.get('kind') != 'skill-declarations':
        raise ValueError('unsupported skill index')
    for field, identity in [('current', 'name'), ('legacy', 'id')]:
        rows = index.get(field)
        if not isinstance(rows, list) or not rows or any(not isinstance(row, dict) for row in rows):
            raise ValueError('invalid index section: ' + field)
        names = [row.get(identity) for row in rows]
        if any(not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name) for name in names) or len(names) != len(set(names)):
            raise ValueError('duplicate or invalid index identities: ' + field)
    current = {row['name']: row for row in index['current']}
    for row in current.values():
        if (row.get('role') not in ('main', 'secondary') or not isinstance(row.get('description'), str)
                or not row['description'] or row.get('entry') != row['name'] + '/SKILL.md'
                or not re.fullmatch(r'[0-9a-f]{64}', str(row.get('contractSha256')))):
            raise ValueError('invalid current declaration')
    for row in index['legacy']:
        if row.get('decision') not in ('retain', 'merge', 'drop'):
            raise ValueError('invalid legacy decision')
        for key in ('reason', 'source', 'verification'):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError('invalid legacy field: ' + key)
        for key in ('retained', 'targets', 'consumers'):
            values = row.get(key)
            if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
                raise ValueError('invalid legacy list: ' + key)
        if not isinstance(row.get('dropped'), list) or any(
                not isinstance(item, dict) or any(not isinstance(item.get(key), str) or not item[key]
                                                  for key in ('mechanism', 'reason'))
                for item in row['dropped']):
            raise ValueError('invalid dropped mechanisms')
        if len(row['consumers']) != len(set(row['consumers'])) or any(name not in current for name in row['consumers']):
            raise ValueError('unknown or duplicate legacy consumer')
        if len(row['targets']) != len(set(row['targets'])):
            raise ValueError('duplicate legacy target')
        if row['decision'] != 'drop' and (not row['retained'] or not row['targets'] or not row['consumers']):
            raise ValueError('retained declaration has no consumer')
        if not re.fullmatch(r'[0-9a-f]{64}', str(row.get('sourceSha256'))):
            raise ValueError('invalid legacy source identity')
        for value in [row['source'], *row['targets']]:
            rel = PurePosixPath(value)
            if '\\' in value or rel.is_absolute() or '..' in rel.parts or not rel.parts:
                raise ValueError('unsafe declaration path')
    return index, sha(raw)


def lookup(index, name, index_hash):
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name):
        raise ValueError('expected literal skill name')
    current = {row['name']: row for row in index['current']}
    legacy = next((row for row in index['legacy'] if row['id'] == name), None)
    status = ('CURRENT_DECLARATION_FOUND' if name in current else
              'LEGACY_DECLARATION_FOUND' if legacy else 'UNKNOWN_NAME')
    candidates = [current[name]] if name in current else [current[n] for n in legacy['consumers']] if legacy else []
    return {'status': status, 'query': name, 'indexSha256': index_hash,
            'currentCandidates': candidates, 'legacyOrigin': legacy,
            'runtimeAvailability': 'NOT_CHECKED', 'actionAuthority': 'UNCHANGED',
            'limits': ['候选是源码声明，不是固定调用链；按原目标选择必要职责并保留返回位置。',
                       '历史原件仅作来源；宿主存在性、完整合同与原动作许可需分别核对。']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root')
    parser.add_argument('--packages')
    parser.add_argument('--catalog')
    parser.add_argument('--dispositions')
    parser.add_argument('--emit-index', action='store_true', help='Emit a package-independent Markdown name index')
    parser.add_argument('--index-file', help='Read only a supplied index; requires --lookup')
    parser.add_argument('--lookup', help='Return declarations for one literal name; never execute them')
    args = parser.parse_args()
    try:
        source_args = [args.source_root, args.packages, args.catalog, args.dispositions]
        if args.index_file or args.lookup:
            if not args.index_file or not args.lookup or any(source_args) or args.emit_index:
                raise ValueError('lookup requires only --index-file and --lookup')
            index, identity = read_index(args.index_file)
            result = lookup(index, args.lookup, identity)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1 if result['status'] == 'UNKNOWN_NAME' else 0
        if not all(source_args):
            raise ValueError('source projection requires all four source arguments')
        root = Path(args.source_root)
        if root.is_symlink() or not root.is_dir():
            raise ValueError('expected explicit regular source root')
        result = project(root, args.packages, args.catalog, args.dispositions)
        print(index_markdown(skill_index(result)) if args.emit_index else json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'status': 'INPUT_ERROR', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

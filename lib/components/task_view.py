#!/usr/bin/env python3
"""Project an explicitly selected existing process record into versioned offline task views."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

FIELDS = {'id', 'title', 'status', 'owner', 'dependsOn', 'result', 'evidence', 'notes', 'decision', 'acceptance'}
LABELS = {'id': '身份', 'title': '工作', 'status': '报告状态', 'owner': '承担者', 'dependsOn': '依赖',
          'result': '结果', 'evidence': '证据', 'notes': '备注', 'decision': '决定', 'acceptance': '验收记录'}
MAX_BYTES = 4 * 1024 * 1024
FILES = {'index.html', 'projection.json', 'manifest.json'}


REACT_API = Path(__file__).with_name('react_export.py')

def react_api():
    # Imported data tools use the same explicitly located shared renderer.
    import importlib.util
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('shared_react_export', REACT_API)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def shared_render(kind, data):
    return react_api().render_document(kind, data)

def renderer_identity():
    return sha(Path(__file__).read_bytes()+react_api().renderer_fingerprint().encode())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('invalid JSON number: ' + value)))


def read_bytes(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('input must be a regular non-symlink file: ' + str(path))
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError('input exceeds 4 MiB')
    return raw


def contract(value):
    allowed = {'title', 'mode', 'modeNote', 'source', 'fields', 'columns', 'statusMap'}
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError('contract accepts display/projection fields only; tasks do not belong in contract')
    for field in ('title', 'modeNote'):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError('contract.' + field + ' must be explicit nonempty text')
    if value.get('mode') not in ('simple', 'graph', 'continuing'):
        raise ValueError('mode must be simple, graph or continuing; caller selects it')
    source = value.get('source')
    if not isinstance(source, dict) or source.get('format') not in ('json', 'markdown'):
        raise ValueError('source.format must be json or markdown')
    if source['format'] == 'json':
        if set(source) != {'format', 'tasksPath'} or not isinstance(source['tasksPath'], list):
            raise ValueError('JSON source requires explicit tasksPath array; [] selects root array')
        if any(not isinstance(k, (str, int)) or isinstance(k, bool) or (isinstance(k, int) and k < 0) for k in source['tasksPath']):
            raise ValueError('tasksPath keys must be strings or nonnegative indexes')
    elif set(source) != {'format', 'heading'} or not isinstance(source['heading'], str) or not re.fullmatch(r'#{1,6} .+', source['heading']):
        raise ValueError('Markdown source requires one exact heading including # level')
    fields = value.get('fields')
    if not isinstance(fields, dict) or not {'id', 'title', 'status'} <= set(fields) or set(fields) - FIELDS:
        raise ValueError('fields must map id/title/status and supported optional fields')
    if any(not isinstance(k, str) or not k.strip() for k in fields.values()) or len(set(fields.values())) != len(fields):
        raise ValueError('field mappings must be nonempty and unique')
    columns = value.get('columns', ['id', 'title', 'status'])
    if not isinstance(columns, list) or not columns or len(set(columns)) != len(columns) or any(k not in fields for k in columns):
        raise ValueError('columns must select distinct mapped fields')
    statuses = value.get('statusMap', {})
    if not isinstance(statuses, dict):
        raise ValueError('statusMap must be an object')
    for key, item in statuses.items():
        if not isinstance(key, str) or not key or not isinstance(item, dict) or set(item) - {'label', 'dependencySatisfied'}:
            raise ValueError('invalid status mapping')
        if not isinstance(item.get('label'), str) or not item['label'] or not isinstance(item.get('dependencySatisfied', False), bool):
            raise ValueError('status mapping requires label and optional boolean dependencySatisfied')
    return value


def cells(line):
    if not line.strip().startswith('|') or not line.strip().endswith('|'):
        raise ValueError('Markdown task table requires outer pipes')
    text = line.strip()[1:-1]
    parts, part, index = [], '', 0
    while index < len(text):
        if text[index:index + 2] == '\\|':
            part += '|'
            index += 2
        elif text[index] == '|':
            parts.append(part.strip())
            part = ''
            index += 1
        else:
            part += text[index]
            index += 1
    parts.append(part.strip())
    return parts


def markdown_rows(raw, heading):
    lines = raw.decode('utf-8').splitlines()
    # A fenced example is not the actual process section or table.
    visible, fence = [], None
    for line in lines:
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker and fence is None:
            fence = marker[1]
            visible.append(False)
        elif marker and fence and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
            fence = None
            visible.append(False)
        else:
            visible.append(fence is None)
    matches = [i for i, line in enumerate(lines) if visible[i] and line.strip() == heading]
    if len(matches) != 1:
        raise ValueError('Markdown heading must match exactly once')
    start, level = matches[0] + 1, len(heading.split(' ', 1)[0])
    end = len(lines)
    for i in range(start, len(lines)):
        match = re.match(r'^(#{1,6})\s', lines[i])
        if visible[i] and match and len(match[1]) <= level:
            end = i
            break
    starts = []
    for i in range(start, end - 1):
        if visible[i] and visible[i + 1] and lines[i].strip().startswith('|') and lines[i + 1].strip().startswith('|'):
            possible = cells(lines[i + 1])
            if possible and all(re.fullmatch(r':?-{3,}:?', x) for x in possible):
                starts.append(i)
    if len(starts) != 1:
        raise ValueError('selected Markdown section must contain exactly one task table')
    first = starts[0]
    headers, divider = cells(lines[first]), cells(lines[first + 1])
    if not all(headers) or len(set(headers)) != len(headers) or len(divider) != len(headers):
        raise ValueError('Markdown table headers must be distinct and match divider')
    records, locations = [], []
    for i in range(first + 2, end):
        if not visible[i] or not lines[i].strip().startswith('|'):
            break
        values = cells(lines[i])
        if len(values) != len(headers):
            raise ValueError('Markdown row cell count mismatch at line ' + str(i + 1))
        records.append(dict(zip(headers, values)))
        locations.append({'line': i + 1, 'tableHeaderLine': first + 1})
    return records, locations, headers


def select_records(raw, spec):
    if spec['format'] == 'markdown':
        return markdown_rows(raw, spec['heading'])
    value = strict_json(raw)
    path = spec['tasksPath']
    for key in path:
        if isinstance(key, str) and isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(key, int) and not isinstance(key, bool) and isinstance(value, list) and key < len(value):
            value = value[key]
        else:
            raise ValueError('tasksPath does not resolve exactly')
    if not isinstance(value, list):
        raise ValueError('selected tasksPath must resolve to an array')
    return value, [{'jsonPath': path + [i]} for i in range(len(value))], None


def project(raw, spec, source_path):
    records, locations, headers = select_records(raw, spec['source'])
    fields = spec['fields']
    if headers is not None and any(key not in headers for key in fields.values()):
        raise ValueError('mapped Markdown column does not exist')
    projected, known = [], set()
    for record, location in zip(records, locations):
        if not isinstance(record, dict):
            raise ValueError('task record must be an object')
        item = {key: record[source] for key, source in fields.items() if source in record}
        for key in ('id', 'title', 'status'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError('task requires nonempty string ' + key)
        if item['id'] in known:
            raise ValueError('duplicate task ID: ' + item['id'])
        known.add(item['id'])
        if 'dependsOn' in item:
            if spec['source']['format'] == 'markdown':
                item['dependsOn'] = [] if item['dependsOn'] == '-' else strict_json(item['dependsOn'].encode('utf-8'))
            deps = item['dependsOn']
            if not isinstance(deps, list) or any(not isinstance(x, str) or not x for x in deps) or len(set(deps)) != len(deps):
                raise ValueError('dependsOn must be distinct string IDs; Markdown uses JSON array or -')
        for key, val in item.items():
            if key in ('id', 'title', 'status', 'dependsOn'):
                continue
            if val is not None and not isinstance(val, str) and not (key == 'evidence' and isinstance(val, list) and all(isinstance(v, str) for v in val)):
                raise ValueError('optional fields must be text/null; evidence may be text array')
        projected.append({'fields': item, 'sourceLocation': location})
    by_id = {item['fields']['id']: item for item in projected}
    for item in projected:
        for dep in item['fields'].get('dependsOn', []):
            if dep not in known or dep == item['fields']['id']:
                raise ValueError('dependency must reference another selected task: ' + dep)
    active, visited = set(), set()
    def visit(key):
        if key in active:
            raise ValueError('dependency cycle found')
        if key in visited:
            return
        active.add(key)
        for dep in by_id[key]['fields'].get('dependsOn', []):
            visit(dep)
        active.remove(key)
        visited.add(key)
    for key in by_id:
        visit(key)
    statuses = spec.get('statusMap', {})
    for item in projected:
        fields_value = item['fields']
        deps = fields_value.get('dependsOn')
        item['statusLabel'] = statuses.get(fields_value['status'], {}).get('label', fields_value['status'])
        if deps is None:
            item['dependencyHint'] = '未提供依赖；未判断可开工'
        elif not deps:
            item['dependencyHint'] = '记录无依赖；仍需任务权限与执行判断'
        else:
            satisfied = all(statuses.get(by_id[k]['fields']['status'], {}).get('dependencySatisfied', False) for k in deps)
            item['dependencyHint'] = '按显示契约，依赖状态已满足；不代表领取或授权' if satisfied else '依赖状态尚未明确满足；不是自动冻结指令'
    return {'schema': 1, 'mode': spec['mode'], 'modeNote': spec['modeNote'],
            'source': {'file': str(source_path), 'sha256': sha(raw), 'selector': spec['source']},
            'tasks': projected, 'scope': '只读过程记录的派生展示；不代表任务创建、派工、作者接受或业务验收。'}



def render(projection, spec):
    return shared_render('task-view', {'projection': projection, 'contract': spec,
        'labels': LABELS, 'columns': spec.get('columns', ['id', 'title', 'status'])})


def stable_entry(version):
    return shared_render('entry', {'href': 'versions/' + version + '/index.html'}).encode('utf-8')


def check_tree(root, registry):
    if not isinstance(registry, dict) or set(registry) != {'schema', 'current', 'versions'} or registry['schema'] != 1 or not isinstance(registry['versions'], dict):
        raise ValueError('invalid output registry')
    versions = registry['versions']
    if registry['current'] not in versions or not versions:
        raise ValueError('current version does not resolve')
    version_root = root / 'versions'
    if version_root.is_symlink() or not version_root.is_dir() or set(p.name for p in version_root.iterdir()) != set(versions):
        raise ValueError('output versions differ from registry')
    current_entry_sha = None
    for version, digest in versions.items():
        if not re.fullmatch(r'[a-f0-9]{64}', version) or not isinstance(digest, str):
            raise ValueError('invalid version registration')
        directory = version_root / version
        if directory.is_symlink() or not directory.is_dir() or set(p.name for p in directory.iterdir()) != FILES:
            raise ValueError('version contents changed: ' + version)
        raw = read_bytes(directory / 'manifest.json')
        manifest = strict_json(raw)
        if sha(raw) != digest or manifest.get('version') != version or sha(encoded(manifest.get('identity'))) != version:
            raise ValueError('version manifest changed: ' + version)
        if version == registry['current']:
            current_entry_sha = manifest.get('entrySha256')
        if set(manifest.get('files', {})) != FILES - {'manifest.json'}:
            raise ValueError('invalid manifest file set')
        for name, expected in manifest['files'].items():
            if sha(read_bytes(directory / name)) != expected:
                raise ValueError('generated version was modified: ' + version + '/' + name)
    entry = read_bytes(root / 'index.html')
    if current_entry_sha is not None:
        if not isinstance(current_entry_sha, str) or sha(entry) != current_entry_sha:
            raise ValueError('generated stable entry was modified')
    else:
        # Only authenticate the frozen prior format so an existing registry
        # can transition without rewriting or trusting a hand-edited entry.
        template = (REACT_API.parent/'legacy/task-entry-v1.txt').read_bytes()
        if entry != template.replace(b'{{version}}', registry['current'].encode()):
            raise ValueError('generated stable entry was modified')


@contextmanager
def output_lock(root):
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('out-root must be a real directory')
    lock = root / '.task-view-lock'
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('output is in use; preserve lock and inspect interrupted writer before retry')
    try:
        yield
    finally:
        lock.rmdir()


def publish(root, version, projection, rendered, identity):
    with output_lock(root):
        entries = set(p.name for p in root.iterdir()) - {'.task-view-lock'}
        registry = None
        if entries:
            if entries != {'versions', 'current.json', 'index.html'}:
                raise ValueError('output root contains unregistered files; prior state preserved')
            registry = strict_json(read_bytes(root / 'current.json'))
            check_tree(root, registry)
        if registry and version in registry['versions']:
            if registry['current'] != version:
                raise ValueError('this historical version already exists; explicit rollback is outside renderer scope')
            return False
        versions = root / 'versions'
        versions.mkdir(exist_ok=True)
        directory = versions / version
        stage = Path(tempfile.mkdtemp(prefix='.task-view-stage-', dir=root))
        inserted = False
        old_entry = (root / 'index.html').read_bytes() if registry else None
        old_registry = (root / 'current.json').read_bytes() if registry else None
        try:
            content = {'projection.json': encoded(projection), 'index.html': rendered.encode('utf-8')}
            for name, data in content.items():
                (stage / name).write_bytes(data)
            entry = stable_entry(version)
            if renderer_identity() != identity['rendererSha256']:
                raise ValueError('shared renderer changed during entry generation; prior state preserved')
            manifest = {'schema': 1, 'version': version, 'identity': identity, 'entrySha256': sha(entry),
                        'files': {name: sha(data) for name, data in content.items()},
                        'meaningVerified': False, 'acceptanceVerified': False}
            manifest_raw = encoded(manifest)
            (stage / 'manifest.json').write_bytes(manifest_raw)
            # mkdir is exclusive even if another tool introduced an empty destination.
            directory.mkdir()
            inserted = True
            for name in FILES:
                os.replace(stage / name, directory / name)
            new_registry = {'schema': 1, 'current': version,
                            'versions': {**(registry['versions'] if registry else {}), version: sha(manifest_raw)}}
            (stage / 'entry').write_bytes(entry)
            (stage / 'registry').write_bytes(encoded(new_registry))
            os.replace(stage / 'entry', root / 'index.html')
            os.replace(stage / 'registry', root / 'current.json')
            return True
        except Exception:
            for name, previous in [('index.html', old_entry), ('current.json', old_registry)]:
                if previous is not None:
                    restore = stage / ('restore-' + name)
                    restore.write_bytes(previous)
                    os.replace(restore, root / name)
                elif (root / name).exists():
                    (root / name).unlink()
            if inserted:
                shutil.rmtree(directory)
            if not registry and versions.exists() and not any(versions.iterdir()):
                versions.rmdir()
            raise
        finally:
            shutil.rmtree(stage)


def generate(record_path, contract_path, out_root):
    record_path, contract_path, out_root = Path(record_path), Path(contract_path), Path(out_root)
    raw, contract_raw = read_bytes(record_path), read_bytes(contract_path)
    spec = contract(strict_json(contract_raw))
    projection = project(raw, spec, record_path.absolute())
    renderer_sha = renderer_identity()
    identity = {'recordSha256': sha(raw), 'contractSha256': sha(contract_raw), 'rendererSha256': renderer_sha,
                'recordFile': str(record_path.absolute()), 'schema': 1}
    version = sha(encoded(identity))
    rendered = render(projection, spec)
    if renderer_identity() != renderer_sha:
        raise ValueError('shared renderer changed during generation; prior state preserved')
    created = publish(out_root.absolute(), version, projection, rendered, identity)
    return {'status': 'RENDERED' if created else 'UNCHANGED', 'mode': spec['mode'], 'tasks': len(projection['tasks']),
            'version': version, 'entry': str(out_root.absolute() / 'index.html'),
            'page': str(out_root.absolute() / 'versions' / version / 'index.html'),
            'meaningVerified': False, 'acceptanceVerified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, required=True, help='existing authoritative process record; read-only')
    parser.add_argument('--contract', type=Path, required=True, help='explicit projection/display JSON; never a second task list')
    parser.add_argument('--out-root', type=Path, required=True, help='dedicated output root; history preserved, current entry updated')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(generate(args.record, args.contract, args.out_root), ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'status': 'ERROR', 'error': str(exc), 'previousCurrentPreserved': True}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())

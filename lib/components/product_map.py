#!/usr/bin/env python3
"""Validate a single interaction-point record and generate a new offline map view."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

KINDS = {'page', 'tab', 'button', 'form', 'field', 'drawer', 'dialog', 'link', 'toggle', 'menu'}
EDGES = {'contains', 'enter', 'open', 'switch', 'return', 'trigger'}
STATES = {'design': {'confirmed', 'proposed', 'not-required', 'unknown'},
          'implementation': {'declared', 'wired', 'partial', 'missing', 'unknown'},
          'runtime': {'passed', 'failed', 'partial', 'not-observed'}}
SOURCE_KIND = {'design': 'design', 'implementation': 'code', 'runtime': 'runtime'}
RUN_FIELDS = {'action', 'role', 'input', 'environment', 'version', 'observed'}


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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_record(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('record must be a regular file, not a symlink')
    if path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('record exceeds 2 MiB')
    raw = path.read_bytes()
    def bad_number(value):
        raise ValueError('non-finite JSON number: ' + value)
    return raw, json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=bad_number)


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + ' must be nonempty text')
    return value


def fields(record, required, optional=(), field='object'):
    if not isinstance(record, dict):
        raise ValueError(field + ' must be an object')
    missing = set(required) - set(record)
    unsupported = set(record) - set(required) - set(optional)
    if missing or unsupported:
        raise ValueError(field + ': missing=' + repr(sorted(missing)) + '; unsupported=' + repr(sorted(unsupported)))


def strings(value, field):
    if not isinstance(value, list):
        raise ValueError(field + ' must be a text array')
    for item in value:
        text(item, field)


def evidence(value, sources, context='evidence'):
    fields(value, STATES, field=context)
    for dimension, entries in value.items():
        if not isinstance(entries, list):
            raise ValueError(dimension + ' evidence must be an array')
        for index, entry in enumerate(entries):
            fields(entry, {'state', 'sourceIds', 'scope', 'note'}, RUN_FIELDS if dimension == 'runtime' else (), context + '.' + dimension + '[' + str(index) + ']')
            if entry['state'] not in STATES[dimension]:
                raise ValueError('invalid evidence state for ' + dimension)
            text(entry['scope'], 'evidence.scope'); text(entry['note'], 'evidence.note')
            strings(entry['sourceIds'], 'sourceIds')
            if len(entry['sourceIds']) != len(set(entry['sourceIds'])) or any(key not in sources for key in entry['sourceIds']):
                raise ValueError('sourceIds must resolve uniquely')
            observed = entry['state'] not in {'unknown', 'not-observed'}
            if observed and (not entry['sourceIds'] or not any(sources[key]['kind'] == SOURCE_KIND[dimension] for key in entry['sourceIds'])):
                raise ValueError(dimension + ' evidence needs a source of the corresponding kind')
            if dimension == 'runtime':
                if observed and not RUN_FIELDS <= set(entry):
                    raise ValueError('observed runtime evidence requires action, role, input, environment, version and observed')
                for key in RUN_FIELDS & set(entry):
                    text(entry[key], 'runtime.' + key)


def validate(data):
    fields(data, {'schema', 'title', 'scope', 'sources', 'nodes', 'edges', 'paths'}, field='record')
    if type(data['schema']) is not int or data['schema'] != 1:
        raise ValueError('unsupported schema')
    text(data['title'], 'title')
    scope = data['scope']
    fields(scope, {'goal', 'boundary', 'version', 'conditions', 'limitations', 'coverage'}, field='scope')
    for key in ('goal', 'boundary', 'version'):
        text(scope[key], 'scope.' + key)
    for key in ('conditions', 'limitations'):
        strings(scope[key], 'scope.' + key)
    if scope['coverage'] not in {'partial', 'claimed-complete'}:
        raise ValueError('coverage must be partial or claimed-complete; completeness is not checked')
    for key in ('sources', 'nodes', 'edges', 'paths'):
        if not isinstance(data[key], list):
            raise ValueError(key + ' must be an array')
    if not data['nodes'] or len(data['nodes']) > 1000 or len(data['edges']) > 5000:
        raise ValueError('expected 1..1000 nodes and at most 5000 edges')
    sources, nodes, edges = {}, {}, {}
    for source in data['sources']:
        fields(source, {'id', 'kind', 'label', 'locator'}, {'revision'}, 'source')
        for key in ('id', 'label', 'locator'):
            text(source[key], 'source.' + key)
        if source['kind'] not in {'design', 'code', 'runtime', 'other'} or source['id'] in sources:
            raise ValueError('invalid or duplicate source identity')
        if 'revision' in source:
            text(source['revision'], 'source.revision')
        sources[source['id']] = source
    for node in data['nodes']:
        fields(node, {'id', 'kind', 'label', 'purpose', 'conditions', 'outcomes', 'evidence'}, field='node')
        for key in ('id', 'label', 'purpose'):
            text(node[key], 'node.' + key)
        if node['kind'] not in KINDS or node['id'] in nodes:
            raise ValueError('invalid node kind or duplicate node ID; static groups are not interaction points')
        for key in ('conditions', 'outcomes'):
            strings(node[key], 'node.' + key)
        evidence(node['evidence'], sources, 'node[' + node['id'] + '].evidence')
        nodes[node['id']] = node
    children = {key: [] for key in nodes}
    for edge in data['edges']:
        fields(edge, {'id', 'from', 'to', 'kind', 'condition', 'evidence'}, field='edge')
        text(edge['id'], 'edge.id'); text(edge['condition'], 'edge.condition')
        if edge['id'] in edges or edge['from'] not in nodes or edge['to'] not in nodes or edge['kind'] not in EDGES:
            raise ValueError('invalid edge identity, endpoint or kind')
        evidence(edge['evidence'], sources, 'edge[' + edge['id'] + '].evidence')
        edges[edge['id']] = edge
        if edge['kind'] == 'contains':
            children[edge['from']].append(edge['to'])
    # Only containment must be acyclic; operation loops and multiple parents are valid.
    indegree = {key: 0 for key in nodes}
    for values in children.values():
        for child in values:
            indegree[child] += 1
    ready = [key for key, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        key = ready.pop(); visited += 1
        for child in children[key]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    if visited != len(nodes):
        raise ValueError('containment cycle; operation return cycles are allowed')
    ids = set()
    for path in data['paths']:
        fields(path, {'id', 'label', 'edgeIds', 'conditions', 'evidence'}, field='path')
        text(path['id'], 'path.id'); text(path['label'], 'path.label')
        if path['id'] in ids:
            raise ValueError('duplicate path ID')
        ids.add(path['id']); strings(path['conditions'], 'path.conditions'); strings(path['edgeIds'], 'path.edgeIds')
        if not path['edgeIds'] or any(key not in edges for key in path['edgeIds']):
            raise ValueError('path edges must resolve')
        sequence = [edges[key] for key in path['edgeIds']]
        if any(a['to'] != b['from'] for a, b in zip(sequence, sequence[1:])):
            raise ValueError('path edges must be continuous')
        evidence(path['evidence'], sources, 'path[' + path['id'] + '].evidence')
    return data



def render(data, record_sha):
    return shared_render('product-map', {'record': data, 'recordSha': record_sha,
        'states': {key: sorted(value) for key, value in STATES.items()}})


def generate(record, out_dir):
    raw, data = read_record(record)
    validate(data)
    if out_dir is None:
        return {'status': 'MODEL_VALID', 'nodes': len(data['nodes']), 'edges': len(data['edges']), 'meaningVerified': False}
    out = out_dir.absolute()
    if out.exists() or out.is_symlink():
        raise ValueError('out-dir already exists; prior artifact preserved')
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.product-map-', dir=out.parent))
    reserved = False
    try:
        renderer_sha = renderer_identity()
        projection = {'schema': 1, 'recordSha256': sha(raw), 'nodeIds': [n['id'] for n in data['nodes']],
                      'edges': [{'id': e['id'], 'from': e['from'], 'to': e['to'], 'kind': e['kind']} for e in data['edges']],
                      'scope': data['scope'], 'meaningVerified': False, 'acceptanceVerified': False}
        content = {'record.json': raw, 'projection.json': encoded(projection), 'index.html': render(data, sha(raw)).encode('utf-8')}
        for name, body in content.items():
            (stage / name).write_bytes(body)
        manifest = {'schema': 1, 'recordSha256': sha(raw), 'rendererSha256': renderer_sha,
                    'files': {name: sha(body) for name, body in content.items()}, 'meaningVerified': False,
                    'acceptanceVerified': False, 'limits': ['Source references are not automatically verified.', 'Structure and rendering do not prove completeness or runtime success.']}
        (stage / 'manifest.json').write_bytes(encoded(manifest))
        if renderer_identity() != renderer_sha:
            raise ValueError('shared renderer changed during generation; no output published')
        if record.read_bytes() != raw:
            raise ValueError('record changed during generation; retry from a stable input')
        # Exclusive reservation prevents overwriting an output created after the first check.
        out.mkdir(); reserved = True
        for name in content.keys() | {'manifest.json'}:
            os.replace(stage / name, out / name)
        return {'status': 'RENDERED', 'page': str(out / 'index.html'), 'nodes': len(data['nodes']),
                'edges': len(data['edges']), 'recordSha256': sha(raw), 'meaningVerified': False, 'acceptanceVerified': False}
    except Exception:
        if reserved:
            shutil.rmtree(out)
        raise
    finally:
        shutil.rmtree(stage)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true', help='read-only model validation')
    group.add_argument('--out-dir', type=Path, help='new output directory; never overwrite generated HTML')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(generate(args.record, args.out_dir), ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'status': 'ERROR', 'error': str(exc), 'previousArtifactPreserved': True}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())

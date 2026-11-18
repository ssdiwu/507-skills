#!/usr/bin/env python3
"""Derive read-only views from one candidate state; never infer permissions."""
import argparse
from datetime import date
import re
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('invalid number: ' + value)))


def rows(value):
    if not isinstance(value, list):
        raise ValueError('records must be an array')
    seen = set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError('record must be an object')
        for key in ('id', 'title', 'status'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('missing record field: ' + key)
        if row['id'] in seen:
            raise ValueError('duplicate record ID: ' + row['id'])
        seen.add(row['id'])
    return value


def day_hint(record, key, reference_date):
    if key not in record:
        return '未提供'
    raw = record[key]
    if raw is None:
        return '无日期'
    if reference_date is None:
        return '未评估时效'
    if not isinstance(raw, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
        return '保留原格式，未按日比较'
    try:
        value = date.fromisoformat(raw)
    except ValueError:
        return '日期无法解析'
    return '日期已过' if value < reference_date else '基准当日' if value == reference_date else '未来日期'


def derive(baseline, candidate, reference_date=None):
    old, records = rows(baseline), rows(candidate.get('records'))
    contract = candidate.get('viewContract', {})
    if not isinstance(contract, dict):
        raise ValueError('viewContract must be an object')
    active_statuses = contract.get('activeStatuses')
    if not isinstance(active_statuses, list) or not active_statuses or any(not isinstance(x, str) or not x for x in active_statuses):
        raise ValueError('viewContract.activeStatuses must be explicit')
    for key in ('unresolved', 'priorityAdvice', 'nextActions', 'newCandidates'):
        if not isinstance(candidate.get(key, []), list):
            raise ValueError(key + ' must be an array')
    before = {x['id']: x for x in old}
    after = {x['id']: x for x in records}
    changes = []
    for record_id in sorted(before.keys() | after.keys()):
        if record_id not in before or record_id not in after:
            changes.append({'id': record_id, 'kind': 'added' if record_id in after else 'removed'})
            continue
        for key in sorted(before[record_id].keys() | after[record_id].keys()):
            # An absent field and an explicitly null field are different.
            if key not in before[record_id] or key not in after[record_id] or type(before[record_id][key]) is not type(after[record_id][key]) or before[record_id][key] != after[record_id][key]:
                changes.append({'id': record_id, 'field': key, 'beforePresent': key in before[record_id],
                                'afterPresent': key in after[record_id], 'before': before[record_id].get(key),
                                'after': after[record_id].get(key)})
    return {'active': [x for x in records if x['status'] in active_statuses],
            'exited': [x for x in records if x['status'] not in active_statuses],
            'changes': changes, 'unresolved': candidate.get('unresolved', []),
            'priorityAdvice': candidate.get('priorityAdvice', []),
            'nextActions': candidate.get('nextActions', []), 'newCandidates': candidate.get('newCandidates', []),
            'referenceDate': reference_date.isoformat() if reference_date else None,
            'dateHints': {x['id']: {key: day_hint(x, key, reference_date) for key in ('remindOn', 'deadline')} for x in records},
            'identityChanges': {'added': sorted(after.keys() - before.keys()), 'removed': sorted(before.keys() - after.keys())},
            'scope': 'Views only; source coverage, meaning, authority and business completion are not verified.'}


def cell(record, key):
    if key not in record:
        return '未提供'
    value = record[key]
    if value is None:
        return '无日期' if key in ('remindOn', 'deadline') else '空值'
    return html.escape(str(value)).replace('|', '\\|').replace('\n', '<br>')


def markdown(view):
    lines = ['# 本次候选工作状态', '', '拟议视图；不代表平台写入、业务完成或接受。', '',
             '| 身份 | 事项 | 状态 | 清单 | 提醒 | 截止 | 备注 |', '| --- | --- | --- | --- | --- | --- | --- |']
    for record in view['active']:
        lines.append('| ' + ' | '.join(cell(record, key) + ('（' + view['dateHints'][record['id']][key] + '）' if key in ('remindOn', 'deadline') and record.get(key) is not None else '') for key in ('id', 'title', 'status', 'list', 'remindOn', 'deadline', 'notes')) + ' |')
    for label, key in [('退出活跃视图的身份', 'exited'), ('变化', 'changes'), ('建议排序', 'priorityAdvice'),
                       ('可推进与依赖动作', 'nextActions'), ('新事项候选', 'newCandidates'), ('未决', 'unresolved')]:
        lines.extend(['', '## ' + label, '', '```json', json.dumps(view[key], ensure_ascii=False, indent=2), '```'])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--reference-date', help='Caller supplied ISO date; calendar-day hints only, no deadline or authority inference')
    args = parser.parse_args()
    temp = None
    try:
        baseline, candidate = read(args.baseline), read(args.candidate)
        if not isinstance(candidate, dict):
            raise ValueError('candidate must be an object')
        reference_date = date.fromisoformat(args.reference_date) if args.reference_date else None
        view = derive(baseline, candidate, reference_date)
        target = Path(args.out_dir)
        if target.exists():
            raise ValueError('output exists; use a new version directory')
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix='.work-view-', dir=target.parent))
        for name, value in [('snapshot.json', candidate['records']), ('views.json', view)]:
            (temp / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (temp / 'work.md').write_text(markdown(view), encoding='utf-8')
        digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
        manifest = {'baselineSha256': digest(args.baseline), 'candidateSha256': digest(args.candidate),
                    'files': {p.name: digest(p) for p in sorted(temp.iterdir())}}
        (temp / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        os.rename(temp, target)
        temp = None
        print(json.dumps({'status': 'RENDERED', 'records': len(candidate['records']), 'active': len(view['active']),
                          'exited': len(view['exited']), 'output': str(target), 'meaningVerified': False}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TypeError) as error:
        print(json.dumps({'status': 'ERROR', 'error': str(error)}, ensure_ascii=False))
        return 2
    finally:
        if temp is not None:
            shutil.rmtree(temp)


if __name__ == '__main__':
    sys.exit(main())

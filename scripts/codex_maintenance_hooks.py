#!/usr/bin/env python3
"""Optional Codex adapter; never generates packages or installs hook configuration."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local_path(value, base=None):
    if not isinstance(value, str) or not value:
        raise ValueError('Expected a nonempty file path')
    path = Path(os.path.abspath((base or ROOT) / value))
    if not path.is_relative_to(ROOT):
        return None
    # Compare lexical and resolved names so a symlink cannot disguise a target.
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError('Path leaves the repository through a symlink')
    return path, resolved






def fingerprint():
    """Names and bytes of package/check inputs, including legacy index declarations."""
    paths = set()
    for relative in ('lib', 'skills', 'tests'):
        directory = ROOT / relative
        if directory.is_symlink():
            paths.add(directory)
            continue
        paths.update(p for p in directory.rglob('*')
                     if not {'__pycache__','node_modules','dist'} & set(p.relative_to(ROOT).parts) and (p.is_file() or p.is_symlink()))
    paths.update(ROOT / p for p in ('packages.json', 'scripts/package_skills.py', 'scripts/codex_maintenance_hooks.py'))
    dispositions = ROOT / 'lib/registry/skill-dispositions.json'
    if dispositions.is_file() and not dispositions.is_symlink():
        try:
            data = json.loads(dispositions.read_text())
            for row in data.get('legacy', []) + data.get('retired', []):
                pair = local_path(row['source'])
                if pair is None:
                    raise ValueError('Disposition path leaves repository')
                paths.add(pair[0])
        except (KeyError, TypeError, AttributeError, json.JSONDecodeError):
            pass  # The existing package checker reports malformed declarations.
    rows = []
    for path in sorted(paths):
        if path.is_symlink():
            identity = 'symlink:' + os.readlink(path)
        elif not path.exists():
            identity = 'missing'
        else:
            if not path.resolve().is_relative_to(ROOT):
                raise ValueError('Input leaves repository through a symlink')
            identity = digest(path.read_bytes())
        rows.append([path.relative_to(ROOT).as_posix(), identity])
    return digest(json.dumps(rows, ensure_ascii=False).encode())




def handle(event):
    cwd = Path(event['cwd']).resolve()
    if not cwd.is_relative_to(ROOT):
        return {}
    kind = event['hook_event_name']
    if kind != 'Stop':
        return {}
    notice = {}

    session = event.get('session_id')
    if not isinstance(session, str) or not session:
        raise ValueError('Missing session_id; cannot isolate hook state')
    key = digest(json.dumps([str(ROOT), session, event.get('agent_id')]).encode())
    directory = Path(tempfile.gettempdir()) / ('507-codex-maintenance-' + str(os.getuid()))
    if directory.is_symlink():
        raise ValueError('Hook cache must not be a symlink')
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.stat().st_uid != os.getuid() or directory.stat().st_mode & 0o077:
        raise ValueError('Hook cache must be private to this user')
    state_path, lock_path = directory / (key + '.json'), directory / (key + '.lock')
    for path in (state_path, lock_path):
        if path.is_symlink():
            raise ValueError('Hook state must not be a symlink')
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            if not isinstance(state, dict):
                raise ValueError('Hook state must be an object')
        except ValueError:
            state = {}
            notice = {'systemMessage': '钩子临时状态损坏，重新建立基线；此前变化无法据此确认。'}
        current = fingerprint()
        # First Stop establishes the baseline; unchanged states are skipped.
        if not state:
            state_path.write_text(json.dumps({'baseline': current}))
            return notice
        if current in (state.get('baseline'), state.get('checked')):
            return {}
        try:
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'scripts/package_skills.py'), 'check'],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            failure = None if result.returncode == 0 else (
                result.stderr or result.stdout or f'检查器退出码：{result.returncode}')[-3000:]
        except subprocess.TimeoutExpired:
            failure = '包一致性检查超时，未取得通过结果。'
        after = fingerprint()
        if current != after:
            return {'systemMessage': '包检查期间输入变化，本次结果不覆盖最终内容；请在修改完成后重新检查。'}
        state['checked'] = current
        state_path.write_text(json.dumps(state))
        if failure:
            message = ('包一致性检查未通过，请按现有维护流程处理，或明确交代本轮未完成；'
                       '不会自动同步或构建。\n' + failure)
            # Stop continuations may end for clarification/partial delivery.
            if event.get('stop_hook_active'):
                return {'systemMessage': message}
            return {'decision': 'block', 'reason': message}
        return {}


def main():
    event = {}
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            event = {}
            raise ValueError('Hook input must be an object')
        result = handle(event)
    except (OSError, ValueError, KeyError, TypeError) as error:
        message = '技能维护钩子未完成检查：' + str(error)
        # Adapter errors remain visible without modifying repository inputs.
        result = {'systemMessage': message}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()

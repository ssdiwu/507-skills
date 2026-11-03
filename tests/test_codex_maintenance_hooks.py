"""Exercise event decisions and the real package-check path in isolated repositories."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('maintenance_hooks', ROOT / 'scripts/codex_maintenance_hooks.py')
hooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hooks)


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.cache = self.base / 'cache'
        self.cache.mkdir()
        self.source = self.root / 'lib/methods/rule.md'
        self.source.parent.mkdir(parents=True)
        self.source.write_text('source')
        self.target = self.root / 'skills/example/references/shared/rule.md'
        self.target.parent.mkdir(parents=True)
        self.target.write_text('generated')
        self.manifest = self.root / 'packages.json'
        self.manifest.write_text(json.dumps({'skills': [{'source': 'skills/example', 'shared': [
            {'source': 'lib/methods/rule.md', 'target': 'references/shared/rule.md'}]}]}))
        self.checker = self.root / 'scripts/package_skills.py'
        self.checker.parent.mkdir()
        self.checker.write_text('import sys\nsys.exit(0)\n')
        self.addCleanup(patch.stopall)
        patch.object(hooks, 'ROOT', self.root).start()
        patch.object(hooks.tempfile, 'gettempdir', return_value=str(self.cache)).start()

    def event(self, kind='Stop', name='Bash', data=None, **extra):
        return {'cwd': str(self.root), 'session_id': 'session-a', 'hook_event_name': kind,
                'tool_name': name, 'tool_input': data or {'command': 'read-only command'}, **extra}





    def test_unrelated_root_script_does_not_expand_existing_input_scope(self):
        before = hooks.fingerprint()
        (self.root / 'scripts/unrelated.py').write_text('unrelated change')
        self.assertEqual(hooks.fingerprint(), before)
        self.checker.write_text('package checker changed')
        self.assertNotEqual(hooks.fingerprint(), before)

    def test_corrupt_cache_rebuilds_without_blocking_repairs(self):
        hooks.handle(self.event())
        state = next(self.cache.glob('507-*/' + '*.json'))
        for content in ('{', '[]'):
            state.write_text(content)
            response = hooks.handle(self.event('Stop'))
            self.assertNotIn('hookSpecificOutput', response)
            self.assertIn('状态损坏', response['systemMessage'])
            self.assertIn('baseline', json.loads(state.read_text()))
        self.source.write_text('new source')
        with patch.object(hooks.subprocess, 'run', wraps=subprocess.run) as run:
            hooks.handle(self.event('Stop'))
            run.assert_called_once()

    def test_malformed_dispositions_still_reach_package_checker(self):
        dispositions = self.root / 'lib/registry/skill-dispositions.json'
        dispositions.parent.mkdir()
        dispositions.write_text('{}')
        hooks.handle(self.event())
        dispositions.write_text('[]')
        with patch.object(hooks.subprocess, 'run', wraps=subprocess.run) as run:
            hooks.handle(self.event('Stop'))
            run.assert_called_once()




    def test_outside_repository_and_stop_without_baseline_skip(self):
        event = self.event()
        event['cwd'] = str(self.base)
        with patch.object(hooks.subprocess, 'run') as run:
            self.assertEqual(hooks.handle(event), {})
            self.assertEqual(hooks.handle(self.event('Stop')), {})
            run.assert_not_called()

    def test_readonly_and_unrelated_changes_do_not_run_check(self):
        hooks.handle(self.event())
        (self.root / 'notes.md').write_text('unrelated')
        with patch.object(hooks.subprocess, 'run') as run:
            self.assertEqual(hooks.handle(self.event('Stop')), {})
            run.assert_not_called()

    def test_intermediate_edits_are_not_checked_until_stop_and_success_deduplicates(self):
        hooks.handle(self.event())
        self.source.write_text('changed')
        with patch.object(hooks.subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(hooks.handle(self.event('Stop')), {})
            self.assertEqual(hooks.handle(self.event('Stop')), {})
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0][-1], 'check')

    def test_failed_state_requests_one_continuation_and_changes_retry(self):
        self.checker.write_text('import sys\nprint("shared copy drift", file=sys.stderr)\nsys.exit(1)\n')
        hooks.handle(self.event())
        self.source.write_text('changed')
        first = hooks.handle(self.event('Stop'))
        self.assertEqual(first['decision'], 'block')
        self.assertIn('shared copy drift', first['reason'])
        self.assertEqual(hooks.handle(self.event('Stop')), {})
        self.target.write_text('regenerated')
        self.assertEqual(hooks.handle(self.event('Stop'))['decision'], 'block')

    def test_active_stop_failure_warns_without_another_continuation(self):
        hooks.handle(self.event())
        self.checker.write_text('raise SystemExit(1)')
        self.assertIn('systemMessage', hooks.handle(self.event('Stop', stop_hook_active=True)))

    def test_additions_deletions_and_checker_changes_trigger(self):
        for action in ('add', 'delete', 'checker'):
            with self.subTest(action=action):
                event = self.event(session_id=action)
                hooks.handle(event)
                if action == 'add':
                    (self.source.parent / 'new.md').write_text('new')
                elif action == 'delete':
                    self.source.unlink()
                else:
                    self.checker.write_text('raise SystemExit(0)')
                with patch.object(hooks.subprocess, 'run', wraps=subprocess.run) as run:
                    hooks.handle(self.event('Stop', session_id=action))
                    run.assert_called_once()

    def test_session_and_agent_state_do_not_mix(self):
        hooks.handle(self.event())
        self.source.write_text('changed')
        with patch.object(hooks.subprocess, 'run') as run:
            self.assertEqual(hooks.handle(self.event('Stop', session_id='other')), {})
            self.assertEqual(hooks.handle(self.event('Stop', agent_id='child')), {})
            run.assert_not_called()

    def test_timeout_is_reported_and_not_repeated(self):
        hooks.handle(self.event())
        self.source.write_text('changed')
        with patch.object(hooks.subprocess, 'run', side_effect=subprocess.TimeoutExpired('check', 30)) as run:
            self.assertIn('超时', hooks.handle(self.event('Stop'))['reason'])
            self.assertEqual(hooks.handle(self.event('Stop')), {})
            run.assert_called_once()

    def test_concurrent_input_change_does_not_cache_pass(self):
        hooks.handle(self.event())
        self.source.write_text('changed')
        def change(*args, **kwargs):
            self.source.write_text('changed again')
            return subprocess.CompletedProcess([], 0, '', '')
        with patch.object(hooks.subprocess, 'run', side_effect=change):
            self.assertIn('systemMessage', hooks.handle(self.event('Stop')))
        with patch.object(hooks.subprocess, 'run', wraps=subprocess.run) as run:
            hooks.handle(self.event('Stop'))
            run.assert_called_once()

    def test_real_checker_rejects_private_implementation_and_accepts_its_removal(self):
        # Real package inputs, outside the working tree and installed skills.
        shutil.rmtree(self.root / 'skills')
        shutil.rmtree(self.root / 'lib')
        shutil.copytree(ROOT / 'skills', self.root / 'skills', ignore=shutil.ignore_patterns('__pycache__','node_modules','dist'))
        shutil.copyfile(ROOT / 'packages.json', self.root / 'packages.json')
        shutil.copyfile(ROOT / 'scripts/package_skills.py', self.checker)
        shutil.copytree(ROOT / 'lib', self.root / 'lib', ignore=shutil.ignore_patterns('__pycache__','node_modules','dist'))
        ledger = json.loads((self.root / 'lib/registry/skill-dispositions.json').read_text())
        for row in ledger['legacy'] + ledger.get('retired', []):
            target = self.root / row['source']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['source'], target)
        hooks.handle(self.event())
        private = self.root / 'skills/507-demo/private-component.tsx'
        private.write_text('export default null\n')
        self.assertIn('undeclared', hooks.handle(self.event('Stop'))['reason'])
        private.unlink()
        self.assertEqual(hooks.handle(self.event('Stop')), {})

    def test_cli_json_protocol_and_inactive_example(self):
        script = self.root / 'scripts/codex_maintenance_hooks.py'
        script.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / 'scripts/codex_maintenance_hooks.py', script)
        result = subprocess.run([sys.executable, '-B', str(script)], input=json.dumps(self.event()), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})
        config = json.loads((ROOT / 'templates/codex-maintenance-hooks.example.json').read_text())
        self.assertEqual(set(config['hooks']), {'Stop'})


if __name__ == '__main__':
    unittest.main()

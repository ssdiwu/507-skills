#!/usr/bin/env python3
"""Verify the CI scanner detects a synthetic secret introduced by a merge."""
from pathlib import Path
import subprocess
import sys
import tempfile


def run(root, *args):
    return subprocess.run(args, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def git(root, *args):
    result = run(root, 'git', *args)
    if result.returncode:
        raise RuntimeError('Fixture Git operation failed: ' + ' '.join(args))


def main():
    scanner = Path(sys.argv[1]).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix='507-merge-secret-') as directory:
        root = Path(directory)
        git(root, 'init', '-q', '-b', 'main')
        git(root, 'config', 'user.name', 'Fixture')
        git(root, 'config', 'user.email', 'fixture@example.invalid')
        (root / 'base.txt').write_text('base\n')
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'base')
        git(root, 'checkout', '-qb', 'side')
        (root / 'side.txt').write_text('side\n')
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'side')
        git(root, 'checkout', '-q', 'main')
        (root / 'main.txt').write_text('main\n')
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'main')
        command = [str(scanner), 'git', '--log-opts=-m', '--redact=100', '--no-banner', '--no-color', '--verbose']
        if run(root, *command).returncode:
            raise RuntimeError('Clean history must pass')
        git(root, 'merge', '--no-commit', '--no-ff', 'side')
        secret = 'gh' + 'p_' + 'A1b2C3d4E5f6G7h8I9j0K1l2M3n4P5q6R7s8'
        (root / 'merge.txt').write_text('github_token = "' + secret + '"\n')
        git(root, 'add', '.')
        git(root, 'commit', '-qm', 'merge')
        result = run(root, *command)
        output = result.stdout + result.stderr
        if result.returncode != 1 or secret in output or 'github-pat' not in output or 'REDACTED' not in output:
            raise RuntimeError('Merge-only synthetic secret was not rejected and redacted')
        print('Clean history passed; merge-only synthetic secret rejected and redacted.')


if __name__ == '__main__':
    main()

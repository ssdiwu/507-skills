#!/usr/bin/env python3
"""Run the original v0.3.4 deterministic regressions in a disposable checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REVISION = 'a4c28d19bfea418333ff1487a958d33b797f2308'


def verify_snapshot(checkout):
    decisions = json.loads((ROOT / 'lib/catalog/registry/skill-dispositions.json').read_bytes())
    contracts = {path.relative_to(checkout).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in (checkout / 'archive/legacy').glob('*/*/SKILL.md')}
    if decisions['legacySnapshot'] != {'revision': REVISION, 'contracts': contracts}:
        raise SystemExit('旧名清单或合同指纹与 v0.3.4 原件不符')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-missing-browser', action='store_true')
    args = parser.parse_args()
    if subprocess.run(['git', '-C', str(ROOT), 'cat-file', '-e', REVISION + '^{commit}']).returncode:
        parser.exit(1, '需要含固定历史提交的 Git 仓库。浅克隆请先运行 git fetch --depth=1 origin tag v0.3.4\n')
    with tempfile.TemporaryDirectory(prefix='507-history-') as directory:
        checkout = Path(directory)
        subprocess.run(['git', 'init', '--quiet'], cwd=checkout, check=True)
        subprocess.run(['git', 'fetch', '--quiet', '--depth=1', '--no-tags', str(ROOT), REVISION], cwd=checkout, check=True)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', REVISION], cwd=checkout, check=True)
        verify_snapshot(checkout)
        subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_layout.LayoutTests.test_every_legacy_regression_still_has_its_cwd_and_script'], cwd=checkout / 'tests', check=True)
        command = [sys.executable, '-B', 'scripts/test_all.py']
        if args.allow_missing_browser:
            command.append('--allow-missing-browser')
        return subprocess.run(command, cwd=checkout).returncode


if __name__ == '__main__':
    sys.exit(main())

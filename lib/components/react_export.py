"""Data tools delegate all UI rendering to the one shared React exporter."""
import json
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile


def render_document(kind, data):
    entry = Path(__file__).parent / 'visual-runtime/scripts/render-artifact.mjs'
    with tempfile.TemporaryDirectory(prefix='507-react-document-') as directory:
        source = Path(directory) / 'input.json'
        source.write_text(json.dumps({'kind': kind, 'data': data}, ensure_ascii=False, allow_nan=False))
        try:
            run = subprocess.run(['node', str(entry), '--input', str(source), '--document'], capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValueError('Shared React renderer unavailable: ' + str(error)) from error
        if run.returncode:
            raise ValueError('Shared React renderer failed: ' + run.stderr.strip())
        return run.stdout


def renderer_fingerprint():
    root=Path(__file__).parent/'visual-runtime'
    files={}
    for directory, folders, names in os.walk(root):
        folders[:]=[name for name in folders if name not in {'node_modules','dist','__pycache__','.git'}]
        for name in names:
            path=Path(directory)/name
            files[path.relative_to(root).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    files['react_export.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()

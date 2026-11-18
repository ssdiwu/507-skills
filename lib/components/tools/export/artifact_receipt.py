#!/usr/bin/env python3
"""Record actual target files; signature inspection is not presentation acceptance."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import wave
import zipfile
from xml.etree import ElementTree


def unique(items):
    result = {}
    for k, v in items:
        if k in result:
            raise ValueError('duplicate JSON key: ' + k)
        result[k] = v
    return result


def inspect(path, kind):
    before = path.stat()
    size = before.st_size
    if not 0 < size <= 256 * 1024 * 1024:
        raise ValueError('target must be nonempty and at most 256 MiB')
    with path.open('rb') as handle:
        head = handle.read(32)
    metadata = {}
    if kind == 'png':
        if head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR' or len(head) < 24:
            raise ValueError('target is not a PNG signature')
        metadata = {'width': int.from_bytes(head[16:20], 'big'), 'height': int.from_bytes(head[20:24], 'big')}
        if not metadata['width'] or not metadata['height']:
            raise ValueError('invalid PNG dimensions')
    elif kind == 'jpeg':
        if not head.startswith(b'\xff\xd8\xff'):
            raise ValueError('target is not a JPEG signature')
    elif kind == 'wav':
        with wave.open(str(path), 'rb') as handle:
            rate, frames = handle.getframerate(), handle.getnframes()
            if not frames or not rate:
                raise ValueError('empty WAV')
            expected = frames * handle.getnchannels() * handle.getsampwidth()
            if len(handle.readframes(frames)) != expected:
                raise ValueError('truncated WAV frames')
            metadata = {'durationSeconds': frames / rate, 'sampleRate': rate,
                        'channels': handle.getnchannels()}
    elif kind == 'pptx':
        with zipfile.ZipFile(path) as archive:
            records = archive.infolist()
            names = [r.filename for r in records]
            if len(names) > 4096 or len(names) != len(set(names)) or sum(r.file_size for r in records) > 256 * 1024 * 1024:
                raise ValueError('oversized or duplicate Office entries')
            if any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts for n in names):
                raise ValueError('unsafe Office member path')
            slides = sorted(n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', n))
            if not {'[Content_Types].xml', 'ppt/presentation.xml'} <= set(names) or not slides:
                raise ValueError('missing native presentation parts')
            for name in ['[Content_Types].xml', 'ppt/presentation.xml', *slides]:
                ElementTree.fromstring(archive.read(name))
            metadata = {'slideParts': len(slides)}
    elif kind == 'mp4':
        if len(head) < 12 or head[4:8] != b'ftyp':
            raise ValueError('target is not an MP4 family signature')
        metadata = {'durationSeconds': None, 'durationReason': '需实际媒体探测工具读回，文件头不能证明时长或音视频轨。'}
    elif kind == 'html':
        path.read_text(encoding='utf-8')
    else:
        raise ValueError('unsupported kind: ' + str(kind))
    hasher = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            hasher.update(block)
    after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('target changed during inspection')
    return {'bytes': size, 'sha256': hasher.hexdigest(), 'metadata': metadata,
            'inspection': 'SIGNATURE_AND_SELECTED_STRUCTURE_ONLY', 'presentationAcceptance': 'NOT_PERFORMED'}


def collect(root, config):
    if config.get('schema') != 1 or not isinstance(config.get('files'), list) or not config['files']:
        raise ValueError('expected schema 1 and nonempty files')
    records = []
    seen = set()
    for item in config['files']:
        value = item['path']
        if not isinstance(value, str) or '\\' in value:
            raise ValueError('invalid target path')
        rel = PurePosixPath(value)
        normalized = rel.as_posix()
        if rel.is_absolute() or '..' in rel.parts or not rel.parts or normalized in seen:
            raise ValueError('unsafe or duplicate target path')
        seen.add(normalized)
        path = root
        for part in rel.parts:
            path /= part
            if path.is_symlink():
                raise ValueError('symlink target refused')
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('missing actual target: ' + value)
        records.append({'path': value, 'kind': item['kind'], **inspect(path, item['kind'])})
    return {'schema': 1, 'status': 'ACTUAL_FILES_RECORDED', 'files': records,
            'limits': ['文件存在、指纹和所列结构检查成立；未执行真实渲染、完整媒体解码、语义或作者接受。',
                       'HTML不能替代图片、可编辑PPTX或音视频；无实际目标文件保持未完成。']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-root', required=True)
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    try:
        root, config_path = Path(args.artifact_root), Path(args.input)
        if root.is_symlink() or not root.is_dir() or config_path.is_symlink() or not config_path.is_file():
            raise ValueError('explicit regular root and input required')
        if config_path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError('input exceeds 2 MiB')
        result = collect(root, json.loads(config_path.read_text(), object_pairs_hook=unique))
        result['inputSha256'] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, ElementTree.ParseError, wave.Error, EOFError) as exc:
        print(json.dumps({'status': 'INPUT_ERROR', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

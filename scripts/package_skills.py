#!/usr/bin/env python3
"""Validate a skill collection and its single explicit shared library; never copy resources into skills."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urlsplit

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {'skill-design','507-what','507-why','507-how','507-create','507-work','507-material','507-adapt','507-spec','507-do','507-review','507-issue','507-coordinate','507-deliver','507-retro','507-setup','507-product-map','507-clean','507-plan','507-visualize','507-demo'}
DISPOSITIONS = 'lib/registry/skill-dispositions.json'
class PackageError(ValueError):
    pass

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def rename_new(source, destination):
    """Publish a complete directory while refusing any concurrent destination."""
    if os.name == 'nt':
        os.rename(source, destination)  # Windows rename refuses an existing destination.
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == 'darwin':
        call = libc.renamex_np
        call.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        result = call(os.fsencode(source), os.fsencode(destination), 4)  # RENAME_EXCL
    elif sys.platform.startswith('linux') and hasattr(libc, 'renameat2'):
        call = libc.renameat2
        call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        result = call(-100, os.fsencode(source), -100, os.fsencode(destination), 1)  # RENAME_NOREPLACE
    else:
        raise PackageError('Exclusive directory publication unavailable on this platform')
    if result:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(destination))


def pairs(items):
    result = {}
    for key,value in items:
        if key in result: raise PackageError('Duplicate JSON key: '+key)
        result[key]=value
    return result

def within(root, relative, require=False):
    if not isinstance(relative,str) or not relative or '\\' in relative:
        raise PackageError('Expected POSIX relative path')
    rel=PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or relative=='.':
        raise PackageError('Unsafe relative path: '+relative)
    target=root
    for part in rel.parts:
        target/=part
        if target.is_symlink(): raise PackageError('Symlink not allowed: '+relative)
    if not target.resolve().is_relative_to(root.resolve()): raise PackageError('Path escapes root: '+relative)
    if require and not target.is_file(): raise PackageError('Missing file: '+relative)
    return target

def file_map(base):
    files={}
    for p in sorted(base.rglob('*')):
        if p.is_symlink(): raise PackageError('Symlink not allowed: '+str(p))
        if p.is_file(): files[p.relative_to(base).as_posix()]=p.read_bytes()
    return files

def metadata_scalar(raw):
    raw=raw.strip()
    if raw.startswith('"'):
        value=json.loads(raw)
        if not isinstance(value,str):raise PackageError('Metadata scalar must be text')
        return value
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    return raw.split(' #',1)[0].strip()

def load_manifest(root):
    config=json.loads(within(root,'packages.json',True).read_text(),object_pairs_hook=pairs)
    if not isinstance(config,dict):raise PackageError('Package manifest must be an object')
    if config.get('schema')!=3 or config.get('system')!='507-layered-capabilities' or config.get('sharedRoot')!='lib':
        raise PackageError('Expected collection schema 3 with per-skill RESOURCES.md declarations')
    entries=config.get('skills',[])
    if not isinstance(entries,list) or not all(isinstance(e,dict) for e in entries):raise PackageError('Skill entries must be objects')
    if len(entries)!=len(SKILL_NAMES) or {e.get('name') for e in entries}!=SKILL_NAMES:
        raise PackageError('Unknown, duplicate or missing skill identity')
    shared=config.get('sharedFiles',[])
    if not isinstance(shared,list) or not all(isinstance(p,str) for p in shared) or len(shared)!=len(set(shared)):
        raise PackageError('Invalid shared file inventory')
    for path in shared:
        if not path.startswith('lib/'): raise PackageError('Shared resources must live only in lib')
        within(root,path,True)
    shared_base=within(root,'lib')
    actual_shared={p.relative_to(root).as_posix() for p in shared_base.rglob('*') if p.is_file()
                   and not {'node_modules','dist','tests','__pycache__'}&set(p.relative_to(shared_base).parts)}
    if set(shared)!=actual_shared:raise PackageError('Undeclared or missing shared library resource')
    skill_root=within(root,'skills')
    extras=[p.name for p in skill_root.iterdir() if p.is_symlink() or (p.is_file() and p.name!='README.md')]
    if extras:raise PackageError('Undeclared files/materials in skills root: '+str(sorted(extras)))
    observed={p.name for p in within(root,'skills').iterdir() if p.is_dir()}
    if observed!=SKILL_NAMES: raise PackageError('Undeclared skill directory')
    entries=library_module(root).resource_entries(root, config)
    for entry in entries:
        name=entry['name']
        if entry.get('source')!='skills/'+name or entry.get('role') not in ['main','secondary']:
            raise PackageError('Invalid skill source or role: '+name)
        files=entry.get('files',[]);uses=entry.get('uses',[])
        if not isinstance(files,list) or len(files)!=len(set(files)) or not {'SKILL.md','RESOURCES.md','agents/openai.yaml'}<=set(files):
            raise PackageError('Missing or duplicate skill files: '+name)
        if not isinstance(uses,list) or len(uses)!=len(set(uses)) or not set(uses)<=set(shared):
            raise PackageError('Undeclared shared dependency: '+name+' '+str(sorted(set(uses)-set(shared))))
        validate_package(within(root,entry['source']),name,root,files,uses)
    return entries

def validate_package(base,name,collection_root=None,declared=None,uses=None):
    payload=file_map(base)
    if declared is not None and set(payload)!=set(declared):
        raise PackageError(name+': undeclared or missing skill files: extra='+str(sorted(set(payload)-set(declared)))+' missing='+str(sorted(set(declared)-set(payload))))
    for path,raw in payload.items():
        if path not in ['SKILL.md','RESOURCES.md','agents/openai.yaml'] and not (path.startswith('references/') and path.endswith('.md')):
            raise PackageError(name+': private executable/component/runtime is prohibited: '+path)
        if b'Generated by 507 package_skills; source=lib/' in raw:
            raise PackageError(name+': copied shared resource is prohibited: '+path)
        if path.endswith('/SKILL.md'): raise PackageError('Nested skill is prohibited')
    text=payload.get('SKILL.md',b'').decode()
    front=re.match(r'^---\n(.*?)\n---\n',text,re.S)
    if not front:raise PackageError('Invalid frontmatter: '+name)
    contract={}
    for key in ['name','description']:
        found=re.findall(r'^'+key+r':\s*(.+)$',front.group(1),re.M)
        if len(found)!=1:raise PackageError('Missing or duplicate contract field: '+key)
        contract[key]=metadata_scalar(found[0])
    if contract['name']!=name or not contract['description']:
        raise PackageError('Invalid skill contract: '+name)
    meta=payload.get('agents/openai.yaml',b'').decode()
    if not meta.startswith('interface:\n') or len(re.findall(r'^interface:',meta,re.M))!=1:
        raise PackageError('Missing or duplicate interface metadata')
    values={}
    for key in ['display_name','short_description','default_prompt']:
        found=re.findall(r'^  '+key+r':\s*(.+)$',meta,re.M)
        if len(found)!=1:raise PackageError('Missing or duplicate metadata: '+key)
        values[key]=metadata_scalar(found[0])
        if not values[key]:raise PackageError('Empty metadata: '+key)
    if not re.search(r'\$'+re.escape(name)+r'(?![a-zA-Z0-9_-])',values['default_prompt']):
        raise PackageError('Metadata identity differs from actual default_prompt')
    if collection_root is None:
        raise PackageError('Explicit shared library dependency is required; use the collection layout skills/ + lib/')
    common_hashes={digest(p.read_bytes().strip()) for p in (collection_root/'lib').rglob('*.md')
                   if not {'node_modules','dist','tests','__pycache__'}&set(p.relative_to(collection_root/'lib').parts)}
    for rel,raw in payload.items():
        if rel.endswith('.md') and digest(raw.strip()) in common_hashes:
            raise PackageError(name+': verbatim shared text copy is prohibited: '+rel)
        if not rel.endswith('.md'):continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',raw.decode()):
            parsed=urlsplit(link.strip('<>'))
            if parsed.scheme in ['http','https','mailto'] or link.startswith('#'):continue
            if parsed.scheme or parsed.path.startswith('/'):raise PackageError('Unsupported absolute reference: '+link)
            target=((base/rel).parent/unquote(parsed.path)).resolve()
            if not target.is_relative_to(collection_root.resolve()):raise PackageError('Reference escapes collection: '+link)
            if not target.is_file():raise PackageError('Missing collection reference: '+str(target))
            if uses is not None and target.is_relative_to(collection_root/'lib'):
                dependency=target.relative_to(collection_root).as_posix()
                if dependency not in uses:
                    raise PackageError(name+': Undeclared direct shared reference: '+dependency+' in '+rel)
    return payload

def library_module(root):
    import importlib.util
    path=within(root,'lib/components/library_view.py',True)
    spec=importlib.util.spec_from_file_location('collection_library_view',path)
    module=importlib.util.module_from_spec(spec)
    # Loading a staged source must not add bytecode to the immutable collection.
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module

def check_skill_index(root):
    module=library_module(root)
    actual,_=module.read_index(root/'lib/registry/skill-entry-index.md')
    view=module.project(root,root/'packages.json',root/'lib/catalog.json',root/DISPOSITIONS)
    if actual!=module.skill_index(view):raise PackageError('Stale skill-entry index; regenerate from source declarations')


def check_shared_links(root, paths):
    for rel in paths:
        if not rel.endswith('.md'):continue
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(root/rel).read_text()):
            parsed=urlsplit(link.strip('<>'))
            if parsed.scheme or link.startswith('#'):continue
            target=((root/rel).parent/unquote(parsed.path)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                raise PackageError('Missing shared collection reference: '+rel+' -> '+link)


def check(root,entries=None):
    entries=entries or load_manifest(root)
    payload={}
    for entry in entries:
        files=validate_package(root/entry['source'],entry['name'],root,entry['files'],entry['uses'])
        payload.update({entry['source']+'/'+p:raw for p,raw in files.items()})
    config=json.loads((root/'packages.json').read_text())
    for rel in config['sharedFiles']:
        raw=within(root,rel,True).read_bytes()
        if rel.endswith('.py'):compile(raw,rel,'exec')
        payload[rel]=raw
    check_shared_links(root, config['sharedFiles'])
    check_skill_index(root)
    return payload

def build(root,output=None):
    payload=check(root)
    for rel in ['packages.json','lib/catalog.json']:
        payload[rel]=within(root,rel,True).read_bytes()
    records={rel:digest(raw) for rel,raw in payload.items()}
    fingerprint=digest(json.dumps(records,sort_keys=True,separators=(',',':')).encode())
    manifest={'schema':3,'system':'507-layered-capabilities','layout':'skills/ + one lib/','fingerprint':fingerprint,'files':records}
    raw=(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
    output=Path(output).absolute() if output else root/'dist'
    if output.is_symlink():raise PackageError('Output symlink is prohibited')
    resolved=output.resolve()
    if resolved==root.resolve() or root.resolve().is_relative_to(resolved) or any(resolved.is_relative_to(root/x) for x in ['lib','skills','scripts','tests','archive']):
        raise PackageError('Build output overlaps source')
    output.mkdir(parents=True,exist_ok=True);final=output/fingerprint
    expected={**payload,'bundle.json':raw}
    if final.exists():
        if final.is_symlink() or file_map(final)!=expected:raise PackageError('Existing immutable collection differs; preserved')
        return final,manifest
    stage=Path(tempfile.mkdtemp(prefix='.collection-',dir=output))
    try:
        for rel,content in expected.items():
            p=within(stage,rel);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
        if file_map(stage)!=expected:raise PackageError('Staged collection differs')
        for entry in library_module(stage).resource_entries(stage,json.loads((root/'packages.json').read_text())):
            validate_package(stage/entry['source'],entry['name'],stage,entry['files'],entry['uses'])
        check_shared_links(stage, json.loads((root/'packages.json').read_text())['sharedFiles'])
        rename_new(stage,final)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return final,manifest

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['check','build'])
    parser.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv);root=args.root.resolve()
    if args.output and args.action!='build':parser.error('--output is only valid for build')
    try:
        if args.action=='build':
            path,record=build(root,args.output);result={'status':'PASS','action':'build','path':str(path),'fingerprint':record['fingerprint'],'files':len(record['files']),'sharedCopies':0}
        else:
            data=check(root);result={'status':'PASS','action':'check','skills':len(SKILL_NAMES),'files':len(data),'sharedCopies':0}
        print(json.dumps(result,ensure_ascii=False));return 0
    except (PackageError,OSError,ValueError,KeyError,TypeError,UnicodeError,SyntaxError) as error:
        print(json.dumps({'status':'FAIL','action':args.action,'error':str(error)},ensure_ascii=False),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())

"""Reject misleading format claims and incomplete library projections."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
 value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
receipt=module('artifact_receipt');library=module('library_view')

class ActualFileTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def test_html_renamed_as_png_is_not_an_image(self):
  (self.root/'01.png').write_text('<html>card</html>')
  with self.assertRaisesRegex(ValueError,'PNG'):receipt.collect(self.root,{'schema':1,'files':[{'path':'01.png','kind':'png'}]})
 def test_wav_duration_is_actual_but_acceptance_remains_unknown(self):
  p=self.root/'voice.wav'
  with wave.open(str(p),'wb') as w:w.setparams((1,2,8000,0,'NONE','not compressed'));w.writeframes(b'\x00\x00'*8000)
  r=receipt.collect(self.root,{'schema':1,'files':[{'path':'voice.wav','kind':'wav'}]})
  self.assertEqual(r['files'][0]['metadata']['durationSeconds'],1)
  self.assertEqual(r['files'][0]['presentationAcceptance'],'NOT_PERFORMED')
 def test_pptx_without_native_slides_is_refused(self):
  with zipfile.ZipFile(self.root/'deck.pptx','w') as z:z.writestr('index.html','slides')
  with self.assertRaisesRegex(ValueError,'native'):receipt.collect(self.root,{'schema':1,'files':[{'path':'deck.pptx','kind':'pptx'}]})
 def test_path_escape_and_symlink_are_refused(self):
  p=self.root/'x.html';p.write_text('hello');(self.root/'link.html').symlink_to(p)
  for path in ['../x.html','link.html']:
   with self.assertRaises(ValueError):receipt.collect(self.root,{'schema':1,'files':[{'path':path,'kind':'html'}]})
 def test_alias_paths_are_one_file(self):
  (self.root/'x.html').write_text('hello')
  with self.assertRaisesRegex(ValueError,'duplicate'):
   receipt.collect(self.root,{'schema':1,'files':[{'path':'x.html','kind':'html'},{'path':'./x.html','kind':'html'}]})
 def test_missing_target_cannot_be_recorded(self):
  with self.assertRaisesRegex(ValueError,'missing actual'):receipt.collect(self.root,{'schema':1,'files':[{'path':'missing.mp4','kind':'mp4'}]})

class LibraryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'author';self.root.mkdir()
  for path,body in [('next/skills/a/SKILL.md','---\nname: a\ndescription: A\n---\n'),('next/skills/a/agents/openai.yaml','interface:\n'),('common/old/SKILL.md','legacy'),('lib/methods/m.md','method'),('next/skills/a/references/shared/m.md','copy')]:
   p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
  self.packages={'skills':[{'name':'a','role':'main','source':'next/skills/a','files':['SKILL.md','agents/openai.yaml'],'shared':[{'source':'lib/methods/m.md','target':'references/shared/m.md'}]}]}
  self.catalog={'methods':[{'source':'lib/methods/m.md','consumers':[{'skillId':'a'}]}],'components':[]}
  self.disp={'date':'2026-10-13','legacy':[{'id':'old','group':'common','verification':'not business tested','dropped':[],'source':'common/old/SKILL.md','decision':'merge','reason':'shared','retained':['action'],'targets':['lib/methods/m.md'],'consumers':['a']}],'pending':[],'historicalPlanning':{}}
 def tearDown(self):self.temp.cleanup()
 def run_projection(self):
  for name,data in [('packages',self.packages),('catalog',self.catalog),('decisions',self.disp)]:
   (self.root/(name+'.json')).write_text(json.dumps(data))
  return library.project(self.root,self.root/'packages.json',self.root/'catalog.json',self.root/'decisions.json')
 def test_source_projection_never_claims_runtime(self):
  r=self.run_projection();self.assertEqual(r['status'],'SOURCE_PROJECTED');self.assertEqual(r['implementation']['entrypoints'],1);self.assertEqual(r['implementation']['sharedCopies'],1);self.assertNotIn('businessVerified',r)
 def test_legacy_missing_item_is_not_a_complete_map(self):
  self.disp['legacy']=[]
  with self.assertRaisesRegex(ValueError,'exact source'):self.run_projection()
 def test_undeclared_consumer_is_refused(self):
  self.catalog['methods'][0]['consumers']=[{'skillId':'unknown'}]
  with self.assertRaisesRegex(ValueError,'consumers differ'):self.run_projection()
 def test_retained_action_requires_an_actual_source(self):
  self.disp['legacy'][0]['targets']=['lib/methods/no.md']
  with self.assertRaisesRegex(ValueError,'missing source'):self.run_projection()
 def test_catalog_missing_or_duplicate_resource_is_refused(self):
  record=self.catalog['methods'][0]
  for entries in [[],[record,record]]:
   self.catalog['methods']=entries
   with self.assertRaisesRegex(ValueError,'catalog must exactly'):self.run_projection()
 def test_legacy_identity_and_source_must_match(self):
  self.disp['legacy'][0]['source']='lib/methods/m.md'
  with self.assertRaisesRegex(ValueError,'match identity'):self.run_projection()
 def test_root_readme_is_not_a_consumed_capability(self):
  (self.root/'README.md').write_text('map');self.disp['legacy'][0]['targets']=['README.md']
  with self.assertRaisesRegex(ValueError,'no declared current'):self.run_projection()
 def test_required_web_field_is_not_optional(self):
  del self.disp['legacy'][0]['dropped']
  with self.assertRaisesRegex(ValueError,'legacy field'):self.run_projection()
 def test_duplicate_keys_are_refused(self):
  with self.assertRaisesRegex(ValueError,'duplicate JSON'):json.loads('{"x":1,"x":2}',object_pairs_hook=library.pairs)

 def write_index(self,index=None):
  index=index or library.skill_index(self.run_projection())
  path=self.root/'index.md';path.write_text(library.index_markdown(index));return path
 def query(self,name,index=None,extra=()):
  path=self.write_index(index)
  return subprocess.run([sys.executable,str(ROOT/'library_view.py'),'--index-file',str(path),'--lookup',name,*extra],capture_output=True,text=True)
 def test_standalone_lookup_works_without_author_tree_or_installed_candidate(self):
  path=self.write_index();isolated=Path(self.temp.name)/'runtime';isolated.mkdir()
  shutil.copy2(ROOT/'library_view.py',isolated/'lookup.py');shutil.copy2(path,isolated/'index.md')
  shutil.rmtree(self.root)
  run=subprocess.run([sys.executable,str(isolated/'lookup.py'),'--index-file',str(isolated/'index.md'),'--lookup','old'],cwd=isolated,capture_output=True,text=True)
  self.assertEqual(run.returncode,0,run.stderr);r=json.loads(run.stdout)
  self.assertEqual(r['status'],'LEGACY_DECLARATION_FOUND');self.assertEqual(r['currentCandidates'][0]['name'],'a')
  self.assertEqual(r['runtimeAvailability'],'NOT_CHECKED');self.assertEqual(r['actionAuthority'],'UNCHANGED')
  self.assertEqual({p.name for p in isolated.iterdir()},{'lookup.py','index.md'})
 def test_unknown_name_does_not_guess_or_activate_a_candidate(self):
  run=self.query('older');self.assertEqual(run.returncode,1,run.stderr);r=json.loads(run.stdout)
  self.assertEqual(r['status'],'UNKNOWN_NAME');self.assertEqual(r['currentCandidates'],[]);self.assertIsNone(r['legacyOrigin'])
 def test_current_name_wins_but_preserves_same_name_legacy_origin(self):
  index=library.skill_index(self.run_projection());index['legacy'][0]['id']='a'
  run=self.query('a',index);self.assertEqual(run.returncode,0,run.stderr);r=json.loads(run.stdout)
  self.assertEqual(r['status'],'CURRENT_DECLARATION_FOUND');self.assertEqual(r['legacyOrigin']['id'],'a')
  self.assertEqual([v['name'] for v in r['currentCandidates']],['a'])
 def test_multiple_consumers_are_declarations_not_an_executed_chain(self):
  index=library.skill_index(self.run_projection());index['current'].append({**index['current'][0],'name':'b','entry':'b/SKILL.md'})
  index['legacy'][0]['consumers']=['a','b']
  run=self.query('old',index);self.assertEqual(run.returncode,0,run.stderr);r=json.loads(run.stdout)
  self.assertEqual([v['name'] for v in r['currentCandidates']],['a','b']);self.assertNotIn('execution',r)
  self.assertEqual(r['actionAuthority'],'UNCHANGED');self.assertFalse((self.root/'next/skills/b').exists())
 def test_explicitly_dropped_name_has_no_replacement_candidate(self):
  index=library.skill_index(self.run_projection());old=index['legacy'][0]
  old.update(decision='drop',retained=[],targets=[],consumers=[])
  run=self.query('old',index);self.assertEqual(run.returncode,0,run.stderr)
  self.assertEqual(json.loads(run.stdout)['currentCandidates'],[])
 def test_invalid_index_refuses_unknown_consumer_or_unsafe_path(self):
  original=library.skill_index(self.run_projection())
  for key,value in [('consumers',['missing']),('targets',['../outside.md']),('source','/outside.md'),('dropped',[{'mechanism':True,'reason':'x'}])]:
   index=json.loads(json.dumps(original));index['legacy'][0][key]=value
   with self.subTest(key=key):
    run=self.query('old',index);self.assertEqual(run.returncode,2,run.stdout+run.stderr)
    self.assertEqual(json.loads(run.stderr)['status'],'INPUT_ERROR');self.assertEqual(run.stdout,'')
 def test_duplicate_identity_symlink_and_mixed_query_modes_are_refused(self):
  index=library.skill_index(self.run_projection());index['current'].append(dict(index['current'][0]))
  self.assertEqual(self.query('old',index).returncode,2)
  path=self.write_index();link=self.root/'linked.md';link.symlink_to(path)
  run=subprocess.run([sys.executable,str(ROOT/'library_view.py'),'--index-file',str(link),'--lookup','old'],capture_output=True,text=True)
  self.assertEqual(run.returncode,2,run.stdout+run.stderr)
  self.assertEqual(self.query('old',extra=('--source-root',str(self.root))).returncode,2)

if __name__=='__main__':unittest.main()

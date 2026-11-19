import test from 'node:test'
import assert from 'node:assert/strict'
import {mkdtempSync,writeFileSync,readFileSync,existsSync,rmSync,mkdirSync,symlinkSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {fileURLToPath} from 'node:url'
import {spawnSync} from 'node:child_process'
import {checkScene,assertSceneUnchanged,listItems,inspectItem,searchItems,main} from './component-library.mjs'
const root=fileURLToPath(new URL('..',import.meta.url)),entry=join(root,'scripts/render-artifact.mjs')
const fixture=fn=>{const dir=mkdtempSync(join(tmpdir(),'507-library-test-'));try{return fn(dir)}finally{rmSync(dir,{recursive:true,force:true})}}
const scene=body=>`import React from 'react';export default function Scene(){return ${body}}`
test('CLI through an installation directory link returns results and failure status', () => fixture(dir => {
 const alias = join(dir, 'installed runtime')
 symlinkSync(root, alias, 'junction')
 const command = join(alias, 'scripts/component-library.mjs')
 for (const [args, code, status] of [
  [['list'], 0, 'LISTED'],
  [['search', 'quantum-entanglement-zebra'], 1, 'NO_MATCH'],
  [['unknown-command'], 2, 'ERROR'],
 ]) {
  const result = spawnSync(process.execPath, [command, ...args], {encoding: 'utf8'})
  assert.equal(result.status, code, result.stderr)
  assert.equal(JSON.parse(result.stdout).status, status)
 }
}))
test('discovery connects live exports, previews and differently structured examples',()=>{
 const items=listItems(),ids=new Set(items.map(x=>x.id));assert.equal(ids.size,items.length)
 for(const id of ['kit:Field','kit:Stage','diagram:queue','example:review-flow','example:record-browser'])assert.ok(ids.has(id))
 assert.ok(!items.some(x=>x.id.startsWith('ui:')))
 assert.ok(!items.some(x=>x.preview==='?components'))
 assert.equal(items.find(x=>x.id==='kit:Field').kind,'simulation')
 assert.notEqual(items.find(x=>x.id==='example:review-flow').structure,items.find(x=>x.id==='example:record-browser').structure)
 for(const x of items){assert.ok(existsSync(x.source));assert.ok(x.preview);if(x.api)for(const id of x.api)assert.ok(ids.has(id),id)}
 assert.ok(searchItems('表单错误修正')[0].id.startsWith('example:'))
 assert.ok(searchItems('无结果').some(x=>x.id==='example:record-browser'));assert.ok(searchItems('列表详情空状态').some(x=>x.id==='example:record-browser'));assert.ok(searchItems('排队等待').some(x=>x.id==='diagram:queue'));assert.equal(inspectItem('diagram:queue').inputExample.pages[0].blocks[0].type,'queue');assert.deepEqual(searchItems('quantum-entanglement-zebra'),[])
 assert.equal(main(['search','quantum-entanglement-zebra']).status,'NO_MATCH');assert.equal(main(['inspect','kit:Invented']).status,'NOT_FOUND')
})
test('scene API inspection uses real kit props and source with explicit omission',()=>{
 const stage=inspectItem('kit:Stage');assert.ok(stage.props.some(p=>p.name==='width'&&p.required));assert.ok(stage.props.some(p=>p.name==='height'&&p.required));assert.match(stage.declaration.text,/StageProps/)
})
test('external TSX and JSX reject invalid props and required-prop omissions',()=>fixture(dir=>{
 for(const ext of ['tsx','jsx'])for(const body of ['<button type="sparkly">Save</button>','<textarea rows="not-a-number"/>','<button href="/path">Not a link</button>']){
  const file=join(dir,'scene.'+ext);writeFileSync(file,scene(body));const r=checkScene(file);assert.equal(r.status,'INVALID');assert.ok(r.diagnostics.some(d=>d.code===2322||d.code===2741));assert.ok(r.diagnostics.some(d=>d.file===file&&d.line===1))
 }
}))
test('export gate rejects original invalid action without output and protects prior output',()=>fixture(dir=>{
 const file=join(dir,'scene.tsx'),out=join(dir,'out');writeFileSync(file,scene('<button type="sparkly">Save</button>'))
 let r=spawnSync(process.execPath,[entry,'--scene',file,'--title','Test','--out-dir',out],{encoding:'utf8'});assert.equal(r.status,2);assert.equal(existsSync(out),false);assert.ok(JSON.parse(r.stderr).diagnostics.length)
 writeFileSync(file,scene('<button type="button">Save</button>'));r=spawnSync(process.execPath,[entry,'--scene',file,'--title','Test','--out-dir',out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr)
 const before=readFileSync(join(out,'index.html'));assert.equal(JSON.parse(readFileSync(join(out,'manifest.json'))).sceneCheck.status,'CHECKED')
 writeFileSync(file,scene('<button type="sparkly">Save</button>'));assert.equal(spawnSync(process.execPath,[entry,'--scene',file,'--title','Test','--out-dir',out]).status,2);assert.deepEqual(readFileSync(join(out,'index.html')),before)
}))
test('project paths and relative imports are checked without executing user code',()=>fixture(dir=>{
 mkdirSync(join(dir,'src'));const child=join(dir,'src/piece.tsx'),file=join(dir,'scene.tsx'),config=join(dir,'tsconfig.json')
 writeFileSync(child,`import React from 'react';export const Piece=()=> <button type="button">OK</button>`)
 writeFileSync(config,JSON.stringify({compilerOptions:{baseUrl:'.',paths:{'@/*':['src/*']}}}))
 writeFileSync(file,"import {Piece} from '@/piece';if(typeof window==='undefined')throw new Error('do not execute');export default function Scene(){return <Piece/>}")
 assert.equal(checkScene(file,{project:config}).status,'CHECKED')
 const out=join(dir,'out');const r=spawnSync(process.execPath,[entry,'--scene',file,'--project',config,'--title','Paths','--out-dir',out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr)
 writeFileSync(child,`import React from 'react';export const Piece=()=> <button type="button" inventedAttribute="x"/>`)
 const invalid=checkScene(file,{project:config});assert.equal(invalid.status,'INVALID');assert.ok(invalid.diagnostics.some(d=>d.file===child))
}))
test('default shape, source drift, missing input and malformed config are not passes',()=>fixture(dir=>{
 const file=join(dir,'scene.tsx');writeFileSync(file,'export default 42');assert.equal(checkScene(file).status,'INVALID')
 writeFileSync(file,scene('<button type="button">OK</button>'));const checked=checkScene(file);assert.equal(checked.status,'CHECKED');writeFileSync(file,scene('<button type="button">Changed</button>'));assert.throws(()=>assertSceneUnchanged(checked),/changed after type check/)
 assert.throws(()=>checkScene(join(dir,'missing.tsx')),/existing/)
 const config=join(dir,'tsconfig.json');writeFileSync(config,'{"compilerOptions":');assert.throws(()=>checkScene(file,{project:config}))
 assert.throws(()=>main(['check',file,'--unexpected']),/Usage/)
}))

test('project noCheck cannot bypass scene validation or produce an export',()=>fixture(dir=>{
 const file=join(dir,'scene.tsx'),config=join(dir,'tsconfig.json'),out=join(dir,'out')
 writeFileSync(file,scene('<button type="sparkly">Bad</button>'));writeFileSync(config,JSON.stringify({compilerOptions:{noCheck:true}}))
 assert.equal(checkScene(file,{project:config}).status,'INVALID')
 const result=spawnSync(process.execPath,[entry,'--scene',file,'--project',config,'--title','No check','--out-dir',out],{encoding:'utf8'})
 assert.equal(result.status,2);assert.equal(existsSync(out),false)
}))
test('source names containing node_modules remain tracked, including transitive changes',()=>fixture(dir=>{
 const folder=join(dir,'node_modules_local');mkdirSync(folder)
 const file=join(folder,'scene.tsx'),child=join(folder,'piece.tsx')
 writeFileSync(child,'export default function Piece(){return <p>Before</p>}')
 writeFileSync(file,"import Piece from './piece';export default function Scene(){return <Piece/>}")
 const result=checkScene(file);assert.equal(result.status,'CHECKED');assert.ok(result.checkedFiles.some(x=>x.path.endsWith('/node_modules_local/scene.tsx')))
 writeFileSync(child,'export default function Piece(){return <p>After</p>}');assert.throws(()=>assertSceneUnchanged(result),/changed after type check/)
}))
test('browser conditional source and its call-site contract match the actual bundle',()=>fixture(dir=>{
 const pkg=join(dir,'node_modules/sample-pkg');mkdirSync(pkg,{recursive:true})
 writeFileSync(join(pkg,'package.json'),JSON.stringify({name:'sample-pkg',version:'1.0.0',exports:{browser:'./browser.tsx',default:'./default.tsx'}}));writeFileSync(join(pkg,'LICENSE'),'MIT test fixture')
 writeFileSync(join(pkg,'default.tsx'),'export default function Piece({label}:{label:number}){return <p>{label}</p>}')
 const browser=join(pkg,'browser.tsx'),file=join(dir,'scene.tsx')
 writeFileSync(file,"import Piece from 'sample-pkg';export default function Scene(){return <Piece label={42}/>} ")
 writeFileSync(browser,'export default function Piece({label}:{label:string}){return <p>{label}</p>}')
 assert.equal(checkScene(file).status,'INVALID') // Default branch would accept this prop.
 writeFileSync(file,`import Piece from 'sample-pkg';export default function Scene(){return <Piece label="OK"/>}`)
 assert.equal(checkScene(file).status,'CHECKED')
 const result=spawnSync(process.execPath,[entry,'--scene',file,'--title','Browser branch','--out-dir',join(dir,'out')],{encoding:'utf8'});assert.equal(result.status,0,result.stderr)
 const sources=JSON.parse(readFileSync(join(dir,'out/scene.json'))).sources;assert.ok(sources.some(x=>x.path.endsWith('/browser.tsx')));assert.ok(!sources.some(x=>x.path.endsWith('/default.tsx')))
 writeFileSync(browser,'export default function Piece({label}:{label:string}){const n:number="bad";return <p>{label}{n}</p>}')
 const invalid=checkScene(file);assert.equal(invalid.status,'INVALID');assert.ok(invalid.diagnostics.some(x=>x.file.endsWith('/browser.tsx')))
}))

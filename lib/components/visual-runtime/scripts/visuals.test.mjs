import test from 'node:test'
import assert from 'node:assert/strict'
import {spawnSync} from 'node:child_process'
import {mkdtempSync,readFileSync,writeFileSync,existsSync,rmSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {fileURLToPath} from 'node:url'
const runtime=fileURLToPath(new URL('..',import.meta.url)),entry=join(runtime,'scripts/render-artifact.mjs')
const model=block=>({mode:'site',title:'测试',pages:[{title:'关系',blocks:[block]}],sources:[{id:'s',label:'依据',url:'https://example.com/evidence'}]})
function fixture(data,check){const folder=mkdtempSync(join(tmpdir(),'507-react-test-'));try{const input=join(folder,'input.json'),out=join(folder,'out');writeFileSync(input,typeof data==='string'?data:JSON.stringify(data));const r=spawnSync(process.execPath,[entry,'--input',input,'--out-dir',out],{encoding:'utf8'});return check(r,out,input)}finally{rmSync(folder,{recursive:true,force:true})}}
test('one React exporter renders all five and preserves existing output',()=>{const folder=mkdtempSync(join(tmpdir(),'507-react-example-'));try{const out=join(folder,'out');const run=spawnSync(process.execPath,[entry,'--example','--out-dir',out],{encoding:'utf8'});assert.equal(run.status,0,run.stderr);const html=readFileSync(join(out,'index.html'),'utf8');for(const kind of ['timeline','steps','comparison','layout','queue'])assert.match(html,new RegExp('viz-'+kind+'-block'));const licenses=JSON.parse(html.match(/id="third-party-licenses" type="application\/json">([\s\S]*?)<\/script>/)[1]);for(const name of ['react','react-dom','scheduler','lucide-react','@radix-ui/react-dialog','shadcn/ui adaptations','react-remove-scroll-bar'])assert.ok(licenses.some(x=>x.name===name),'Missing notice: '+name);for(const item of licenses)assert.match(item.text,/Permission (?:is hereby granted|to use, copy, modify)/);const before=readFileSync(join(out,'manifest.json'));assert.equal(spawnSync(process.execPath,[entry,'--example','--out-dir',out]).status,2);assert.deepEqual(readFileSync(join(out,'manifest.json')),before)}finally{rmSync(folder,{recursive:true,force:true})}})
test('unknown/range/zero remain distinct and input is preserved byte for byte',()=>fixture(model({type:'comparison',title:'比较',unit:'分钟',sourceIds:['s'],items:[{label:'已知',value:[1,2]},{label:'未知',value:null},{label:'零',value:0}]}),(r,out,input)=>{assert.equal(r.status,0,r.stderr);const html=readFileSync(join(out,'index.html'),'utf8'),unknown=html.split('<strong>未知</strong>')[1].split('<strong>零</strong>')[0];assert.match(unknown,/暂无数值，不绘制长度/);assert.doesNotMatch(unknown,/viz-track/);assert.match(html,/0 分钟/);assert.match(html,/#source-s/);assert.deepEqual(readFileSync(join(out,'content.json')),readFileSync(input))}))
test('unsupported fields, negative/reversed values and unsupported scheduler refuse output',()=>{for(const block of [{type:'invented',title:'未知'},{type:'steps',title:'步骤',items:[{label:'一',hiddenCondition:'条件'}]},...[true,-1,[3,1]].map(value=>({type:'comparison',title:'比较',items:[{label:'数',value}]})),{type:'queue',title:'排队',model:'parallel',taskForms:[1],minutesPerForm:1,remainingMinutes:0}])fixture(model(block),(r,out)=>{assert.equal(r.status,2,r.stderr);assert.equal(existsSync(out),false)})})
test('a 400 digit raw number is rejected with JSON error and no output',()=>fixture('{"mode":"site","title":"x","pages":[{"title":"x","blocks":[{"type":"comparison","title":"x","items":[{"label":"x","value":'+'1'.repeat(400)+'}]}]}]}',(r,out)=>{assert.equal(r.status,2);assert.equal(JSON.parse(r.stderr).status,'ERROR');assert.equal(existsSync(out),false)}))
test('untrusted text is escaped and an explicit offline policy is retained',()=>fixture(model({type:'steps',title:'<script>alert(1)</script>',items:[{label:'<img src=x onerror=alert(1)>'}]}),(r,out)=>{assert.equal(r.status,0,r.stderr);const html=readFileSync(join(out,'index.html'),'utf8');assert.doesNotMatch(html,/<img src=x|<script>alert/);assert.match(html,/&lt;img/);assert.match(html,/connect-src 'none'/);const embedded=JSON.parse(html.match(/id="visual-model" type="application\/json">([\s\S]*?)<\/script>/)[1]);assert.equal(embedded.data.title,'测试');assert.equal(embedded.data.pages[0].blocks[0].title,'<script>alert(1)</script>');assert.equal(embedded.data.pages[0].blocks[0].items[0].label,'<img src=x onerror=alert(1)>')}))
test('queue SSR exposes correct estimates, platform count and model assumption',()=>fixture(model({type:'queue',title:'排队',model:'serial',taskForms:[1,2],minutesPerForm:[1,1.5],remainingMinutes:[1,2]}),(r,out)=>{assert.equal(r.status,0,r.stderr);const html=readFileSync(join(out,'index.html'),'utf8'),text=html.replace(/<[^>]+>/g,'');assert.match(text,/4–6.5 分钟后开始处理/);assert.match(text,/全平台前方有 2 个等待任务/);assert.match(text,/单处理通道/);assert.match(text,/\(1–2\) \+ 3 × \(1–1.5\)/)}))
test('bilingual artifacts pre-render in the selected language and reject malformed translations',()=>{
 const en={mode:'site',title:'Meeting notes',pages:[{title:'Queue',blocks:[{type:'queue',title:'Wait estimate',id:'wait',model:'serial',taskForms:[1,2],minutesPerForm:1.5,remainingMinutes:1.5}]}]}
 const zh={...en,title:'会议纪要',pages:[{title:'排队',blocks:[{...en.pages[0].blocks[0],title:'等待估算'}]}]}
 fixture({...en,language:'en',translations:{'zh-CN':zh}},(r,out)=>{assert.equal(r.status,0,r.stderr);const html=readFileSync(join(out,'index.html'),'utf8');assert.match(html,/<html lang="en">/);assert.match(html,/Estimated wait: about/);assert.match(html.replace(/<[^>]+>/g,''),/6 minutes/);assert.match(html,/Waiting tasks ahead across the platform/);assert.match(html,/aria-label="Language \/ 阅读语言"/);assert.doesNotMatch(html,/>模拟界面</)})
 for(const data of [{...en,language:'fr'},{...en,language:'en',translations:{en:zh}},{...en,translations:{'zh-CN':zh}},{...en,language:'en',translations:{'zh-CN':{...zh,translations:{}}}},{...en,language:'en',translations:{'zh-CN':{...zh,mode:'deck'}}},{...en,language:'en',translations:{'zh-CN':{...zh,pages:[...zh.pages,...zh.pages]}}},{...en,language:'en',translations:{'zh-CN':{...zh,pages:[{title:'排队',blocks:[{...zh.pages[0].blocks[0],id:'other'}]}]}}},{...en,language:'en',translations:{'zh-CN':{...zh,pages:[{title:'排队',blocks:[{...zh.pages[0].blocks[0],taskForms:[2,2]}]}]}}}])fixture(data,(r,out)=>{assert.equal(r.status,2,r.stderr);assert.equal(existsSync(out),false)})
})

test('the same exporter provides an offline live-control catalogue and strict document shape',()=>{const folder=mkdtempSync(join(tmpdir(),'507-components-test-'));try{const out=join(folder,'out');const r=spawnSync(process.execPath,[entry,'--components','--out-dir',out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);const html=readFileSync(join(out,'index.html'),'utf8');assert.match(html,/ui-catalog/);assert.match(html,/role="tablist"/);assert.doesNotMatch(html,/@import|<script[^>]+src="https?:/);assert.equal(JSON.parse(readFileSync(join(out,'manifest.json'))).mode,'components');assert.equal(spawnSync(process.execPath,[entry,'--components','--out-dir',out]).status,2);const bad=join(folder,'bad.json');writeFileSync(bad,JSON.stringify({kind:'components',data:{injected:'no'}}));assert.equal(spawnSync(process.execPath,[entry,'--document','--input',bad]).status,2)}finally{rmSync(folder,{recursive:true,force:true})}})
test('reading sections preserve explanation, cases and evidence order without hiding legacy content',()=>{
 const data={mode:'site',title:'Reading',pages:[{title:'Cases',sections:[{body:'First explain the cases.',bullets:['Case A','Case B']},{body:'Then show the evidence.'}]}]}
 fixture(data,(r,out)=>{assert.equal(r.status,0,r.stderr);const body=readFileSync(join(out,'index.html'),'utf8').split('<script')[0];assert.ok(body.indexOf('First explain')<body.indexOf('Case A'));assert.ok(body.indexOf('Case B')<body.indexOf('Then show'))})
 for(const page of [{...data.pages[0],body:'Duplicate legacy text'},{title:'x',sections:[]},{title:'x',sections:[{}]},{title:'x',sections:[{unknown:'hidden'}]},{title:'x',sections:[{blocks:[{type:'unknown',title:'invalid'}]}]}])fixture({...data,pages:[page]},(r,out)=>{assert.equal(r.status,2);assert.equal(existsSync(out),false)})
 fixture({...data,language:'en',translations:{'zh-CN':{...data,pages:[{title:'不一致',sections:[{body:'只有一组'}]}]}}},(r,out)=>{assert.equal(r.status,2);assert.equal(existsSync(out),false)})
})
test('custom React scenes use the same protected offline export and carry complete notices',()=>{
 const folder=mkdtempSync(join(tmpdir(),'507-scene-test-'))
 try{
  const input=join(folder,'scene.jsx'),out=join(folder,'out')
  writeFileSync(input,`import React from 'react';import {Button} from ${JSON.stringify(join(runtime,'ui/index.tsx'))};import ${JSON.stringify(join(runtime,'ui/ui.css'))};if(typeof window==='undefined')throw new Error('Scene must not execute in Node');export default function Scene(){return <Button>Scene action</Button>}`)
  const args=[entry,'--scene',input,'--title','<script>Title</script>','--out-dir',out]
  const r=spawnSync(process.execPath,args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr)
  const html=readFileSync(join(out,'index.html'),'utf8');assert.match(html,/&lt;script&gt;Title/);assert.match(html,/connect-src 'none'/);assert.doesNotMatch(html,/<script>Title|@import/)
  const licenses=JSON.parse(html.match(/id="third-party-licenses" type="application\/json">([\s\S]*?)<\/script>/)[1]);for(const name of ['react','react-dom','shadcn/ui adaptations'])assert.ok(licenses.some(x=>x.name===name&&/Permission/.test(x.text)))
  const manifest=readFileSync(join(out,'manifest.json'));assert.equal(JSON.parse(manifest).sourceGraphSha256,JSON.parse(readFileSync(join(out,'scene.json'))).sourceGraphSha256)
  assert.equal(spawnSync(process.execPath,args).status,2);assert.deepEqual(readFileSync(join(out,'manifest.json')),manifest)
  writeFileSync(input,"import 'https://example.com/remote.js';export default function Scene(){return null}")
  const other=join(folder,'external');assert.equal(spawnSync(process.execPath,[entry,'--scene',input,'--title','External','--out-dir',other]).status,2);assert.equal(existsSync(other),false)
 }finally{rmSync(folder,{recursive:true,force:true})}
})
test('a scene using the shared Stage carries its original full MIT notice',()=>{
 const folder=mkdtempSync(join(tmpdir(),'507-kit-license-'))
 try{
  const input=join(folder,'scene.jsx'),out=join(folder,'out')
  writeFileSync(input,`import React from 'react';import {Stage} from ${JSON.stringify(join(runtime,'kit/stage.tsx'))};export default function Scene(){return <Stage width={640} height={320}>{()=> <div>Shared stage</div>}</Stage>}`)
  const r=spawnSync(process.execPath,[entry,'--scene',input,'--title','Shared stage','--out-dir',out],{encoding:'utf8'});assert.equal(r.status,0,r.stderr)
  const html=readFileSync(join(out,'index.html'),'utf8'),licenses=JSON.parse(html.match(/id="third-party-licenses" type="application\/json">([\s\S]*?)<\/script>/)[1])
  const original=licenses.find(x=>x.name==='Stageshow shared adaptations');assert.ok(original)
  assert.equal(original.text,readFileSync(join(runtime,'LICENSE'),'utf8'));assert.match(original.text,/Benji Taylor/);assert.match(original.text,/Permission is hereby granted/)
  const source=JSON.parse(readFileSync(join(out,'scene.json')));assert.ok(source.sources.some(x=>x.path.endsWith('kit/stage.tsx')))
 }finally{rmSync(folder,{recursive:true,force:true})}
})

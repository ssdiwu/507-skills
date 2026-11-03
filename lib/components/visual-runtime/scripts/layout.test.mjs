import test from 'node:test'
import assert from 'node:assert/strict'
import {spawnSync} from 'node:child_process'
import {mkdtempSync,writeFileSync,readFileSync,rmSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {pathToFileURL,fileURLToPath} from 'node:url'
const entry=fileURLToPath(new URL('./layout.mjs',import.meta.url))
function fixture(body,check){
 const folder=mkdtempSync(join(tmpdir(),'507-layout-test-'))
 try{
  const page=join(folder,'page.html');writeFileSync(page,'<!doctype html><meta charset="utf-8"><style>body{margin:0}button{box-sizing:border-box;font:16px/24px system-ui}</style>'+body)
  const run=(scroll,label)=>{
   const report=join(folder,label+'.json'),args=[entry,pathToFileURL(page).href,'--select','.probe','--strict','--delay','0','--report',report]
   if(scroll)args.push('--scroll')
   const result=spawnSync(process.execPath,args,{encoding:'utf8',timeout:30000})
   assert.equal(result.error,undefined,result.error?.message)
   let data;try{data=JSON.parse(readFileSync(report,'utf8'))}catch{assert.fail('Layout report missing; check Chrome/dependencies: '+result.stderr)}
   return {...result,data}
  }
  check(run)
 }finally{rmSync(folder,{recursive:true,force:true})}
}
test('scroll mode checks a normal offscreen region and retains manual review',()=>fixture('<div style="height:2400px"></div><button class="probe" style="height:40px;padding:4px">Valid control</button>',run=>{
 const r=run(true,'valid');assert.equal(r.status,0,r.stderr);assert.equal(r.data.status,'no-issues-detected');assert.equal(r.data.scopes[0].checked.controls,1);assert.equal(r.data.manualReviewRequired,true)
}))
test('scroll mode finds a later clipped control while snapshot mode retains its scope',()=>fixture('<button class="probe" style="height:40px;padding:4px">Valid first control</button><div style="height:2400px"></div><button class="probe" style="height:20px;padding:10px">Clipped later control</button>',run=>{
 const snapshot=run(false,'snapshot');assert.equal(snapshot.status,0,snapshot.stderr)
 const moved=run(true,'moved');assert.equal(moved.status,1,moved.stderr);assert.equal(moved.data.scopes.length,2);assert.equal(moved.data.scopes[0].findings.length,0);assert.ok(moved.data.scopes[1].findings.some(x=>x.rule==='control-block-fit'))
}))
test('an oversized selected region remains inconclusive rather than passing',()=>fixture('<button class="probe" style="height:1500px;padding:10px">Tall region</button>',run=>{
 const r=run(true,'oversized');assert.equal(r.status,2,r.stderr);assert.equal(r.data.status,'inconclusive');assert.ok(r.data.scopes[0].deferred.some(x=>x.includes('beyond the viewport')))
}))

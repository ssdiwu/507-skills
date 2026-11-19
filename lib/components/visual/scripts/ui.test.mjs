import test from 'node:test'
import assert from 'node:assert/strict'
import {spawnSync} from 'node:child_process'
import {mkdtempSync,rmSync,writeFileSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {fileURLToPath,pathToFileURL} from 'node:url'
import {launch} from './browser.mjs'

const runtime=fileURLToPath(new URL('..',import.meta.url))
const exporter=join(runtime,'scripts/render-artifact.mjs')
async function offlinePage(prepare,check){
 const folder=mkdtempSync(join(tmpdir(),'507-visual-views-'));let browser
 try{
  const html=prepare(folder)
  browser=await launch();const page=await browser.newPage({viewport:{width:1280,height:900}})
  const errors=[];page.on('pageerror',error=>errors.push(error.message))
  await page.goto(pathToFileURL(html).href);await page.locator('[data-react-ready]').waitFor()
  await check(page);assert.deepEqual(errors,[])
 }finally{await browser?.close();rmSync(folder,{recursive:true,force:true})}
}
function artifact(folder,data){
 const input=join(folder,'artifact.json'),out=join(folder,'artifact')
 writeFileSync(input,JSON.stringify(data))
 const result=spawnSync(process.execPath,[exporter,'--input',input,'--out-dir',out],{encoding:'utf8'})
 assert.equal(result.status,0,result.stderr)
 return join(out,'index.html')
}
function scene(folder,entry,title){
 const out=join(folder,'scene')
 const result=spawnSync(process.execPath,[exporter,'--scene',join(runtime,entry),'--title',title,'--out-dir',out],{encoding:'utf8'})
 assert.equal(result.status,0,result.stderr)
 return join(out,'index.html')
}
function projection(folder,{script,record,contract}){
 const entry=fileURLToPath(new URL(`../../tools/projections/${script}.py`,import.meta.url))
 const input=join(folder,'record.json'),out=join(folder,'projection')
 writeFileSync(input,JSON.stringify(record))
 const args=[entry,'--record',input]
 if(contract){
  const settings=join(folder,'contract.json')
  writeFileSync(settings,JSON.stringify(contract))
  args.push('--contract',settings,'--out-root',out)
 }else args.push('--out-dir',out)
 const result=spawnSync('python3',['-B',...args],{encoding:'utf8'})
 assert.equal(result.status,0,result.stderr)
 return JSON.parse(result.stdout).page
}
test('record browser native controls preserve search, selection, empty recovery and failure recovery',()=>offlinePage(
 folder=>scene(folder,'scenes/examples/record-browser/index.tsx','记录浏览示例'),
 async page=>{
  const search=page.getByRole('searchbox',{name:'搜索记录'})
  await page.getByRole('button',{name:/会议预约/}).click()
  await page.getByRole('heading',{name:'会议预约'}).waitFor()
  await search.fill('没有匹配')
  await page.getByRole('status').getByText('没有匹配的记录',{exact:true}).waitFor()
  await page.getByRole('button',{name:'清除筛选'}).click()
  assert.equal(await page.getByRole('navigation',{name:'申请列表'}).getByRole('listitem').count(),2)
  await page.getByRole('heading',{name:'会议预约'}).waitFor()
  await search.fill('会议')
  await page.getByRole('button',{name:'模拟加载失败'}).click()
  await page.getByRole('alert').getByText('现有筛选条件已保留。',{exact:false}).waitFor()
  assert.equal(await search.inputValue(),'会议')
  await page.getByRole('button',{name:'重试'}).click()
  await page.getByRole('button',{name:/会议预约/}).waitFor()
  await page.getByRole('heading',{name:'会议预约'}).waitFor()
  await page.setViewportSize({width:390,height:844})
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
  await page.keyboard.press('Tab')
  assert.equal(await page.evaluate(()=>document.activeElement?.tagName), 'BUTTON')
 }))
test('artifact native language and queue controls keep values and update output',()=>offlinePage(folder=>artifact(folder,{
 mode:'site',language:'en',title:'Reading',pages:[{title:'Wait',blocks:[{type:'queue',id:'wait',title:'Wait estimate',model:'serial',taskForms:[1,2],minutesPerForm:1.5,remainingMinutes:1.5}]}],
 translations:{'zh-CN':{mode:'site',title:'阅读',pages:[{title:'等待',blocks:[{type:'queue',id:'wait',title:'等待估算',model:'serial',taskForms:[1,2],minutesPerForm:1.5,remainingMinutes:1.5}]}]}}
}),async page=>{
 const waiting=page.locator('[data-queue-state=waiting]')
 assert.equal(await waiting.getAttribute('aria-pressed'),'true')
 await page.locator('[data-task-count]').fill('3')
 await page.locator('[data-forms]').first().fill('4')
 const values=await page.locator('.queue-example input').evaluateAll(inputs=>inputs.map(input=>input.value))
 const estimate=await page.locator('[data-queue-title]').innerText()
 await page.getByRole('button',{name:'Processing'}).press('Enter')
 await waiting.press('Enter')
 assert.deepEqual(await page.locator('.queue-example input').evaluateAll(inputs=>inputs.map(input=>input.value)),values)
 assert.equal(await page.locator('[data-queue-title]').innerText(),estimate)
 await page.getByRole('button',{name:'中文'}).click()
 await page.getByRole('heading',{name:'阅读'}).waitFor()
 await page.setViewportSize({width:390,height:844})
 await page.emulateMedia({reducedMotion:'reduce'})
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
}))
test('task view keeps execution conditions and status visible while disclosing source guidance',()=>offlinePage(folder=>projection(folder,{
 script:'task_view',
 record:[
  {id:'approval',title:'负责人确认',status:'waiting',owner:'负责人',dependsOn:[],acceptance:'待确认'},
  {id:'delivery',title:'准备交付',status:'draft',owner:'制作人',dependsOn:['approval'],notes:'负责人签字后交付'}
 ],
 contract:{
  title:'交付工作',mode:'continuing',modeNote:'负责人签字后交付',
  source:{format:'json',tasksPath:[]},
  fields:{id:'id',title:'title',status:'status',owner:'owner',dependsOn:'dependsOn',acceptance:'acceptance',notes:'notes'},
  columns:['title','status','owner','acceptance'],
  statusMap:{waiting:{label:'等待确认',dependencySatisfied:false}}
 }
}),async page=>{
 await page.setViewportSize({width:390,height:844})
 await page.getByRole('banner').getByText('负责人签字后交付',{exact:true}).waitFor()
 const table=page.getByRole('table')
 const waitingCell=table.getByRole('cell',{name:'等待确认',exact:true})
 const waitingBounds=await waitingCell.boundingBox()
 assert.ok(waitingBounds&&waitingBounds.y+waitingBounds.height<=844)
 await table.getByRole('cell',{name:'待确认',exact:true}).waitFor()
 const source=page.locator('footer details')
 assert.equal(await source.getAttribute('open'),null)
 await source.getByText('持续工作：沿用现有记录',{exact:true}).waitFor({state:'hidden'})
 await page.getByRole('combobox',{name:'承担者'}).selectOption('制作人')
 assert.equal(await page.getByRole('status').innerText(),'显示 1 / 2 项')
 await page.locator('#graph').getByText('依赖状态尚未明确满足；不是自动冻结指令',{exact:true}).waitFor()
 await table.getByRole('button',{name:'准备交付'}).click()
 const detail=page.getByRole('region',{name:'选定工作详情'})
 await detail.getByRole('heading',{name:'准备交付'}).waitFor()
 assert.equal(await detail.evaluate(element=>element===document.activeElement),true)
 await detail.getByRole('button',{name:'负责人确认'}).press('Enter')
 await detail.getByRole('heading',{name:'负责人确认'}).waitFor()
 await detail.getByRole('button',{name:'准备交付'}).click()
 await detail.getByRole('heading',{name:'准备交付'}).waitFor()
 await source.locator('summary').press('Enter')
 await source.getByText('持续工作：沿用现有记录',{exact:true}).waitFor()
 await source.getByText(/SHA-256/).waitFor()
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
}))
test('product map retains node filtering, source-backed details and history navigation',()=>offlinePage(folder=>{
 const emptyEvidence={design:[],implementation:[],runtime:[]}
 const failed={state:'failed',sourceIds:['run'],scope:'普通成员',note:'打不开详情',action:'打开详情',role:'成员',input:'示例资料',environment:'测试环境',version:'v1',observed:'仍在列表'}
 const node=(id,label,kind,evidence=emptyEvidence)=>({id,label,kind,purpose:'查看资料',conditions:['已登录'],outcomes:['显示资料'],evidence})
 const edge=(id,from,to,kind)=>({id,from,to,kind,condition:'从当前资料进入',evidence:emptyEvidence})
 return projection(folder,{
  script:'product_map',
  record:{
   schema:1,title:'资料交互地图',
   scope:{goal:'核对详情入口',boundary:'示例工作台',version:'v1',conditions:['使用普通成员账号'],limitations:['移动端尚未观察'],coverage:'partial'},
   sources:[{id:'run',kind:'runtime',label:'离线观察',locator:'run.log:12'}],
   nodes:[node('list','资料列表','page'),node('open','打开详情','button',{...emptyEvidence,runtime:[failed]}),node('detail','资料详情','drawer')],
   edges:[edge('list-open','list','open','contains'),edge('list-detail','list','detail','contains'),edge('open-detail','open','detail','open')],
   paths:[{id:'open-flow',label:'查看资料路径',edgeIds:['open-detail'],conditions:['已登录'],evidence:{...emptyEvidence,runtime:[failed]}}]
  }
 })
},async page=>{
 const globalViews=page.getByRole('region',{name:'全局视图'})
 const sections=globalViews.locator(':scope > details')
 assert.equal(await sections.count(),3)
 assert.equal(await globalViews.locator(':scope > details[open]').count(),0)
 await page.getByRole('banner').getByText('限制：移动端尚未观察',{exact:true}).waitFor()
 await page.getByRole('combobox',{name:'证据维度'}).selectOption('runtime')
 await page.getByRole('combobox',{name:'状态',exact:true}).selectOption('failed')
 assert.equal(await page.getByRole('status').innerText(),'显示 1 / 3 个交互点')
 const points=page.locator('#points')
 await points.getByRole('button',{name:/打开详情/}).press('Enter')
 const detail=page.getByRole('region',{name:'交互点详情'})
 await detail.getByText('失败',{exact:true}).waitFor()
 await detail.getByText('打不开详情',{exact:true}).waitFor()
 const missingEvidence=detail.locator(':scope > p').filter({hasText:'未提供证据；不判断该维度已通过或已缺失。'})
 assert.equal(await missingEvidence.count(),2)
 await missingEvidence.first().waitFor()
 assert.equal(await detail.evaluate(element=>element===document.activeElement),true)
 await detail.getByText('打开 · 打开详情 → 资料详情',{exact:true}).press('Enter')
 await detail.getByRole('button',{name:'资料详情',exact:true}).click()
 await detail.getByRole('heading',{name:'资料详情',exact:true}).waitFor()
 assert.equal(new URL(page.url()).hash,'#node=detail')
 await page.goBack()
 await detail.getByRole('heading',{name:'打开详情',exact:true}).waitFor()
 await page.goForward()
 await detail.getByRole('heading',{name:'资料详情',exact:true}).waitFor()
 await page.reload()
 await detail.getByRole('heading',{name:'资料详情',exact:true}).waitFor()
 assert.equal(await globalViews.locator(':scope > details[open]').count(),0)
 await globalViews.getByText('包含树',{exact:true}).press('Enter')
 await globalViews.locator('#tree').getByRole('button',{name:'资料列表',exact:true}).click()
 await detail.getByRole('heading',{name:'资料列表',exact:true}).waitFor()
 await globalViews.getByText('全部关系',{exact:true}).press('Enter')
 await globalViews.getByRole('table').getByRole('row',{name:/打开详情 打开 资料详情/}).getByRole('button',{name:'打开详情',exact:true}).click()
 await detail.getByRole('heading',{name:'打开详情',exact:true}).waitFor()
 await globalViews.getByText('登记路径与独立路径证据',{exact:true}).press('Enter')
 await globalViews.getByText('查看资料路径',{exact:true}).press('Enter')
 await globalViews.locator('#paths').getByText('失败',{exact:true}).waitFor()
 await page.setViewportSize({width:390,height:844})
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
}))

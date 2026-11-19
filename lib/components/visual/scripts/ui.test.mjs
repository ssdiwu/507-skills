import test from 'node:test'
import assert from 'node:assert/strict'
import {spawnSync} from 'node:child_process'
import {mkdtempSync,rmSync,writeFileSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {fileURLToPath,pathToFileURL} from 'node:url'
import {launch} from './browser.mjs'

async function offlinePage(prepare,check){
 const folder=mkdtempSync(join(tmpdir(),'507-ui-browser-'));let browser
 try{
  const html=prepare(folder)
  browser=await launch();const page=await browser.newPage({viewport:{width:1280,height:900}})
  const errors=[];page.on('pageerror',error=>errors.push(error.message))
  await page.goto(pathToFileURL(html).href);await page.locator('[data-react-ready]').waitFor()
  await check(page);assert.deepEqual(errors,[])
 }finally{await browser?.close();rmSync(folder,{recursive:true,force:true})}
}
function catalogue(check,mode='--components'){
 return offlinePage(folder=>{
  const out=join(folder,'catalogue'),entry=fileURLToPath(new URL('./render-artifact.mjs',import.meta.url))
  const result=spawnSync(process.execPath,[entry,mode,'--out-dir',out],{encoding:'utf8'})
  assert.equal(result.status,0,result.stderr)
  return join(out,'index.html')
 },check)
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
test('offline edit validates input, traps focus and restores the trigger after dismissal',()=>catalogue(async page=>{
 await page.getByRole('button',{name:'创建资料',exact:true}).click()
 const dialog=page.getByRole('dialog',{name:'创建一份资料'})
 assert.equal(await dialog.evaluate(element=>document.getElementById(element.getAttribute('aria-describedby'))?.textContent),'填写资料名称后提交。')
 await dialog.getByRole('button',{name:'创建示例',exact:true}).click()
 assert.equal(await dialog.getByRole('textbox',{name:'资料名称'}).getAttribute('aria-invalid'),'true')
 await dialog.getByRole('textbox',{name:'资料名称'}).fill('测试资料')
 await dialog.getByRole('button',{name:'创建示例',exact:true}).click()
 assert.match(await dialog.getByRole('status').innerText(),/测试资料/)
 await dialog.getByRole('button',{name:'关闭对话框',exact:true}).focus();await page.keyboard.press('Tab')
 assert.equal(await dialog.getByRole('textbox',{name:'资料名称'}).evaluate(el=>document.activeElement===el),true)
 await page.keyboard.press('Escape');await dialog.waitFor({state:'detached'})
 await page.getByRole('button',{name:'创建资料',exact:true}).locator(':scope:focus').waitFor()
}))
test('keyboard selection, empty recovery, narrow layout and reduced motion survive offline export',()=>catalogue(async page=>{
 const exampleScope=page.getByText('本页使用虚构资料。操作只改变本页状态，刷新后重置，不写入文件或外部系统，也不发送通知。',{exact:true})
 assert.equal(await exampleScope.count(),1)
 const keyboardHelp=page.getByRole('button',{name:'如何使用键盘？',exact:true})
 await keyboardHelp.press('Enter')
 assert.equal(await keyboardHelp.getAttribute('aria-expanded'),'true')
 await page.getByText('Tab 移动焦点',{exact:false}).waitFor()
 await page.getByRole('button',{name:'列表',exact:true}).click();await page.keyboard.press('End');await page.keyboard.press('Enter')
 await page.getByRole('button',{name:'紧凑列表',exact:true}).waitFor()
 await page.getByRole('textbox',{name:'搜索资料'}).fill('不匹配')
 await page.getByRole('button',{name:'清除搜索',exact:true}).click()
 assert.equal(await page.locator('.ui-record').count(),3)
 await page.getByRole('button',{name:'查看会议跟进资料',exact:true}).click()
 await page.getByRole('status').filter({hasText:'已选择：会议跟进资料'}).waitFor()
 await page.getByRole('tab',{name:'工作列表',exact:true}).focus();await page.keyboard.press('ArrowRight')
 const formPanel=page.getByRole('tabpanel',{name:'表单与设置',exact:true})
 await formPanel.waitFor()
 await exampleScope.waitFor()
 const reminder=formPanel.getByRole('switch',{name:'开启更新提醒',exact:true})
 await reminder.press('Space')
 assert.equal(await reminder.getAttribute('aria-checked'),'false')
 const validate=formPanel.getByRole('button',{name:'验证示例',exact:true})
 await validate.click()
 const nameInput=formPanel.getByRole('textbox',{name:'资料名称',exact:true})
 assert.equal(await nameInput.getAttribute('aria-invalid'),'true')
 await nameInput.fill('测试资料')
 await validate.click()
 assert.equal(await formPanel.getByRole('status').innerText(),'输入已通过示例检查')
 await page.setViewportSize({width:390,height:844});await page.emulateMedia({reducedMotion:'reduce'})
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
 await page.getByRole('tab',{name:'状态与反馈',exact:true}).click()
 assert.equal(await page.locator('.ui-skeleton>span:not(.ui-sr-only)').first().evaluate(el=>getComputedStyle(el).animationName),'none')
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
 assert.equal(await page.getByRole('progressbar',{name:'示例文件准备进度'}).getAttribute('value'),'64')
}))
test('the reading consumer retains a selected state on hover and preserves edited queue conditions',()=>catalogue(async page=>{
 const waiting=page.locator('[data-queue-state=waiting]')
 const settledBackground=button=>button.evaluate(async element=>{
  element.getBoundingClientRect()
  await Promise.all(element.getAnimations().map(animation=>animation.finished))
  return getComputedStyle(element).backgroundColor
 })
 assert.equal(await waiting.getAttribute('aria-pressed'),'true')
 const before=await settledBackground(waiting)
 await waiting.hover()
 assert.equal(await settledBackground(waiting),before)
 await page.locator('[data-task-count]').fill('3');await page.locator('[data-forms]').first().fill('4')
 const values=await page.locator('.queue-example input').evaluateAll(inputs=>inputs.map(el=>el.value))
 const estimate=await page.locator('[data-queue-title]').innerText()
 await page.locator('[data-queue-state=processing]').click();await waiting.click()
 assert.deepEqual(await page.locator('.queue-example input').evaluateAll(inputs=>inputs.map(el=>el.value)),values)
 assert.equal(await page.locator('[data-queue-title]').innerText(),estimate)
} ,'--example'))

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

test('product map displays local evidence first and preserves navigation across global disclosures',()=>offlinePage(folder=>{
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

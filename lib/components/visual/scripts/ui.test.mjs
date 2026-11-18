import test from 'node:test'
import assert from 'node:assert/strict'
import {spawnSync} from 'node:child_process'
import {mkdtempSync,rmSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {fileURLToPath,pathToFileURL} from 'node:url'
import {launch} from './browser.mjs'

async function catalogue(check,mode='--components'){
 const folder=mkdtempSync(join(tmpdir(),'507-ui-browser-'));let browser
 try{
  const out=join(folder,'catalogue'),entry=fileURLToPath(new URL('./render-artifact.mjs',import.meta.url))
  const result=spawnSync(process.execPath,[entry,mode,'--out-dir',out],{encoding:'utf8'})
  assert.equal(result.status,0,result.stderr)
  browser=await launch();const page=await browser.newPage({viewport:{width:1280,height:900}})
  const errors=[];page.on('pageerror',error=>errors.push(error.message))
  await page.goto(pathToFileURL(join(out,'index.html')).href);await page.locator('[data-react-ready]').waitFor()
  await check(page);assert.deepEqual(errors,[])
 }finally{await browser?.close();rmSync(folder,{recursive:true,force:true})}
}
test('offline edit validates input, traps focus and restores the trigger after dismissal',()=>catalogue(async page=>{
 await page.getByRole('button',{name:'创建资料',exact:true}).click()
 const dialog=page.getByRole('dialog',{name:'创建一份资料'})
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
 await page.getByRole('button',{name:'列表',exact:true}).click();await page.keyboard.press('End');await page.keyboard.press('Enter')
 await page.getByRole('button',{name:'紧凑列表',exact:true}).waitFor()
 await page.getByRole('textbox',{name:'搜索资料'}).fill('不匹配')
 await page.getByRole('button',{name:'清除搜索',exact:true}).click()
 assert.equal(await page.locator('.ui-record').count(),3)
 await page.getByRole('tab',{name:'工作列表',exact:true}).focus();await page.keyboard.press('ArrowRight')
 await page.getByRole('tabpanel',{name:'表单与设置',exact:true}).waitFor()
 await page.setViewportSize({width:390,height:844});await page.emulateMedia({reducedMotion:'reduce'})
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
 await page.getByRole('tab',{name:'状态与反馈',exact:true}).click()
 assert.equal(await page.locator('.ui-skeleton>span:not(.ui-sr-only)').first().evaluate(el=>getComputedStyle(el).animationName),'none')
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)
 assert.equal(await page.getByRole('progressbar',{name:'示例文件准备进度'}).getAttribute('value'),'64')
}))
test('the reading consumer retains a selected state on hover and preserves edited queue conditions',()=>catalogue(async page=>{
 const waiting=page.locator('[data-queue-state=waiting]')
 const before=await waiting.evaluate(el=>getComputedStyle(el).backgroundColor)
 await waiting.hover()
 assert.equal(await waiting.evaluate(el=>getComputedStyle(el).backgroundColor),before)
 await page.locator('[data-task-count]').fill('3');await page.locator('[data-forms]').first().fill('4')
 const values=await page.locator('.queue-example input').evaluateAll(inputs=>inputs.map(el=>el.value))
 const estimate=await page.locator('[data-queue-title]').innerText()
 await page.locator('[data-queue-state=processing]').click();await waiting.click()
 assert.deepEqual(await page.locator('.queue-example input').evaluateAll(inputs=>inputs.map(el=>el.value)),values)
 assert.equal(await page.locator('[data-queue-title]').innerText(),estimate)
} ,'--example'))

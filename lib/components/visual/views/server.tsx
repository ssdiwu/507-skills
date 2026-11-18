import React from 'react'
import {Buffer} from 'node:buffer'
import {renderToString,renderToStaticMarkup} from 'react-dom/server'
import {App} from './App'
import {DocumentModel,validateDocument} from './model'
type License={name:string;text:string}
const inline=(value:unknown)=>JSON.stringify(value).replace(/[<>&]/g,char=>String.fromCharCode(92)+'u'+char.charCodeAt(0).toString(16).padStart(4,'0'))
function shell(title:string,language:string,markup:string,model:unknown,css:string,script:string,licenses:License[]){
 const policy="default-src 'none'; style-src 'unsafe-inline'; script-src data:; connect-src 'none'; img-src 'none'; base-uri 'none'; form-action 'none'"
 const code=Buffer.from(script).toString('base64'),safeCSS=css.replace(/<\/style/gi,'<\\/style')
 return `<!doctype html><html lang="${language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${policy}">${renderToStaticMarkup(<title>{title}</title>)}<style>${safeCSS}</style></head><body><div id="app">${markup}</div><script id="visual-model" type="application/json">${inline(model)}</script><script id="third-party-licenses" type="application/json">${inline(licenses)}</script><script type="module" src="data:text/javascript;base64,${code}"></script></body></html>`
}
// Scene source is compiled for the browser; it is never imported by Node SSR.
export function renderScene(title:string,source:unknown,css:string,script:string,licenses:License[]){return shell(title,'zh-CN','<noscript>此交互场景需要允许本地脚本。</noscript>',source,css,script,licenses)}
export function render(model:DocumentModel,css:string,script:string,licenses:{name:string;text:string}[]=[]){
 validateDocument(model)
 const data=model.data as any,title=model.kind==='artifact'?data.title:model.kind==='task-view'?data.contract.title:model.kind==='product-map'?data.record.title:model.kind==='components'?'共有基础组件':'当前任务视图'
 return shell(title,model.kind==='artifact'?(data.language??'zh-CN'):'zh-CN',renderToString(<App model={model}/>),model,css,script,licenses)
}

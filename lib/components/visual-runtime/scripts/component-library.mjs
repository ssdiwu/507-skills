#!/usr/bin/env node
/** Local discovery and source-derived API/scene checks. Never executes scene code. */
let ts, buildSync
try { ts = (await import('typescript')).default } catch { /* Report through the public JSON error path. */ }
try { ({buildSync} = await import('esbuild')) } catch { /* Report through the public JSON error path. */ }
import {readFileSync,existsSync,statSync,realpathSync} from 'node:fs'
import {resolve,dirname,join,relative,isAbsolute} from 'node:path'
import {fileURLToPath} from 'node:url'
import {createHash} from 'node:crypto'
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..')
const hash=x=>createHash('sha256').update(x).digest('hex')
const print=x=>console.log(JSON.stringify(x,null,2))
function local(path){const full=resolve(root,path);if(!path||isAbsolute(path)||relative(root,full).startsWith('..')||!existsSync(full))throw new Error('Missing or invalid catalogue path: '+path);return full}
function diagnostic(d){const pos=d.file&&d.start!==undefined?d.file.getLineAndCharacterOfPosition(d.start):null;return {code:d.code,file:d.file?.fileName,line:pos?pos.line+1:undefined,column:pos?pos.character+1:undefined,message:ts.flattenDiagnosticMessageText(d.messageText,' ')}}
const canonical = path => existsSync(path) ? realpathSync(path) : resolve(path)
const dependency = path => path.split(/[\\/]/).includes('node_modules')
export function sceneBuildOptions(entry, project) {
 return {absWorkingDir:root,stdin:{contents:`import React from 'react';import {createRoot} from 'react-dom/client';import Scene from ${JSON.stringify(resolve(entry))};createRoot(document.getElementById('app')).render(<Scene/>);document.documentElement.dataset.reactReady='true';`,loader:'tsx',resolveDir:root},alias:{react:join(root,'node_modules/react'),'react-dom':join(root,'node_modules/react-dom')},nodePaths:[join(root,'node_modules')],...(project?{tsconfig:resolve(project)}:{}),conditions:['browser','module'],bundle:true,platform:'browser',format:'iife',write:false,metafile:true,minify:true,charset:'utf8',target:'es2020',logLevel:'silent',jsx:'automatic',define:{'process.env.NODE_ENV':'"production"'}}
}
function bundlePaths(metafile) { return Object.keys(metafile.inputs).filter(p=>p!=='<stdin>').map(p=>canonical(resolve(root,p))).sort() }
function programFor(entries,project,virtual={},graph=new Map(),configFiles=new Set()){
 if(!ts)throw new Error('Shared TypeScript dependency missing: run npm ci --ignore-scripts in the shared visual-runtime directory')
 let inherited={}
 const readConfig=path=>{configFiles.add(resolve(path));return ts.sys.readFile(path)}
 if(project){const result=ts.readConfigFile(resolve(project),readConfig);if(result.error)throw new Error(ts.flattenDiagnosticMessageText(result.error.messageText,' '));const parsed=ts.parseJsonConfigFileContent(result.config,{...ts.sys,readFile:readConfig},dirname(resolve(project)));const errors=parsed.errors.filter(x=>x.code!==18003);if(errors.length)throw new Error(errors.map(x=>ts.flattenDiagnosticMessageText(x.messageText,' ')).join('\n'));inherited=parsed.options}
 const options={...inherited,target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext,moduleResolution:ts.ModuleResolutionKind.Bundler,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true,allowSyntheticDefaultImports:true,allowImportingTsExtensions:true,resolveJsonModule:true,allowJs:true,checkJs:true,strict:true,noCheck:false,customConditions:['browser','module'],noEmit:true,skipLibCheck:true,incremental:false,composite:false,types:[],typeRoots:[join(root,'node_modules/@types')],noUncheckedSideEffectImports:true}
 const ambient=join(root,'__507_readonly_css__.d.ts')
 virtual={...virtual,[ambient]:'declare module "*.css";'}
 const host=ts.createCompilerHost(options),read=host.readFile.bind(host),get=host.getSourceFile.bind(host),exists=host.fileExists.bind(host)
 host.fileExists=p=>Object.hasOwn(virtual,p)||exists(p)
 host.readFile=p=>virtual[p]??read(p)
 host.getSourceFile=(p,v,e,n)=>Object.hasOwn(virtual,p)?ts.createSourceFile(p,virtual[p],v,true):get(p,v,e,n)
 host.resolveModuleNames=(names,containing)=>names.map(name=>{
  const shared=/^(react|react-dom)(\/|$)/.test(name)
  let found=ts.resolveModuleName(name,shared?join(root,'__resolver__.tsx'):containing,shared?{...options,paths:undefined,baseUrl:undefined}:options,host).resolvedModule
  if(!found&&!name.startsWith('.')&&!isAbsolute(name))found=ts.resolveModuleName(name,join(root,'__resolver__.tsx'),{...options,paths:undefined,baseUrl:undefined},host).resolvedModule
  const target=graph.get(canonical(containing))?.get(name)
  // Follow the browser bundle for source modules; installed JS packages retain their declared API.
  if(!shared&&target&&(/\.[cm]?tsx?$/.test(target)||(/\.[cm]?jsx?$/.test(target)&&!dependency(target)))){
   if(found&&canonical(found.resolvedFileName)===target)return found
   return {resolvedFileName:target,extension:target.endsWith('.tsx')?ts.Extension.Tsx:target.endsWith('.jsx')?ts.Extension.Jsx:target.endsWith('.js')?ts.Extension.Js:ts.Extension.Ts,isExternalLibraryImport:false}
  }
  return found
 })
 return ts.createProgram([...entries,ambient],options,host)
}
export function checkScene(entry,{project}={}){
 const file=resolve(entry)
 if(!existsSync(file)||!statSync(file).isFile()||! /\.[jt]sx?$/.test(file))throw new Error('Scene must be an existing JS/JSX/TS/TSX file')
 if(statSync(file).size>8*1024*1024)throw new Error('Input exceeds 8 MiB')
 if(!buildSync)throw new Error('Shared esbuild dependency missing: run npm ci --ignore-scripts in the shared visual-runtime directory')
 // Resolve in memory with the exact browser bundler settings, without executing scene code.
 const bundle=buildSync({...sceneBuildOptions(file,project),outfile:join(root,'__507_readonly_bundle__.js')})
 const paths=bundlePaths(bundle.metafile), graph=new Map()
 for(const [input,details] of Object.entries(bundle.metafile.inputs)){
  if(input==='<stdin>')continue
  graph.set(canonical(resolve(root,input)),new Map(details.imports.filter(i=>!i.external&&i.original).map(i=>[i.original,canonical(resolve(root,i.path))])))
 }
 const snapshots=new Map(paths.map(path=>[path,hash(readFileSync(path))]))
 const probe=join(root,'__507_readonly_scene__.tsx'),configFiles=new Set()
 const sourceEntries=paths.filter(path=>/\.[cm]?tsx?$/.test(path)||(/\.[cm]?jsx?$/.test(path)&&!dependency(path)))
 const p=programFor([...new Set([file,probe,...sourceEntries])],project,{[probe]:`import React from 'react'; import Scene from ${JSON.stringify(file)}; const scene: React.ComponentType = Scene;`},graph,configFiles)
 const errors=ts.getPreEmitDiagnostics(p).filter(d=>d.category===ts.DiagnosticCategory.Error).map(diagnostic)
 // Include declarations and all actual bundle inputs; directory substrings never exclude a user's source.
 for(const source of p.getSourceFiles())if(existsSync(source.fileName)&&!p.isSourceFileDefaultLibrary(source)){
  const path=canonical(source.fileName),bytes=readFileSync(path),digest=hash(bytes)
  if(bytes.toString('utf8').replace(/^\uFEFF/,'')!==source.text.replace(/^\uFEFF/,''))throw new Error('Scene source changed during type check: '+path)
  if(snapshots.has(path)&&snapshots.get(path)!==digest)throw new Error('Scene source changed during type check: '+path)
  snapshots.set(path,digest)
 }
 for(const path of configFiles)if(existsSync(path))snapshots.set(canonical(path),hash(readFileSync(path)))
 const result={status:errors.length?'INVALID':'CHECKED',entry:file,project:project?resolve(project):null,sourceSha256:hash(readFileSync(file)),bundleInputs:paths,checkedFiles:[...snapshots].map(([path,sha256])=>({path,sha256})),diagnostics:errors,limits:['Type checking follows the browser source graph; installed JavaScript packages are checked through their type declarations, not their runtime implementation.','Type checking does not execute the scene or verify visual quality, accessibility, business behaviour or user acceptance.','Explicit any, TypeScript suppression comments and dynamic data can bypass static guarantees.']}
 assertSceneUnchanged(result)
 return result
}
export function assertSceneUnchanged(result,metafile){
 for(const f of result.checkedFiles)if(!existsSync(f.path)||hash(readFileSync(f.path))!==f.sha256)throw new Error('Scene source changed after type check: '+f.path)
 if(metafile&&JSON.stringify(bundlePaths(metafile))!==JSON.stringify(result.bundleInputs))throw new Error('Scene dependency graph changed after type check')
}

function catalogue(){
 const data=JSON.parse(readFileSync(join(root,'catalog.json'),'utf8'))
 if(data.schema!==1||!Array.isArray(data.modules)||!Array.isArray(data.examples))throw new Error('Invalid component catalogue')
 const ids=new Set()
 for(const item of [...data.modules,...data.examples,...(data.diagrams??[])]){
  if(!item.id||ids.has(item.id))throw new Error('Duplicate/empty catalogue id');ids.add(item.id);local(item.source)
  for(const path of [...(item.styles??[]),...(item.guide?[item.guide]:[]),...(item.example?[item.example]:[])])local(path)
 }
 return data
}
function moduleSymbols(mod){const program=programFor([local(mod.source)]);const checker=program.getTypeChecker();const file=program.getSourceFile(local(mod.source));const symbol=checker.getSymbolAtLocation(file);return {checker,symbols:checker.getExportsOfModule(symbol)}}
function publicItem(item){return {...item,source:local(item.source),guide:item.guide?local(item.guide):undefined,styles:(item.styles??[]).map(local),example:item.example?local(item.example):undefined}}
export function listItems(){
 const data=catalogue(),items=[...data.examples.map(e=>publicItem({...e,id:'example:'+e.id})),...(data.diagrams??[]).map(e=>publicItem({...e,id:'diagram:'+e.id}))]
 for(const mod of data.modules){const {checker,symbols}=moduleSymbols(mod)
  for(const symbol of symbols){const actual=symbol.flags&ts.SymbolFlags.Alias?checker.getAliasedSymbol(symbol):symbol;if(!(actual.flags&ts.SymbolFlags.Value))continue
   const family=mod.families?.find(f=>f.exports.includes(symbol.name));items.push(publicItem({id:mod.id+':'+symbol.name,name:symbol.name,kind:mod.kind,note:mod.note,source:mod.source,guide:mod.guide,styles:mod.styles,example:mod.example,preview:mod.preview,tags:[...mod.tags,...(family?.tags??[])],states:family?.states??[]}))
  }
 }
 return items
}
export function searchItems(query){
 const q=query.toLocaleLowerCase().trim();if(!q)throw new Error('Search query must not be empty')
 return listItems().map(item=>{const terms=[item.id,item.name,...item.tags,...(item.states??[])].map(x=>x.toLocaleLowerCase());const matched=[...new Set(terms.filter(t=>q.includes(t)||t.includes(q)))];return {...item,matched,score:matched.reduce((n,t)=>n+(q===t?10:Math.min(t.length,6)),0)}}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id))
}
export function inspectItem(id){
 const data=catalogue(),item=listItems().find(x=>x.id===id);if(!item)return null
 if(id.startsWith('diagram:')){const model=JSON.parse(readFileSync(item.source,'utf8'));const page=model.pages.find(p=>p.blocks?.some(b=>b.type===id.split(':')[1]));if(!page)throw new Error('Diagram example missing');return {...item,modelSource:local('visuals/model.ts'),inputExample:{...model,pages:[{...page,blocks:page.blocks.filter(b=>b.type===id.split(':')[1])}]},invocation:{script:local('scripts/render-artifact.mjs'),args:['--input','<input.json>','--out-dir','<new directory>']}}}
 if(id.startsWith('example:'))return {...item,sourceText:readFileSync(item.source,'utf8'),api:item.api.map(api=>({id:api,command:['inspect',api]}))}
 const [modId,name]=id.split(':'),mod=data.modules.find(x=>x.id===modId),{checker,symbols}=moduleSymbols(mod),symbol=symbols.find(x=>x.name===name)
 const actual=symbol.flags&ts.SymbolFlags.Alias?checker.getAliasedSymbol(symbol):symbol
 const declaration=actual.valueDeclaration??actual.declarations?.[0]
 const type=checker.getTypeOfSymbolAtLocation(actual,declaration),calls=type.getCallSignatures()
 const props=calls[0]?.parameters[0],propType=props?checker.getTypeOfSymbolAtLocation(props,declaration):null
 const fields=propType?checker.getPropertiesOfType(propType).map(p=>({name:p.name,required:!(p.flags&ts.SymbolFlags.Optional),type:checker.typeToString(checker.getTypeOfSymbolAtLocation(p,p.valueDeclaration??declaration),undefined,ts.TypeFormatFlags.NoTruncation),local:p.declarations?.some(d=>!d.getSourceFile().fileName.includes('node_modules'))??false})):[]
 fields.sort((a,b)=>Number(b.required)-Number(a.required)||Number(b.local)-Number(a.local)||a.name.localeCompare(b.name))
 return {...item,apiSource:'current TypeScript source and installed declarations',signature:checker.typeToString(type,undefined,ts.TypeFormatFlags.NoTruncation),props:fields.slice(0,30),omittedProps:fields.slice(30).map(x=>x.name),declaration:{path:declaration.getSourceFile().fileName,text:declaration.getText()},usageNote:'Use check on the actual scene; the shortened property view is not an exhaustive API validator.'}
}
export function main(args){
 const [command,...rest]=args
 if(command==='list'&&rest.length===0)return {status:'LISTED',items:listItems()}
 if(command==='search'&&rest.length===1){const items=searchItems(rest[0]);return {status:items.length?'MATCHES':'NO_MATCH',matching:'local keyword matching, not semantic ranking',items}}
 if(command==='inspect'&&rest.length===1){const item=inspectItem(rest[0]);return item?{status:'FOUND',item}:{status:'NOT_FOUND',id:rest[0]}}
 if(command==='check'&&(rest.length===1||(rest.length===3&&rest[1]==='--project')))return checkScene(rest[0],{project:rest[2]})
 throw new Error('Usage: component-library.mjs list | search <text> | inspect <ui:Name|kit:Name|example:id|diagram:type> | check <scene> [--project <tsconfig.json>]')
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{const result=main(process.argv.slice(2));print(result);if(['INVALID','NO_MATCH','NOT_FOUND'].includes(result.status))process.exitCode=1}
 catch(e){print({status:'ERROR',error:e.message});process.exitCode=2}
}

#!/usr/bin/env node
// The sole visual export entry: React SSR and hydration share the same components.
import {createRequire} from 'node:module'
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync,existsSync,lstatSync,rmdirSync} from 'node:fs'
import {resolve,dirname,join,relative,basename} from 'node:path'
import {fileURLToPath} from 'node:url'
import {tmpdir} from 'node:os'
import {createHash} from 'node:crypto'
import {checkScene,assertSceneUnchanged,sceneBuildOptions} from './component-library.mjs'
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),sha=x=>createHash('sha256').update(x).digest('hex')
function options(args){const out={};for(let i=0;i<args.length;i++){const k=args[i];if(['--example','--document','--components'].includes(k)){if(k in out)throw new Error('Duplicate argument');out[k]=true;continue}if(!['--input','--out-dir','--scene','--title','--project'].includes(k)||!args[i+1]||args[i+1].startsWith('--'))throw new Error('Expected --example, --components, --input <JSON> or --scene <React entry> --title <text>, and --out-dir <new directory>; --document prints an internal document to stdout');if(k in out)throw new Error('Duplicate argument');out[k]=args[++i]}if(['--example','--components','--input','--scene'].filter(k=>out[k]).length!==1)throw new Error('Choose exactly one input');if(out['--document']?out['--out-dir']||!out['--input']:!out['--out-dir'])throw new Error('Invalid output mode');if(out['--scene']?!out['--title']?.trim():out['--title'])throw new Error('Scene mode requires a nonempty title; other modes reject title');if(out['--project']&&!out['--scene'])throw new Error('--project requires --scene');return out}
function bundledLicenses(metafile){
 const directories=new Set()
 for(const input of Object.keys(metafile.inputs)){
  if(!input.includes('node_modules/'))continue
  let folder=dirname(resolve(root,input))
  while(folder!==dirname(folder)&&!existsSync(join(folder,'package.json')))folder=dirname(folder)
  if(existsSync(join(folder,'package.json')))directories.add(folder)
 }
 return [...directories].map(folder=>{
  const pkg=JSON.parse(readFileSync(join(folder,'package.json'),'utf8'))
  const packaged=['LICENSE','LICENSE.md','LICENSE.txt','license','license.md'].map(name=>join(folder,name)).find(existsSync)
  // This exact npm tarball omits its MIT notice; pin the source notice locally.
  const path=packaged??(pkg.name==='react-remove-scroll-bar'&&pkg.version==='2.3.8'?join(root,'ui/licenses/react-remove-scroll-bar-2.3.8.txt'):undefined)
  if(!path)throw new Error('Missing license notice for bundled package '+pkg.name)
  return {name:pkg.name,version:pkg.version,text:readFileSync(path,'utf8')}
 }).sort((a,b)=>a.name.localeCompare(b.name))
}
let stage,ownedOutput,ownedFiles=[]
try{
 let build;try{({build}=await import('esbuild'))}catch{throw new Error('Shared React dependencies missing: run npm ci --ignore-scripts once in the shared visual-runtime directory')}
 const args=options(process.argv.slice(2)),scene=args['--scene']?resolve(args['--scene']):null
 if(scene&&!/\.[jt]sx?$/.test(scene))throw new Error('Scene entry must be a JS/JSX/TS/TSX module with a default React component')
 let sceneCheck
 if(scene){sceneCheck=checkScene(scene,{project:args['--project']});if(sceneCheck.status!=='CHECKED'){const e=new Error('Scene type check failed');e.diagnostics=sceneCheck.diagnostics;throw e}}
 const raw=args['--components']?Buffer.from('{}\n'):readFileSync(scene??(args['--example']?join(root,'visuals/example.json'):resolve(args['--input'])));if(raw.length>8*1024*1024)throw new Error('Input exceeds 8 MiB')
 const parsed=scene?null:JSON.parse(raw.toString()),model=args['--components']?{kind:'components',data:{}}:args['--document']?parsed:{kind:'artifact',data:parsed};stage=mkdtempSync(join(tmpdir(),'507-react-export-'))
 const server=await build({entryPoints:[join(root,'visuals/server.tsx')],outfile:join(stage,'server.cjs'),bundle:true,platform:'node',format:'cjs',logLevel:'silent',jsx:'automatic',define:{'process.env.NODE_ENV':'"production"'}})
 const client=await build(scene?{...sceneBuildOptions(scene,args['--project']),outfile:join(stage,'client.js')}:{absWorkingDir:root,entryPoints:[join(root,'visuals/client.tsx')],outfile:join(stage,'client.js'),bundle:true,platform:'browser',format:'iife',write:false,metafile:true,minify:true,charset:'utf8',target:'es2020',logLevel:'silent',jsx:'automatic',define:{'process.env.NODE_ENV':'"production"'}})
 if(sceneCheck)assertSceneUnchanged(sceneCheck,client.metafile)
 if(Object.values(client.metafile.outputs).some(out=>out.imports.some(item=>item.external)))throw new Error('Offline scene cannot retain external imports or resources')
 const require=createRequire(import.meta.url),renderer=require(join(stage,'server.cjs'))
 const licenses=bundledLicenses(client.metafile)
 licenses.push({name:'shadcn/ui adaptations',text:readFileSync(join(root,'ui/licenses/shadcn-ui.txt'),'utf8')})
 // Shared kit/examples are local sources, so npm's license graph cannot cover them.
 licenses.push({name:'Stageshow shared adaptations',text:readFileSync(join(root,'LICENSE'),'utf8')})
 let css,source
 if(scene){
  css=client.outputFiles.filter(file=>file.path.endsWith('.css')).map(file=>file.text).join('\n')
  const graph=Object.keys(client.metafile.inputs).filter(path=>path!=='<stdin>').sort().map(path=>({path:relative(dirname(scene),resolve(root,path)),sha256:sha(readFileSync(resolve(root,path)))}))
  source={kind:'scene',title:args['--title'],entry:basename(scene),inputSha256:sha(raw),sourceGraphSha256:sha(JSON.stringify(graph)),sources:graph}
 }else{
  const result=await build({entryPoints:[join(root,'visuals/visuals.css')],bundle:true,write:false,minify:true,logLevel:'silent'});css=result.outputFiles[0].text
 }
 const script=client.outputFiles.find(file=>file.path.endsWith('.js')).text
 const html=scene?renderer.renderScene(args['--title'],source,css,script,licenses):renderer.render(model,css,script,licenses)
 if(args['--document'])process.stdout.write(html)
 else{
  const out=resolve(args['--out-dir']);if(existsSync(out)||(()=>{try{return lstatSync(out).isSymbolicLink()}catch{return false}})())throw new Error('out-dir already exists; prior artifact preserved')
  const manifest={schema:2,renderer:'shared React',mode:scene?'scene':args['--components']?'components':parsed.mode,pages:scene||args['--components']?1:parsed.pages.length,inputSha256:sha(raw),...(scene?{sourceGraphSha256:source.sourceGraphSha256,sceneCheck:{status:sceneCheck.status,sourceSha256:sceneCheck.sourceSha256,project:sceneCheck.project?relative(dirname(scene),sceneCheck.project):null,limits:sceneCheck.limits}}:{}),htmlSha256:sha(html),format:'offline HTML',limits:['Rendering is not semantic review, author acceptance or publishing.',...(scene?['Scene source is browser-only, not executed for Node SSR. Editable source remains at the supplied entry; export contains compiled code.']:[])]},files={'index.html':html,[scene?'scene.json':'content.json']:scene?JSON.stringify(source,null,2)+'\n':raw,'manifest.json':JSON.stringify(manifest,null,2)+'\n'}
  mkdirSync(dirname(out),{recursive:true});mkdirSync(out);ownedOutput=out
  for(const [name,body] of Object.entries(files)){writeFileSync(join(out,name),body,{flag:'wx'});ownedFiles.push(name)}
  ownedOutput=null;console.log(JSON.stringify({status:'RENDERED',path:join(out,'index.html'),...manifest}))
 }
}catch(error){if(ownedOutput){for(const name of ownedFiles)try{rmSync(join(ownedOutput,name))}catch{};try{rmdirSync(ownedOutput)}catch{}}console.error(JSON.stringify({status:'ERROR',error:error.message,...(error.diagnostics?{diagnostics:error.diagnostics}:{})}));process.exitCode=2}
finally{if(stage)rmSync(stage,{recursive:true,force:true})}

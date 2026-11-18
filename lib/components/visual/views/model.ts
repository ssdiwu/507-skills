export type Range = number | [number, number]
export type Item = {label:string; detail?:string; date?:string; status?:string}
export type BaseBlock = {id?:string;type:string;title:string;caption?:string;sourceIds?:string[]}
export type Block = BaseBlock & {items?: (Item & {value?:Range|null;note?:string})[]; unit?:string; max?:number; aside?:Item; model?:'serial'; taskForms?:number[];minutesPerForm?:Range;remainingMinutes?:Range}
export type Language = 'en' | 'zh-CN'
export type ReadingSection = {body?:string;bullets?:string[];blocks?:Block[]}
export type ArtifactPage = ReadingSection & {title:string;sourceIds?:string[];notes?:string;sections?:ReadingSection[]}
export const pageSections = (page:ArtifactPage):ReadingSection[] => page.sections??[page]
export type ArtifactContent = {mode:'site'|'cards'|'deck';title:string;subtitle?:string;pages:ArtifactPage[];sources?:{id:string;label:string;url?:string}[]}
export type ArtifactModel = ArtifactContent & {language?:Language;translations?:Partial<Record<Language,ArtifactContent>>}
export type DocumentModel = {kind:'artifact';data:ArtifactModel}|{kind:'components';data:Record<string,never>}|{kind:'task-view'|'product-map'|'entry';data:any}
export function bounds(value:Range):[number,number]{return typeof value==='number'?[value,value]:value}
export function format(value:number){return Number(value.toPrecision(8)).toString()}
export function rangeText(value:Range){const [low,high]=bounds(value);return low===high?format(low):`${format(low)}–${format(high)}`}
function object(value:unknown,allowed:string[],required:string[]=[]):asserts value is Record<string,any>{if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).some(k=>!allowed.includes(k))||required.some(k=>!(k in value)))throw new Error('Invalid fields; allowed: '+allowed.join(', '))}
function text(value:unknown):asserts value is string{if(typeof value!=='string')throw new Error('Expected text')}
function number(value:unknown,minimum=0):asserts value is number{if(typeof value!=='number'||!Number.isFinite(value)||value<minimum)throw new Error('Expected finite nonnegative number')}
function range(value:unknown,minimum=0):asserts value is Range{if(Array.isArray(value)){if(value.length!==2)throw new Error('Expected two range bounds');value.forEach(v=>number(v,minimum));if(value[0]>value[1])throw new Error('Reversed range')}else number(value,minimum)}
function strings(value:unknown):asserts value is string[]{if(!Array.isArray(value)||value.some(v=>typeof v!=='string'))throw new Error('Expected text array')}
function refs(value:unknown,known:Set<string>){strings(value);if(value.some(v=>!known.has(v)))throw new Error('Unknown source reference')}
function validateContent(data:unknown):asserts data is ArtifactContent{
 object(data,['mode','title','subtitle','pages','sources'],['mode','title','pages']);text(data.title);if(!['site','cards','deck'].includes(data.mode))throw new Error('Unknown mode');if(data.subtitle!==undefined)text(data.subtitle)
 const blockIds=new Set<string>();const known=new Set<string>();if(data.sources!==undefined&&!Array.isArray(data.sources))throw new Error('Expected sources')
 for(const s of data.sources??[]){object(s,['id','label','url'],['id','label']);text(s.id);text(s.label);if(!s.id||known.has(s.id))throw new Error('Duplicate/empty source');known.add(s.id);if(s.url){text(s.url);const u=new URL(s.url);if(!['https:','http:'].includes(u.protocol))throw new Error('Unsupported source URL')}}
 if(!Array.isArray(data.pages)||!data.pages.length)throw new Error('Expected nonempty pages')
 for(const page of data.pages){object(page,['title','body','bullets','sourceIds','notes','blocks','sections'],['title']);text(page.title);if(page.notes!==undefined)text(page.notes);refs(page.sourceIds??[],known)
  if(page.sections!==undefined){
   if(!Array.isArray(page.sections)||!page.sections.length||page.sections.length>50)throw new Error('Expected 1–50 reading sections')
   if(['body','bullets','blocks'].some(k=>k in page))throw new Error('Use sections or legacy page content, not both')
   for(const section of page.sections){object(section,['body','bullets','blocks']);if(!Object.keys(section).length)throw new Error('Empty reading section')}
  }
  for(const section of page.sections??[page]){
  if(section.body!==undefined)text(section.body);if(section.bullets!==undefined)strings(section.bullets)
  if(section.blocks!==undefined&&!Array.isArray(section.blocks))throw new Error('Expected blocks')
  for(const b of section.blocks??[]){
   const fields:Record<string,string[]>={timeline:['items'],steps:['items'],comparison:['items','unit','max'],layout:['items','aside'],queue:['model','taskForms','minutesPerForm','remainingMinutes']}
   if(!fields[b.type])throw new Error('Unknown visual type');object(b,['id','type','title','caption','sourceIds',...fields[b.type]],['type','title']);text(b.title);if(b.id!==undefined){text(b.id);if(!b.id||blockIds.has(b.id))throw new Error('Duplicate/empty block id');blockIds.add(b.id)}if(b.caption!==undefined)text(b.caption);refs(b.sourceIds??[],known)
   if(b.type==='queue'){
    if(b.model!=='serial')throw new Error('Explicit serial model required');if(!Array.isArray(b.taskForms)||b.taskForms.length>8||b.taskForms.some((v:unknown)=>typeof v!=='number'||!Number.isInteger(v)||v<1||v>100))throw new Error('Expected 0–8 tasks of 1–100 forms');range(b.minutesPerForm,.000001);range(b.remainingMinutes);if(bounds(b.minutesPerForm)[1]>10000||bounds(b.remainingMinutes)[1]>10000)throw new Error('Queue minutes exceed illustration range')
   }else{
    if(!Array.isArray(b.items)||!b.items.length||b.items.length>50)throw new Error('Expected 1–50 items');let largest=1
    for(const item of b.items){object(item,['label','detail',...(b.type==='timeline'?['date','status']:[]),...(b.type==='comparison'?['value','note']:[])],['label',...(b.type==='comparison'?['value']:[])]);for(const k of ['label','detail','date','status','note'])if(item[k]!==undefined)text(item[k]);if(b.type==='comparison'&&item.value!==null){range(item.value);largest=Math.max(largest,bounds(item.value)[1])}}
    if(b.unit!==undefined)text(b.unit);if(b.max!==undefined){number(b.max,.000001);if(b.max<largest&&b.items.some((x:any)=>x.value!==null&&bounds(x.value)[1]>b.max))throw new Error('Comparison scale clips known values')}
    if(b.aside!==undefined){object(b.aside,['label','detail'],['label']);text(b.aside.label);if(b.aside.detail!==undefined)text(b.aside.detail)}
   }
  }
  }
 }
}
export function validateArtifact(data:unknown):asserts data is ArtifactModel{
 object(data,['mode','title','subtitle','pages','sources','language','translations'],['mode','title','pages'])
 const {language,translations,...content}=data
 validateContent(content)
 if(language!==undefined&&!['en','zh-CN'].includes(language))throw new Error('Unsupported language')
 if(translations!==undefined){
  object(translations,['en','zh-CN'])
  for(const [key,value] of Object.entries(translations)){
   if(key===(language??'zh-CN'))throw new Error('Translation duplicates default language')
   validateContent(value)
   if(value.mode!==content.mode)throw new Error('Translation mode must match')
   if(value.pages.length!==content.pages.length)throw new Error('Translation pages must align')
   value.pages.forEach((page,i)=>{
    const sections=pageSections(page),priorSections=pageSections(content.pages[i])
    if(sections.length!==priorSections.length)throw new Error('Translation reading sections must align')
    sections.forEach((section,k)=>{
    const blocks=section.blocks??[],original=priorSections[k].blocks??[]
    if(blocks.length!==original.length)throw new Error('Translation blocks must align')
    blocks.forEach((block,j)=>{
     const prior=original[j]
     if(block.type!==prior.type||block.id!==prior.id)throw new Error('Translation block identities must align')
     if(block.type==='queue'){
      if(!block.id)throw new Error('Translated queues require stable block ids')
      for(const field of ['model','taskForms','minutesPerForm','remainingMinutes'] as const)if(JSON.stringify(block[field])!==JSON.stringify(prior[field]))throw new Error('Translation queue conditions must match')
     }
    })
    })
   })
  }
 }
}
export function validateDocument(value:unknown):asserts value is DocumentModel{
 object(value,['kind','data'],['kind','data']);if(value.kind==='artifact')validateArtifact(value.data);else if(value.kind==='components')object(value.data,[]);else if(!['task-view','product-map','entry'].includes(value.kind)||!value.data||typeof value.data!=='object')throw new Error('Unknown document kind');else if(value.kind==='entry'&&!/^versions\/[a-f0-9]+\/index\.html$/.test(value.data.href))throw new Error('Invalid version entry')
}

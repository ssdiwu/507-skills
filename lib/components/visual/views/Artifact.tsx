import React,{useState,useEffect} from 'react'
import {FileText,Clock3,Check,TriangleAlert,LoaderCircle} from 'lucide-react'
import {Button,Input} from '../ui'
import {ArtifactModel,ArtifactContent,Language,Block,bounds,format,rangeText,pageSections} from './model'
export function Queue({block:b,language='zh-CN'}:{block:Block;language?:Language}){
 const t=(en:string,zh:string)=>language==='en'?en:zh
 const [forms,setForms]=useState(b.taskForms!),[state,setState]=useState('waiting')
 const [low,high]=bounds(b.minutesPerForm!),remaining=bounds(b.remainingMinutes!),total=forms.reduce((a,n)=>a+n,0)
 const wait:[number,number]=[remaining[0]+total*low,remaining[1]+total*high]
 const states:Record<string,[string,string]>={
  processing:[t('Checking your forms','正在检查你的表格'),t('Your task is processing; a wait estimate no longer applies.','当前任务已经开始处理，等待时间不再适用。')],
  completed:[t('Check completed; the report is ready','检查完成，可以查看报告'),t('Illustration only; this page has not generated a real report.','完成状态仅为示意；本页未生成真实报告。')],
  failed:[t('Processing failed; follow-up required','处理失败，需要跟进'),t('Illustration only; the business system provides the actual reason and recovery.','失败状态仅为示意；实际原因与恢复方式由业务系统提供。')]
 }
 const choices=[['waiting',t('Waiting','等待中')],['processing',t('Processing','处理中')],['completed',t('Completed','已完成')],['failed',t('Failed','失败')]]
 const term=(value:Parameters<typeof rangeText>[0])=>Array.isArray(value)?`(${rangeText(value)})`:rangeText(value)
 const StateIcon=state==='completed'?Check:state==='failed'?TriangleAlert:state==='processing'?LoaderCircle:Clock3
 function numeric(value:string,min:number,max:number,previous:number){const n=Number(value);return value.trim()&&Number.isFinite(n)?Math.max(min,Math.min(max,Math.round(n))):previous}
 return <div className={'viz-queue queue-example is-'+state}>
  <div className="queue-toolbar">
   <span className="queue-example-label"><span aria-hidden="true"/>{t('Interactive example','交互示意')}</span>
   <div className="queue-states" role="group" aria-label={t('Illustration states','切换示意状态')}>
    {choices.map(([key,label])=><Button type="button" key={key} data-queue-state={key} aria-pressed={state===key} onClick={()=>setState(key)}>{label}</Button>)}
   </div>
  </div>
  <div className="queue-result" role="status" aria-live="polite">
   <StateIcon size={20} strokeWidth={1.7} aria-hidden="true"/>
   <div><strong data-queue-title>{state==='waiting'?<>{t('Estimated wait: about ','预计约 ')}<span className="viz-quantity">{rangeText(wait)} {t('minutes','分钟')}</span>{t(' until processing starts','后开始处理')}</>:states[state][0]}</strong>
   <p data-queue-detail>{state==='waiting'?t(`${forms.length} waiting tasks ahead across all users, containing ${total} forms; excludes your current task.`,`全平台前方有 ${forms.length} 个等待任务，共 ${total} 份表格；不含当前任务。`):states[state][1]}</p></div>
  </div>
  <div hidden={state!=='waiting'}>
   <div className="queue-flow-heading">
    <span>{t('Processing order','处理顺序')}</span>
    <label className="queue-count">{t('Waiting tasks ahead across the platform','全平台前方等待任务数')}<Input data-task-count type="number" min={0} max={8} value={forms.length} onChange={e=>{const n=numeric(e.target.value,0,8,forms.length);setForms(old=>Array.from({length:n},(_,i)=>old[i]??1))}}/></label>
   </div>
   <ol className="queue-flow" aria-label={t('Illustrative platform queue','平台队列示意')}>
    <li className="queue-task queue-active"><span className="queue-position">{t('Processing channel','当前处理通道')}</span><Clock3 size={26} strokeWidth={1.4} aria-hidden="true"/><strong>{t('Already processing','正在处理')}</strong><span className="queue-task-detail">{t('Remaining: ','剩余 ')}{rangeText(b.remainingMinutes!)} {t('min','分钟')}</span></li>
    {forms.map((n,i)=><li className="queue-task queue-waiting" key={i} data-waiting-task>
     <span className="queue-position">{t(`Ahead ${i+1}`,`前方 ${i+1}`)}</span><FileText size={26} strokeWidth={1.4} aria-hidden="true"/><strong>{t(`Task ${i+1}`,`任务 ${i+1}`)}</strong>
     <label className="queue-forms">{t('Forms','表格')}<Input data-forms type="number" min={1} max={100} aria-label={t(`Forms in task ${i+1} ahead`,`前方任务 ${i+1} 的表格数`)} value={n} onChange={e=>{const value=numeric(e.target.value,1,100,n);setForms(old=>old.map((x,j)=>j===i?value:x))}}/>{t('','份')}</label>
    </li>)}
    <li className="queue-task queue-mine"><span className="queue-position">{t('Next after these','轮到我时')}</span><FileText size={26} strokeWidth={1.4} aria-hidden="true"/><strong>{t('Your task','我的任务')}</strong><span className="queue-task-detail">{t('Waiting to start','等待开始处理')}</span></li>
   </ol>
   <div className="queue-calculation"><span>{t('Wait calculation','等待时间估算')}</span><span>{term(b.remainingMinutes!)} + {total} × {term(b.minutesPerForm!)} = <strong>{rangeText(wait)} {t('min','分钟')}</strong></span></div>
  </div>
  <p className="queue-assumption">{t(`Illustration only. One processing channel, in queue order; each form takes ${rangeText(b.minutesPerForm!)} min. Not measured performance or a live queue. Other users’ file details are hidden.`,`单处理通道、按队列顺序处理，每份表格 ${rangeText(b.minutesPerForm!)} 分钟。以上为示意假设，非实测或实时队列，不展示其他用户文件详情。`)}</p>
 </div>
}
export function VisualBlock({block:b,id,model,language='zh-CN'}:{block:Block;id:string;model:ArtifactContent;language?:Language}){
 const t=(en:string,zh:string)=>language==='en'?en:zh
 const items=b.items??[],maximum=b.max??Math.max(1,...items.map(i=>i.value===null||i.value===undefined?0:bounds(i.value)[1]));let content:React.ReactNode
 if(b.type==='queue')content=<Queue block={b} language={language}/>
 else if(b.type==='comparison')content=<>{items.map((i,k)=><div className="viz-compare-row" key={k}><div className="viz-compare-label"><strong>{i.label}</strong><span>{i.value===null?t('Unknown / not measured','未知／未量度'):rangeText(i.value!)+(b.unit?' '+b.unit:'')}</span></div>{i.value===null?<div className="viz-unknown">{t('No value available; no bar drawn','暂无数值，不绘制长度')}</div>:<div className="viz-track" aria-hidden="true"><span className="viz-fill" style={{width:format(bounds(i.value!)[0]/maximum*100)+'%'}}/><span className="viz-range" style={{left:format(bounds(i.value!)[0]/maximum*100)+'%',width:format((bounds(i.value!)[1]-bounds(i.value!)[0])/maximum*100)+'%'}}/></div>}{i.note&&<p className="viz-note">{i.note}</p>}</div>)}<p className="viz-note">{t('Common scale: ','共同尺度：')}0–{format(maximum)} {b.unit}{t('. Hatching indicates a range.','。斜纹表示区间。')}</p></>
 else{
  const list=<ol className={'viz-'+b.type}>{items.map((i,k)=><li key={k}>{b.type==='timeline'?<span className="viz-date">{i.date}</span>:<span className="viz-index">{k+1}</span>}<strong>{i.label}</strong>{i.status&&<span className="viz-status">{i.status}</span>}{i.detail&&<p>{i.detail}</p>}</li>)}</ol>
  content=b.type==='layout'?<><div className="viz-layout-pair">{list}<div className="viz-aside"><strong>{b.aside?.label??t('Notes','说明区')}</strong><p>{b.aside?.detail}</p></div></div><p className="viz-note">{t('Layout illustration, not an actual product screenshot.','版面示意，非真实产品截图。')}</p></>:list
 }
 return <figure className={'viz viz-'+b.type+'-block'} aria-labelledby={id+'-title'}><figcaption id={id+'-title'}>{b.title}</figcaption>{content}{b.caption&&<p className="viz-caption">{b.caption}</p>}{!!b.sourceIds?.length&&<p className="viz-sources">{t('Source: ','来源：')}{b.sourceIds.map((ref,i)=>{const s=model.sources!.find(s=>s.id===ref)!;return <React.Fragment key={ref}>{i?'；':''}<a href={'#source-'+encodeURIComponent(ref)}>{s.label}</a></React.Fragment>})}</p>}</figure>
}
export function Artifact({data}:{data:ArtifactModel}){
 const [language,setLanguage]=useState<Language>(data.language??'zh-CN')
 const d:ArtifactContent=language===(data.language??'zh-CN')?data:data.translations![language]!
 const t=(en:string,zh:string)=>language==='en'?en:zh
 const languages=[data.language??'zh-CN',...Object.keys(data.translations??{})] as Language[]
 useEffect(()=>{document.documentElement.lang=language;document.title=d.title},[language,d.title])
 return <div className={d.mode+' artifact'}>
  <header>
   {languages.length>1&&<div className="artifact-languages" role="group" aria-label="Language / 阅读语言">{languages.map(l=><Button type="button" key={l} lang={l} aria-pressed={language===l} onClick={()=>setLanguage(l)}>{l==='en'?'EN':'中文'}</Button>)}</div>}
   <h1>{d.title}</h1><p>{d.subtitle}</p>
   <nav aria-label={t('Page sections','逐页阅读')}>{d.pages.map((p,i)=><a key={i} href={'#p'+(i+1)}>{p.title}</a>)}</nav>
  </header>
  <main>{d.pages.map((p,i)=><article id={'p'+(i+1)} tabIndex={-1} key={i}>
   <span className="number">{String(i+1).padStart(2,'0')}</span><h2>{p.title}</h2>
   {pageSections(p).map((section,k)=><React.Fragment key={k}>
    {section.body?.split('\n\n').map((text,j)=><p key={j}>{text}</p>)}
    {section.blocks?.map((b,j)=><VisualBlock key={b.id!==undefined?`id:${b.id}`:`index:${j}`} block={b} model={d} language={language} id={`visual-${i+1}-${pageSections(p).slice(0,k).reduce((n,s)=>n+(s.blocks?.length??0),0)+j+1}`}/>)}
    {!!section.bullets?.length&&<ul>{section.bullets.map((t,j)=><li key={j}>{t}</li>)}</ul>}
   </React.Fragment>)}
   {!!p.sourceIds?.length&&<footer>{t('Source: ','来源：')}{p.sourceIds.map(ref=><a key={ref} href={'#source-'+encodeURIComponent(ref)}>{d.sources!.find(s=>s.id===ref)!.label} </a>)}</footer>}
   {p.notes&&<details><summary>{t('Reading notes','讲述提示')}</summary><p>{p.notes}</p></details>}
  </article>)}</main>
  <footer><h2>{t('Sources and reading basis','来源与阅读依据')}</h2><ol>{d.sources?.map(s=><li id={'source-'+encodeURIComponent(s.id)} key={s.id}>{s.url?<a href={s.url} rel="noopener noreferrer">{s.label}</a>:s.label}</li>)}</ol></footer>
 </div>
}

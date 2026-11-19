import React,{useEffect,useRef,useState} from 'react'
const display=(v:any)=>v===undefined?'未提供':v===null?'明确空值':v===''?'空文本':Array.isArray(v)?v.length?v.join('；'):'空数组':String(v)
export function TaskView({data:d}:{data:any}){
 const {projection:p,contract:c,labels,columns}=d,tasks=p.tasks as any[];const [navigation,setNavigation]=useState(0);const [query,setQuery]=useState(''),[status,setStatus]=useState(''),[owner,setOwner]=useState(''),[selected,setSelected]=useState<string|null>(null),detail=useRef<HTMLElement>(null)
 const byId=new Map<string,any>(tasks.map(t=>[t.fields.id,t])),chosen=selected?byId.get(selected):null
 const filtered=tasks.filter(t=>(!status||display(t.fields.status)===status)&&(!owner||display(t.fields.owner)===owner)&&(!query||Object.values(t.fields).flat().join(' ').toLocaleLowerCase().includes(query.trim().toLocaleLowerCase())))
 const link=(id:string)=><button type="button" className="task-link" data-task={id} onClick={()=>{setSelected(id);setNavigation(n=>n+1)}}>{byId.get(id)?.fields.title??id}</button>
 useEffect(()=>{if(selected){detail.current?.focus();detail.current?.scrollIntoView({block:'start'})}},[selected,navigation])
 const modeLabel=({simple:'普通工作：必要拆分与交回',graph:'有依赖的独立工作：任务关系',continuing:'持续工作：沿用现有记录'} as Record<string,string>)[c.mode]
 return <div className="task-view">
  <header><h1>{c.title}</h1><p>{c.modeNote}</p></header>
  <main>
   <section>
    <h2>当前工作</h2>
    <div className="tools">
     <label htmlFor="query">搜索<input className="task-control" id="query" type="search" value={query} onChange={event=>setQuery(event.target.value)}/></label>
     <label htmlFor="status">报告状态<select className="task-control" id="status" value={status} onChange={event=>setStatus(event.target.value)}><option value="">全部状态</option>{[...new Set(tasks.map(task=>display(task.fields.status)))].map(value=><option key={value} value={value}>{c.statusMap?.[value]?.label??value}</option>)}</select></label>
     <label htmlFor="owner">承担者<select className="task-control" id="owner" value={owner} onChange={event=>setOwner(event.target.value)}><option value="">全部承担者</option>{[...new Set(tasks.map(task=>display(task.fields.owner)))].map(value=><option key={value}>{value}</option>)}</select></label>
    </div>
    <p id="count" role="status" aria-live="polite">显示 {filtered.length} / {tasks.length} 项</p>
    <div className="table" role="region" aria-label="工作记录，可横向滚动" tabIndex={0}>
     <table>
      <thead><tr>{columns.map((key:string)=><th scope="col" key={key}>{labels[key]}</th>)}</tr></thead>
      <tbody id="rows">{filtered.map(task=><tr key={task.fields.id}>{columns.map((key:string)=><td key={key}>{key==='title'?link(task.fields.id):key==='status'?task.statusLabel:display(task.fields[key])}</td>)}</tr>)}</tbody>
     </table>
    </div>
    <p id="empty" hidden={!!filtered.length}>当前筛选没有匹配工作。</p>
   </section>
   {c.mode!=='simple'&&<section>
    <h2>工作之间的依赖</h2>
    <p className="tiny">关系来自指定记录；筛选不改变依赖。</p>
    <div id="graph" className="grid">{filtered.map(task=><article className="node" key={task.fields.id}>
     <div className="tiny">{task.fields.id} · {task.statusLabel}</div>
     <h3>{link(task.fields.id)}</h3>
     <p>{task.dependencyHint}</p>
     <p>依赖：{!('dependsOn' in task.fields)?'未提供':!task.fields.dependsOn.length?'记录无依赖':task.fields.dependsOn.map((id:string)=><React.Fragment key={id}>{link(id)} </React.Fragment>)}</p>
    </article>)}</div>
   </section>}
   <section id="detail" ref={detail} className="detail" tabIndex={-1} hidden={!chosen} aria-label="选定工作详情">
    {chosen&&<>
     <h2>{chosen.fields.title}</h2>
     <dl>{Object.keys(c.fields).map(key=><React.Fragment key={key}><dt>{labels[key]}</dt><dd>{key==='status'?chosen.statusLabel+'（原值：'+display(chosen.fields[key])+'）':display(chosen.fields[key])}</dd></React.Fragment>)}</dl>
     <p>{chosen.dependencyHint}</p>
     <p className="tiny">报告状态与验收记录分别展示；未提供验收不能解释成已验收。</p>
     <p className="mono">来源：{p.source.file} · {chosen.sourceLocation.line?'行 '+chosen.sourceLocation.line+'（表头行 '+chosen.sourceLocation.tableHeaderLine+'）':'JSON 路径 '+JSON.stringify(chosen.sourceLocation.jsonPath)}<br/>SHA-256：{p.source.sha256}</p>
     {!!chosen.fields.dependsOn?.length&&<p>前置工作：{chosen.fields.dependsOn.map((id:string)=><React.Fragment key={id}>{link(id)} </React.Fragment>)}</p>}
     <p>后续工作：{tasks.filter(task=>task.fields.dependsOn?.includes(selected)).map(task=><React.Fragment key={task.fields.id}>{link(task.fields.id)} </React.Fragment>)}</p>
    </>}
   </section>
   <noscript>本页的筛选和详情需要浏览器允许本地脚本。完整只读投影位于同目录 projection.json。</noscript>
  </main>
  <footer><details>
   <summary>来源与生成范围</summary>
   <p>{modeLabel}</p>
   <p>{p.scope}</p>
   <p className="mono">文件：{p.source.file}<br/>SHA-256：{p.source.sha256}</p>
   <p>在原过程记录维护任务，更新后重跑共有组件。{c.mode==='continuing'&&'历史网页保留。'}</p>
  </details></footer>
 </div>
}
const dimensions:Record<string,string>={design:'设计',implementation:'实现',runtime:'跑通观察'},kinds:Record<string,string>={page:'页面',tab:'Tab',button:'按钮',form:'表单',field:'输入／选择字段',drawer:'抽屉',dialog:'对话框',link:'链接',toggle:'开关',menu:'菜单'},edgeKinds:Record<string,string>={contains:'包含',enter:'进入',open:'打开',switch:'切换',return:'返回',trigger:'触发'},states:Record<string,string>={confirmed:'已确认',proposed:'候选','not-required':'明确不要求',unknown:'未知',declared:'已声明',wired:'已接线',partial:'部分',missing:'有依据的缺失',passed:'限定通过',failed:'失败','not-observed':'未观察'}
function Evidence({model,sources}:{model:any;sources:Map<string,any>}){return <>{Object.keys(dimensions).map(k=><React.Fragment key={k}><h3>{dimensions[k]}证据 · {model[k].length}条</h3>{model[k].length?model[k].map((x:any,i:number)=><article className={'ev '+(x.state==='failed'?'failed':x.state==='unknown'||x.state==='not-observed'?'unknown':'')} key={i}><strong>{states[x.state]}</strong><p>支持范围：{x.scope}</p><p>{x.note}</p>{['action','role','input','environment','version','observed'].filter(f=>f in x).map(f=><p key={f}>{({action:'动作',role:'角色',input:'输入',environment:'环境',version:'版本',observed:'观察'} as Record<string,string>)[f]}: {x[f]}</p>)}<p className="tiny">{x.sourceIds.length?x.sourceIds.map((id:string)=>{const s=sources.get(id);return s.label+' · '+s.locator+(s.revision?' · '+s.revision:'')}).join('\n'):'未提供来源'}</p></article>):<p className="unknown">未提供证据；不判断该维度已通过或已缺失。</p>}</React.Fragment>)}</>}
export function ProductMap({data:d}:{data:any}){
 const r=d.record,nodes=r.nodes as any[],edges=r.edges as any[],byId=new Map<string,any>(nodes.map(n=>[n.id,n])),byEdge=new Map<string,any>(edges.map(e=>[e.id,e])),sources=new Map<string,any>(r.sources.map((s:any)=>[s.id,s]));const [navigation,setNavigation]=useState(0);const [query,setQuery]=useState(''),[kind,setKind]=useState(''),[dimension,setDimension]=useState('design'),[state,setState]=useState(''),[selected,setSelected]=useState<string|null>(null),detail=useRef<HTMLElement>(null)
 function choose(id:string){setSelected(id);setNavigation(n=>n+1);if(typeof location!=='undefined')location.hash='node='+encodeURIComponent(id)}
 useEffect(()=>{const restore=()=>{const id=new URLSearchParams(location.hash.slice(1)).get('node');setSelected(id&&byId.has(id)?id:null)};window.addEventListener('hashchange',restore);restore();return()=>window.removeEventListener('hashchange',restore)},[])
 useEffect(()=>{if(selected){detail.current?.focus();detail.current?.scrollIntoView({block:'start'})}},[selected,navigation])
 const link=(id:string)=><button type="button" className="map-link" data-node={id} onClick={()=>choose(id)}>{byId.get(id)?.label??id}</button>
 const filtered=nodes.filter(n=>(!kind||n.kind===kind)&&(!query||[n.id,n.label,n.purpose,...n.conditions,...n.outcomes].join(' ').toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()))&&(!state||(state==='unprovided'?n.evidence[dimension].length===0:n.evidence[dimension].some((e:any)=>e.state===state))))
 const contained=new Set(edges.filter(e=>e.kind==='contains').map(e=>e.to)),tree:{id:string;depth:number}[]=[],stack=nodes.filter(n=>!contained.has(n.id)).reverse().map(n=>({id:n.id,depth:0}));while(stack.length&&tree.length<3000){const next=stack.pop()!;tree.push(next);for(const e of edges.filter(e=>e.kind==='contains'&&e.from===next.id).reverse())stack.push({id:e.to,depth:next.depth+1})}
 const chosen=selected?byId.get(selected):null
 const relations=(list:any[])=>list.map(e=><details key={e.id}><summary>{edgeKinds[e.kind]} · {byId.get(e.from)?.label} → {byId.get(e.to)?.label}</summary><p>{e.condition}</p><p>{link(e.from)} → {link(e.to)}</p><Evidence model={e.evidence} sources={sources}/></details>)
 return <div className="product-map">
  <header>
   <h1>{r.title}</h1>
   <p>{r.scope.goal}</p>
   <p>范围：{r.scope.boundary} · 版本：{r.scope.version}</p>
   <p>覆盖：{r.scope.coverage}（记录作者声明；组件不核完整性）</p>
   <p>条件：{r.scope.conditions.join('；')||'未列出'}</p>
   <p>限制：{r.scope.limitations.join('；')||'未列出'}</p>
  </header>
  <main>
   <section className="tools" aria-label="交互点筛选">
    <label htmlFor="query">搜索<input className="map-control" id="query" type="search" value={query} onChange={event=>setQuery(event.target.value)}/></label>
    <label htmlFor="kind">类型<select className="map-control" id="kind" value={kind} onChange={event=>setKind(event.target.value)}><option value="">全部类型</option>{Object.keys(kinds).map(key=><option key={key} value={key}>{kinds[key]}</option>)}</select></label>
    <label htmlFor="dimension">证据维度<select className="map-control" id="dimension" value={dimension} onChange={event=>{setDimension(event.target.value);setState('')}}>{Object.entries(dimensions).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></label>
    <label htmlFor="state">状态<select className="map-control" id="state" value={state} onChange={event=>setState(event.target.value)}><option value="">全部证据状态</option><option value="unprovided">未提供证据</option>{d.states[dimension].map((key:string)=><option value={key} key={key}>{states[key]}</option>)}</select></label>
   </section>
   <p id="count" role="status" aria-live="polite">显示 {filtered.length} / {nodes.length} 个交互点</p>
   <div className="grid">
    <section className="panel">
     <h2>交互点</h2>
     <div id="points" className="points">{filtered.length?filtered.map(node=><button className="point" type="button" data-node={node.id} onClick={()=>choose(node.id)} key={node.id}>
      <strong>{node.label}</strong><br/><span className="tiny">{kinds[node.kind]} · {Object.keys(dimensions).map(key=>dimensions[key]+node.evidence[key].length+'条').join(' ／ ')}</span>
     </button>):<p>没有匹配交互点；筛选不改变关系与证据。</p>}</div>
    </section>
    <section className="panel" id="detail" ref={detail} tabIndex={-1} aria-label="交互点详情">
     {chosen?<>
      <h2>{chosen.label}</h2>
      <p>{kinds[chosen.kind]} · <span className="mono">{chosen.id}</span></p>
      <p>{chosen.purpose}</p>
      <h3>可用条件</h3><p>{chosen.conditions.join('；')||'未列出条件'}</p>
      <h3>结果</h3><p>{chosen.outcomes.join('；')||'未提供结果'}</p>
      <Evidence model={chosen.evidence} sources={sources}/>
      <h3>入出关系（含筛选外节点）</h3>
      {relations(edges.filter(edge=>edge.from===selected||edge.to===selected))}
     </>:<p>选择一个交互点，看同一身份的三类证据和关联。</p>}
    </section>
   </div>
   <section aria-labelledby="global-views">
    <h2 id="global-views">全局视图</h2>
    <details className="panel">
     <summary>包含树</summary>
     <p className="tiny">按包含关系组织，同一节点可多处引用。多入口、返回和循环见全部关系。</p>
     <ul id="tree" className="tree">{tree.map((node,index)=><li key={index} style={{marginInlineStart:Math.min(node.depth,12)*12}}>{link(node.id)}{node.depth>12&&<span>（深层关系，完整内容见关系表）</span>}</li>)}</ul>
     {stack.length>0&&<p>包含投影显示已到上限，完整关系见关系表。</p>}
    </details>
    <details className="panel">
     <summary>全部关系</summary>
     <div className="table" tabIndex={0} aria-label="关系表，可横向滚动">
      <table>
       <thead><tr><th>起点</th><th>关系</th><th>目标</th><th>条件</th></tr></thead>
       <tbody id="relations">{edges.map(edge=><tr key={edge.id}><td>{link(edge.from)}</td><td>{edgeKinds[edge.kind]}</td><td>{link(edge.to)}</td><td>{edge.condition}</td></tr>)}</tbody>
      </table>
     </div>
    </details>
    <details className="panel">
     <summary>登记路径与独立路径证据</summary>
     <div id="paths">{r.paths.length?r.paths.map((path:any)=><details key={path.id}>
      <summary>{path.label}</summary>
      <p>{path.conditions.join('；')}</p>
      {relations(path.edgeIds.map((id:string)=>byEdge.get(id)))}
      <Evidence model={path.evidence} sources={sources}/>
     </details>):<p>未登记路径；节点证据不自动合成为路径通过。</p>}</div>
    </details>
   </section>
   <noscript>交互需要本地脚本；完整模型见同目录record.json。</noscript>
  </main>
  <footer><details>
   <summary>来源与生成范围</summary>
   <ul>{r.sources.map((source:any)=><li key={source.id}>{source.id} · {source.label} · {source.locator}</li>)}</ul>
   <p className="mono">记录SHA-256：{d.recordSha}</p>
   <p>每个节点是交互点。设计、实现与跑通证据分别保留；生成成功不是产品验收。</p>
   <p>只验证结构，来源定位按原记录保留、未自动验证。</p>
  </details></footer>
 </div>
}

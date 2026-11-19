import {useState} from 'react'
import './records.css'

const records = [
  {id:'A-102',title:'设备申请',owner:'陈晓',status:'待补资料',detail:'需要补充设备使用地点。'},
  {id:'A-103',title:'会议预约',owner:'林青',status:'待审核',detail:'申请周五使用二号会议室。'},
]
export default function RecordBrowser(){
 const [query,setQuery]=useState(''),[selected,setSelected]=useState<string|null>(records[0].id),[failed,setFailed]=useState(false)
 const visible=records.filter(r=>(r.title+r.id+r.owner).includes(query.trim()))
 const active=visible.find(r=>r.id===selected)
 return <section className="record-demo" aria-label="记录浏览示例">
  <header><div><h1>申请记录</h1><p>虚构示意数据 · 控件可操作，未连接业务服务</p></div><button type="button" onClick={()=>setFailed(!failed)}>{failed?'恢复示例':'模拟加载失败'}</button></header>
  <label className="record-search" htmlFor="record-query">搜索记录<input id="record-query" type="search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="名称、编号或负责人"/></label>
  {failed?<div className="record-alert" role="alert"><strong>记录暂时无法加载</strong><p>这是错误状态示例，现有筛选条件已保留。</p><button type="button" onClick={()=>setFailed(false)}>重试</button></div>:<div className="record-columns">
   <nav aria-label="申请列表">{visible.length?<ul>{visible.map(r=><li key={r.id}><button type="button" className="record-item" aria-pressed={selected===r.id} onClick={()=>setSelected(r.id)}><span><strong>{r.title}</strong><small>{r.id} · {r.owner}</small></span><span className="record-badge">{r.status}</span></button></li>)}</ul>:<div className="record-empty" role="status"><strong>没有匹配的记录</strong><p>试试其他名称或负责人。</p><button type="button" onClick={()=>setQuery('')}>清除筛选</button></div>}</nav>
   <article aria-label="记录详情">{active?<><p className="record-id">{active.id}</p><h2>{active.title}</h2><dl><dt>负责人</dt><dd>{active.owner}</dd><dt>当前状态</dt><dd>{active.status}</dd></dl><p>{active.detail}</p><button type="button" onClick={()=>setSelected(null)}>返回列表</button></>:<div className="record-empty"><strong>选择一条记录</strong><p>从列表查看状态和需要补充的内容。</p></div>}</article>
  </div>}
 </section>
}

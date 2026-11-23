import React, {useEffect, useRef, useState} from 'react'
import type {LibraryData} from './model'

type Target = {kind: 'skill' | 'resource' | 'legacy', id: string}
type RoleFilter = 'all' | 'main' | 'secondary'

const STAGE_TONES = ['lm-st-1', 'lm-st-2', 'lm-st-3', 'lm-st-4', 'lm-st-5'] as const

const STAGE_SUBGROUPS: Record<string, {title: string, skills: string[]}[]> = {
  '想清楚与定方案': [
    {title: '从模糊需求到设计规格', skills: ['507-what', '507-domain-model', '507-design', '507-behavior-spec']},
    {title: '现状理解与反馈研判', skills: ['507-explain', '507-case-synthesis']},
  ],
  '写代码与交工程': [
    {title: '排查、实现、交付与复盘', skills: ['507-work-issue', '507-build', '507-version-deliver', '507-work-retro']},
    {title: '功能地图、清理与计划', skills: ['507-product-map', '507-clean', '507-step-plan']},
  ],
  '写作品与换载体': [
    {title: '材料、成文、演示与换载体', skills: ['507-source-material', '507-create', '507-ui-demo', '507-adapt']},
  ],
  '推工作、立规矩与练协作': [
    {title: '事项推进与协同', skills: ['507-track', '507-task-dispatch']},
    {title: '规范、技能与门禁', skills: ['507-setup', '507-skill', '507-audit']},
  ],
}

const PRINCIPLE_GROUPS: {title: string, subtitle: string, tone: string, match: (source: string) => boolean}[] = [
  {
    title: 'Principles: 研究、取证与决策',
    subtitle: '事实基线、决定边界与协作续办',
    tone: 'lm-st-1',
    match: source => source.startsWith('lib/methods/evidence-and-decisions/') || source.startsWith('lib/methods/collaboration/'),
  },
  {
    title: 'Principles: 方案、界面与架构设计',
    subtitle: '结构候选、阅读/任务页与交互指导',
    tone: 'lm-st-3',
    match: source => source.startsWith('lib/methods/design/'),
  },
  {
    title: 'Principles: 工程、检查与门禁',
    subtitle: '工程取证、行为不变与自动化脚本',
    tone: 'lm-st-2',
    match: source => source.startsWith('lib/methods/engineering/') || source.startsWith('lib/components/tools/checks/'),
  },
  {
    title: 'Principles: 创作、表达与视觉组件',
    subtitle: '作者口吻、表达校验与 React 运行库',
    tone: 'lm-st-4',
    match: source => source.startsWith('lib/methods/writing/') || source.startsWith('lib/components/visual/visual-') || source.startsWith('lib/components/visual/references/') || source === 'lib/components/visual/LICENSE' || source === 'lib/components/visual/UPSTREAM.json',
  },
  {
    title: 'Principles: 投影、导出、清单与示例',
    subtitle: '地图投影、离线打包器与目录契约',
    tone: 'lm-st-5',
    match: () => true,
  },
]

const isMainSkill = (name: string) => {
  const rest = name.startsWith('507-') ? name.slice(4) : name
  return !rest.includes('-')
}

const summaryLine = (text: string) => {
  const first = text.split(/[。！？!?\n]/)[0]?.trim() || text.trim()
  return first
}

function StageIcon({index}: {index: number}) {
  if (index === 0) return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M15.5 8.5l-2 5-5 2 2-5z" /></svg>
  if (index === 1) return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" /></svg>
  if (index === 2) return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20l1-4L16 5l3 3L8 19z" /><path d="M14 7l3 3" /></svg>
  if (index === 3) return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="M9 12l2 2 4-4" /></svg>
  return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="6" r="2.5" /><circle cx="18" cy="6" r="2.5" /><circle cx="12" cy="18" r="2.5" /><path d="M8 7.5l3 8M16 7.5l-3 8M8.5 6h7" /></svg>
}

export function LibraryMap({data}: {data: LibraryData}) {
  const [query, setQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('all')
  const [zoom, setZoom] = useState(1)
  const [fullscreen, setFullscreen] = useState(false)
  const [selected, setSelected] = useState<Target | null>(null)
  const dialog = useRef<HTMLDialogElement>(null)
  const close = useRef<HTMLButtonElement>(null)

  const skills = new Map(data.skills.map(skill => [skill.name, skill]))
  const resources = new Map(data.resources.map(resource => [resource.source, resource]))
  const legacy = new Map(data.legacy.map(entry => [entry.id, entry]))
  const startSkills = new Set(data.recipes.map(recipe => recipe.steps[0]).filter((id): id is string => Boolean(id)))

  const skillStageTone = new Map<string, string>()
  data.lanes.forEach((lane, laneIndex) => {
    const tone = STAGE_TONES[laneIndex % STAGE_TONES.length]
    lane.skills.forEach(name => skillStageTone.set(name, tone))
  })
  data.crosscutting.forEach(name => skillStageTone.set(name, 'lm-st-5'))

  const mainCount = data.skills.filter(s => isMainSkill(s.name)).length
  const secondaryCount = data.skills.length - mainCount

  const skill = selected?.kind === 'skill' && skills.get(selected.id)
  const resource = selected?.kind === 'resource' && resources.get(selected.id)
  const historical = selected?.kind === 'legacy' && legacy.get(selected.id)

  useEffect(() => {
    function restore() {
      const route = new URLSearchParams(window.location.hash.slice(1))
      const kind = route.get('kind')
      const id = route.get('id')
      if (id && ((kind === 'skill' && data.skills.some(item => item.name === id)) ||
          (kind === 'legacy' && data.legacy.some(item => item.id === id)) ||
          (kind === 'resource' && data.resources.some(item => item.source === id)))) {
        setSelected({kind, id})
      } else {
        setSelected(null)
        dialog.current?.close()
      }
    }
    restore()
    window.addEventListener('hashchange', restore)
    return () => window.removeEventListener('hashchange', restore)
  }, [data])

  useEffect(() => {
    if (selected) {
      if (!dialog.current?.open) dialog.current?.showModal()
      close.current?.focus()
      dialog.current?.scrollTo(0, 0)
    }
  }, [selected])

  function openTarget(kind: Target['kind'], id: string) {
    setSelected({kind, id})
    window.location.hash = new URLSearchParams({kind, id}).toString()
  }

  function chip(kind: Target['kind'], id: string) {
    const label = kind === 'skill' ? skills.get(id)?.displayName : kind === 'resource' ? resources.get(id)?.title : id
    return <button type="button" key={`${kind}:${id}`} onClick={() => openTarget(kind, id)}>{label ?? id}</button>
  }

  const chips = (kind: Target['kind'], ids: string[]) => <div className="lm-chips">{ids.map(id => chip(kind, id))}</div>

  function skillCard(name: string, stageTone: string, showStart = false) {
    const item = skills.get(name)
    if (!item) return null
    const main = isMainSkill(item.name)
    const dimmed = (roleFilter === 'main' && !main) || (roleFilter === 'secondary' && main)
    return (
      <button
        type="button"
        key={item.name}
        aria-label={item.displayName}
        className={`lm-node ${stageTone}${dimmed ? ' is-dim' : ''}${selected?.kind === 'skill' && selected.id === item.name ? ' is-sel' : ''}`}
        onClick={() => openTarget('skill', item.name)}
      >
        {showStart && <span className="lm-start-pill" aria-hidden="true">START</span>}
        <span className="lm-node-top">
          <span className="lm-node-zh">{item.displayName}</span>
          <span className={`lm-role-tag ${main ? 'is-main' : 'is-sec'}`}>{main ? '主 · 3字' : '次 · 4字'}</span>
        </span>
        <code className="lm-node-id">{item.name}</code>
        <span className="lm-node-desc">{summaryLine(item.description)}</span>
      </button>
    )
  }

  function resourceCard(item: LibraryData['resources'][number], tone: string) {
    const dimmed = roleFilter !== 'all' && !item.consumers.some(c => roleFilter === 'main' ? isMainSkill(c) : !isMainSkill(c))
    const shortPath = item.source.replace(/^lib\//, '')
    return (
      <button
        type="button"
        key={item.source}
        aria-label={item.title}
        className={`lm-res-card ${tone}${dimmed ? ' is-dim' : ''}${selected?.kind === 'resource' && selected.id === item.source ? ' is-sel' : ''}`}
        onClick={() => openTarget('resource', item.source)}
      >
        <span className="lm-res-title">{item.title}</span>
        <span className="lm-res-meta">
          <code>{shortPath}</code>
          <span>复用 {item.consumers.length}</span>
        </span>
      </button>
    )
  }

  function partitionLane(lane: {title: string, skills: string[]}) {
    const preset = STAGE_SUBGROUPS[lane.title]
    if (!preset) return [{title: '', skills: lane.skills}]
    const seen = new Set<string>()
    const groups = preset
      .map(group => {
        const list = group.skills.filter(id => lane.skills.includes(id))
        list.forEach(id => seen.add(id))
        return {title: group.title, skills: list}
      })
      .filter(group => group.skills.length > 0)
    const rest = lane.skills.filter(id => !seen.has(id))
    if (rest.length > 0) groups.push({title: '其他职责', skills: rest})
    return groups
  }

  const queryText = query.trim().toLowerCase()
  const matches = (...terms: string[]) => terms.some(term => term.toLowerCase().includes(queryText))
  const previousNames = Object.entries(data.previousLabels)
  const exactTarget = previousNames.find(([name]) => name.toLowerCase() === queryText)?.[1]
  const previousMatches = new Set(previousNames.filter(([name]) => matches(name)).map(([, id]) => id))

  const foundSkills = data.skills.filter(item => {
    const textHit = exactTarget
      ? item.name === exactTarget
      : previousMatches.has(item.name) || matches(item.name, item.displayName, item.description, ...item.aliases)
    if (!textHit) return false
    if (roleFilter === 'main') return isMainSkill(item.name)
    if (roleFilter === 'secondary') return !isMainSkill(item.name)
    return true
  })
  const foundResources = data.resources.filter(item => matches(item.source, item.title))
  const foundLegacy = data.legacy.filter(item => exactTarget
    ? item.id === exactTarget && !skills.has(exactTarget)
    : matches(item.id) || (!skills.has(item.id) && previousMatches.has(item.id)))
  const total = foundSkills.length + foundResources.length + foundLegacy.length

  const stages = [
    ...data.lanes.map((lane, index) => ({
      title: lane.title,
      stageLabel: `Stage ${index + 1}`,
      tone: STAGE_TONES[index % STAGE_TONES.length],
      iconIndex: index,
      subgroups: partitionLane(lane),
      note: '',
    })),
    ...(data.crosscutting.length > 0 ? [{
      title: '跨跑道能力',
      stageLabel: `Stage ${data.lanes.length + 1}`,
      tone: 'lm-st-5',
      iconIndex: 4,
      subgroups: [{title: '贯穿全阶段 · 随时介入', skills: data.crosscutting}],
      note: '独立只读审查与复杂度图解可介入前面任一阶段，不单独锁定单一阶段。',
    }] : []),
  ]

  const principleBuckets = PRINCIPLE_GROUPS.map(group => ({...group, items: [] as LibraryData['resources']}))
  for (const item of data.resources) {
    const bucket = principleBuckets.find(group => group.match(item.source)) ?? principleBuckets[principleBuckets.length - 1]
    bucket.items.push(item)
  }

  const dialogTone = skill
    ? (skillStageTone.get(skill.name) ?? 'lm-st-2')
    : resource
      ? (principleBuckets.find(group => group.items.some(item => item.source === resource.source))?.tone ?? 'lm-st-5')
      : 'lm-st-1'

  return (
    <main className="library-map">
      <header className="lm-page-head">
        <div className="lm-title-row">
          <span className="lm-logo" aria-hidden="true">
            <svg viewBox="0 0 24 24"><rect x="3" y="3" width="8" height="8" rx="2" /><rect x="13" y="3" width="8" height="8" rx="2" /><rect x="3" y="13" width="8" height="8" rx="2" /><rect x="13" y="13" width="8" height="8" rx="2" /></svg>
          </span>
          <h1>技能应用地图</h1>
          <span className="lm-vpill">507-skills · {data.skills.length} 技能 · {mainCount} 主 / {secondaryCount} 次</span>
        </div>
        <p className="lm-page-sub">
          主要技能统一「1 英文词 + 3 汉字」（先抓主入口），次要技能统一「2 英文词 + 4 汉字」（专责深化）。点任意卡片查看适用边界、上下游交接与共享原则。
        </p>
      </header>

      <section className={`lm-hero${fullscreen ? ' is-fullscreen' : ''}`} aria-label="技能应用全景画布">
        <div className="lm-toolbar">
          <div className="lm-search-wrap">
            <label className="lm-sr-only" htmlFor="lm-search">查找技能、共有资源或旧名</label>
            <input
              id="lm-search"
              type="search"
              placeholder="搜索技能、共有资源或旧名（如：507-执行 / why）"
              value={query}
              onChange={event => setQuery(event.target.value)}
            />
          </div>

          <div className="lm-seg" role="group" aria-label="按技能角色筛选">
            <button type="button" aria-pressed={roleFilter === 'all'} onClick={() => setRoleFilter('all')}>全部 ({data.skills.length})</button>
            <button type="button" aria-pressed={roleFilter === 'main'} onClick={() => setRoleFilter('main')}>主要 · 3字 ({mainCount})</button>
            <button type="button" aria-pressed={roleFilter === 'secondary'} onClick={() => setRoleFilter('secondary')}>次要 · 4字 ({secondaryCount})</button>
          </div>

          <div className="lm-canvas-actions">
            <button type="button" className="lm-tbb sq" aria-label="缩小画布" onClick={() => setZoom(z => Math.max(0.75, Number((z - 0.1).toFixed(2))))}>−</button>
            <button type="button" className="lm-tbb sq" aria-label="放大画布" onClick={() => setZoom(z => Math.min(1.25, Number((z + 0.1).toFixed(2))))}>+</button>
            <button type="button" className="lm-tbb" onClick={() => setZoom(1)}>Fit 适配</button>
            <button type="button" className="lm-tbb" onClick={() => {setQuery(''); setRoleFilter('all'); setZoom(1)}}>Reset 重置</button>
            <button type="button" className="lm-tbb" aria-pressed={fullscreen} onClick={() => setFullscreen(v => !v)}>{fullscreen ? '退出全屏' : 'Full screen 全屏'}</button>
          </div>
        </div>

        {(roleFilter !== 'all' || zoom !== 1) && !queryText && (
          <div className="lm-fpill">
            <span>
              {roleFilter === 'main' ? `当前突出主要技能（${mainCount} 项）` : roleFilter === 'secondary' ? `当前突出次要技能（${secondaryCount} 项）` : '全部技能'}
              {zoom !== 1 ? ` · 缩放 ${Math.round(zoom * 100)}%` : ''}
            </span>
            <button type="button" onClick={() => {setRoleFilter('all'); setZoom(1)}}>恢复默认视图</button>
          </div>
        )}

        {queryText ? (
          <section className="lm-search-results">
            <div className="lm-search-head">
              <div>
                <h2>搜索结果</h2>
                <p role="status">{total ? `找到 ${total} 项` : '没有匹配项'}</p>
              </div>
              <button type="button" className="lm-tbb" onClick={() => setQuery('')}>返回地图</button>
            </div>
            {foundSkills.length > 0 && (
              <section className="lm-result-block">
                <h3>技能（{foundSkills.length}）</h3>
                <div className="lm-result-grid">
                  {foundSkills.map(item => skillCard(item.name, skillStageTone.get(item.name) ?? 'lm-st-2', startSkills.has(item.name)))}
                </div>
              </section>
            )}
            {foundResources.length > 0 && (
              <section className="lm-result-block">
                <h3>共有资源（{foundResources.length}）</h3>
                <div className="lm-result-grid">
                  {foundResources.map(item => resourceCard(item, 'lm-st-5'))}
                </div>
              </section>
            )}
            {foundLegacy.length > 0 && (
              <section className="lm-result-block">
                <h3>历史入口（{foundLegacy.length}）</h3>
                <div className="lm-chips">
                  {foundLegacy.map(item => chip('legacy', item.id))}
                </div>
              </section>
            )}
          </section>
        ) : (
          <div className="lm-canvas-scroll">
            <div
              className="lm-board"
              style={zoom === 1 ? undefined : ({zoom} as React.CSSProperties)}
            >
              <section aria-labelledby="lm-stages-title">
                <div className="lm-section-bar">
                  <h2 id="lm-stages-title">按任务选技能 · Stage Flow</h2>
                  <span className="lm-legend">
                    <span><b>START</b> 接力配方起点</span>
                    <span><b>↓</b> 本跑道实有下游接力</span>
                    <span><b>主 · 3字</b> 一词主要入口</span>
                    <span><b>次 · 4字</b> 两词次要专责</span>
                  </span>
                </div>

                <div className="lm-stage-grid" style={{'--stage-count': String(stages.length)} as React.CSSProperties}>
                  {stages.map((stage, stageIndex) => (
                    <section key={stage.title} className={`lm-stage-col ${stage.tone}`}>
                      <header className="lm-stage-head">
                        <span className="lm-stage-icon"><StageIcon index={stage.iconIndex} /></span>
                        <div>
                          <h3 className="lm-stage-title">{stage.title}</h3>
                          <span className="lm-stage-num">{stage.stageLabel}</span>
                        </div>
                        {stageIndex < stages.length - 1 && <span className="lm-stage-rail-arrow" aria-hidden="true">→</span>}
                      </header>

                      <div className="lm-stage-body">
                        {stage.subgroups.map(group => (
                          <div key={group.title || 'default'} className="lm-subgroup">
                            {group.title && <h4 className="lm-subgroup-title">{group.title}</h4>}
                            <div className="lm-card-stack">
                              {group.skills.map((skillId, idx) => {
                                const prevSkill = idx > 0 ? skills.get(group.skills[idx - 1]) : undefined
                                const hasEdge = Boolean(prevSkill?.downstream.includes(skillId))
                                return (
                                  <React.Fragment key={skillId}>
                                    {hasEdge && <div className="lm-flow-arrow" aria-hidden="true">↓</div>}
                                    {skillCard(skillId, stage.tone, startSkills.has(skillId))}
                                  </React.Fragment>
                                )
                              })}
                            </div>
                          </div>
                        ))}
                        {stage.note && <p className="lm-stage-gap">{stage.note}</p>}
                      </div>
                    </section>
                  ))}
                </div>
              </section>

              <section className="lm-anytime" aria-labelledby="lm-anytime-title">
                <div className="lm-anytime-head">
                  <span className="lm-infinity" aria-hidden="true">∞</span>
                  <div>
                    <h2 id="lm-anytime-title">Anytime · 任务接力与共有原则</h2>
                    <p>清楚任务直接单用或按需接力，下方原则卡片展示全部 {data.resources.length} 份共有规则、工具与组件入口。</p>
                  </div>
                </div>

                <section className="lm-recipes-band" aria-labelledby="lm-recipes-title">
                  <h3 id="lm-recipes-title" className="lm-band-heading">任务接力（{data.recipes.length} 条典型路线）</h3>
                  <div className="lm-recipes-grid">
                    {data.recipes.map(recipe => (
                      <section key={recipe.title} className="lm-recipe">
                        <h4>{recipe.title}</h4>
                        <ol aria-label={`${recipe.title}的接力顺序`}>
                          {recipe.steps.map((id, index) => (
                            <li key={`${index}:${id}`}>
                              <span className={index === 0 ? 'lm-step-start' : 'lm-step-arrow'} aria-hidden="true">
                                {index === 0 ? 'START' : '→'}
                              </span>
                              {chip('skill', id)}
                            </li>
                          ))}
                        </ol>
                      </section>
                    ))}
                  </div>
                </section>

                {data.resources.length > 0 && (
                  <section className="lm-principles-band" aria-labelledby="lm-principles-title">
                    <h3 id="lm-principles-title" className="lm-band-heading">Principles &amp; Shared Library · 共有原则与工具（{data.resources.length} 项）</h3>
                    <div className="lm-principles-grid">
                      {principleBuckets.filter(bucket => bucket.items.length > 0).map(bucket => (
                        <section key={bucket.title} className={`lm-principle-col ${bucket.tone}`}>
                          <header className="lm-principle-head">
                            <h4>{bucket.title}</h4>
                            <p>{bucket.subtitle}</p>
                          </header>
                          <div className="lm-res-grid">
                            {bucket.items.map(item => resourceCard(item, bucket.tone))}
                          </div>
                        </section>
                      ))}
                    </div>
                  </section>
                )}

                <details className="lm-legacy-drawer">
                  <summary>历史旧名与退役映射（{data.legacy.length} 条记录，也可直接在上方搜索框查旧名）</summary>
                  <div className="lm-legacy-list">
                    {chips('legacy', data.legacy.map(item => item.id))}
                  </div>
                </details>
              </section>
            </div>
          </div>
        )}
      </section>

      <dialog
        ref={dialog}
        className={`lm-dialog ${dialogTone}`}
        aria-labelledby="lm-detail"
        onClose={() => {
          if (window.location.hash) window.location.hash = ''
          setSelected(null)
        }}
      >
        <div className="lm-dialog-bar">
          <div className="lm-dialog-tags">
            {skill && <span className="lm-dtag is-key">{isMainSkill(skill.name) ? '主要技能 · 1词3字' : '次要技能 · 2词4字'}</span>}
            {resource && <span className="lm-dtag is-key">共有资源</span>}
            {historical && <span className="lm-dtag is-key">历史名称：{historical.decision}</span>}
          </div>
          <button type="button" className="lm-close" ref={close} onClick={() => dialog.current?.close()}>关闭详情</button>
        </div>

        <h2 id="lm-detail">{skill ? skill.displayName : resource ? resource.title : historical ? historical.id : ''}</h2>

        {skill && (
          <>
            <code className="lm-dialog-code">{skill.name}</code>
            <dl className="lm-dl">
              {[
                ['何时使用', skill.description, 'l-when'],
                ['何时跳过', skill.skip, 'l-warn'],
                ['输入', skill.input, 'l-is'],
                ['权限', skill.authority, 'l-get'],
                ['停止位置', skill.stop, 'l-use'],
                ['一句话示例', skill.example, 'l-ex'],
              ].map(([label, value, badge]) => (
                <div key={label} className="lm-dl-row">
                  <dt><span className={`lm-sec-badge ${badge}`}>{label}</span></dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
            <div className="lm-links-group">
              <h3>上游技能</h3>
              {skill.upstream.length > 0 ? chips('skill', skill.upstream) : <p className="lm-empty-note">可作为独立起点直接触发</p>}
              <h3>下游技能</h3>
              {skill.downstream.length > 0 ? chips('skill', skill.downstream) : <p className="lm-empty-note">当前路线末端交付</p>}
              <h3>共有资源</h3>
              {skill.resources.length > 0 ? chips('resource', skill.resources) : <p className="lm-empty-note">无额外共有资源依赖</p>}
              <h3>历史旧名</h3>
              {skill.aliases.length > 0 ? chips('legacy', skill.aliases) : <p className="lm-empty-note">无历史旧名映射</p>}
            </div>
          </>
        )}

        {resource && (
          <>
            <code className="lm-dialog-code">{resource.source}</code>
            <h3>使用此资源的技能</h3>
            {resource.consumers.length > 0 ? chips('skill', resource.consumers) : <p className="lm-empty-note">暂无直接声明消费者</p>}
          </>
        )}

        {historical && (
          <>
            <p className="lm-legacy-status">{historical.decision} · {historical.reason}</p>
            {historical.consumers.length > 0 && (
              <>
                <h3>现行入口</h3>
                {chips('skill', historical.consumers)}
              </>
            )}
          </>
        )}
      </dialog>
    </main>
  )
}

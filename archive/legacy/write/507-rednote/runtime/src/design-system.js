export const RUNTIME_VERSION = '0.1.0'

export const FONT_FAMILIES = {
  'source-han-sans': {
    label: '思源黑体',
    description: 'Adobe Source Han Sans CN Variable，SIL OFL 1.1。',
    face: 'RedNote Source Han Sans CN',
    cssFamily: '"RedNote Source Han Sans CN", sans-serif',
  },
  'source-han-serif': {
    label: '思源宋体',
    description: 'Adobe Source Han Serif CN Variable，SIL OFL 1.1。',
    face: 'RedNote Source Han Serif CN',
    cssFamily: '"RedNote Source Han Serif CN", serif',
  },
}

export const DESIGN_LANGUAGES = {
  'precision-modern': {label: '精密现代', description: '严格网格、锐利轮廓与精密层级。'},
  'editorial-archive': {label: '编辑档案', description: '暖纸、编辑栏栅格、细规则线与印刷层级。'},
  'soft-product': {label: '柔和产品', description: '舒展模块、人文层级与柔和状态色。'},
  'warm-narrative': {label: '温暖叙事', description: '非对称节奏、暖色与纸面叙事感。'},
  'research-organic': {label: '研究自然', description: '研究型层级、克制自然色与低装饰。'},
  'bold-statement': {label: '强力表达', description: '黑白高对比、粗规则线与单一高能强调。'},
}

export const PRESENTATION_SUPPORT = {
  cover: ['type-led', 'panel-led', 'editorial-print-led', 'illustration-led'],
  heading: ['type-led', 'editorial-print-led'],
  paragraph: ['type-led', 'editorial-print-led'],
  quote: ['type-led', 'panel-led', 'editorial-print-led'],
  list: ['type-led', 'panel-led', 'editorial-print-led'],
  code: ['panel-led', 'editorial-print-led'],
  table: ['data-led', 'panel-led', 'editorial-print-led'],
  diagram: ['schematic-led', 'hand-drawn-explainer'],
  media: ['photo-led', 'ui-product-led'],
  hr: ['editorial-print-led'],
}

export const PRESENTATION_LABELS = {
  'type-led': '文字主导',
  'panel-led': '面板模块',
  'data-led': '数据表达',
  'schematic-led': '结构示意',
  'photo-led': '照片证据',
  'ui-product-led': '产品界面',
  'editorial-print-led': '编辑印刷',
  'hand-drawn-explainer': '手绘解释',
  'illustration-led': '插画主导',
}

export const COMPONENT_LABELS = {
  cover: '封面', heading: '标题', paragraph: '正文', quote: '引语', list: '列表', code: '代码',
  table: '表格', diagram: '流程图', media: '图片', hr: '分隔线',
}

const PRESENTATIONS = {
  'precision-modern': {
    cover: 'type-led', heading: 'type-led', paragraph: 'type-led', quote: 'type-led', list: 'panel-led',
    code: 'panel-led', table: 'data-led', diagram: 'schematic-led', media: 'ui-product-led', hr: 'editorial-print-led',
  },
  'editorial-archive': {
    cover: 'editorial-print-led', heading: 'editorial-print-led', paragraph: 'editorial-print-led', quote: 'editorial-print-led',
    list: 'editorial-print-led', code: 'panel-led', table: 'editorial-print-led', diagram: 'schematic-led', media: 'photo-led', hr: 'editorial-print-led',
  },
  'soft-product': {
    cover: 'panel-led', heading: 'type-led', paragraph: 'type-led', quote: 'panel-led', list: 'panel-led',
    code: 'panel-led', table: 'panel-led', diagram: 'schematic-led', media: 'ui-product-led', hr: 'editorial-print-led',
  },
  'warm-narrative': {
    cover: 'illustration-led', heading: 'editorial-print-led', paragraph: 'editorial-print-led', quote: 'editorial-print-led',
    list: 'type-led', code: 'panel-led', table: 'editorial-print-led', diagram: 'hand-drawn-explainer', media: 'photo-led', hr: 'editorial-print-led',
  },
  'research-organic': {
    cover: 'editorial-print-led', heading: 'type-led', paragraph: 'type-led', quote: 'editorial-print-led', list: 'panel-led',
    code: 'panel-led', table: 'data-led', diagram: 'schematic-led', media: 'photo-led', hr: 'editorial-print-led',
  },
  'bold-statement': {
    cover: 'illustration-led', heading: 'editorial-print-led', paragraph: 'type-led', quote: 'editorial-print-led',
    list: 'type-led', code: 'panel-led', table: 'data-led', diagram: 'schematic-led', media: 'photo-led', hr: 'editorial-print-led',
  },
}

export const LANGUAGE_PALETTES = {
  'precision-modern': {paper: 'oklch(0.985 0.006 240)', paperAlt: 'oklch(0.94 0.012 240)', ink: 'oklch(0.22 0.02 250)', muted: 'oklch(0.52 0.04 250)', accent: 'oklch(0.58 0.19 255)', line: 'oklch(0.72 0.035 250)'},
  'editorial-archive': {paper: 'oklch(0.94 0.025 83)', paperAlt: 'oklch(0.89 0.034 75)', ink: 'oklch(0.23 0.018 55)', muted: 'oklch(0.48 0.035 60)', accent: 'oklch(0.49 0.14 32)', line: 'oklch(0.68 0.035 65)'},
  'soft-product': {paper: 'oklch(0.97 0.016 210)', paperAlt: 'oklch(0.92 0.028 215)', ink: 'oklch(0.28 0.035 240)', muted: 'oklch(0.53 0.045 235)', accent: 'oklch(0.62 0.13 210)', line: 'oklch(0.79 0.035 220)'},
  'warm-narrative': {paper: 'oklch(0.95 0.032 75)', paperAlt: 'oklch(0.89 0.055 62)', ink: 'oklch(0.28 0.035 47)', muted: 'oklch(0.52 0.06 48)', accent: 'oklch(0.62 0.15 45)', line: 'oklch(0.74 0.06 62)'},
  'research-organic': {paper: 'oklch(0.955 0.022 135)', paperAlt: 'oklch(0.90 0.038 140)', ink: 'oklch(0.26 0.035 145)', muted: 'oklch(0.49 0.055 145)', accent: 'oklch(0.51 0.12 148)', line: 'oklch(0.72 0.06 145)'},
  'bold-statement': {paper: 'oklch(0.985 0.004 80)', paperAlt: 'oklch(0.93 0.006 80)', ink: 'oklch(0.18 0.006 60)', muted: 'oklch(0.46 0.012 60)', accent: 'oklch(0.62 0.23 28)', line: 'oklch(0.30 0.01 60)'},
}

const treatmentFor = language => ({cover: language === 'bold-statement' ? 'section-emphasis' : 'default', heading: language === 'bold-statement' ? 'section-emphasis' : 'default', table: 'dense'})
const preset = (label, caption, designLanguage, palette = {}, presentationOverrides = {}, treatmentOverrides = {}) => ({
  label,
  caption,
  designLanguage,
  palette: {...LANGUAGE_PALETTES[designLanguage], ...palette},
  swatch: {background: (palette.paper || LANGUAGE_PALETTES[designLanguage].paper), color: (palette.accent || LANGUAGE_PALETTES[designLanguage].accent)},
  presentations: {...PRESENTATIONS[designLanguage], ...presentationOverrides},
  treatments: {...treatmentFor(designLanguage), ...treatmentOverrides},
})

export const PRESETS = {
  'current-editorial': preset('当前编辑红', '真实样例方向', 'bold-statement'),
  'retro-vintage': preset('复古怀旧', '旧纸与棕红', 'warm-narrative', {paper: 'oklch(0.92 0.045 78)', paperAlt: 'oklch(0.86 0.065 70)', accent: 'oklch(0.53 0.13 40)'}, {cover: 'editorial-print-led', heading: 'editorial-print-led', media: 'photo-led'}),
  newspaper: preset('报纸', '黑墨与新闻红', 'editorial-archive', {paper: 'oklch(0.95 0.018 85)', paperAlt: 'oklch(0.90 0.025 80)', accent: 'oklch(0.43 0.16 28)'}),
  'minimal-mono': preset('极简黑白', '克制高对比', 'precision-modern', {paper: 'oklch(0.985 0.002 80)', paperAlt: 'oklch(0.94 0.003 80)', ink: 'oklch(0.16 0.004 60)', accent: 'oklch(0.22 0.004 60)'}, {cover: 'type-led', list: 'type-led', media: 'photo-led'}),
  'nature-forest': preset('自然森系', '研究绿与浅纸', 'research-organic'),
  'signal-blue': preset('蓝色信号', '技术蓝与严格网格', 'precision-modern'),
  'autumn-warm': preset('秋日暖阳', '橙棕与叙事纸面', 'warm-narrative', {accent: 'oklch(0.65 0.16 52)', paper: 'oklch(0.96 0.034 75)'}),
  'dark-night': preset('深夜暗色', '深墨与紫色信号', 'bold-statement', {paper: 'oklch(0.20 0.028 285)', paperAlt: 'oklch(0.25 0.038 285)', ink: 'oklch(0.92 0.015 280)', muted: 'oklch(0.70 0.045 280)', accent: 'oklch(0.72 0.17 305)', line: 'oklch(0.42 0.06 285)'}, {cover: 'panel-led', list: 'panel-led', media: 'ui-product-led'}, {cover: 'inverse'}),
  morandi: preset('莫兰迪', '低饱和灰粉', 'soft-product', {paper: 'oklch(0.90 0.028 50)', paperAlt: 'oklch(0.85 0.035 330)', ink: 'oklch(0.36 0.025 45)', accent: 'oklch(0.62 0.06 325)'}),
  cyberpunk: preset('赛博朋克', '深紫与青色信号', 'precision-modern', {paper: 'oklch(0.18 0.04 285)', paperAlt: 'oklch(0.24 0.055 285)', ink: 'oklch(0.92 0.025 210)', muted: 'oklch(0.70 0.08 220)', accent: 'oklch(0.78 0.16 195)', line: 'oklch(0.52 0.11 305)'}, {cover: 'panel-led', list: 'panel-led', table: 'panel-led', media: 'ui-product-led'}),
  'neo-brutalism': preset('新野蛮主义', '粗线与高能黄', 'bold-statement', {paper: 'oklch(0.96 0.15 98)', paperAlt: 'oklch(0.88 0.17 94)', accent: 'oklch(0.52 0.21 28)', line: 'oklch(0.20 0.01 60)'}, {cover: 'panel-led', list: 'panel-led', quote: 'panel-led', media: 'ui-product-led'}),
  'film-retro': preset('胶片复古', '褪色纸面与暗红', 'editorial-archive', {paper: 'oklch(0.89 0.045 73)', paperAlt: 'oklch(0.82 0.06 65)', accent: 'oklch(0.48 0.12 32)'}, {cover: 'illustration-led', quote: 'type-led', list: 'type-led'}),
  memphis: preset('孟菲斯', '明快模块与紫橙', 'soft-product', {paper: 'oklch(0.97 0.035 95)', paperAlt: 'oklch(0.91 0.08 330)', accent: 'oklch(0.62 0.18 35)'}, {cover: 'illustration-led', diagram: 'hand-drawn-explainer', media: 'photo-led'}),
  magazine: preset('杂志排版', '栏栅格与编辑节奏', 'editorial-archive', {}, {cover: 'panel-led', heading: 'type-led', list: 'panel-led'}),
  'frosted-soft': preset('磨砂柔光', '低对比产品表面', 'soft-product', {paper: 'oklch(0.96 0.02 235)', paperAlt: 'oklch(0.91 0.035 240)', accent: 'oklch(0.63 0.11 250)'}, {cover: 'panel-led', quote: 'type-led', list: 'type-led', media: 'ui-product-led'}),
  'grid-layout': preset('格子布局', '规则模块与单一强调', 'precision-modern', {}, {cover: 'panel-led', list: 'panel-led', table: 'data-led', media: 'ui-product-led'}),
  y2k: preset('千禧复古', '银紫与数字感', 'soft-product', {paper: 'oklch(0.94 0.035 285)', paperAlt: 'oklch(0.88 0.07 290)', accent: 'oklch(0.62 0.18 310)'}, {cover: 'type-led', list: 'type-led', media: 'ui-product-led'}),
  'pink-gradient': preset('粉色层次', '粉色场与深墨文字', 'soft-product', {paper: 'oklch(0.96 0.035 350)', paperAlt: 'oklch(0.89 0.075 350)', accent: 'oklch(0.62 0.19 355)'}, {cover: 'illustration-led', quote: 'type-led', media: 'photo-led'}),
  'field-notes': preset('田野笔记', '研究与观察', 'research-organic', {accent: 'oklch(0.48 0.11 140)'}, {cover: 'type-led', heading: 'editorial-print-led', diagram: 'hand-drawn-explainer'}),
}

export const DEFAULT_PLAN = {
  schemaVersion: 1,
  mode: 'article',
  presetId: 'current-editorial',
  designLanguage: 'bold-statement',
  palette: {...PRESETS['current-editorial'].palette},
  presentations: {...PRESETS['current-editorial'].presentations},
  treatments: {...PRESETS['current-editorial'].treatments},
  typography: {fontFamily: 'source-han-sans', bodySize: 30, lineHeight: 1.68, characterWidth: 1, pageMargin: 58},
  pageChrome: {showPageNumber: true, showDate: false, date: '', showAuthor: false, author: '507'},
  cover: {title: '', subtitle: '', image: '', author: '507'},
}

export function normalizePlan(input = {}) {
  const presetEntry = PRESETS[input.presetId] || PRESETS['current-editorial']
  const language = DESIGN_LANGUAGES[input.designLanguage] ? input.designLanguage : presetEntry.designLanguage
  const basePalette = input.presetId && PRESETS[input.presetId] ? presetEntry.palette : LANGUAGE_PALETTES[language]
  const basePresentations = input.presetId && PRESETS[input.presetId] ? presetEntry.presentations : PRESENTATIONS[language]
  const presentations = {...basePresentations, ...(input.presentations || {})}
  for (const [kind, supported] of Object.entries(PRESENTATION_SUPPORT)) {
    if (!supported.includes(presentations[kind])) presentations[kind] = supported[0]
  }
  const typography = {...DEFAULT_PLAN.typography, ...(input.typography || {})}
  if (!FONT_FAMILIES[typography.fontFamily]) typography.fontFamily = DEFAULT_PLAN.typography.fontFamily
  if (!Number.isFinite(typography.characterWidth)) typography.characterWidth = DEFAULT_PLAN.typography.characterWidth
  typography.characterWidth = Math.min(1.08, Math.max(0.94, typography.characterWidth))
  return {
    ...DEFAULT_PLAN,
    ...input,
    schemaVersion: 1,
    mode: input.mode === 'summary' ? 'summary' : 'article',
    designLanguage: language,
    palette: {...basePalette, ...(input.palette || {})},
    presentations,
    treatments: {...treatmentFor(language), ...(input.treatments || {})},
    typography,
    pageChrome: {...DEFAULT_PLAN.pageChrome, ...(input.pageChrome || {})},
    cover: {...DEFAULT_PLAN.cover, ...(input.cover || {})},
  }
}

export function fontFamilyFor(plan) {
  return (FONT_FAMILIES[plan.typography?.fontFamily] || FONT_FAMILIES[DEFAULT_PLAN.typography.fontFamily]).cssFamily
}

export function applyPreset(plan, presetId) {
  const presetEntry = PRESETS[presetId]
  if (!presetEntry) return normalizePlan(plan)
  return normalizePlan({
    ...plan,
    presetId,
    designLanguage: presetEntry.designLanguage,
    palette: {...presetEntry.palette},
    presentations: {...presetEntry.presentations},
    treatments: {...presetEntry.treatments},
  })
}

export function applyDesignLanguage(plan, designLanguage) {
  const language = DESIGN_LANGUAGES[designLanguage] ? designLanguage : 'bold-statement'
  return normalizePlan({
    ...plan,
    presetId: null,
    designLanguage: language,
    palette: {...LANGUAGE_PALETTES[language]},
    presentations: {...PRESENTATIONS[language]},
    treatments: treatmentFor(language),
  })
}

export function presentationFor(plan, kind) {
  const supported = PRESENTATION_SUPPORT[kind] || ['type-led']
  const requested = plan.presentations?.[kind]
  return supported.includes(requested) ? requested : supported[0]
}

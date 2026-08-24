import {applyDesignLanguage, applyPreset, COMPONENT_LABELS, DEFAULT_PLAN, DESIGN_LANGUAGES, FONT_FAMILIES, normalizePlan, PRESENTATION_LABELS, PRESENTATION_SUPPORT, PRESETS, RUNTIME_VERSION} from './design-system.js'
import {compileMarkdown} from './markdown.js'
import {paginate} from './paginator.js'
import {enqueueSave} from './save-queue.js'

const query = new URLSearchParams(location.search)
const token = query.get('token') || ''
const exportMode = query.get('export') === '1'
const exportPage = Math.max(1, Number(query.get('page') || 1))
const elements = {
  workbench: document.querySelector('#workbench'),
  content: document.querySelector('#content-input'),
  insertImageButton: document.querySelector('#insert-image-button'),
  contentImageInput: document.querySelector('#content-image-input'),
  saveState: document.querySelector('#save-state'),
  compileState: document.querySelector('#compile-state'),
  pageSummary: document.querySelector('#page-summary'),
  previewGrid: document.querySelector('#preview-grid'),
  measureRoot: document.querySelector('#measure-root'),
  presetGrid: document.querySelector('#preset-grid'),
  mode: document.querySelector('#mode-select'),
  language: document.querySelector('#language-select'),
  languageDescription: document.querySelector('#language-description'),
  presentationControls: document.querySelector('#presentation-controls'),
  fontFamily: document.querySelector('#font-family-select'),
  fontFamilyDescription: document.querySelector('#font-family-description'),
  bodySize: document.querySelector('#body-size'),
  bodySizeOutput: document.querySelector('#body-size-output'),
  lineHeight: document.querySelector('#line-height'),
  lineHeightOutput: document.querySelector('#line-height-output'),
  characterWidth: document.querySelector('#character-width'),
  characterWidthOutput: document.querySelector('#character-width-output'),
  pageMargin: document.querySelector('#page-margin'),
  pageMarginOutput: document.querySelector('#page-margin-output'),
  showPageNumber: document.querySelector('#show-page-number'),
  showDate: document.querySelector('#show-date'),
  showAuthor: document.querySelector('#show-author'),
  coverTitle: document.querySelector('#cover-title'),
  coverSubtitle: document.querySelector('#cover-subtitle'),
  coverImage: document.querySelector('#cover-image'),
  coverUploadButton: document.querySelector('#cover-upload-button'),
  coverImageInput: document.querySelector('#cover-image-input'),
  exportFormat: document.querySelector('#export-format'),
  exportButton: document.querySelector('#export-button'),
  exportStatus: document.querySelector('#export-status'),
  toast: document.querySelector('#toast'),
}

let content = ''
let plan = normalizePlan(DEFAULT_PLAN)
let currentArtifact = null
let projectIdentity = {runtimeSha256: '', assetSetSha256: '', fontSet: ''}
let renderRevision = 0
let renderTimer = null
let toastTimer = null
let saveInFlight = Promise.resolve()

function api(path, options = {}) {
  const headers = {'Content-Type': 'application/json', 'X-Rednote-Token': token, ...(options.headers || {})}
  return fetch(path, {...options, headers}).then(async response => {
    const payload = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(payload.error || `请求失败：${response.status}`)
    return payload
  })
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`
  return JSON.stringify(value)
}

async function sha256Text(value) {
  const data = new TextEncoder().encode(value)
  const digest = await crypto.subtle.digest('SHA-256', data)
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, '0')).join('')
}

function setSaveState(label, state = '') {
  elements.saveState.textContent = label
  elements.saveState.dataset.state = state
}

function toast(message) {
  elements.toast.textContent = message
  elements.toast.classList.add('visible')
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => elements.toast.classList.remove('visible'), 2600)
}

function debounceRender(delay = 220) {
  clearTimeout(renderTimer)
  renderTimer = setTimeout(() => renderProject({persist: true}), delay)
}

function fileDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error('读取图片失败'))
    reader.readAsDataURL(file)
  })
}

async function uploadImage(file, button) {
  if (!file) return null
  button.disabled = true
  const previous = button.textContent
  button.textContent = '上传中…'
  try {
    const dataUrl = await fileDataUrl(file)
    const result = await api('/api/upload-image', {method: 'POST', body: JSON.stringify({fileName: file.name, dataUrl})})
    projectIdentity.assetSetSha256 = result.assetSetSha256
    return result
  } finally {
    button.disabled = false
    button.textContent = previous
  }
}

function insertMarkdownImage(path, alt) {
  const input = elements.content
  const safeAlt = String(alt || '图片').replace(/[\[\]]/g, '')
  const prefix = input.selectionStart > 0 && !input.value.slice(0, input.selectionStart).endsWith('\n\n') ? '\n\n' : ''
  const suffix = input.selectionEnd < input.value.length && !input.value.slice(input.selectionEnd).startsWith('\n\n') ? '\n\n' : '\n'
  input.setRangeText(`${prefix}![${safeAlt}](${path})${suffix}`, input.selectionStart, input.selectionEnd, 'end')
  input.dispatchEvent(new Event('input', {bubbles: true}))
  input.focus()
}

function renderPresets() {
  elements.presetGrid.replaceChildren()
  for (const [id, preset] of Object.entries(PRESETS)) {
    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'preset-button'
    button.style.setProperty('--preset-bg', preset.swatch.background)
    button.style.setProperty('--preset-ink', preset.swatch.color)
    button.setAttribute('aria-pressed', String(plan.presetId === id))
    const title = document.createElement('strong')
    title.textContent = preset.label
    const caption = document.createElement('span')
    caption.textContent = `${DESIGN_LANGUAGES[preset.designLanguage].label} · ${preset.caption}`
    button.append(title, caption)
    button.addEventListener('click', () => {
      plan = applyPreset(plan, id)
      syncControls()
      debounceRender(0)
    })
    elements.presetGrid.append(button)
  }
}

function renderLanguages() {
  elements.language.replaceChildren()
  for (const [id, language] of Object.entries(DESIGN_LANGUAGES)) {
    const option = document.createElement('option')
    option.value = id
    option.textContent = language.label
    elements.language.append(option)
  }
}

function renderFontFamilies() {
  elements.fontFamily.replaceChildren()
  for (const [id, font] of Object.entries(FONT_FAMILIES)) {
    const option = document.createElement('option')
    option.value = id
    option.textContent = `${font.label} · OFL`
    elements.fontFamily.append(option)
  }
}

function renderPresentationControls() {
  elements.presentationControls.replaceChildren()
  for (const [kind, supported] of Object.entries(PRESENTATION_SUPPORT)) {
    if (supported.length < 2) continue
    const label = document.createElement('label')
    label.textContent = COMPONENT_LABELS[kind] || kind
    const select = document.createElement('select')
    select.dataset.componentKind = kind
    for (const presentation of supported) {
      const option = document.createElement('option')
      option.value = presentation
      option.textContent = PRESENTATION_LABELS[presentation] || presentation
      select.append(option)
    }
    select.value = plan.presentations[kind]
    select.addEventListener('change', () => {
      plan.presetId = null
      plan.presentations[kind] = select.value
      renderPresets()
      debounceRender(0)
    })
    label.append(select)
    elements.presentationControls.append(label)
  }
}

function syncControls() {
  renderPresets()
  elements.mode.value = plan.mode
  elements.language.value = plan.designLanguage
  elements.languageDescription.textContent = DESIGN_LANGUAGES[plan.designLanguage]?.description || ''
  renderPresentationControls()
  elements.fontFamily.value = plan.typography.fontFamily
  elements.fontFamilyDescription.textContent = FONT_FAMILIES[plan.typography.fontFamily]?.description || ''
  elements.bodySize.value = String(plan.typography.bodySize)
  elements.bodySizeOutput.value = `${plan.typography.bodySize}px`
  elements.lineHeight.value = String(plan.typography.lineHeight)
  elements.lineHeightOutput.value = String(plan.typography.lineHeight)
  elements.characterWidth.value = String(plan.typography.characterWidth)
  elements.characterWidthOutput.value = `${Math.round(plan.typography.characterWidth * 100)}%`
  elements.pageMargin.value = String(plan.typography.pageMargin)
  elements.pageMarginOutput.value = `${plan.typography.pageMargin}px`
  elements.showPageNumber.checked = Boolean(plan.pageChrome.showPageNumber)
  elements.showDate.checked = Boolean(plan.pageChrome.showDate)
  elements.showAuthor.checked = Boolean(plan.pageChrome.showAuthor)
  elements.coverTitle.value = plan.cover.title || ''
  elements.coverSubtitle.value = plan.cover.subtitle || ''
  elements.coverImage.value = plan.cover.image || ''
}

function updatePreviewScale() {
  for (const frame of elements.previewGrid.querySelectorAll('.page-frame')) {
    const scaler = frame.querySelector('.page-scaler')
    const scale = frame.clientWidth / 750
    scaler.style.width = '750px'
    scaler.style.height = '1000px'
    scaler.style.transform = `scale(${scale})`
  }
}

const resizeObserver = new ResizeObserver(updatePreviewScale)
resizeObserver.observe(elements.previewGrid)

function renderPreview(pages) {
  elements.previewGrid.replaceChildren()
  for (const page of pages) {
    const frame = document.createElement('div')
    frame.className = 'page-frame'
    const scaler = document.createElement('div')
    scaler.className = 'page-scaler'
    scaler.append(page.cloneNode(true))
    frame.append(scaler)
    elements.previewGrid.append(frame)
  }
  requestAnimationFrame(updatePreviewScale)
}

async function waitForImages(root) {
  const images = [...root.querySelectorAll('img')]
  await Promise.all(images.map(image => image.complete ? Promise.resolve() : image.decode().catch(() => undefined)))
}

async function waitForSelectedFont() {
  const font = FONT_FAMILIES[plan.typography.fontFamily]
  if (!font) throw new Error('当前字体配置无效')
  const sample = '字体许可与分页 Aa 123'
  const loaded = await document.fonts.load(`400 30px "${font.face}"`, sample)
  if (!loaded.length) throw new Error(`${font.label} 本地字体加载失败`)
}

function validateSummary(compiled, pages) {
  if (plan.mode !== 'summary') return []
  const issues = []
  const sections = new Map()
  for (const component of compiled.components) {
    if (component.kind === 'page-break') continue
    const entry = sections.get(component.sectionIndex) || {headings: 0, componentIds: []}
    if (component.kind === 'heading') entry.headings += 1
    entry.componentIds.push(component.id)
    sections.set(component.sectionIndex, entry)
  }
  const pageBySection = new Map()
  for (const page of pages.filter(item => item.role === 'body')) {
    const sectionIds = [...new Set(page.fragments.map(fragment => fragment.sectionIndex).filter(value => Number.isInteger(value)))]
    if (sectionIds.length > 1) issues.push(`${page.id} 混入多个摘要段落`)
    for (const sectionId of sectionIds) {
      const pageIds = pageBySection.get(sectionId) || new Set()
      pageIds.add(page.id)
      pageBySection.set(sectionId, pageIds)
    }
  }
  for (const [sectionId, entry] of sections) {
    if (!entry.componentIds.length) continue
    if (entry.headings !== 1) issues.push(`摘要段落 ${sectionId + 1} 必须且只能有一个标题`)
    const pageIds = pageBySection.get(sectionId) || new Set()
    if (pageIds.size !== 1) issues.push(`摘要段落 ${sectionId + 1} 必须完整落在一页`)
  }
  if (sections.size < 1) issues.push('视觉摘要至少需要一个正文观点')
  return issues
}

async function persistState(artifact) {
  setSaveState('正在保存')
  saveInFlight = enqueueSave(saveInFlight, async () => {
    await Promise.all([
      api('/api/content', {method: 'POST', body: JSON.stringify({content})}),
      api('/api/visual-plan', {method: 'POST', body: JSON.stringify({visualPlan: plan})}),
    ])
    await api('/api/paged-content', {method: 'POST', body: JSON.stringify({pagedContent: artifact})})
  })
  try {
    await saveInFlight
    setSaveState('已自动保存', 'saved')
  } catch (error) {
    setSaveState('保存失败', 'error')
    throw error
  }
}

async function renderProject({persist = false} = {}) {
  const revision = ++renderRevision
  elements.compileState.dataset.state = ''
  elements.pageSummary.textContent = '正在真实分页'
  try {
    plan = normalizePlan(plan)
    const compiled = compileMarkdown(content, plan)
    let result = paginate(compiled, plan, elements.measureRoot)
    await document.fonts.ready
    await waitForSelectedFont()
    await waitForImages(elements.measureRoot)
    if (revision !== renderRevision) return
    result = paginate(compiled, plan, elements.measureRoot)
    if (revision !== renderRevision) return

    const [contentSha256, visualPlanSha256] = await Promise.all([
      sha256Text(content), sha256Text(stableJson(plan)),
    ])
    const overflowPages = result.pageArtifacts.filter(page => page.validation.overflow)
    const summaryIssues = validateSummary(compiled, result.pageArtifacts)
    const artifact = {
      schemaVersion: 1,
      status: overflowPages.length || summaryIssues.length ? 'invalid' : 'compiled',
      mode: plan.mode,
      inputs: {
        contentSha256,
        visualPlanSha256,
        runtimeVersion: RUNTIME_VERSION,
        runtimeSha256: projectIdentity.runtimeSha256,
        assetSetSha256: projectIdentity.assetSetSha256,
        fontSet: projectIdentity.fontSet,
      },
      canvas: {width: 1500, height: 2000, cssWidth: 750, cssHeight: 1000},
      pageCount: result.pages.length,
      pages: result.pageArtifacts,
      validationIssues: summaryIssues,
    }
    currentArtifact = artifact
    renderPreview(result.pages)
    elements.pageSummary.textContent = `${artifact.pageCount} 页 · 1500×2000 · ${DESIGN_LANGUAGES[plan.designLanguage].label}`
    elements.compileState.dataset.state = overflowPages.length || summaryIssues.length ? 'error' : 'ready'
    elements.compileState.title = overflowPages.length ? `${overflowPages.length} 页存在溢出` : summaryIssues.length ? summaryIssues.join('；') : '分页已编译'
    elements.exportButton.disabled = Boolean(overflowPages.length || summaryIssues.length)
    window.__REDNOTE_READY__ = {
      pageCount: result.pages.length,
      status: artifact.status,
      mode: plan.mode,
      fontFamily: plan.typography.fontFamily,
      characterWidth: plan.typography.characterWidth,
    }
    document.documentElement.dataset.renderReady = artifact.status
    if (overflowPages.length) toast(`第 ${overflowPages.map(page => Number(page.id.slice(-3))).join('、')} 页存在溢出，已停止导出`)
    else if (summaryIssues.length) toast(summaryIssues[0])
    if (persist && !exportMode) await persistState(artifact)

    if (exportMode) {
      document.body.classList.add('export-mode')
      result.pages.forEach((page, index) => page.classList.toggle('export-target', index + 1 === exportPage))
      window.__REDNOTE_READY__ = {
        pageCount: result.pages.length,
        target: exportPage,
        status: artifact.status,
        mode: plan.mode,
        fontFamily: plan.typography.fontFamily,
        characterWidth: plan.typography.characterWidth,
      }
      document.documentElement.dataset.renderReady = artifact.status
    }
  } catch (error) {
    elements.compileState.dataset.state = 'error'
    elements.pageSummary.textContent = '分页失败'
    elements.exportButton.disabled = true
    setSaveState('渲染失败', 'error')
    toast(error.message)
    window.__REDNOTE_READY__ = {status: 'error', error: error.message}
    document.documentElement.dataset.renderReady = 'error'
    console.error(error)
  }
}

function bindControls() {
  elements.content.addEventListener('input', () => {
    content = elements.content.value
    setSaveState('有新改动')
    debounceRender()
  })
  elements.mode.addEventListener('change', () => {
    plan.mode = elements.mode.value === 'summary' ? 'summary' : 'article'
    debounceRender(0)
  })
  elements.language.addEventListener('change', () => {
    plan = applyDesignLanguage(plan, elements.language.value)
    syncControls()
    debounceRender(0)
  })
  elements.fontFamily.addEventListener('change', () => {
    plan.typography.fontFamily = elements.fontFamily.value
    syncControls()
    debounceRender(0)
  })
  elements.insertImageButton.addEventListener('click', () => elements.contentImageInput.click())
  elements.contentImageInput.addEventListener('change', async () => {
    const file = elements.contentImageInput.files?.[0]
    try {
      const uploaded = await uploadImage(file, elements.insertImageButton)
      if (uploaded) {
        insertMarkdownImage(uploaded.path, uploaded.alt)
        toast('图片已上传并插入平台稿')
      }
    } catch (error) {
      toast(error.message)
    } finally {
      elements.contentImageInput.value = ''
    }
  })
  for (const [element, key, transform] of [
    [elements.bodySize, 'bodySize', Number], [elements.lineHeight, 'lineHeight', Number],
    [elements.characterWidth, 'characterWidth', Number], [elements.pageMargin, 'pageMargin', Number],
  ]) {
    element.addEventListener('input', () => {
      plan.typography[key] = transform(element.value)
      syncControls()
      debounceRender()
    })
  }
  for (const [element, key] of [
    [elements.showPageNumber, 'showPageNumber'], [elements.showDate, 'showDate'], [elements.showAuthor, 'showAuthor'],
  ]) {
    element.addEventListener('change', () => {
      plan.pageChrome[key] = element.checked
      debounceRender(0)
    })
  }
  for (const [element, key] of [
    [elements.coverTitle, 'title'], [elements.coverSubtitle, 'subtitle'],
  ]) {
    element.addEventListener('input', () => {
      plan.cover[key] = element.value
      debounceRender()
    })
  }
  elements.coverUploadButton.addEventListener('click', () => elements.coverImageInput.click())
  elements.coverImageInput.addEventListener('change', async () => {
    const file = elements.coverImageInput.files?.[0]
    try {
      const uploaded = await uploadImage(file, elements.coverUploadButton)
      if (uploaded) {
        plan.cover.image = uploaded.path
        syncControls()
        debounceRender(0)
        toast('封面图片已上传')
      }
    } catch (error) {
      toast(error.message)
    } finally {
      elements.coverImageInput.value = ''
    }
  })
  document.querySelector('#toggle-left').addEventListener('click', () => elements.workbench.classList.toggle('left-collapsed'))
  document.querySelector('#toggle-right').addEventListener('click', () => elements.workbench.classList.toggle('right-collapsed'))
  elements.exportButton.addEventListener('click', async () => {
    if (!currentArtifact || currentArtifact.status !== 'compiled') return
    elements.exportButton.disabled = true
    elements.exportStatus.textContent = '正在从当前 DOM 导出…'
    try {
      const result = await api('/api/export', {method: 'POST', body: JSON.stringify({format: elements.exportFormat.value})})
      elements.exportStatus.textContent = `已导出 ${result.pageCount} 页：${result.outputDir}`
      toast('导出完成')
    } catch (error) {
      elements.exportStatus.textContent = error.message
      toast(error.message)
    } finally {
      elements.exportButton.disabled = currentArtifact?.status !== 'compiled'
    }
  })
}

async function init() {
  if (location.protocol === 'file:') {
    document.body.classList.add('file-mode')
    document.querySelector('#file-mode-help').hidden = false
    return
  }
  if (!token) throw new Error('缺少本地工作台访问令牌')
  if (innerWidth < 700) elements.workbench.classList.add('left-collapsed', 'right-collapsed')
  else if (innerWidth < 980) elements.workbench.classList.add('right-collapsed')
  const project = await api('/api/project')
  projectIdentity = {
    runtimeSha256: project.runtimeSha256 || '',
    assetSetSha256: project.assetSetSha256 || '',
    fontSet: project.fontSet || '',
  }
  content = project.content || ''
  plan = normalizePlan(project.visualPlan || DEFAULT_PLAN)
  elements.content.value = content
  renderLanguages()
  renderFontFamilies()
  syncControls()
  bindControls()
  await renderProject({persist: !exportMode})
  if (!exportMode) setSaveState('已从文件载入', 'saved')
}

init().catch(error => {
  setSaveState('载入失败', 'error')
  elements.pageSummary.textContent = error.message
  toast(error.message)
  window.__REDNOTE_READY__ = {status: 'error', error: error.message}
})

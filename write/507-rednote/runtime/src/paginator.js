import {projectAssetUrl} from './asset-url.js'
import {fontFamilyFor, presentationFor} from './design-system.js'

function pageStyle(page, plan) {
  page.dataset.language = plan.designLanguage
  page.style.setProperty('--body-size', `${plan.typography.bodySize}px`)
  page.style.setProperty('--line-height', String(plan.typography.lineHeight))
  page.style.setProperty('--text-font', fontFamilyFor(plan))
  const spacing = Math.abs(plan.typography.characterWidth - 1) < 0.0005 ? 0 : plan.typography.characterWidth - 1
  page.style.setProperty('--character-spacing', `${spacing.toFixed(3)}em`)
  page.style.setProperty('--page-margin', `${plan.typography.pageMargin}px`)
  const paletteVariables = {paper: '--paper', paperAlt: '--paper-alt', ink: '--ink', muted: '--muted', accent: '--accent', line: '--line'}
  for (const [key, variable] of Object.entries(paletteVariables)) {
    if (plan.palette?.[key]) page.style.setProperty(variable, plan.palette[key])
  }
  const hasTopChrome = plan.pageChrome.showDate || plan.pageChrome.showPageNumber
  const hasBottomChrome = plan.pageChrome.showAuthor
  page.style.setProperty('--page-top', `${hasTopChrome ? Math.max(68, plan.typography.pageMargin) : plan.typography.pageMargin}px`)
  page.style.setProperty('--page-bottom', `${hasBottomChrome ? Math.max(58, plan.typography.pageMargin) : plan.typography.pageMargin}px`)
}

function createCover(plan, compiled) {
  const page = document.createElement('article')
  page.className = 'rednote-page cover-page'
  page.dataset.role = 'cover'
  page.dataset.presentation = presentationFor(plan, 'cover')
  page.dataset.treatment = plan.treatments?.cover || 'default'
  pageStyle(page, plan)
  const art = document.createElement('div')
  art.className = 'cover-art'
  const coverImage = projectAssetUrl(plan.cover.image)
  if (coverImage) {
    const image = document.createElement('img')
    image.src = coverImage
    image.alt = ''
    art.append(image)
  }
  const copy = document.createElement('div')
  copy.className = 'cover-copy'
  const kicker = document.createElement('p')
  kicker.className = 'cover-kicker'
  kicker.textContent = plan.cover.author || plan.pageChrome.author || '507'
  const title = document.createElement('h1')
  title.className = 'cover-title'
  title.textContent = plan.cover.title || compiled.title || '未命名作品'
  const subtitle = document.createElement('p')
  subtitle.className = 'cover-subtitle'
  subtitle.textContent = plan.cover.subtitle || ''
  copy.append(kicker, title)
  if (subtitle.textContent) copy.append(subtitle)
  page.append(art, copy)
  page.__fragments = [{
    componentId: 'cover-title', type: 'cover', part: 'whole', node: copy,
    sourceRange: compiled.titleSourceRange || {start: 0, end: 0},
    visibleText: [title.textContent, subtitle.textContent].filter(Boolean).join('\n'), repeated: false,
  }]
  return page
}

function createBodyPage(plan, index) {
  const page = document.createElement('article')
  page.className = 'rednote-page body-page'
  page.dataset.role = 'body'
  page.dataset.pageNumber = String(index)
  pageStyle(page, plan)
  if (plan.pageChrome.showDate || plan.pageChrome.showPageNumber) {
    const chrome = document.createElement('div')
    chrome.className = 'page-chrome'
    const date = document.createElement('span')
    date.textContent = plan.pageChrome.showDate ? (plan.pageChrome.date || '') : ''
    const number = document.createElement('span')
    number.className = 'page-number'
    number.textContent = plan.pageChrome.showPageNumber ? String(index).padStart(2, '0') : ''
    chrome.append(date, number)
    page.append(chrome)
  }
  if (plan.pageChrome.showAuthor) {
    const author = document.createElement('div')
    author.className = 'page-author'
    author.textContent = plan.pageChrome.author || plan.cover.author || ''
    page.append(author)
  }
  const content = document.createElement('div')
  content.className = 'page-content'
  page.append(content)
  page.__content = content
  page.__fragments = []
  page.__breakKind = 'natural'
  return page
}

function fits(page) {
  const content = page.__content
  return content.scrollHeight <= content.clientHeight + 0.5
}

function cloneTextRange(element, start, end) {
  const clone = element.cloneNode(true)
  const walker = document.createTreeWalker(clone, NodeFilter.SHOW_TEXT)
  const nodes = []
  while (walker.nextNode()) nodes.push(walker.currentNode)
  let cursor = 0
  for (const node of nodes) {
    const nodeStart = cursor
    const nodeEnd = cursor + node.data.length
    cursor = nodeEnd
    if (nodeEnd <= start || nodeStart >= end) {
      node.data = ''
      continue
    }
    const from = Math.max(0, start - nodeStart)
    const to = Math.min(node.data.length, end - nodeStart)
    node.data = node.data.slice(from, to)
  }
  clone.querySelectorAll('a').forEach(anchor => {
    if (!anchor.textContent.trim()) anchor.remove()
  })
  return clone
}

function preferredBreak(text, start, candidate) {
  if (candidate >= text.length) return text.length
  const floor = Math.max(start + 1, candidate - 32)
  for (let index = candidate; index >= floor; index -= 1) {
    if (/[\s，。！？；：、,.!?;:）】》”’]/u.test(text[index - 1] || '')) return index
  }
  return candidate
}

function maxTextThatFits(page, element, start) {
  const text = element.textContent || ''
  let low = start + 1
  let high = text.length
  let best = start
  while (low <= high) {
    const middle = Math.floor((low + high) / 2)
    const probe = cloneTextRange(element, start, middle)
    page.__content.append(probe)
    const okay = fits(page)
    probe.remove()
    if (okay) {
      best = middle
      low = middle + 1
    } else {
      high = middle - 1
    }
  }
  return preferredBreak(text, start, best)
}

function fragment(component, node, part, visibleText, extra = {}) {
  return {
    componentId: component.id,
    type: component.kind,
    part,
    node,
    sourceRange: component.sourceRange,
    sectionIndex: component.sectionIndex,
    visibleText: visibleText.trim(),
    repeated: false,
    ...extra,
  }
}

function appendWhole(page, component, element, part = 'whole', extra = {}) {
  page.__content.append(element)
  if (!fits(page)) element.dataset.overflow = 'true'
  page.__fragments.push(fragment(component, element, part, element.textContent || '', extra))
}

function splitTextComponent(component, element, state) {
  const text = element.textContent || ''
  let start = 0
  let partIndex = 0
  while (start < text.length) {
    let page = state.current()
    let end = maxTextThatFits(page, element, start)
    if (end <= start && page.__content.children.length) {
      page = state.next('component-continuation')
      end = maxTextThatFits(page, element, start)
    }
    if (end <= start) {
      const fallback = cloneTextRange(element, start, text.length)
      fallback.dataset.overflow = 'true'
      appendWhole(page, component, fallback, partIndex ? 'end' : 'whole', {visibleRange: {start, end: text.length}})
      return
    }
    const slice = cloneTextRange(element, start, end)
    const remaining = end < text.length
    const part = !partIndex && !remaining ? 'whole' : !partIndex ? 'start' : remaining ? 'middle' : 'end'
    appendWhole(page, component, slice, part, {visibleRange: {start, end}})
    start = end
    partIndex += 1
    if (remaining) state.next('component-continuation')
  }
}

function splitCode(component, element, state) {
  const lines = (element.querySelector('code')?.textContent || element.textContent || '').split('\n')
  let cursor = 0
  while (cursor < lines.length) {
    let page = state.current()
    const outer = element.cloneNode(false)
    const pre = document.createElement('pre')
    const code = document.createElement('code')
    pre.append(code)
    outer.append(pre)
    let accepted = 0
    while (cursor + accepted < lines.length) {
      code.textContent = lines.slice(cursor, cursor + accepted + 1).join('\n')
      page.__content.append(outer)
      const okay = fits(page)
      outer.remove()
      if (!okay) break
      accepted += 1
    }
    if (!accepted && page.__content.children.length) {
      state.next('component-continuation')
      continue
    }
    accepted = Math.max(1, accepted)
    code.textContent = lines.slice(cursor, cursor + accepted).join('\n')
    const remaining = cursor + accepted < lines.length
    const part = cursor === 0 ? (remaining ? 'start' : 'whole') : (remaining ? 'middle' : 'end')
    appendWhole(page, component, outer, part, {lineRange: {start: cursor, end: cursor + accepted}})
    cursor += accepted
    if (remaining) state.next('component-continuation')
  }
}

function splitList(component, element, state) {
  const sourceList = element.querySelector('ul,ol')
  if (!sourceList) return splitTextComponent(component, element, state)
  const items = [...sourceList.children]
  let cursor = 0
  while (cursor < items.length) {
    let page = state.current()
    const outer = element.cloneNode(false)
    const list = sourceList.cloneNode(false)
    if (sourceList.tagName === 'OL') list.start = cursor + 1
    outer.append(list)
    let accepted = 0
    while (cursor + accepted < items.length) {
      list.append(items[cursor + accepted].cloneNode(true))
      page.__content.append(outer)
      const okay = fits(page)
      outer.remove()
      if (!okay) {
        list.lastElementChild?.remove()
        break
      }
      accepted += 1
    }
    if (!accepted && page.__content.children.length) {
      state.next('component-continuation')
      continue
    }
    if (!accepted) {
      list.append(items[cursor].cloneNode(true))
      accepted = 1
      outer.dataset.overflow = fits(page) ? 'false' : 'true'
    }
    const remaining = cursor + accepted < items.length
    const part = cursor === 0 ? (remaining ? 'start' : 'whole') : (remaining ? 'middle' : 'end')
    appendWhole(page, component, outer, part, {itemRange: {start: cursor, end: cursor + accepted}})
    cursor += accepted
    if (remaining) state.next('component-continuation')
  }
}

function splitTable(component, element, state) {
  const sourceTable = element.querySelector('table')
  if (!sourceTable) return splitTextComponent(component, element, state)
  const header = sourceTable.querySelector('thead')
  const rows = [...sourceTable.querySelectorAll('tbody tr')]
  let cursor = 0
  while (cursor < rows.length) {
    let page = state.current()
    const outer = element.cloneNode(false)
    const table = sourceTable.cloneNode(false)
    if (header) table.append(header.cloneNode(true))
    const body = document.createElement('tbody')
    table.append(body)
    outer.append(table)
    let accepted = 0
    while (cursor + accepted < rows.length) {
      body.append(rows[cursor + accepted].cloneNode(true))
      page.__content.append(outer)
      const okay = fits(page)
      outer.remove()
      if (!okay) {
        body.lastElementChild?.remove()
        break
      }
      accepted += 1
    }
    if (!accepted && page.__content.children.length) {
      state.next('component-continuation')
      continue
    }
    if (!accepted) {
      body.append(rows[cursor].cloneNode(true))
      accepted = 1
      outer.dataset.overflow = fits(page) ? 'false' : 'true'
    }
    const remaining = cursor + accepted < rows.length
    const part = cursor === 0 ? (remaining ? 'start' : 'whole') : (remaining ? 'middle' : 'end')
    appendWhole(page, component, outer, part, {rowRange: {start: cursor, end: cursor + accepted}, repeatedHeader: cursor > 0})
    cursor += accepted
    if (remaining) state.next('component-continuation')
  }
}

function appendAtomic(component, element, state) {
  let page = state.current()
  page.__content.append(element)
  if (!fits(page) && page.__content.children.length > 1) {
    element.remove()
    page = state.next('natural')
    page.__content.append(element)
  }
  if (!fits(page)) {
    const available = page.__content.clientHeight - 8
    const media = element.querySelector('img,svg')
    if (media) media.style.maxHeight = `${available}px`
  }
  if (!fits(page)) element.dataset.overflow = 'true'
  page.__fragments.push(fragment(component, element, 'whole', element.textContent || '', {atomic: true}))
}

function geometry(page, node) {
  const pageRect = page.getBoundingClientRect()
  const rect = node.getBoundingClientRect()
  return {
    x: Math.round((rect.left - pageRect.left) * 100) / 100,
    y: Math.round((rect.top - pageRect.top) * 100) / 100,
    width: Math.round(rect.width * 100) / 100,
    height: Math.round(rect.height * 100) / 100,
  }
}

function pageArtifact(page, index) {
  const fragments = page.__fragments.map(item => {
    const {node, ...serializable} = item
    return {...serializable, geometry: geometry(page, node)}
  })
  const sourceRanges = fragments.filter(item => !item.repeated && item.sourceRange?.end > item.sourceRange?.start).map(item => item.sourceRange)
  const content = page.__content
  const overflow = content ? content.scrollHeight > content.clientHeight + 0.5 || Boolean(page.querySelector('[data-overflow="true"]')) : false
  const contentRect = content?.getBoundingClientRect()
  const pageRect = page.getBoundingClientRect()
  const maxBottom = fragments.length ? Math.max(...fragments.map(item => item.geometry.y + item.geometry.height)) : 0
  const chromeText = [...page.querySelectorAll('.page-chrome,.page-author')].map(node => node.textContent.trim()).filter(Boolean)
  return {
    id: `page-${String(index + 1).padStart(3, '0')}`,
    role: page.dataset.role,
    break: {kind: page.__breakKind || 'natural'},
    sourceRange: sourceRanges.length ? {start: Math.min(...sourceRanges.map(item => item.start)), end: Math.max(...sourceRanges.map(item => item.end))} : {start: 0, end: 0},
    contentText: fragments.map(item => item.visibleText).filter(Boolean).join('\n'),
    chromeText,
    fragments,
    validation: {
      overflow,
      maxBottom: Math.round(maxBottom * 100) / 100,
      contentHeight: contentRect ? Math.round(contentRect.height * 100) / 100 : Math.round(pageRect.height * 100) / 100,
    },
  }
}

export function paginate(compiled, plan, measureRoot) {
  measureRoot.replaceChildren()
  const pages = [createCover(plan, compiled)]
  measureRoot.append(pages[0])
  let bodyPageNumber = 1
  let currentPage = createBodyPage(plan, bodyPageNumber)
  pages.push(currentPage)
  measureRoot.append(currentPage)

  const state = {
    current: () => currentPage,
    next: breakKind => {
      bodyPageNumber += 1
      currentPage = createBodyPage(plan, bodyPageNumber)
      currentPage.__breakKind = breakKind
      pages.push(currentPage)
      measureRoot.append(currentPage)
      return currentPage
    },
  }

  for (let index = 0; index < compiled.components.length; index += 1) {
    const component = compiled.components[index]
    if (component.kind === 'page-break') {
      if (state.current().__content.children.length) state.next('forced')
      else state.current().__breakKind = 'forced'
      continue
    }
    const element = compiled.createElement(component)
    if (component.kind === 'heading') {
      const page = state.current()
      page.__content.append(element)
      const nextComponent = compiled.components[index + 1]
      let keep = true
      if (nextComponent && nextComponent.kind !== 'page-break') {
        const probe = compiled.createElement(nextComponent)
        const probeText = probe.textContent || ''
        const shortProbe = probeText.length > 24 ? cloneTextRange(probe, 0, 24) : probe
        page.__content.append(shortProbe)
        keep = fits(page)
        shortProbe.remove()
      } else keep = fits(page)
      element.remove()
      if (!keep && page.__content.children.length) state.next('natural')
      appendWhole(state.current(), component, element)
      continue
    }

    const page = state.current()
    page.__content.append(element)
    const wholeFits = fits(page)
    element.remove()
    if (wholeFits) {
      appendWhole(page, component, element)
      continue
    }

    if (component.kind === 'code') splitCode(component, element, state)
    else if (component.kind === 'list') splitList(component, element, state)
    else if (component.kind === 'table') splitTable(component, element, state)
    else if (['media', 'diagram', 'hr'].includes(component.kind)) appendAtomic(component, element, state)
    else splitTextComponent(component, element, state)
  }

  if (pages.length > 2 && !pages.at(-1).__content.children.length) {
    pages.pop().remove()
  }
  pages.forEach((page, index) => {
    page.dataset.pageId = `page-${String(index + 1).padStart(3, '0')}`
  })
  return {pages, pageArtifacts: pages.map(pageArtifact)}
}

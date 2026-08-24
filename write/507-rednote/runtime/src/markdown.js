import DOMPurify from 'dompurify'
import {marked} from 'marked'
import {projectAssetUrl} from './asset-url.js'
import {renderFlowchart} from './flowchart.js'
import {presentationFor} from './design-system.js'

const PAGE_BREAK = '<!-- rednote:page-break -->'

marked.setOptions({gfm: true, breaks: false})

function sanitizeHtml(value) {
  return DOMPurify.sanitize(value, {
    USE_PROFILES: {html: true},
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form'],
    FORBID_ATTR: ['style', 'onerror', 'onclick', 'onload'],
  })
}

function inferKind(token) {
  const mapping = {
    heading: 'heading', paragraph: 'paragraph', blockquote: 'quote', list: 'list',
    code: 'code', table: 'table', hr: 'hr', html: 'paragraph', text: 'paragraph',
  }
  return mapping[token.type] || 'paragraph'
}

function stripFrontmatter(content) {
  if (!content.startsWith('---\n') && !content.startsWith('---\r\n')) return {body: content, offset: 0}
  const match = content.match(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/)
  return match ? {body: content.slice(match[0].length), offset: match[0].length} : {body: content, offset: 0}
}

function splitByPageBreak(content, baseOffset) {
  const segments = []
  let cursor = 0
  while (cursor <= content.length) {
    const next = content.indexOf(PAGE_BREAK, cursor)
    if (next < 0) {
      segments.push({text: content.slice(cursor), start: baseOffset + cursor, breakAfter: false})
      break
    }
    segments.push({text: content.slice(cursor, next), start: baseOffset + cursor, breakAfter: true, directiveStart: baseOffset + next})
    cursor = next + PAGE_BREAK.length
  }
  return segments
}

function normalizeRenderedElement(wrapper, kind) {
  wrapper.querySelectorAll('a').forEach(anchor => {
    const href = anchor.getAttribute('href') || ''
    if (!href) return
    anchor.setAttribute('rel', 'noreferrer')
    if (anchor.textContent.trim() !== href) {
      const url = document.createElement('span')
      url.className = 'expanded-url'
      url.textContent = `（${href}）`
      anchor.after(url)
    }
  })
  wrapper.querySelectorAll('img').forEach(image => {
    const original = image.getAttribute('src') || ''
    const resolved = projectAssetUrl(original)
    if (!resolved) {
      const fallback = document.createElement('p')
      fallback.textContent = `[远程图片未加载：${image.getAttribute('alt') || original}]`
      image.replaceWith(fallback)
      return
    }
    image.setAttribute('src', resolved)
    image.setAttribute('loading', 'eager')
  })
  if (kind === 'paragraph' && wrapper.querySelector('img') && !wrapper.textContent.trim()) return 'media'
  return kind
}

function buildComponentElement(component, plan) {
  const outer = document.createElement(component.kind === 'media' ? 'figure' : 'section')
  outer.className = 'semantic-component'
  outer.dataset.componentId = component.id
  outer.dataset.kind = component.kind
  outer.dataset.presentation = presentationFor(plan, component.kind)
  outer.dataset.treatment = plan.treatments?.[component.kind] || 'default'
  outer.dataset.sourceStart = String(component.sourceRange.start)
  outer.dataset.sourceEnd = String(component.sourceRange.end)
  if (component.level) outer.dataset.level = String(component.level)

  if (component.kind === 'diagram') {
    try {
      outer.append(renderFlowchart(component.diagramSource))
    } catch (error) {
      outer.dataset.kind = 'code'
      outer.dataset.presentation = presentationFor(plan, 'code')
      outer.dataset.treatment = plan.treatments?.code || 'default'
      const pre = document.createElement('pre')
      const code = document.createElement('code')
      code.textContent = component.diagramSource
      pre.append(code)
      outer.append(pre)
      outer.dataset.diagramError = error.message
    }
    return outer
  }

  const template = document.createElement('template')
  template.innerHTML = component.html
  outer.append(template.content.cloneNode(true))
  if (component.kind === 'media') {
    const image = outer.querySelector('img')
    if (image?.alt) {
      const caption = document.createElement('figcaption')
      caption.textContent = image.alt
      outer.append(caption)
    }
  }
  return outer
}

export function compileMarkdown(content, plan) {
  const stripped = stripFrontmatter(content)
  const segments = splitByPageBreak(stripped.body, stripped.offset)
  const components = []
  let componentIndex = 0
  let title = ''
  let titleSourceRange = null
  let sectionIndex = 0

  for (const segment of segments) {
    const tokens = marked.lexer(segment.text)
    let localCursor = 0
    for (const token of tokens) {
      if (token.type === 'space') {
        localCursor += token.raw?.length || 0
        continue
      }
      const raw = token.raw || ''
      const relative = segment.text.indexOf(raw, localCursor)
      const start = segment.start + (relative >= 0 ? relative : localCursor)
      const end = start + raw.length
      localCursor = (relative >= 0 ? relative : localCursor) + raw.length
      let kind = inferKind(token)
      let html = ''
      if (token.type === 'code' && String(token.lang || '').trim().toLowerCase() === 'mermaid') {
        kind = 'diagram'
      } else {
        html = sanitizeHtml(marked.parse(raw))
        const probe = document.createElement('div')
        probe.innerHTML = html
        kind = normalizeRenderedElement(probe, kind)
        html = probe.innerHTML
      }
      const level = token.type === 'heading' ? Number(token.depth || 2) : undefined
      const component = {
        id: `component-${String(++componentIndex).padStart(4, '0')}`,
        kind,
        raw,
        html,
        level,
        sourceRange: {start, end},
        sectionIndex,
        diagramSource: kind === 'diagram' ? String(token.text || '') : undefined,
      }
      if (!title && token.type === 'heading' && level === 1) {
        title = String(token.text || '').trim()
        titleSourceRange = {start, end}
        component.coverTitle = true
      } else {
        components.push(component)
      }
    }
    if (segment.breakAfter) {
      components.push({
        id: `component-${String(++componentIndex).padStart(4, '0')}`,
        kind: 'page-break',
        sectionIndex,
        sourceRange: {start: segment.directiveStart, end: segment.directiveStart + PAGE_BREAK.length},
      })
      sectionIndex += 1
    }
  }

  return {title, titleSourceRange, components, createElement: component => buildComponentElement(component, plan)}
}

export {PAGE_BREAK}

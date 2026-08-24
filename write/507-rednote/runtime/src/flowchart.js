const SVG_NS = 'http://www.w3.org/2000/svg'

function svg(name, attrs = {}) {
  const node = document.createElementNS(SVG_NS, name)
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value))
  return node
}

function parseNode(raw) {
  const match = raw.trim().match(/^([A-Za-z0-9_-]+)(?:\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\})?$/)
  if (!match) return null
  return {id: match[1], label: match[2] || match[3] || match[4] || match[1], shape: match[4] ? 'decision' : 'box'}
}

export function parseFlowchart(source) {
  const lines = source.split(/\r?\n/).map(line => line.trim()).filter(Boolean)
  const header = lines.shift() || ''
  const headerMatch = header.match(/^(?:flowchart|graph)\s+(LR|RL|TD|TB|BT)$/i)
  if (!headerMatch) throw new Error('流程图必须以 flowchart LR 或 flowchart TD 开头')
  const direction = headerMatch[1].toUpperCase()
  const nodes = new Map()
  const edges = []

  const remember = node => {
    if (!node) return null
    const existing = nodes.get(node.id)
    nodes.set(node.id, existing ? {...existing, label: node.label === node.id ? existing.label : node.label} : node)
    return nodes.get(node.id)
  }

  for (const line of lines) {
    const edgeMatch = line.match(/^(.+?)\s*--+>?\s*(?:\|([^|]+)\|\s*)?(.+)$/)
    if (edgeMatch) {
      const from = remember(parseNode(edgeMatch[1]))
      const to = remember(parseNode(edgeMatch[3]))
      if (!from || !to) throw new Error(`无法解析流程关系：${line}`)
      edges.push({from: from.id, to: to.id, label: edgeMatch[2] || ''})
      continue
    }
    const node = remember(parseNode(line))
    if (!node) throw new Error(`无法解析流程节点：${line}`)
  }
  if (!nodes.size) throw new Error('流程图没有节点')
  if (nodes.size > 12 || edges.length > 20) throw new Error('首版流程图最多支持 12 个节点和 20 条边')
  return {direction, nodes: [...nodes.values()], edges}
}

function wrapLabel(label, max = 10) {
  const chars = [...label]
  if (chars.length <= max) return [label]
  const lines = []
  for (let index = 0; index < chars.length; index += max) lines.push(chars.slice(index, index + max).join(''))
  return lines.slice(0, 3)
}

export function renderFlowchart(source) {
  const model = parseFlowchart(source)
  const horizontal = ['LR', 'RL'].includes(model.direction)
  const reverse = ['RL', 'BT'].includes(model.direction)
  const nodeWidth = 190
  const nodeHeight = 82
  const gapX = 84
  const gapY = 58
  const columns = horizontal ? Math.min(model.nodes.length, 3) : Math.min(3, Math.ceil(Math.sqrt(model.nodes.length)))
  const rows = Math.ceil(model.nodes.length / columns)
  const positions = new Map()
  const ordered = reverse ? [...model.nodes].reverse() : model.nodes
  ordered.forEach((node, index) => {
    const col = horizontal ? index % columns : index % columns
    const row = horizontal ? Math.floor(index / columns) : Math.floor(index / columns)
    positions.set(node.id, {x: 34 + col * (nodeWidth + gapX), y: 34 + row * (nodeHeight + gapY)})
  })
  const width = 68 + columns * nodeWidth + (columns - 1) * gapX
  const height = 68 + rows * nodeHeight + (rows - 1) * gapY
  const root = svg('svg', {viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': '流程图'})
  const defs = svg('defs')
  const marker = svg('marker', {id: 'arrow', markerWidth: 10, markerHeight: 10, refX: 8, refY: 3, orient: 'auto', markerUnits: 'strokeWidth'})
  marker.append(svg('path', {d: 'M0,0 L0,6 L9,3 z', fill: 'currentColor'}))
  defs.append(marker)
  root.append(defs)

  for (const edge of model.edges) {
    const from = positions.get(edge.from)
    const to = positions.get(edge.to)
    if (!from || !to) continue
    const startX = from.x + nodeWidth / 2
    const startY = from.y + nodeHeight / 2
    const endX = to.x + nodeWidth / 2
    const endY = to.y + nodeHeight / 2
    const path = svg('path', {
      d: `M ${startX} ${startY} C ${(startX + endX) / 2} ${startY}, ${(startX + endX) / 2} ${endY}, ${endX} ${endY}`,
      class: 'diagram-edge', 'marker-end': 'url(#arrow)',
    })
    root.append(path)
    if (edge.label) {
      const text = svg('text', {x: (startX + endX) / 2, y: (startY + endY) / 2 - 8, class: 'diagram-label', 'text-anchor': 'middle'})
      text.textContent = edge.label
      root.append(text)
    }
  }

  for (const node of model.nodes) {
    const pos = positions.get(node.id)
    const group = svg('g')
    const shape = node.shape === 'decision'
      ? svg('polygon', {points: `${pos.x + nodeWidth / 2},${pos.y} ${pos.x + nodeWidth},${pos.y + nodeHeight / 2} ${pos.x + nodeWidth / 2},${pos.y + nodeHeight} ${pos.x},${pos.y + nodeHeight / 2}`, class: 'diagram-node'})
      : svg('rect', {x: pos.x, y: pos.y, width: nodeWidth, height: nodeHeight, rx: 8, class: 'diagram-node'})
    group.append(shape)
    const lines = wrapLabel(node.label)
    const text = svg('text', {x: pos.x + nodeWidth / 2, y: pos.y + nodeHeight / 2 - (lines.length - 1) * 12, class: 'diagram-label', 'text-anchor': 'middle'})
    lines.forEach((line, index) => {
      const tspan = svg('tspan', {x: pos.x + nodeWidth / 2, dy: index === 0 ? 0 : 25})
      tspan.textContent = line
      text.append(tspan)
    })
    group.append(text)
    root.append(group)
  }
  return root
}

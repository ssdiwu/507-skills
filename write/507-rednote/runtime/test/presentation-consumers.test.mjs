import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import test from 'node:test'

test('presentation and treatment state reach DOM consumers', () => {
  const markdown = readFileSync(new URL('../src/markdown.js', import.meta.url), 'utf8')
  const paginator = readFileSync(new URL('../src/paginator.js', import.meta.url), 'utf8')
  const css = readFileSync(new URL('../styles.css', import.meta.url), 'utf8')
  assert.match(css, /SourceHanSansCN-VF\.otf\.woff2/)
  assert.match(css, /SourceHanSerifCN-VF\.otf\.woff2/)
  assert.match(css, /data-kind="quote"[^}]+var\(--body-size\)[^}]+var\(--line-height\)/s)
  assert.match(css, /letter-spacing:\s*var\(--character-spacing\)/)
  assert.match(markdown, /dataset\.presentation/)
  assert.match(markdown, /dataset\.treatment/)
  assert.match(paginator, /dataset\.presentation/)
  assert.match(paginator, /dataset\.treatment/)
  for (const presentation of ['panel-led', 'data-led', 'schematic-led', 'photo-led', 'ui-product-led', 'editorial-print-led', 'hand-drawn-explainer', 'illustration-led']) {
    assert.ok(css.includes(`[data-presentation="${presentation}"]`), `missing CSS consumer for ${presentation}`)
  }
  for (const treatment of ['inverse', 'section-emphasis', 'dense']) {
    assert.ok(css.includes(`[data-treatment="${treatment}"]`), `missing CSS consumer for ${treatment}`)
  }
})

import assert from 'node:assert/strict'
import test from 'node:test'
import {applyPreset, DEFAULT_PLAN, DESIGN_LANGUAGES, FONT_FAMILIES, normalizePlan, PRESENTATION_SUPPORT, PRESETS} from '../src/design-system.js'

test('typography uses licensed local fonts and survives preset changes', () => {
  assert.deepEqual(Object.keys(FONT_FAMILIES), ['source-han-sans', 'source-han-serif'])
  assert.equal(DEFAULT_PLAN.typography.fontFamily, 'source-han-sans')
  assert.equal(DEFAULT_PLAN.typography.characterWidth, 1)
  const custom = normalizePlan({typography: {fontFamily: 'source-han-serif', characterWidth: 0.96}})
  const restyled = applyPreset(custom, 'field-notes')
  assert.equal(restyled.typography.fontFamily, 'source-han-serif')
  assert.equal(restyled.typography.characterWidth, 0.96)
  assert.equal(normalizePlan({typography: {fontFamily: 'unknown'}}).typography.fontFamily, 'source-han-sans')
  for (const language of Object.values(DESIGN_LANGUAGES)) {
    assert.doesNotMatch(language.description, /衬线/, 'design language copy must not imply a hidden font switch')
  }
})

test('presets are complete combinations layered over six base languages', () => {
  assert.equal(Object.keys(DESIGN_LANGUAGES).length, 6)
  assert.ok(Object.keys(PRESETS).length >= 18)
  const counts = new Map()
  for (const preset of Object.values(PRESETS)) counts.set(preset.designLanguage, (counts.get(preset.designLanguage) || 0) + 1)
  assert.ok([...counts.values()].some(count => count > 1))
  const dark = applyPreset(DEFAULT_PLAN, 'dark-night')
  assert.equal(dark.designLanguage, 'bold-statement')
  assert.equal(dark.palette.paper, PRESETS['dark-night'].palette.paper)
  assert.equal(dark.presentations.table, PRESETS['dark-night'].presentations.table)
  for (const language of Object.keys(DESIGN_LANGUAGES)) {
    const signatures = Object.values(PRESETS)
      .filter(preset => preset.designLanguage === language)
      .map(preset => JSON.stringify({presentations: preset.presentations, treatments: preset.treatments}))
    assert.equal(new Set(signatures).size, signatures.length, `${language} presets must have distinct structural combinations`)
  }
  for (const preset of Object.values(PRESETS)) {
    for (const [kind, presentation] of Object.entries(preset.presentations)) {
      assert.ok(PRESENTATION_SUPPORT[kind].includes(presentation), `${preset.label} has unsupported ${kind} presentation`)
    }
  }
})

#!/usr/bin/env node
// Check actual box fit in a host page, including controls outside a Stage.
import { launch } from './browser.mjs'
import { auditLayout, layoutResult } from './layout-core.mjs'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'

const args = process.argv.slice(2)
const options = { select: 'body', width: 1280, delay: 300, report: null, screenshot: null, strict: false, scroll: false }
let url
try {
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    if (arg === '--help') { console.log('usage: node scripts/layout.mjs <url> [--select body] [--width 1280] [--delay 300] [--report layout.json] [--screenshot layout.png] [--strict] [--scroll]\nWith --scroll, brings each matched region into view and marks oversized regions incomplete. Checks visible controls and padded containers in this document at one snapshot. Iframes need a separate direct URL check. Exit 2 = incomplete; --strict exits 1 for findings. The optional screenshot captures the last inspected 1000px-high viewport. No motion approval.'); process.exit(0) }
    if (arg === '--scroll') options.scroll = true
    else if (arg === '--strict') options.strict = true
    else if (/^--(select|width|delay|report|screenshot)$/.test(arg)) {
      if (!args[i + 1] || args[i + 1].startsWith('--')) throw new Error(`${arg} requires a value`)
      options[arg.slice(2)] = args[++i]
    } else if (arg.startsWith('--') || url) throw new Error(`unexpected argument: ${arg}`)
    else url = arg
  }
  if (!url) throw new Error('a URL is required; use --help')
  for (const name of ['width', 'delay']) {
    options[name] = Number(options[name])
    if (!Number.isInteger(options[name]) || options[name] < (name === 'width' ? 1 : 0)) throw new Error(`--${name} must be ${name === 'width' ? 'a positive' : 'a nonnegative'} integer`)
  }
} catch (error) { console.error(`layout: ${error.message}`); process.exit(2) }
const browser = await launch()
const page = await browser.newPage({ viewport: { width: options.width, height: 1000 } })
const errors = [], scopes = []
page.on('pageerror', (error) => errors.push(`page: ${error.message}`))
page.on('response', (response) => { if (response.status() >= 400 && !/\/favicon\./.test(response.url())) errors.push(`resource: ${response.status()} ${response.url()}`) })
try {
  await page.goto(url, { waitUntil: 'domcontentloaded' })
  await page.locator(options.select).first().waitFor({ state: 'visible', timeout: 10000 })
  await page.evaluate(() => document.fonts.ready)
  await page.waitForTimeout(options.delay)
  for (const root of await page.locator(options.select).all()) {
    if (await root.isVisible()) {
      if (options.scroll) {
        await root.scrollIntoViewIfNeeded()
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))))
      }
      const region = await root.boundingBox()
      const scope = { selector: options.select, region, ...await root.evaluate(auditLayout) }
      if (options.scroll && region && (region.y < -1 || region.y + region.height > 1001 || region.x < -1 || region.x + region.width > options.width + 1)) {
        scope.deferred.push('selected region extends beyond the viewport; only its visible portion was checked')
      }
      scopes.push(scope)
    }
  }
  if (options.screenshot) {
    const path = resolve(options.screenshot)
    mkdirSync(dirname(path), { recursive: true })
    await page.screenshot({ path })
    console.log(`layout screenshot: ${path}`)
  }
} catch (error) { errors.push(error.message) }
await browser.close()
const result = layoutResult(scopes, errors, options.strict)
result.viewport = { width: options.width, height: 1000 }
result.url = url
result.scrollRegions = options.scroll
for (const scope of scopes) {
  console.log(`layout coverage: ${scope.checked.controls} controls, ${scope.checked.paddedContainers} padded containers`)
  for (const finding of scope.findings) console.log(finding.message)
  for (const deferred of scope.deferred) console.log(`incomplete: ${deferred}`)
  for (const manual of scope.manual) console.log(`manual: ${manual}`)
}
for (const error of result.errors) console.error(`incomplete: ${error}`)
console.log(`layout: ${result.status}; this snapshot is not visual approval`)
if (options.report) {
  const path = resolve(options.report)
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, JSON.stringify(result, null, 2) + '\n')
}
process.exitCode = result.exitCode

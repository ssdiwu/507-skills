import test from 'node:test'
import assert from 'node:assert/strict'
import { reportResult, applyRehearsalGate } from './verification.mjs'

const result = (status = 'complete', findings = []) => reportResult({
  still: true,
  stages: [{ coverage: { status }, findings, manual: [] }],
})

test('a non-strict gate failure exits 1 and is recorded in JSON', () => {
  const findings = ['framing: clipped control']
  const report = applyRehearsalGate(result('complete', findings), findings)
  assert.equal(report.exitCode, 1)
  assert.equal(report.status, 'issues')
  assert.equal(JSON.parse(JSON.stringify(report)).gate.status, 'failed')
})

test('incomplete sampling cannot become a gate pass or a definitive failure', () => {
  for (const findings of [[], ['framing: clipped control']]) {
    const report = applyRehearsalGate(result('inconclusive', findings), findings)
    assert.equal(report.exitCode, 2)
    assert.equal(report.status, 'inconclusive')
    assert.equal(report.gate.status, 'inconclusive')
    assert.deepEqual(report.gate.findings, findings)
  }
})

test('complete clean coverage can pass the gate', () => {
  const report = applyRehearsalGate(result(), [])
  assert.equal(report.exitCode, 0)
  assert.equal(report.gate.status, 'passed')
})

test('ordinary non-strict and strict findings keep their existing behavior', () => {
  const stage = { coverage: { status: 'complete' }, findings: ['candidate'], manual: [] }
  assert.equal(reportResult({ stages: [stage] }).exitCode, 0)
  assert.equal(reportResult({ stages: [stage], strict: true }).exitCode, 1)
})

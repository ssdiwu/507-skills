import assert from 'node:assert/strict'
import test from 'node:test'
import {enqueueSave} from '../src/save-queue.js'

test('a failed save does not poison later saves', async () => {
  const events = []
  let queue = Promise.resolve()
  queue = enqueueSave(queue, async () => {
    events.push('failed')
    throw new Error('temporary failure')
  })
  await assert.rejects(queue, /temporary failure/)
  queue = enqueueSave(queue, async () => {
    events.push('recovered')
    return 'saved'
  })
  await assert.doesNotReject(queue)
  assert.deepEqual(events, ['failed', 'recovered'])
})

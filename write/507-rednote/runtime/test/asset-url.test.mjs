import assert from 'node:assert/strict'
import test from 'node:test'
import {projectAssetUrl} from '../src/asset-url.js'

test('project asset paths are encoded exactly once', () => {
  const search = '?token=local token'
  const raw = projectAssetUrl('assets/预测收束-主视觉.png', search)
  const alreadyEncoded = projectAssetUrl('assets/%E9%A2%84%E6%B5%8B%E6%94%B6%E6%9D%9F-%E4%B8%BB%E8%A7%86%E8%A7%89.png', search)
  assert.equal(raw, alreadyEncoded)
  assert.match(raw, /^\/project\/assets\/%E9%A2%84/)
  assert.doesNotMatch(raw, /%25E9/)
  assert.match(raw, /token=local%20token$/)
})

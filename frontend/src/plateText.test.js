import assert from 'node:assert/strict'
import test from 'node:test'
import { findPlateReading, normalizePlateText } from './plateText.js'

test('normalizes Indian registration text with separators', () => {
  assert.deepEqual(normalizePlateText('ka 05 ab 2045'), {
    rawText: 'ka 05 ab 2045',
    cleanedText: 'KA05AB2045',
    validFormat: true,
  })
})

test('corrects common OCR confusions in registration digits', () => {
  assert.equal(normalizePlateText('KAOSABZO45').cleanedText, 'KA05AB2045')
})

test('marks unrelated text as invalid', () => {
  assert.equal(normalizePlateText('TRAFFIC').validFormat, false)
})

test('joins OCR words and chooses the strongest plate candidate', () => {
  const result = findPlateReading({
    text: 'KA 05 AB 2045',
    confidence: 75,
    words: [
      { text: 'KA', confidence: 90 },
      { text: '05', confidence: 92 },
      { text: 'AB', confidence: 94 },
      { text: '2045', confidence: 96 },
    ],
  })

  assert.equal(result.cleanedText, 'KA05AB2045')
  assert.equal(result.confidence, 93)
})
const platePattern = /^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}$/
const letterCorrections = { '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '6': 'G', '8': 'B' }
const digitCorrections = { O: '0', I: '1', S: '5', Z: '2', G: '6', B: '8' }

function convertCharacters(value, corrections) {
  return [...value].map((character) => corrections[character] ?? character).join('')
}

export function normalizePlateText(rawText = '') {
  const cleanedText = String(rawText).toUpperCase().replace(/[^A-Z0-9]/g, '')
  if (cleanedText === 'UNKNOWN' || cleanedText === 'UNKN0WN') {
    return { rawText, cleanedText: 'UNKNOWN', validFormat: false }
  }

  if (platePattern.test(cleanedText)) {
    return { rawText, cleanedText, validFormat: true }
  }

  for (const registrationLength of [2, 1]) {
    for (const seriesLength of [2, 1, 3]) {
      for (const numberLength of [4, 3, 2, 1]) {
        if (cleanedText.length !== 2 + registrationLength + seriesLength + numberLength) continue

        const registrationEnd = 2 + registrationLength
        const seriesEnd = registrationEnd + seriesLength
        const candidate =
          convertCharacters(cleanedText.slice(0, 2), letterCorrections) +
          convertCharacters(cleanedText.slice(2, registrationEnd), digitCorrections) +
          convertCharacters(cleanedText.slice(registrationEnd, seriesEnd), letterCorrections) +
          convertCharacters(cleanedText.slice(seriesEnd), digitCorrections)

        if (platePattern.test(candidate)) {
          return { rawText, cleanedText: candidate, validFormat: true }
        }
      }
    }
  }

  return { rawText, cleanedText, validFormat: false }
}

export function findPlateReading(data) {
  const words = (data.words ?? []).filter((word) => word.text?.trim())
  const candidates = []

  for (let start = 0; start < words.length; start += 1) {
    for (let end = start + 1; end <= Math.min(start + 4, words.length); end += 1) {
      const text = words.slice(start, end).map((word) => word.text).join('')
      if (text.length < 8 || text.length > 12) continue

      const reading = normalizePlateText(text)
      if (reading.validFormat) {
        const confidence = words
          .slice(start, end)
          .reduce((total, word) => total + (Number(word.confidence) || 0), 0) / (end - start)
        candidates.push({ ...reading, confidence })
      }
    }
  }

  const fullTextReading = normalizePlateText(data.text)
  if (fullTextReading.validFormat) {
    candidates.push({ ...fullTextReading, confidence: Number(data.confidence) || 0 })
  }

  return candidates.sort((first, second) => second.confidence - first.confidence)[0] ?? null
}
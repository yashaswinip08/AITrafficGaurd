import { createWorker, OEM, PSM } from 'tesseract.js'
import { findPlateReading } from './plateText.js'

export async function analyzeImage(file, onProgress) {
  const worker = await createWorker('eng', OEM.LSTM_ONLY, {
    workerPath: '/ocr/worker.min.js',
    corePath: '/ocr/',
    langPath: '/ocr/lang',
    gzip: true,
    logger: onProgress ?? (() => {}),
  })

  try {
    await worker.setParameters({
      tessedit_pageseg_mode: PSM.SINGLE_LINE,
      tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    })
    const { data } = await worker.recognize(file)
    return {
      text: data.text.trim(),
      confidence: Math.round(Number(data.confidence) || 0),
      plateReading: findPlateReading(data),
    }
  } finally {
    await worker.terminate()
  }
}
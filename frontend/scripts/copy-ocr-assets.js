import { copyFile, mkdir } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const require = createRequire(import.meta.url)
const frontendDirectory = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const publicOcrDirectory = resolve(frontendDirectory, 'public/ocr')
const languageDirectory = resolve(publicOcrDirectory, 'lang')
const coreDirectory = dirname(require.resolve('tesseract.js-core'))

await mkdir(languageDirectory, { recursive: true })
await copyFile(
  require.resolve('tesseract.js/dist/worker.min.js'),
  resolve(publicOcrDirectory, 'worker.min.js'),
)

for (const coreFile of [
  'tesseract-core.wasm.js',
  'tesseract-core-lstm.wasm.js',
  'tesseract-core-simd.wasm.js',
  'tesseract-core-simd-lstm.wasm.js',
  'tesseract-core-relaxedsimd.wasm.js',
  'tesseract-core-relaxedsimd-lstm.wasm.js',
]) {
  await copyFile(resolve(coreDirectory, coreFile), resolve(publicOcrDirectory, coreFile))
}

await copyFile(
  resolve(frontendDirectory, 'node_modules/@tesseract.js-data/eng/4.0.0_best_int/eng.traineddata.gz'),
  resolve(languageDirectory, 'eng.traineddata.gz'),
)
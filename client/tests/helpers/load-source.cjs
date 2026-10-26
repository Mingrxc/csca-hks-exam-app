const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const { parse, compileScript } = require('@vue/compiler-sfc')
const { transformSync } = require('esbuild')
const root = path.resolve(__dirname, '../../src')

// One cache per test keeps the reactive locale shared by real consumers.
function createLoader(mocks = {}, globals = {}) {
  const cache = new Map()
  function load(file) {
    let filename = path.resolve(root, file)
    if (!fs.existsSync(filename)) filename += '.ts'
    if (fs.statSync(filename).isDirectory()) filename = path.join(filename, 'index.ts')
    if (cache.has(filename)) return cache.get(filename).exports
    let source = fs.readFileSync(filename, 'utf8')
    if (filename.endsWith('.vue')) source = compileScript(parse(source, { filename }).descriptor, { id: 'source-test' }).content
    const { code } = transformSync(source, { loader: 'ts', format: 'cjs', define: { 'import.meta.env': JSON.stringify({ PROD: false, VITE_API_BASE_URL: 'https://api.example.com/api/v1' }) } })
    const module = { exports: {} }
    cache.set(filename, module)
    vm.runInNewContext(code, { module, exports: module.exports, console, Date, setTimeout, ...globals,
      require(name) {
        if (name in mocks) return mocks[name]
        if (name === 'vue') return require('vue')
        if (name.startsWith('@/')) return load(name.slice(2))
        if (name.startsWith('.')) return load(path.resolve(path.dirname(filename), name))
        throw new Error('Unexpected import ' + name)
      },
    }, { filename })
    return module.exports
  }
  return load
}
module.exports = { createLoader }

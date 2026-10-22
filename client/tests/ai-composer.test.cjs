const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const test = require('node:test')
const { parse, compileScript } = require('@vue/compiler-sfc')
const { transformSync } = require('esbuild')
const vue = require('vue')

// Exercise the page's real setup code without making network or storage writes.
const filename = path.join(__dirname, '../src/pages/ai/index.vue')
const { descriptor } = parse(fs.readFileSync(filename, 'utf8'), { filename })
const compiled = compileScript(descriptor, { id: 'ai-composer-test' })
const { code } = transformSync(compiled.content, { loader: 'ts', format: 'cjs' })

function createPage(chat = async () => ({ reply: '测试回复' })) {
  const storage = new Map()
  const hooks = []
  const calls = []
  const module = { exports: {} }
  const imports = {
    vue: { ...vue, onMounted: (callback) => hooks.push(callback) },
    '@dcloudio/uni-app': { onShow: (callback) => hooks.push(callback), onShareAppMessage() {} },
    '@/constants/share': { createAppShareMessage() {} },
    '@/constants/exam': { getExamLabel: (exam) => exam === 'HKS' ? 'HSK' : exam },
    '@/stores/user': { useUserStore: () => ({ isLogin: true, selectedExams: ['CSCA'], primaryExam: 'CSCA', userInfo: { targetExam: 'CSCA' } }) },
    '@/features/ai/api': { aiApi: { chat: (payload) => { calls.push(payload); return chat(payload) } } },
  }
  vm.runInNewContext(code, {
    module,
    exports: module.exports,
    require: (name) => {
      assert(name in imports, `Unexpected import: ${name}`)
      return imports[name]
    },
    uni: { getStorageSync: (key) => storage.get(key), setStorageSync: (key, value) => storage.set(key, value), removeStorageSync: (key) => storage.delete(key) },
  }, { filename })
  const page = module.exports.default.setup({}, { expose() {} })
  hooks.forEach((callback) => callback())
  return { page, calls }
}

const input = (value) => ({ detail: { value } })

test('empty or whitespace input cannot send; native input enables sending', async () => {
  const { page, calls } = createPage()
  assert.equal(page.canSend.value, false)
  page.onDraftInput(input('   '))
  await page.send()
  assert.equal(calls.length, 0)
  page.onDraftInput(input('请讲解这道题'))
  assert.equal(page.canSend.value, true)
})

test('button send submits the question and stores the reply before clearing the input', async () => {
  const { page, calls } = createPage()
  page.onDraftInput(input('  请讲解这道题  '))
  await page.send()
  assert.equal(calls.length, 1)
  assert.equal(calls[0].question, '请讲解这道题')
  assert.equal(calls[0].examType, 'CSCA')
  assert.equal(calls[0].messages.at(-1).content, '请讲解这道题')
  assert.equal(page.currentMessages.value.at(-1).content, '测试回复')
  assert.equal(page.draft.value, '')
  assert.equal(page.canSend.value, false)
  assert.equal(page.sending.value, false)
})

test('keyboard confirmation uses its latest text', async () => {
  const { page, calls } = createPage()
  page.onDraftInput(input('旧内容'))
  await page.onDraftConfirm(input('刚输入的最后一句'))
  assert.equal(calls[0].question, '刚输入的最后一句')
})

test('pending requests reject repeated button and keyboard submissions', async () => {
  let resolveReply
  const { page, calls } = createPage(() => new Promise((resolve) => { resolveReply = resolve }))
  page.onDraftInput(input('只发送一次'))
  const pending = page.send()
  assert.equal(page.sending.value, true)
  await page.send()
  await page.onDraftConfirm(input('不能覆盖正在发送的内容'))
  assert.equal(calls.length, 1)
  assert.equal(page.draft.value, '只发送一次')
  resolveReply({ reply: '完成' })
  await pending
  assert.equal(page.sending.value, false)
})

test('a failed request preserves the question and context and allows retry', async () => {
  let fail = true
  const { page, calls } = createPage(async () => {
    if (fail) throw new Error('test network failure')
    return { reply: '重试成功' }
  })
  page.onDraftInput(input('这道题怎么解'))
  page.contextDraft.value = '题目上下文'
  await page.send()
  assert.equal(page.sending.value, false)
  assert.equal(page.draft.value, '这道题怎么解')
  assert.equal(page.contextDraft.value, '题目上下文')
  assert.equal(page.canSend.value, true)
  fail = false
  await page.send()
  assert.equal(calls.length, 2)
  assert.equal(page.currentMessages.value.at(-1).content, '重试成功')
  assert.equal(page.draft.value, '')
  assert.equal(page.contextDraft.value, '')
})

test('question context alone can be submitted', async () => {
  const { page, calls } = createPage()
  page.contextDraft.value = '仅有题目上下文'
  assert.equal(page.canSend.value, true)
  await page.send()
  assert.equal(calls[0].context, '仅有题目上下文')
  assert.equal(calls[0].messages.at(-1).content, '仅有题目上下文')
})

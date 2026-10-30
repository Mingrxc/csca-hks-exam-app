const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const test = require('node:test')
const { parse, compileScript } = require('@vue/compiler-sfc')
const { transformSync } = require('esbuild')
const vue = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')
const APP_VERSION = require('../src/manifest.json').versionName

async function createPage(name, options = {}) {
  const filename = path.join(__dirname, `../src/pages/${name}.vue`)
  // Match the WeChat branch of this page, without running a browser or WeChat.
  const source = fs.readFileSync(filename, 'utf8').replace(/\/\/ #ifndef MP-WEIXIN[\s\S]*?\/\/ #endif/g, '')
  const { descriptor } = parse(source, { filename })
  const compiled = compileScript(descriptor, { id: 'profile-support-test' })
  const { code } = transformSync(compiled.content, { loader: 'ts', format: 'cjs' })
  const storage = options.storage || new Map()
  const calls = []
  const navigation = []
  const toasts = []
  const scrolls = []
  const hooks = []
  const user = options.user || { isLogin: true, userInfo: { id: 7 }, login: async () => {} }
  const categories = ['question', 'bug', 'suggestion', 'other'].map((value) => ({ value, label: value }))
  const imports = {
    vue,
    '@dcloudio/uni-app': { onLoad: (callback) => hooks.push(callback), onShow() {}, onHide() {}, onUnload() {}, onReachBottom() {} },
    '@/constants/brand': { APP_VERSION, APP_NAME: '老外1点通', APP_ICON_PATH: '/static/brand/icon.png', APP_DESCRIPTION: '面向留学生的 HSK 与 CSCA 学习备考工具' },
    '@/stores/user': { useUserStore: () => user },
    '@/features/feedback/api': { FEEDBACK_CATEGORIES: categories, feedbackApi: { submit: async (payload) => { calls.push(payload); return options.submit ? options.submit(payload) : { id: 31, status: 'unread', created_at: '2026-10-25T12:00:00Z' } } } },
    '@/features/content/api': { contentApi: {
      listAnnouncements: async (page) => { calls.push(page); return options.list ? options.list(page) : { items: [], total: 0 } },
      getAnnouncement: async (id) => { calls.push(id); return options.get ? options.get(id) : { id, body: '正文' } },
    } },
    '@/features/content/date': { formatReleaseDate: (value) => value },
  }
  const module = { exports: {} }
  const wx = options.wx || { openPrivacyContract: () => { calls.push('privacy') } }
  const uni = {
    getStorageSync: (key) => storage.get(key),
    setStorageSync: (key, value) => { if (options.failStorage) throw new Error('storage full'); storage.set(key, value) },
    removeStorageSync: (key) => { if (options.failStorage) throw new Error('storage unavailable'); storage.delete(key) },
    showToast: (value) => toasts.push(value), navigateTo: (value) => navigation.push(value.url),
    pageScrollTo: (value) => scrolls.push(value),
  }
  const loadI18n = createLoader({ '@dcloudio/uni-app': { onShow() {} } }, { uni, getCurrentPages: () => [] })
  vm.runInNewContext(code, {
    module, exports: module.exports,
    require: (name) => { if (name.startsWith('@/i18n')) return loadI18n(name.slice(2)); assert(name in imports, `Unexpected import: ${name}`); return imports[name] },
    uni, wx,
  }, { filename })
  const page = module.exports.default.setup({}, { expose() {} })
  for (const callback of hooks) await callback(options.query || {})
  return { page, calls, storage, user, navigation, toasts, scrolls, i18n: loadI18n('i18n') }
}

const input = (value) => ({ detail: { value } })

test('feedback validates empty input and preserves its draft before submission', async () => {
  const { page, calls, storage } = await createPage('feedback/index')
  page.onInput(input('  \n '))
  await page.submit()
  assert.equal(calls.length, 0)
  page.onInput(input('题目选项看不清'))
  page.selectCategory('question')
  assert.equal(page.canSubmit.value, true)
  assert.equal(storage.get('feedback_draft_v1_7').content, '题目选项看不清')
  page.onInput(input('字'.repeat(1001)))
  assert.equal(page.canSubmit.value, false)
})

test('language changes preserve feedback category, text and retry identity', async () => {
  const { page, storage, i18n } = await createPage('feedback/index')
  page.onInput(input('中文反馈内容'))
  page.selectCategory('bug')
  const draft = JSON.stringify(storage.get('feedback_draft_v1_7'))
  i18n.setLanguage('en')
  assert.equal(page.content.value, '中文反馈内容')
  assert.equal(page.category.value, 'bug')
  assert.equal(JSON.stringify(storage.get('feedback_draft_v1_7')), draft)
})

test('a pending feedback request blocks double submission and input changes', async () => {
  let resolve
  const { page, calls, storage, scrolls } = await createPage('feedback/index', { submit: () => new Promise((done) => { resolve = done }) })
  page.onInput(input('  有一个小建议  '))
  const pending = page.submit()
  await page.submit()
  page.onInput(input('不能替换'))
  page.selectCategory('bug')
  assert.equal(calls.length, 1)
  assert.equal(calls[0].content, '有一个小建议')
  assert.equal(calls[0].category, 'suggestion')
  assert.equal(calls[0].app_version, APP_VERSION)
  assert.equal(page.content.value, '  有一个小建议  ')
  resolve({ id: 9, status: 'unread' })
  await pending
  assert.equal(page.receipt.value.id, 9)
  assert.equal(page.content.value, '')
  assert.equal(storage.has('feedback_draft_v1_7'), false)
  assert.equal(scrolls[0].scrollTop, 0)
})

test('network failure and reopening preserve the same idempotency key for a safe retry', async () => {
  const storage = new Map()
  const first = await createPage('feedback/index', { storage, submit: async () => { throw new Error('response lost') } })
  first.page.onInput(input('听力播放问题'))
  await first.page.submit()
  const firstId = first.calls[0].request_id
  assert.equal(first.page.sending.value, false)
  assert.equal(first.page.canSubmit.value, true)
  assert.equal(first.page.content.value, '听力播放问题')
  const reopened = await createPage('feedback/index', { storage })
  await reopened.page.submit()
  assert.equal(reopened.calls[0].request_id, firstId)
  assert.equal(reopened.page.receipt.value.id, 31)
})

test('feedback drafts are isolated by user and account changes cannot submit the previous draft', async () => {
  const storage = new Map([['feedback_draft_v1_7', { category: 'bug', content: '用户7的草稿', requestId: 'feedback-old-key', appVersion: '1.5.1' }]])
  const current = await createPage('feedback/index', { storage })
  assert.equal(current.page.content.value, '用户7的草稿')
  current.user.userInfo.id = 8
  await current.page.submit()
  assert.equal(current.calls.length, 0)
  assert.equal(current.page.content.value, '')
  assert.equal(storage.get('feedback_draft_v1_7').content, '用户7的草稿')
})

test('storage errors cannot change a successful server response into a failed submission', async () => {
  const { page } = await createPage('feedback/index', { failStorage: true })
  page.onInput(input('一个建议'))
  await page.submit()
  assert.equal(page.receipt.value.id, 31)
  assert.equal(page.sending.value, false)
})

test('login failure leaves the feedback form disabled', async () => {
  const { page, calls } = await createPage('feedback/index', { user: { isLogin: false, userInfo: { id: 0 }, login: async () => { throw new Error('offline') } } })
  assert.equal(page.loadError.value, true)
  assert.equal(page.canSubmit.value, false)
  await page.submit()
  assert.equal(calls.length, 0)
})

test('announcement pagination failures keep existing cards and retry the failed page', async () => {
  let fail = true
  const { page, calls } = await createPage('about/announcements', { list: async (number) => {
    if (number === 1) return { items: [{ id: 1 }], total: 2 }
    if (fail) throw new Error('offline')
    return { items: [{ id: 2 }], total: 2 }
  } })
  await page.loadMore()
  assert.equal(page.error.value, true)
  assert.equal(page.items.value.length, 1)
  fail = false
  await page.retry()
  assert.equal(calls.join(','), '1,2,2')
  assert.equal(page.items.value.length, 2)
  assert.equal(page.hasMore.value, false)
})

test('invalid announcement identifiers never trigger a detail request', async () => {
  const { page, calls } = await createPage('about/announcement', { query: { id: '-1' } })
  assert.equal(page.error.value, true)
  assert.equal(calls.length, 0)
})

test('about navigates to updates and opens the official privacy guide without requesting authorization', async () => {
  const { page, navigation, calls } = await createPage('about/index')
  page.openAnnouncements()
  page.openPrivacyGuide()
  assert.equal(navigation[0], '/pages/about/announcements')
  assert.equal(calls.join(','), 'privacy')
})

test('all shipped client version metadata agrees with 1.5.3', () => {
  const root = path.join(__dirname, '..')
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'src/manifest.json'), 'utf8'))
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'))
  const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'))
  assert.equal(manifest.versionName, '1.5.3')
  assert.equal(manifest.versionCode, '153')
  assert.equal(pkg.version, manifest.versionName)
  assert.equal(lock.version, manifest.versionName)
  assert.equal(lock.packages[''].version, manifest.versionName)
})

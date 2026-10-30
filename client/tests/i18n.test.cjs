const assert = require('node:assert/strict')
const test = require('node:test')
const vue = require('vue')
const pinia = require('pinia')
const { createLoader } = require('./helpers/load-source.cjs')

function environment(options = {}) {
  const storage = options.storage || new Map()
  const chrome = [], modals = [], hooks = []
  let route = 'pages/profile/index'
  const uni = {
    getStorageSync: key => storage.get(key), setStorageSync: (key, value) => storage.set(key, value),
    removeStorageSync: key => storage.delete(key), getAppBaseInfo: () => ({ language: options.system || 'zh_CN' }),
    setNavigationBarTitle: value => chrome.push(['title', value.title]),
    setTabBarItem: value => chrome.push(['tab', value.index, value.text]),
    showModal: value => modals.push(value), showToast() {}, navigateTo() {},
  }
  const load = createLoader({ pinia, '@dcloudio/uni-app': { onShow: fn => hooks.push(fn), onLoad: fn => hooks.push(fn), onShareAppMessage() {} }, ...options.mocks }, { uni, getCurrentPages: () => [{ route }] })
  const i18n = load('i18n')
  i18n.initializeLanguage()
  return { i18n, load, uni, storage, chrome, modals, hooks, setRoute: value => { route = value } }
}

test('first launch follows WeChat; explicit local choice survives restart without login', () => {
  const storage = new Map()
  const first = environment({ storage, system: 'fr' })
  assert.equal(first.i18n.getLanguage(), 'en')
  first.i18n.setLanguage('zh')
  assert.equal(environment({ storage, system: 'en' }).i18n.getLanguage(), 'zh')
  assert.equal(environment({ system: 'zh_TW' }).i18n.getLanguage(), 'zh')
  first.uni.getStorageSync = () => { throw new Error('unavailable') }
  assert.equal(first.i18n.initializeLanguage(), 'en')
})

test('switching updates native navigation and all tabs; a cached page cannot overwrite the active title', async () => {
  const env = environment()
  const scope = vue.effectScope()
  const { usePageI18n } = env.load('i18n/page')
  scope.run(() => { usePageI18n('pages/exam/index'); usePageI18n('pages/profile/index') })
  try {
    env.i18n.setLanguage('en')
    await vue.nextTick()
    assert.equal(env.chrome.filter(item => item[0] === 'title').length, 1)
    assert.equal(env.chrome[0][1], 'Me')
    assert.deepEqual(env.chrome.filter(item => item[0] === 'tab'), [
      ['tab', 0, 'Home'], ['tab', 1, 'Practice'], ['tab', 2, 'Me'],
    ])
    env.setRoute('pages/exam/index')
    env.hooks[0]()
    assert.equal(env.chrome.at(-4)[1], 'Practice')
    env.i18n.setLanguage('zh')
    await vue.nextTick()
    assert.equal(env.chrome.at(-4)[1], '刷题')
    const tabs = require('../src/pages.json').tabBar.list
    assert.deepEqual(env.chrome.slice(-3), tabs.map((item, index) => ['tab', index, item.text]))
  } finally { scope.stop() }
})

test('language changes preserve the active practice, Chinese material and answer snapshot', () => {
  const env = environment()
  const store = env.load('stores/exam.ts').useExamStore(pinia.createPinia())
  store.setPaper(12, [{ id: 3, examType: 'HKS', type: 'single', difficulty: 'easy', stem: '今天星期几？', options: [{ key: 'A', text: '星期一' }], answer: 'A', analysis: '原始中文解析', transcript: '原始听力内容' }])
  store.start()
  store.setAnswer(0, 'A')
  store.persistProgress()
  const snapshot = JSON.stringify(env.storage.get('exam_active_progress_v2'))
  const state = JSON.stringify(store.$state)
  env.i18n.setLanguage('en')
  assert.equal(JSON.stringify(store.$state), state)
  assert.equal(JSON.stringify(env.storage.get('exam_active_progress_v2')), snapshot)
  assert.equal(store.currentQuestion.analysis, '原始中文解析')
})

test('English filter labels keep Chinese subject/module/topic API values', async () => {
  let request
  const store = { config: {}, hasActiveProgress: false, setConfig() {}, setPaper() {}, start() {} }
  const env = environment({ mocks: {
    '@/stores/exam': { useExamStore: () => store },
    '@/constants/share': { createAppShareMessage() {} },
    '@/api/contracts': { toQuestion: value => value },
    '@/features/exam/api': { questionApi: {
      getCatalog: async () => [{ exam_type: 'CSCA', subject: '物理', knowledge_module: '光学', knowledge_point: '折射' }],
      generatePaper: async payload => { request = payload; return { id: 2, questions: [] } },
    } },
  } })
  const page = env.load('pages/exam/paper.vue').default.setup({}, { expose() {} })
  await env.hooks[1]({ examType: 'CSCA', strategy: 'knowledge', subject: '物理' })
  page.selectModule(1)
  page.form.knowledgePoint = '折射'
  env.i18n.setLanguage('en')
  assert.equal(env.i18n.t(page.subjects.value[0]), 'Physics')
  assert.equal(env.i18n.t(page.modules.value[0]), 'Optics')
  await page.startExam()
  assert.equal(request.subjects[0], '物理')
  assert.equal(request.knowledgeModules[0], '光学')
  assert.equal(request.knowledgePoints[0], '折射')
})

test('native editable dialogs translate controls while preserving user text', () => {
  const env = environment({ system: 'en' })
  env.load('i18n/ui').showModal({ title: '修改昵称', editable: true, content: '关于', placeholderText: '输入昵称' })
  assert.equal(env.modals[0].title, 'Edit name')
  assert.equal(env.modals[0].content, '关于')
  assert.equal(env.modals[0].confirmText, 'Confirm')
  assert.equal(env.modals[0].cancelText, 'Cancel')
})

const assert = require('node:assert/strict')
const test = require('node:test')
const pinia = require('pinia')
const { createLoader } = require('./helpers/load-source.cjs')

function environment(saved = new Map()) {
  const calls = [], modals = [], navigation = []
  let response, loginCalls = 0
  let route = 'pages/index/index'
  const uni = {
    getStorageSync: key => saved.get(key), setStorageSync: (key, value) => saved.set(key, value),
    removeStorageSync: key => saved.delete(key), showToast() {}, showLoading() {}, hideLoading() {},
    login: options => { loginCalls++; options.success({ code: 'explicit-code' }) },
    request: options => { calls.push(options); response?.(options) },
    navigateTo: options => navigation.push(options.url),
    navigateBack: options => options?.success?.(), redirectTo: options => navigation.push(options.url),
    showModal: options => modals.push(options),
  }
  const load = createLoader({ pinia }, { uni, getCurrentPages: () => [{ route: 'pages/index/index' }, { route }] })
  const session = load('shared/auth/session')
  const api = load('api/client')
  pinia.setActivePinia(pinia.createPinia())
  return { load, api, session, uni, calls, modals, navigation, saved,
    get loginCalls() { return loginCalls }, respond: handler => { response = handler }, setRoute: value => { route = value } }
}
const profile = (id = 7) => ({ id, user_code: `lw00${id}`, nickname: '中文昵称', avatar_url: null,
  target_exam: 'CSCA', target_dates: {}, total_questions: 4, total_correct: 3, total_objective: 4,
  correct_rate: 75, streak_days: 1, favorite_count: 0 })
const success = (options, data) => options.success({ statusCode: 200, data: { code: 0, data } })

test('avatar uploads use the API host and distinguish the uploadFile domain allowlist', async () => {
  const env = environment()
  env.session.establishSession('upload-token', 7)
  let upload
  env.uni.uploadFile = options => { upload = options; options.fail({ errMsg: 'uploadFile:fail url not in domain list' }) }
  const userApi = env.load('features/user/api').userApi
  await assert.rejects(userApi.uploadAvatar('wxfile://selected-avatar.jpg'), error =>
    error.code === 'DOMAIN_NOT_CONFIGURED' && error.message === '上传域名未配置')
  assert.equal(upload.url, 'https://api.example.com/api/v1/user/avatar')
  assert.equal(upload.filePath, 'wxfile://selected-avatar.jpg')
  assert.equal(upload.name, 'file')
  assert.equal(upload.header.Authorization, 'Bearer upload-token')
  assert.equal(env.session.getToken(), 'upload-token')
  env.load('i18n').setLanguage('en')
  assert.equal(env.load('i18n').errorText('上传域名未配置'), 'Upload server domain is not configured')
})

test('a failed avatar upload from an old session cannot report a new account error', async () => {
  const env = environment()
  env.session.establishSession('old-upload-token', 7)
  let upload
  env.uni.uploadFile = options => { upload = options }
  const pending = env.api.upload('/user/avatar', 'wxfile://avatar.jpg')
  env.session.clearSession()
  env.session.establishSession('other-token', 8)
  upload.fail({ errMsg: 'uploadFile:fail url not in domain list' })
  await assert.rejects(pending, error => error.code === 'SESSION_CHANGED')
  assert.equal(env.session.getToken(), 'other-token')
})

test('guest requests never invoke WeChat login or send protected network calls', async () => {
  const env = environment()
  const user = env.load('stores/user').useUserStore()
  await user.restoreSession()
  assert.equal(user.isLogin, false)
  await assert.rejects(env.api.request({ url: '/question/papers' }), error => error.code === 'AUTH_REQUIRED')
  assert.equal(env.calls.length, 0)
  assert.equal(env.loginCalls, 0)
  env.respond(options => success(options, []))
  await env.api.request({ url: '/content/announcements', requireAuth: false })
  assert.equal(env.calls.length, 1)
})

test('valid stored session restores profile without silent WeChat login; explicit logout stays guest', async () => {
  const env = environment(new Map([['token', 'saved-token']]))
  const user = env.load('stores/user').useUserStore()
  env.respond(options => success(options, profile()))
  await Promise.all([user.restoreSession(), user.restoreSession()])
  assert.equal(env.calls.length, 1)
  assert.equal(user.isLogin, true)
  assert.equal(user.userInfo.userCode, 'lw007')
  assert.equal(env.loginCalls, 0)
  user.logout()
  await user.restoreSession()
  assert.equal(user.isLogin, false)
  assert.equal(user.userInfo.id, 0)
  assert.equal(env.saved.has('token'), false)
  assert.equal(env.calls.length, 1)
})

test('401 clears credentials without relogin/retry, and passive restore does not prompt', async () => {
  const env = environment(new Map([['token', 'expired']]))
  let prompts = 0
  env.session.configureLoginPrompt(() => prompts++)
  const user = env.load('stores/user').useUserStore()
  env.respond(options => options.success({ statusCode: 401, data: { detail: '过期' } }))
  await user.restoreSession()
  assert.equal(prompts, 0)
  assert.equal(user.isLogin, false)
  assert.equal(env.calls.length, 1)
  assert.equal(env.loginCalls, 0)
  assert.equal(env.saved.has('token'), false)
})

test('a pending response cannot restore credentials or data after logout', async () => {
  const env = environment(new Map([['token', 'saved']]))
  const user = env.load('stores/user').useUserStore()
  const restoring = user.restoreSession()
  user.logout()
  success(env.calls[0], profile())
  await restoring
  assert.equal(user.isLogin, false)
  assert.equal(user.userInfo.nickname, '留学同学')
  const login = user.login()
  await Promise.resolve()
  user.logout()
  success(env.calls[1], { token: 'new-token', openid: 'wx', user: profile() })
  await assert.rejects(login, /登录已取消/)
  assert.equal(env.saved.has('token'), false)
})

test('user-initiated login runs WeChat once and profile updates remain shared', async () => {
  const env = environment()
  const user = env.load('stores/user').useUserStore()
  env.respond(options => success(options, { token: 'new-token', openid: 'wx', user: profile() }))
  await user.login('中文昵称')
  assert.equal(env.loginCalls, 1)
  assert.equal(env.calls[0].data.nickname, '中文昵称')
  assert.equal(user.isLogin, true)
  user.applyProfile({ ...profile(), nickname: '新昵称', avatar_url: '/api/v1/user/avatar/avatar.jpg' })
  assert.equal(user.userInfo.nickname, '新昵称')
  assert.equal(user.userInfo.avatarUrl, 'https://api.example.com/api/v1/user/avatar/avatar.jpg')
})

test('practice snapshots and exam preferences are isolated and recover only for their owner', () => {
  const env = environment()
  const user = env.load('stores/user').useUserStore()
  const exam = env.load('stores/exam').useExamStore()
  env.session.establishSession('a', 7)
  user.setSelectedExams(['HKS'])
  exam.setPaper(12, [{ id: 1, stem: '原始中文题目', type: 'single' }])
  exam.start()
  exam.setAnswer(0, 'A')
  env.session.clearSession()
  assert.equal(exam.questions.length, 0)
  assert.equal(exam.hasActiveProgress, false)
  assert.equal(env.saved.get('exam_active_progress_v3_7').ownerId, 7)
  env.session.establishSession('b', 8)
  assert.equal(exam.questions.length, 0)
  assert.equal(user.selectedExams.length, 0)
  env.session.establishSession('a', 7)
  assert.equal(exam.paperId, 12)
  assert.equal(exam.answers[0], 'A')
  assert.equal(user.selectedExams.join(','), 'HKS')
})

test('cached page data and in-flight loading clear on account changes', async () => {
  const env = environment()
  const state = env.load('shared/composables/useAsyncState').useAsyncState(null)
  let resolve
  const pending = state.execute(() => new Promise(done => { resolve = done }))
  env.session.establishSession('b', 8)
  resolve({ private: 'account A' })
  await pending
  assert.equal(state.data.value, null)
  assert.equal(state.loading.value, false)
})

test('protected card prompts first and resumes its destination after explicit login', async () => {
  const env = environment()
  const user = env.load('stores/user').useUserStore()
  const navigation = env.load('shared/auth/navigation')
  await navigation.navigateProtected('/pages/feedback/index')
  assert.equal(env.navigation.length, 0)
  assert.equal(env.modals[0].title, '登录后即可使用')
  assert.equal(env.modals[0].confirmText, '去登录')
  env.modals[0].success({ confirm: true })
  env.modals[0].complete()
  assert.equal(env.navigation[0], '/pages/login/index')
  env.respond(options => success(options, { token: 'token', openid: 'wx', user: profile() }))
  await user.login()
  env.setRoute('pages/login/index')
  navigation.finishLogin()
  await new Promise(resolve => setImmediate(resolve))
  assert.equal(env.navigation.at(-1), '/pages/feedback/index')
})

test('login controls have English labels while profile content remains original', () => {
  const env = environment()
  const i18n = env.load('i18n')
  i18n.setLanguage('en')
  assert.equal(i18n.t('登录后即可使用'), 'Sign in to continue')
  assert.equal(i18n.t('返回'), 'Back')
  assert.equal(i18n.t('填写昵称，可稍后完善'), 'Enter a nickname, or add one later')
})

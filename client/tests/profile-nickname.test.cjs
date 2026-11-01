const assert = require('node:assert/strict')
const test = require('node:test')
const { reactive, ref, effectScope } = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')

function environment(update, getProfile) {
  const calls = [], navigation = [], toasts = []
  const activeUserId = ref(7)
  let generation = 0
  const user = reactive({
    isLogin: true, selectedExams: [],
    userInfo: { id: 7, userCode: 'lw007', nickname: '原来的昵称', targetExam: 'CSCA', targetDates: {} },
    applyProfile(value) { Object.assign(this.userInfo, value) },
    async restoreSession() {},
  })
  const load = createLoader({
    '@dcloudio/uni-app': { onShow() {}, onShareAppMessage() {} },
    '@/i18n/page': { usePageI18n() {} },
    '@/constants/share': { createAppShareMessage() {} },
    '@/api/contracts': { toDashboardData: value => value },
    '@/stores/user': { useUserStore: () => user },
    '@/shared/auth/session': { activeUserId, sessionGeneration: () => generation },
    '@/shared/auth/navigation': { openLogin: () => navigation.push('login'), navigateProtected() {}, requireLogin: async () => user.isLogin },
    '@/features/user/api': { userApi: { getUserInfo: async () => getProfile(), updateProfile: async payload => {
      calls.push(payload)
      return update ? update(payload) : { nickname: payload.nickname }
    } } },
  }, { uni: { showToast: value => toasts.push(value), getStorageSync() {} } })
  const scope = effectScope()
  const page = scope.run(() => load('pages/profile/index.vue').default.setup({}, { expose() {} }))
  return { page, user, calls, navigation, toasts, dispose: () => scope.stop(),
    logout() { generation++; user.isLogin = false; activeUserId.value = 0; user.userInfo = { id: 0, nickname: '留学同学', targetDates: {} } } }
}
const input = value => ({ detail: { value } })

test('nickname edits stay in place; cancel preserves profile and WeChat quick-fill saves the shared name', async t => {
  const env = environment()
  t.after(env.dispose)
  await env.page.editNickname()
  assert.equal(env.navigation.length, 0)
  assert.equal(env.page.nicknameFocused.value, true)
  assert.equal(env.page.nicknameDraft.value, '原来的昵称')
  env.page.onNicknameInput(input('取消的内容'))
  env.page.onNicknameBlur(input('取消的内容'))
  env.page.cancelNicknameEdit()
  assert.equal(env.user.userInfo.nickname, '原来的昵称')
  assert.equal(env.calls.length, 0)
  await env.page.editNickname()
  // Native nickname quick-fill may deliver its final value on blur.
  env.page.onNicknameBlur(input('  微信昵称  '))
  await env.page.saveNickname()
  assert.equal(env.calls[0].nickname, '微信昵称')
  assert.equal(env.user.userInfo.nickname, '微信昵称')
  assert.equal(env.user.userInfo.userCode, 'lw007')
  assert.equal(env.page.editingNickname.value, false)
})

test('empty and rejected names never save, and pending saves cannot double-submit or cancel', async t => {
  let resolve
  const env = environment(() => new Promise(done => { resolve = done }))
  t.after(env.dispose)
  await env.page.editNickname()
  env.page.onNicknameInput(input(' '))
  await env.page.saveNickname()
  env.page.onNicknameInput(input('待审核'))
  env.page.reviewNickname({ detail: { pass: false } })
  await env.page.saveNickname()
  assert.equal(env.calls.length, 0)
  env.page.onNicknameInput(input('新昵称'))
  const pending = env.page.saveNickname()
  await env.page.saveNickname()
  env.page.cancelNicknameEdit()
  assert.equal(env.calls.length, 1)
  assert.equal(env.page.editingNickname.value, true)
  resolve({ nickname: '新昵称' })
  await pending
  assert.equal(env.user.userInfo.nickname, '新昵称')
})

test('failed saves keep the draft for retry without changing the displayed profile', async t => {
  let fail = true
  const env = environment(async payload => { if (fail) throw new Error('网络异常'); return payload })
  t.after(env.dispose)
  await env.page.editNickname()
  env.page.onNicknameInput(input('保留的草稿'))
  await env.page.saveNickname()
  assert.equal(env.user.userInfo.nickname, '原来的昵称')
  assert.equal(env.page.nicknameDraft.value, '保留的草稿')
  assert.equal(env.page.nicknameError.value, '网络异常')
  assert.equal(env.page.editingNickname.value, true)
  fail = false
  await env.page.saveNickname()
  assert.equal(env.user.userInfo.nickname, '保留的草稿')
})

test('logout discards an in-flight nickname response and clears the editor', async t => {
  let resolve
  const env = environment(() => new Promise(done => { resolve = done }))
  t.after(env.dispose)
  await env.page.editNickname()
  env.page.onNicknameInput(input('旧账号昵称'))
  const pending = env.page.saveNickname()
  env.logout()
  resolve({ nickname: '旧账号昵称' })
  await pending
  assert.equal(env.user.userInfo.nickname, '留学同学')
  assert.equal(env.page.editingNickname.value, false)
  assert.equal(env.page.savingNickname.value, false)
  assert.equal(env.page.nicknameDraft.value, '')
  assert.equal(env.toasts.length, 0)
})

test('a slow profile refresh cannot overwrite a nickname that was just saved', async t => {
  let resolve
  const env = environment(undefined, () => new Promise(done => { resolve = done }))
  t.after(env.dispose)
  const refreshing = env.page.loadProfile()
  await env.page.editNickname()
  env.page.onNicknameInput(input('已经保存的新昵称'))
  await env.page.saveNickname()
  resolve({ nickname: '原来的昵称' })
  await refreshing
  assert.equal(env.user.userInfo.nickname, '已经保存的新昵称')
})

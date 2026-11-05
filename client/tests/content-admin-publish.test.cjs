const assert = require('node:assert/strict')
const test = require('node:test')
const vue = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')

const announcement = (overrides = {}) => ({ id: 9, category: 'notice', title: '版本更新', summary: '更新摘要',
  body: '更新正文', release_version: '1.6.0', is_active: false, published_at: null, sort_order: 0, ...overrides })

function environment(role = 'owner') {
  const calls = [], toasts = [], modals = []
  let session, fail = false
  const user = vue.reactive({ isLogin: true, isAdmin: vue.computed(() => session.adminRole.value !== 'user'),
    isOwner: vue.computed(() => session.adminRole.value === 'owner'),
    async restoreSession() {}, async refreshProfile() {},
  })
  const contentApi = {
    listAdmin: async () => [],
    create: async payload => {
      calls.push({ action: 'create', payload: { ...payload } })
      if (fail) throw { message: '网络异常' }
      return announcement(payload)
    },
    update: async (id, payload) => {
      calls.push({ action: 'update', id, payload: { ...payload } })
      if (fail) throw { message: '网络异常' }
      return announcement({ ...payload, id })
    },
  }
  const load = createLoader({
    '@/stores/user': { useUserStore: () => user }, '@/features/content/api': { contentApi },
    '@/constants/brand': { APP_VERSION: '1.6.0' }, '@/i18n/page': { usePageI18n() {} },
    '@dcloudio/uni-app': { onShow() {} },
  }, { uni: { getStorageSync() {}, setStorageSync() {}, removeStorageSync() {}, showToast: value => toasts.push(value), showModal: value => modals.push(value) } })
  session = load('shared/auth/session')
  session.establishSession('owner-test-token', 7)
  session.setAdminRole(role)
  const scope = vue.effectScope()
  const page = scope.run(() => load('pages/content-admin/index.vue').default.setup({}, { expose() {} }))
  function fill() {
    Object.assign(page.form, { category: 'notice', title: '版本更新', summary: '更新摘要', body: '更新正文', release_version: '1.6.0' })
    page.isAnnouncement.value = true
  }
  return { page, calls, toasts, modals, fill, session, failWrites: () => { fail = true }, dispose: () => scope.stop() }
}

test('new announcements have distinct save-draft and publish operations without a switch', async t => {
  for (const publish of [false, true]) {
    const env = environment()
    t.after(env.dispose)
    env.fill()
    await env.page.save(publish)
    assert.equal(env.calls.length, 1)
    assert.equal(env.calls[0].payload.is_active, publish)
    assert.equal(env.calls[0].payload.release_version, '1.6.0')
    assert.equal(env.calls[0].payload.published_at, null)
    assert.equal(env.page.form.title, '')
    assert.equal(env.toasts.at(-1).title, publish ? '已发布' : '已保存')
  }
})

test('publishing an edited draft requests immediate publication rather than retaining a future date', async t => {
  const env = environment()
  t.after(env.dispose)
  env.page.edit(announcement({ published_at: '2099-01-01T00:00:00Z' }))
  await env.page.save(true)
  assert.equal(env.calls[0].action, 'update')
  assert.equal(env.calls[0].id, 9)
  assert.equal(env.calls[0].payload.is_active, true)
  assert.equal(env.calls[0].payload.published_at, null)
})

test('an existing saved draft can be published directly without copying its text to the editor', async t => {
  const env = environment()
  t.after(env.dispose)
  await env.page.publish(announcement())
  assert.equal(env.calls.length, 1)
  assert.equal(env.calls[0].id, 9)
  assert.deepEqual(env.calls[0].payload, { is_active: true, published_at: null })
})

test('saving changes to a published announcement preserves its publication date', async t => {
  const env = environment()
  t.after(env.dispose)
  env.page.edit(announcement({ is_active: true, published_at: '2026-11-02T00:00:00Z' }))
  env.page.form.body = '修改后的正文'
  await env.page.save(true)
  assert.equal(env.calls[0].payload.body, '修改后的正文')
  assert.equal(env.calls[0].payload.is_active, true)
  assert.equal(env.calls[0].payload.published_at, '2026-11-02T00:00:00Z')
})

test('withdrawing requires confirmation and preserves text being edited', async t => {
  const env = environment()
  t.after(env.dispose)
  const item = announcement({ is_active: true, published_at: '2026-11-02T00:00:00Z' })
  env.page.edit(item)
  env.page.form.body = '尚未保存的修改'
  env.page.withdraw(item)
  assert.equal(env.calls.length, 0)
  await env.modals[0].success({ confirm: false })
  assert.equal(env.calls.length, 0)
  env.page.withdraw(item)
  await env.modals[1].success({ confirm: true })
  assert.deepEqual(env.calls[0].payload, { is_active: false })
  assert.equal(env.page.form.is_active, false)
  assert.equal(env.page.form.body, '尚未保存的修改')
})

test('viewers cannot save or publish, and failed publication preserves an owner draft', async t => {
  const viewer = environment('viewer')
  const owner = environment()
  t.after(viewer.dispose)
  t.after(owner.dispose)
  viewer.fill()
  await viewer.page.save(true)
  await viewer.page.publish(announcement())
  assert.equal(viewer.calls.length, 0)
  owner.fill()
  owner.failWrites()
  await owner.page.save(true)
  assert.equal(owner.page.form.body, '更新正文')
  assert.equal(owner.page.form.is_active, false)
  assert.equal(owner.toasts.length, 0)
  assert.equal(owner.page.loadError.value, '网络异常')
  assert.equal(owner.page.saving.value, false)
})

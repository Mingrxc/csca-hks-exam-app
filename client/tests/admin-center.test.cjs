const assert = require('node:assert/strict')
const test = require('node:test')
const { reactive, computed, effectScope } = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')

function environment(role = 'user') {
  const hooks = [], calls = [], storage = new Map()
  let session, responseRole = role
  const user = reactive({
    isLogin: true,
    isAdmin: computed(() => session.adminRole.value !== 'user'),
    isOwner: computed(() => session.adminRole.value === 'owner'),
    async restoreSession() {}, async refreshProfile() { calls.push('profile'); session.setAdminRole(responseRole) },
  })
  const load = createLoader({
    '@/stores/user': { useUserStore: () => user },
    '@dcloudio/uni-app': { onShow: callback => hooks.push(callback) },
  }, { uni: { getStorageSync: key => storage.get(key), setStorageSync: (key, value) => storage.set(key, value), removeStorageSync: key => storage.delete(key) } })
  session = load('shared/auth/session')
  session.establishSession('test-token', 7)
  session.setAdminRole(role)
  const scope = effectScope()
  return { load, user, session, calls, hooks,
    page(initial, fetcher, ownerOnly = false) { return scope.run(() => load('features/admin/useAdminPage').useAdminPage(initial, fetcher, ownerOnly)) },
    setResponseRole(value) { responseRole = value }, dispose: () => scope.stop() }
}

test('ordinary users fetch no management data even with a direct route, and viewers cannot open owner pages', async t => {
  for (const role of ['user', 'viewer']) {
    const env = environment(role)
    t.after(env.dispose)
    let reads = 0
    const page = env.page([], async () => { reads++; return ['private'] }, role === 'viewer')
    await page.load()
    assert.equal(page.allowed.value, false)
    assert.equal(page.data.value.length, 0)
    assert.equal(reads, 0)
  }
})

test('viewers read full feedback but never invoke a write request', async t => {
  const env = environment('viewer')
  t.after(env.dispose)
  let writes = 0
  const page = env.page([], async () => [{ content: '用户反馈原文' }])
  await page.load()
  assert.equal(page.data.value[0].content, '用户反馈原文')
  await page.write(async () => { writes++; return true })
  assert.equal(writes, 0)
})

test('revocation clears already displayed feedback and discards pending results', async t => {
  const env = environment('viewer')
  t.after(env.dispose)
  let resolve, count = 0
  const page = env.page([], () => ++count === 1 ? Promise.resolve(['反馈全文']) : new Promise(done => { resolve = done }))
  await page.load()
  assert.equal(page.data.value.length, 1)
  env.session.setAdminRole('user')
  assert.equal(page.data.value.length, 0)
  assert.equal(page.allowed.value, false)
  env.session.setAdminRole('viewer')
  const pending = page.load()
  await new Promise(done => setImmediate(done))
  env.session.setAdminRole('user')
  resolve(['过期的反馈全文'])
  await pending
  assert.equal(page.data.value.length, 0)
})

test('granting a role is recognized on refresh, and writes are blocked against double submission', async t => {
  const env = environment()
  t.after(env.dispose)
  const page = env.page([], async () => ['管理数据'])
  env.setResponseRole('owner')
  await page.load()
  assert.equal(page.allowed.value, true)
  let writes = 0, resolve
  const pending = page.write(() => { writes++; return new Promise(done => { resolve = done }) })
  await page.write(async () => { writes++; return true })
  assert.equal(writes, 1)
  resolve(true)
  assert.equal(await pending, true)
})

test('switching accounts discards old management data and pending writes', async t => {
  const env = environment('owner')
  t.after(env.dispose)
  const page = env.page([], async () => ['账号A的数据'])
  await page.load()
  let resolve
  const pending = page.write(() => new Promise(done => { resolve = done }))
  env.session.clearSession()
  env.user.isLogin = false
  resolve({ changed: true })
  assert.equal(await pending, undefined)
  assert.equal(page.data.value.length, 0)
  assert.equal(page.allowed.value, false)
})

test('an earlier overlapping refresh cannot replace a newer result or end its spinner', async t => {
  const env = environment('viewer')
  t.after(env.dispose)
  const resolvers = []
  const page = env.page([], () => new Promise(done => resolvers.push(done)))
  const first = page.load()
  await new Promise(done => setImmediate(done))
  const second = page.load()
  await new Promise(done => setImmediate(done))
  resolvers[0](['旧请求'])
  await first
  assert.equal(page.loading.value, true)
  assert.equal(page.data.value.length, 0)
  resolvers[1](['新请求'])
  await second
  assert.equal(page.data.value[0], '新请求')
})

test('failed user-list requests end loading and allow retry', async t => {
  const env = environment('viewer')
  t.after(env.dispose)
  let failing = true
  const page = env.page({ items: [], total: 0 }, async () => {
    if (failing) throw { message: '请求超时' }
    return { items: [{ user_code: 'lw007' }], total: 1 }
  })
  await page.load()
  assert.equal(page.loading.value, false)
  assert.equal(page.error.value, '请求超时')
  failing = false
  await page.load()
  assert.equal(page.loading.value, false)
  assert.equal(page.error.value, '')
  assert.equal(page.data.value.items[0].user_code, 'lw007')
})

test('the real user store exposes the management entry only for verified administrator sessions', () => {
  const pinia = require('pinia')
  pinia.setActivePinia(pinia.createPinia())
  const load = createLoader({ pinia, '@/features/user/api': { userApi: {} } }, {
    uni: { getStorageSync() {}, setStorageSync() {}, removeStorageSync() {} },
  })
  const session = load('shared/auth/session')
  const user = load('stores/user').useUserStore()
  session.setAdminRole('owner')
  assert.equal(user.isAdmin, false)
  const profile = { id: 7, user_code: 'lw007', nickname: '用户', target_exam: 'CSCA', total_questions: 0, total_correct: 0, correct_rate: 0, streak_days: 0, favorite_count: 0 }
  user.applyProfile({ ...profile, admin_role: 'viewer' })
  session.establishSession('verified-token', 7)
  assert.equal(user.isAdmin, true)
  assert.equal(user.isOwner, false)
  user.applyProfile({ ...profile, admin_role: 'owner' })
  assert.equal(user.isOwner, true)
  user.applyProfile({ ...profile, admin_role: 'user' })
  assert.equal(user.isAdmin, false)
  user.logout()
  assert.equal(session.adminRole.value, 'user')
})

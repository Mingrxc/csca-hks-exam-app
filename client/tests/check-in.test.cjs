const assert = require('node:assert/strict')
const test = require('node:test')
const vue = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')

const pending = () => {
  let resolve, reject
  const promise = new Promise((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
const status = checked => ({ today: '2026-11-01', checked_in: checked, streak_days: checked ? 1 : 0,
  week: Array.from({ length: 7 }, (_, i) => ({ date: i === 6 ? '2026-11-01' : `2026-10-${26 + i}`, checked: checked && i === 6 })) })
const dashboard = checked => ({ user_name: '同学', target_exam: 'HKS', today_stats: { question_count: 0, correct_rate: 0, wrong_count: 0 },
  pending_wrong_count: 0, favorite_count: 0, recent_papers: [], check_in: status(checked) })

function home(api) {
  const identity = vue.ref(7)
  const load = createLoader({
    '@/features/user/api': { userApi: api }, '@/features/content/api': { contentApi: {} },
    '@/shared/auth/session': { activeUserId: identity },
    '@/constants/exam': { DIFFICULTY_MAP: {}, QUESTION_TYPE_MAP: {} },
    '@/api/client': { resolveMediaUrl: value => value },
  }, { Error })
  const scope = vue.effectScope()
  const page = scope.run(() => load('features/home/useHomePage').useHomePage())
  return { page, identity, stop: () => scope.stop() }
}

test('guest calendar uses Beijing dates and Monday-Sunday across year and day boundaries', () => {
  const { beijingDate, emptyCheckInWeek } = createLoader()('features/home/checkInCalendar')
  assert.equal(beijingDate(Date.parse('2026-11-01T15:59:59Z')), '2026-11-01')
  assert.equal(beijingDate(Date.parse('2026-11-01T16:00:00Z')), '2026-11-02')
  const dates = now => Array.from(emptyCheckInWeek(Date.parse(now)), day => day.date)
  assert.deepEqual(dates('2026-11-01T16:00:00Z'), ['2026-11-02', '2026-11-03', '2026-11-04', '2026-11-05', '2026-11-06', '2026-11-07', '2026-11-08'])
  assert.deepEqual(dates('2026-01-01T00:00:00Z'), ['2025-12-29', '2025-12-30', '2025-12-31', '2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04'])
})

test('home reads saved week, suppresses duplicate clicks, and marks only a successful check-in', async () => {
  const request = pending()
  let calls = 0
  const env = home({ getDashboard: async () => dashboard(false), checkIn: () => { calls++; return request.promise } })
  try {
    await env.page.loadDashboard(true)
    assert.equal(env.page.checkInState.data.value.checkedIn, false)
    const first = env.page.checkIn()
    await env.page.checkIn()
    assert.equal(calls, 1)
    assert.equal(env.page.checkInState.data.value.checkedIn, false)
    request.resolve(status(true))
    await first
    assert.equal(env.page.checkInState.data.value.streakDays, 1)
    assert.equal(env.page.checkInState.data.value.week[6].checked, true)
  } finally { env.stop() }
})

for (const refreshDuringPost of [false, true]) {
  test(`dashboard refresh cannot roll back a check-in (${refreshDuringPost ? 'during' : 'before'} POST)`, async () => {
    const get = pending(), post = pending()
    const env = home({ getDashboard: () => get.promise, checkIn: () => post.promise })
    try {
      let loading, signing
      if (refreshDuringPost) { signing = env.page.checkIn(); loading = env.page.loadDashboard(true) }
      else { loading = env.page.loadDashboard(true); signing = env.page.checkIn() }
      post.resolve(status(true))
      await signing
      get.resolve(dashboard(false))
      await loading
      assert.equal(env.page.checkInState.data.value.checkedIn, true)
      assert.equal(env.page.checkInState.data.value.streakDays, 1)
    } finally { env.stop() }
  })
}

test('account switching discards a late check-in and guest viewing makes no API request', async () => {
  const post = pending()
  const env = home({ getDashboard: () => { throw new Error('Guest must not fetch private data') }, checkIn: () => post.promise })
  try {
    const signing = env.page.checkIn()
    env.identity.value = 0
    await env.page.loadDashboard(false)
    post.resolve(status(true))
    assert.equal(await signing, undefined)
    assert.equal(env.page.checkInState.data.value, null)
    assert.equal(env.page.checkInState.loading.value, false)
    assert.equal(env.page.dashboardState.data.value, null)
  } finally { env.stop() }
})

test('failed save leaves the day unchecked and can be retried', async () => {
  let failing = true
  const env = home({ getDashboard: async () => dashboard(false), checkIn: async () => {
    if (failing) throw new Error('offline')
    return status(true)
  } })
  try {
    await env.page.loadDashboard(true)
    await env.page.checkIn()
    assert.equal(env.page.checkInState.error.value, 'offline')
    assert.equal(env.page.checkInState.data.value.checkedIn, false)
    failing = false
    await env.page.checkIn()
    assert.equal(env.page.checkInState.data.value.checkedIn, true)
    assert.equal(env.page.checkInState.error.value, '')
  } finally { env.stop() }
})

test('home check-in button sends a guest through the existing login guard', async () => {
  let guards = 0, posts = 0
  const env = home({ checkIn: () => { posts++; return Promise.resolve(status(true)) } })
  const load = createLoader({
    '@/i18n': { t: key => key, language: vue.ref('zh') }, '@/i18n/page': { usePageI18n() {} },
    '@dcloudio/uni-app': { onShow() {}, onShareAppMessage() {}, onShareTimeline() {} },
    '@/constants/share': { isTimelinePreview: () => false }, '@/components/TimelinePreview/index.vue': {},
    '@/constants/exam': { getExamLabel: value => value, getPaperTitle: value => value },
    '@/stores/user': { useUserStore: () => ({ isLogin: false, userInfo: {} }) },
    '@/stores/exam': { useExamStore: () => ({}) },
    '@/features/home/useHomePage': { useHomePage: () => env.page },
    '@/features/exam/useExamNavigation': { useExamNavigation: () => ({}) },
    '@/shared/auth/navigation': { requireLogin: async () => { guards++; return false } },
  })
  try {
    const page = load('pages/index/index.vue').default.setup({}, { expose() {} })
    await page.handleCheckIn()
    assert.equal(guards, 1)
    assert.equal(posts, 0)
  } finally { env.stop() }
})

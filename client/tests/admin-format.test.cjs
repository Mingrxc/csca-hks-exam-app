const assert = require('node:assert/strict')
const test = require('node:test')
const { ref } = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')

function formatter(intl) {
  const language = ref('zh')
  const load = createLoader({ '@/i18n': { language } }, { Intl: intl })
  return { language, adminDate: load('features/admin/format').adminDate }
}

test('management dates render without Intl, using Beijing time for both languages', () => {
  const { language, adminDate } = formatter(undefined)
  assert.equal(adminDate('2026-11-03T02:14:10Z'), '2026/11/03 10:14')
  language.value = 'en'
  assert.equal(adminDate('2026-11-03T02:14:10Z'), '03/11/2026 10:14')
})

test('partial Intl implementations cannot break a populated user list', () => {
  const { adminDate } = formatter({ DateTimeFormat: function () { throw new RangeError('Unsupported time zone') } })
  const users = [
    { created_at: '2026-11-02T16:01:00Z', last_study_at: '2026-11-03T10:00:00+08:00' },
    { created_at: '2026-11-03T00:00:00Z', last_study_at: null },
  ]
  assert.deepEqual(users.map(user => [adminDate(user.created_at), adminDate(user.last_study_at)]), [
    ['2026/11/03 00:01', '2026/11/03 10:00'], ['2026/11/03 08:00', '—'],
  ])
})

test('UTC-naive dates, explicit offsets, year changes and invalid values stay safe', () => {
  const { adminDate } = formatter(undefined)
  assert.equal(adminDate('2026-12-31T16:00:00'), '2027/01/01 00:00')
  assert.equal(adminDate('2026-11-03 02:14:10'), '2026/11/03 10:14')
  assert.equal(adminDate('2026-11-03T02:14:10+00:00'), '2026/11/03 10:14')
  assert.equal(adminDate('2026-11-03T10:14:10+08:00'), '2026/11/03 10:14')
  for (const value of [undefined, null, '', 'not-a-date']) assert.equal(adminDate(value), '—')
})

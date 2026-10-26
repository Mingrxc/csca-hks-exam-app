const assert = require('node:assert/strict')
const test = require('node:test')
const vue = require('vue')
const { createLoader } = require('./helpers/load-source.cjs')

function load(file, mocks = {}, globals = {}) {
  return createLoader(mocks, globals)(file)
}

test('question mapping preserves media, task, level and scoring metadata', () => {
  const { toQuestion } = load('api/contracts.ts')
  const mapped = toQuestion({ id: 1, exam_type: 'HKS', exam_version: 'HSK3.0', level: '7-9', subject: '翻译', question_type: 'fill', difficulty: 'hard', stem_text: 'Translate', options: [{ key: 'A', text: '图片A', image: '/api/v1/question/media/HSK/_assets/images/cup.png' }], stem_audio: '/api/v1/question/media/HSK/_assets/audio/test.wav', response_mode: 'translation', max_score: 10, grading_key_points: ['意义准确'] })
  assert.equal(mapped.examVersion, 'HSK3.0')
  assert.equal(mapped.level, '7-9')
  assert.equal(mapped.responseMode, 'translation')
  assert.equal(mapped.stemAudio, 'https://api.example.com/api/v1/question/media/HSK/_assets/audio/test.wav')
  assert.equal(mapped.options[0].image, 'https://api.example.com/api/v1/question/media/HSK/_assets/images/cup.png')
  assert.equal(mapped.gradingKeyPoints[0], '意义准确')
  assert.equal(mapped.answer, undefined)
  assert.equal(mapped.transcript, undefined)
})

function component() {
  const beforeUnmount = [], hidden = [], contexts = []
  const props = vue.reactive({ question: { id: 1, examType: 'HKS', type: 'single', difficulty: 'easy', stem: 'Listen', options: [], stemAudio: 'https://example.com/test.wav', responseMode: 'choice' }, index: 0, userAnswer: '', showResult: false })
  const module = load('components/QuestionItem/index.vue', {
    vue: { ...vue, onBeforeUnmount: fn => beforeUnmount.push(fn) },
    '@dcloudio/uni-app': { onHide: fn => hidden.push(fn) },
  }, { uni: { createInnerAudioContext() {
    const context = { playCount: 0, pauseCount: 0, destroyCount: 0, stop() {}, destroy() { this.destroyCount++ }, play() { this.playCount++; this.played?.() }, pause() { this.pauseCount++; this.paused?.() }, onPlay(fn) { this.played = fn }, onPause(fn) { this.paused = fn }, onEnded(fn) { this.ended = fn }, onTimeUpdate(fn) { this.time = fn }, onError(fn) { this.error = fn } }
    contexts.push(context); return context
  }, previewImage() {} } })
  const page = module.default.setup(props, { expose() {}, emit() {} })
  return { page, props, contexts, beforeUnmount, hidden }
}

test('audio pauses, stops on question change and destroys on leaving', async () => {
  const { page, props, contexts, beforeUnmount, hidden } = component()
  page.toggleAudio()
  assert.equal(page.playing.value, true)
  page.toggleAudio()
  assert.equal(contexts[0].pauseCount, 1)
  page.toggleAudio(); hidden.forEach(fn => fn())
  assert.equal(page.playing.value, false)
  props.question = { ...props.question, id: 2 }
  await vue.nextTick()
  assert.equal(contexts[0].destroyCount, 1)
  page.toggleAudio()
  beforeUnmount.forEach(fn => fn())
  assert.equal(contexts[1].destroyCount, 1)
})

test('audio failures allow retry with a fresh audio context', () => {
  const { page, contexts } = component()
  page.toggleAudio(); contexts[0].error()
  assert.equal(page.playing.value, false)
  assert.match(page.audioError.value, /重试/)
  page.toggleAudio()
  assert.equal(contexts.length, 2)
  assert.equal(page.audioError.value, '')
})

test('only expressive tasks show self assessment', () => {
  const { page, props } = component()
  props.question.responseMode = 'character'
  assert.equal(page.selfReview.value, false)
  props.question.responseMode = 'essay'; props.question.maxScore = 10
  assert.equal(page.selfReview.value, true)
  assert.equal(page.scoreOptions.value.length, 11)
})

function session(submitAnswer) {
  const store = vue.reactive({ config: { mode: 'practice' }, paperId: 1, currentIndex: 0, answers: {}, submitted: {}, answerCorrectness: {}, wrongReasons: {}, questions: [{ id: 11, examType: 'HKS', stem: '写作', type: 'fill', options: [], responseMode: 'essay' }], remainingSeconds: 0,
    get currentQuestion() { return this.questions[this.currentIndex] },
    setAnswer(i, answer) { this.answers[i] = answer }, clearAnswer(i) { delete this.answers[i] },
    markSubmitted(i, correct) { this.submitted[i] = true; if (typeof correct === 'boolean') this.answerCorrectness[i] = correct },
    persistProgress() {}, addElapsed() { return 0 }, setCurrentIndex(i) { this.currentIndex = i }, setWrongReason(i, reason) { this.wrongReasons[i] = reason },
  })
  const module = load('features/exam/useAnswerSession.ts', {
    '@/stores/exam': { useExamStore: () => store }, '@/features/favorite/api': { favoriteApi: {} },
    './api': { examApi: { submitAnswer, selfReview: async () => ({ self_score: 8, evaluation_status: 'self_reviewed' }) } },
  }, { uni: { showToast() {} } })
  return { store, page: module.useAnswerSession() }
}

test('written answer keeps draft until save, receives solution afterwards and supports self review', async () => {
  let finish
  const { store, page } = session(() => new Promise(resolve => { finish = resolve }))
  store.questions[0].isFavorite = true
  page.setDraft('我自己的表达')
  const pending = page.selectOption('我自己的表达')
  page.moveTo(1)
  assert.equal(store.currentIndex, 0)
  assert.equal(store.questions[0].answer, undefined)
  finish({ is_correct: null, evaluation_status: 'awaiting_self_review', solution: { id: 11, exam_type: 'HKS', subject: '写作', question_type: 'fill', difficulty: 'medium', stem_text: '写作', options: [], answer: '范文', response_mode: 'essay', max_score: 10 } })
  await pending
  assert.equal(store.questions[0].answer, '范文')
  assert.equal(store.questions[0].isFavorite, true)
  assert.equal(store.answerCorrectness[0], undefined)
  assert.equal(page.currentWrong.value, false)
  await page.submitSelfReview(8)
  assert.equal(store.questions[0].selfScore, 8)
})

test('failed written submission retains the draft for retry', async () => {
  const { store, page } = session(async () => { throw new Error('offline') })
  page.setDraft('保留草稿')
  await page.selectOption('保留草稿')
  assert.equal(store.answers[0], '保留草稿')
  assert.equal(store.submitted[0], undefined)
  assert.equal(page.isSubmitting.value, false)
})

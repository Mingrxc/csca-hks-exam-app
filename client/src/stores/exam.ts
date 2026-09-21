import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ExamConfig, Question } from '@/types/exam'

export type { ExamConfig, Question } from '@/types/exam'

const PROGRESS_STORAGE_KEY = 'exam_active_progress_v1'
const PROGRESS_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000

interface ExamProgressSnapshot {
  version: 1
  savedAt: number
  config: ExamConfig
  paperId: number
  questions: Question[]
  currentIndex: number
  answers: Record<number, string>
  submitted: Record<number, boolean>
  answerCorrectness: Record<number, boolean>
  wrongReasons: Record<number, string>
  elapsedByQuestion: Record<number, number>
  startTime: number
}

function isProgressSnapshot(value: unknown): value is ExamProgressSnapshot {
  if (!value || typeof value !== 'object') return false
  const snapshot = value as Partial<ExamProgressSnapshot>
  return snapshot.version === 1
    && typeof snapshot.savedAt === 'number'
    && Date.now() - snapshot.savedAt <= PROGRESS_MAX_AGE_MS
    && typeof snapshot.paperId === 'number'
    && Array.isArray(snapshot.questions)
    && snapshot.questions.length > 0
    && typeof snapshot.startTime === 'number'
}

export const useExamStore = defineStore('exam', () => {
  const config = ref<ExamConfig>({
    examType: 'CSCA',
    questionCount: 20,
    difficulty: 'all',
    strategy: 'random',
    knowledgePoints: [],
    mode: 'practice',
    timeLimit: 60,
  })

  const paperId = ref<number | null>(null)
  const questions = ref<Question[]>([])
  const currentIndex = ref(0)
  const answers = ref<Record<number, string>>({})
  const submitted = ref<Record<number, boolean>>({})
  const answerCorrectness = ref<Record<number, boolean>>({})
  const wrongReasons = ref<Record<number, string>>({})
  const elapsedByQuestion = ref<Record<number, number>>({})
  const startTime = ref(0)
  const endTime = ref(0)
  const restoredFromStorage = ref(false)

  const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
  const totalCount = computed(() => questions.value.length)
  const answeredCount = computed(() => Object.keys(answers.value).length)
  const progressPercent = computed(() =>
    totalCount.value ? Math.round((answeredCount.value / totalCount.value) * 100) : 0
  )
  const timeUsed = computed(() => {
    const end = endTime.value || Date.now()
    return Math.floor((end - startTime.value) / 1000)
  })
  const remainingSeconds = computed(() => {
    if (config.value.mode !== 'exam' || !startTime.value) return 0
    const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
    return Math.max(config.value.timeLimit * 60 - elapsed, 0)
  })
  const hasActiveProgress = computed(() => !!paperId.value && questions.value.length > 0 && !endTime.value)

  const correctCount = computed(() => {
    let count = 0
    questions.value.forEach((q, i) => {
      if (answers.value[i] === q.answer) count++
    })
    return count
  })

  function setConfig(c: Partial<ExamConfig>) {
    Object.assign(config.value, c)
    persistProgress()
  }

  function setQuestions(qs: Question[]) {
    questions.value = qs
  }

  function setPaper(id: number, qs: Question[]) {
    paperId.value = id
    setQuestions(qs)
    persistProgress()
  }

  function setCurrentIndex(index: number) {
    if (index >= 0 && index < questions.value.length) {
      currentIndex.value = index
      persistProgress()
    }
  }

  function setAnswer(index: number, answer: string) {
    answers.value[index] = answer
    persistProgress()
  }

  function clearAnswer(index: number) {
    delete answers.value[index]
    delete submitted.value[index]
    delete answerCorrectness.value[index]
    persistProgress()
  }

  function markSubmitted(index: number, correct?: boolean) {
    submitted.value[index] = true
    if (typeof correct === 'boolean') answerCorrectness.value[index] = correct
    persistProgress()
  }

  function setWrongReason(index: number, reason: string) {
    wrongReasons.value[index] = reason
    persistProgress()
  }

  function addElapsed(index: number, seconds: number) {
    elapsedByQuestion.value[index] = (elapsedByQuestion.value[index] || 0) + Math.max(0, seconds)
    persistProgress()
    return elapsedByQuestion.value[index]
  }

  function start() {
    currentIndex.value = 0
    answers.value = {}
    submitted.value = {}
    answerCorrectness.value = {}
    wrongReasons.value = {}
    elapsedByQuestion.value = {}
    startTime.value = Date.now()
    endTime.value = 0
    restoredFromStorage.value = false
    persistProgress()
  }

  function finish() {
    endTime.value = Date.now()
    clearPersistedProgress()
  }

  function persistProgress() {
    if (!paperId.value || !questions.value.length || !startTime.value || endTime.value) return
    const snapshot: ExamProgressSnapshot = {
      version: 1,
      savedAt: Date.now(),
      config: { ...config.value, knowledgePoints: [...config.value.knowledgePoints] },
      paperId: paperId.value,
      questions: questions.value,
      currentIndex: currentIndex.value,
      answers: { ...answers.value },
      submitted: { ...submitted.value },
      answerCorrectness: { ...answerCorrectness.value },
      wrongReasons: { ...wrongReasons.value },
      elapsedByQuestion: { ...elapsedByQuestion.value },
      startTime: startTime.value,
    }
    try {
      uni.setStorageSync(PROGRESS_STORAGE_KEY, snapshot)
    } catch (error) {
      console.warn('[exam progress] local persistence unavailable', error)
    }
  }

  function clearPersistedProgress() {
    try {
      uni.removeStorageSync(PROGRESS_STORAGE_KEY)
    } catch (error) {
      console.warn('[exam progress] local cleanup unavailable', error)
    }
  }

  function hydrateProgress() {
    let stored: unknown
    try {
      stored = uni.getStorageSync(PROGRESS_STORAGE_KEY)
    } catch (error) {
      console.warn('[exam progress] local recovery unavailable', error)
      return false
    }
    if (!isProgressSnapshot(stored)) {
      clearPersistedProgress()
      return false
    }
    config.value = stored.config
    paperId.value = stored.paperId
    questions.value = stored.questions
    currentIndex.value = Math.min(Math.max(stored.currentIndex, 0), stored.questions.length - 1)
    answers.value = stored.answers || {}
    submitted.value = stored.submitted || {}
    answerCorrectness.value = stored.answerCorrectness || {}
    wrongReasons.value = stored.wrongReasons || {}
    elapsedByQuestion.value = stored.elapsedByQuestion || {}
    startTime.value = stored.startTime
    endTime.value = 0
    restoredFromStorage.value = true
    return true
  }

  function acknowledgeRestore() {
    restoredFromStorage.value = false
  }

  function reset() {
    config.value = {
      examType: 'CSCA', questionCount: 20, difficulty: 'all',
      strategy: 'random', knowledgePoints: [], mode: 'practice', timeLimit: 60,
    }
    questions.value = []
    paperId.value = null
    currentIndex.value = 0
    answers.value = {}
    submitted.value = {}
    answerCorrectness.value = {}
    wrongReasons.value = {}
    elapsedByQuestion.value = {}
    startTime.value = 0
    endTime.value = 0
    clearPersistedProgress()
  }

  hydrateProgress()

  return {
    config, paperId, questions, currentIndex, answers, submitted, answerCorrectness, wrongReasons, elapsedByQuestion,
    startTime, endTime, restoredFromStorage, currentQuestion, totalCount, answeredCount, progressPercent, timeUsed,
    remainingSeconds, hasActiveProgress, correctCount,
    setConfig, setPaper, setQuestions, setCurrentIndex, setAnswer, clearAnswer, markSubmitted,
    setWrongReason, addElapsed, start, finish, persistProgress, hydrateProgress, acknowledgeRestore, reset,
  }
})

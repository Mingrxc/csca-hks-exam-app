import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ExamConfig, Question } from '@/types/exam'

export type { ExamConfig, Question } from '@/types/exam'

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
  const startTime = ref(0)
  const endTime = ref(0)

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

  const correctCount = computed(() => {
    let count = 0
    questions.value.forEach((q, i) => {
      if (answers.value[i] === q.answer) count++
    })
    return count
  })

  function setConfig(c: Partial<ExamConfig>) {
    Object.assign(config.value, c)
  }

  function setQuestions(qs: Question[]) {
    questions.value = qs
  }

  function setPaper(id: number, qs: Question[]) {
    paperId.value = id
    setQuestions(qs)
  }

  function setCurrentIndex(index: number) {
    if (index >= 0 && index < questions.value.length) {
      currentIndex.value = index
    }
  }

  function setAnswer(index: number, answer: string) {
    answers.value[index] = answer
  }

  function clearAnswer(index: number) {
    delete answers.value[index]
  }

  function start() {
    currentIndex.value = 0
    answers.value = {}
    startTime.value = Date.now()
    endTime.value = 0
  }

  function finish() {
    endTime.value = Date.now()
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
    startTime.value = 0
    endTime.value = 0
  }

  return {
    config, paperId, questions, currentIndex, answers, startTime, endTime,
    currentQuestion, totalCount, answeredCount, progressPercent, timeUsed, correctCount,
    setConfig, setPaper, setQuestions, setCurrentIndex, setAnswer, clearAnswer, start, finish, reset,
  }
})

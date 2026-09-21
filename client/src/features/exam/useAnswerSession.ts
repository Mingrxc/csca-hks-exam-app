import { computed, ref } from 'vue'
import { WRONG_REASONS } from '@/constants/exam'
import { favoriteApi } from '@/features/favorite/api'
import { useExamStore } from '@/stores/exam'
import { examApi } from './api'

export function useAnswerSession() {
  const examStore = useExamStore()
  const isSubmitting = ref(false)
  const questionStartedAt = ref(Date.now())

  const mode = computed(() => examStore.config.mode)
  const currentIndex = computed(() => examStore.currentIndex)
  const answers = computed(() => examStore.answers)
  const submitted = computed(() => examStore.submitted)
  const showResult = computed<Record<number, boolean>>(() => mode.value === 'practice' ? submitted.value : {})
  const answerCorrectness = computed(() => examStore.answerCorrectness)
  const selectedReasons = computed(() => examStore.wrongReasons)
  const questions = computed(() => examStore.questions)
  const remainingSeconds = computed(() => examStore.remainingSeconds)
  const currentQuestion = computed(() => examStore.currentQuestion)
  const progressPercent = computed(() => examStore.progressPercent)
  const answeredCount = computed(() => examStore.answeredCount)
  const currentCorrect = computed(() => answerCorrectness.value[currentIndex.value] === true)
  const currentSelectedReason = computed(() => selectedReasons.value[currentIndex.value] || '')
  const answerSheetItems = computed(() => questions.value.map((_, index) => ({
    index,
    answered: answers.value[index] != null,
    marked: !!showResult.value[index],
  })))

  const commitElapsedTime = () => {
    const index = currentIndex.value
    const elapsed = Math.max(0, Math.floor((Date.now() - questionStartedAt.value) / 1000))
    questionStartedAt.value = Date.now()
    return examStore.addElapsed(index, elapsed)
  }

  const toggleFavorite = async () => {
    if (!currentQuestion.value) return
    try {
      const status = await favoriteApi.toggle(currentQuestion.value.id)
      currentQuestion.value.isFavorite = status.is_favorite
      uni.showToast({ title: status.is_favorite ? '已收藏' : '已取消收藏', icon: 'none' })
    } catch {}
  }

  const selectOption = async (key: string) => {
    if (!currentQuestion.value || !examStore.paperId || isSubmitting.value) return
    if (showResult.value[currentIndex.value] && mode.value === 'practice') return

    isSubmitting.value = true
    const index = currentIndex.value
    const previousAnswer = answers.value[index]
    examStore.setAnswer(index, key)

    try {
      const response = await examApi.submitAnswer({
        paperId: examStore.paperId,
        questionId: currentQuestion.value.id,
        userAnswer: key,
        timeSpent: commitElapsedTime(),
        wrongReason: currentSelectedReason.value || undefined,
      })
      examStore.markSubmitted(index, response.is_correct)
    } catch {
      if (previousAnswer == null) examStore.clearAnswer(index)
      else examStore.setAnswer(index, previousAnswer)
    } finally {
      isSubmitting.value = false
    }
  }

  const selectWrongReason = async (reason: string) => {
    const index = currentIndex.value
    const previousReason = selectedReasons.value[index]
    examStore.setWrongReason(index, reason)
    const answer = answers.value[index]
    if (!answer || !currentQuestion.value || !examStore.paperId || isSubmitting.value) return

    isSubmitting.value = true
    try {
      const response = await examApi.submitAnswer({
        paperId: examStore.paperId,
        questionId: currentQuestion.value.id,
        userAnswer: answer,
        timeSpent: commitElapsedTime(),
        wrongReason: reason,
      })
      examStore.markSubmitted(index, response.is_correct)
    } catch {
      if (previousReason == null) {
        delete examStore.wrongReasons[index]
        examStore.persistProgress()
      } else {
        examStore.setWrongReason(index, previousReason)
      }
    } finally {
      isSubmitting.value = false
    }
  }

  const moveTo = (index: number) => {
    if (index === currentIndex.value) return
    commitElapsedTime()
    examStore.setCurrentIndex(index)
  }

  return {
    examStore, mode, currentIndex, answers, showResult, questions, remainingSeconds,
    currentQuestion, progressPercent, answeredCount, currentCorrect, currentSelectedReason,
    answerSheetItems, wrongReasons: WRONG_REASONS, toggleFavorite, selectOption, selectWrongReason,
    commitElapsedTime, moveTo,
  }
}

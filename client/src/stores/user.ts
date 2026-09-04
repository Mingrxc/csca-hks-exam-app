import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ensureLogin, userApi } from '@/api'
import type { ExamType } from '@/types/exam'

const defaultUserInfo = {
  id: 0,
  nickname: '留学同学',
  avatarUrl: '',
  targetExam: 'CSCA' as 'CSCA' | 'HKS',
  targetDate: '',
  targetDates: {},
  totalQuestions: 0,
  totalCorrect: 0,
  streakDays: 0,
  favoriteCount: 0,
}

const EXAM_SELECTION_KEY = 'exam_selected_types'

function isExamType(value: unknown): value is ExamType {
  return value === 'CSCA' || value === 'HKS'
}

function normalizeExamSelections(value: unknown): ExamType[] {
  const raw = Array.isArray(value) ? value : typeof value === 'string' ? [value] : []
  return Array.from(new Set(raw.filter(isExamType))).slice(0, 2)
}

function readExamSelections(): ExamType[] {
  return normalizeExamSelections(uni.getStorageSync(EXAM_SELECTION_KEY))
}

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const openid = ref('')
  const userInfo = ref({ ...defaultUserInfo })
  const selectedExams = ref<ExamType[]>(readExamSelections())

  const isLogin = computed(() => !!token.value)
  const isBrowseMode = computed(() => selectedExams.value.length === 0)
  const selectedExamText = computed(() =>
    selectedExams.value.length ? selectedExams.value.join(' / ') : '随便看看',
  )
  const primaryExam = computed<ExamType>(() => selectedExams.value[0] || userInfo.value.targetExam)
  const correctRate = computed(() => {
    if (userInfo.value.totalQuestions === 0) return 0
    return Math.round((userInfo.value.totalCorrect / userInfo.value.totalQuestions) * 100)
  })

  function setToken(t: string) {
    token.value = t
    uni.setStorageSync('token', t)
  }

  function persistSelectedExams() {
    uni.setStorageSync(EXAM_SELECTION_KEY, selectedExams.value)
  }

  function setSelectedExams(exams: ExamType[]) {
    selectedExams.value = normalizeExamSelections(exams)
    persistSelectedExams()
  }

  function toggleSelectedExam(exam: ExamType) {
    const next = [...selectedExams.value]
    const index = next.indexOf(exam)
    if (index >= 0) {
      next.splice(index, 1)
    } else if (next.length < 2) {
      next.push(exam)
    }
    setSelectedExams(next)
  }

  function setBrowseMode() {
    setSelectedExams([])
  }

  async function login(force = false) {
    const result = await ensureLogin(force)
    setToken(result.token)
    openid.value = result.openid
    const profile = result.user || await userApi.getUserInfo()
    userInfo.value = {
      id: profile.id,
      nickname: profile.nickname,
      avatarUrl: profile.avatar_url || '',
      targetExam: profile.target_exam,
      targetDate: profile.target_date || '',
      targetDates: {
        ...(profile.target_dates?.CSCA ? { CSCA: profile.target_dates.CSCA } : {}),
        ...(profile.target_dates?.HKS ? { HKS: profile.target_dates.HKS } : {}),
      },
      totalQuestions: profile.total_questions,
      totalCorrect: profile.total_correct,
      streakDays: profile.streak_days,
      favoriteCount: profile.favorite_count,
    }
  }

  function logout() {
    token.value = ''
    openid.value = ''
    userInfo.value = { ...defaultUserInfo }
    uni.removeStorageSync('token')
  }

  return {
    token,
    openid,
    userInfo,
    selectedExams,
    isLogin,
    isBrowseMode,
    selectedExamText,
    primaryExam,
    correctRate,
    setToken,
    setSelectedExams,
    toggleSelectedExam,
    setBrowseMode,
    login,
    logout,
  }
})

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { userApi } from '@/features/user/api'
import { getExamLabel } from '@/constants/exam'
import { resolveMediaUrl } from '@/api/client'
import { accessToken, activeUserId, adminRole, setAdminRole, clearSession, establishSession, sessionGeneration } from '@/shared/auth/session'
import type { ApiUser } from '@/api/contracts'
import type { ExamType } from '@/types/exam'
import type { ExamTargetDates } from '@/types/user'

export const defaultUserInfo = () => ({ id: 0, userCode: '', nickname: '留学同学', avatarUrl: '',
  targetExam: 'CSCA' as ExamType, targetDate: '', targetDates: {} as ExamTargetDates,
  totalQuestions: 0, totalCorrect: 0, correctRate: 0, objectiveCount: 0, streakDays: 0, favoriteCount: 0 })

const normalize = (value: unknown): ExamType[] => Array.isArray(value)
  ? [...new Set(value.filter(item => item === 'CSCA' || item === 'HKS'))] as ExamType[] : []

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(defaultUserInfo())
  const openid = ref('')
  const isLogin = computed(() => !!accessToken.value && activeUserId.value > 0 && userInfo.value.id === activeUserId.value)
  const busy = ref(false)
  const selectedExams = ref<ExamType[]>([])
  let restoring: Promise<void> | null = null
  const selectionKey = () => activeUserId.value ? `exam_selected_types_${activeUserId.value}` : 'exam_selected_types_guest'
  function loadSelection() {
    try {
      const saved = uni.getStorageSync(selectionKey())
      selectedExams.value = normalize(saved || (!activeUserId.value ? uni.getStorageSync('exam_selected_types') : []))
    } catch { selectedExams.value = [] }
  }
  watch(activeUserId, loadSelection, { immediate: true, flush: 'sync' })
  watch(accessToken, token => { if (!token) { userInfo.value = defaultUserInfo(); openid.value = '' } }, { flush: 'sync' })

  function applyProfile(profile: ApiUser) {
    setAdminRole(profile.admin_role)
    userInfo.value = { id: profile.id, userCode: profile.user_code, nickname: profile.nickname,
      avatarUrl: resolveMediaUrl(profile.avatar_url) || '', targetExam: profile.target_exam,
      targetDate: profile.target_date || '', targetDates: profile.target_dates || {},
      totalQuestions: profile.total_questions, totalCorrect: profile.total_correct,
      correctRate: profile.correct_rate, objectiveCount: profile.total_objective ?? 0,
      streakDays: profile.streak_days, favoriteCount: profile.favorite_count }
  }
  async function restoreSession() {
    if (!accessToken.value || isLogin.value) return
    if (restoring) return restoring
    const generation = sessionGeneration()
    restoring = (async () => {
      try {
        const profile = await userApi.getUserInfo()
        if (generation !== sessionGeneration()) return
        applyProfile(profile)
        establishSession(accessToken.value, profile.id)
      } catch (error: any) {
        if (error?.statusCode === 401 && generation === sessionGeneration()) clearSession()
      } finally { restoring = null }
    })()
    return restoring
  }
  async function login(nickname?: string) {
    if (busy.value) return
    busy.value = true
    const generation = sessionGeneration()
    try {
      const code = await new Promise<string>((resolve, reject) => uni.login({
        success: result => result.code ? resolve(result.code) : reject(new Error('微信登录未返回临时凭证')), fail: reject,
      }))
      const result = await userApi.wxLogin(code, nickname)
      if (generation !== sessionGeneration()) throw new Error('登录已取消')
      if (!result.user) throw new Error('登录信息不完整，请重试')
      applyProfile(result.user)
      openid.value = result.openid
      establishSession(result.token, result.user.id)
    } finally { busy.value = false }
  }
  async function refreshProfile() {
    const generation = sessionGeneration()
    const profile = await userApi.getUserInfo()
    if (generation === sessionGeneration()) applyProfile(profile)
  }
  function logout() { clearSession(); userInfo.value = defaultUserInfo(); openid.value = '' }
  function setSelectedExams(exams: ExamType[]) {
    selectedExams.value = normalize(exams).slice(0, 2)
    try { uni.setStorageSync(selectionKey(), selectedExams.value) } catch {}
  }
  function toggleSelectedExam(exam: ExamType) {
    const next = selectedExams.value.includes(exam) ? selectedExams.value.filter(value => value !== exam) : [...selectedExams.value, exam]
    setSelectedExams(next)
  }
  return { token: accessToken, openid, userInfo, isLogin, busy, selectedExams, adminRole,
    isAdmin: computed(() => isLogin.value && adminRole.value !== 'user'),
    isOwner: computed(() => isLogin.value && adminRole.value === 'owner'),
    isBrowseMode: computed(() => selectedExams.value.length === 0),
    selectedExamText: computed(() => selectedExams.value.length ? selectedExams.value.map(getExamLabel).join(' / ') : '随便看看'),
    primaryExam: computed<ExamType>(() => selectedExams.value[0] || userInfo.value.targetExam),
    correctRate: computed(() => userInfo.value.correctRate),
    setSelectedExams, toggleSelectedExam, setBrowseMode: () => setSelectedExams([]), applyProfile, restoreSession, refreshProfile, login, logout }
})

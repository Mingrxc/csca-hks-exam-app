import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ensureLogin, userApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const openid = ref('')
  const userInfo = ref({
    id: 0,
    nickname: '考霸同学',
    avatarUrl: '',
    targetExam: 'CSCA' as 'CSCA' | 'HKS',
    targetDate: '',
    totalQuestions: 0,
    totalCorrect: 0,
    streakDays: 0,
  })

  const isLogin = computed(() => !!token.value)
  const correctRate = computed(() => {
    if (userInfo.value.totalQuestions === 0) return 0
    return Math.round((userInfo.value.totalCorrect / userInfo.value.totalQuestions) * 100)
  })

  function setToken(t: string) {
    token.value = t
    uni.setStorageSync('token', t)
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
      totalQuestions: profile.total_questions,
      totalCorrect: profile.total_correct,
      streakDays: profile.streak_days,
    }
  }

  function logout() {
    token.value = ''
    uni.removeStorageSync('token')
  }

  return { token, openid, userInfo, isLogin, correctRate, setToken, login, logout }
})

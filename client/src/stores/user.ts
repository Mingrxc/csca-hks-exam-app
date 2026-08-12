import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
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

  function login() {
    // 微信登录逻辑
    return new Promise<void>((resolve) => {
      uni.login({
        success: () => {
          // 调用后端 wxLogin 接口换取 token
          setToken('mock-token')
          resolve()
        }
      })
    })
  }

  function logout() {
    token.value = ''
    uni.removeStorageSync('token')
  }

  return { token, openid, userInfo, isLogin, correctRate, setToken, login, logout }
})

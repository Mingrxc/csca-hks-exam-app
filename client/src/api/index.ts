import type {
  ApiExamResult,
  ApiDashboard,
  ApiHistoryPaper,
  ApiPaper,
  ApiQuestion,
  ApiRelatedQuestion,
  ApiSubmitAnswerResult,
  ApiUser,
  ApiWrongBookDetail,
  ApiWrongBookItem,
} from './contracts'

// API 基础配置
const DEFAULT_BASE_URL = 'http://127.0.0.1:8000/api/v1'
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, '')

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  showLoading?: boolean
}

interface LoginResult {
  token: string
  openid: string
  user?: ApiUser
}

let loginPromise: Promise<LoginResult> | null = null

export function ensureLogin(force = false): Promise<LoginResult> {
  const storedToken = uni.getStorageSync('token')
  if (storedToken && !force) {
    return Promise.resolve({ token: storedToken, openid: '' })
  }
  if (loginPromise) return loginPromise

  loginPromise = new Promise((resolve, reject) => {
    uni.login({
      success: (loginResult: any) => {
        if (!loginResult.code) {
          reject(new Error('微信登录未返回临时凭证'))
          return
        }
        uni.request({
          url: BASE_URL + '/user/wx-login',
          method: 'POST',
          data: { code: loginResult.code },
          header: { 'Content-Type': 'application/json' },
          success: (response: any) => {
            const payload = response.data
            if (response.statusCode === 200 && payload?.code === 0) {
              uni.setStorageSync('token', payload.data.token)
              resolve(payload.data)
            } else {
              reject(payload || new Error('登录失败'))
            }
          },
          fail: reject,
        })
      },
      fail: reject,
    })
  }).finally(() => {
    loginPromise = null
  })

  return loginPromise
}

// 请求拦截
function request<T = any>(options: RequestOptions): Promise<T> {
  const finishLoading = () => {
    if (options.showLoading !== false) uni.hideLoading()
  }

  return new Promise((resolve, reject) => {
    if (options.showLoading !== false) {
      uni.showLoading({ title: '加载中...', mask: true })
    }

    const send = (token: string, allowRetry: boolean) => {
      const header: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options.header,
      }
      if (token) header.Authorization = `Bearer ${token}`

      uni.request({
        url: BASE_URL + options.url,
        method: options.method || 'GET',
        data: options.data,
        header,
        success: async (res: any) => {
          const { statusCode, data } = res
          if (statusCode === 200 && data.code === 0) {
            finishLoading()
            resolve(data.data)
            return
          }
          if (statusCode === 401 && allowRetry && options.url !== '/user/wx-login') {
            uni.removeStorageSync('token')
            try {
              const login = await ensureLogin(true)
              send(login.token, false)
              return
            } catch {
              // Fall through to the shared unauthorized state.
            }
          }

          finishLoading()
          if (statusCode === 401) {
            uni.removeStorageSync('token')
            uni.showToast({ title: '登录已失效，请重试', icon: 'none' })
          } else {
            uni.showToast({ title: data?.message || data?.detail || '请求失败', icon: 'none' })
          }
          reject(data)
        },
        fail: (err) => {
          finishLoading()
          uni.showToast({ title: '网络异常', icon: 'none' })
          reject(err)
        },
      })
    }

    const storedToken = uni.getStorageSync('token')
    if (storedToken || options.url === '/user/wx-login') {
      send(storedToken, true)
      return
    }
    ensureLogin()
      .then((login) => send(login.token, true))
      .catch(() => send('', true))
  })
}

async function download(url: string): Promise<string> {
  let token = uni.getStorageSync('token')
  if (!token) {
    try {
      token = (await ensureLogin()).token
    } catch {
      // Local H5 development may continue through explicit backend dev auth.
    }
  }

  return new Promise((resolve, reject) => {
    uni.downloadFile({
      url: BASE_URL + url,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (response: any) => {
        if (response.statusCode === 200) {
          resolve(response.tempFilePath)
        } else {
          reject(new Error(`PDF download failed with status ${response.statusCode}`))
        }
      },
      fail: reject,
    })
  })
}

// ==================== 用户模块 ====================
export const userApi = {
  wxLogin: (code: string) => request<LoginResult>({
    url: '/user/wx-login',
    method: 'POST',
    data: { code },
  }),
  getDashboard: () => request<ApiDashboard>({ url: '/user/dashboard' }),
  getUserInfo: () => request<ApiUser>({ url: '/user/info' }),
  updateProfile: (data: any) => request<ApiUser>({ url: '/user/profile', method: 'PUT', data }),
}

// ==================== 题库模块 ====================
export const questionApi = {
  getPapers: (params: any) => request<ApiHistoryPaper[]>({ url: '/question/papers', data: params }),
  generatePaper: (config: any) => request<ApiPaper>({
    url: '/question/generate-paper',
    method: 'POST',
    data: config,
  }),
  getQuestionDetail: (id: number) => request<ApiQuestion>({ url: `/question/${id}` }),
}

// ==================== 答题模块 ====================
export const examApi = {
  submitAnswer: (data: any) => request<ApiSubmitAnswerResult>({
    url: '/exam/submit',
    method: 'POST',
    data,
    showLoading: false,
  }),
  getResult: (paperId: number) => request<ApiExamResult>({ url: `/exam/result/${paperId}` }),
}

// ==================== 错题本模块 ====================
export const wrongBookApi = {
  getList: (params: Record<string, string>) => request<ApiWrongBookItem[]>({ url: '/wrongbook/list', data: params }),
  getDetail: (id: number) => request<ApiWrongBookDetail>({ url: `/wrongbook/${id}` }),
  getDetailByQuestion: (questionId: number) => request<ApiWrongBookDetail>({ url: `/wrongbook/question/${questionId}` }),
  markMastered: (id: number) => request<{ id: number; question_id: number; is_mastered: boolean }>({
    url: `/wrongbook/${id}/master`,
    method: 'PUT',
  }),
  getRelated: (questionId: number) => request<ApiRelatedQuestion[]>({
    url: `/wrongbook/related/${questionId}`,
  }),
  generateRedoPaper: (params: { examType: string; limit?: number }) => request<ApiPaper>({
    url: `/wrongbook/redo-paper?examType=${params.examType}&limit=${params.limit || 20}`,
    method: 'POST',
  }),
  exportPdf: (params: Record<string, string>) => {
    const query = Object.entries(params)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&')
    return download(`/wrongbook/export-pdf?${query}`)
  },
}

export default { userApi, questionApi, examApi, wrongBookApi }

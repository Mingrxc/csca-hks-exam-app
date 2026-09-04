import type {
  ApiExamResult,
  ApiDashboard,
  ApiAIReply,
  ApiContentItem,
  ApiFavoriteItem,
  ApiFavoriteStatus,
  ApiHistoryPaper,
  ApiPaper,
  ApiSpecialOption,
  ApiQuestion,
  ApiRelatedQuestion,
  ApiSubmitAnswerResult,
  ApiUser,
  ApiWrongBookDetail,
  ApiWrongBookItem,
} from './contracts'
import type { ExamType } from '@/types/exam'

// API 基础配置
const DEFAULT_BASE_URL = 'http://127.0.0.1:8000/api/v1'
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, '')
const FALLBACK_BASE_URL = (import.meta.env.VITE_API_FALLBACK_URL || DEFAULT_BASE_URL).replace(/\/$/, '')
const API_BASE_URLS = Array.from(new Set([BASE_URL, FALLBACK_BASE_URL].filter(Boolean)))

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  showLoading?: boolean
  requireAuth?: boolean
}

function formatNetworkErrorMessage(err: any): string {
  const raw = typeof err?.errMsg === 'string' ? err.errMsg : ''
  if (!raw) return '网络异常'
  if (raw.includes('url not in domain list')) return '域名未配置'
  if (raw.includes('SSL') || raw.includes('TLS')) return '证书校验失败'
  if (raw.includes('timeout')) return '请求超时'
  if (raw.includes('fail')) return raw.replace(/^fail\s*/i, '').slice(0, 30)
  return raw.slice(0, 30)
}

interface LoginResult {
  token: string
  openid: string
  user?: ApiUser
}

let loginPromise: Promise<LoginResult> | null = null

function wxLoginWithBaseUrl(baseUrl: string, code: string): Promise<LoginResult> {
  return new Promise((resolve, reject) => {
    uni.request({
      url: baseUrl + '/user/wx-login',
      method: 'POST',
      data: { code },
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
  })
}

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
        const tryLogin = (baseIndex: number): void => {
          wxLoginWithBaseUrl(API_BASE_URLS[baseIndex], loginResult.code)
            .then(resolve)
            .catch((error) => {
              if (baseIndex + 1 < API_BASE_URLS.length) {
                tryLogin(baseIndex + 1)
                return
              }
              reject(error)
            })
        }
        tryLogin(0)
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

    const send = (token: string, allowRetry: boolean, baseIndex = 0) => {
      const header: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options.header,
      }
      if (token) header.Authorization = `Bearer ${token}`

      uni.request({
        url: API_BASE_URLS[baseIndex] + options.url,
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
          if (baseIndex + 1 < API_BASE_URLS.length) {
            send(token, allowRetry, baseIndex + 1)
            return
          }
          finishLoading()
          const message = formatNetworkErrorMessage(err)
          console.error('[request fail]', options.url, err)
          uni.showToast({ title: message, icon: 'none' })
          reject(err)
        },
      })
    }

    const storedToken = uni.getStorageSync('token')
    const requiresAuth = options.requireAuth !== false
    if (!requiresAuth) {
      send(storedToken, true)
      return
    }
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

  const downloadWithBaseUrl = (baseIndex: number): Promise<string> =>
    new Promise((resolve, reject) => {
      uni.downloadFile({
        url: API_BASE_URLS[baseIndex] + url,
        header: token ? { Authorization: `Bearer ${token}` } : {},
        success: (response: any) => {
          if (response.statusCode === 200) {
            resolve(response.tempFilePath)
          } else {
            reject(new Error(`PDF download failed with status ${response.statusCode}`))
          }
        },
        fail: (error) => {
          if (baseIndex + 1 < API_BASE_URLS.length) {
            downloadWithBaseUrl(baseIndex + 1).then(resolve).catch(reject)
            return
          }
          reject(error)
        },
      })
    })

  return downloadWithBaseUrl(0)
}

// ==================== 用户模块 ====================
export const userApi = {
  wxLogin: (code: string) => request<LoginResult>({
    url: '/user/wx-login',
    method: 'POST',
    data: { code },
    requireAuth: false,
  }),
  getDashboard: () => request<ApiDashboard>({ url: '/user/dashboard' }),
  getUserInfo: () => request<ApiUser>({ url: '/user/info' }),
  updateProfile: (data: any) => request<ApiUser>({ url: '/user/profile', method: 'PUT', data }),
}

// ==================== 内容模块 ====================
export const contentApi = {
  listHome: () => request<ApiContentItem[]>({ url: '/content/home', showLoading: false, requireAuth: false }),
  get: (id: number) => request<ApiContentItem>({ url: `/content/${id}`, requireAuth: false }),
  listAdmin: () => request<ApiContentItem[]>({ url: '/content/list' }),
  create: (data: Record<string, unknown>) => request<ApiContentItem>({ url: '/content', method: 'POST', data }),
  update: (id: number, data: Record<string, unknown>) => request<ApiContentItem>({ url: `/content/${id}`, method: 'PUT', data }),
  remove: (id: number) => request<{ id: number; deleted: boolean }>({ url: `/content/${id}`, method: 'DELETE' }),
}

// ==================== 题库模块 ====================
export const questionApi = {
  getPapers: (params: any) => request<ApiHistoryPaper[]>({ url: '/question/papers', data: params }),
  getSpecialOptions: (examType: ExamType, limit = 100) =>
    request<ApiSpecialOption[]>({
      url: `/question/special-options?examType=${examType}&limit=${limit}`,
      showLoading: false,
    }),
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

// ==================== 收藏模块 ====================
export const favoriteApi = {
  list: (limit = 50) => request<ApiFavoriteItem[]>({ url: `/favorite/list?limit=${limit}` }),
  status: (questionId: number) => request<ApiFavoriteStatus>({ url: `/favorite/status/${questionId}`, showLoading: false }),
  toggle: (questionId: number) => request<ApiFavoriteStatus>({
    url: '/favorite/toggle',
    method: 'POST',
    data: { questionId },
    showLoading: false,
  }),
}

// ==================== AI 模块 ====================
export const aiApi = {
  chat: (data: {
    messages: Array<{ role: 'user' | 'assistant'; content: string }>
    examType?: 'CSCA' | 'HKS'
    question?: string
    topic?: string
    context?: string
  }) => request<ApiAIReply>({ url: '/ai/chat', method: 'POST', data }),
}

export default { userApi, questionApi, examApi, wrongBookApi, favoriteApi, contentApi, aiApi }

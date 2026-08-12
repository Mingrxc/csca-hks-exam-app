import type {
  ApiExamResult,
  ApiPaper,
  ApiQuestion,
  ApiRelatedQuestion,
  ApiSubmitAnswerResult,
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

// 请求拦截
function request<T = any>(options: RequestOptions): Promise<T> {
  const token = uni.getStorageSync('token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.header,
  }
  if (token) {
    header.Authorization = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    if (options.showLoading !== false) {
      uni.showLoading({ title: '加载中...', mask: true })
    }

    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res: any) => {
        const { statusCode, data } = res
        if (statusCode === 200 && data.code === 0) {
          resolve(data.data)
        } else if (statusCode === 401) {
          uni.removeStorageSync('token')
          uni.showToast({ title: '请先登录', icon: 'none' })
          reject(data)
        } else {
          uni.showToast({ title: data?.message || data?.detail || '请求失败', icon: 'none' })
          reject(data)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
      complete: () => {
        if (options.showLoading !== false) {
          uni.hideLoading()
        }
      },
    })
  })
}

// ==================== 用户模块 ====================
export const userApi = {
  wxLogin: (code: string) => request<{ token: string; openid: string }>({
    url: '/user/wx-login',
    method: 'POST',
    data: { code },
  }),
  getUserInfo: () => request({ url: '/user/info' }),
  updateProfile: (data: any) => request({ url: '/user/profile', method: 'PUT', data }),
}

// ==================== 题库模块 ====================
export const questionApi = {
  getPapers: (params: any) => request<ApiPaper[]>({ url: '/question/papers', data: params }),
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
  exportPdf: (params: any) => request({
    url: '/wrongbook/export-pdf',
    method: 'POST',
    data: params,
  }),
}

export default { userApi, questionApi, examApi, wrongBookApi }

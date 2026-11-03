import { showToast, showLoading } from '@/i18n/ui'
import { clearSession, getToken, notifyLoginRequired, sessionGeneration, setAdminRole } from '@/shared/auth/session'

const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()
if (!configuredBaseUrl && import.meta.env.PROD) throw new Error('VITE_API_BASE_URL is required for production builds')
const BASE_URL = (configuredBaseUrl || 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '')
if (!/^https?:\/\//i.test(BASE_URL)) throw new Error('VITE_API_BASE_URL must start with http:// or https://')
const configuredTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS || 15000)
const REQUEST_TIMEOUT_MS = Number.isFinite(configuredTimeout) && configuredTimeout > 0 ? configuredTimeout : 15000
let requestSequence = 0
const createRequestId = () => `mp-${Date.now().toString(36)}-${(++requestSequence).toString(36)}`

export function resolveMediaUrl(value?: string | null): string | undefined {
  if (!value) return undefined
  if (/^https?:\/\//i.test(value)) return value
  if (!value.startsWith('/')) return undefined
  return `${BASE_URL.match(/^https?:\/\/[^/]+/)?.[0] || ''}${value}`
}

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  showLoading?: boolean
  requireAuth?: boolean
  authPrompt?: boolean
}

export class ApiRequestError extends Error {
  statusCode?: number
  code?: number | string
  requestId?: string
  cause?: unknown
  constructor(message: string, options: { statusCode?: number; code?: number | string; requestId?: string; cause?: unknown } = {}) {
    super(message)
    this.name = 'ApiRequestError'
    Object.assign(this, options)
  }
}

function responseError(statusCode: number, payload: any): ApiRequestError {
  const candidate = payload?.message || payload?.detail
  return new ApiRequestError(typeof candidate === 'string' ? candidate : `请求失败 (${statusCode})`, {
    statusCode, code: payload?.code, requestId: payload?.request_id, cause: payload,
  })
}
function networkError(error: any, requestId: string, operation: 'request' | 'upload' = 'request') {
  const raw = String(error?.errMsg || '')
  const domainBlocked = /url not in domain list/i.test(raw)
  const message = !raw ? '网络异常' : raw.includes('timeout') ? '请求超时'
    : domainBlocked ? operation === 'upload' ? '上传域名未配置' : '域名未配置'
    : /SSL|TLS/.test(raw) ? '证书校验失败'
    : raw.includes('ERR_CONNECTION_REFUSED') ? '无法连接服务器，请确认后端已启动'
    : /network is down|ERR_INTERNET_DISCONNECTED/.test(raw) ? '网络不可用，请检查网络连接'
    : raw.replace(/^(request:)?fail\s*/i, '').slice(0, 80)
  return new ApiRequestError(message, { requestId, cause: error, ...(domainBlocked ? { code: 'DOMAIN_NOT_CONFIGURED' } : {}) })
}
function unauthorized(prompt = true) {
  if (prompt) notifyLoginRequired()
  return new ApiRequestError('登录后即可使用', { statusCode: 401, code: 'AUTH_REQUIRED' })
}
function staleSession() { return new ApiRequestError('登录状态已改变，请重试', { code: 'SESSION_CHANGED' }) }
function handleFailure(error: ApiRequestError, token: string, prompt = true) {
  if (error.statusCode === 403 && error.code === 40341) setAdminRole('user')
  if (error.statusCode === 401) {
    if (getToken() === token) clearSession()
    error.message = '登录已失效，请重试'
    if (prompt) notifyLoginRequired()
  } else showToast({ title: error.message, icon: 'none' })
}

export function request<T = any>(options: RequestOptions): Promise<T> {
  const token = getToken()
  const needsAuth = options.requireAuth !== false
  if (needsAuth && !token) return Promise.reject(unauthorized(options.authPrompt !== false))
  const generation = sessionGeneration()
  const method = options.method || 'GET'
  const requestId = createRequestId()
  const changed = () => needsAuth && (generation !== sessionGeneration() || token !== getToken())
  return new Promise((resolve, reject) => {
    if (options.showLoading !== false) showLoading({ title: '加载中...', mask: true })
    const finish = () => { if (options.showLoading !== false) uni.hideLoading() }
    const send = (retries: number) => {
      if (changed()) { finish(); reject(staleSession()); return }
      uni.request({ url: BASE_URL + options.url, method, data: options.data, timeout: REQUEST_TIMEOUT_MS,
        header: { 'Content-Type': 'application/json', 'X-Request-ID': requestId, ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.header },
        success: response => {
          finish()
          if (changed()) { reject(staleSession()); return }
          const payload = response.data as any
          if (response.statusCode === 200 && payload?.code === 0) { resolve(payload.data); return }
          const error = responseError(response.statusCode, payload)
          handleFailure(error, token, needsAuth && options.authPrompt !== false)
          reject(error)
        },
        fail: error => {
          if (changed()) { finish(); reject(staleSession()); return }
          if (retries > 0) { send(retries - 1); return }
          finish()
          const failure = networkError(error, requestId)
          showToast({ title: failure.message, icon: 'none' })
          reject(failure)
        },
      })
    }
    send(method === 'GET' ? 1 : 0)
  })
}

export function upload<T>(url: string, filePath: string): Promise<T> {
  const token = getToken()
  if (!token) return Promise.reject(unauthorized())
  const generation = sessionGeneration()
  const requestId = createRequestId()
  return new Promise((resolve, reject) => uni.uploadFile({
    url: BASE_URL + url, filePath, name: 'file', timeout: REQUEST_TIMEOUT_MS,
    header: { Authorization: `Bearer ${token}`, 'X-Request-ID': requestId },
    success: response => {
      if (generation !== sessionGeneration()) { reject(staleSession()); return }
      let payload: any
      try { payload = JSON.parse(response.data) } catch { reject(new ApiRequestError('头像上传失败，请重试')); return }
      if (response.statusCode === 200 && payload?.code === 0) { resolve(payload.data); return }
      const error = responseError(response.statusCode, payload)
      handleFailure(error, token)
      reject(error)
    },
    fail: error => reject(generation !== sessionGeneration() ? staleSession() : networkError(error, requestId, 'upload')),
  }))
}

export function download(url: string): Promise<string> {
  const token = getToken()
  if (!token) return Promise.reject(unauthorized())
  const generation = sessionGeneration()
  const requestId = createRequestId()
  return new Promise((resolve, reject) => {
    const send = (retries: number) => uni.downloadFile({ url: BASE_URL + url, timeout: REQUEST_TIMEOUT_MS,
      header: { Authorization: `Bearer ${token}`, 'X-Request-ID': requestId },
      success: response => {
        if (generation !== sessionGeneration()) { reject(staleSession()); return }
        if (response.statusCode === 200) { resolve(response.tempFilePath); return }
        const error = responseError(response.statusCode, response.data)
        handleFailure(error, token)
        reject(error)
      },
      fail: error => {
        if (generation !== sessionGeneration()) { reject(staleSession()); return }
        if (retries > 0) send(retries - 1)
        else reject(networkError(error, requestId))
      },
    })
    send(1)
  })
}

import type { ApiUser } from './contracts'

const DEFAULT_BASE_URL = 'http://127.0.0.1:8000/api/v1'
const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()
if (!configuredBaseUrl && import.meta.env.PROD) {
  throw new Error('VITE_API_BASE_URL is required for production builds')
}
const BASE_URL = (configuredBaseUrl || DEFAULT_BASE_URL).replace(/\/$/, '')
if (!/^https?:\/\//i.test(BASE_URL)) {
  throw new Error('VITE_API_BASE_URL must start with http:// or https://')
}
const configuredTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS || 15000)
const REQUEST_TIMEOUT_MS = Number.isFinite(configuredTimeout) && configuredTimeout > 0
  ? configuredTimeout
  : 15000
const IDEMPOTENT_METHODS = new Set(['GET'])
let requestSequence = 0

function createRequestId(): string {
  requestSequence = (requestSequence + 1) % 1000000
  return `mp-${Date.now().toString(36)}-${requestSequence.toString(36)}`
}

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  showLoading?: boolean
  requireAuth?: boolean
}

export class ApiRequestError extends Error {
  statusCode?: number
  code?: number | string
  requestId?: string
  cause?: unknown

  constructor(
    message: string,
    options: { statusCode?: number; code?: number | string; requestId?: string; cause?: unknown } = {},
  ) {
    super(message)
    this.name = 'ApiRequestError'
    this.statusCode = options.statusCode
    this.code = options.code
    this.requestId = options.requestId
    this.cause = options.cause
  }
}

function formatNetworkErrorMessage(err: unknown): string {
  const networkError = err as { errMsg?: string }
  const raw = typeof networkError?.errMsg === 'string' ? networkError.errMsg : ''
  if (!raw) return '网络异常'
  if (raw.includes('url not in domain list')) return '域名未配置'
  if (raw.includes('SSL') || raw.includes('TLS')) return '证书校验失败'
  if (raw.includes('timeout')) return '请求超时'
  if (raw.includes('ERR_CONNECTION_REFUSED')) return '无法连接服务器，请确认后端已启动'
  if (raw.includes('network is down') || raw.includes('ERR_INTERNET_DISCONNECTED')) {
    return '网络不可用，请检查网络连接'
  }
  return raw.replace(/^request:fail\s*/i, '').replace(/^fail\s*/i, '').slice(0, 40)
}

function normalizeResponseError(statusCode: number, payload: any): ApiRequestError {
  const candidate = payload?.message || payload?.detail
  const message = typeof candidate === 'string' ? candidate : `请求失败 (${statusCode})`
  return new ApiRequestError(message, {
    statusCode,
    code: payload?.code,
    requestId: payload?.request_id,
    cause: payload,
  })
}

function normalizeNetworkError(error: unknown, requestId?: string): ApiRequestError {
  return new ApiRequestError(formatNetworkErrorMessage(error), { requestId, cause: error })
}

interface LoginResult {
  token: string
  openid: string
  user?: ApiUser
}

let loginPromise: Promise<LoginResult> | null = null

function wxLogin(code: string): Promise<LoginResult> {
  const requestId = createRequestId()
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + '/user/wx-login',
      method: 'POST',
      data: { code },
      header: {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
      },
      timeout: REQUEST_TIMEOUT_MS,
      success: (response: any) => {
        const payload = response.data
        if (response.statusCode === 200 && payload?.code === 0) {
          uni.setStorageSync('token', payload.data.token)
          resolve(payload.data)
        } else {
          reject(normalizeResponseError(response.statusCode, payload))
        }
      },
      fail: (error) => reject(normalizeNetworkError(error, requestId)),
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
        wxLogin(loginResult.code).then(resolve).catch(reject)
      },
      fail: (error) => reject(normalizeNetworkError(error)),
    })
  }).finally(() => {
    loginPromise = null
  })

  return loginPromise
}

export function request<T = any>(options: RequestOptions): Promise<T> {
  const method = options.method || 'GET'
  const initialNetworkRetries = IDEMPOTENT_METHODS.has(method) ? 1 : 0
  const requestId = createRequestId()
  const finishLoading = () => {
    if (options.showLoading !== false) uni.hideLoading()
  }

  return new Promise((resolve, reject) => {
    if (options.showLoading !== false) {
      uni.showLoading({ title: '加载中...', mask: true })
    }

    const send = (token: string, allowAuthRetry: boolean, networkRetries: number) => {
      const header: Record<string, string> = {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
        ...options.header,
      }
      if (token) header.Authorization = `Bearer ${token}`

      uni.request({
        url: BASE_URL + options.url,
        method,
        data: options.data,
        header,
        timeout: REQUEST_TIMEOUT_MS,
        success: async (res: any) => {
          const { statusCode, data } = res
          if (statusCode === 200 && data?.code === 0) {
            finishLoading()
            resolve(data.data)
            return
          }
          if (statusCode === 401 && allowAuthRetry && options.url !== '/user/wx-login') {
            uni.removeStorageSync('token')
            console.info('[auth retry]', method, options.url, data?.request_id || requestId)
            try {
              const login = await ensureLogin(true)
              send(login.token, false, networkRetries)
              return
            } catch {
              // Fall through to the shared unauthorized state.
            }
          }

          finishLoading()
          const error = normalizeResponseError(statusCode, data)
          if (statusCode === 401) {
            uni.removeStorageSync('token')
            error.message = '登录已失效，请重试'
          }
          uni.showToast({ title: error.message, icon: 'none' })
          reject(error)
        },
        fail: (rawError) => {
          if (networkRetries > 0) {
            send(token, allowAuthRetry, networkRetries - 1)
            return
          }
          finishLoading()
          const error = normalizeNetworkError(rawError, requestId)
          console.error('[request fail]', method, options.url, requestId, error)
          uni.showToast({ title: error.message, icon: 'none' })
          reject(error)
        },
      })
    }

    const storedToken = uni.getStorageSync('token')
    const requiresAuth = options.requireAuth !== false
    if (!requiresAuth) {
      send(storedToken, false, initialNetworkRetries)
      return
    }
    if (storedToken || options.url === '/user/wx-login') {
      send(storedToken, true, initialNetworkRetries)
      return
    }
    ensureLogin()
      .then((login) => send(login.token, true, initialNetworkRetries))
      .catch(() => send('', false, initialNetworkRetries))
  })
}

export async function download(url: string): Promise<string> {
  const requestId = createRequestId()
  let token = uni.getStorageSync('token')
  if (!token) {
    try {
      token = (await ensureLogin()).token
    } catch {
      // Local H5 development may continue through explicit backend dev auth.
    }
  }

  const downloadFile = (networkRetries: number): Promise<string> =>
    new Promise((resolve, reject) => {
      uni.downloadFile({
        url: BASE_URL + url,
        header: {
          'X-Request-ID': requestId,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        timeout: REQUEST_TIMEOUT_MS,
        success: (response: any) => {
          if (response.statusCode === 200) {
            resolve(response.tempFilePath)
          } else {
            reject(normalizeResponseError(response.statusCode, response.data))
          }
        },
        fail: (rawError) => {
          if (networkRetries > 0) {
            downloadFile(networkRetries - 1).then(resolve).catch(reject)
            return
          }
          reject(normalizeNetworkError(rawError, requestId))
        },
      })
    })

  return downloadFile(1)
}


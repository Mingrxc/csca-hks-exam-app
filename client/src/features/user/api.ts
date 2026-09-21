import { request } from '@/api/client'
import type { ApiDashboard, ApiUser } from '@/api/contracts'

export interface LoginResult {
  token: string
  openid: string
  user?: ApiUser
}

export const userApi = {
  wxLogin: (code: string) => request<LoginResult>({
    url: '/user/wx-login', method: 'POST', data: { code }, requireAuth: false,
  }),
  getDashboard: () => request<ApiDashboard>({ url: '/user/dashboard' }),
  getUserInfo: () => request<ApiUser>({ url: '/user/info' }),
  updateProfile: (data: Record<string, unknown>) =>
    request<ApiUser>({ url: '/user/profile', method: 'PUT', data }),
}

import { request, upload } from '@/api/client'
import type { ApiCheckIn, ApiDashboard, ApiUser } from '@/api/contracts'

export interface LoginResult {
  token: string
  openid: string
  user?: ApiUser
}

export const userApi = {
  wxLogin: (code: string, nickname?: string) => request<LoginResult>({
    url: '/user/wx-login', method: 'POST', data: { code, ...(nickname ? { nickname } : {}) }, requireAuth: false,
  }),
  getDashboard: () => request<ApiDashboard>({ url: '/user/dashboard', authPrompt: false, showLoading: false }),
  checkIn: () => request<ApiCheckIn>({ url: '/user/check-in', method: 'POST', authPrompt: false, showLoading: false }),
  getUserInfo: () => request<ApiUser>({ url: '/user/info', authPrompt: false, showLoading: false }),
  uploadAvatar: (filePath: string) => upload<ApiUser>('/user/avatar', filePath),
  updateProfile: (data: Record<string, unknown>) =>
    request<ApiUser>({ url: '/user/profile', method: 'PUT', data }),
}

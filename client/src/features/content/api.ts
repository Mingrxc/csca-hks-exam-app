import { request } from '@/api/client'
import type { ApiContentItem } from '@/api/contracts'

export const contentApi = {
  listHome: () => request<ApiContentItem[]>({ url: '/content/home', showLoading: false, requireAuth: false }),
  get: (id: number) => request<ApiContentItem>({ url: `/content/${id}`, requireAuth: false }),
  listAdmin: () => request<ApiContentItem[]>({ url: '/content/list' }),
  create: (data: Record<string, unknown>) => request<ApiContentItem>({ url: '/content', method: 'POST', data }),
  update: (id: number, data: Record<string, unknown>) =>
    request<ApiContentItem>({ url: `/content/${id}`, method: 'PUT', data }),
  remove: (id: number) => request<{ id: number; deleted: boolean }>({ url: `/content/${id}`, method: 'DELETE' }),
}

import { request } from '@/api/client'
import type { ApiContentItem } from '@/api/contracts'

export const contentApi = {
  listAnnouncements: (page = 1) => request<{ items: ApiContentItem[]; total: number }>({
    url: '/content/announcements', data: { page, page_size: 20 }, requireAuth: false, showLoading: false,
  }),
  getAnnouncement: (id: number) => request<ApiContentItem>({
    url: `/content/announcements/${id}`, requireAuth: false, showLoading: false,
  }),
  listHome: () => request<ApiContentItem[]>({ url: '/content/home', showLoading: false, requireAuth: false }),
  get: (id: number) => request<ApiContentItem>({ url: `/content/${id}`, requireAuth: false }),
  listAdmin: () => request<ApiContentItem[]>({ url: '/content/list' }),
  create: (data: Record<string, unknown>) => request<ApiContentItem>({ url: '/content', method: 'POST', data }),
  update: (id: number, data: Record<string, unknown>) =>
    request<ApiContentItem>({ url: `/content/${id}`, method: 'PUT', data }),
  remove: (id: number) => request<{ id: number; deleted: boolean }>({ url: `/content/${id}`, method: 'DELETE' }),
}

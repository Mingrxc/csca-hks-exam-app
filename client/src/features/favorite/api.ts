import { request } from '@/api/client'
import type { ApiFavoriteItem, ApiFavoriteStatus } from '@/api/contracts'

export const favoriteApi = {
  list: (limit = 50) => request<ApiFavoriteItem[]>({ url: `/favorite/list?limit=${limit}` }),
  toggle: (questionId: number) => request<ApiFavoriteStatus>({
    url: '/favorite/toggle', method: 'POST', data: { questionId }, showLoading: false,
  }),
}

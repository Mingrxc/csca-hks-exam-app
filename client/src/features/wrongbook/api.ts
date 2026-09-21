import { download, request } from '@/api/client'
import type { ApiPaper, ApiRelatedQuestion, ApiWrongBookDetail, ApiWrongBookItem } from '@/api/contracts'

export const wrongBookApi = {
  getList: (params: Record<string, string>) => request<ApiWrongBookItem[]>({ url: '/wrongbook/list', data: params }),
  getDetail: (id: number) => request<ApiWrongBookDetail>({ url: `/wrongbook/${id}` }),
  getDetailByQuestion: (questionId: number) => request<ApiWrongBookDetail>({ url: `/wrongbook/question/${questionId}` }),
  markMastered: (id: number) => request<{ id: number; question_id: number; is_mastered: boolean }>({
    url: `/wrongbook/${id}/master`, method: 'PUT',
  }),
  getRelated: (questionId: number) => request<ApiRelatedQuestion[]>({ url: `/wrongbook/related/${questionId}` }),
  generateRedoPaper: (params: { examType: string; limit?: number }) => request<ApiPaper>({
    url: `/wrongbook/redo-paper?examType=${params.examType}&limit=${params.limit || 20}`, method: 'POST',
  }),
  exportPdf: (params: Record<string, string>) => {
    const query = Object.entries(params)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&')
    return download(`/wrongbook/export-pdf?${query}`)
  },
}

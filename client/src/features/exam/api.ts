import { request } from '@/api/client'
import type {
  ApiCatalogItem, ApiExamResult, ApiHistoryPaper, ApiPaper, ApiQuestion, ApiSpecialOption, ApiSubmitAnswerResult,
} from '@/api/contracts'
import type { ExamType } from '@/types/exam'

export const questionApi = {
  getCatalog: () => request<ApiCatalogItem[]>({ url: '/question/catalog', showLoading: false }),
  getPapers: (params: { limit?: number }) => request<ApiHistoryPaper[]>({ url: '/question/papers', data: params }),
  getSpecialOptions: (examType: ExamType, limit = 100) =>
    request<ApiSpecialOption[]>({
      url: `/question/special-options?examType=${examType}&limit=${limit}`,
      showLoading: false,
    }),
  generatePaper: (config: Record<string, unknown>) => request<ApiPaper>({
    url: '/question/generate-paper', method: 'POST', data: config,
  }),
  getQuestionDetail: (id: number) => request<ApiQuestion>({ url: `/question/${id}` }),
}

export const examApi = {
  selfReview: (data: { paperId: number; questionId: number; score: number }) => request<{ self_score: number; evaluation_status: string }>({
    url: '/exam/self-review', method: 'POST', data, showLoading: false,
  }),
  submitAnswer: (data: Record<string, unknown>) => request<ApiSubmitAnswerResult>({
    url: '/exam/submit', method: 'POST', data, showLoading: false,
  }),
  getResult: (paperId: number) => request<ApiExamResult>({ url: `/exam/result/${paperId}` }),
}

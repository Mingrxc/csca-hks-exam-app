import { request } from '@/api/client'
import type {
  ApiExamResult, ApiHistoryPaper, ApiPaper, ApiQuestion, ApiSpecialOption, ApiSubmitAnswerResult,
} from '@/api/contracts'
import type { ExamType } from '@/types/exam'

export const questionApi = {
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
  submitAnswer: (data: Record<string, unknown>) => request<ApiSubmitAnswerResult>({
    url: '/exam/submit', method: 'POST', data, showLoading: false,
  }),
  getResult: (paperId: number) => request<ApiExamResult>({ url: `/exam/result/${paperId}` }),
}

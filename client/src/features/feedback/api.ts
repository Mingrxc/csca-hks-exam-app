import { request } from '@/api/client'

export const FEEDBACK_CATEGORIES = [
  { value: 'question', label: '题目问题' },
  { value: 'bug', label: '功能异常' },
  { value: 'suggestion', label: '使用建议' },
  { value: 'other', label: '其他' },
] as const

export type FeedbackCategory = typeof FEEDBACK_CATEGORIES[number]['value']

export interface FeedbackPayload {
  request_id: string
  category: FeedbackCategory
  content: string
  app_version: string
}

export interface FeedbackReceipt {
  id: number
  status: 'unread' | 'read' | 'resolved'
  created_at: string
}

export const feedbackApi = {
  submit: (data: FeedbackPayload) => request<FeedbackReceipt>({
    url: '/feedback', method: 'POST', data, showLoading: false,
  }),
}

import { request } from '@/api/client'
import { getLanguage } from '@/i18n'

interface AIChatPayload {
  messages: Array<{ role: 'user' | 'assistant'; content: string }>
  examType?: 'CSCA' | 'HKS'
  question?: string
  topic?: string
  context?: string
}

interface AIChatResponse {
  reply: string
  model: string
  usage: Record<string, number>
}

export const aiApi = {
  chat: (data: AIChatPayload) => request<AIChatResponse>({
    url: '/ai/chat',
    method: 'POST',
    data: { ...data, language: getLanguage() },
  }),
}

import { request } from '@/api/client'
import type { ApiAIReply } from '@/api/contracts'

interface AIChatPayload {
  messages: Array<{ role: 'user' | 'assistant'; content: string }>
  examType?: 'CSCA' | 'HKS'
  question?: string
  topic?: string
  context?: string
}

export const aiApi = {
  chat: (data: AIChatPayload) => request<ApiAIReply>({ url: '/ai/chat', method: 'POST', data }),
}

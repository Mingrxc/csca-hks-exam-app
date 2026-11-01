import { request } from '@/api/client'

export interface AdminUser {
  id: number; user_code: string; nickname: string; avatar_url: string | null
  role: 'user' | 'viewer' | 'owner'; created_at: string; total_questions: number
  total_objective: number; correct_rate: number; streak_days: number; last_study_at: string | null
}
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }
export interface Overview {
  total_users: number; new_users_today: number; answering_users_today: number
  total_answers: number; total_papers: number; total_feedback: number; unread_feedback: number; study_timezone: string
}
export interface AdminFeedback {
  id: number; user_id: number; user_code: string | null; nickname: string | null
  category: 'question' | 'bug' | 'suggestion' | 'other'; content: string; app_version: string
  status: 'unread' | 'read' | 'resolved'; created_at: string; updated_at: string
}
export const adminApi = {
  overview: () => request<Overview>({ url: '/admin/overview', showLoading: false }),
  users: (search: string, page: number) => request<Page<AdminUser>>({ url: '/admin/users', data: { search, page }, showLoading: false }),
  members: (page: number) => request<Page<AdminUser>>({ url: '/admin/members', data: { page }, showLoading: false }),
  lookup: (user_code: string) => request<AdminUser>({ url: '/admin/members/lookup', data: { user_code }, showLoading: false }),
  grant: (user_code: string) => request<{ changed: boolean }>({ url: '/admin/members', method: 'POST', data: { user_code }, showLoading: false }),
  revoke: (id: number) => request<{ changed: boolean }>({ url: `/admin/members/${id}`, method: 'DELETE', showLoading: false }),
  feedback: (status: string, page: number) => request<Page<AdminFeedback>>({ url: '/feedback/admin', data: { ...(status ? { status } : {}), page }, showLoading: false }),
  feedbackStatus: (id: number, status: AdminFeedback['status']) => request<AdminFeedback>({ url: `/feedback/admin/${id}/status`, method: 'PUT', data: { status }, showLoading: false }),
}

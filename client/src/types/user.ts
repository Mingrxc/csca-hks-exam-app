import type { ExamType } from './exam'

export interface TodayStats {
  questionCount: number
  correctRate: number
  wrongCount: number
}

export interface CountdownValue {
  days: string
  hours: string
  minutes: string
}

export interface RecentPaper {
  id: number
  title: string
  questionCount: number
  score: number
  date: string
}

export interface DashboardData {
  userName: string
  targetExam: ExamType
  countdown: CountdownValue
  todayStats: TodayStats
  pendingWrongCount: number
  recentPapers: RecentPaper[]
}

export interface UserProfile {
  nickname: string
  targetExam: ExamType
  totalQuestions: number
  correctRate: number
  streakDays: number
}

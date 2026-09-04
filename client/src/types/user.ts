import type { ExamType } from './exam'

export type ExamTargetDates = Partial<Record<ExamType, string>>

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
  targetDate: string
  targetDates: ExamTargetDates
  countdown: CountdownValue
  todayStats: TodayStats
  pendingWrongCount: number
  favoriteCount: number
  recentPapers: RecentPaper[]
}

export interface UserProfile {
  nickname: string
  avatarUrl: string
  targetExam: ExamType
  targetDate: string
  targetDates: ExamTargetDates
  totalQuestions: number
  correctRate: number
  streakDays: number
  favoriteCount: number
}

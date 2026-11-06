import type { ExamType } from './exam'

export type ExamTargetDates = Partial<Record<ExamType, string>>

export interface TodayStats {
  objectiveCount?: number
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
  objectiveCount?: number
  id: number
  title: string
  questionCount: number
  score: number
  date: string
}

export interface CheckInStatus {
  today: string
  checkedIn: boolean
  streakDays: number
  week: Array<{ date: string; checked: boolean }>
}

export interface DashboardData {
  checkIn: CheckInStatus | null
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

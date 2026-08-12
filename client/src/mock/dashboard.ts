import type { DashboardData } from '@/types/user'

export const mockDashboard: DashboardData = {
  userName: '考霸同学',
  targetExam: 'CSCA',
  countdown: { days: '86', hours: '14', minutes: '32' },
  todayStats: {
    questionCount: 0,
    correctRate: 0,
    wrongCount: 0,
  },
  pendingWrongCount: 3,
  recentPapers: [],
}

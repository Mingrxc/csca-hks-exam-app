import { userApi } from '@/features/user/api'
import { toDashboardData } from '@/api/contracts'
import { useAsyncState } from '@/shared/composables/useAsyncState'

interface ExamDashboardSummary {
  todayStats: { questionCount: number; correctRate: number; wrongCount: number }
  pendingWrongCount: number
  favoriteCount: number
}

const emptyDashboard: ExamDashboardSummary = {
  todayStats: { questionCount: 0, correctRate: 0, wrongCount: 0 },
  pendingWrongCount: 0,
  favoriteCount: 0,
}

export function useExamDashboard() {
  const state = useAsyncState<ExamDashboardSummary>({ ...emptyDashboard })
  const load = () => state.execute(async () => {
    const dashboard = toDashboardData(await userApi.getDashboard())
    return {
      todayStats: dashboard.todayStats,
      pendingWrongCount: dashboard.pendingWrongCount,
      favoriteCount: dashboard.favoriteCount,
    }
  })
  return { ...state, load }
}

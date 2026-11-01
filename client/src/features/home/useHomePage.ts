import { computed } from 'vue'
import { contentApi } from '@/features/content/api'
import { userApi } from '@/features/user/api'
import { toCheckInStatus, toDashboardData } from '@/api/contracts'
import { useAsyncState } from '@/shared/composables/useAsyncState'
import type { ApiContentItem } from '@/api/contracts'
import type { CheckInStatus, DashboardData } from '@/types/user'

export function useHomePage() {
  const contentState = useAsyncState<ApiContentItem[]>([])
  const dashboardState = useAsyncState<DashboardData | null>(null)
  const checkInState = useAsyncState<CheckInStatus | null>(null)
  let checkInRevision = 0
  const recentPapers = computed(() => dashboardState.data.value?.recentPapers || [])

  const loadContents = () => contentState.execute(async () => (await contentApi.listHome()).slice(0, 5))
  const loadDashboard = async (authenticated: boolean) => {
    if (!authenticated) {
      dashboardState.data.value = null
      dashboardState.error.value = ''
      checkInState.data.value = null
      checkInState.error.value = ''
      return undefined
    }
    const revision = checkInRevision
    const refreshCheckIn = !checkInState.loading.value
    const result = await dashboardState.execute(async () => toDashboardData(await userApi.getDashboard()))
    // A dashboard response started before/during check-in must not undo its result.
    if (result && refreshCheckIn && revision === checkInRevision) {
      checkInState.data.value = result.checkIn
      checkInState.error.value = ''
    }
    return result
  }
  const checkIn = () => {
    if (checkInState.loading.value) return Promise.resolve(undefined)
    checkInRevision++
    return checkInState.execute(async () => toCheckInStatus(await userApi.checkIn()))
  }

  return { contentState, dashboardState, checkInState, recentPapers, loadContents, loadDashboard, checkIn }
}

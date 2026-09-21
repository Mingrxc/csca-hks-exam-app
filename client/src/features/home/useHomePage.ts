import { computed } from 'vue'
import { contentApi } from '@/features/content/api'
import { userApi } from '@/features/user/api'
import { toDashboardData } from '@/api/contracts'
import { useAsyncState } from '@/shared/composables/useAsyncState'
import type { ApiContentItem } from '@/api/contracts'
import type { DashboardData } from '@/types/user'

export function useHomePage() {
  const contentState = useAsyncState<ApiContentItem[]>([])
  const dashboardState = useAsyncState<DashboardData | null>(null)
  const recentPapers = computed(() => dashboardState.data.value?.recentPapers || [])

  const loadContents = () => contentState.execute(async () => (await contentApi.listHome()).slice(0, 5))
  const loadDashboard = (authenticated: boolean) => {
    if (!authenticated) {
      dashboardState.data.value = null
      dashboardState.error.value = ''
      return Promise.resolve(undefined)
    }
    return dashboardState.execute(async () => toDashboardData(await userApi.getDashboard()))
  }

  return { contentState, dashboardState, recentPapers, loadContents, loadDashboard }
}

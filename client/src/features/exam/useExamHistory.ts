import { computed } from 'vue'
import { questionApi } from './api'
import { toHistoryPaper } from '@/api/contracts'
import { useAsyncState } from '@/shared/composables/useAsyncState'
import type { HistoryPaper } from '@/types/exam'

export function useExamHistory() {
  const state = useAsyncState<HistoryPaper[]>([])
  const count = computed(() => state.data.value.length)
  const load = () => state.execute(async () => (await questionApi.getPapers({ limit: 100 })).map(toHistoryPaper))
  return { ...state, count, load }
}

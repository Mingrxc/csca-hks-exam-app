import { favoriteApi } from './api'
import { useAsyncState } from '@/shared/composables/useAsyncState'
import type { ApiFavoriteItem } from '@/api/contracts'

export function useFavorites() {
  const state = useAsyncState<ApiFavoriteItem[]>([])
  const load = () => state.execute(() => favoriteApi.list())
  const remove = async (questionId: number) => {
    await favoriteApi.toggle(questionId)
    state.data.value = state.data.value.filter((item) => item.question_id !== questionId)
  }
  return { ...state, load, remove }
}

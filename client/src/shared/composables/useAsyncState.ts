import { computed, ref, watch } from 'vue'
import { activeUserId } from '@/shared/auth/session'
import type { Ref } from 'vue'

export function useAsyncState<T>(initialValue: T) {
  const fresh = () => initialValue && typeof initialValue === 'object' ? JSON.parse(JSON.stringify(initialValue)) as T : initialValue
  let generation = 0
  const data = ref(initialValue) as Ref<T>
  const loading = ref(false)
  const error = ref('')
  watch(activeUserId, () => { generation++; data.value = fresh(); loading.value = false; error.value = '' }, { flush: 'sync' })

  const isEmpty = computed(() => {
    const value = data.value
    return Array.isArray(value) ? value.length === 0 : value == null
  })

  async function execute(loader: () => Promise<T>): Promise<T | undefined> {
    if (loading.value) return undefined
    loading.value = true
    error.value = ''
    const current = ++generation
    try {
      const result = await loader()
      if (current !== generation) return undefined
      data.value = result
      return result
    } catch (reason) {
      if (current === generation) error.value = reason instanceof Error ? reason.message : '加载失败，请稍后重试'
      return undefined
    } finally {
      if (current === generation) loading.value = false
    }
  }

  return { data, loading, error, isEmpty, execute }
}

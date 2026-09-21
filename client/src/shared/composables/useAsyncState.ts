import { computed, ref } from 'vue'
import type { Ref } from 'vue'

export function useAsyncState<T>(initialValue: T) {
  const data = ref(initialValue) as Ref<T>
  const loading = ref(false)
  const error = ref('')

  const isEmpty = computed(() => {
    const value = data.value
    return Array.isArray(value) ? value.length === 0 : value == null
  })

  async function execute(loader: () => Promise<T>): Promise<T | undefined> {
    if (loading.value) return undefined
    loading.value = true
    error.value = ''
    try {
      const result = await loader()
      data.value = result
      return result
    } catch (reason) {
      error.value = reason instanceof Error ? reason.message : '加载失败，请稍后重试'
      return undefined
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, isEmpty, execute }
}

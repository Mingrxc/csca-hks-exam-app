import { computed, ref, watch } from 'vue'
import type { Ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { activeUserId, adminRole, getToken, setAdminRole, sessionGeneration } from '@/shared/auth/session'
import { errorText } from '@/i18n'

export function useAdminPage<T>(initial: T, fetcher: () => Promise<T>, ownerOnly = false) {
  const user = useUserStore()
  const fresh = () => initial == null ? initial : JSON.parse(JSON.stringify(initial)) as T
  const data = ref(fresh()) as Ref<T>
  const loading = ref(true)
  const saving = ref(false)
  const error = ref('')
  const allowed = computed(() => ownerOnly ? user.isOwner : user.isAdmin)
  let epoch = 0
  let loadSequence = 0
  function clear() { epoch++; data.value = fresh(); error.value = ''; loading.value = false; saving.value = false }
  watch([activeUserId, adminRole], clear, { flush: 'sync' })
  async function load() {
    const run = ++loadSequence
    const token = getToken()
    epoch++
    loading.value = true
    error.value = ''
    data.value = fresh()
    try {
      await user.restoreSession()
      if (run !== loadSequence || token !== getToken() || !user.isLogin) return
      await user.refreshProfile()
      if (run !== loadSequence || token !== getToken() || !allowed.value) return
      const current = ++epoch
      const session = sessionGeneration()
      loading.value = true
      const value = await fetcher()
      if (run === loadSequence && current === epoch && session === sessionGeneration() && allowed.value) data.value = value
    } catch (reason: any) {
      if (reason?.statusCode === 403 && reason?.code === 40341) setAdminRole('user')
      if (run === loadSequence && token === getToken() && allowed.value) error.value = errorText(reason?.message || '加载失败')
    } finally {
      if (run === loadSequence) loading.value = false
    }
  }
  async function write<R>(task: () => Promise<R>): Promise<R | undefined> {
    if (!user.isOwner || saving.value) return
    saving.value = true
    const current = epoch
    const session = sessionGeneration()
    try {
      const result = await task()
      if (current === epoch && session === sessionGeneration() && user.isOwner) return result
    } catch (reason: any) {
      if (reason?.code === 40341) setAdminRole('user')
      if (current === epoch) error.value = errorText(reason?.message || '操作失败，请稍后重试')
    } finally { if (current === epoch) saving.value = false }
  }
  onShow(load)
  return { user, data, loading, saving, error, allowed, load, write }
}

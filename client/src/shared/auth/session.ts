import { ref } from 'vue'

function storedToken(): string {
  try { return typeof uni === 'undefined' ? '' : String(uni.getStorageSync('token') || '') } catch { return '' }
}

export const accessToken = ref(storedToken())
export const activeUserId = ref(0)
export type AdminRole = 'user' | 'viewer' | 'owner'
export const adminRole = ref<AdminRole>('user')
export function setAdminRole(value: unknown) {
  adminRole.value = value === 'owner' || value === 'viewer' ? value : 'user'
}
let generation = 0
let loginPrompt: (() => void) | undefined

export const sessionGeneration = () => generation
export const getToken = () => accessToken.value
export function establishSession(token: string, userId: number) {
  generation++
  accessToken.value = token
  activeUserId.value = userId
  try { uni.setStorageSync('token', token) } catch {}
}
export function clearSession() {
  generation++
  activeUserId.value = 0
  accessToken.value = ''
  setAdminRole('user')
  try { uni.removeStorageSync('token') } catch {}
}
export function configureLoginPrompt(handler: () => void) { loginPrompt = handler }
export function notifyLoginRequired() { loginPrompt?.() }

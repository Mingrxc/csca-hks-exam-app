import { ref } from 'vue'

function storedToken(): string {
  try { return typeof uni === 'undefined' ? '' : String(uni.getStorageSync('token') || '') } catch { return '' }
}

export const accessToken = ref(storedToken())
export const activeUserId = ref(0)
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
  try { uni.removeStorageSync('token') } catch {}
}
export function configureLoginPrompt(handler: () => void) { loginPrompt = handler }
export function notifyLoginRequired() { loginPrompt?.() }

import { ref } from 'vue'
import { english } from './messages'

export type Language = 'zh' | 'en'
export const LANGUAGE_STORAGE_KEY = 'app_language_v1'
const locale = ref<Language>('zh')
export const language = locale

export function initializeLanguage(): Language {
  let saved: unknown
  try { saved = uni.getStorageSync(LANGUAGE_STORAGE_KEY) } catch { /* Fall back to WeChat language. */ }
  if (saved === 'zh' || saved === 'en') {
    locale.value = saved
    return saved
  }
  let detected = ''
  try { detected = uni.getAppBaseInfo?.().language || '' } catch {}
  try {
    if (!detected) detected = uni.getSystemInfoSync?.().language || ''
  } catch {}
  locale.value = !detected || /^zh(?:[-_]|$)/i.test(detected) ? 'zh' : 'en'
  return locale.value
}

export function getLanguage(): Language {
  return locale.value
}

export function setLanguage(value: Language): void {
  if (value !== 'zh' && value !== 'en') return
  locale.value = value
  try { uni.setStorageSync(LANGUAGE_STORAGE_KEY, value) } catch { /* Keep the in-memory choice. */ }
}

/** Translate interface copy only. Never pass question, announcement or user content here. */
export function t(message: string | null | undefined, params: Record<string, string | number> = {}): string {
  const key = message || ''
  const translated = locale.value === 'en' ? english[key] || key : key
  return translated.replace(/\{(\w+)\}/g, (match, key) => String(params[key] ?? match))
}

/** Backend errors are interface copy; unknown Chinese errors get a usable English fallback. */
export function errorText(message: string): string {
  if (locale.value !== 'en') return message
  const status = message.match(/^请求失败 \((\d+)\)$/)?.[1]
  if (status) return t('请求失败 ({status})', { status })
  return english[message] || (/[\u3400-\u9fff]/.test(message) ? t('操作失败，请稍后重试') : message)
}

export function levelLabel(level: string | number): string {
  return String(level) === '7-9' ? t('七至九级联合') : t('{level}级', { level })
}

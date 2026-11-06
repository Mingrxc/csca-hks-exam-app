import { language } from '@/i18n'
export function adminDate(value?: string | null) {
  if (!value) return '—'
  const iso = value.trim().replace(' ', 'T')
  const timestamp = new Date(/(?:Z|[+-]\d\d:\d\d)$/i.test(iso) ? iso : iso + 'Z').getTime()
  if (!Number.isFinite(timestamp)) return '—'
  // 部分微信环境缺少 Intl 时区数据，直接按 UTC+8 格式化。
  const date = new Date(timestamp + 8 * 60 * 60 * 1000)
  const pad = (part: number) => String(part).padStart(2, '0')
  const year = date.getUTCFullYear(), month = pad(date.getUTCMonth() + 1), day = pad(date.getUTCDate())
  const calendar = language.value === 'en' ? `${day}/${month}/${year}` : `${year}/${month}/${day}`
  return `${calendar} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`
}

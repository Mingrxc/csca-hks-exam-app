import { language } from '@/i18n'
export function adminDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(/(?:Z|[+-]\d\d:\d\d)$/.test(value) ? value : value + 'Z')
  if (!Number.isFinite(date.getTime())) return '—'
  return new Intl.DateTimeFormat(language.value === 'en' ? 'en-GB' : 'zh-CN', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
  }).format(date)
}

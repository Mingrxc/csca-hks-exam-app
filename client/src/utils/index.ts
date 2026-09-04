/**
 * 格式化时间（秒 → MM:SS）
 */
export function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

/**
 * 格式化日期
 */
export function formatDate(date: Date | string | number, fmt = 'YYYY-MM-DD'): string {
  const d = new Date(date)
  const map: Record<string, string> = {
    YYYY: String(d.getFullYear()),
    MM: String(d.getMonth() + 1).padStart(2, '0'),
    DD: String(d.getDate()).padStart(2, '0'),
    HH: String(d.getHours()).padStart(2, '0'),
    mm: String(d.getMinutes()).padStart(2, '0'),
    ss: String(d.getSeconds()).padStart(2, '0'),
  }
  return fmt.replace(/YYYY|MM|DD|HH|mm|ss/g, (match) => map[match] || match)
}

/**
 * 根据时段生成问候语
 */
export function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
}

export { DIFFICULTY_MAP, QUESTION_TYPE_MAP } from '@/constants/exam'

/**
 * 防抖
 */
export function debounce<T extends (...args: any[]) => any>(fn: T, delay = 300): T {
  let timer: any = null
  return ((...args: any[]) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }) as unknown as T
}

/**
 * 节流
 */
export function throttle<T extends (...args: any[]) => any>(fn: T, delay = 300): T {
  let last = 0
  return ((...args: any[]) => {
    const now = Date.now()
    if (now - last >= delay) {
      last = now
      fn(...args)
    }
  }) as unknown as T
}

/**
 * 计算考试倒计时
 */
export function getCountdown(targetDate: string): { days: string; hours: string; minutes: string } {
  const now = Date.now()
  const target = new Date(targetDate).getTime()
  const diff = target - now

  if (diff <= 0) return { days: '0', hours: '00', minutes: '00' }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  return {
    days: String(days),
    hours: String(hours).padStart(2, '0'),
    minutes: String(minutes).padStart(2, '0'),
  }
}

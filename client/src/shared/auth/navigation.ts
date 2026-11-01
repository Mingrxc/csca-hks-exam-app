import { useUserStore } from '@/stores/user'
import { showModal } from '@/i18n/ui'
import { t } from '@/i18n'

let pendingAction: (() => unknown) | undefined
let prompting = false

function currentPageAction(): (() => void) | undefined {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  if (!page?.route || page.route === 'pages/login/index') return
  const route = '/' + page.route
  if (['/pages/index/index', '/pages/exam/index', '/pages/profile/index'].includes(route)) return
  const query = Object.entries(page.options || {}).map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`).join('&')
  return () => uni.redirectTo({ url: route + (query ? '?' + query : '') })
}

export function openLogin(action?: () => unknown) {
  const pages = getCurrentPages()
  if (pages[pages.length - 1]?.route === 'pages/login/index') return
  pendingAction = action || currentPageAction()
  uni.navigateTo({ url: '/pages/login/index' })
}

export function promptLogin(action?: () => unknown) {
  if (prompting) return
  const pages = getCurrentPages()
  if (pages[pages.length - 1]?.route === 'pages/login/index') return
  prompting = true
  showModal({ title: t('登录后即可使用'), content: t('登录后保存你的学习记录与进度'), confirmText: t('去登录'),
    success: result => { if (result.confirm) openLogin(action) }, complete: () => { prompting = false },
  })
}

export async function requireLogin(action?: () => unknown): Promise<boolean> {
  const user = useUserStore()
  await user.restoreSession()
  if (user.isLogin) return true
  promptLogin(action)
  return false
}

export async function navigateProtected(url: string) {
  if (await requireLogin(() => navigateProtected(url))) uni.navigateTo({ url })
}

export function finishLogin() {
  const action = pendingAction
  pendingAction = undefined
  const pages = getCurrentPages()
  if (pages.length > 1) uni.navigateBack({ success: () => { action?.() } })
  else uni.switchTab({ url: '/pages/profile/index' })
}

export function cancelLogin() { pendingAction = undefined }

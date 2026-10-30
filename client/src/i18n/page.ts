import { watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { language, t } from './index'

const pageTitles: Record<string, string> = {
  'pages/index/index': '老外1点通',
  'pages/exam/index': '刷题',
  'pages/exam/paper': '组卷',
  'pages/exam/answer': '答题中',
  'pages/exam/result': '成绩报告',
  'pages/exam/history': '历史试卷',
  'pages/profile/index': '我的',
  'pages/favorite/index': '收藏题目',
  'pages/wrongbook/index': '错题本',
  'pages/wrongbook/detail': '错题详情',
  'pages/wrongbook/redo': '错题重做',
  'pages/feedback/index': '用户反馈',
  'pages/about/index': '关于',
  'pages/about/announcements': '更新公告',
  'pages/about/announcement': '公告详情',
  'pages/content-admin/index': '内容管理',
}
const tabTitles = ['首页', '刷题', '我的']
const tabRoutes = ['pages/index/index', 'pages/exam/index', 'pages/profile/index']

export function updatePageChrome(route: string): void {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]?.route?.replace(/^\//, '')
  if (current !== route) return
  const title = pageTitles[route]
  if (title) uni.setNavigationBarTitle({ title: t(title) })
  if (tabRoutes.includes(route)) {
    tabTitles.forEach((text, index) => uni.setTabBarItem({ index, text: t(text) }))
  }
}

/** No navigation or state reset: cached pages refresh their own chrome when shown. */
export function usePageI18n(route: string) {
  onShow(() => updatePageChrome(route))
  watch(language, () => updatePageChrome(route))
  return { t, language }
}

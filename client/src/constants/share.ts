import { APP_ICON_PATH } from '@/constants/brand'

const APP_SHARE_TITLE = '老外一点通｜CSCA、HSK备考练习'

export function createAppShareMessage() {
  return {
    title: APP_SHARE_TITLE,
    path: '/pages/index/index',
    // 固定图片避免默认页面截图包含用户的学习记录或聊天内容。
    imageUrl: APP_ICON_PATH,
  }
}

export function createTimelineShareMessage() {
  return {
    title: APP_SHARE_TITLE,
    // 朋友圈只能打开当前页，清空参数，避免沿用当前页面的个人数据标识。
    query: '',
    imageUrl: APP_ICON_PATH,
  }
}

export function isTimelinePreview(scene?: number): boolean {
  // #ifdef MP-WEIXIN
  if (scene !== undefined) return scene === 1154
  const options = typeof uni.getEnterOptionsSync === 'function'
    ? uni.getEnterOptionsSync()
    : uni.getLaunchOptionsSync()
  return options?.scene === 1154
  // #endif
  // #ifndef MP-WEIXIN
  return false
  // #endif
}

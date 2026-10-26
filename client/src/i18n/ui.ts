import { errorText, t } from './index'

export function showToast(options: Parameters<typeof uni.showToast>[0]) {
  return uni.showToast({ ...options, title: errorText(options.title) })
}

export function showLoading(options: Parameters<typeof uni.showLoading>[0]) {
  return uni.showLoading({ ...options, title: t(options.title) })
}

export function showActionSheet(options: Parameters<typeof uni.showActionSheet>[0]) {
  return uni.showActionSheet({ ...options, itemList: options.itemList.map(item => t(item)) })
}

export function showModal(options: Parameters<typeof uni.showModal>[0]) {
  return uni.showModal({
    ...options,
    title: t(options.title || ''),
    // Editable content is user data, such as a nickname.
    content: options.editable ? options.content : t(options.content || ''),
    placeholderText: t(options.placeholderText || ''),
    confirmText: t(options.confirmText || '确定'),
    cancelText: t(options.cancelText || '取消'),
  })
}

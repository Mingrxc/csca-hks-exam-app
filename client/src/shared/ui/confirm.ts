interface ConfirmOptions {
  title: string
  content: string
  confirmText?: string
}

export function confirmAction(options: ConfirmOptions): Promise<boolean> {
  return new Promise((resolve) => {
    uni.showModal({
      title: options.title,
      content: options.content,
      confirmText: options.confirmText || '确定',
      success: (result) => resolve(result.confirm),
      fail: () => resolve(false),
    })
  })
}

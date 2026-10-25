<template>
  <view class="page app-shell">
    <view class="app-section" v-if="initializing"><view class="app-card"><c-app-state state="loading" title="正在准备反馈" /></view></view>
    <view class="app-section" v-else-if="loadError"><view class="app-card"><c-app-state state="error" title="暂时无法提交反馈" description="请检查登录和网络状态后重试。" @retry="initialize" /></view></view>
    <view v-else-if="receipt" class="app-section">
      <view class="success-card app-card">
        <view class="success-icon"><t-icon name="check-circle" size="72rpx" /></view>
        <text class="success-title">反馈已收到</text>
        <text class="success-description">谢谢你，帮助我们把每一点体验做好。</text>
        <text class="receipt-number">反馈编号 #{{ receipt.id }}</text>
        <button class="secondary-button" @tap="startAnother">继续反馈</button>
      </view>
    </view>
    <view v-else class="feedback-form">
      <view class="app-section heading">
        <text class="app-section-title">说说你的想法</text>
        <text class="app-section-subtitle">一道题的疑惑，一次使用体验，或一个小建议</text>
      </view>
      <view class="app-section">
        <view class="form-card app-card app-card-pad">
          <text class="field-label">反馈类型</text>
          <view class="category-options">
            <view v-for="option in FEEDBACK_CATEGORIES" :key="option.value" class="category-chip" :class="{ selected: category === option.value }" @tap="selectCategory(option.value)">{{ option.label }}</view>
          </view>
          <text class="field-label content-label">反馈内容</text>
          <textarea class="feedback-input" :value="content" :disabled="sending" :maxlength="1000" placeholder="请描述你遇到的问题或建议。如果是题目问题，可以附上考试、等级及题目内容。" :adjust-position="true" :show-confirm-bar="true" @input="onInput" />
          <text class="word-count">{{ content.length }} / 1000</text>
        </view>
      </view>
      <view class="app-section">
        <text class="privacy-note">反馈仅开发者可见。请勿填写密码、证件号码等敏感信息。</text>
        <button class="submit-button" :disabled="!canSubmit" :loading="sending" @tap="submit">{{ sending ? '正在提交' : '提交反馈' }}</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { onLoad, onShow, onHide, onUnload } from '@dcloudio/uni-app'
import { APP_VERSION } from '@/constants/brand'
import { useUserStore } from '@/stores/user'
import { FEEDBACK_CATEGORIES, feedbackApi } from '@/features/feedback/api'
import type { FeedbackCategory, FeedbackReceipt } from '@/features/feedback/api'

const userStore = useUserStore()
const category = ref<FeedbackCategory>('suggestion')
const content = ref('')
const requestId = ref('')
const ownerId = ref(0)
const initializing = ref(true)
const loadError = ref(false)
const sending = ref(false)
const receipt = ref<FeedbackReceipt | null>(null)
let pageVisible = true
const canSubmit = computed(() => !initializing.value && !loadError.value && !sending.value && !!content.value.trim() && content.value.length <= 1000)
const draftKey = () => `feedback_draft_v1_${ownerId.value}`
const createRequestId = () => `fb_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 14)}`

function persistDraft() {
  if (!ownerId.value || ownerId.value !== userStore.userInfo.id || receipt.value) return
  try {
    uni.setStorageSync(draftKey(), { category: category.value, content: content.value, requestId: requestId.value, appVersion: APP_VERSION })
  } catch { /* Storage failure must not turn a successful server submission into failure. */ }
}

async function initialize() {
  initializing.value = true
  loadError.value = false
  content.value = ''
  category.value = 'suggestion'
  requestId.value = ''
  receipt.value = null
  try {
    if (!userStore.isLogin || !userStore.userInfo.id) await userStore.login()
    if (!userStore.userInfo.id) throw new Error('User unavailable')
    ownerId.value = userStore.userInfo.id
    let saved: any
    try { saved = uni.getStorageSync(draftKey()) } catch {}
    if (saved && typeof saved.content === 'string' && saved.content.length <= 1000) {
      content.value = saved.content
      if (FEEDBACK_CATEGORIES.some((option) => option.value === saved.category)) category.value = saved.category
      if (saved.appVersion === APP_VERSION && typeof saved.requestId === 'string' && /^[A-Za-z0-9_-]{8,64}$/.test(saved.requestId)) requestId.value = saved.requestId
    }
  } catch { loadError.value = true }
  finally { initializing.value = false }
}

function draftChanged() {
  requestId.value = createRequestId()
  persistDraft()
}

function onInput(event: { detail: { value: string } }) {
  if (sending.value) return
  content.value = event.detail.value
  draftChanged()
}

function selectCategory(value: FeedbackCategory) {
  if (sending.value || category.value === value) return
  category.value = value
  draftChanged()
}

async function submit() {
  if (!canSubmit.value) return
  if (ownerId.value !== userStore.userInfo.id || !userStore.isLogin) { await initialize(); return }
  if (!requestId.value) requestId.value = createRequestId()
  persistDraft()
  sending.value = true
  try {
    const result = await feedbackApi.submit({ request_id: requestId.value, category: category.value, content: content.value.trim(), app_version: APP_VERSION })
    if (ownerId.value !== userStore.userInfo.id) { await initialize(); return }
    receipt.value = result
    content.value = ''
    requestId.value = ''
    try { uni.removeStorageSync(draftKey()) } catch {}
    await nextTick()
    if (pageVisible) uni.pageScrollTo({ scrollTop: 0, duration: 0 })
  } catch {
    persistDraft()
  } finally { sending.value = false }
}

function startAnother() {
  receipt.value = null
  category.value = 'suggestion'
  content.value = ''
  requestId.value = ''
}

onLoad(initialize)
onShow(() => { pageVisible = true })
onHide(() => { pageVisible = false; persistDraft() })
onUnload(() => { pageVisible = false; persistDraft() })
</script>

<style lang="scss" scoped>
.heading { padding-top: 16rpx; }
.field-label { display: block; font-size: 28rpx; font-weight: 600; }
.category-options { display: flex; flex-wrap: wrap; gap: 14rpx; margin-top: 20rpx; }
.category-chip { border: 1rpx solid var(--app-border); border-radius: 999rpx; padding: 12rpx 22rpx; font-size: 25rpx; color: var(--app-text-weak); background: var(--app-surface-quiet); }
.category-chip.selected { background: var(--app-primary-soft); color: var(--app-primary); border-color: var(--app-primary); }
.content-label { margin-top: 36rpx; }
.feedback-input { display: block; width: 100%; min-height: 340rpx; margin-top: 20rpx; padding: 20rpx; border: 1rpx solid var(--app-border); border-radius: 18rpx; background: var(--app-surface-quiet); font-size: 28rpx; line-height: 1.8; color: var(--app-text); }
.word-count { display: block; margin-top: 12rpx; text-align: right; font-size: 22rpx; color: var(--app-text-mute); }
.privacy-note { display: block; padding: 0 4rpx; color: var(--app-text-mute); font-size: 23rpx; line-height: 1.8; }
.submit-button { width: 100%; margin: 24rpx 0 0; border-radius: 22rpx; background: var(--app-primary); color: var(--app-surface); font-size: 30rpx; font-weight: 600; line-height: 1.5; padding: 25rpx; }
.submit-button[disabled] { color: var(--app-text-mute); background: var(--app-primary-soft); }
.success-card { padding: 64rpx 32rpx 44rpx; text-align: center; }
.success-icon { color: var(--app-secondary); }
.success-title { display: block; margin-top: 22rpx; font-size: 36rpx; font-weight: 600; }
.success-description { display: block; margin-top: 16rpx; color: var(--app-text-weak); font-size: 26rpx; line-height: 1.8; }
.receipt-number { display: block; margin-top: 20rpx; font-size: 24rpx; color: var(--app-text-mute); }
.secondary-button { margin: 36rpx 0 0; color: var(--app-primary); background: var(--app-primary-soft); border-radius: 20rpx; font-size: 28rpx; padding: 12rpx; }
</style>

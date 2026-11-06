<template>
  <c-auth-frame>
  <view class="page app-shell">
    <view class="app-section" v-if="initializing"><view class="app-card"><c-app-state state="loading" :title="t('正在准备反馈')" /></view></view>
    <view class="app-section" v-else-if="loadError"><view class="app-card"><c-app-state state="error" :title="t('暂时无法提交反馈')" :description="t('请检查登录和网络状态后重试。')" @retry="initialize" /></view></view>
    <view v-else-if="receipt" class="app-section">
      <view class="success-card app-card">
        <view class="success-icon"><t-icon name="check-circle" size="72rpx" /></view>
        <text class="success-title">{{ t("反馈已收到") }}</text>
        <text class="receipt-number">{{ t('反馈编号 #{id}', { id: receipt.id }) }}</text>
        <button class="secondary-button" @tap="startAnother">{{ t("继续反馈") }}</button>
      </view>
    </view>
    <view v-else class="feedback-form">
      <view class="app-section heading">
        <text class="app-section-title">{{ t("用户反馈") }}</text>
      </view>
      <view class="app-section">
        <view class="form-card app-card app-card-pad">
          <text class="field-label">{{ t("反馈类型") }}</text>
          <view class="category-options">
            <view v-for="option in FEEDBACK_CATEGORIES" :key="option.value" class="category-chip" :class="{ selected: category === option.value }" @tap="selectCategory(option.value)">{{ t(option.label) }}</view>
          </view>
          <text class="field-label content-label">{{ t("反馈内容") }}</text>
          <textarea class="feedback-input" :value="content" :disabled="sending" :maxlength="1000" :placeholder="t('请描述你遇到的问题或建议。如果是题目问题，可以附上考试、等级及题目内容。')" :adjust-position="true" :show-confirm-bar="true" @input="onInput" />
          <text class="word-count">{{ content.length }} / 1000</text>
        </view>
      </view>
      <view class="app-section">
        <button class="submit-button" :disabled="!canSubmit" :loading="sending" @tap="submit">{{ sending ? t("正在提交") : t("提交反馈") }}</button>
      </view>
    </view>
  </view>
  </c-auth-frame>
</template>

<script setup lang="ts">
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { computed, nextTick, ref } from 'vue'
import { onLoad, onShow, onHide, onUnload } from '@dcloudio/uni-app'
import { APP_VERSION } from '@/constants/brand'
import { useUserStore } from '@/stores/user'
import { FEEDBACK_CATEGORIES, feedbackApi } from '@/features/feedback/api'
import type { FeedbackCategory, FeedbackReceipt } from '@/features/feedback/api'

usePageI18n('pages/feedback/index')

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
const canSubmit = computed(() => userStore.isLogin && ownerId.value === userStore.userInfo.id && !initializing.value && !loadError.value && !sending.value && !!content.value.trim() && content.value.length <= 1000)
const draftKey = () => `feedback_draft_v1_${ownerId.value}`
const createRequestId = () => `fb_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 14)}`

function persistDraft() {
  if (!ownerId.value || ownerId.value !== userStore.userInfo.id || receipt.value) return
  try {
    uni.setStorageSync(draftKey(), { category: category.value, content: content.value, requestId: requestId.value, appVersion: APP_VERSION })
  } catch {
    // 服务端已收件，草稿缓存清理失败时仍显示提交成功。
  }
}

async function initialize() {
  initializing.value = true
  loadError.value = false
  content.value = ''
  category.value = 'suggestion'
  requestId.value = ''
  receipt.value = null
  try {
    await userStore.restoreSession()
    if (!userStore.isLogin || !userStore.userInfo.id) { ownerId.value = 0; return }
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
  if (ownerId.value !== userStore.userInfo.id || !userStore.isLogin) { await initialize(); return }
  if (!canSubmit.value) return
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
.submit-button { width: 100%; margin: 0; border-radius: 22rpx; background: var(--app-primary); color: var(--app-surface); font-size: 30rpx; font-weight: 600; line-height: 1.5; padding: 25rpx; }
.submit-button[disabled] { color: var(--app-text-mute); background: var(--app-primary-soft); }
.success-card { padding: 64rpx 32rpx 44rpx; text-align: center; }
.success-icon { color: var(--app-secondary); }
.success-title { display: block; margin-top: 22rpx; font-size: 36rpx; font-weight: 600; }
.receipt-number { display: block; margin-top: 20rpx; font-size: 24rpx; color: var(--app-text-mute); }
.secondary-button { margin: 36rpx 0 0; color: var(--app-primary); background: var(--app-primary-soft); border-radius: 20rpx; font-size: 28rpx; padding: 12rpx; }
</style>

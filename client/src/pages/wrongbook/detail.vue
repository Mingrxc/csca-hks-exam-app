<template>
  <view class="page app-shell" v-if="question">
    <view class="app-section">
      <view class="question-section app-card app-card-pad">
        <view class="q-header">
          <view class="tag-row">
            <t-tag theme="primary" variant="light" shape="round" size="small">{{ t(question.typeLabel) }}</t-tag>
            <t-tag theme="default" variant="light" shape="round" size="small" :class="question.difficulty">{{ t(question.diffLabel) }}</t-tag>
            <t-tag theme="warning" variant="light" shape="round" size="small">{{ t(domainLabel) }}·{{ t(domainValue) }}</t-tag>
          </view>
          <t-tag theme="danger" variant="light" shape="round" size="small">{{ t('错误 {n} 次', { n: question.wrongCount }) }}</t-tag>
        </view>

        <text class="q-stem">{{ question.stem }}</text>

        <view class="q-options">
          <view
            class="option"
            :class="{
              correct: opt.key === question.answer,
              my: opt.key === question.myAnswer,
              wrong: opt.key === question.myAnswer && opt.key !== question.answer
            }"
            v-for="opt in question.options"
            :key="opt.key"
          >
            <view class="option-key">{{ opt.key }}</view>
            <text class="option-text">{{ opt.text }}</text>
            <text class="option-mark" v-if="opt.key === question.answer">✓</text>
            <text class="option-mark wrong-mark" v-else-if="opt.key === question.myAnswer">✗</text>
          </view>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="analysis-section app-card app-card-pad">
        <view class="analysis-header">
          <text class="analysis-title">{{ t("题目解析") }}</text>
        </view>
        <text class="analysis-text">{{ question.analysis }}</text>

        <view class="confusion-box" v-if="question.confusion">
          <text class="confusion-title">{{ t("易混选项辨析") }}</text>
          <text class="confusion-text">{{ question.confusion }}</text>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="related-section">
        <view class="related-header">
          <text class="app-section-title">{{ t("举一反三") }}</text>
          <text class="app-section-subtitle">{{ t('以下题目基于相同{label}「{value}」推荐。', { label: t(domainLabel), value: t(domainValue) }) }}</text>
        </view>
        <c-app-state v-if="relatedLoading" compact state="loading" :title="t('正在寻找相关练习')" />
        <c-app-state v-else-if="relatedError" compact state="error" :title="t('相关练习暂时无法加载')" @retry="loadRelated" />
        <view v-else class="related-list">
          <view class="related-item app-card" v-for="item in relatedQuestions" :key="item.id" @click="goRelated">
            <view class="related-tags">
              <t-tag theme="primary" variant="light" shape="round" size="small">{{ t(item.diffLabel) }}</t-tag>
              <t-tag theme="default" variant="light" shape="round" size="small">{{ t(item.typeLabel) }}</t-tag>
            </view>
            <text class="related-stem">{{ item.stem }}</text>
            <text class="related-action">{{ t("去练习 ›") }}</text>
          </view>
        </view>
        <c-app-state v-if="!relatedLoading && !relatedError && !relatedQuestions.length" compact state="empty" :title="t('暂时没有相关练习')" />
      </view>
    </view>

    <view class="actions">
      <t-button theme="primary" block shape="round" @click="markMastered">
        {{ question.mastered ? t("已掌握") : t("标记为已掌握") }}
      </t-button>
      <t-button theme="default" variant="outline" block shape="round" @click="sendToAI">{{ t("发给 AI") }}</t-button>
      <t-button theme="default" variant="outline" block shape="round" @click="goRedo">{{ t("重做错题") }}</t-button>
    </view>
  </view>
  <view class="app-shell" v-else>
    <view class="app-section">
      <c-app-state v-if="isLoading" state="loading" :title="t('正在加载错题详情')" />
      <c-app-state v-else state="error" :title="t('错题详情暂时无法加载')" :description="loadError" @retry="loadDetail(detailId, detailQuestionId)" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { showToast } from '@/i18n/ui'
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { computed, ref } from 'vue'
import { onShareAppMessage, onLoad } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import { wrongBookApi } from '@/features/wrongbook/api'
import { toRelatedQuestion, toWrongBookDetail } from '@/api/contracts'
import { getExamLabel, getQuestionDomain, getQuestionDomainLabel } from '@/constants/exam'
import type { RelatedQuestion, WrongBookDetail } from '@/types/wrongbook'

usePageI18n('pages/wrongbook/detail')

const question = ref<WrongBookDetail | null>(null)
const wrongBookId = ref<number | null>(null)
const isLoading = ref(true)
const loadError = ref('')
const detailId = ref<number>()
const detailQuestionId = ref<number>()
const relatedQuestionId = ref(0)
const relatedLoading = ref(false)
const relatedError = ref(false)

const relatedQuestions = ref<RelatedQuestion[]>([])
const domainLabel = computed(() => (question.value ? getQuestionDomainLabel(question.value.examType) : '专项'))
const domainValue = computed(() => (question.value ? getQuestionDomain(question.value) : ''))

const loadDetail = async (id?: number, questionId?: number) => {
  if (!id && !questionId) return
  isLoading.value = true
  loadError.value = ''
  try {
    const payload = questionId ? await wrongBookApi.getDetailByQuestion(questionId) : await wrongBookApi.getDetail(id as number)
    question.value = toWrongBookDetail(payload)
    wrongBookId.value = payload.id
    relatedQuestionId.value = payload.question_id

    void loadRelated()
  } catch {
    loadError.value = '请检查网络连接后重试。'
  } finally {
    isLoading.value = false
  }
}

const loadRelated = async () => {
  if (!question.value || relatedLoading.value) return
  relatedLoading.value = true
  relatedError.value = false
  try {
    const items = await wrongBookApi.getRelated(relatedQuestionId.value)
    relatedQuestions.value = items.map(toRelatedQuestion)
  } catch {
    relatedError.value = true
  } finally {
    relatedLoading.value = false
  }
}

onLoad((query) => {
  const id = Number(query?.id)
  const questionId = Number(query?.questionId)
  if (Number.isInteger(questionId) && questionId > 0) {
    detailQuestionId.value = questionId
    loadDetail(undefined, questionId)
    return
  }
  if (Number.isInteger(id) && id > 0) {
    detailId.value = id
    loadDetail(id)
    return
  }
  isLoading.value = false
  loadError.value = '未找到这道错题的记录。'
  showToast({ title: '未找到错题记录', icon: 'none' })
  setTimeout(() => uni.navigateBack(), 300)
})

const markMastered = async () => {
  if (!question.value || !wrongBookId.value) return
  try {
    const payload = await wrongBookApi.markMastered(wrongBookId.value)
    question.value.mastered = payload.is_mastered
    showToast({ title: payload.is_mastered ? '已标记为掌握' : '已取消标记', icon: 'success' })
  } catch {
    // The shared request layer already displays the error message.
  }
}

const goRelated = () => {
  if (!question.value) return
  const special = encodeURIComponent(domainValue.value)
  uni.navigateTo({
    url: `/pages/exam/paper?strategy=knowledge&examType=${question.value.examType}&special=${special}`,
  })
}

const goRedo = () => {
  if (!question.value) return
  uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${question.value.examType}` })
}

const sendToAI = () => {
  if (!question.value) return
  uni.setStorageSync('ai_prefill', {
    content: question.value.stem,
    topic: t('{exam} 错题咨询', { exam: getExamLabel(question.value.examType) }),
    context: [
      t('考试类型：{value}', { value: getExamLabel(question.value.examType) }),
      `${domainLabel.value}：${domainValue.value}`,
      t('我的答案：{value}', { value: question.value.myAnswer || '未作答' }),
      t('正确答案：{value}', { value: question.value.answer || '暂无' }),
      question.value.analysis ? t('解析：{value}', { value: question.value.analysis }) : '',
      question.value.confusion ? t('易混选项：{value}', { value: question.value.confusion }) : '',
    ]
      .filter(Boolean)
      .join('\n'),
    examType: question.value.examType,
  })
  uni.switchTab({ url: '/pages/ai/index' })
}
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
// #endif
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
}

.q-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 18rpx;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.q-stem {
  display: block;
  font-size: 30rpx;
  line-height: 1.75;
  color: var(--app-text);
  margin-bottom: 22rpx;
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.option {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx;
  border-radius: var(--app-radius-md);
  border: 1rpx solid var(--app-border);
  background: rgba(255, 251, 246, 0.96);
}

.option.correct {
  border-color: rgba(126, 154, 128, 0.24);
  background: #eff5ef;
}

.option.wrong {
  border-color: rgba(198, 95, 82, 0.24);
  background: #fbefeb;
}

.option.my {
  box-shadow: inset 0 0 0 1rpx rgba(184, 107, 75, 0.18);
}

.option-key {
  width: 44rpx;
  height: 44rpx;
  border-radius: 999px;
  background: var(--app-surface-quiet);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  color: var(--app-text-weak);
}

.option.correct .option-key {
  background: var(--app-success);
  color: #ffffff;
}

.option.wrong .option-key {
  background: var(--app-danger);
  color: #ffffff;
}

.option-text {
  flex: 1;
  font-size: 26rpx;
  line-height: 1.6;
  color: var(--app-text);
}

.option-mark {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-success);
}

.wrong-mark {
  color: var(--app-danger);
}

.analysis-section {
  background: rgba(255, 251, 246, 0.98);
}

.analysis-header {
  margin-bottom: 12rpx;
}

.analysis-title {
  font-size: 30rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.analysis-text {
  font-size: 26rpx;
  line-height: 1.7;
  color: var(--app-text-weak);
}

.confusion-box {
  margin-top: 16rpx;
  padding: 18rpx;
  border-radius: var(--app-radius-md);
  background: var(--app-accent-soft);
}

.confusion-title {
  display: block;
  margin-bottom: 8rpx;
  font-size: 24rpx;
  line-height: 1.4;
  font-weight: 600;
  color: #92400e;
}

.confusion-text {
  font-size: 24rpx;
  line-height: 1.7;
  color: #92400e;
}

.related-header {
  margin-bottom: 14rpx;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.related-item {
  padding: 20rpx 22rpx;
  border-left: 4rpx solid var(--app-primary);
  background: rgba(255, 251, 246, 0.96);
}

.related-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.related-stem {
  display: block;
  font-size: 24rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.related-action {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--app-primary);
}

.actions {
  padding: 8rpx 24rpx 36rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.loading-state {
  padding: 120rpx 24rpx;
  text-align: center;
  font-size: 28rpx;
  color: var(--app-text-weak);
}
</style>

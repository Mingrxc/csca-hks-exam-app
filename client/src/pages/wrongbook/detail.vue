<template>
  <view class="page app-shell" v-if="question">
    <view class="app-section">
      <view class="question-section app-card app-card-pad">
        <view class="q-header">
          <view class="tag-row">
            <t-tag theme="primary" variant="light" shape="round" size="small">{{ question.typeLabel }}</t-tag>
            <t-tag theme="default" variant="light" shape="round" size="small" :class="question.difficulty">{{ question.diffLabel }}</t-tag>
            <t-tag theme="warning" variant="light" shape="round" size="small">{{ domainLabel }}·{{ domainValue }}</t-tag>
          </view>
          <t-tag theme="danger" variant="light" shape="round" size="small">错误 {{ question.wrongCount }} 次</t-tag>
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
          <text class="analysis-title">题目解析</text>
        </view>
        <text class="analysis-text">{{ question.analysis }}</text>

        <view class="confusion-box" v-if="question.confusion">
          <text class="confusion-title">易混选项辨析</text>
          <text class="confusion-text">{{ question.confusion }}</text>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="related-section">
        <view class="related-header">
          <text class="app-section-title">举一反三</text>
          <text class="app-section-subtitle">以下题目基于相同{{ domainLabel }}「{{ domainValue }}」推荐。</text>
        </view>
        <view class="related-list">
          <view class="related-item app-card" v-for="item in relatedQuestions" :key="item.id" @click="goRelated">
            <view class="related-tags">
              <t-tag theme="primary" variant="light" shape="round" size="small">{{ item.diffLabel }}</t-tag>
              <t-tag theme="default" variant="light" shape="round" size="small">{{ item.typeLabel }}</t-tag>
            </view>
            <text class="related-stem">{{ item.stem }}</text>
            <text class="related-action">去练习 ›</text>
          </view>
        </view>
      </view>
    </view>

    <view class="actions">
      <t-button theme="primary" block shape="round" @click="markMastered">
        {{ question.mastered ? '已掌握' : '标记为已掌握' }}
      </t-button>
      <t-button theme="default" variant="outline" block shape="round" @click="sendToAI">发给 AI</t-button>
      <t-button theme="default" variant="outline" block shape="round" @click="goRedo">加入重做列表</t-button>
    </view>
  </view>
  <view class="loading-state" v-else>正在加载错题详情...</view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { wrongBookApi } from '@/api'
import { toRelatedQuestion, toWrongBookDetail } from '@/api/contracts'
import { getQuestionDomain, getQuestionDomainLabel } from '@/constants/exam'
import type { RelatedQuestion, WrongBookDetail } from '@/types/wrongbook'

const question = ref<WrongBookDetail | null>(null)
const wrongBookId = ref<number | null>(null)

const relatedQuestions = ref<RelatedQuestion[]>([])
const domainLabel = computed(() => (question.value ? getQuestionDomainLabel(question.value.examType) : '专项'))
const domainValue = computed(() => (question.value ? getQuestionDomain(question.value) : ''))

const loadDetail = async (id?: number, questionId?: number) => {
  try {
    const payload = questionId ? await wrongBookApi.getDetailByQuestion(questionId) : await wrongBookApi.getDetail(id as number)
    question.value = toWrongBookDetail(payload)
    wrongBookId.value = payload.id

    const related = await wrongBookApi.getRelated(payload.question_id)
    relatedQuestions.value = related.map(toRelatedQuestion)
  } catch {
    // The shared request layer already displays the error message.
  }
}

onLoad((query) => {
  const id = Number(query?.id)
  const questionId = Number(query?.questionId)
  if (Number.isInteger(questionId) && questionId > 0) {
    loadDetail(undefined, questionId)
    return
  }
  if (Number.isInteger(id) && id > 0) {
    loadDetail(id)
    return
  }
  uni.showToast({ title: '未找到错题记录', icon: 'none' })
  setTimeout(() => uni.navigateBack(), 300)
})

const markMastered = async () => {
  if (!question.value || !wrongBookId.value) return
  try {
    const payload = await wrongBookApi.markMastered(wrongBookId.value)
    question.value.mastered = payload.is_mastered
    uni.showToast({ title: payload.is_mastered ? '已标记为掌握' : '已取消标记', icon: 'success' })
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
    topic: `${question.value.examType} 错题咨询`,
    context: [
      `考试类型：${question.value.examType}`,
      `${domainLabel.value}：${domainValue.value}`,
      `我的答案：${question.value.myAnswer || '未作答'}`,
      `正确答案：${question.value.answer || '暂无'}`,
      question.value.analysis ? `解析：${question.value.analysis}` : '',
      question.value.confusion ? `易混选项：${question.value.confusion}` : '',
    ]
      .filter(Boolean)
      .join('\n'),
    examType: question.value.examType,
  })
  uni.switchTab({ url: '/pages/ai/index' })
}
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
  box-shadow: inset 0 0 0 1rpx rgba(199, 127, 94, 0.18);
}

.option-key {
  width: 44rpx;
  height: 44rpx;
  border-radius: 999px;
  background: #f7efe5;
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
  color: #524740;
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

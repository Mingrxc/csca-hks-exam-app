<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="score-header app-card app-card-pad" :class="passed ? 'passed' : 'failed'">
        <view class="score-head">
          <view class="score-copy">
            <t-tag :theme="passed ? 'success' : 'warning'" variant="light" shape="round">
              {{ passed ? '通过' : '继续加油' }}
            </t-tag>
            <text class="score-title">{{ passed ? '恭喜通过！' : '这次已经比上次更接近了' }}</text>
            <text class="score-subtitle">本次答题结果会和错题记录一起保留，方便后面回看。</text>
          </view>
          <view class="score-ring-wrap">
            <c-ring-chart :percent="result.correctRate" :size="180" :line-width="14" :label="'正确率'" />
          </view>
        </view>

        <view class="score-stats">
          <view class="stat-item">
            <text class="stat-value">{{ result.correctCount }}/{{ result.totalCount }}</text>
            <text class="stat-label">正确</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ result.correctRate }}%</text>
            <text class="stat-label">正确率</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ result.timeUsed }}</text>
            <text class="stat-label">用时</text>
          </view>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="analysis-head app-row">
        <view>
          <text class="app-section-title">{{ analysisTitle }}</text>
          <text class="app-section-subtitle">{{ analysisSubtitle }}</text>
        </view>
        <t-tag theme="primary" variant="light" shape="round" size="small">{{ paperExamType }}</t-tag>
      </view>
      <view class="analysis-card app-card" v-if="analysisItems.length">
        <view class="analysis-item" v-for="item in analysisItems" :key="item.name">
          <view class="analysis-top">
            <text class="analysis-name">{{ item.name }}</text>
            <text class="analysis-rate">{{ item.correctRate }}%</text>
          </view>
          <view class="analysis-track">
            <view class="analysis-fill" :style="{ width: item.correctRate + '%' }"></view>
          </view>
          <text class="analysis-desc">{{ item.correct }}/{{ item.total }} 题答对</text>
        </view>
      </view>
      <t-empty v-else :description="analysisEmptyText" />
    </view>

    <view class="app-section">
      <text class="app-section-title">答题用时</text>
      <text class="app-section-subtitle">用时越稳定，节奏就越容易保持。</text>
      <view class="time-card app-card">
        <view class="time-row">
          <view class="bar-label">总用时</view>
          <view class="bar-track">
            <view class="bar-fill" :style="{ width: timeUsagePercent + '%' }"></view>
          </view>
          <view class="bar-time">{{ result.timeUsed }}</view>
        </view>
      </view>
    </view>

    <view class="app-section" v-if="wrongQuestions.length > 0">
      <text class="app-section-title">错题回顾（{{ wrongQuestions.length }}题）</text>
      <text class="app-section-subtitle">先看错在哪里，再决定下一步怎么练。</text>
      <view class="wrong-list">
        <view class="wrong-item app-card" v-for="q in wrongQuestions" :key="q.id" @click="goDetail(q.id)">
          <text class="wrong-stem">{{ q.stem }}</text>
          <view class="wrong-info">
            <t-tag theme="default" variant="light" shape="round" size="small">{{ q.typeLabel }}</t-tag>
            <text class="wrong-your">你的答案：{{ q.yourAnswer }}</text>
            <text class="wrong-correct">正确答案：{{ q.correctAnswer }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="app-section" id="all-review" v-if="showReview">
      <text class="app-section-title">全部解析（{{ reviewQuestions.length }}题）</text>
      <text class="app-section-subtitle">如果想一次看全，直接往下展开。</text>
      <view class="review-list">
        <view class="review-item app-card" v-for="(question, index) in reviewQuestions" :key="question.id">
          <view class="review-header">
            <text class="review-index">第 {{ index + 1 }} 题 · {{ question.typeLabel }}</text>
            <t-tag :theme="question.correct ? 'success' : 'danger'" variant="light" shape="round" size="small">
              {{ question.correct ? '正确' : '错误' }}
            </t-tag>
          </view>
          <text class="review-stem">{{ question.stem }}</text>
          <view class="review-options" v-if="question.options.length">
            <text class="review-option" v-for="option in question.options" :key="option.key">
              {{ option.key }}. {{ option.text }}
            </text>
          </view>
          <view class="review-answer-row">
            <text>你的答案：{{ question.userAnswer || '未作答' }}</text>
            <text class="review-correct-answer">正确答案：{{ question.correctAnswer }}</text>
          </view>
          <view class="review-analysis">{{ question.analysis }}</view>
        </view>
      </view>
    </view>

    <view class="actions">
      <t-button theme="default" variant="outline" block shape="round" @click="reviewAll">
        {{ showReview ? '收起全部解析' : '查看全部解析' }}
      </t-button>
      <t-button theme="primary" block shape="round" @click="goHome">返回首页</t-button>
      <t-button theme="default" variant="outline" block shape="round" @click="retryWrong">错题重做</t-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { examApi } from '@/features/exam/api'
import { toExamResultSummary, toResultReviewQuestions, toResultWrongQuestions } from '@/api/contracts'
import { useExamStore } from '@/stores/exam'
import type { ApiQuestion } from '@/api/contracts'
import type { ExamResultSummary, ExamType, ResultReviewQuestion, ResultWrongQuestion } from '@/types/exam'

const examStore = useExamStore()
const result = ref<ExamResultSummary>({
  score: 0,
  correctCount: 0,
  totalCount: 0,
  correctRate: 0,
  timeUsed: '00:00',
})
const isLoading = ref(false)
const showReview = ref(false)
const paperExamType = ref<ExamType>(examStore.config.examType)
const paperQuestions = ref<ApiQuestion[]>([])
const questionResultMap = ref<Record<number, boolean>>({})

const passed = computed(() => result.value.correctRate >= 60)

const wrongQuestions = ref<ResultWrongQuestion[]>([])
const reviewQuestions = ref<ResultReviewQuestion[]>([])
const analysisTitle = computed(() => (paperExamType.value === 'CSCA' ? '科目分析' : '知识点分析'))
const analysisSubtitle = computed(() =>
  paperExamType.value === 'CSCA'
    ? 'CSCA 按科目回看表现，方便定位哪一门最需要补。'
    : 'HSK 按知识点回看表现，便于找到该补的细分项。',
)
const analysisEmptyText = computed(() =>
  paperExamType.value === 'CSCA' ? '暂无科目统计' : '暂无知识点统计',
)
const analysisItems = computed(() => {
  const map = new Map<string, { total: number; correct: number }>()
  const questions = paperQuestions.value
  questions.forEach((question) => {
    const name = paperExamType.value === 'CSCA' ? question.subject : question.knowledge_point
    if (!name) return
    const bucket = map.get(name) || { total: 0, correct: 0 }
    bucket.total += 1
    bucket.correct += questionResultMap.value[question.id] ? 1 : 0
    map.set(name, bucket)
  })
  return Array.from(map.entries()).map(([name, value]) => ({
    name,
    total: value.total,
    correct: value.correct,
    correctRate: value.total ? Math.round((value.correct / value.total) * 100) : 0,
  }))
})

const timeUsagePercent = computed(() => {
  const [minutes, seconds] = result.value.timeUsed.split(':').map(Number)
  const usedSeconds = minutes * 60 + seconds
  const configuredSeconds = examStore.config.timeLimit * 60
  if (!configuredSeconds) return 100
  return Math.min(100, Math.max(6, Math.round((usedSeconds / configuredSeconds) * 100)))
})

const loadResult = async (paperId: number) => {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const payload = await examApi.getResult(paperId)
    result.value = toExamResultSummary(payload)
    wrongQuestions.value = toResultWrongQuestions(payload)
    reviewQuestions.value = toResultReviewQuestions(payload)
    paperQuestions.value = payload.paper.questions
    paperExamType.value = payload.paper.exam_type
    questionResultMap.value = Object.fromEntries(
      payload.review_questions.map((question) => [question.id, question.is_correct]),
    )
  } catch {
    // The shared request layer already displays the error message.
  } finally {
    isLoading.value = false
  }
}

onLoad((query) => {
  const paperId = Number(query?.paperId || query?.id || examStore.paperId)
  if (!Number.isInteger(paperId) || paperId <= 0) {
    uni.showToast({ title: '未找到试卷结果', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 300)
    return
  }
  loadResult(paperId)
})

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/wrongbook/detail?questionId=${id}` })
}

const reviewAll = async () => {
  showReview.value = !showReview.value
  if (showReview.value) {
    await nextTick()
    uni.pageScrollTo({ selector: '#all-review', duration: 250 })
  }
}

const goHome = () => uni.switchTab({ url: '/pages/index/index' })
const retryWrong = () => {
  uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${paperExamType.value}` })
}
</script>

<style lang="scss" scoped>
.score-header {
  background: linear-gradient(180deg, rgba(199, 127, 94, 0.08), rgba(255, 251, 246, 0.9));
}

.score-header.failed {
  background: linear-gradient(180deg, rgba(208, 161, 106, 0.12), rgba(255, 251, 246, 0.92));
}

.score-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.score-copy {
  flex: 1;
  min-width: 0;
}

.score-title {
  display: block;
  margin-top: 12rpx;
  font-size: 34rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.score-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--app-text-weak);
}

.score-ring-wrap {
  flex: none;
}

.score-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12rpx;
  margin-top: 20rpx;
}

.stat-item {
  padding: 16rpx 12rpx;
  border-radius: var(--app-radius-md);
  background: rgba(255, 251, 246, 0.74);
  border: 1rpx solid var(--app-border);
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 32rpx;
  line-height: 1.1;
  font-weight: 600;
  color: var(--app-text);
}

.stat-label {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.analysis-head {
  margin-bottom: 16rpx;
}

.analysis-card,
.time-card {
  padding: 22rpx;
}

.analysis-item {
  margin-bottom: 16rpx;
}

.analysis-item:last-child {
  margin-bottom: 0;
}

.analysis-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14rpx;
  margin-bottom: 10rpx;
}

.analysis-name {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-text);
}

.analysis-rate {
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.analysis-track {
  height: 12rpx;
  background: #f2e7db;
  border-radius: 999px;
  overflow: hidden;
}

.analysis-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--app-primary), var(--app-accent));
}

.analysis-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: var(--app-text-weak);
}

.time-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.bar-label {
  flex: none;
  width: 72rpx;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.bar-track {
  flex: 1;
  height: 12rpx;
  background: #f2e7db;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--app-secondary), var(--app-primary));
}

.bar-time {
  flex: none;
  width: 84rpx;
  text-align: right;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.wrong-list,
.review-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.wrong-item {
  padding: 22rpx;
}

.wrong-stem {
  display: block;
  font-size: 26rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.wrong-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx 14rpx;
  margin-top: 12rpx;
}

.wrong-your,
.wrong-correct {
  font-size: 21rpx;
}

.wrong-your {
  color: var(--app-danger);
}

.wrong-correct {
  color: var(--app-success);
}

.review-item {
  padding: 22rpx;
}

.review-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-bottom: 14rpx;
}

.review-index {
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.review-stem {
  display: block;
  font-size: 26rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.review-options {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-top: 14rpx;
}

.review-option {
  font-size: 23rpx;
  line-height: 1.6;
  color: #524740;
}

.review-answer-row {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-top: 16rpx;
  padding-top: 14rpx;
  border-top: 1rpx solid var(--app-border);
  font-size: 22rpx;
  color: var(--app-danger);
}

.review-correct-answer {
  color: var(--app-success);
}

.review-analysis {
  margin-top: 14rpx;
  padding: 16rpx;
  border-radius: var(--app-radius-md);
  background: #faf4ec;
  font-size: 23rpx;
  line-height: 1.65;
  color: #524740;
}

.actions {
  padding: 8rpx 24rpx 36rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}
</style>

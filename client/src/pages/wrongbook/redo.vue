<template>
  <view class="page app-page">
    <view class="top-bar app-card">
      <t-button class="top-action" theme="default" variant="text" size="small" shape="round" @click="confirmExit">
        退出
      </t-button>
      <view class="progress-info">
        <text class="question-index">{{ questions.length ? currentIndex + 1 : 0 }} / {{ questions.length }}</text>
      </view>
      <t-tag theme="danger" variant="light" shape="round">错题重做</t-tag>
    </view>

    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
    </view>

    <scroll-view class="question-area" scroll-y>
      <view class="question-card app-card app-card-pad">
        <c-question-item
          v-if="currentQuestion"
          :question="currentQuestion"
          :index="currentIndex"
          :user-answer="answers[currentIndex] || ''"
          :show-result="!!showResult[currentIndex]"
          @select="selectOption"
        />
        <view v-else class="empty-question">
          {{ isLoading ? '加载错题中...' : '暂无可重做错题' }}
        </view>
      </view>
    </scroll-view>

    <view class="bottom-bar app-card">
      <t-button class="bar-btn" theme="default" variant="outline" shape="round" :disabled="currentIndex === 0 || isLoading" @click="prevQuestion">
        上一题
      </t-button>
      <t-button
        v-if="currentIndex < questions.length - 1"
        class="bar-btn"
        theme="primary"
        shape="round"
        :disabled="isLoading"
        @click="nextQuestion"
      >
        下一题
      </t-button>
      <t-button class="bar-btn" theme="primary" shape="round" :disabled="isLoading || !questions.length" @click="finishRedo">
        完成
      </t-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { examApi } from '@/features/exam/api'
import { wrongBookApi } from '@/features/wrongbook/api'
import { toQuestion } from '@/api/contracts'
import { useExamStore } from '@/stores/exam'
import type { ExamType, Question } from '@/types/exam'

const examStore = useExamStore()
const currentIndex = ref(0)
const answers = ref<Record<number, string>>({})
const showResult = ref<Record<number, boolean>>({})
const questions = ref<Question[]>([])
const paperId = ref<number | null>(null)
const isLoading = ref(false)
const isSubmitting = ref(false)
const questionStartedAt = ref(Date.now())
const elapsedSeconds = ref<Record<number, number>>({})

const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
const progressPercent = computed(() => {
  if (!questions.value.length) return 0
  const answered = Object.keys(answers.value).length
  return Math.round((answered / questions.value.length) * 100)
})

const commitElapsedTime = () => {
  const index = currentIndex.value
  const elapsed = Math.max(0, Math.floor((Date.now() - questionStartedAt.value) / 1000))
  elapsedSeconds.value[index] = (elapsedSeconds.value[index] || 0) + elapsed
  questionStartedAt.value = Date.now()
  return elapsedSeconds.value[index]
}

const loadRedoPaper = async (examType: ExamType) => {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const paper = await wrongBookApi.generateRedoPaper({ examType, limit: 20 })
    const mappedQuestions = paper.questions.map(toQuestion)
    paperId.value = paper.id
    questions.value = mappedQuestions
    currentIndex.value = 0
    answers.value = {}
    showResult.value = {}
    elapsedSeconds.value = {}
    examStore.setConfig({
      examType,
      questionCount: mappedQuestions.length,
      difficulty: 'all',
      strategy: 'knowledge',
      knowledgePoints: [],
      mode: 'practice',
      timeLimit: 0,
    })
    examStore.setPaper(paper.id, mappedQuestions)
    examStore.start()
    questionStartedAt.value = Date.now()
  } catch {
    questions.value = []
  } finally {
    isLoading.value = false
  }
}

const selectOption = async (key: string) => {
  if (!currentQuestion.value || !paperId.value || isSubmitting.value) return
  if (showResult.value[currentIndex.value]) return

  const index = currentIndex.value
  answers.value[index] = key
  examStore.setAnswer(index, key)
  isSubmitting.value = true

  try {
    await examApi.submitAnswer({
      paperId: paperId.value,
      questionId: currentQuestion.value.id,
      userAnswer: key,
      timeSpent: commitElapsedTime(),
    })
    showResult.value[index] = true
  } catch {
    delete answers.value[index]
    examStore.clearAnswer(index)
  } finally {
    isSubmitting.value = false
  }
}

const moveTo = (index: number) => {
  if (index < 0 || index >= questions.value.length || index === currentIndex.value) return
  commitElapsedTime()
  currentIndex.value = index
  examStore.setCurrentIndex(index)
}

const prevQuestion = () => moveTo(currentIndex.value - 1)
const nextQuestion = () => moveTo(currentIndex.value + 1)

const confirmExit = () => {
  uni.showModal({
    title: '确认退出',
    content: '退出后当前重做进度将不会继续提交，确定退出吗？',
    success: (res: any) => {
      if (res.confirm) uni.navigateBack()
    },
  })
}

const finishRedo = () => {
  if (!paperId.value) {
    uni.navigateBack()
    return
  }
  commitElapsedTime()
  examStore.finish()
  uni.redirectTo({ url: `/pages/exam/result?paperId=${paperId.value}` })
}

const chooseExamType = () => {
  uni.showActionSheet({
    itemList: ['CSCA 错题', 'HKS 错题'],
    success: ({ tapIndex }) => loadRedoPaper(tapIndex === 0 ? 'CSCA' : 'HKS'),
    fail: () => uni.navigateBack(),
  })
}

onLoad((query) => {
  if (query?.examType === 'CSCA' || query?.examType === 'HKS') {
    loadRedoPaper(query.examType)
    return
  }
  chooseExamType()
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--app-bg);
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  padding: 16rpx 20rpx;
  margin: 20rpx 24rpx 0;
}

.progress-info {
  flex: 1;
  text-align: center;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--app-text);
}

.question-index {
  font-variant-numeric: tabular-nums;
}

.progress-bar {
  height: 4rpx;
  margin: 14rpx 24rpx 0;
  background: #eadfce;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--app-danger), var(--app-accent));
}

.question-area {
  flex: 1;
  padding: 24rpx;
}

.question-card {
  min-height: 100%;
}

.empty-question {
  padding: 84rpx 20rpx;
  text-align: center;
  font-size: 28rpx;
  color: var(--app-text-weak);
}

.bottom-bar {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 20rpx calc(28rpx + env(safe-area-inset-bottom));
  margin: 0 24rpx 24rpx;
}

.bar-btn {
  flex: 1;
}
</style>

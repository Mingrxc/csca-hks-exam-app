<template>
  <view class="page">
    <view class="top-bar">
      <view class="back-btn" @click="confirmExit">
        <text>退出</text>
      </view>
      <view class="progress-info">
        <text class="question-index">{{ questions.length ? currentIndex + 1 : 0 }} / {{ questions.length }}</text>
      </view>
      <view class="mode-badge">错题重做</view>
    </view>

    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
    </view>

    <scroll-view class="question-area" scroll-y>
      <view class="question-card">
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

    <view class="bottom-bar">
      <button class="prev-btn" :disabled="currentIndex === 0 || isLoading" @click="prevQuestion">上一题</button>
      <button
        class="next-btn"
        v-if="currentIndex < questions.length - 1"
        :disabled="isLoading"
        @click="nextQuestion"
      >下一题</button>
      <button class="submit-btn" v-else :disabled="isLoading || !questions.length" @click="finishRedo">完成</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { examApi, wrongBookApi } from '@/api'
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
    success: (res: any) => { if (res.confirm) uni.navigateBack() },
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
.page { height: 100vh; display: flex; flex-direction: column; background: #F5F5F7; }

.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24rpx; height: 88rpx; background: #fff;
  border-bottom: 1rpx solid #E5E7EB;
}
.back-btn { color: #6B7280; font-size: 28rpx; }
.progress-info { font-weight: 600; font-size: 28rpx; color: #1F2937; }
.mode-badge { padding: 4rpx 16rpx; border-radius: 12rpx; font-size: 20rpx; background: #FEE2E2; color: #991B1B; }

.progress-bar { height: 4rpx; background: #E5E7EB; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #EF4444, #F59E0B); transition: width 0.3s; }

.question-area { flex: 1; padding: 24rpx; }
.question-card { background: #fff; border-radius: 16rpx; padding: 32rpx 24rpx; }
.empty-question { color: #6B7280; font-size: 28rpx; text-align: center; padding: 80rpx 20rpx; }

.bottom-bar {
  display: flex; align-items: center; gap: 16rpx;
  padding: 16rpx 24rpx 40rpx; background: #fff;
  border-top: 1rpx solid #E5E7EB;
}
.bottom-bar button { border-radius: 24rpx; font-size: 28rpx; padding: 12rpx 28rpx; border: none; }
.prev-btn { background: #F3F4F6; color: #374151; }
.prev-btn[disabled] { opacity: 0.4; }
.next-btn { background: #EEF2FF; color: #4F46E5; }
.submit-btn { background: linear-gradient(135deg, #10B981, #059669); color: #fff; font-weight: 600; }
.submit-btn[disabled] { opacity: 0.5; }
</style>

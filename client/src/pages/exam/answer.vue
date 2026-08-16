<template>
  <view class="page">
    <!-- 顶部状态栏 -->
    <view class="top-bar">
      <view class="back-btn" @click="confirmExit">
        <text>← 退出</text>
      </view>
      <view class="progress-info">
        <text class="question-index">{{ currentIndex + 1 }} / {{ questions.length }}</text>
      </view>
      <c-countdown-bar v-if="mode === 'exam'" :seconds="remainingSeconds" @timeout="submitExam(true)" />
      <view class="mode-badge" :class="mode">
        {{ mode === 'exam' ? '考试模式' : '练习模式' }}
      </view>
    </view>

    <!-- 进度条 -->
    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
    </view>

    <!-- 题目区 -->
    <scroll-view class="question-area" scroll-y :scroll-into-view="'q-' + currentIndex">
      <view class="question-card" :id="'q-' + currentIndex">
        <c-question-item
          v-if="currentQuestion"
          :question="currentQuestion"
          :index="currentIndex"
          :user-answer="answers[currentIndex] || ''"
          :show-result="!!showResult[currentIndex]"
          @select="selectOption"
        />
        <view v-else class="empty-question">试卷题目加载失败，请返回重新组卷。</view>
        <view class="wrong-reason" v-if="showResult[currentIndex] && !currentCorrect">
          <text class="reason-label">这道题为什么错了？</text>
          <view class="reason-tags">
            <view
              class="reason-tag"
              :class="{ selected: currentSelectedReason === r }"
              v-for="r in wrongReasons"
              :key="r"
              @click="selectWrongReason(r)"
            >{{ r }}</view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 答题卡弹出 -->
    <view class="answer-sheet-mask" v-if="showSheet" @click="showSheet = false">
      <view class="answer-sheet" @click.stop>
        <c-answer-card
          :items="answerSheetItems"
          :total="questions.length"
          :answered-count="answeredCount"
          :current="currentIndex"
          @jump="jumpToAndClose"
        />
        <button class="sheet-close" @click="showSheet = false">关闭</button>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <button class="sheet-btn" @click="showSheet = true">
        <text>📋 答题卡</text>
      </button>
      <button class="prev-btn" :disabled="currentIndex === 0" @click="prevQuestion">上一题</button>
      <button class="next-btn" v-if="currentIndex < questions.length - 1" @click="nextQuestion">下一题</button>
      <button class="submit-btn" v-else @click="submitExam">交卷</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { WRONG_REASONS } from '@/constants/exam'
import { examApi } from '@/api'
import { useExamStore } from '@/stores/exam'

const examStore = useExamStore()
const mode = computed(() => examStore.config.mode)
const currentIndex = computed(() => examStore.currentIndex)
const answers = computed(() => examStore.answers)
const showResult = ref<Record<number, boolean>>({})
const answerCorrectness = ref<Record<number, boolean>>({})
const selectedReasons = ref<Record<number, string>>({})
const showSheet = ref(false)
const isSubmitting = ref(false)
const questionStartedAt = ref(Date.now())
const questionElapsedSeconds = ref<Record<number, number>>({})
const questions = computed(() => examStore.questions)
const remainingSeconds = computed(() => examStore.config.timeLimit * 60)

const currentQuestion = computed(() => examStore.currentQuestion)
const progressPercent = computed(() => examStore.progressPercent)
const answeredCount = computed(() => examStore.answeredCount)
const currentCorrect = computed(() => answerCorrectness.value[currentIndex.value] === true)
const currentSelectedReason = computed(() => selectedReasons.value[currentIndex.value] || '')

const wrongReasons = WRONG_REASONS

const commitElapsedTime = () => {
  const index = currentIndex.value
  const elapsed = Math.max(0, Math.floor((Date.now() - questionStartedAt.value) / 1000))
  questionElapsedSeconds.value[index] = (questionElapsedSeconds.value[index] || 0) + elapsed
  questionStartedAt.value = Date.now()
  return questionElapsedSeconds.value[index]
}

const selectOption = async (key: string) => {
  if (!currentQuestion.value || !examStore.paperId || isSubmitting.value) return
  if (showResult.value[currentIndex.value] && mode.value === 'practice') return

  isSubmitting.value = true
  const index = currentIndex.value
  const previousAnswer = answers.value[index]
  examStore.setAnswer(index, key)

  try {
    const response = await examApi.submitAnswer({
      paperId: examStore.paperId,
      questionId: currentQuestion.value.id,
      userAnswer: key,
      timeSpent: commitElapsedTime(),
      wrongReason: currentSelectedReason.value || undefined,
    })
    if (typeof response.is_correct === 'boolean') {
      answerCorrectness.value[index] = response.is_correct
    }
    if (mode.value === 'practice') {
      showResult.value[index] = true
    }
  } catch {
    // The shared request layer already displays the error message.
    if (previousAnswer == null) {
      examStore.clearAnswer(index)
    } else {
      examStore.setAnswer(index, previousAnswer)
    }
  } finally {
    isSubmitting.value = false
  }
}

const selectWrongReason = async (reason: string) => {
  const index = currentIndex.value
  const previousReason = selectedReasons.value[index]
  selectedReasons.value[index] = reason
  const answer = answers.value[index]
  if (!answer || !currentQuestion.value || !examStore.paperId || isSubmitting.value) return

  isSubmitting.value = true
  try {
    const response = await examApi.submitAnswer({
      paperId: examStore.paperId,
      questionId: currentQuestion.value.id,
      userAnswer: answer,
      timeSpent: commitElapsedTime(),
      wrongReason: reason,
    })
    if (typeof response.is_correct === 'boolean') {
      answerCorrectness.value[index] = response.is_correct
    }
  } catch {
    // The shared request layer already displays the error message.
    if (previousReason == null) {
      delete selectedReasons.value[index]
    } else {
      selectedReasons.value[index] = previousReason
    }
  } finally {
    isSubmitting.value = false
  }
}

const moveTo = (index: number) => {
  if (index === currentIndex.value) return
  commitElapsedTime()
  examStore.setCurrentIndex(index)
}
const prevQuestion = () => moveTo(currentIndex.value - 1)
const nextQuestion = () => moveTo(currentIndex.value + 1)
const jumpTo = (i: number) => moveTo(i)
const jumpToAndClose = (i: number) => {
  jumpTo(i)
  showSheet.value = false
}

const answerSheetItems = computed(() =>
  questions.value.map((_, index) => ({
    index,
    answered: answers.value[index] != null,
    marked: !!showResult.value[index],
  })),
)

const confirmExit = () => {
  uni.showModal({
    title: '确认退出',
    content: '退出后答题进度将不会保存，确定退出吗？',
    success: (res: any) => { if (res.confirm) uni.navigateBack() }
  })
}

const completeExam = () => {
  if (!examStore.paperId) {
    uni.showToast({ title: '试卷信息已失效，请重新组卷', icon: 'none' })
    uni.navigateBack()
    return
  }
  commitElapsedTime()
  examStore.finish()
  uni.redirectTo({ url: `/pages/exam/result?paperId=${examStore.paperId}` })
}

const submitExam = (forced = false) => {
  if (forced) {
    completeExam()
    return
  }

  const answered = Object.keys(answers.value).length
  uni.showModal({
    title: '确认交卷',
    content: `还有 ${questions.value.length - answered} 题未作答，确定交卷吗？`,
    success: (res: any) => {
      if (res.confirm) {
        completeExam()
      }
    }
  })
}

if (!examStore.paperId || questions.value.length === 0) {
  uni.showToast({ title: '请先完成组卷', icon: 'none' })
  setTimeout(() => uni.navigateBack(), 300)
}
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
.timer { font-size: 28rpx; color: #4F46E5; font-weight: 600; font-family: 'Menlo', monospace; }
.timer .time-warning { color: #EF4444; }
.mode-badge { padding: 4rpx 16rpx; border-radius: 12rpx; font-size: 20rpx; }
.mode-badge.exam { background: #FEE2E2; color: #991B1B; }
.mode-badge.practice { background: #D1FAE5; color: #065F46; }

.progress-bar { height: 4rpx; background: #E5E7EB; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #4F46E5, #7C3AED); transition: width 0.3s; }

.question-area { flex: 1; padding: 24rpx; }
.question-card { background: #fff; border-radius: 16rpx; padding: 32rpx 24rpx; }
.empty-question { color: #6B7280; font-size: 28rpx; text-align: center; padding: 80rpx 20rpx; }

.q-header { display: flex; gap: 12rpx; margin-bottom: 20rpx; }
.type-tag, .difficulty-tag { padding: 4rpx 16rpx; border-radius: 8rpx; font-size: 20rpx; }
.type-tag.single { background: #DBEAFE; color: #1E40AF; }
.type-tag.multi { background: #FEF3C7; color: #92400E; }
.type-tag.judge { background: #D1FAE5; color: #065F46; }
.type-tag.fill { background: #EDE9FE; color: #5B21B6; }
.difficulty-tag.easy { background: #D1FAE5; color: #065F46; }
.difficulty-tag.medium { background: #FEF3C7; color: #92400E; }
.difficulty-tag.hard { background: #FEE2E2; color: #991B1B; }

.q-stem { font-size: 30rpx; line-height: 1.8; color: #1F2937; margin-bottom: 32rpx; }

.q-options { display: flex; flex-direction: column; gap: 16rpx; }
.option-item {
  display: flex; align-items: center;
  padding: 24rpx 20rpx; border-radius: 12rpx;
  border: 2rpx solid #E5E7EB; background: #fff;
}
.option-item.selected { border-color: #4F46E5; background: #EEF2FF; }
.option-item.correct { border-color: #10B981; background: #D1FAE5; }
.option-item.wrong { border-color: #EF4444; background: #FEE2E2; }
.option-key {
  width: 48rpx; height: 48rpx; border-radius: 50%;
  background: #F3F4F6; display: flex; align-items: center;
  justify-content: center; font-size: 24rpx; font-weight: 600; color: #6B7280;
}
.option-item.selected .option-key { background: #4F46E5; color: #fff; }
.option-item.correct .option-key { background: #10B981; color: #fff; }
.option-item.wrong .option-key { background: #EF4444; color: #fff; }
.option-text { flex: 1; margin-left: 16rpx; font-size: 28rpx; color: #1F2937; }
.option-icon { font-size: 28rpx; font-weight: 700; }
.option-item.correct .option-icon { color: #10B981; }
.option-item.wrong .option-icon { color: #EF4444; }

.analysis { margin-top: 24rpx; padding: 20rpx; background: #F0FDF4; border-radius: 12rpx; }
.analysis-header { display: flex; align-items: center; gap: 8rpx; margin-bottom: 8rpx; }
.analysis-icon { font-size: 28rpx; }
.analysis-title { font-size: 26rpx; font-weight: 600; color: #065F46; }
.analysis-text { font-size: 24rpx; color: #374151; line-height: 1.7; }

.wrong-reason { margin-top: 24rpx; }
.reason-label { font-size: 24rpx; color: #6B7280; display: block; margin-bottom: 12rpx; }
.reason-tags { display: flex; flex-wrap: wrap; gap: 12rpx; }
.reason-tag {
  padding: 8rpx 20rpx; border-radius: 16rpx; font-size: 22rpx;
  background: #F3F4F6; color: #6B7280;
}
.reason-tag.selected { background: #FEF3C7; color: #92400E; border: 1rpx solid #FCD34D; }

/* 答题卡弹窗 */
.answer-sheet-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: flex-end; justify-content: center; z-index: 100;
}
.answer-sheet {
  background: #fff; border-radius: 32rpx 32rpx 0 0;
  width: 100%; padding: 40rpx 32rpx 60rpx;
}
.sheet-title { font-size: 32rpx; font-weight: 700; text-align: center; display: block; margin-bottom: 24rpx; }
.sheet-grid { display: flex; flex-wrap: wrap; gap: 16rpx; justify-content: center; }
.sheet-item {
  width: 72rpx; height: 72rpx; border-radius: 50%;
  background: #F3F4F6; display: flex; align-items: center;
  justify-content: center; font-size: 26rpx; color: #6B7280;
}
.sheet-item.answered { background: #EEF2FF; color: #4F46E5; }
.sheet-item.current { background: #4F46E5; color: #fff; }
.sheet-legend { display: flex; justify-content: center; gap: 32rpx; margin: 24rpx 0; }
.legend-item { display: flex; align-items: center; gap: 8rpx; font-size: 22rpx; color: #9CA3AF; }
.dot { width: 20rpx; height: 20rpx; border-radius: 50%; background: #F3F4F6; }
.dot.answered { background: #EEF2FF; }
.dot.current { background: #4F46E5; }
.sheet-close {
  background: #F3F4F6; border-radius: 24rpx; font-size: 28rpx;
  color: #374151; text-align: center; padding: 16rpx 0; border: none;
}

/* 底部操作栏 */
.bottom-bar {
  display: flex; align-items: center; gap: 16rpx;
  padding: 16rpx 24rpx 40rpx; background: #fff;
  border-top: 1rpx solid #E5E7EB;
}
.bottom-bar button {
  border-radius: 24rpx; font-size: 28rpx; padding: 12rpx 28rpx; border: none;
}
.sheet-btn { background: #F3F4F6; color: #374151; }
.prev-btn { background: #F3F4F6; color: #374151; }
.prev-btn[disabled] { opacity: 0.4; }
.next-btn { background: #EEF2FF; color: #4F46E5; }
.submit-btn { background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #fff; font-weight: 600; }
</style>

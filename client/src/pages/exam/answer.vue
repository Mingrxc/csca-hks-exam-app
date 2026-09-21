<template>
  <view class="page app-page">
    <view class="top-bar app-card">
      <t-button class="top-action" theme="default" variant="text" size="small" shape="round" @click="confirmExit">
        退出
      </t-button>
      <view class="progress-info">
        <text class="question-index">{{ currentIndex + 1 }} / {{ questions.length }}</text>
      </view>
      <c-countdown-bar v-if="mode === 'exam'" :seconds="remainingSeconds" @timeout="submitExam(true)" />
      <t-tag class="mode-badge" :theme="mode === 'exam' ? 'danger' : 'success'" variant="light" shape="round">
        {{ mode === 'exam' ? '考试模式' : '练习模式' }}
      </t-tag>
    </view>

    <view class="progress-bar">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
    </view>

    <scroll-view class="question-area" scroll-y :scroll-into-view="'q-' + currentIndex">
      <view class="question-card app-card app-card-pad" :id="'q-' + currentIndex">
        <c-question-item
          v-if="currentQuestion"
          :question="currentQuestion"
          :index="currentIndex"
          :user-answer="answers[currentIndex] || ''"
          :show-result="!!showResult[currentIndex]"
          :is-favorite="currentQuestion?.isFavorite"
          @select="selectOption"
          @favorite="toggleFavorite"
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
            >
              {{ r }}
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="answer-sheet-mask" v-if="showSheet" @click="showSheet = false">
      <view class="answer-sheet" @click.stop>
        <c-answer-card
          :items="answerSheetItems"
          :total="questions.length"
          :answered-count="answeredCount"
          :current="currentIndex"
          @jump="jumpToAndClose"
        />
        <t-button class="sheet-close" block theme="default" variant="outline" shape="round" @click="showSheet = false">
          关闭
        </t-button>
      </view>
    </view>

    <view class="bottom-bar app-card">
      <t-button class="bar-btn" theme="default" variant="outline" shape="round" @click="showSheet = true">
        答题卡
      </t-button>
      <t-button class="bar-btn" theme="default" variant="outline" shape="round" :disabled="currentIndex === 0" @click="prevQuestion">
        上一题
      </t-button>
      <t-button
        v-if="currentIndex < questions.length - 1"
        class="bar-btn"
        theme="primary"
        shape="round"
        @click="nextQuestion"
      >
        下一题
      </t-button>
      <t-button v-else class="bar-btn" theme="primary" shape="round" @click="submitExam()">交卷</t-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { confirmAction } from '@/shared/ui/confirm'
import { useAnswerSession } from '@/features/exam/useAnswerSession'

const {
  examStore, mode, currentIndex, answers, showResult, questions, remainingSeconds,
  currentQuestion, progressPercent, answeredCount, currentCorrect, currentSelectedReason,
  answerSheetItems, wrongReasons, toggleFavorite, selectOption, selectWrongReason,
  commitElapsedTime, moveTo,
} = useAnswerSession()
const showSheet = ref(false)

const prevQuestion = () => moveTo(currentIndex.value - 1)
const nextQuestion = () => moveTo(currentIndex.value + 1)
const jumpTo = (i: number) => moveTo(i)
const jumpToAndClose = (i: number) => {
  jumpTo(i)
  showSheet.value = false
}

const confirmExit = async () => {
  examStore.persistProgress()
  const confirmed = await confirmAction({
    title: '暂时退出',
    content: '当前答题进度已保存在本机，下次进入答题页可继续。',
    confirmText: '退出',
  })
  if (confirmed) uni.navigateBack()
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

const submitExam = async (forced = false) => {
  if (forced) {
    completeExam()
    return
  }

  const answered = Object.keys(answers.value).length
  const unanswered = questions.value.length - answered
  const confirmed = await confirmAction({
    title: '确认交卷',
    content: unanswered > 0 ? `还有 ${unanswered} 题未作答，确定交卷吗？` : '已完成全部题目，确定交卷吗？',
  })
  if (confirmed) completeExam()
}

if (!examStore.paperId || questions.value.length === 0) {
  uni.showToast({ title: '请先完成组卷', icon: 'none' })
  setTimeout(() => uni.navigateBack(), 300)
}

onMounted(() => {
  if (examStore.restoredFromStorage) {
    uni.showToast({ title: '已恢复上次答题进度', icon: 'none' })
    examStore.acknowledgeRestore()
  }
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

.top-action {
  flex: none;
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

.mode-badge {
  flex: none;
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
  background: linear-gradient(90deg, var(--app-primary), var(--app-secondary));
  transition: width 0.25s ease;
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

.wrong-reason {
  margin-top: 24rpx;
}

.reason-label {
  display: block;
  margin-bottom: 12rpx;
  font-size: 24rpx;
  color: var(--app-text-weak);
}

.reason-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.reason-tag {
  padding: 8rpx 18rpx;
  border-radius: 999px;
  background: #f8fafc;
  border: 1rpx solid var(--app-border);
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.reason-tag.selected {
  background: var(--app-accent-soft);
  border-color: rgba(217, 119, 6, 0.18);
  color: var(--app-accent);
}

.answer-sheet-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.48);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 100;
}

.answer-sheet {
  width: 100%;
  padding: 28rpx 24rpx 40rpx;
  background: #fffaf3;
  border-radius: 32rpx 32rpx 0 0;
}

.sheet-close {
  margin-top: 18rpx;
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

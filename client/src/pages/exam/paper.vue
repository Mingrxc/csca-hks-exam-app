<template>
  <view class="page">
    <!-- 策略标题 -->
    <view class="strategy-header">
      <text class="strategy-icon">{{ currentStrategy.icon }}</text>
      <text class="strategy-name">{{ currentStrategy.title }}</text>
      <text class="strategy-desc">{{ currentStrategy.desc }}</text>
    </view>

    <!-- 组卷配置 -->
    <view class="config-section">
      <!-- 考试类型 -->
      <view class="config-row">
        <text class="config-label">考试类型</text>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.examType === 'CSCA' }"
            @click="form.examType = 'CSCA'"
          >CSCA</view>
          <view
            class="option-tag"
            :class="{ active: form.examType === 'HKS' }"
            @click="form.examType = 'HKS'"
          >HKS</view>
        </view>
      </view>

      <!-- 题目数量 -->
      <view class="config-row">
        <text class="config-label">题目数量</text>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.questionCount === n }"
            v-for="n in questionCountOptions"
            :key="n"
            @click="form.questionCount = n"
          >{{ n }}题</view>
        </view>
      </view>

      <!-- 难度选择 -->
      <view class="config-row">
        <text class="config-label">难度</text>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.difficulty === d.value }"
            v-for="d in difficulties"
            :key="d.value"
            @click="form.difficulty = d.value"
          >{{ d.label }}</view>
        </view>
      </view>

      <!-- 知识点选择（仅专项模式） -->
      <view class="config-row" v-if="strategyType === 'knowledge'">
        <text class="config-label">知识点</text>
        <view class="knowledge-tags">
          <view
            class="knowledge-tag"
            :class="{ selected: form.knowledgePoints.includes(k) }"
            v-for="k in knowledgePoints"
            :key="k"
            @click="toggleKnowledge(k)"
          >{{ k }}</view>
        </view>
      </view>

      <!-- 模式选择 -->
      <view class="config-row">
        <text class="config-label">答题模式</text>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.mode === 'exam' }"
            @click="form.mode = 'exam'"
          >考试模式</view>
          <view
            class="option-tag"
            :class="{ active: form.mode === 'practice' }"
            @click="form.mode = 'practice'"
          >练习模式</view>
        </view>
      </view>

      <!-- 限时（考试模式） -->
      <view class="config-row" v-if="form.mode === 'exam'">
        <text class="config-label">限时（分钟）</text>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.timeLimit === t }"
            v-for="t in timeLimitOptions"
            :key="t"
            @click="form.timeLimit = t"
          >{{ t }}分钟</view>
        </view>
      </view>
    </view>

    <!-- 开始按钮 -->
    <view class="footer">
      <view class="summary">
        <text>{{ form.questionCount }}题 · {{ form.mode === 'exam' ? '考试模式' : '练习模式' }}</text>
        <text v-if="form.mode === 'exam'"> · {{ form.timeLimit }}分钟</text>
      </view>
      <button class="start-btn" @click="startExam">开始刷题</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { questionApi } from '@/api'
import { toQuestion } from '@/api/contracts'
import {
  DIFFICULTY_OPTIONS,
  KNOWLEDGE_POINTS,
  PAPER_STRATEGY_MAP,
  QUESTION_COUNT_OPTIONS,
  TIME_LIMIT_OPTIONS,
} from '@/constants/exam'
import type { DifficultyFilter, ExamMode, ExamType, PaperStrategy } from '@/types/exam'
import { useExamStore } from '@/stores/exam'

const examStore = useExamStore()
const strategyType = ref('random')
const isGenerating = ref(false)

const currentStrategy = computed(() => PAPER_STRATEGY_MAP[strategyType.value as keyof typeof PAPER_STRATEGY_MAP] || PAPER_STRATEGY_MAP.random)
const difficulties = DIFFICULTY_OPTIONS
const knowledgePoints = KNOWLEDGE_POINTS
const questionCountOptions = QUESTION_COUNT_OPTIONS
const timeLimitOptions = TIME_LIMIT_OPTIONS

const form = reactive({
  examType: 'CSCA' as ExamType,
  questionCount: 20,
  difficulty: 'all' as DifficultyFilter,
  knowledgePoints: [] as string[],
  mode: 'practice' as ExamMode,
  timeLimit: 60,
})

const toggleKnowledge = (k: string) => {
  const idx = form.knowledgePoints.indexOf(k)
  if (idx >= 0) {
    form.knowledgePoints.splice(idx, 1)
  } else {
    form.knowledgePoints.push(k)
  }
}

onLoad((query) => {
  const strategy = query?.strategy
  if (typeof strategy === 'string' && strategy in PAPER_STRATEGY_MAP) {
    strategyType.value = strategy
  }
  const knowledge = query?.knowledge
  if (typeof knowledge === 'string' && KNOWLEDGE_POINTS.includes(knowledge)) {
    form.knowledgePoints = [knowledge]
  }
})

const startExam = async () => {
  if (strategyType.value === 'knowledge' && form.knowledgePoints.length === 0) {
    uni.showToast({ title: '请至少选择一个知识点', icon: 'none' })
    return
  }
  if (isGenerating.value) return

  isGenerating.value = true
  try {
    const paper = await questionApi.generatePaper({
      examType: form.examType,
      questionCount: form.questionCount,
      difficulty: form.difficulty,
      strategy: strategyType.value,
      knowledgePoints: form.knowledgePoints,
      mode: form.mode,
      timeLimit: form.mode === 'exam' ? form.timeLimit : 0,
    })
    examStore.setConfig({
      ...form,
      strategy: strategyType.value as PaperStrategy,
      timeLimit: paper.time_limit,
    })
    examStore.setPaper(paper.id, paper.questions.map(toQuestion))
    examStore.start()
    uni.navigateTo({ url: '/pages/exam/answer' })
  } catch {
    // The shared request layer already displays the error message.
  } finally {
    isGenerating.value = false
  }
}
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; padding-bottom: 160rpx; }

.strategy-header {
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  padding: 40rpx 32rpx;
  text-align: center;
}
.strategy-icon { font-size: 56rpx; display: block; }
.strategy-name { font-size: 36rpx; font-weight: 700; color: #fff; display: block; margin-top: 12rpx; }
.strategy-desc { font-size: 24rpx; color: rgba(255,255,255,0.7); display: block; margin-top: 8rpx; }

.config-section { padding: 24rpx; }
.config-row {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
.config-label { font-size: 28rpx; font-weight: 600; color: #1F2937; margin-bottom: 16rpx; display: block; }
.config-options { display: flex; flex-wrap: wrap; gap: 12rpx; }
.option-tag {
  padding: 10rpx 28rpx; border-radius: 20rpx; font-size: 24rpx;
  background: #F3F4F6; color: #6B7280;
}
.option-tag.active { background: #EEF2FF; color: #4F46E5; font-weight: 600; }

.knowledge-tags { display: flex; flex-wrap: wrap; gap: 12rpx; }
.knowledge-tag {
  padding: 10rpx 28rpx; border-radius: 20rpx; font-size: 24rpx;
  background: #F3F4F6; color: #6B7280;
}
.knowledge-tag.selected { background: #EEF2FF; color: #4F46E5; font-weight: 600; }

.footer {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #fff; padding: 20rpx 32rpx 40rpx;
  box-shadow: 0 -2rpx 12rpx rgba(0,0,0,0.06);
}
.summary { text-align: center; font-size: 24rpx; color: #9CA3AF; margin-bottom: 16rpx; }
.start-btn {
  background: linear-gradient(135deg, #4F46E5, #7C3AED);
  color: #fff; border-radius: 48rpx; font-size: 32rpx;
  font-weight: 600; padding: 20rpx 0; border: none; text-align: center;
}
</style>

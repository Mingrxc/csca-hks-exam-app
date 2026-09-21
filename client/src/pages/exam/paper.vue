<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-card app-visual-card app-card-pad">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">组卷中心</text>
            <text class="hero-title">{{ currentStrategy.title }}</text>
            <text class="hero-subtitle">{{ currentStrategy.desc }}</text>
          </view>
          <view class="hero-visual">
            <view class="visual-main">
              <text class="visual-value">{{ form.examType }}</text>
              <text class="visual-label">考试类型</text>
            </view>
            <view class="visual-stack">
              <view class="visual-mini">
                <text class="visual-mini-value">{{ form.questionCount ?? '未选' }}</text>
                <text class="visual-mini-label">题数</text>
              </view>
              <view class="visual-mini">
                <text class="visual-mini-value">
                  {{ form.mode === 'exam' ? (form.timeLimit ?? '未选') : form.mode === 'practice' ? '练习' : '未选' }}
                </text>
                <text class="visual-mini-label">
                  {{ form.mode === 'exam' ? '限时分钟' : form.mode === 'practice' ? '练习模式' : '答题模式' }}
                </text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="app-section config-list">
      <view class="config-card app-card">
        <view class="config-head">
          <text class="config-label">考试类型</text>
        </view>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.examType === 'CSCA' }"
            @click="setExamType('CSCA')"
          >
            CSCA
          </view>
          <view
            class="option-tag"
            :class="{ active: form.examType === 'HKS' }"
            @click="setExamType('HKS')"
          >
            HKS
          </view>
        </view>
      </view>

      <view class="config-card app-card" v-if="!isRealStrategy">
        <view class="config-head">
          <text class="config-label">题目数量</text>
        </view>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.questionCount === item }"
            v-for="item in questionCountOptions"
            :key="item"
            @click="form.questionCount = item"
          >
            {{ item }} 题
          </view>
        </view>
      </view>

      <view class="config-card app-card" v-if="showsDifficulty">
        <view class="config-head">
          <text class="config-label">难度</text>
        </view>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.difficulty === item.value }"
            v-for="item in difficulties"
            :key="item.value"
            @click="form.difficulty = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <view class="config-card app-card" v-if="needsSpecialSelection">
        <view class="config-head">
          <text class="config-label">{{ specialLabel }}</text>
        </view>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: selectedSpecials.includes(item) }"
            v-for="item in specialOptions"
            :key="item"
            @click="toggleSpecial(item)"
          >
            {{ item }}
          </view>
        </view>
      </view>

      <view class="config-card app-card" v-if="showsMode">
        <view class="config-head">
          <text class="config-label">答题模式</text>
        </view>
        <view class="config-options">
          <view class="option-tag" :class="{ active: form.mode === 'exam' }" @click="form.mode = 'exam'">
            考试模式
          </view>
          <view class="option-tag" :class="{ active: form.mode === 'practice' }" @click="form.mode = 'practice'">
            练习模式
          </view>
        </view>
      </view>

      <view class="config-card app-card" v-if="isRealStrategy || form.mode === 'exam'">
        <view class="config-head">
          <text class="config-label">限时（分钟）</text>
        </view>
        <view class="config-options">
          <view
            class="option-tag"
            :class="{ active: form.timeLimit === item }"
            v-for="item in timeLimitOptions"
            :key="item"
            @click="form.timeLimit = item"
          >
            {{ item }} 分钟
          </view>
        </view>
      </view>
    </view>

    <view class="footer">
      <view class="summary">
        <text>{{ form.examType }} · {{ summaryText }}</text>
      </view>
      <t-button theme="primary" block size="large" shape="round" :loading="isGenerating" @click="startExam">
        开始刷题
      </t-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { questionApi } from '@/features/exam/api'
import { toQuestion } from '@/api/contracts'
import {
  CSCA_SUBJECT_OPTIONS,
  DIFFICULTY_OPTIONS,
  HSK_CATEGORY_OPTIONS,
  PAPER_STRATEGY_MAP,
  REAL_EXAM_DEFAULT_QUESTION_COUNTS,
  QUESTION_COUNT_OPTIONS,
  REAL_EXAM_QUESTION_COUNTS,
  TIME_LIMIT_OPTIONS,
} from '@/constants/exam'
import type { DifficultyFilter, ExamMode, ExamType, PaperStrategy } from '@/types/exam'
import { useExamStore } from '@/stores/exam'
import { confirmAction } from '@/shared/ui/confirm'

const examStore = useExamStore()
const strategyType = ref<PaperStrategy>('random')
const isGenerating = ref(false)
const initialSpecial = ref('')
const specialOptionsByExam = reactive<Record<ExamType, string[]>>({
  CSCA: [...CSCA_SUBJECT_OPTIONS],
  HKS: [...HSK_CATEGORY_OPTIONS],
})

const currentStrategy = computed(
  () => PAPER_STRATEGY_MAP[strategyType.value] || PAPER_STRATEGY_MAP.random,
)
const difficulties = DIFFICULTY_OPTIONS
const questionCountOptions = QUESTION_COUNT_OPTIONS
const timeLimitOptions = TIME_LIMIT_OPTIONS

const form = reactive({
  examType: 'CSCA' as ExamType,
  questionCount: 20 as number | null,
  difficulty: 'all' as DifficultyFilter | null,
  specialValues: [] as string[],
  mode: 'practice' as ExamMode | null,
  timeLimit: 60 as number | null,
})

const isProgressiveStrategy = computed(() => strategyType.value === 'progressive')
const isRealStrategy = computed(() => strategyType.value === 'real')
const needsSpecialSelection = computed(() =>
  strategyType.value === 'knowledge' ||
  isProgressiveStrategy.value ||
  (isRealStrategy.value && form.examType === 'CSCA'),
)
const showsDifficulty = computed(() => strategyType.value === 'random' || strategyType.value === 'knowledge')
const showsMode = computed(() => !isRealStrategy.value)
const singleSpecialSelection = computed(
  () => form.examType === 'CSCA' || isProgressiveStrategy.value || isRealStrategy.value,
)

const specialLabel = computed(() => {
  if (isProgressiveStrategy.value || isRealStrategy.value) return '考试科目'
  return form.examType === 'CSCA' ? '科目' : '分类'
})
const specialOptions = computed(() => specialOptionsByExam[form.examType] || [])
const selectedSpecials = computed(() => form.specialValues)
const summaryText = computed(() => {
  const special = needsSpecialSelection.value
    ? selectedSpecials.value.length
      ? `${selectedSpecials.value.join(' / ')}`
      : '科目未选择'
    : isRealStrategy.value && form.examType === 'HKS'
      ? '全科覆盖'
    : '分类不限'
  const questionText = form.questionCount === null ? '题数未选择' : `${form.questionCount}题`
  const modeText =
    isRealStrategy.value
      ? '模拟考试'
      : form.mode === 'exam'
      ? form.timeLimit === null
        ? '考试未设置限时'
        : `考试 ${form.timeLimit} 分钟`
      : form.mode === 'practice'
        ? '练习模式'
        : '答题模式未选择'
  const difficultyText =
    !showsDifficulty.value
      ? isProgressiveStrategy.value
        ? '自动递进'
        : '按真实考试'
      : form.difficulty === null
      ? '难度未选择'
      : form.difficulty === 'all'
      ? '全部难度'
      : (difficulties.find((item) => item.value === form.difficulty)?.label || form.difficulty)
  return `${questionText} · ${difficultyText} · ${special} · ${modeText}`
})

const updateRealQuestionCount = (specialValue?: string) => {
  if (!isRealStrategy.value) return
  form.questionCount = specialValue
    ? REAL_EXAM_QUESTION_COUNTS[form.examType][specialValue] || null
    : null
}

const toggleSpecial = (value: string) => {
  if (singleSpecialSelection.value) {
    form.specialValues = selectedSpecials.value[0] === value ? [] : [value]
    updateRealQuestionCount(form.specialValues[0])
    return
  }

  const index = form.specialValues.indexOf(value)
  if (index >= 0) {
    form.specialValues.splice(index, 1)
  } else {
    form.specialValues.push(value)
  }
}

const resetFormSelections = () => {
  form.questionCount = null
  form.difficulty = null
  form.specialValues = []
  form.mode = null
  form.timeLimit = null
}

const applyRealExamPreset = () => {
  form.questionCount =
    form.examType === 'HKS' ? REAL_EXAM_DEFAULT_QUESTION_COUNTS.HKS : null
  form.difficulty = 'all'
  form.mode = 'exam'
  form.timeLimit = null
}

const setExamType = (value: ExamType) => {
  if (form.examType === value) return
  form.examType = value
  initialSpecial.value = ''
  resetFormSelections()
  if (isRealStrategy.value) applyRealExamPreset()
}

onLoad((query) => {
  const strategy = query?.strategy
  if (typeof strategy === 'string' && strategy in PAPER_STRATEGY_MAP) {
    strategyType.value = strategy as PaperStrategy
  }

  const examType = query?.examType
  if (examType === 'CSCA' || examType === 'HKS') {
    form.examType = examType
  }

  const special = query?.special || query?.knowledge || query?.subject
  initialSpecial.value = typeof special === 'string' ? special : ''
  if (isRealStrategy.value) applyRealExamPreset()
  const initialSelection = specialOptions.value.includes(initialSpecial.value)
    ? initialSpecial.value
    : form.examType === 'HKS'
      ? specialOptions.value.find((item) => initialSpecial.value.startsWith(item)) || ''
      : ''
  if (initialSelection && (!isRealStrategy.value || form.examType === 'CSCA')) {
    form.specialValues = [initialSelection]
    updateRealQuestionCount(initialSelection)
  }
})

const startExam = async () => {
  if (needsSpecialSelection.value && form.specialValues.length === 0) {
    uni.showToast({ title: `请选择${specialLabel.value}`, icon: 'none' })
    return
  }
  if (form.questionCount === null) {
    uni.showToast({ title: '请完成组卷选择', icon: 'none' })
    return
  }
  if (showsDifficulty.value && form.difficulty === null) {
    uni.showToast({ title: '请选择难度', icon: 'none' })
    return
  }
  if (showsMode.value && form.mode === null) {
    uni.showToast({ title: '请选择答题模式', icon: 'none' })
    return
  }
  if ((isRealStrategy.value || form.mode === 'exam') && form.timeLimit === null) {
    uni.showToast({ title: '请选择限时时间', icon: 'none' })
    return
  }
  if (isGenerating.value) return

  if (examStore.hasActiveProgress) {
    const confirmed = await confirmAction({
      title: '开始新试卷',
      content: '开始新试卷会覆盖本机保存的未完成答题进度。',
      confirmText: '继续组卷',
    })
    if (!confirmed) return
  }

  isGenerating.value = true
  try {
    const difficulty = showsDifficulty.value ? (form.difficulty as DifficultyFilter) : 'all'
    const mode = isRealStrategy.value ? 'exam' : (form.mode as ExamMode)
    const timeLimit = mode === 'exam' ? (form.timeLimit as number) : 0
    const paper = await questionApi.generatePaper({
      examType: form.examType,
      questionCount: form.questionCount,
      difficulty,
      strategy: strategyType.value,
      knowledgePoints: form.specialValues,
      mode,
      timeLimit,
    })
    examStore.setConfig({
      examType: form.examType,
      questionCount: form.questionCount,
      difficulty,
      strategy: strategyType.value,
      knowledgePoints: form.specialValues,
      mode,
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
.hero {
  border-radius: 30rpx;
  overflow: hidden;
}

.hero-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.hero-copy {
  flex: 1;
  min-width: 0;
}

.hero-brand {
  display: block;
  color: var(--app-primary);
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.hero-title {
  display: block;
  margin-top: 10rpx;
  font-size: 36rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.hero-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--app-text-weak);
}

.hero-visual {
  flex: none;
  width: 210rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.visual-main,
.visual-mini {
  border-radius: 22rpx;
  overflow: hidden;
  background: rgba(255, 251, 246, 0.9);
  border: 1rpx solid rgba(201, 151, 118, 0.14);
  box-shadow: var(--app-shadow-sm);
}

.visual-main {
  padding: 18rpx 16rpx;
  text-align: center;
}

.visual-value {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: var(--app-primary);
}

.visual-label {
  display: block;
  margin-top: 4rpx;
  font-size: 20rpx;
  color: var(--app-text-weak);
}

.visual-stack {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10rpx;
}

.visual-mini {
  padding: 12rpx 8rpx;
  text-align: center;
}

.visual-mini-value {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-text);
}

.visual-mini-label {
  display: block;
  margin-top: 4rpx;
  font-size: 18rpx;
  white-space: nowrap;
  color: var(--app-text-weak);
}

.hero-band {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 18rpx;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.config-card {
  padding: 22rpx;
}

.config-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 14rpx;
}

.config-label {
  display: block;
  font-size: 28rpx;
  line-height: 1.4;
  font-weight: 600;
  color: var(--app-text);
}

.config-note {
  flex: none;
  font-size: 20rpx;
  color: var(--app-text-mute);
}

.config-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.option-tag {
  padding: 10rpx 22rpx;
  border-radius: 999px;
  background: #fffdf9;
  color: var(--app-text);
  font-size: 23rpx;
  line-height: 1.35;
  border: 1rpx solid var(--app-border);
}

.option-tag.active {
  background: var(--app-primary);
  color: var(--app-text);
  border-color: var(--app-primary);
  box-shadow: 0 6rpx 14rpx rgba(199, 127, 94, 0.2);
  font-weight: 600;
}

.footer {
  position: sticky;
  bottom: 0;
  z-index: 5;
  margin-top: 28rpx;
  padding: 18rpx 24rpx 34rpx;
  background: linear-gradient(180deg, rgba(247, 241, 232, 0) 0%, rgba(247, 241, 232, 0.92) 16%, #f7f1e8 100%);
}

.summary {
  margin-bottom: 14rpx;
  text-align: center;
  font-size: 22rpx;
  line-height: 1.5;
  color: var(--app-text-weak);
}
</style>

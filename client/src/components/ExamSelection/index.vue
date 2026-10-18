<template>
  <view class="exam-selection" :class="{ 'exam-selection--compact': compact }">
    <view class="exam-selection-options">
      <button
        v-for="exam in examOptions"
        :key="exam"
        class="app-pill exam-selection-option"
        :class="{ 'app-pill--active': selectedExams.includes(exam) }"
        role="button"
        :aria-label="'备考 ' + getExamLabel(exam)"
        :aria-pressed="selectedExams.includes(exam)"
        @click="emit('toggle', exam)"
      >
        <t-icon v-if="selectedExams.includes(exam)" name="check" size="22rpx" />
        <text>{{ getExamLabel(exam) }}</text>
      </button>
    </view>
    <text class="exam-selection-hint">{{ selectedExams.length ? '可多选 · 再点取消' : '随便看看 · 可多选' }}</text>
  </view>
</template>

<script setup lang="ts">
import { getExamLabel } from '@/constants/exam'
import type { ExamType } from '@/types/exam'

withDefaults(defineProps<{ selectedExams: ExamType[]; compact?: boolean }>(), { compact: false })
const emit = defineEmits<{ (event: 'toggle', exam: ExamType): void }>()
const examOptions: ExamType[] = ['HKS', 'CSCA']
</script>

<style lang="scss" scoped>
.exam-selection-options { display: flex; gap: 12rpx; }
.exam-selection-option { display: flex; align-items: center; justify-content: center; gap: 8rpx; margin: 0; min-width: 144rpx; }
.exam-selection-hint { display: block; margin-top: 10rpx; color: var(--app-text-mute); font-size: 22rpx; line-height: 1.4; }
.exam-selection--compact .exam-selection-options { gap: 8rpx; }
.exam-selection--compact .exam-selection-option { padding: 8rpx 18rpx; min-width: 122rpx; min-height: 56rpx; font-size: 22rpx; }
.exam-selection--compact .exam-selection-hint { margin-top: 6rpx; font-size: 19rpx; text-align: right; }
.exam-selection-option::after { border: 0; }
</style>

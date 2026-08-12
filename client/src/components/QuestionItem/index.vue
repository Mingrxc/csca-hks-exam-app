<template>
  <view class="question-item">
    <!-- 题目标题区 -->
    <view class="q-header">
      <text class="q-index">第 {{ index + 1 }} 题</text>
      <view class="q-tags">
        <text class="q-tag type" :class="question.type">{{ typeLabel }}</text>
        <text class="q-tag diff" :class="question.difficulty">{{ diffLabel }}</text>
      </view>
    </view>

    <!-- 题干 -->
    <view class="q-stem">
      <rich-text :nodes="question.stem"></rich-text>
    </view>

    <!-- 选项列表 -->
    <view class="q-options">
      <view
        class="option-item"
        :class="getOptionClass(opt.key)"
        v-for="opt in question.options"
        :key="opt.key"
        @click="$emit('select', opt.key)"
      >
        <view class="option-key">{{ opt.key }}</view>
        <text class="option-text">{{ opt.text }}</text>
        <text class="option-icon" v-if="showResult && opt.key === question.answer">✓</text>
        <text class="option-icon wrong" v-else-if="showResult && userAnswer === opt.key">✗</text>
      </view>
    </view>

    <!-- 解析区 -->
    <view class="analysis" v-if="showResult && question.analysis">
      <text class="analysis-label">💡 解析</text>
      <text class="analysis-text">{{ question.analysis }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Question } from '@/types/exam'
import { QUESTION_TYPE_MAP, DIFFICULTY_MAP } from '@/utils'

const props = defineProps<{
  question: Question
  index: number
  userAnswer: string
  showResult: boolean
}>()

defineEmits<{
  (e: 'select', key: string): void
}>()

const typeLabel = computed(() => QUESTION_TYPE_MAP[props.question.type] || props.question.type)
const diffLabel = computed(() => DIFFICULTY_MAP[props.question.difficulty] || props.question.difficulty)

function getOptionClass(key: string) {
  return {
    selected: props.userAnswer === key && !props.showResult,
    correct: props.showResult && key === props.question.answer,
    wrong: props.showResult && props.userAnswer === key && key !== props.question.answer,
  }
}
</script>

<style lang="scss" scoped>
.question-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
}

.q-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.q-index {
  font-size: 24rpx;
  color: #9CA3AF;
}

.q-tags {
  display: flex;
  gap: 8rpx;
}

.q-tag {
  padding: 2rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.q-tag.type.single { background: #DBEAFE; color: #1E40AF; }
.q-tag.type.multi { background: #FEF3C7; color: #92400E; }
.q-tag.type.judge { background: #D1FAE5; color: #065F46; }
.q-tag.type.fill { background: #EDE9FE; color: #5B21B6; }

.q-tag.diff.easy { background: #D1FAE5; color: #065F46; }
.q-tag.diff.medium { background: #FEF3C7; color: #92400E; }
.q-tag.diff.hard { background: #FEE2E2; color: #991B1B; }

.q-stem {
  font-size: 28rpx;
  line-height: 1.8;
  color: #1F2937;
  margin-bottom: 24rpx;
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 20rpx 16rpx;
  border-radius: 12rpx;
  border: 2rpx solid #E5E7EB;
  background: #fff;
}

.option-item.selected {
  border-color: #4F46E5;
  background: #EEF2FF;
}

.option-item.correct {
  border-color: #10B981;
  background: #D1FAE5;
}

.option-item.wrong {
  border-color: #EF4444;
  background: #FEE2E2;
}

.option-key {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  color: #6B7280;
}

.option-item.selected .option-key {
  background: #4F46E5;
  color: #fff;
}

.option-item.correct .option-key {
  background: #10B981;
  color: #fff;
}

.option-item.wrong .option-key {
  background: #EF4444;
  color: #fff;
}

.option-text {
  flex: 1;
  margin-left: 12rpx;
  font-size: 26rpx;
  color: #1F2937;
}

.option-icon {
  font-size: 24rpx;
  font-weight: 700;
  color: #10B981;
}

.option-icon.wrong {
  color: #EF4444;
}

.analysis {
  margin-top: 20rpx;
  padding: 16rpx;
  background: #F0FDF4;
  border-radius: 12rpx;
}

.analysis-label {
  font-size: 24rpx;
  font-weight: 600;
  color: #065F46;
  display: block;
  margin-bottom: 8rpx;
}

.analysis-text {
  font-size: 24rpx;
  color: #374151;
  line-height: 1.7;
}
</style>

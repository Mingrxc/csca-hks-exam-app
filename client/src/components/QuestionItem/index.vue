<template>
  <view class="question-item">
    <view class="q-header">
      <view class="q-index-wrap">
        <text class="q-index">第 {{ index + 1 }} 题</text>
        <text class="q-index-sub">{{ getExamLabel(question.examType) }}</text>
      </view>
      <view class="q-tags">
        <t-tag theme="primary" variant="light" shape="round" size="small">{{ typeLabel }}</t-tag>
        <t-tag theme="default" variant="light" shape="round" size="small">{{ diffLabel }}</t-tag>
        <t-tag theme="warning" variant="light" shape="round" size="small">
          {{ domainLabel }}·{{ domainValue }}
        </t-tag>
        <t-button
          class="favorite-btn"
          theme="default"
          :variant="isFavorite ? 'outline' : 'text'"
          size="small"
          shape="round"
          @click.stop="$emit('favorite')"
        >
          {{ isFavorite ? '已收藏' : '收藏' }}
        </t-button>
      </view>
    </view>

    <view class="q-stem">
      <view class="stem-ribbon"></view>
      <rich-text :nodes="question.stem"></rich-text>
    </view>

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

    <view class="analysis" v-if="showResult && question.analysis">
      <text class="analysis-label">解析</text>
      <text class="analysis-text">{{ question.analysis }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Question } from '@/types/exam'
import { DIFFICULTY_MAP, QUESTION_TYPE_MAP } from '@/utils'
import { getQuestionDomain, getQuestionDomainLabel, getExamLabel } from '@/constants/exam'

const props = defineProps<{
  question: Question
  index: number
  userAnswer: string
  showResult: boolean
  isFavorite?: boolean
}>()

defineEmits<{
  (e: 'select', key: string): void
  (e: 'favorite'): void
}>()

const typeLabel = computed(() => QUESTION_TYPE_MAP[props.question.type] || props.question.type)
const diffLabel = computed(() => DIFFICULTY_MAP[props.question.difficulty] || props.question.difficulty)
const domainLabel = computed(() => getQuestionDomainLabel(props.question.examType))
const domainValue = computed(() => getQuestionDomain(props.question))

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
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.q-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18rpx;
  flex-wrap: wrap;
}

.q-index-wrap {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.q-index {
  font-size: 22rpx;
  font-weight: 600;
  color: var(--app-text-weak);
}

.q-index-sub {
  font-size: var(--app-font-xs);
  color: var(--app-text-mute);
}

.q-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10rpx;
}

.favorite-btn {
  min-width: 110rpx;
}

.q-stem {
  position: relative;
  padding: 16rpx 18rpx 16rpx 24rpx;
  border-radius: var(--app-radius-md);
  background: var(--app-surface-quiet);
  border: 1rpx solid rgba(201, 151, 118, 0.12);
  font-size: 30rpx;
  line-height: 1.8;
  color: var(--app-text);
}

.stem-ribbon {
  position: absolute;
  left: 0;
  top: 18rpx;
  bottom: 18rpx;
  width: 6rpx;
  border-radius: 999px;
  background: var(--app-primary);
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.option-item {
  display: flex;
  align-items: center;
  min-height: 96rpx;
  padding: 22rpx 20rpx;
  border-radius: var(--app-radius-md);
  border: 1rpx solid var(--app-border);
  background: rgba(255, 253, 249, 0.94);
}

.option-item.selected {
  border-color: rgba(184, 107, 75, 0.28);
  background: var(--app-primary-soft);
}

.option-item.correct {
  border-color: rgba(126, 154, 128, 0.26);
  background: #f0f6f1;
}

.option-item.wrong {
  border-color: rgba(198, 95, 82, 0.22);
  background: #fbefeb;
}

.option-key {
  width: 44rpx;
  height: 44rpx;
  border-radius: 999px;
  background: var(--app-surface-quiet);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  color: var(--app-text-weak);
}

.option-item.selected .option-key {
  background: var(--app-primary);
  color: #ffffff;
}

.option-item.correct .option-key {
  background: var(--app-success);
  color: #ffffff;
}

.option-item.wrong .option-key {
  background: var(--app-danger);
  color: #ffffff;
}

.option-text {
  flex: 1;
  margin-left: 12rpx;
  font-size: 28rpx;
  line-height: 1.7;
  color: var(--app-text);
}

.option-icon {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-success);
}

.option-icon.wrong {
  color: var(--app-danger);
}

.analysis {
  margin-top: 4rpx;
  padding: 18rpx;
  background: var(--app-secondary-soft);
  border-radius: var(--app-radius-md);
  border: 1rpx solid rgba(126, 154, 128, 0.12);
}

.analysis-label {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-primary);
  display: block;
  margin-bottom: 8rpx;
}

.analysis-text {
  font-size: 24rpx;
  color: var(--app-text-weak);
  line-height: 1.7;
}
</style>

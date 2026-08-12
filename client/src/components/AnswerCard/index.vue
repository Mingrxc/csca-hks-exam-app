<template>
  <view class="answer-card">
    <view class="card-header">
      <text class="card-title">答题卡</text>
      <view class="card-stats">
        <text>{{ answeredCount }}/{{ total }}已答</text>
      </view>
    </view>

    <view class="card-grid">
      <view
        class="card-item"
        :class="{
          answered: item.answered,
          current: item.index === current,
          marked: item.marked
        }"
        v-for="item in items"
        :key="item.index"
        @click="$emit('jump', item.index)"
      >
        {{ item.index + 1 }}
      </view>
    </view>

    <view class="card-legend">
      <view class="legend-item">
        <view class="dot answered"></view>
        <text>已答</text>
      </view>
      <view class="legend-item">
        <view class="dot"></view>
        <text>未答</text>
      </view>
      <view class="legend-item">
        <view class="dot current"></view>
        <text>当前</text>
      </view>
      <view class="legend-item">
        <view class="dot marked"></view>
        <text>标记</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
export interface AnswerItem {
  index: number
  answered: boolean
  marked: boolean
}

const props = defineProps<{
  items: AnswerItem[]
  total: number
  answeredCount: number
  current: number
}>()

defineEmits<{
  (e: 'jump', index: number): void
}>()
</script>

<style lang="scss" scoped>
.answer-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
}

.card-stats {
  font-size: 22rpx;
  color: #9CA3AF;
}

.card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  justify-content: center;
}

.card-item {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #6B7280;
}

.card-item.answered {
  background: #EEF2FF;
  color: #4F46E5;
}

.card-item.current {
  background: #4F46E5;
  color: #fff;
  font-weight: 600;
}

.card-item.marked {
  border: 2rpx solid #F59E0B;
}

.card-legend {
  display: flex;
  justify-content: center;
  gap: 32rpx;
  margin-top: 20rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 20rpx;
  color: #9CA3AF;
}

.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #F3F4F6;
}

.dot.answered {
  background: #EEF2FF;
}

.dot.current {
  background: #4F46E5;
}

.dot.marked {
  background: #FEF3C7;
  border: 2rpx solid #F59E0B;
}
</style>

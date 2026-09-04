<template>
  <view class="answer-card">
    <view class="card-header">
      <view>
        <text class="card-title">答题卡</text>
        <text class="card-subtitle">点选题号快速跳转</text>
      </view>
      <view class="card-stats">{{ answeredCount }}/{{ total }} 已答</view>
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
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16rpx;
}

.card-title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: var(--app-text);
}

.card-subtitle {
  display: block;
  margin-top: 4rpx;
  font-size: 20rpx;
  color: var(--app-text-weak);
}

.card-stats {
  flex: none;
  padding: 8rpx 14rpx;
  border-radius: 999px;
  background: var(--app-primary-soft);
  color: var(--app-primary);
  font-size: 20rpx;
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
  border-radius: 999px;
  background: #f8f1e8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: var(--app-text-weak);
  border: 1rpx solid var(--app-border);
}

.card-item.answered {
  background: var(--app-primary-soft);
  color: var(--app-primary);
  border-color: rgba(199, 127, 94, 0.18);
}

.card-item.current {
  background: var(--app-primary);
  color: #fff;
  font-weight: 600;
}

.card-item.marked {
  border: 1rpx solid rgba(208, 161, 106, 0.9);
}

.card-legend {
  display: flex;
  justify-content: center;
  gap: 32rpx;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 20rpx;
  color: var(--app-text-weak);
}

.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #efe5d8;
}

.dot.answered {
  background: var(--app-primary-soft);
}

.dot.current {
  background: var(--app-primary);
}

.dot.marked {
  background: var(--app-accent-soft);
  border: 1rpx solid var(--app-accent);
}
</style>

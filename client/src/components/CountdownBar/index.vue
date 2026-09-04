<template>
  <view class="countdown-bar">
    <view class="timer-icon">
      <view class="timer-core"></view>
    </view>
    <text class="timer-text" :class="{ warning: remaining <= 300, danger: remaining <= 60 }">
      {{ displayText }}
    </text>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { formatTime } from '@/utils'

const props = defineProps<{
  seconds: number
}>()

const emit = defineEmits<{
  (e: 'timeout'): void
}>()

const remaining = ref(props.seconds)
let timer: any = null

const displayText = computed(() => formatTime(remaining.value))

onMounted(() => {
  timer = setInterval(() => {
    if (remaining.value > 0) {
      remaining.value--
    } else {
      clearInterval(timer)
      emit('timeout')
    }
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style lang="scss" scoped>
.countdown-bar {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 8rpx 14rpx;
  border-radius: 999px;
  background: #fbf3e8;
  border: 1rpx solid var(--app-border);
}

.timer-icon {
  width: 22rpx;
  height: 22rpx;
  border-radius: 50%;
  border: 2rpx solid var(--app-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.timer-core {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: var(--app-primary);
}

.timer-text {
  font-size: 26rpx;
  font-weight: 600;
  font-family: var(--app-font-family);
  font-variant-numeric: tabular-nums;
  color: var(--app-text);
}

.timer-text.warning {
  color: var(--app-accent);
}

.timer-text.danger {
  color: var(--app-danger);
}
</style>

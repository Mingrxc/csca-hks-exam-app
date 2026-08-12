<template>
  <view class="countdown-bar">
    <view class="timer-icon">⏱</view>
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
  gap: 8rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  background: #F3F4F6;
}

.timer-icon {
  font-size: 24rpx;
}

.timer-text {
  font-size: 26rpx;
  font-weight: 600;
  font-family: 'Menlo', monospace;
  color: #374151;
}

.timer-text.warning {
  color: #F59E0B;
}

.timer-text.danger {
  color: #EF4444;
}
</style>

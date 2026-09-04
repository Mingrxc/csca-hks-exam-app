<template>
  <view class="ring-chart" :style="{ width: size + 'rpx', height: size + 'rpx' }">
    <canvas
      canvas-id="ringCanvas"
      :style="{ width: size + 'rpx', height: size + 'rpx' }"
    ></canvas>
    <view class="ring-center">
      <text class="ring-value" :style="{ color }">{{ percent }}%</text>
      <text class="ring-label" v-if="label">{{ label }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
  percent: number
  size?: number
  color?: string
  bgColor?: string
  lineWidth?: number
  label?: string
}>()

const size = ref(props.size || 200)
const color = ref(props.color || '#C77F5E')
const bgColor = ref(props.bgColor || '#E2E8F0')
const lineWidth = ref(props.lineWidth || 12)

function drawRing() {
  const ctx = uni.createCanvasContext('ringCanvas')
  const center = size.value / 2
  const radius = center - lineWidth.value / 2
  const endAngle = (props.percent / 100) * 2 * Math.PI

  // 背景圆环
  ctx.beginPath()
  ctx.arc(center, center, radius, 0, 2 * Math.PI)
  ctx.setStrokeStyle(bgColor.value)
  ctx.setLineWidth(lineWidth.value)
  ctx.setLineCap('round')
  ctx.stroke()

  // 进度圆环
  ctx.beginPath()
  ctx.arc(center, center, radius, -Math.PI / 2, -Math.PI / 2 + endAngle)
  ctx.setStrokeStyle(color.value)
  ctx.setLineWidth(lineWidth.value)
  ctx.setLineCap('round')
  ctx.stroke()

  ctx.draw()
}

onMounted(() => drawRing())
watch(() => props.percent, () => drawRing())
</script>

<style lang="scss" scoped>
.ring-chart {
  position: relative;
  margin: 0 auto;
}

.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-value {
  font-size: 38rpx;
  font-weight: 600;
  line-height: 1;
  color: var(--app-text);
}

.ring-label {
  font-size: 20rpx;
  color: var(--app-text-weak);
  margin-top: 4rpx;
}
</style>

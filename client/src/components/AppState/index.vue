<template>
  <view class="app-state" :class="`app-state--${state}`">
    <view v-if="state === 'loading'" class="app-state__spinner"></view>
    <t-icon v-else :name="state === 'error' ? 'error-circle' : icon" size="52rpx" :color="iconColor" />
    <text class="app-state__title">{{ resolvedTitle }}</text>
    <text v-if="description" class="app-state__description">{{ description }}</text>
    <t-button
      v-if="state === 'error'"
      class="app-state__action"
      theme="primary"
      variant="outline"
      size="small"
      shape="round"
      @click="$emit('retry')"
    >
      重新加载
    </t-button>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  state: 'loading' | 'empty' | 'error'
  title?: string
  description?: string
  icon?: string
}>(), {
  title: '', description: '', icon: 'inbox',
})

defineEmits<{ (event: 'retry'): void }>()

const resolvedTitle = computed(() => props.title || ({
  loading: '正在加载', empty: '暂无内容', error: '加载失败',
}[props.state]))
const iconColor = computed(() => props.state === 'error' ? 'var(--app-danger)' : 'var(--app-text-mute)')
</script>

<style lang="scss" scoped>
.app-state {
  min-height: 260rpx;
  padding: var(--app-space-8) var(--app-space-5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.app-state__spinner {
  width: 44rpx;
  height: 44rpx;
  border: 4rpx solid var(--app-primary-soft);
  border-top-color: var(--app-primary);
  border-radius: 50%;
  animation: app-state-spin 0.8s linear infinite;
}

.app-state__title {
  margin-top: var(--app-space-3);
  font-size: var(--app-font-md);
  font-weight: 600;
  color: var(--app-text);
}

.app-state__description {
  margin-top: var(--app-space-2);
  font-size: var(--app-font-sm);
  color: var(--app-text-weak);
}

.app-state__action { margin-top: var(--app-space-4); }

@keyframes app-state-spin { to { transform: rotate(360deg); } }
</style>

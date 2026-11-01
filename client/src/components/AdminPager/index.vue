<template>
  <view v-if="total > pageSize" class="pager app-section">
    <button :disabled="loading || page <= 1" @tap="$emit('change', page - 1)">{{ t('上一页') }}</button>
    <text>{{ page }} / {{ Math.ceil(total / pageSize) }}</text>
    <button :disabled="loading || page * pageSize >= total" @tap="$emit('change', page + 1)">{{ t('下一页') }}</button>
  </view>
</template>
<script setup lang="ts">
import { t } from '@/i18n'
withDefaults(defineProps<{ page: number; total: number; pageSize?: number; loading: boolean }>(), { pageSize: 20 })
defineEmits<{ change: [page: number] }>()
</script>
<style scoped>
.pager { display: flex; align-items: center; justify-content: space-between; gap: 20rpx; font-size: 24rpx; color: var(--app-text-weak); }
.pager button { margin: 0; padding: 12rpx 24rpx; border-radius: 16rpx; font-size: 24rpx; background: var(--app-surface); color: var(--app-primary); }
.pager button::after { border: 0; }.pager button[disabled] { color: var(--app-text-mute); }
</style>

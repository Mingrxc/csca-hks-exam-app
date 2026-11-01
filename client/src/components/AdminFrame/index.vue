<template>
  <c-auth-frame>
    <view class="admin-shell app-shell">
      <view v-if="loading" class="app-section app-card app-card-pad"><c-app-state state="loading" :title="t('正在加载管理数据')" /></view>
      <view v-else-if="!allowed" class="app-section app-card app-card-pad"><c-app-state state="empty" :title="t('暂无管理权限')" :description="t('请返回我的页面。')" /></view>
      <template v-else>
        <view v-if="error" class="app-section app-card app-card-pad"><c-app-state state="error" :title="t('暂时无法加载')" :description="error" @retry="$emit('retry')" /></view>
        <slot />
      </template>
    </view>
  </c-auth-frame>
</template>
<script setup lang="ts">
import { t } from '@/i18n'
defineProps<{ loading: boolean; allowed: boolean; error: string }>()
defineEmits<{ retry: [] }>()
</script>
<style scoped>.admin-shell { min-height: 100vh; padding-top: 8rpx; padding-bottom: 40rpx; }</style>

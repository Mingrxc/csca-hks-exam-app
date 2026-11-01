<template>
  <slot v-if="user.isLogin" />
  <view v-else class="auth-frame app-shell">
    <view class="app-section"><view class="app-card app-card-pad auth-card">
      <t-icon name="user-circle" size="64rpx" color="#b86b4b" />
      <text class="auth-title">{{ t('登录后即可使用') }}</text>
      <text class="auth-copy">{{ t('登录后保存你的学习记录与进度') }}</text>
      <button class="auth-button" @tap="openLogin()">{{ t('去登录') }}</button>
    </view></view>
  </view>
</template>
<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { openLogin } from '@/shared/auth/navigation'
import { t } from '@/i18n'
import { onMounted } from 'vue'
import { promptLogin } from '@/shared/auth/navigation'
const user = useUserStore()
onMounted(async () => { await user.restoreSession(); if (!user.isLogin) promptLogin() })
</script>
<style scoped>
.auth-frame { min-height: 100vh; padding-top: 48rpx; }
.auth-card { text-align: center; }
.auth-title { display: block; margin-top: 24rpx; font-size: 34rpx; font-weight: 600; }
.auth-copy { display: block; margin-top: 16rpx; color: var(--app-text-weak); font-size: 26rpx; }
.auth-button { margin-top: 32rpx; padding: 20rpx; line-height: 1.5; border-radius: 20rpx; background: var(--app-primary); color: var(--app-surface); font-size: 28rpx; }
</style>

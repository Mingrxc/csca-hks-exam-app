<template>
  <view class="login-page app-shell">
    <view class="app-section"><view class="login-card app-card app-card-pad">
      <text class="login-title">{{ user.isLogin ? t('完善个人资料') : t('欢迎回来') }}</text>
      <text class="login-copy">{{ t('登录后保存你的学习记录与进度') }}</text>
      <button class="avatar-picker" open-type="chooseAvatar" :disabled="saving" @chooseavatar="chooseAvatar">
        <image v-if="avatarDraft || user.userInfo.avatarUrl" :src="avatarDraft || user.userInfo.avatarUrl" mode="aspectFill" class="avatar-image" />
        <t-icon v-else name="user-circle" size="90rpx" color="#b86b4b" />
      </button>
      <text class="avatar-hint">{{ t('点击选择头像') }}</text>
      <text class="field-label">{{ t('昵称') }}</text>
      <input class="nickname-input" type="nickname" :value="nickname" :disabled="saving" maxlength="64"
        :placeholder="t('填写昵称，可稍后完善')" @input="nickname = $event.detail.value" @blur="onNicknameBlur"
        @nicknamereview="nicknameAllowed = $event.detail.pass !== false" />
      <text class="login-note">{{ t('点击头像选择图片；点击昵称输入框，可选用微信昵称。资料可稍后完善。') }}</text>
      <text v-if="error" class="login-error">{{ error }}</text>
      <button class="login-button" :loading="saving" :disabled="saving || !nicknameAllowed" @tap="submit">
        {{ saving ? t('正在保存…') : user.isLogin ? t('保存资料') : t('微信登录') }}
      </button>
      <button class="later-button" :disabled="saving" @tap="leave">{{ user.isLogin ? t('返回') : t('暂不登录，继续浏览') }}</button>
    </view></view>
  </view>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/features/user/api'
import { usePageI18n } from '@/i18n/page'
import { errorText, t } from '@/i18n'
import { cancelLogin, finishLogin } from '@/shared/auth/navigation'

usePageI18n('pages/login/index')
const user = useUserStore()
const nickname = ref('')
const avatarDraft = ref('')
const nicknameAllowed = ref(true)
const saving = ref(false)
const error = ref('')
function chooseAvatar(event: any) { avatarDraft.value = event.detail?.avatarUrl || '' }
function onNicknameBlur(event: any) { nickname.value = String(event.detail?.value || nickname.value) }
onLoad(async () => { await user.restoreSession(); if (user.isLogin) nickname.value = user.userInfo.nickname })
async function submit() {
  if (saving.value || !nicknameAllowed.value) return
  saving.value = true
  error.value = ''
  try {
    const name = nickname.value.trim()
    if (!user.isLogin) await user.login(name || undefined)
    else if (name && name !== user.userInfo.nickname) user.applyProfile(await userApi.updateProfile({ nickname: name }))
    if (avatarDraft.value) user.applyProfile(await userApi.uploadAvatar(avatarDraft.value))
    finishLogin()
  } catch (reason: any) {
    error.value = errorText(reason?.message || reason?.errMsg || '登录失败，请重试')
  } finally { saving.value = false }
}
function leave() {
  cancelLogin()
  if (getCurrentPages().length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
}
onUnload(cancelLogin)
</script>
<style scoped>
.login-page { min-height: 100vh; padding-top: 40rpx; }
.login-card { padding: 48rpx 36rpx; }
.login-title { display: block; font-size: 40rpx; font-weight: 600; }
.login-copy { display: block; margin-top: 14rpx; font-size: 26rpx; line-height: 1.6; color: var(--app-text-weak); }
.avatar-picker { display: flex; align-items: center; justify-content: center; width: 140rpx; height: 140rpx; margin: 42rpx auto 0; padding: 0; border: 1rpx solid var(--app-border); border-radius: 50%; background: var(--app-primary-soft); overflow: hidden; }
.avatar-picker::after { border: 0; }
.avatar-image { width: 100%; height: 100%; }
.avatar-hint { display: block; margin: 14rpx 0 36rpx; text-align: center; font-size: 23rpx; color: var(--app-primary); }
.field-label { display: block; margin-bottom: 14rpx; font-size: 26rpx; }
.nickname-input { height: 94rpx; padding: 0 22rpx; background: var(--app-surface-quiet); border: 1rpx solid var(--app-border); border-radius: 20rpx; font-size: 28rpx; color: var(--app-text); }
.login-note { display: block; margin: 18rpx 0 30rpx; font-size: 23rpx; line-height: 1.7; color: var(--app-text-mute); }
.login-error { display: block; margin: 20rpx 0; color: var(--app-danger); font-size: 24rpx; }
.login-button { padding: 24rpx; line-height: 1.5; border: 0; border-radius: 20rpx; background: var(--app-primary); color: var(--app-surface); font-size: 29rpx; }
.later-button { margin-top: 20rpx; padding: 18rpx; line-height: 1.5; border: 0; background: transparent; color: var(--app-text-weak); font-size: 25rpx; }
.later-button::after, .login-button::after { border: 0; }
</style>

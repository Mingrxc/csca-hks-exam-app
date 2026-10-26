<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="brand-card app-card">
        <image class="brand-icon" :src="APP_ICON_PATH" mode="aspectFit" />
        <text class="brand-name">{{ APP_NAME }}</text>
        <text class="brand-version">{{ t("版本") }} {{ APP_VERSION }}</text>
        <text class="brand-description">{{ t(APP_DESCRIPTION) }}</text>
      </view>
    </view>
    <view class="app-section">
      <view class="about-menu app-card">
        <view class="about-row" hover-class="about-row--pressed" @tap="openAnnouncements">
          <view class="app-icon-badge"><t-icon name="notification" size="32rpx" /></view>
          <text class="row-label">{{ t("更新公告") }}</text>
          <t-icon name="chevron-right" size="32rpx" />
        </view>
        <view class="about-row" hover-class="about-row--pressed" @tap="openPrivacyGuide">
          <view class="app-icon-badge"><t-icon name="secured" size="32rpx" /></view>
          <text class="row-label">{{ t("隐私保护指引") }}</text>
          <t-icon name="chevron-right" size="32rpx" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { showToast } from '@/i18n/ui'
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { APP_DESCRIPTION, APP_ICON_PATH, APP_NAME, APP_VERSION } from '@/constants/brand'

usePageI18n('pages/about/index')

const openAnnouncements = () => uni.navigateTo({ url: '/pages/about/announcements' })

function openPrivacyGuide() {
  // #ifdef MP-WEIXIN
  if (typeof wx !== 'undefined' && typeof wx.openPrivacyContract === 'function') {
    wx.openPrivacyContract({
      fail: () => showToast({ title: '隐私保护指引暂时无法打开，请稍后重试', icon: 'none' }),
    })
  } else {
    showToast({ title: '请更新微信后查看隐私保护指引', icon: 'none' })
  }
  // #endif
  // #ifndef MP-WEIXIN
  showToast({ title: '请在微信小程序中查看隐私保护指引', icon: 'none' })
  // #endif
}
</script>

<style lang="scss" scoped>
.brand-card { display: flex; flex-direction: column; align-items: center; padding: 64rpx 32rpx 52rpx; text-align: center; }
.brand-icon { width: 148rpx; height: 148rpx; border-radius: 32rpx; }
.brand-name { margin-top: 28rpx; font-size: 40rpx; font-weight: 600; color: var(--app-text); }
.brand-version { margin-top: 8rpx; color: var(--app-text-mute); font-size: 24rpx; }
.brand-description { margin-top: 28rpx; color: var(--app-text-weak); font-size: 26rpx; line-height: 1.8; }
.about-menu { padding: 0 24rpx; }
.about-row { display: flex; align-items: center; gap: 18rpx; min-height: 120rpx; color: var(--app-text-mute); }
.about-row + .about-row { border-top: 1rpx solid var(--app-border); }
.about-row--pressed { opacity: .65; }
.row-label { flex: 1; font-size: 28rpx; color: var(--app-text); }
</style>

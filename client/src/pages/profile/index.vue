<template>
  <view class="page">
    <!-- 用户信息卡片 -->
    <view class="profile-header">
      <view class="avatar-area">
        <view class="avatar">😊</view>
        <text class="nickname">{{ userInfo.nickname }}</text>
        <text class="exam-target">目标：{{ userInfo.targetExam }}</text>
      </view>
    </view>

    <!-- 学习数据 -->
    <view class="stats-section">
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-num">{{ userInfo.totalQuestions }}</text>
          <text class="stat-label">累计刷题</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ userInfo.correctRate }}%</text>
          <text class="stat-label">总正确率</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-num">{{ userInfo.streakDays }}</text>
          <text class="stat-label">连续打卡</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-group">
        <view class="menu-item" @click="goPage('/pages/exam/index')">
          <text class="menu-icon">📝</text>
          <text class="menu-label">我的试卷</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="goPage('/pages/wrongbook/index')">
          <text class="menu-icon">📋</text>
          <text class="menu-label">错题统计</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item" @click="goPage('/pages/wrongbook/redo')">
          <text class="menu-icon">🔄</text>
          <text class="menu-label">错题重做</text>
          <text class="menu-arrow">→</text>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-item">
          <text class="menu-icon">🏆</text>
          <text class="menu-label">成就勋章</text>
          <text class="menu-badge">3</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item">
          <text class="menu-icon">📊</text>
          <text class="menu-label">学习报告</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item">
          <text class="menu-icon">⏰</text>
          <text class="menu-label">学习提醒</text>
          <view class="menu-switch">
            <switch :checked="reminderOn" @change="toggleReminder" color="#4F46E5" />
          </view>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-item">
          <text class="menu-icon">🎯</text>
          <text class="menu-label">考试目标设置</text>
          <text class="menu-value">{{ userInfo.targetExam }}</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item">
          <text class="menu-icon">📖</text>
          <text class="menu-label">关于留学考霸</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-item">
          <text class="menu-icon">💬</text>
          <text class="menu-label">意见反馈</text>
          <text class="menu-arrow">→</text>
        </view>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { mockUserProfile } from '@/mock/user'
import type { UserProfile } from '@/types/user'

const userInfo = ref<UserProfile>(mockUserProfile)

const reminderOn = ref(true)

const toggleReminder = (e: any) => {
  reminderOn.value = e.detail.value
  uni.showToast({ title: reminderOn.value ? '已开启提醒' : '已关闭提醒', icon: 'none' })
}

const goPage = (url: string) => {
  if (url.startsWith('/pages/exam') || url.startsWith('/pages/wrongbook')) {
    uni.navigateTo({ url })
  } else {
    uni.switchTab({ url })
  }
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '退出后需要重新登录，确定退出吗？',
    success: (res: any) => {
      if (res.confirm) {
        uni.removeStorageSync('token')
        uni.showToast({ title: '已退出登录', icon: 'success' })
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; padding-bottom: 40rpx; }

.profile-header {
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
  padding: 60rpx 0 48rpx;
  border-radius: 0 0 48rpx 48rpx;
}
.avatar-area { text-align: center; }
.avatar { font-size: 80rpx; display: block; margin-bottom: 16rpx; }
.nickname { font-size: 36rpx; font-weight: 700; color: #fff; display: block; }
.exam-target { font-size: 24rpx; color: rgba(255,255,255,0.7); margin-top: 8rpx; display: block; }

.stats-section { padding: 0 24rpx; margin-top: -28rpx; }
.stats-card {
  background: #fff; border-radius: 20rpx; padding: 28rpx 0;
  display: flex; align-items: center; justify-content: space-around;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
}
.stat-item { text-align: center; flex: 1; }
.stat-num { font-size: 40rpx; font-weight: 700; color: #4F46E5; display: block; }
.stat-label { font-size: 22rpx; color: #9CA3AF; margin-top: 6rpx; }
.stat-divider { width: 2rpx; height: 48rpx; background: #E5E7EB; }

.menu-section { padding: 24rpx; }
.menu-group { background: #fff; border-radius: 16rpx; margin-bottom: 16rpx; overflow: hidden; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03); }
.menu-item {
  display: flex; align-items: center; padding: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
}
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 36rpx; margin-right: 16rpx; }
.menu-label { flex: 1; font-size: 28rpx; color: #1F2937; }
.menu-value { font-size: 24rpx; color: #9CA3AF; margin-right: 8rpx; }
.menu-badge {
  background: #EF4444; color: #fff; font-size: 20rpx;
  padding: 2rpx 12rpx; border-radius: 20rpx; margin-right: 8rpx;
}
.menu-arrow { font-size: 24rpx; color: #C7D2FE; }

.logout-section { padding: 24rpx; }
.logout-btn {
  background: #fff; border-radius: 48rpx; font-size: 28rpx;
  color: #EF4444; text-align: center; padding: 20rpx 0; border: none;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
</style>

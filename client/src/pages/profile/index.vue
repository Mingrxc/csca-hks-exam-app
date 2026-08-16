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

    <view class="load-error" v-if="loadError" @click="loadProfile">
      <text>个人资料加载失败，点击重试</text>
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
        <view class="menu-item" @click="goRedo">
          <text class="menu-icon">🔄</text>
          <text class="menu-label">错题重做</text>
          <text class="menu-arrow">→</text>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-item" @click="openTargetEditor">
          <text class="menu-icon">🎯</text>
          <text class="menu-label">考试目标设置</text>
          <text class="menu-value">{{ userInfo.targetExam }}</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="target-editor" v-if="targetEditorOpen">
          <view class="exam-segments">
            <view class="exam-segment" :class="{ active: targetDraftExam === 'CSCA' }" @click="targetDraftExam = 'CSCA'">CSCA</view>
            <view class="exam-segment" :class="{ active: targetDraftExam === 'HKS' }" @click="targetDraftExam = 'HKS'">HKS</view>
          </view>
          <picker mode="date" :value="targetDraftDate" :start="today" @change="selectTargetDate">
            <view class="date-picker">{{ targetDraftDate || '选择考试日期' }}</view>
          </picker>
          <button class="save-target" :disabled="savingTarget" @click="saveTarget">保存目标</button>
        </view>
        <view class="menu-item" @click="showAbout">
          <text class="menu-icon">📖</text>
          <text class="menu-label">关于留学考霸</text>
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
import { onShow } from '@dcloudio/uni-app'
import { userApi } from '@/api'
import { toUserProfile } from '@/api/contracts'
import type { UserProfile } from '@/types/user'

const userInfo = ref<UserProfile>({
  nickname: '考霸同学',
  avatarUrl: '',
  targetExam: 'CSCA',
  targetDate: '',
  totalQuestions: 0,
  correctRate: 0,
  streakDays: 0,
})
const loadError = ref(false)
const targetEditorOpen = ref(false)
const targetDraftExam = ref<'CSCA' | 'HKS'>('CSCA')
const targetDraftDate = ref('')
const savingTarget = ref(false)
const now = new Date()
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

const loadProfile = async () => {
  loadError.value = false
  try {
    userInfo.value = toUserProfile(await userApi.getUserInfo())
  } catch {
    loadError.value = true
  }
}

const openTargetEditor = () => {
  targetDraftExam.value = userInfo.value.targetExam
  targetDraftDate.value = userInfo.value.targetDate
  targetEditorOpen.value = !targetEditorOpen.value
}

const selectTargetDate = (event: any) => {
  targetDraftDate.value = event.detail.value
}

const saveTarget = async () => {
  if (!targetDraftDate.value) {
    uni.showToast({ title: '请选择考试日期', icon: 'none' })
    return
  }
  savingTarget.value = true
  try {
    const updated = await userApi.updateProfile({
      target_exam: targetDraftExam.value,
      target_date: targetDraftDate.value,
    })
    userInfo.value = toUserProfile(updated)
    targetEditorOpen.value = false
    uni.showToast({ title: '目标已更新', icon: 'success' })
  } catch {
    // The shared request layer displays the failure.
  } finally {
    savingTarget.value = false
  }
}

const showAbout = () => {
  uni.showModal({
    title: '留学考霸',
    content: 'CSCA 与 HKS 备考刷题工具\n版本 1.0.0',
    showCancel: false,
  })
}

const goPage = (url: string) => {
  if (url === '/pages/exam/index' || url === '/pages/wrongbook/index') {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

const goRedo = () => {
  uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${userInfo.value.targetExam}` })
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

onShow(loadProfile)
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

.target-editor { padding: 24rpx; border-bottom: 1rpx solid #F3F4F6; }
.exam-segments { display: flex; background: #F3F4F6; border-radius: 8rpx; padding: 4rpx; }
.exam-segment { flex: 1; text-align: center; padding: 14rpx 0; font-size: 24rpx; color: #6B7280; border-radius: 6rpx; }
.exam-segment.active { background: #fff; color: #4F46E5; font-weight: 600; }
.date-picker { margin-top: 16rpx; padding: 20rpx; border: 1rpx solid #E5E7EB; border-radius: 8rpx; font-size: 24rpx; color: #374151; }
.save-target { margin-top: 16rpx; background: #4F46E5; color: #fff; border-radius: 8rpx; font-size: 26rpx; padding: 16rpx 0; }

.logout-section { padding: 24rpx; }
.logout-btn {
  background: #fff; border-radius: 48rpx; font-size: 28rpx;
  color: #EF4444; text-align: center; padding: 20rpx 0; border: none;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
.load-error { margin: 24rpx; padding: 24rpx; text-align: center; color: #B91C1C; background: #FEF2F2; border-radius: 12rpx; font-size: 24rpx; }
</style>

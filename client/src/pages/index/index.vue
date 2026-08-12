<template>
  <view class="page">
    <!-- 头部欢迎区 -->
    <view class="header">
      <view class="header-top">
        <view class="greeting">
          <text class="greeting-text">{{ greetingText }}</text>
          <text class="user-name">{{ userName }}</text>
        </view>
        <view class="avatar">😊</view>
      </view>
      <!-- 考试倒计时 -->
      <view class="countdown-card" v-if="targetExam">
        <text class="countdown-label">距 {{ targetExam }} 考试还有</text>
        <view class="countdown-nums">
          <view class="countdown-item">
            <text class="countdown-num">{{ countdown.days }}</text>
            <text class="countdown-unit">天</text>
          </view>
          <text class="countdown-sep">:</text>
          <view class="countdown-item">
            <text class="countdown-num">{{ countdown.hours }}</text>
            <text class="countdown-unit">时</text>
          </view>
          <text class="countdown-sep">:</text>
          <view class="countdown-item">
            <text class="countdown-num">{{ countdown.minutes }}</text>
            <text class="countdown-unit">分</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 今日数据卡片 -->
    <view class="stats-row">
      <view class="stat-card">
        <text class="stat-num">{{ todayStats.questionCount }}</text>
        <text class="stat-label">今日刷题</text>
      </view>
      <view class="stat-card accent">
        <text class="stat-num">{{ todayStats.correctRate }}%</text>
        <text class="stat-label">正确率</text>
      </view>
      <view class="stat-card warning">
        <text class="stat-num">{{ todayStats.wrongCount }}</text>
        <text class="stat-label">错题待复习</text>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="section">
      <text class="section-title">快速开始</text>
      <view class="quick-actions">
        <view
          class="action-card"
          :class="{ primary: index === 0 }"
          v-for="(item, index) in strategies"
          :key="item.key"
          @click="goExam(item.key)"
        >
          <view class="action-icon">{{ item.icon }}</view>
          <text class="action-title">{{ item.title }}</text>
          <text class="action-desc">{{ item.shortDesc }}</text>
        </view>
      </view>
    </view>

    <!-- 错题复习提醒 -->
    <view class="section" v-if="pendingWrongCount > 0">
      <view class="wrong-reminder" @click="goWrongBook">
        <view class="reminder-left">
          <text class="reminder-icon">📝</text>
          <view class="reminder-text">
            <text class="reminder-title">你有 {{ pendingWrongCount }} 道错题待复习</text>
            <text class="reminder-desc">温故而知新，错题是进步的阶梯</text>
          </view>
        </view>
        <text class="reminder-arrow">→</text>
      </view>
    </view>

    <!-- 最近试卷 -->
    <view class="section">
      <text class="section-title">最近试卷</text>
      <view class="paper-list" v-if="recentPapers.length > 0">
        <view class="paper-item" v-for="paper in recentPapers" :key="paper.id" @click="goPaper(paper.id)">
          <view class="paper-info">
            <text class="paper-title">{{ paper.title }}</text>
            <text class="paper-meta">{{ paper.questionCount }}题 · {{ paper.score }}分</text>
          </view>
          <text class="paper-date">{{ paper.date }}</text>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-icon">📋</text>
        <text class="empty-text">还没有做过试卷，快去刷题吧</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { PAPER_STRATEGIES } from '@/constants/exam'
import { mockDashboard } from '@/mock/dashboard'
import { getGreeting } from '@/utils'
import type { PaperStrategy } from '@/types/exam'

const strategies = PAPER_STRATEGIES
const userName = ref(mockDashboard.userName)
const targetExam = ref(mockDashboard.targetExam)

const greetingText = computed(() => getGreeting())

const countdown = ref(mockDashboard.countdown)
const todayStats = ref(mockDashboard.todayStats)
const pendingWrongCount = ref(mockDashboard.pendingWrongCount)
const recentPapers = ref(mockDashboard.recentPapers)

const goExam = (strategy: PaperStrategy) => {
  uni.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}` })
}

const goWrongBook = () => {
  uni.switchTab({ url: '/pages/wrongbook/index' })
}

const goPaper = (id: number) => {
  uni.navigateTo({ url: `/pages/exam/result?id=${id}` })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  padding-bottom: 40rpx;
}

.header {
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
  padding: 48rpx 32rpx 40rpx;
  border-radius: 0 0 48rpx 48rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.greeting-text { color: rgba(255,255,255,0.8); font-size: 28rpx; }
.user-name { color: #fff; font-size: 36rpx; font-weight: 700; margin-left: 8rpx; }
.avatar { font-size: 48rpx; }

.countdown-card {
  background: rgba(255,255,255,0.15);
  border-radius: 20rpx;
  padding: 24rpx;
  backdrop-filter: blur(10px);
}

.countdown-label { color: rgba(255,255,255,0.8); font-size: 24rpx; }
.countdown-nums { display: flex; align-items: baseline; margin-top: 12rpx; }
.countdown-item { display: flex; align-items: baseline; }
.countdown-num { color: #fff; font-size: 48rpx; font-weight: 700; font-family: 'Menlo', monospace; }
.countdown-unit { color: rgba(255,255,255,0.7); font-size: 24rpx; margin-left: 4rpx; }
.countdown-sep { color: rgba(255,255,255,0.5); font-size: 40rpx; margin: 0 8rpx; }

.stats-row {
  display: flex;
  margin: -24rpx 24rpx 24rpx;
  gap: 16rpx;
}

.stat-card {
  flex: 1;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}

.stat-num { font-size: 40rpx; font-weight: 700; color: #4F46E5; display: block; }
.stat-card.accent .stat-num { color: #10B981; }
.stat-card.warning .stat-num { color: #F59E0B; }
.stat-label { font-size: 22rpx; color: #9CA3AF; margin-top: 8rpx; }

.section { padding: 0 24rpx; margin-bottom: 28rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: #1F2937; margin-bottom: 16rpx; display: block; }

.quick-actions { display: flex; flex-wrap: wrap; gap: 16rpx; }
.action-card {
  width: calc(50% - 8rpx);
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.action-card.primary { background: linear-gradient(135deg, #EEF2FF, #E0E7FF); border: 2rpx solid #C7D2FE; }
.action-icon { font-size: 40rpx; display: block; margin-bottom: 12rpx; }
.action-title { font-size: 28rpx; font-weight: 600; color: #1F2937; }
.action-desc { font-size: 22rpx; color: #9CA3AF; margin-top: 6rpx; display: block; }

.wrong-reminder {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 2rpx solid #FCD34D;
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.reminder-left { display: flex; align-items: center; }
.reminder-icon { font-size: 40rpx; margin-right: 16rpx; }
.reminder-title { font-size: 28rpx; font-weight: 600; color: #92400E; display: block; }
.reminder-desc { font-size: 22rpx; color: #B45309; margin-top: 4rpx; display: block; }
.reminder-arrow { font-size: 32rpx; color: #F59E0B; }

.paper-list { background: #fff; border-radius: 16rpx; overflow: hidden; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }
.paper-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24rpx; border-bottom: 1rpx solid #F3F4F6;
}
.paper-item:last-child { border-bottom: none; }
.paper-title { font-size: 28rpx; font-weight: 500; color: #1F2937; }
.paper-meta { font-size: 22rpx; color: #9CA3AF; display: block; margin-top: 4rpx; }
.paper-date { font-size: 22rpx; color: #9CA3AF; }

.empty-state { padding: 60rpx 0; text-align: center; }
.empty-icon { font-size: 60rpx; display: block; margin-bottom: 16rpx; }
.empty-text { font-size: 26rpx; color: #9CA3AF; }
</style>

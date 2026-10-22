<template>
  <view class="exam-page app-shell">
    <view class="app-section">
      <view class="app-heading">
        <text class="app-heading-title">练习中心</text>
        <text class="app-heading-desc">按自己的节奏，练好每一题</text>
      </view>
      <c-exam-selection :selected-exams="userStore.selectedExams" @toggle="userStore.toggleSelectedExam" />
    </view>

    <view v-if="examStore.hasActiveProgress" class="app-section">
      <button class="resume-card app-card" @click="goResume">
        <view class="resume-icon"><t-icon name="play-circle" size="40rpx" /></view>
        <view class="resume-copy"><text class="app-card-title">继续上次答题</text><text class="app-card-desc">{{ getExamLabel(examStore.config.examType) }} · 已完成 {{ examStore.answeredCount }} / {{ examStore.totalCount }} 题</text></view>
        <t-icon name="chevron-right" size="28rpx" />
      </button>
    </view>

    <view class="app-section">
      <view class="app-section-head"><text class="app-section-title">选择练习方式</text><text class="exam-context">{{ userStore.selectedExamText }}</text></view>
      <view class="strategy-grid">
        <button v-for="item in strategyCards" :key="item.key" class="strategy-card app-card" @click="goPaper(item.key)">
          <view class="strategy-icon" :class="{ 'strategy-icon--sage': item.sage }"><t-icon :name="item.icon" size="38rpx" /></view>
          <text class="app-card-title">{{ item.title }}</text>
          <text class="strategy-desc">{{ item.desc }}</text>
          <view class="strategy-arrow"><t-icon name="arrow-right" size="26rpx" /></view>
        </button>
      </view>
    </view>

    <view class="app-section">
      <view class="app-section-head"><text class="app-section-title">复习与积累</text></view>
      <view class="tool-list app-card">
        <button v-for="tool in tools" :key="tool.title" class="tool-row" @click="tool.open">
          <view class="tool-icon"><t-icon :name="tool.icon" size="34rpx" /></view>
          <view class="tool-copy"><text class="tool-title">{{ tool.title }}</text><text class="tool-desc">{{ tool.desc }}</text></view>
          <t-icon name="chevron-right" size="26rpx" color="#857970" />
        </button>
      </view>
    </view>

    <view class="app-section">
      <view class="dashboard-card app-card app-card-pad">
        <view class="app-section-head"><text class="app-card-title">今天的积累</text></view>
        <c-app-state v-if="studyLoading || loading" compact state="loading" title="正在整理学习数据" />
        <c-app-state v-else-if="error" compact state="error" title="学习数据加载失败" :description="error" @retry="loadStudyData" />
        <view v-else-if="loaded" class="metric-row">
          <view class="metric"><text class="app-number">{{ dashboard.todayStats.questionCount }}</text><text class="metric-label">完成题数</text></view>
          <view class="metric metric--sage"><text class="app-number">{{ dashboard.todayStats.objectiveCount === 0 ? '—' : dashboard.todayStats.correctRate + '%' }}</text><text class="metric-label">正确率</text></view>
          <view class="metric"><text class="app-number">{{ dashboard.pendingWrongCount }}</text><text class="metric-label">待复习</text></view>
        </view>
        <c-app-state v-else compact state="empty" title="学习数据尚未加载" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShareAppMessage, onShow } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import type { PaperStrategy } from '@/types/exam'
import { getExamLabel } from '@/constants/exam'
import { useUserStore } from '@/stores/user'
import { useExamStore } from '@/stores/exam'
import { useExamDashboard } from '@/features/exam/useExamDashboard'
import { useExamNavigation } from '@/features/exam/useExamNavigation'

const userStore = useUserStore()
const examStore = useExamStore()
const { data: dashboard, loading, error, load: loadDashboard } = useExamDashboard()
const { goPractice: goPaper, goWrongRedo } = useExamNavigation()
const studyLoading = ref(false)
const loaded = ref(false)
const strategyCards: Array<{ key: PaperStrategy; icon: string; title: string; desc: string; sage: boolean }> = [
  { key: 'random', icon: 'edit-1', title: '随机练习', desc: '自由选择题数与难度', sage: false },
  { key: 'real', icon: 'calendar', title: '模拟考试', desc: '在限时中练习考试节奏', sage: true },
  { key: 'knowledge', icon: 'book', title: '专项训练', desc: '集中巩固科目与知识点', sage: true },
  { key: 'progressive', icon: 'chart-bar', title: '难度递进', desc: '从易到难，逐步提升', sage: false },
]
const goResume = () => uni.navigateTo({ url: '/pages/exam/answer' })
const tools = [
  { title: '错题复习', desc: '回看解析，找到容易错的地方', icon: 'book', open: () => uni.navigateTo({ url: '/pages/wrongbook/index' }) },
  { title: '我的收藏', desc: '留住值得反复看的题目', icon: 'star', open: () => uni.navigateTo({ url: '/pages/favorite/index' }) },
  { title: '练习记录', desc: '查看每一次练习的表现', icon: 'time', open: () => uni.navigateTo({ url: '/pages/exam/history' }) },
  { title: '错题重做', desc: '把理解变成真正的掌握', icon: 'refresh', open: goWrongRedo },
]

const loadStudyData = async () => {
  if (studyLoading.value) return
  studyLoading.value = true
  if (!userStore.isLogin) {
    try { await userStore.login() } catch {}
  }
  await loadDashboard()
  loaded.value = !error.value
  studyLoading.value = false
}

onShow(loadStudyData)
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
// #endif
</script>

<style lang="scss" scoped>
.exam-context { color: var(--app-text-mute); font-size: 22rpx; }
.resume-card { display: flex; align-items: center; gap: 20rpx; width: 100%; margin: 0; padding: 24rpx; text-align: left; color: var(--app-primary); background: var(--app-primary-soft); }
.resume-icon { flex: none; }
.resume-copy { flex: 1; min-width: 0; }
.strategy-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16rpx; }
.strategy-card { position: relative; margin: 0; padding: 28rpx 24rpx; min-height: 244rpx; text-align: left; line-height: 1.5; }
.strategy-icon { display: flex; align-items: center; justify-content: center; width: 68rpx; height: 68rpx; margin-bottom: 22rpx; border-radius: var(--app-radius-md); color: var(--app-primary); background: var(--app-primary-soft); }
.strategy-icon--sage { color: var(--app-success); background: var(--app-secondary-soft); }
.strategy-desc { display: block; margin-top: 8rpx; color: var(--app-text-weak); font-size: 22rpx; line-height: 1.6; }
.strategy-arrow { position: absolute; right: 22rpx; top: 32rpx; color: var(--app-text-mute); }
.tool-row { display: flex; align-items: center; gap: 20rpx; width: 100%; margin: 0; padding: 24rpx; background: transparent; text-align: left; line-height: 1.5; border-top: 1rpx solid var(--app-border); }
.tool-row:first-child { border: 0; }
.tool-icon { display: flex; align-items: center; justify-content: center; width: 62rpx; height: 62rpx; border-radius: 16rpx; flex: none; color: var(--app-success); background: var(--app-secondary-soft); }
.tool-copy { flex: 1; min-width: 0; }
.tool-title { display: block; color: var(--app-text); font-size: 26rpx; font-weight: 500; }
.tool-desc { display: block; margin-top: 5rpx; color: var(--app-text-weak); font-size: 22rpx; }
.metric-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.metric { border-left: 1rpx solid var(--app-border); text-align: center; }
.metric:first-child { border: 0; }
.metric .app-number { display: block; font-size: 44rpx; line-height: 1.2; color: var(--app-primary); }
.metric--sage .app-number { color: var(--app-success); }
.metric-label { display: block; margin-top: 8rpx; font-size: 22rpx; color: var(--app-text-weak); }
</style>

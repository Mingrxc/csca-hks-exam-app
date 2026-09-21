<template>
  <view class="page exam-page app-shell">
    <view class="app-section">
      <view class="hero app-card app-card-pad">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-title">刷题</text>
            <view v-if="selectedExamLabels.length" class="hero-exams">
              <t-tag
                v-for="item in selectedExamLabels"
                :key="item.value"
                :theme="item.theme"
                variant="light"
                shape="round"
                size="small"
              >
                {{ item.label }}
              </t-tag>
            </view>
          </view>
        </view>

        <view class="hero-metrics">
          <view class="hero-metric">
            <text class="hero-metric-value">{{ dashboard.todayStats.questionCount }}</text>
            <text class="hero-metric-label">今日刷题</text>
          </view>
          <view class="hero-metric">
            <text class="hero-metric-value">{{ dashboard.todayStats.correctRate }}%</text>
            <text class="hero-metric-label">正确率</text>
          </view>
          <view class="hero-metric">
            <text class="hero-metric-value">{{ dashboard.pendingWrongCount }}</text>
            <text class="hero-metric-label">待复习</text>
          </view>
          <view class="hero-metric">
            <text class="hero-metric-value">{{ dashboard.favoriteCount }}</text>
            <text class="hero-metric-label">收藏题目</text>
          </view>
        </view>
      </view>
    </view>

    <view v-if="examStore.hasActiveProgress" class="app-section">
      <view class="resume-card app-card app-card-pad" @click="goResume">
        <view class="app-list-row">
          <view class="app-list-main">
            <text class="app-card-title">继续上次答题</text>
            <text class="app-card-desc">
              {{ examStore.config.examType }} · 已答 {{ examStore.answeredCount }} / {{ examStore.totalCount }} 题
            </text>
          </view>
          <t-button theme="primary" size="small" shape="round">继续</t-button>
        </view>
      </view>
    </view>

    <view class="app-section exam-group">
      <view class="section-head">
        <text class="app-section-title">快速开始</text>
      </view>
      <view class="feature-grid">
        <view class="feature-card exam-entry-card app-card app-card-compact" v-for="item in strategyCards" :key="item.key" @click="goPaper(item.key)">
          <view class="feature-top">
            <view class="app-icon-badge"><t-icon :name="item.icon" :color="item.iconColor" size="28rpx" /></view>
          </view>
          <text class="app-card-title">{{ item.title }}</text>
        </view>
      </view>
    </view>

    <view class="app-section exam-group">
      <view class="section-head">
        <text class="app-section-title">错题收藏</text>
      </view>
      <view class="tool-grid">
        <view class="tool-card exam-entry-card app-card app-card-compact" @click="goHistory">
          <view class="tool-top">
            <view class="app-icon-badge">
              <t-icon name="file-paste-filled" size="28rpx" color="#c77f5e" />
            </view>
          </view>
          <text class="app-card-title">历史试卷</text>
        </view>
        <view class="tool-card exam-entry-card app-card app-card-compact" @click="goWrongBook">
          <view class="tool-top">
            <view class="app-icon-badge"><t-icon name="book" size="28rpx" color="#c77f5e" /></view>
          </view>
          <text class="app-card-title">错题本</text>
        </view>
        <view class="tool-card exam-entry-card app-card app-card-compact" @click="goFavorite">
          <view class="tool-top">
            <view class="app-icon-badge"><t-icon name="star" size="28rpx" color="#c77f5e" /></view>
          </view>
          <text class="app-card-title">收藏题目</text>
        </view>
        <view class="tool-card exam-entry-card app-card app-card-compact" @click="goRedo">
          <view class="tool-top">
            <view class="app-icon-badge"><t-icon name="refresh" size="28rpx" color="#c77f5e" /></view>
          </view>
          <text class="app-card-title">错题重做</text>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import type { PaperStrategy } from '@/types/exam'
import { useUserStore } from '@/stores/user'
import { useExamStore } from '@/stores/exam'
import { useExamDashboard } from '@/features/exam/useExamDashboard'

const userStore = useUserStore()
const examStore = useExamStore()
const { data: dashboard, load: loadDashboard } = useExamDashboard()
const strategyCards = computed(
  () =>
    [
      {
        key: 'random',
        icon: 'star',
        iconColor: '#c77f5e',
        title: '随机组卷',
      },
      {
        key: 'real',
        icon: 'calendar',
        iconColor: '#c77f5e',
        title: '模拟考试',
      },
      {
        key: 'knowledge',
        icon: 'book',
        iconColor: '#c77f5e',
        title: '专项训练',
      },
      {
        key: 'progressive',
        icon: 'arrow-right',
        iconColor: '#c77f5e',
        title: '难度递进',
      },
    ] as const,
)

const selectedExamLabels = computed(() =>
  userStore.selectedExams.map((exam) => ({
    value: exam,
    label: exam,
    theme: exam === 'CSCA' ? ('primary' as const) : ('warning' as const),
  })),
)
const defaultExamType = computed(() => userStore.primaryExam)

const goPaper = (strategy: PaperStrategy) => {
  uni.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}&examType=${defaultExamType.value}` })
}
const goResume = () => uni.navigateTo({ url: '/pages/exam/answer' })

const goHistory = () => uni.navigateTo({ url: '/pages/exam/history' })
const goWrongBook = () => uni.navigateTo({ url: '/pages/wrongbook/index' })
const goFavorite = () => uni.navigateTo({ url: '/pages/favorite/index' })
const goRedo = () => uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${defaultExamType.value}` })

onShow(async () => {
  if (!userStore.isLogin) {
    try { await userStore.login() } catch {}
  }
  await loadDashboard()
})
</script>

<style lang="scss" scoped>
.hero {
  border-radius: var(--app-radius-xl);
  background: linear-gradient(180deg, #fffaf4 0%, #f8ecdf 100%);
}

.resume-card {
  border-color: rgba(199, 127, 94, 0.28);
  background: linear-gradient(135deg, var(--app-primary-soft), var(--app-surface));
}

.exam-page .app-card {
  border-radius: 24rpx !important;
  overflow: hidden;
}

.exam-group .section-head {
  margin-bottom: 16rpx;
}

.exam-group + .exam-group {
  margin-top: 48rpx;
}

.hero-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18rpx;
}

.hero-copy {
  flex: 1;
  min-width: 0;
}

.hero-title {
  display: block;
  font-size: 40rpx;
  line-height: 1.25;
  font-weight: 600;
  color: var(--app-text);
}

.hero-exams {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 14rpx;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
  margin-top: 18rpx;
}

.hero-metric {
  padding: 16rpx 12rpx;
  border-radius: 20rpx !important;
  background: #fffdf8;
  border: 1rpx solid #eadfce;
  overflow: hidden;
  text-align: center;
}

.hero-metric-value {
  display: block;
  font-size: 32rpx;
  line-height: 1.1;
  font-weight: 600;
  color: var(--app-text);
}

.hero-metric-label {
  display: block;
  margin-top: 6rpx;
  font-size: 20rpx;
  color: var(--app-text-weak);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20rpx;
}

.feature-card {
  min-height: 154rpx;
}

.feature-top,
.tool-top {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 10rpx;
  margin-bottom: 14rpx;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20rpx;
}

.tool-card {
  min-height: 154rpx;
}

.exam-entry-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24rpx;
  min-height: 160rpx;
  border-radius: 24rpx !important;
  background: #fffdf8 !important;
  border: 1rpx solid #eadfce !important;
  box-shadow: 0 8rpx 24rpx rgba(117, 86, 62, 0.12) !important;
  overflow: hidden;
}

</style>

<template>
  <TimelinePreview v-if="timelinePreview" />
  <view v-else class="home-page app-shell">
    <view class="home-header">
      <view class="home-greeting">
        <text class="greeting-title">{{ t(greeting) }}{{ language === 'en' ? ', ' : '，' }}{{ displayName }}</text>
        <text class="greeting-desc">{{ t("今天，也向目标靠近一点") }}</text>
      </view>
      <c-exam-selection compact :selected-exams="userStore.selectedExams" @toggle="userStore.toggleSelectedExam" />
    </view>

    <view class="app-section goal-section">
      <view class="goal-card app-card app-card-pad">
        <view class="goal-top">
          <view class="goal-copy">
            <text class="goal-label">{{ t("我的学习目标") }}</text>
            <template v-if="userStore.isBrowseMode">
              <text class="goal-caption">{{ t("随便看看，按自己的节奏开始") }}</text>
              <text class="browse-note">{{ t("先探索感兴趣的内容，再慢慢确定目标") }}</text>
            </template>
            <template v-else-if="goalTargets.length === 1">
              <text class="goal-caption">{{ goalTargets[0].date ? t('距 {exam} 目标考试', { exam: goalTargets[0].label }) : t('为 {exam} 设定学习目标', { exam: goalTargets[0].label }) }}</text>
              <view v-if="goalTargets[0].date" class="countdown"><text class="countdown-value app-number">{{ goalTargets[0].days }}</text><text class="countdown-unit">{{ t("天") }}</text></view>
              <button v-else class="target-link app-text-link" @click="goProfile">{{ t("设置考试日期") }} <t-icon name="chevron-right" size="24rpx" /></button>
              <text v-if="goalTargets[0].date" class="goal-date">{{ t("目标日期") }} {{ goalTargets[0].date }}</text>
            </template>
            <template v-else>
              <text class="goal-caption">{{ t("同时备考，两份目标一起前进") }}</text>
              <view class="goal-targets">
                <button v-for="target in goalTargets" :key="target.exam" class="goal-target" @click="goProfile">
                  <view><text class="goal-target-label">{{ target.label }}</text><text class="goal-date">{{ target.date || t("设置考试日期") }}</text></view>
                  <view v-if="target.date" class="goal-target-countdown"><text class="app-number">{{ target.days }}</text><text>{{ t("天") }}</text></view>
                  <t-icon v-else name="chevron-right" size="24rpx" />
                </button>
              </view>
            </template>
          </view>
          <view class="calendar-art" aria-hidden="true">
            <view class="calendar-binding"><view></view><view></view></view>
            <view class="calendar-grid"><view v-for="day in 9" :key="day" :class="{ 'calendar-day--active': day === 5 }"></view></view>
            <view class="calendar-check"><t-icon name="check" size="28rpx" color="#fffaf3" /></view>
          </view>
        </view>
        <t-button theme="primary" block size="large" @click="goPrimaryAction"><view class="primary-action-inner"><text>{{ examStore.hasActiveProgress ? t("继续上次答题") : t("开始今日练习") }}</text><t-icon name="chevron-right" size="28rpx" /></view></t-button>
        <view v-if="examStore.hasActiveProgress" class="resume-progress">
          <text>{{ t('{exam} · 已完成 {done} / {total} 题', { exam: getExamLabel(examStore.config.examType), done: examStore.answeredCount, total: examStore.totalCount }) }}</text>
          <view class="resume-track"><view :style="{ width: examStore.progressPercent + '%' }"></view></view>
        </view>
        <text v-else class="goal-footer">{{ t("从一组练习开始，慢慢积累进步") }}</text>
      </view>
    </view>

    <view class="app-section">
      <view class="study-card app-card app-card-pad">
        <view class="app-section-head"><text class="app-card-title">{{ t("今日学习") }}</text><button class="plain-link" :aria-label="t('去刷题')" @click="goExam"><t-icon name="chevron-right" size="28rpx" /></button></view>
        <c-app-state v-if="studyLoading && !dashboard" compact state="loading" :title="t('正在整理学习数据')" />
        <c-app-state v-else-if="dashboardState.error.value" compact state="error" :title="t('学习数据暂时不可用')" :description="dashboardState.error.value" @retry="loadStudyData" />
        <view v-else class="metric-row">
          <view class="metric"><text class="metric-value app-number">{{ dashboard ? dashboard.todayStats.questionCount : '—' }}</text><text class="metric-label">{{ t("完成题数") }}</text></view>
          <view class="metric metric--sage"><text class="metric-value app-number">{{ dashboard && dashboard.todayStats.objectiveCount !== 0 ? dashboard.todayStats.correctRate + '%' : '—' }}</text><text class="metric-label">{{ t("正确率") }}</text></view>
          <view class="metric"><text class="metric-value app-number">{{ dashboard ? dashboard.pendingWrongCount : '—' }}</text><text class="metric-label">{{ t("待复习") }}</text></view>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="app-card app-card-pad">
        <view class="app-section-head"><text class="app-card-title">{{ t("学习工具") }}</text></view>
        <view class="tool-row">
          <button class="tool" @click="goWrongBook"><view class="tool-icon"><t-icon name="book" size="42rpx" /></view><text>{{ t("错题复习") }}</text></button>
          <button class="tool" @click="goFavorite"><view class="tool-icon"><t-icon name="star" size="42rpx" /></view><text>{{ t("我的收藏") }}</text></button>
          <button class="tool" @click="goHistory"><view class="tool-icon tool-icon--sage"><t-icon name="chart-bar" size="42rpx" /></view><text>{{ t("练习记录") }}</text></button>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="recent-card app-card">
        <view class="recent-heading"><text class="app-card-title">{{ t("最近练习") }}</text><button class="plain-link" :aria-label="t('全部练习记录')" @click="goHistory"><t-icon name="chevron-right" size="28rpx" /></button></view>
        <view v-if="recentPapers.length" class="recent-list">
          <button v-for="paper in recentPapers" :key="paper.id" class="recent-row" @click="goPaper(paper.id)">
            <view class="recent-icon"><t-icon name="file" size="32rpx" /></view>
            <view class="recent-copy"><text class="recent-title">{{ getPaperTitle(paper.title) }}</text><text class="recent-meta">{{ t('{n}题', { n: paper.questionCount }) }} · {{ paper.date }}</text></view>
            <text class="recent-score app-number">{{ paper.objectiveCount === 0 ? t("自评") : Math.round(paper.score) + '%' }}</text><t-icon name="chevron-right" size="24rpx" color="#857970" />
          </button>
        </view>
        <view v-else class="recent-empty"><text>{{ dashboardState.error.value ? t("连接恢复后，可查看最近练习") : t("完成第一组练习，记录每一次进步") }}</text></view>
      </view>
    </view>

    <view class="app-section">
      <view class="app-card app-card-pad">
        <view class="app-section-head"><text class="app-card-title">{{ t("留学资讯") }}</text><text class="preparing-label">{{ t("筹备中") }}</text></view>
        <view class="content-empty"><view class="content-icon"><t-icon name="file" size="38rpx" /></view><view><text class="content-title">{{ t("资讯栏目正在准备中") }}</text><text class="content-desc">{{ t("考试动态、申请提醒与学习资料") }}</text></view></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { t, language } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { computed, ref } from 'vue'
import { onShareAppMessage, onShareTimeline, onShow } from '@dcloudio/uni-app'
import { createAppShareMessage, createTimelineShareMessage, isTimelinePreview } from '@/constants/share'
import TimelinePreview from '@/components/TimelinePreview/index.vue'
import { getExamLabel, getPaperTitle } from '@/constants/exam'
import { useUserStore } from '@/stores/user'
import { useExamStore } from '@/stores/exam'
import { useHomePage } from '@/features/home/useHomePage'
import { useExamNavigation } from '@/features/exam/useExamNavigation'
import type { ExamType } from '@/types/exam'

usePageI18n('pages/index/index')

const userStore = useUserStore()
const examStore = useExamStore()
const { dashboardState, recentPapers, loadDashboard } = useHomePage()
const { goPractice } = useExamNavigation()
const examTabs: ExamType[] = ['HKS', 'CSCA']
const now = ref(Date.now())
const timelinePreview = ref(isTimelinePreview())
const studyLoading = ref(false)
const dashboard = computed(() => dashboardState.data.value)
const displayName = computed(() => dashboard.value?.userName || userStore.userInfo.nickname || '留学同学')
const greeting = computed(() => {
  const hour = new Date(now.value).getHours()
  return hour < 11 ? '早上好' : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好'
})
function daysRemaining(date: string) {
  if (!date) return 0
  const [year, month, day] = date.split('-').map(Number)
  const today = new Date(now.value)
  const midnight = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
  return Math.max(0, Math.ceil((new Date(year, month - 1, day).getTime() - midnight) / 86400000))
}
const goalTargets = computed(() => examTabs.filter((exam) => userStore.selectedExams.includes(exam)).map((exam) => {
  const date = dashboard.value?.targetDates[exam] || userStore.userInfo.targetDates[exam] || ''
  return { exam, label: getExamLabel(exam), date, days: daysRemaining(date) }
}))

async function loadStudyData() {
  if (timelinePreview.value || studyLoading.value) return
  studyLoading.value = true
  dashboardState.error.value = ''
  try {
    await userStore.login()
    await loadDashboard(true)
  } catch {
    dashboardState.error.value = '暂时无法连接，请稍后重试'
  } finally {
    studyLoading.value = false
  }
}

const goExam = () => uni.switchTab({ url: '/pages/exam/index' })
const goProfile = () => uni.switchTab({ url: '/pages/profile/index' })
const goWrongBook = () => uni.navigateTo({ url: '/pages/wrongbook/index' })
const goFavorite = () => uni.navigateTo({ url: '/pages/favorite/index' })
const goHistory = () => uni.navigateTo({ url: '/pages/exam/history' })
const goPaper = (id: number) => uni.navigateTo({ url: '/pages/exam/result?id=' + id })
const goPrimaryAction = () => {
  if (examStore.hasActiveProgress) uni.navigateTo({ url: '/pages/exam/answer' })
  else goPractice('random')
}

onShow(() => {
  timelinePreview.value = isTimelinePreview()
  if (timelinePreview.value) return
  // #ifdef MP-WEIXIN
  uni.showShareMenu({ menus: ['shareAppMessage', 'shareTimeline'] })
  // #endif
  now.value = Date.now()
  loadStudyData()
})
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
onShareTimeline(createTimelineShareMessage)
// #endif
</script>

<style lang="scss" scoped>
.home-page { padding-bottom: calc(36rpx + env(safe-area-inset-bottom)); }
.primary-action-inner { display: flex; align-items: center; justify-content: center; gap: 12rpx; }
.home-page button { border: 0; }
.home-page button::after { border: 0; }
.home-header { padding: 30rpx 28rpx 0; display: flex; align-items: center; flex-wrap: wrap; gap: 18rpx; }
.home-greeting { flex: 1; min-width: 300rpx; }
.greeting-title { display: block; color: var(--app-text); font-size: 36rpx; line-height: 1.4; font-weight: 600; overflow-wrap: anywhere; }
.greeting-desc { display: block; margin-top: 8rpx; color: var(--app-text-weak); font-size: 24rpx; }
.goal-section { margin-top: 26rpx; }
.goal-top { display: flex; align-items: center; justify-content: space-between; gap: 24rpx; min-height: 206rpx; margin-bottom: 24rpx; }
.goal-copy { flex: 1; min-width: 0; }
.goal-label { display: block; font-size: 28rpx; font-weight: 600; }
.goal-caption { display: block; margin-top: 10rpx; color: var(--app-text-weak); font-size: 24rpx; }
.countdown { display: flex; align-items: baseline; gap: 12rpx; }
.countdown-value { color: var(--app-primary); font-size: 92rpx; line-height: 1.2; }
.countdown-unit { color: var(--app-text-weak); font-size: 30rpx; }
.goal-date { display: block; color: var(--app-text-mute); font-size: 20rpx; }
.browse-note { display: block; margin-top: 18rpx; color: var(--app-text-mute); font-size: 22rpx; line-height: 1.7; }
.goal-targets { display: flex; flex-direction: column; gap: 10rpx; margin-top: 14rpx; }
.goal-target { display: flex; align-items: center; justify-content: space-between; gap: 12rpx; width: 100%; margin: 0; padding: 10rpx 14rpx; background: var(--app-surface-quiet); border-radius: var(--app-radius-sm); color: var(--app-primary); text-align: left; line-height: 1.4; }
.goal-target-label { display: block; color: var(--app-text); font-size: 23rpx; font-weight: 600; }
.goal-target-countdown { display: flex; align-items: baseline; gap: 6rpx; flex: none; font-size: 20rpx; }
.goal-target-countdown .app-number { font-size: 38rpx; }
.target-link { margin: 16rpx 0 0; padding: 0; background: transparent; text-align: left; min-height: 56rpx; }
.calendar-art { position: relative; width: 138rpx; height: 126rpx; flex: none; margin-right: 16rpx; border-radius: 18rpx; background: var(--app-primary-soft); border-top: 28rpx solid #ebccb7; }
.calendar-binding { position: absolute; display: flex; justify-content: space-around; width: 100%; top: -40rpx; }
.calendar-binding view { width: 9rpx; height: 32rpx; border-radius: 6rpx; background: var(--app-primary); }
.calendar-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8rpx; padding: 18rpx; }
.calendar-grid view { height: 15rpx; border-radius: 3rpx; background: #e6cbb8; }
.calendar-grid .calendar-day--active { background: var(--app-primary); }
.calendar-check { position: absolute; right: -18rpx; bottom: -10rpx; width: 48rpx; height: 48rpx; border: 4rpx solid var(--app-surface); border-radius: 50%; background: var(--app-secondary); display: flex; align-items: center; justify-content: center; }
.resume-progress { display: flex; align-items: center; gap: 20rpx; margin-top: 14rpx; color: var(--app-text-weak); font-size: 21rpx; }
.resume-track { height: 10rpx; flex: 1; border-radius: 999px; background: var(--app-border); overflow: hidden; }
.resume-track view { height: 100%; background: var(--app-primary); border-radius: 999px; }
.goal-footer { display: block; margin-top: 14rpx; color: var(--app-text-mute); font-size: 21rpx; text-align: center; }
.plain-link { display: flex; align-items: center; justify-content: center; margin: -8rpx -8rpx -8rpx 0; padding: 8rpx; min-width: 52rpx; min-height: 52rpx; color: var(--app-text-weak); background: transparent; }
.metric-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.metric { text-align: center; border-left: 1rpx solid var(--app-border); }
.metric:first-child { border: 0; }
.metric-value { display: block; font-size: 48rpx; line-height: 1.2; color: var(--app-primary); }
.metric--sage .metric-value { color: var(--app-success); }
.metric-label { display: block; margin-top: 8rpx; font-size: 24rpx; color: var(--app-text-weak); }
.tool-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16rpx; }
.tool { margin: 0; padding: 0; background: transparent; color: var(--app-text); font-size: 24rpx; line-height: 1.5; }
.tool-icon { display: flex; align-items: center; justify-content: center; width: 112rpx; height: 80rpx; margin: 0 auto 14rpx; border-radius: var(--app-radius-md); background: var(--app-surface-quiet); color: var(--app-primary); }
.tool-icon--sage { color: var(--app-success); background: var(--app-secondary-soft); }
.recent-heading { display: flex; align-items: center; justify-content: space-between; padding: 22rpx 26rpx; }
.recent-row { display: flex; align-items: center; gap: 16rpx; width: 100%; margin: 0; padding: 22rpx 26rpx; background: transparent; border-top: 1rpx solid var(--app-border); text-align: left; line-height: 1.5; }
.recent-icon { display: flex; align-items: center; justify-content: center; width: 60rpx; height: 66rpx; flex: none; border-radius: 14rpx; color: var(--app-success); background: var(--app-secondary-soft); }
.recent-copy { flex: 1; min-width: 0; }
.recent-title { display: block; font-size: 26rpx; font-weight: 500; color: var(--app-text); }
.recent-meta { display: block; margin-top: 5rpx; font-size: 22rpx; color: var(--app-text-weak); }
.recent-score { flex: none; color: var(--app-primary); font-size: 34rpx; }
.recent-empty { padding: 0 26rpx 26rpx; color: var(--app-text-weak); font-size: 24rpx; line-height: 1.6; }
.preparing-label { color: var(--app-text-mute); font-size: 21rpx; }
.content-empty { display: flex; align-items: center; gap: 20rpx; padding: 22rpx; border-radius: var(--app-radius-md); background: var(--app-surface-quiet); }
.content-icon { color: var(--app-text-mute); flex: none; }
.content-title { display: block; font-size: 24rpx; }
.content-desc { display: block; margin-top: 6rpx; color: var(--app-text-mute); font-size: 22rpx; line-height: 1.5; }
</style>

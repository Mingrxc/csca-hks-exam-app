<template>
  <TimelinePreview v-if="timelinePreview" />
  <view v-else class="home-page app-shell">
    <view class="home-header">
      <view class="home-greeting">
        <text class="greeting-title">{{ t(greeting) }}{{ language === 'en' ? ', ' : '，' }}{{ displayName }}</text>
      </view>
    </view>

    <view class="app-section check-in-section">
      <view class="check-in-card app-card app-card-pad">
        <view class="check-in-heading">
          <text class="check-in-streak">{{ t('连续学习 {n} 天', { n: streakDays }) }}</text>
          <button class="check-in-button" :class="{ 'check-in-button--done': checkedIn }"
            :disabled="checkInState.loading.value || checkedIn" @click="handleCheckIn">
            <t-icon :name="checkedIn ? 'check' : 'calendar'" size="32rpx" />
            <text>{{ checkInState.loading.value ? t('签到中') : checkedIn ? t('已签到') : t('签到') }}</text>
          </button>
        </view>
        <view class="check-in-week">
          <view v-for="(day, index) in checkInWeek" :key="day.date" class="check-in-day"
            :class="{ 'check-in-day--done': day.checked, 'check-in-day--today': day.date === checkInToday, 'check-in-day--future': day.date > checkInToday }"
            :aria-label="day.date + ' · ' + t(day.checked ? '已打卡' : checkInStatus || !userStore.isLogin ? '未打卡' : '签到数据暂不可用')">
            <text class="check-in-weekday">{{ t(weekdays[index]) }}</text>
            <view class="check-in-mark"><t-icon v-if="day.checked" name="check" size="30rpx" /><text v-else>{{ Number(day.date.slice(8)) }}</text></view>
          </view>
        </view>
        <text v-if="checkInState.error.value" class="check-in-error">{{ t('签到失败，请重试') }}</text>
        <t-button theme="primary" block size="large" @click="goPrimaryAction"><view class="primary-action-inner"><text>{{ examStore.hasActiveProgress ? t("继续上次答题") : t("开始今日练习") }}</text><t-icon name="chevron-right" size="28rpx" /></view></t-button>
        <view v-if="examStore.hasActiveProgress" class="resume-progress">
          <text>{{ t('{exam} · 已完成 {done} / {total} 题', { exam: getExamLabel(examStore.config.examType), done: examStore.answeredCount, total: examStore.totalCount }) }}</text>
          <view class="resume-track"><view :style="{ width: examStore.progressPercent + '%' }"></view></view>
        </view>
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
        <view v-else class="recent-empty"><text>{{ dashboardState.error.value ? t("连接恢复后，可查看最近练习") : t("暂无练习记录") }}</text></view>
      </view>
    </view>

    <view class="app-section">
      <view class="app-card app-card-pad">
        <view class="app-section-head"><text class="app-card-title">{{ t("留学资讯") }}</text><text class="preparing-label">{{ t("筹备中") }}</text></view>
        <view class="content-empty"><view class="content-icon"><t-icon name="file" size="38rpx" /></view><view><text class="content-title">{{ t("资讯栏目正在准备中") }}</text></view></view>
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
import { beijingDate, emptyCheckInWeek } from '@/features/home/checkInCalendar'
import { useExamNavigation } from '@/features/exam/useExamNavigation'
import { navigateProtected, requireLogin } from '@/shared/auth/navigation'

usePageI18n('pages/index/index')

const userStore = useUserStore()
const examStore = useExamStore()
const { dashboardState, checkInState, recentPapers, loadDashboard, checkIn } = useHomePage()
const { goPractice } = useExamNavigation()
const now = ref(Date.now())
const timelinePreview = ref(isTimelinePreview())
const studyLoading = ref(false)
const dashboard = computed(() => dashboardState.data.value)
const displayName = computed(() => userStore.isLogin ? userStore.userInfo.nickname : t('留学同学'))
const greeting = computed(() => {
  const hour = new Date(now.value).getHours()
  return hour < 11 ? '早上好' : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好'
})
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const checkInStatus = computed(() => userStore.isLogin ? checkInState.data.value : null)
const checkInToday = computed(() => checkInStatus.value?.today || beijingDate(now.value))
const checkInWeek = computed(() => checkInStatus.value?.week || emptyCheckInWeek(now.value))
const checkedIn = computed(() => !!checkInStatus.value?.checkedIn)
const streakDays = computed(() => !userStore.isLogin ? 0 : checkInStatus.value?.streakDays ?? '—')

async function handleCheckIn() {
  if (checkInState.loading.value || checkedIn.value) return
  if (!await requireLogin(handleCheckIn)) return
  const result = await checkIn()
  if (result) {
    userStore.userInfo.streakDays = result.streakDays
    uni.showToast({ title: t('签到成功'), icon: 'success' })
  }
}

async function loadStudyData() {
  if (timelinePreview.value || studyLoading.value) return
  studyLoading.value = true
  dashboardState.error.value = ''
  try {
    await userStore.restoreSession()
    await loadDashboard(userStore.isLogin)
  } catch {
    dashboardState.error.value = '暂时无法连接，请稍后重试'
  } finally {
    studyLoading.value = false
  }
}

const goExam = () => uni.switchTab({ url: '/pages/exam/index' })
const goWrongBook = () => navigateProtected('/pages/wrongbook/index')
const goFavorite = () => navigateProtected('/pages/favorite/index')
const goHistory = () => navigateProtected('/pages/exam/history')
const goPaper = (id: number) => navigateProtected('/pages/exam/result?id=' + id)
const goPrimaryAction = () => {
  if (examStore.hasActiveProgress) navigateProtected('/pages/exam/answer')
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
.check-in-section { margin-top: 26rpx; }
.check-in-heading { display: flex; align-items: center; justify-content: space-between; gap: 18rpx; }
.check-in-streak { flex: 1; min-width: 0; font-size: 34rpx; line-height: 1.4; font-weight: 600; }
.check-in-button { display: flex; align-items: center; justify-content: center; flex: none; gap: 8rpx; min-width: 140rpx; margin: 0; padding: 18rpx 20rpx; border-radius: var(--app-radius-md); background: var(--app-primary); color: var(--app-surface); font-size: 25rpx; line-height: 1.4; }
.check-in-button[disabled] { background: var(--app-primary-soft); color: var(--app-primary); }
.check-in-button--done[disabled] { background: var(--app-secondary-soft); color: var(--app-success); }
.check-in-week { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 10rpx; margin: 30rpx 0; }
.check-in-day { display: flex; flex-direction: column; align-items: center; gap: 12rpx; color: var(--app-text-weak); }
.check-in-weekday { font-size: 21rpx; line-height: 1.5; }
.check-in-mark { display: flex; align-items: center; justify-content: center; width: 60rpx; height: 60rpx; box-sizing: border-box; border: 2rpx solid transparent; border-radius: 50%; background: var(--app-surface-quiet); font-size: 25rpx; }
.check-in-day--today .check-in-weekday { color: var(--app-primary); font-weight: 600; }
.check-in-day--today .check-in-mark { border-color: var(--app-primary); }
.check-in-day--done .check-in-mark { background: var(--app-secondary-soft); color: var(--app-success); }
.check-in-day--future .check-in-mark { color: var(--app-text-mute); background: transparent; }
.check-in-error { display: block; margin: -10rpx 0 20rpx; color: var(--app-danger); font-size: 24rpx; }
.resume-progress { display: flex; align-items: center; gap: 20rpx; margin-top: 14rpx; color: var(--app-text-weak); font-size: 21rpx; }
.resume-track { height: 10rpx; flex: 1; border-radius: 999px; background: var(--app-border); overflow: hidden; }
.resume-track view { height: 100%; background: var(--app-primary); border-radius: 999px; }
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
</style>

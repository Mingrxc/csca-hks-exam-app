<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="profile-card app-card app-card-pad">
        <view class="profile-top">
          <t-avatar v-if="userInfo.avatarUrl" class="profile-avatar" :image="userInfo.avatarUrl" size="112rpx" shape="circle" />
          <view v-else class="profile-avatar-fallback">{{ userInfo.nickname.slice(0, 1) }}</view>
          <view class="profile-copy">
            <text class="profile-name">{{ userInfo.nickname }}</text>
            <view class="profile-meta">
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
              <t-tag v-if="!selectedExamLabels.length" theme="default" variant="light" shape="round" size="small">
                随便看看
              </t-tag>
              <t-tag v-if="userInfo.targetDate && !selectedExamLabels.length" theme="warning" variant="light" shape="round" size="small">
                {{ userInfo.targetDate }}
              </t-tag>
            </view>
          </view>
        </view>

        <view class="profile-actions">
          <t-button class="profile-action" theme="primary" variant="outline" size="small" shape="round" open-type="chooseAvatar" @chooseavatar="chooseAvatar">
            更换头像
          </t-button>
          <t-button class="profile-action" theme="default" variant="outline" size="small" shape="round" @click="editNickname">
            修改昵称
          </t-button>
        </view>
      </view>
    </view>

    <view class="app-section" v-if="loadError">
      <view class="app-card"><c-app-state compact state="error" title="个人资料暂时无法加载" description="请检查网络连接后重试。" @retry="loadAll" /></view>
    </view>

    <view class="app-section">
      <c-app-state v-if="isLoading" compact state="loading" title="正在整理学习记录" />
      <view v-else class="stats-grid">
        <view class="stat-card app-card">
          <text class="stat-value">{{ profileLoaded ? userInfo.totalQuestions : '—' }}</text>
          <text class="stat-label">累计刷题数</text>
        </view>
        <view class="stat-card app-card">
          <text class="stat-value">{{ profileLoaded && userInfo.objectiveCount !== 0 ? userInfo.correctRate + '%' : '—' }}</text>
          <text class="stat-label">正确率</text>
        </view>
        <view class="stat-card app-card">
          <text class="stat-value">{{ profileLoaded ? userInfo.streakDays : '—' }}</text>
          <text class="stat-label">连续学习天数</text>
        </view>
        <view class="stat-card app-card">
          <text class="stat-value">{{ dashboardLoaded ? dashboard.pendingWrongCount : '—' }}</text>
          <text class="stat-label">错题数量</text>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="target-card app-card app-card-pad">
        <view class="target-head">
          <text class="app-section-title">目标设置</text>
        </view>

        <view class="target-mode">
          <view class="mode-chip" :class="{ active: targetDraftExams.length === 0 }" @click="setBrowseMode">
            随便看看
          </view>
          <view class="mode-chip" :class="{ active: targetDraftExams.includes('CSCA') }" @click="toggleDraftExam('CSCA')">
            CSCA
          </view>
          <view class="mode-chip" :class="{ active: targetDraftExams.includes('HKS') }" @click="toggleDraftExam('HKS')">HSK</view>
        </view>

        <view v-if="targetDraftExams.length > 0" class="target-dates">
          <view v-for="exam in targetDraftExams" :key="exam" class="target-date-row">
            <text class="target-date-label">{{ getExamLabel(exam) }} 考试日期</text>
            <picker mode="date" :value="targetDraftDates[exam]" :start="today" @change="selectTargetDate(exam, $event)">
              <view class="date-picker">{{ targetDraftDates[exam] || '选择考试日期' }}</view>
            </picker>
          </view>
        </view>

        <t-button theme="primary" block shape="round" :loading="savingTarget" @click="saveTarget">保存目标</t-button>
      </view>
    </view>

    <view class="app-section">
      <view class="menu-grid">
        <view class="menu-card app-card" @click="goPage('/pages/feedback/index')">
          <view class="menu-head">
            <view class="app-icon-badge"><t-icon name="chat" size="28rpx" /></view>
          </view>
          <text class="app-card-title">用户反馈</text>
        </view>
        <view class="menu-card app-card" @click="showAbout">
          <view class="menu-head">
            <view class="app-icon-badge"><t-icon name="info-circle" size="28rpx" /></view>
          </view>
          <text class="app-card-title">关于</text>
        </view>
        <view class="menu-card app-card danger" @click="handleLogout">
          <view class="menu-head">
            <view class="app-icon-badge"><t-icon name="poweroff" size="28rpx" /></view>
          </view>
          <text class="app-card-title">退出登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { getExamLabel } from '@/constants/exam'
import { computed, reactive, ref } from 'vue'
import { onShareAppMessage, onShow } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import { userApi } from '@/features/user/api'
import { toDashboardData, toUserProfile } from '@/api/contracts'
import { useUserStore } from '@/stores/user'
import type { DashboardData, UserProfile } from '@/types/user'
import type { ExamType } from '@/types/exam'

const userStore = useUserStore()
const userInfo = ref<UserProfile>({
  nickname: '留学同学',
  avatarUrl: '',
  targetExam: 'CSCA',
  targetDate: '',
  targetDates: {},
  totalQuestions: 0,
  correctRate: 0,
  streakDays: 0,
  favoriteCount: 0,
})
const dashboard = reactive<DashboardData>({
  userName: '留学同学',
  targetExam: 'CSCA',
  targetDate: '',
  targetDates: {},
  countdown: { days: '0', hours: '00', minutes: '00' },
  todayStats: { questionCount: 0, correctRate: 0, wrongCount: 0 },
  pendingWrongCount: 0,
  favoriteCount: 0,
  recentPapers: [],
})
const loadError = ref(false)
const isLoading = ref(false)
const profileLoaded = ref(false)
const dashboardLoaded = ref(false)
const targetDraftExams = ref<ExamType[]>([...userStore.selectedExams])
const targetDraftDates = reactive<Record<ExamType, string>>({ CSCA: '', HKS: '' })
const savingTarget = ref(false)
const now = new Date()
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

const selectedExamLabels = computed(() =>
  targetDraftExams.value.map((exam) => ({
    value: exam,
    label: getExamLabel(exam),
    theme: exam === 'CSCA' ? ('primary' as const) : ('warning' as const),
  })),
)

const loadProfile = async () => {
  try {
    userInfo.value = toUserProfile(await userApi.getUserInfo())
    profileLoaded.value = true
    targetDraftDates.CSCA = userInfo.value.targetDates.CSCA || ''
    targetDraftDates.HKS = userInfo.value.targetDates.HKS || ''
    targetDraftExams.value = [...userStore.selectedExams]
  } catch {
    loadError.value = true
  }
}

const loadDashboard = async () => {
  try {
    Object.assign(dashboard, toDashboardData(await userApi.getDashboard()))
    dashboardLoaded.value = true
  } catch {
    loadError.value = true
  }
}

const loadAll = async () => {
  if (isLoading.value) return
  isLoading.value = true
  loadError.value = false
  await Promise.all([loadProfile(), loadDashboard()])
  isLoading.value = false
}

const selectTargetDate = (exam: ExamType, event: any) => {
  targetDraftDates[exam] = event.detail.value
}

const toggleDraftExam = (exam: ExamType) => {
  const index = targetDraftExams.value.indexOf(exam)
  if (index >= 0) {
    targetDraftExams.value.splice(index, 1)
  } else if (targetDraftExams.value.length < 2) {
    targetDraftExams.value.push(exam)
  }
  if (targetDraftExams.value.length === 0) {
    userStore.setBrowseMode()
  } else {
    userStore.setSelectedExams(targetDraftExams.value)
  }
}

const setBrowseMode = () => {
  targetDraftExams.value = []
  targetDraftDates.CSCA = ''
  targetDraftDates.HKS = ''
  userStore.setBrowseMode()
}

const saveTarget = async () => {
  const missingExam = targetDraftExams.value.find((exam) => !targetDraftDates[exam])
  if (missingExam) {
    uni.showToast({ title: `请选择 ${getExamLabel(missingExam)} 考试日期`, icon: 'none' })
    return
  }
  savingTarget.value = true
  try {
    const primaryExam = targetDraftExams.value[0] || userInfo.value.targetExam
    const targetDates: Record<ExamType, string | null> = {
      CSCA: targetDraftExams.value.includes('CSCA') ? targetDraftDates.CSCA || null : null,
      HKS: targetDraftExams.value.includes('HKS') ? targetDraftDates.HKS || null : null,
    }
    const payload: Record<string, unknown> = {
      target_exam: primaryExam,
      target_date: targetDates[primaryExam],
      target_dates: targetDates,
    }
    const updated = await userApi.updateProfile(payload)
    userInfo.value = toUserProfile(updated)
    targetDraftDates.CSCA = userInfo.value.targetDates.CSCA || ''
    targetDraftDates.HKS = userInfo.value.targetDates.HKS || ''
    dashboard.targetExam = updated.target_exam
    dashboard.targetDate = updated.target_date || ''
    uni.showToast({ title: '目标已更新', icon: 'success' })
  } catch {
    // request layer handles toast
  } finally {
    savingTarget.value = false
  }
}

const chooseAvatar = async (event: any) => {
  const avatarUrl = event.detail?.avatarUrl
  if (!avatarUrl) return
  try {
    const updated = await userApi.updateProfile({ avatar_url: avatarUrl })
    userInfo.value = toUserProfile(updated)
    uni.showToast({ title: '头像已更新', icon: 'success' })
  } catch {}
}

const editNickname = () => {
  uni.showModal({
    title: '修改昵称',
    editable: true,
    placeholderText: '输入昵称',
    content: userInfo.value.nickname,
    success: async (result: any) => {
      const nickname = String(result.content || '').trim()
      if (!result.confirm || !nickname || nickname === userInfo.value.nickname) return
      try {
        const updated = await userApi.updateProfile({ nickname })
        userInfo.value = toUserProfile(updated)
      } catch {}
    },
  })
}

const showAbout = () => {
  uni.navigateTo({ url: '/pages/about/index' })
}

const goPage = (url: string) => {
  if (url === '/pages/exam/index') {
    uni.switchTab({ url })
  } else {
    uni.navigateTo({ url })
  }
}

const goRedo = () => {
  const examType = targetDraftExams.value[0] || userInfo.value.targetExam
  uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${examType}` })
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '退出后需要重新登录，确定退出吗？',
    success: (res: any) => {
      if (res.confirm) {
        userStore.logout()
        userInfo.value = {
          nickname: '留学同学',
          avatarUrl: '',
          targetExam: 'CSCA',
          targetDate: '',
          targetDates: {},
          totalQuestions: 0,
          correctRate: 0,
          streakDays: 0,
          favoriteCount: 0,
        }
        targetDraftExams.value = []
        profileLoaded.value = false
        dashboardLoaded.value = false
        loadError.value = false
        uni.showToast({ title: '已退出登录', icon: 'success' })
      }
    },
  })
}

onShow(async () => {
  targetDraftExams.value = [...userStore.selectedExams]
  await loadAll()
})
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
// #endif
</script>

<style lang="scss" scoped>
.profile-card {
  background: var(--app-surface);
}

.profile-top {
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.profile-avatar {
  flex: none;
}

.profile-avatar-fallback {
  width: 112rpx;
  height: 112rpx;
  border-radius: 999px;
  background: var(--app-primary-soft);
  color: var(--app-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 600;
  flex: none;
}

.profile-copy {
  flex: 1;
  min-width: 0;
}

.profile-name {
  display: block;
  font-size: 36rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10rpx 12rpx;
  margin-top: 10rpx;
}

.profile-actions {
  display: flex;
  gap: 12rpx;
  margin-top: 18rpx;
}

.profile-action {
  flex: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 124rpx;
  padding: 20rpx 16rpx;
  text-align: center;
  background: var(--app-surface);
  border: 1rpx solid var(--app-border);
  border-radius: var(--app-radius-lg);
  box-shadow: var(--app-shadow-sm);
}

.stat-value {
  display: block;
  font-size: 42rpx;
  font-family: var(--app-number-font);
  line-height: 1.1;
  font-weight: 600;
  color: var(--app-text);
}

.stat-label {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.target-head {
  margin-bottom: 14rpx;
}

.target-mode {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10rpx;
  margin-bottom: 16rpx;
}

.mode-chip {
  padding: 14rpx 0;
  border-radius: 999px;
  background: var(--app-surface-quiet);
  color: var(--app-text-weak);
  font-size: 24rpx;
  text-align: center;
}

.mode-chip.active {
  background: var(--app-primary-soft);
  color: var(--app-primary);
  font-weight: 600;
}

.target-dates {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.target-date-row {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.target-date-label {
  font-size: 22rpx;
  line-height: 1.4;
  color: var(--app-text-weak);
}

.date-picker {
  margin-bottom: 16rpx;
  padding: 18rpx 20rpx;
  border: 1rpx solid var(--app-border);
  border-radius: var(--app-radius-md);
  color: var(--app-text);
  font-size: 24rpx;
  background: var(--app-surface);
}

.target-date-row .date-picker {
  margin-bottom: 0;
}

.menu-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 14rpx;
}

.menu-card {
  display: flex;
  align-items: center;
  gap: 14rpx;
  min-height: 88rpx;
  padding: 14rpx 22rpx;
  border-radius: var(--app-radius-lg);
  background: var(--app-surface);
  border: 1rpx solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
}

.menu-card.danger .app-card-title {
  color: var(--app-danger);
}

.menu-head {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 10rpx;
  flex: none;
  margin-bottom: 0;
}

.error-card {
  padding: 24rpx;
  text-align: center;
  color: var(--app-danger);
  background: var(--app-danger-soft);
}
</style>

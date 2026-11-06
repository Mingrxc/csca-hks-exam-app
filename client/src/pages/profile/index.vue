<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="profile-card app-card app-card-pad">
        <view class="profile-top" @tap="loginFromProfile">
          <t-avatar v-if="userStore.isLogin && userInfo.avatarUrl" class="profile-avatar" :image="userInfo.avatarUrl" size="112rpx" shape="circle" />
          <view v-else class="profile-avatar-fallback"><t-icon name="user-circle" size="64rpx" /></view>
          <view class="profile-copy">
            <view class="profile-name-row">
              <input v-if="editingNickname" class="profile-name-input" type="nickname" :value="nicknameDraft"
                :focus="nicknameFocused" :disabled="savingNickname" maxlength="64" confirm-type="done"
                :placeholder="t('输入昵称，或选择微信昵称')" :aria-label="t('昵称')"
                @input="onNicknameInput" @blur="onNicknameBlur" @confirm="confirmNickname" @nicknamereview="reviewNickname" />
              <text v-else class="profile-name">{{ userStore.isLogin ? userInfo.nickname : t('未登录') }}</text>
              <text v-if="userStore.isLogin" class="profile-code" @tap.stop="copyUserCode">{{ userInfo.userCode }}</text>
            </view>
            <text v-if="editingNickname && nicknameError" class="nickname-hint nickname-hint-error">
              {{ nicknameError }}
            </text>
            <text v-if="!userStore.isLogin" class="login-link">{{ t('点击登录') }}</text>
            <view class="profile-meta">
              <t-tag
                v-for="item in selectedExamLabels"
                :key="item.value"
                :theme="item.theme"
                variant="light"
                shape="round"
                size="small"
              >
                {{ t(item.label) }}
              </t-tag>
              <t-tag v-if="!selectedExamLabels.length" theme="default" variant="light" shape="round" size="small">
                {{ t("随便看看") }}
              </t-tag>
              <t-tag v-if="userInfo.targetDate && !selectedExamLabels.length" theme="warning" variant="light" shape="round" size="small">
                {{ userInfo.targetDate }}
              </t-tag>
            </view>
          </view>
        </view>

        <view v-if="userStore.isLogin" class="profile-actions">
          <template v-if="editingNickname">
            <t-button class="profile-action" theme="default" variant="outline" size="small" shape="round" :disabled="savingNickname" @click="cancelNicknameEdit">
              {{ t('取消') }}
            </t-button>
            <t-button class="profile-action" theme="primary" size="small" shape="round" :loading="savingNickname" :disabled="!canSaveNickname" @click="saveNickname">
              {{ t('保存昵称') }}
            </t-button>
          </template>
          <template v-else>
          <t-button class="profile-action" theme="primary" variant="outline" size="small" shape="round" open-type="chooseAvatar" @chooseavatar="chooseAvatar">
            {{ t("更换头像") }}
          </t-button>
          <t-button class="profile-action" theme="default" variant="outline" size="small" shape="round" @click="editNickname">
            {{ t("修改昵称") }}
          </t-button>
          </template>
        </view>
      </view>
    </view>

    <view class="app-section" v-if="loadError">
      <view class="app-card"><c-app-state compact state="error" :title="t('个人资料暂时无法加载')" :description="t('请检查网络连接后重试。')" @retry="loadAll" /></view>
    </view>

    <view class="app-section">
      <c-app-state v-if="isLoading" compact state="loading" :title="t('正在整理学习记录')" />
      <view v-else class="stats-grid">
        <view class="stat-card app-card">
          <text class="stat-value">{{ profileLoaded ? userInfo.totalQuestions : '—' }}</text>
          <text class="stat-label">{{ t("累计刷题数") }}</text>
        </view>
        <view class="stat-card app-card">
          <text class="stat-value">{{ profileLoaded && userInfo.objectiveCount !== 0 ? userInfo.correctRate + '%' : '—' }}</text>
          <text class="stat-label">{{ t("正确率") }}</text>
        </view>
        <view class="stat-card app-card">
          <text class="stat-value">{{ profileLoaded ? userInfo.streakDays : '—' }}</text>
          <text class="stat-label">{{ t("连续学习天数") }}</text>
        </view>
        <view class="stat-card app-card">
          <text class="stat-value">{{ dashboardLoaded ? dashboard.pendingWrongCount : '—' }}</text>
          <text class="stat-label">{{ t("错题数量") }}</text>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="target-card app-card app-card-pad">
        <view class="target-head">
          <text class="app-section-title">{{ t("目标设置") }}</text>
        </view>

        <view class="target-mode">
          <view class="mode-chip" :class="{ active: targetDraftExams.length === 0 }" @click="setBrowseMode">
            {{ t("随便看看") }}
          </view>
          <view class="mode-chip" :class="{ active: targetDraftExams.includes('CSCA') }" @click="toggleDraftExam('CSCA')">
            CSCA
          </view>
          <view class="mode-chip" :class="{ active: targetDraftExams.includes('HKS') }" @click="toggleDraftExam('HKS')">HSK</view>
        </view>

        <view v-if="userStore.isLogin && targetDraftExams.length > 0" class="target-dates">
          <view v-for="exam in targetDraftExams" :key="exam" class="target-date-row">
            <text class="target-date-label">{{ t('{exam} 考试日期', { exam: getExamLabel(exam) }) }}</text>
            <picker mode="date" :value="targetDraftDates[exam]" :start="today" @change="selectTargetDate(exam, $event)">
              <view class="date-picker">{{ targetDraftDates[exam] || t("选择考试日期") }}</view>
            </picker>
          </view>
        </view>

        <t-button theme="primary" block shape="round" :loading="savingTarget" @click="saveTarget">{{ t("保存目标") }}</t-button>
      </view>
    </view>

    <view class="app-section">
      <view class="language-card app-card">
        <text class="app-card-title">语言 / Language</text>
        <view class="language-options">
          <button class="language-option" :class="{ active: language === 'zh' }" :aria-pressed="language === 'zh'" @tap="setLanguage('zh')">简体中文</button>
          <button class="language-option" :class="{ active: language === 'en' }" :aria-pressed="language === 'en'" @tap="setLanguage('en')">English</button>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="menu-grid">
        <view v-if="userStore.isAdmin" class="menu-card app-card" @click="goPage('/pages/admin/index')">
          <view class="menu-head"><view class="app-icon-badge"><t-icon name="setting" size="28rpx" /></view></view>
          <text class="app-card-title">{{ t('管理中心') }}</text>
        </view>
        <view class="menu-card app-card" @click="goPage('/pages/feedback/index')">
          <view class="menu-head">
            <view class="app-icon-badge"><t-icon name="chat" size="28rpx" /></view>
          </view>
          <text class="app-card-title">{{ t("用户反馈") }}</text>
        </view>
        <view class="menu-card app-card" @click="showAbout">
          <view class="menu-head">
            <view class="app-icon-badge"><t-icon name="info-circle" size="28rpx" /></view>
          </view>
          <text class="app-card-title">{{ t("关于") }}</text>
        </view>
        <view v-if="userStore.isLogin" class="menu-card app-card danger" @click="handleLogout">
          <view class="menu-head">
            <view class="app-icon-badge"><t-icon name="poweroff" size="28rpx" /></view>
          </view>
          <text class="app-card-title">{{ t("退出登录") }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { showToast, showModal } from '@/i18n/ui'
import { errorText, t, language, setLanguage } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { getExamLabel } from '@/constants/exam'
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { activeUserId, sessionGeneration } from '@/shared/auth/session'
import { openLogin, navigateProtected, requireLogin } from '@/shared/auth/navigation'
import { onShareAppMessage, onShow } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import { userApi } from '@/features/user/api'
import { toDashboardData } from '@/api/contracts'
import { useUserStore } from '@/stores/user'
import type { DashboardData } from '@/types/user'
import type { ExamType } from '@/types/exam'

usePageI18n('pages/profile/index')

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)
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
const editingNickname = ref(false)
const nicknameDraft = ref('')
const nicknameFocused = ref(false)
const nicknameAllowed = ref(true)
const savingNickname = ref(false)
const nicknameError = ref('')
const canSaveNickname = computed(() => userStore.isLogin && editingNickname.value && !savingNickname.value
  && nicknameAllowed.value && !!nicknameDraft.value.trim() && nicknameDraft.value.trim().length <= 64)
let profileRevision = 0
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
  const revision = profileRevision
  try {
    const profile = await userApi.getUserInfo()
    if (revision === profileRevision) userStore.applyProfile(profile)
    profileLoaded.value = true
    targetDraftDates.CSCA = userInfo.value.targetDates.CSCA || ''
    targetDraftDates.HKS = userInfo.value.targetDates.HKS || ''
    targetDraftExams.value = [...userStore.selectedExams]
  } catch {
    if (userStore.isLogin) loadError.value = true
  }
}

const loadDashboard = async () => {
  try {
    Object.assign(dashboard, toDashboardData(await userApi.getDashboard()))
    dashboardLoaded.value = true
  } catch {
    if (userStore.isLogin) loadError.value = true
  }
}

const loadAll = async () => {
  if (isLoading.value) return
  isLoading.value = true
  loadError.value = false
  await userStore.restoreSession()
  if (userStore.isLogin) await Promise.all([loadProfile(), loadDashboard()])
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
  if (!await requireLogin()) return
  const missingExam = targetDraftExams.value.find((exam) => !targetDraftDates[exam])
  if (missingExam) {
    showToast({ title: t('请选择 {exam} 考试日期', { exam: getExamLabel(missingExam) }), icon: 'none' })
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
    profileRevision++
    userStore.applyProfile(updated)
    targetDraftDates.CSCA = userInfo.value.targetDates.CSCA || ''
    targetDraftDates.HKS = userInfo.value.targetDates.HKS || ''
    dashboard.targetExam = updated.target_exam
    dashboard.targetDate = updated.target_date || ''
    showToast({ title: '目标已更新', icon: 'success' })
  } catch {
    // 请求层已显示错误，编辑内容留待重试。
  } finally {
    savingTarget.value = false
  }
}

const chooseAvatar = async (event: any) => {
  const avatarUrl = event.detail?.avatarUrl
  if (!avatarUrl) return
  try {
    const updated = await userApi.uploadAvatar(avatarUrl)
    profileRevision++
    userStore.applyProfile(updated)
    showToast({ title: '头像已更新', icon: 'success' })
  } catch (error: any) { showToast({ title: error?.message || '头像上传失败，请重试', icon: 'none' }) }
}

const editNickname = async () => {
  if (!userStore.isLogin) { openLogin(); return }
  profileRevision++
  nicknameDraft.value = userInfo.value.nickname
  nicknameError.value = ''
  nicknameAllowed.value = true
  editingNickname.value = true
  await nextTick()
  if (editingNickname.value) nicknameFocused.value = true
}

function resetNicknameEditor() {
  editingNickname.value = false
  nicknameFocused.value = false
  nicknameDraft.value = ''
  nicknameError.value = ''
  nicknameAllowed.value = true
}

function cancelNicknameEdit() { if (!savingNickname.value) resetNicknameEditor() }
function onNicknameInput(event: any) {
  if (!editingNickname.value || savingNickname.value) return
  nicknameDraft.value = String(event.detail?.value ?? '')
  nicknameAllowed.value = true
  nicknameError.value = ''
}
function onNicknameBlur(event: any) {
  nicknameFocused.value = false
  if (editingNickname.value && !savingNickname.value) nicknameDraft.value = String(event.detail?.value ?? nicknameDraft.value)
}
function reviewNickname(event: any) {
  if (!editingNickname.value) return
  nicknameAllowed.value = event.detail?.pass !== false
  nicknameError.value = nicknameAllowed.value ? '' : t('昵称未通过审核，请修改后重试')
}
function confirmNickname(event: any) {
  if (savingNickname.value) return
  nicknameDraft.value = String(event.detail?.value ?? nicknameDraft.value)
  return saveNickname()
}
async function saveNickname() {
  if (!canSaveNickname.value) return
  const name = nicknameDraft.value.trim()
  if (name === userInfo.value.nickname) { resetNicknameEditor(); return }
  const generation = sessionGeneration()
  savingNickname.value = true
  nicknameError.value = ''
  try {
    const updated = await userApi.updateProfile({ nickname: name })
    if (generation !== sessionGeneration()) return
    profileRevision++
    userStore.applyProfile(updated)
    resetNicknameEditor()
    showToast({ title: '昵称已更新', icon: 'success' })
  } catch (error: any) {
    if (generation === sessionGeneration()) nicknameError.value = errorText(error?.message || '昵称保存失败，请重试')
  } finally {
    if (generation === sessionGeneration()) savingNickname.value = false
  }
}
const loginFromProfile = () => { if (!userStore.isLogin) openLogin() }
const copyUserCode = () => uni.setClipboardData({ data: userInfo.value.userCode })

const showAbout = () => {
  uni.navigateTo({ url: '/pages/about/index' })
}

const goPage = (url: string) => navigateProtected(url)

const handleLogout = () => {
  showModal({
    title: '确认退出',
    content: '退出后需要重新登录，确定退出吗？',
    success: (res: any) => {
      if (res.confirm) {
        userStore.logout()
        showToast({ title: '已退出登录', icon: 'success' })
      }
    },
  })
}

watch(activeUserId, () => {
  profileRevision++
  resetNicknameEditor()
  savingNickname.value = false
  profileLoaded.value = false
  dashboardLoaded.value = false
  loadError.value = false
  targetDraftDates.CSCA = ''
  targetDraftDates.HKS = ''
  targetDraftExams.value = [...userStore.selectedExams]
}, { flush: 'sync' })

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

.language-card { padding: 22rpx; }
.language-options { display: flex; gap: 12rpx; margin-top: 18rpx; }
.language-option { flex: 1; margin: 0; padding: 16rpx 12rpx; border: 1rpx solid var(--app-border); border-radius: var(--app-radius-md); color: var(--app-text-weak); background: var(--app-surface-quiet); font-size: 26rpx; line-height: 1.5; }
.language-option::after { border: 0; }
.language-option.active { color: var(--app-primary); background: var(--app-primary-soft); border-color: var(--app-primary); font-weight: 600; }

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

.profile-name-row { display: flex; align-items: baseline; flex-wrap: wrap; gap: 14rpx; }
.profile-name-input { flex: 1; min-width: 180rpx; width: 100%; height: 72rpx; padding: 0 12rpx; border: 1rpx solid var(--app-primary); border-radius: 12rpx; font-size: 34rpx; color: var(--app-text); background: var(--app-surface-quiet); }
.nickname-hint { display: block; margin-top: 10rpx; color: var(--app-text-weak); font-size: 22rpx; line-height: 1.5; }
.nickname-hint-error { color: var(--app-danger); }
.profile-code { color: var(--app-text-weak); font-size: 24rpx; }
.login-link { display: block; margin-top: 8rpx; color: var(--app-primary); font-size: 26rpx; }
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

<script setup lang="ts">
import { onHide, onLaunch, onShow } from '@dcloudio/uni-app'
import { isTimelinePreview } from '@/constants/share'
import { useUserStore } from '@/stores/user'
import { useExamStore } from '@/stores/exam'
import { initializeLanguage } from '@/i18n'
import { configureLoginPrompt } from '@/shared/auth/session'
import { promptLogin } from '@/shared/auth/navigation'

const userStore = useUserStore()
const examStore = useExamStore()
configureLoginPrompt(() => promptLogin())

onLaunch((options) => {
  initializeLanguage()
  if (isTimelinePreview(options?.scene)) return
  userStore.restoreSession().catch(() => {})
})

onShow(() => {})
onHide(() => {
  if (isTimelinePreview()) return
  examStore.persistProgress()
})
</script>

<style src="@tdesign/uniapp/theme.css"></style>

<style lang="scss">
@use '@/styles/app.scss';
</style>

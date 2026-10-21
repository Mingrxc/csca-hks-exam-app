<script setup lang="ts">
import { onHide, onLaunch, onShow } from '@dcloudio/uni-app'
import { isTimelinePreview } from '@/constants/share'
import { useUserStore } from '@/stores/user'
import { useExamStore } from '@/stores/exam'

const userStore = useUserStore()
const examStore = useExamStore()

onLaunch((options) => {
  if (isTimelinePreview(options?.scene)) return
  userStore.login().catch(() => {})
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

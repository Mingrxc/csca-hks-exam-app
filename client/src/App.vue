<script setup lang="ts">
import { onHide, onLaunch, onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { useExamStore } from '@/stores/exam'

const userStore = useUserStore()
const examStore = useExamStore()

onLaunch(() => {
  userStore.login().catch(() => {})
})

onShow(() => {})
onHide(() => {
  examStore.persistProgress()
})
</script>

<style lang="scss">
@import '@/styles/app.scss';
</style>

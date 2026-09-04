<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onLaunch(() => {
  userStore.login().catch(() => {})
})

onShow(() => {})
onHide(() => {})
</script>

<style lang="scss">
@import '@/styles/app.scss';
</style>

<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="section-head">
        <text class="app-section-title">留学资讯</text>
      </view>
      <c-app-state v-if="contentState.loading.value" state="loading" title="正在加载资讯" />
      <c-app-state
        v-else-if="contentState.error.value"
        state="error"
        title="资讯加载失败"
        :description="contentState.error.value"
        @retry="loadContents"
      />
      <view v-else-if="contents.length" class="app-list">
        <view v-for="item in contents" :key="item.id" class="content-card home-card app-card app-list-card" @click="openContent(item)">
          <view class="app-list-row">
            <view class="app-list-main">
              <view class="content-head">
                <text class="app-list-meta">{{ item.created_at?.slice(0, 10) || '' }}</text>
              </view>
              <text class="app-list-title">{{ item.title }}</text>
              <text class="app-list-desc">{{ item.summary }}</text>
            </view>
            <t-icon name="chevron-right" size="28rpx" color="#9d8f84" />
          </view>
        </view>
      </view>
      <c-app-state v-else state="empty" title="暂无资讯内容" />
    </view>

    <view class="app-section">
      <view class="section-head">
        <text class="app-section-title">社团广告</text>
      </view>
      <view class="app-list">
        <view v-for="item in clubAds" :key="item.title" class="ad-card home-card app-card app-card-compact">
          <view class="app-list-row">
            <view class="app-list-main">
              <text class="app-list-title">{{ item.title }}</text>
              <text class="app-list-desc">{{ item.desc }}</text>
            </view>
            <t-icon name="arrow-right" size="26rpx" color="#c77f5e" />
          </view>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="section-head">
        <text class="app-section-title">最近学习记录</text>
      </view>
      <c-app-state v-if="dashboardState.loading.value" state="loading" title="正在加载学习记录" />
      <c-app-state
        v-else-if="dashboardState.error.value"
        state="error"
        title="学习记录加载失败"
        :description="dashboardState.error.value"
        @retry="loadRecentPapers"
      />
      <view v-else-if="recentPapers.length" class="app-list">
        <view v-for="paper in recentPapers" :key="paper.id" class="paper-card home-card app-card app-list-card" @click="goPaper(paper.id)">
          <view class="app-list-row">
            <view class="app-list-main">
              <text class="app-list-title">{{ paper.title }}</text>
              <text class="app-list-desc">{{ paper.questionCount }} 题 · {{ paper.score }} 分</text>
            </view>
            <view class="paper-meta">
              <text>{{ paper.date }}</text>
              <t-icon name="chevron-right" size="26rpx" color="#9d8f84" />
            </view>
          </view>
        </view>
      </view>
      <c-app-state v-else state="empty" title="还没有学习记录" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import type { ApiContentItem } from '@/api/contracts'
import { useUserStore } from '@/stores/user'
import { useHomePage } from '@/features/home/useHomePage'

const userStore = useUserStore()
const { contentState, dashboardState, recentPapers, loadContents, loadDashboard } = useHomePage()
const contents = computed(() => contentState.data.value)
const clubAds = [
  { title: '本周活动招募', desc: '报名入口和时间放在这里。' },
  { title: '学习资料合作位', desc: '适合放推荐和活动宣传。' },
]

const loadRecentPapers = async () => {
  await loadDashboard(userStore.isLogin)
}

const goPaper = (id: number) => {
  uni.navigateTo({ url: `/pages/exam/result?id=${id}` })
}

const openContent = (item: ApiContentItem) => {
  if (item.link_url) {
    uni.navigateTo({ url: item.link_url })
    return
  }
  uni.showModal({ title: item.title, content: item.body, showCancel: false })
}

onShow(async () => {
  loadContents()
  if (!userStore.isLogin) {
    try { await userStore.login() } catch {}
  }
  await loadRecentPapers()
})
</script>

<style lang="scss" scoped>
.content-card,
.ad-card,
.paper-card {
  background: rgba(255, 255, 255, 0.86);
}

.home-card {
  border-radius: 32rpx !important;
  overflow: hidden;
}

.app-section + .app-section {
  margin-top: 40rpx;
}

.content-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-bottom: 10rpx;
}

.paper-meta {
  flex: none;
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: var(--app-text-mute);
  font-size: 21rpx;
}
</style>

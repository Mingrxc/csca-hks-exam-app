<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="section-head">
        <text class="app-section-title">留学资讯</text>
      </view>
      <view v-if="contents.length" class="app-list">
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
      <t-empty v-else description="暂无资讯内容" />
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
      <view v-if="recentPapers.length" class="app-list">
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
      <t-empty v-else description="还没有学习记录" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { contentApi, userApi } from '@/api'
import { toDashboardData } from '@/api/contracts'
import type { ApiContentItem } from '@/api/contracts'
import type { RecentPaper } from '@/types/user'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const recentPapers = ref<RecentPaper[]>([])
const contents = ref<ApiContentItem[]>([])
const clubAds = [
  { title: '本周活动招募', desc: '报名入口和时间放在这里。' },
  { title: '学习资料合作位', desc: '适合放推荐和活动宣传。' },
]

const loadRecentPapers = async () => {
  if (!userStore.isLogin) {
    recentPapers.value = []
    return
  }
  try {
    const data = toDashboardData(await userApi.getDashboard())
    recentPapers.value = data.recentPapers
  } catch {}
}

const loadContents = async () => {
  try {
    contents.value = (await contentApi.listHome()).slice(0, 5)
  } catch {}
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

onShow(() => {
  loadRecentPapers()
  loadContents()
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

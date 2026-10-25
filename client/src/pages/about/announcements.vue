<template>
  <view class="page app-shell">
    <view class="app-section heading">
      <text class="app-section-title">每一点进步，都在这里</text>
      <text class="app-section-subtitle">查看新功能、体验优化与修复记录</text>
    </view>
    <view class="app-section">
      <view v-if="loading && !items.length" class="app-card"><c-app-state state="loading" title="正在加载更新公告" /></view>
      <view v-else-if="!error && !items.length" class="app-card"><c-app-state state="empty" title="暂无更新公告" description="新的更新消息会在这里与你见面。" /></view>
      <view v-for="item in items" :key="item.id" class="announcement-card app-card" hover-class="card-pressed" @tap="openAnnouncement(item.id)">
        <view class="announcement-meta"><text class="version-tag">v{{ item.release_version }}</text><text>{{ formatReleaseDate(item.published_at) }}</text></view>
        <view class="announcement-heading"><text class="announcement-title">{{ item.title }}</text><t-icon name="chevron-right" size="30rpx" /></view>
        <text class="announcement-summary">{{ item.summary }}</text>
      </view>
      <view v-if="error" class="app-card"><c-app-state compact state="error" title="公告暂时无法加载" @retry="retry" /></view>
      <button v-else-if="hasMore" class="load-more" :loading="loading" :disabled="loading" @tap="loadMore">{{ loading ? '正在加载' : '查看更多' }}</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad, onReachBottom } from '@dcloudio/uni-app'
import { contentApi } from '@/features/content/api'
import { formatReleaseDate } from '@/features/content/date'
import type { ApiContentItem } from '@/api/contracts'

const items = ref<ApiContentItem[]>([])
const loading = ref(false)
const error = ref(false)
const page = ref(0)
const total = ref(0)
const hasMore = computed(() => items.value.length < total.value)

async function load(reset = false) {
  if (loading.value) return
  loading.value = true
  error.value = false
  const nextPage = reset ? 1 : page.value + 1
  try {
    const result = await contentApi.listAnnouncements(nextPage)
    items.value = reset ? result.items : [...items.value, ...result.items]
    total.value = result.total
    page.value = nextPage
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

const retry = () => load(page.value === 0)
const loadMore = () => { if (hasMore.value) return load() }
const openAnnouncement = (id: number) => uni.navigateTo({ url: `/pages/about/announcement?id=${id}` })
onLoad(() => load(true))
onReachBottom(loadMore)
</script>

<style lang="scss" scoped>
.heading { padding-top: 16rpx; }
.announcement-card { padding: 28rpx; margin-bottom: 20rpx; }
.announcement-meta { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; font-size: 22rpx; color: var(--app-text-mute); }
.version-tag { color: var(--app-primary); background: var(--app-primary-soft); border-radius: 10rpx; padding: 4rpx 12rpx; }
.announcement-heading { display: flex; align-items: center; gap: 12rpx; margin-top: 18rpx; color: var(--app-text-mute); }
.announcement-title { flex: 1; min-width: 0; font-size: 30rpx; font-weight: 600; color: var(--app-text); overflow-wrap: anywhere; }
.announcement-summary { display: block; margin-top: 12rpx; font-size: 26rpx; line-height: 1.8; color: var(--app-text-weak); overflow-wrap: anywhere; }
.load-more { background: transparent; color: var(--app-primary); font-size: 26rpx; padding: 12rpx; }
.card-pressed { opacity: .65; }
</style>

<template>
  <view class="page app-shell">
    <view class="app-section">
      <view v-if="loading" class="app-card"><c-app-state state="loading" title="正在加载公告" /></view>
      <view v-else-if="error" class="app-card"><c-app-state state="error" title="公告暂时无法查看" description="内容可能已撤下，请返回列表或重试。" @retry="load" /></view>
      <view v-else-if="item" class="detail-card app-card">
        <view class="detail-meta"><text>v{{ item.release_version }}</text><text>{{ formatReleaseDate(item.published_at) }}</text></view>
        <text class="detail-title">{{ item.title }}</text>
        <text class="detail-body" selectable>{{ item.body }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { contentApi } from '@/features/content/api'
import { formatReleaseDate } from '@/features/content/date'
import type { ApiContentItem } from '@/api/contracts'

const id = ref(0)
const item = ref<ApiContentItem | null>(null)
const loading = ref(false)
const error = ref(false)

async function load() {
  if (loading.value) return
  if (!Number.isSafeInteger(id.value) || id.value <= 0) { error.value = true; return }
  loading.value = true
  error.value = false
  try { item.value = await contentApi.getAnnouncement(id.value) }
  catch { error.value = true }
  finally { loading.value = false }
}

onLoad((options) => { id.value = Number(options?.id); return load() })
</script>

<style lang="scss" scoped>
.detail-card { padding: 36rpx 28rpx 44rpx; }
.detail-meta { display: flex; justify-content: space-between; gap: 16rpx; font-size: 24rpx; color: var(--app-primary); }
.detail-title { display: block; margin-top: 24rpx; font-size: 38rpx; font-weight: 600; line-height: 1.5; overflow-wrap: anywhere; }
.detail-body { display: block; margin-top: 32rpx; padding-top: 28rpx; border-top: 1rpx solid var(--app-border); white-space: pre-wrap; overflow-wrap: anywhere; font-size: 28rpx; line-height: 1.95; color: var(--app-text-weak); }
</style>

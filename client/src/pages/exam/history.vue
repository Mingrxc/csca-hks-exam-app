<template>
  <view class="page app-shell history-page">
    <view class="app-section history-heading-section">
      <view class="history-heading">
        <view class="history-heading-copy">
          <text class="app-section-title">历史试卷</text>
          <text class="app-section-subtitle">查看每一次练习的成绩和答题表现</text>
        </view>
        <view class="history-count">
          <text class="history-count-value">{{ historyPapers.length }}</text>
          <text class="history-count-label">份</text>
        </view>
      </view>
    </view>

    <view v-if="loadError" class="app-section">
      <view class="error-card app-card" @click="loadHistory">历史试卷加载失败，点击重试</view>
    </view>

    <view v-if="!loadError" class="app-section">
      <view class="history-list app-list">
        <view
          v-for="paper in historyPapers"
          :key="paper.id"
          class="history-paper app-card app-list-card"
          @click="goResult(paper.id)"
        >
          <view class="app-list-row">
            <view class="app-list-main">
              <text class="app-list-title">{{ paper.title }}</text>
              <text class="app-list-desc">{{ paper.correctRate }}% · {{ paper.timeUsed }}</text>
            </view>
            <view class="paper-side">
              <t-tag :theme="paper.passed ? 'success' : 'danger'" variant="light" shape="round" size="small">
                {{ paper.passed ? '通过' : '未通过' }}
              </t-tag>
              <text class="app-list-meta">{{ paper.date }}</text>
            </view>
            <t-icon class="paper-arrow" name="chevron-right" size="26rpx" color="#b6a69a" />
          </view>
        </view>
      </view>

      <t-empty v-if="!loading && historyPapers.length === 0" description="还没有答题记录" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { questionApi } from '@/api'
import { toHistoryPaper } from '@/api/contracts'
import type { HistoryPaper } from '@/types/exam'

const historyPapers = ref<HistoryPaper[]>([])
const loading = ref(false)
const loadError = ref(false)

const loadHistory = async () => {
  if (loading.value) return

  loading.value = true
  loadError.value = false
  try {
    const items = await questionApi.getPapers({ limit: 100 })
    historyPapers.value = items.map(toHistoryPaper)
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

const goResult = (id: number) => {
  uni.navigateTo({ url: `/pages/exam/result?id=${id}` })
}

onShow(loadHistory)
</script>

<style lang="scss" scoped>
.history-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.history-heading-copy {
  flex: 1;
  min-width: 0;
}

.history-count {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
  padding: 10rpx 16rpx;
  border-radius: 999px;
  background: var(--app-primary-soft);
  color: var(--app-primary);
  flex: none;
}

.history-count-value {
  font-size: 30rpx;
  line-height: 1;
  font-weight: 600;
}

.history-count-label {
  font-size: 20rpx;
}

.history-paper {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 28rpx !important;
  transition: opacity 0.15s ease;
}

.history-paper:active {
  opacity: 0.75;
}

.paper-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
  flex: none;
}

.paper-arrow {
  flex: none;
  margin-left: 2rpx;
}

.error-card {
  padding: 24rpx;
  text-align: center;
  color: var(--app-danger);
  background: var(--app-danger-soft);
  border-radius: 28rpx !important;
}
</style>

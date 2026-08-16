<template>
  <view class="page">
    <!-- 刷题入口卡片 -->
    <view class="section">
      <text class="section-title">选择组卷策略</text>
      <view class="strategy-list">
        <view class="strategy-card" v-for="item in strategies" :key="item.key" @click="goPaper(item.key)">
          <view class="strategy-left">
            <text class="strategy-icon">{{ item.icon }}</text>
          </view>
          <view class="strategy-right">
            <text class="strategy-title">{{ item.title }}</text>
            <text class="strategy-desc">{{ item.desc }}</text>
          </view>
          <text class="strategy-arrow">→</text>
        </view>
      </view>
    </view>

    <!-- 历史试卷 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">历史试卷</text>
        <text class="section-more" v-if="canViewAll" @click="viewAll">查看全部</text>
      </view>
      <view class="load-error" v-if="loadError" @click="loadHistory(historyLimit)">
        <text>历史试卷加载失败，点击重试</text>
      </view>
      <view class="paper-card" v-for="paper in historyPapers" :key="paper.id" @click="goResult(paper.id)">
        <view class="paper-header">
          <text class="paper-name">{{ paper.title }}</text>
          <view class="paper-badge" :class="paper.passed ? 'pass' : 'fail'">
            {{ paper.passed ? '通过' : '未通过' }}
          </view>
        </view>
        <view class="paper-stats">
          <text class="paper-stat">正确率 {{ paper.correctRate }}%</text>
          <text class="paper-stat">用时 {{ paper.timeUsed }}</text>
          <text class="paper-stat">{{ paper.date }}</text>
        </view>
      </view>
      <view class="empty-state" v-if="!loading && !loadError && historyPapers.length === 0">
        <text class="empty-icon">📝</text>
        <text class="empty-text">还没有答题记录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { questionApi } from '@/api'
import { toHistoryPaper } from '@/api/contracts'
import { PAPER_STRATEGIES } from '@/constants/exam'
import type { HistoryPaper, PaperStrategy } from '@/types/exam'

const strategies = ref(PAPER_STRATEGIES)

const historyPapers = ref<HistoryPaper[]>([])
const historyLimit = ref(5)
const loading = ref(false)
const loadError = ref(false)
const canViewAll = computed(() => historyLimit.value === 5 && historyPapers.value.length === 5)

const loadHistory = async (limit: number) => {
  loading.value = true
  loadError.value = false
  try {
    const items = await questionApi.getPapers({ limit })
    historyPapers.value = items.map(toHistoryPaper)
    historyLimit.value = limit
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

const goPaper = (strategy: PaperStrategy) => {
  uni.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}` })
}

const goResult = (id: number) => {
  uni.navigateTo({ url: `/pages/exam/result?id=${id}` })
}

const viewAll = () => {
  loadHistory(100)
}

onShow(() => loadHistory(historyLimit.value))
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; padding: 24rpx 0 40rpx; }
.section { padding: 0 24rpx; margin-bottom: 32rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: #1F2937; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.section-more { font-size: 24rpx; color: #4F46E5; }

.strategy-list { display: flex; flex-direction: column; gap: 16rpx; margin-top: 16rpx; }
.strategy-card {
  display: flex; align-items: center;
  background: #fff; border-radius: 16rpx; padding: 28rpx 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.strategy-icon { font-size: 44rpx; }
.strategy-right { flex: 1; margin-left: 20rpx; }
.strategy-title { font-size: 28rpx; font-weight: 600; color: #1F2937; }
.strategy-desc { font-size: 22rpx; color: #9CA3AF; margin-top: 6rpx; display: block; }
.strategy-arrow { font-size: 28rpx; color: #C7D2FE; }

.paper-card {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); margin-bottom: 16rpx;
}
.paper-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12rpx; }
.paper-name { font-size: 28rpx; font-weight: 500; color: #1F2937; }
.paper-badge { font-size: 20rpx; padding: 4rpx 16rpx; border-radius: 20rpx; }
.paper-badge.pass { background: #D1FAE5; color: #065F46; }
.paper-badge.fail { background: #FEE2E2; color: #991B1B; }
.paper-stats { display: flex; gap: 24rpx; }
.paper-stat { font-size: 22rpx; color: #9CA3AF; }

.empty-state { padding: 80rpx 0; text-align: center; }
.empty-icon { font-size: 60rpx; display: block; margin-bottom: 16rpx; }
.empty-text { font-size: 26rpx; color: #9CA3AF; }
.load-error { margin-top: 16rpx; padding: 24rpx; text-align: center; color: #B91C1C; background: #FEF2F2; border-radius: 12rpx; font-size: 24rpx; }
</style>

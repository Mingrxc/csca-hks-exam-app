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

    <view class="app-section">
      <c-app-state v-if="loading" state="loading" title="正在加载历史试卷" />
      <c-app-state
        v-else-if="error"
        state="error"
        title="历史试卷加载失败"
        :description="error"
        @retry="load"
      />
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

      <c-app-state v-if="!loading && !error && historyPapers.length === 0" state="empty" title="还没有答题记录" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { useExamHistory } from '@/features/exam/useExamHistory'

const { data: historyPapers, loading, error, load } = useExamHistory()

const goResult = (id: number) => {
  uni.navigateTo({ url: `/pages/exam/result?id=${id}` })
}

onShow(load)
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

</style>

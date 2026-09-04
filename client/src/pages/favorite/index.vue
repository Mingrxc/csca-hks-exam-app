<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-card app-card-soft app-card-pad">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">收藏题目</text>
            <text class="hero-title">把值得反复看的题留住</text>
            <text class="hero-subtitle">答题时顺手收藏，后面集中复习会更省力。</text>
          </view>
          <t-tag theme="primary" variant="light" shape="round">{{ items.length }}</t-tag>
        </view>
      </view>
    </view>

    <view v-if="loadError" class="app-section">
      <view class="error-card app-card" @click="load">加载失败，点击重试</view>
    </view>

    <view class="app-section">
      <view class="favorite-list">
        <view v-for="item in items" :key="item.id" class="favorite-item app-card app-card-compact">
          <view class="meta">
            <t-tag theme="primary" variant="light" shape="round" size="small">{{ item.question.exam_type }}</t-tag>
            <t-tag theme="warning" variant="light" shape="round" size="small">
              {{ item.question.exam_type === 'CSCA' ? item.question.subject : item.question.knowledge_point }}
            </t-tag>
            <text class="date">{{ item.created_at.slice(0, 10) }}</text>
          </view>
          <text class="stem">{{ item.question.stem_text }}</text>
          <view class="actions">
            <t-button theme="default" variant="outline" size="small" shape="round" @click="askAI(item)">
              发给 AI
            </t-button>
            <t-button theme="danger" variant="outline" size="small" shape="round" @click="remove(item.question_id)">
              取消收藏
            </t-button>
          </view>
        </view>
      </view>

      <t-empty v-if="!loading && !loadError && items.length === 0" description="还没有收藏题目" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { favoriteApi } from '@/api'
import type { ApiFavoriteItem } from '@/api/contracts'

const items = ref<ApiFavoriteItem[]>([])
const loading = ref(false)
const loadError = ref(false)

const load = async () => {
  loading.value = true
  loadError.value = false
  try {
    items.value = await favoriteApi.list()
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

const remove = async (questionId: number) => {
  try {
    await favoriteApi.toggle(questionId)
    items.value = items.value.filter((item) => item.question_id !== questionId)
  } catch {}
}

const askAI = (item: ApiFavoriteItem) => {
  uni.setStorageSync('ai_prefill', {
    content: item.question.stem_text,
    topic: '收藏题目咨询',
    context: [
      `考试类型：${item.question.exam_type}`,
      item.question.exam_type === 'CSCA'
        ? `科目：${item.question.subject}`
        : `知识点：${item.question.knowledge_point}`,
      `收藏时间：${item.created_at.slice(0, 10)}`,
      item.note ? `备注：${item.note}` : '',
    ]
      .filter(Boolean)
      .join('\n'),
    examType: item.question.exam_type,
  })
  uni.switchTab({ url: '/pages/ai/index' })
}

onShow(load)
</script>

<style lang="scss" scoped>
.hero-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.hero-copy {
  flex: 1;
  min-width: 0;
}

.hero-brand {
  display: block;
  color: var(--app-primary);
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.hero-title {
  display: block;
  margin-top: 10rpx;
  font-size: 36rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.hero-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--app-text-weak);
}

.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.favorite-item {
  padding: 20rpx;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10rpx;
}

.date {
  margin-left: auto;
  font-size: 21rpx;
  color: var(--app-text-mute);
}

.stem {
  display: block;
  margin-top: 14rpx;
  font-size: 26rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12rpx;
  margin-top: 16rpx;
}

.error-card {
  padding: 24rpx;
  text-align: center;
  color: var(--app-danger);
  background: var(--app-danger-soft);
}
</style>

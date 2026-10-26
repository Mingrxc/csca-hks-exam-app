<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-heading">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">{{ t("收藏题目") }}</text>
            <text class="hero-title">{{ t("我的收藏") }}</text>
            <text class="hero-subtitle">{{ t("值得反复看的题目，集中留在这里。") }}</text>
          </view>
          <t-tag theme="primary" variant="light" shape="round">{{ loading || error ? '—' : items.length }}</t-tag>
        </view>
      </view>
    </view>

    <view class="app-section">
      <c-app-state v-if="loading" state="loading" :title="t('正在加载收藏')" />
      <c-app-state v-else-if="error" state="error" :title="t('收藏加载失败')" :description="error" @retry="load" />
      <view v-else class="favorite-list">
        <view v-for="item in items" :key="item.id" class="favorite-item app-card app-card-compact">
          <view class="meta">
            <t-tag theme="primary" variant="light" shape="round" size="small">{{ getExamLabel(item.question.exam_type) }}</t-tag>
            <t-tag theme="warning" variant="light" shape="round" size="small">
              {{ t(item.question.exam_type === 'CSCA' ? item.question.subject : item.question.knowledge_point) }}
            </t-tag>
            <text class="date">{{ item.created_at.slice(0, 10) }}</text>
          </view>
          <text class="stem">{{ item.question.stem_text }}</text>
          <view class="actions">
            <t-button theme="default" variant="outline" size="small" shape="round" @click="askAI(item)">
              {{ t("发给 AI") }}
            </t-button>
            <t-button theme="danger" variant="outline" size="small" shape="round" @click="remove(item.question_id)">
              {{ t("取消收藏") }}
            </t-button>
          </view>
        </view>
      </view>

      <c-app-state v-if="!loading && !error && items.length === 0" state="empty" :title="t('还没有收藏题目')" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { getExamLabel } from '@/constants/exam'
import { onShareAppMessage, onShow } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import type { ApiFavoriteItem } from '@/api/contracts'
import { useFavorites } from '@/features/favorite/useFavorites'

usePageI18n('pages/favorite/index')

const { data: items, loading, error, load, remove: removeFavorite } = useFavorites()

const remove = async (questionId: number) => {
  try { await removeFavorite(questionId) } catch {}
}

const askAI = (item: ApiFavoriteItem) => {
  uni.setStorageSync('ai_prefill', {
    content: item.question.stem_text,
    topic: t('收藏题目咨询'),
    context: [
      t('考试类型：{value}', { value: getExamLabel(item.question.exam_type) }),
      item.question.exam_type === 'CSCA'
        ? t('科目：{value}', { value: item.question.subject })
        : t('知识点：{value}', { value: item.question.knowledge_point }),
      t('收藏时间：{value}', { value: item.created_at.slice(0, 10) }),
      item.note ? t('备注：{value}', { value: item.note }) : '',
    ]
      .filter(Boolean)
      .join('\n'),
    examType: item.question.exam_type,
  })
  uni.switchTab({ url: '/pages/ai/index' })
}

onShow(load)
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
// #endif
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
  font-size: var(--app-font-xs);
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

</style>

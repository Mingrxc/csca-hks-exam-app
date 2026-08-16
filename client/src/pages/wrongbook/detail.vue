<template>
  <view class="page" v-if="question">
    <!-- 题目信息 -->
    <view class="question-section">
      <view class="q-header">
        <view class="tag-row">
          <text class="tag type">{{ question.typeLabel }}</text>
          <text class="tag diff" :class="question.difficulty">{{ question.diffLabel }}</text>
          <text class="tag point">{{ question.knowledgePoint }}</text>
        </view>
        <text class="wrong-count">错误 {{ question.wrongCount }} 次</text>
      </view>

      <text class="q-stem">{{ question.stem }}</text>

      <!-- 选项 -->
      <view class="q-options">
        <view
          class="option"
          :class="{
            correct: opt.key === question.answer,
            my: opt.key === question.myAnswer,
            wrong: opt.key === question.myAnswer && opt.key !== question.answer
          }"
          v-for="opt in question.options"
          :key="opt.key"
        >
          <view class="option-key">{{ opt.key }}</view>
          <text class="option-text">{{ opt.text }}</text>
          <text class="option-mark" v-if="opt.key === question.answer">✓</text>
          <text class="option-mark wrong-mark" v-else-if="opt.key === question.myAnswer">✗</text>
        </view>
      </view>
    </view>

    <!-- 解析区 -->
    <view class="analysis-section">
      <view class="analysis-header">
        <text class="analysis-icon">💡</text>
        <text class="analysis-title">题目解析</text>
      </view>
      <text class="analysis-text">{{ question.analysis }}</text>

      <!-- 易混选项辨析 -->
      <view class="confusion-box" v-if="question.confusion">
        <text class="confusion-title">易混选项辨析</text>
        <text class="confusion-text">{{ question.confusion }}</text>
      </view>
    </view>

    <!-- 举一反三 -->
    <view class="related-section">
      <view class="related-header">
        <text class="related-title">举一反三</text>
        <text class="related-desc">以下题目基于相同知识点「{{ question.knowledgePoint }}」推荐</text>
      </view>
      <view class="related-list">
        <view class="related-item" v-for="item in relatedQuestions" :key="item.id" @click="goRelated">
          <view class="related-tags">
            <text class="related-tag diff" :class="item.difficulty">{{ item.diffLabel }}</text>
            <text class="related-tag">{{ item.typeLabel }}</text>
          </view>
          <text class="related-stem">{{ item.stem }}</text>
          <text class="related-action">去练习 →</text>
        </view>
      </view>
    </view>

    <!-- 操作 -->
    <view class="actions">
      <button class="action-btn" @click="markMastered">
        {{ question.mastered ? '✓ 已掌握' : '标记为已掌握' }}
      </button>
      <button class="action-btn outline" @click="goRedo">加入重做列表</button>
    </view>
  </view>
  <view class="loading-state" v-else>正在加载错题详情...</view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { wrongBookApi } from '@/api'
import { toRelatedQuestion, toWrongBookDetail } from '@/api/contracts'
import type { RelatedQuestion, WrongBookDetail } from '@/types/wrongbook'

const question = ref<WrongBookDetail | null>(null)
const wrongBookId = ref<number | null>(null)

const relatedQuestions = ref<RelatedQuestion[]>([])

const loadDetail = async (id?: number, questionId?: number) => {
  try {
    const payload = questionId
      ? await wrongBookApi.getDetailByQuestion(questionId)
      : await wrongBookApi.getDetail(id as number)
    question.value = toWrongBookDetail(payload)
    wrongBookId.value = payload.id

    const related = await wrongBookApi.getRelated(payload.question_id)
    relatedQuestions.value = related.map(toRelatedQuestion)
  } catch {
    // The shared request layer already displays the error message.
  }
}

onLoad((query) => {
  const id = Number(query?.id)
  const questionId = Number(query?.questionId)
  if (Number.isInteger(questionId) && questionId > 0) {
    loadDetail(undefined, questionId)
    return
  }
  if (Number.isInteger(id) && id > 0) {
    loadDetail(id)
    return
  }
  uni.showToast({ title: '未找到错题记录', icon: 'none' })
  setTimeout(() => uni.navigateBack(), 300)
})

const markMastered = async () => {
  if (!question.value || !wrongBookId.value) return
  try {
    const payload = await wrongBookApi.markMastered(wrongBookId.value)
    question.value.mastered = payload.is_mastered
    uni.showToast({ title: payload.is_mastered ? '已标记为掌握' : '已取消标记', icon: 'success' })
  } catch {
    // The shared request layer already displays the error message.
  }
}

const goRelated = () => {
  if (!question.value) return
  uni.navigateTo({
    url: `/pages/exam/paper?strategy=knowledge&knowledge=${encodeURIComponent(question.value.knowledgePoint)}`,
  })
}

const goRedo = () => {
  if (!question.value) return
  uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${question.value.examType}` })
}
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; padding: 24rpx; background: #F5F5F7; }

.question-section {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
.q-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.tag-row { display: flex; gap: 8rpx; }
.tag { padding: 2rpx 12rpx; border-radius: 8rpx; font-size: 20rpx; }
.tag.type { background: #DBEAFE; color: #1E40AF; }
.tag.diff { background: #F3F4F6; color: #6B7280; }
.tag.diff.hard { background: #FEE2E2; color: #991B1B; }
.tag.point { background: #EDE9FE; color: #5B21B6; }
.wrong-count { font-size: 22rpx; color: #EF4444; font-weight: 600; }

.q-stem { font-size: 30rpx; line-height: 1.8; color: #1F2937; display: block; margin-bottom: 24rpx; }

.q-options { display: flex; flex-direction: column; gap: 12rpx; }
.option {
  display: flex; align-items: center;
  padding: 20rpx 20rpx; border-radius: 12rpx;
  border: 2rpx solid #E5E7EB; background: #fff;
}
.option.correct { border-color: #10B981; background: #D1FAE5; }
.option.wrong { border-color: #EF4444; background: #FEE2E2; }
.option.my { border-color: #818CF8; }
.option-key {
  width: 44rpx; height: 44rpx; border-radius: 50%;
  background: #F3F4F6; display: flex; align-items: center;
  justify-content: center; font-size: 22rpx; font-weight: 600; color: #6B7280;
}
.option.correct .option-key { background: #10B981; color: #fff; }
.option.wrong .option-key { background: #EF4444; color: #fff; }
.option-text { flex: 1; margin-left: 12rpx; font-size: 26rpx; color: #1F2937; }
.option-mark { font-size: 24rpx; font-weight: 700; color: #10B981; margin-left: 8rpx; }
.wrong-mark { color: #EF4444; }

.analysis-section {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
.analysis-header { display: flex; align-items: center; gap: 8rpx; margin-bottom: 12rpx; }
.analysis-icon { font-size: 28rpx; }
.analysis-title { font-size: 28rpx; font-weight: 600; color: #1F2937; }
.analysis-text { font-size: 26rpx; color: #374151; line-height: 1.7; }
.confusion-box { margin-top: 16rpx; padding: 20rpx; background: #FFFBEB; border-radius: 12rpx; }
.confusion-title { font-size: 24rpx; font-weight: 600; color: #92400E; display: block; margin-bottom: 8rpx; }
.confusion-text { font-size: 24rpx; color: #78350F; line-height: 1.7; }

.related-section { margin-bottom: 32rpx; }
.related-header { margin-bottom: 16rpx; }
.related-title { font-size: 30rpx; font-weight: 600; color: #1F2937; display: block; }
.related-desc { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; display: block; }
.related-list { display: flex; flex-direction: column; gap: 12rpx; }
.related-item {
  background: #fff; border-radius: 16rpx; padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03); border-left: 4rpx solid #4F46E5;
}
.related-tags { display: flex; gap: 8rpx; margin-bottom: 8rpx; }
.related-tag { padding: 2rpx 12rpx; border-radius: 8rpx; font-size: 20rpx; background: #F3F4F6; color: #6B7280; }
.related-tag.diff.hard { background: #FEE2E2; color: #991B1B; }
.related-stem { font-size: 24rpx; color: #1F2937; line-height: 1.6; display: block; }
.related-action { font-size: 22rpx; color: #4F46E5; margin-top: 8rpx; display: block; }

.actions { padding: 0 0 40rpx; display: flex; flex-direction: column; gap: 16rpx; }
.action-btn {
  border-radius: 48rpx; font-size: 28rpx; font-weight: 600; padding: 20rpx 0;
  border: none; text-align: center; background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #fff;
}
.action-btn.outline { background: #fff; color: #4F46E5; border: 2rpx solid #4F46E5; }
</style>

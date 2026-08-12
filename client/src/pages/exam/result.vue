<template>
  <view class="page">
    <!-- 成绩概览 -->
    <view class="score-header" :class="passed ? 'passed' : 'failed'">
      <text class="score-label">{{ passed ? '恭喜通过！' : '继续加油' }}</text>
      <view class="score-ring">
        <text class="score-num">{{ result.score }}</text>
        <text class="score-unit">分</text>
      </view>
      <view class="score-stats">
        <view class="stat-item">
          <text class="stat-value">{{ result.correctCount }}/{{ result.totalCount }}</text>
          <text class="stat-desc">正确</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ result.correctRate }}%</text>
          <text class="stat-desc">正确率</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ result.timeUsed }}</text>
          <text class="stat-desc">用时</text>
        </view>
      </view>
    </view>

    <!-- 知识点分析 -->
    <view class="section">
      <text class="section-title">知识点分析</text>
      <view class="knowledge-list" v-if="knowledgeItems.length">
        <view class="knowledge-item" v-for="item in knowledgeItems" :key="item.name">
          <text class="knowledge-name">{{ item.name }}</text>
          <view class="knowledge-track">
            <view class="knowledge-fill" :style="{ width: item.correctRate + '%' }"></view>
          </view>
          <text class="knowledge-rate">{{ item.correctRate }}%</text>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text>暂无知识点统计</text>
      </view>
    </view>

    <!-- 用时统计 -->
    <view class="section">
      <text class="section-title">答题用时</text>
      <view class="time-bars">
        <view class="time-bar-item">
          <view class="bar-label">总用时</view>
          <view class="bar-track">
            <view class="bar-fill" :style="{ width: timeUsagePercent + '%' }"></view>
          </view>
          <view class="bar-time">{{ result.timeUsed }}</view>
        </view>
      </view>
    </view>

    <!-- 错题列表 -->
    <view class="section" v-if="wrongQuestions.length > 0">
      <text class="section-title">错题回顾（{{ wrongQuestions.length }}题）</text>
      <view class="wrong-list">
        <view class="wrong-item" v-for="q in wrongQuestions" :key="q.id" @click="goDetail(q.id)">
          <view class="wrong-stem">{{ q.stem }}</view>
          <view class="wrong-info">
            <text class="wrong-type">{{ q.typeLabel }}</text>
            <text class="wrong-your">你的答案：{{ q.yourAnswer }}</text>
            <text class="wrong-correct">正确答案：{{ q.correctAnswer }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="actions">
      <button class="action-btn secondary" @click="reviewAll">查看全部解析</button>
      <button class="action-btn primary" @click="goHome">返回首页</button>
      <button class="action-btn accent" @click="retryWrong">错题重做</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { examApi } from '@/api'
import { toExamResultSummary, toResultWrongQuestions } from '@/api/contracts'
import { useExamStore } from '@/stores/exam'
import type { ExamResultSummary, ResultWrongQuestion } from '@/types/exam'

const examStore = useExamStore()
const result = ref<ExamResultSummary>({
  score: 0,
  correctCount: 0,
  totalCount: 0,
  correctRate: 0,
  timeUsed: '00:00',
})
const knowledgeAnalysis = ref<Record<string, { total: number; correct: number; correct_rate: number }>>({})
const isLoading = ref(false)

const passed = computed(() => result.value.correctRate >= 60)

const wrongQuestions = ref<ResultWrongQuestion[]>([])
const knowledgeItems = computed(() =>
  Object.entries(knowledgeAnalysis.value).map(([name, value]) => ({
    name,
    correctRate: value.correct_rate,
  })),
)
const timeUsagePercent = computed(() => {
  const [minutes, seconds] = result.value.timeUsed.split(':').map(Number)
  const usedSeconds = minutes * 60 + seconds
  const configuredSeconds = examStore.config.timeLimit * 60
  if (!configuredSeconds) return 100
  return Math.min(100, Math.max(6, Math.round((usedSeconds / configuredSeconds) * 100)))
})

const loadResult = async (paperId: number) => {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const payload = await examApi.getResult(paperId)
    result.value = toExamResultSummary(payload)
    wrongQuestions.value = toResultWrongQuestions(payload)
    knowledgeAnalysis.value = payload.knowledge_analysis
  } catch {
    // The shared request layer already displays the error message.
  } finally {
    isLoading.value = false
  }
}

onLoad((query) => {
  const paperId = Number(query?.paperId || examStore.paperId)
  if (!Number.isInteger(paperId) || paperId <= 0) {
    uni.showToast({ title: '未找到试卷结果', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 300)
    return
  }
  loadResult(paperId)
})

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/wrongbook/detail?questionId=${id}` })
}

const reviewAll = () => console.log('查看全部解析')
const goHome = () => uni.switchTab({ url: '/pages/index/index' })
const retryWrong = () => uni.navigateTo({ url: '/pages/wrongbook/redo' })
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; padding-bottom: 40rpx; }

.score-header {
  padding: 48rpx 32rpx 40rpx; text-align: center;
  background: linear-gradient(135deg, #10B981, #059669);
}
.score-header.failed { background: linear-gradient(135deg, #F59E0B, #D97706); }
.score-label { font-size: 32rpx; color: #fff; font-weight: 600; }
.score-ring {
  width: 160rpx; height: 160rpx; border-radius: 50%;
  border: 6rpx solid rgba(255,255,255,0.4);
  margin: 24rpx auto; display: flex;
  flex-direction: column; align-items: center; justify-content: center;
}
.score-num { font-size: 56rpx; font-weight: 700; color: #fff; line-height: 1; }
.score-unit { font-size: 24rpx; color: rgba(255,255,255,0.7); }
.score-stats { display: flex; justify-content: center; gap: 48rpx; }
.stat-item { text-align: center; }
.stat-value { font-size: 36rpx; font-weight: 700; color: #fff; display: block; }
.stat-desc { font-size: 22rpx; color: rgba(255,255,255,0.7); }

.section { margin: 24rpx 24rpx 0; }
.section-title { font-size: 28rpx; font-weight: 600; color: #1F2937; margin-bottom: 16rpx; display: block; }

.knowledge-list, .empty-state {
  background: #fff; border-radius: 16rpx; padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
.knowledge-item { display: flex; align-items: center; margin-bottom: 16rpx; }
.knowledge-item:last-child { margin-bottom: 0; }
.knowledge-name { width: 170rpx; font-size: 22rpx; color: #374151; }
.knowledge-track { flex: 1; height: 12rpx; background: #F3F4F6; border-radius: 6rpx; overflow: hidden; }
.knowledge-fill { height: 100%; background: #34D399; border-radius: 6rpx; }
.knowledge-rate { width: 72rpx; margin-left: 16rpx; text-align: right; font-size: 22rpx; color: #6B7280; }
.empty-state { font-size: 24rpx; color: #9CA3AF; text-align: center; }

.time-bars { background: #fff; border-radius: 16rpx; padding: 20rpx 24rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03); }
.time-bar-item { display: flex; align-items: center; margin-bottom: 12rpx; }
.time-bar-item:last-child { margin-bottom: 0; }
.bar-label { width: 80rpx; font-size: 22rpx; color: #6B7280; }
.bar-track { flex: 1; height: 12rpx; background: #F3F4F6; border-radius: 6rpx; margin: 0 16rpx; overflow: hidden; }
.bar-fill { height: 100%; background: #818CF8; border-radius: 6rpx; }
.bar-time { width: 60rpx; font-size: 22rpx; color: #6B7280; text-align: right; }

.wrong-list { display: flex; flex-direction: column; gap: 12rpx; }
.wrong-item {
  background: #fff; border-radius: 16rpx; padding: 20rpx 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03); border-left: 4rpx solid #EF4444;
}
.wrong-stem { font-size: 26rpx; color: #1F2937; line-height: 1.6; margin-bottom: 12rpx; }
.wrong-info { display: flex; gap: 24rpx; }
.wrong-type { font-size: 20rpx; color: #9CA3AF; }
.wrong-your { font-size: 20rpx; color: #EF4444; }
.wrong-correct { font-size: 20rpx; color: #10B981; }

.actions { padding: 32rpx 24rpx; display: flex; flex-direction: column; gap: 16rpx; }
.action-btn { border-radius: 48rpx; font-size: 30rpx; font-weight: 600; padding: 20rpx 0; border: none; text-align: center; }
.action-btn.primary { background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #fff; }
.action-btn.secondary { background: #EEF2FF; color: #4F46E5; }
.action-btn.accent { background: linear-gradient(135deg, #FEF3C7, #FDE68A); color: #92400E; }
</style>

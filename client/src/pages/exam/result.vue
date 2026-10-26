<template>
  <view class="page app-shell">
    <view v-if="isLoading || loadError" class="app-section"><c-app-state v-if="isLoading" state="loading" :title="t('正在整理本次练习')" /><c-app-state v-else state="error" :title="t('成绩暂时无法加载')" :description="loadError" @retry="loadResult()" /></view>
    <template v-else>
      <view class="app-section"><view class="score-header app-card app-card-pad">
        <text class="score-title">{{ t("本次练习已完成") }}</text><text class="score-subtitle">{{ getExamLabel(paperExamType) }} {{ t("· 自动判分与开放题自评分开记录") }}</text><text v-if="result.unansweredCount" class="score-subtitle">{{ t('本次有 {n} 题未作答', { n: result.unansweredCount }) }}</text>
        <view class="score-stats"><view class="stat-item"><text class="stat-value">{{ result.correctCount }}/{{ result.objectiveCount || 0 }}</text><text class="stat-label">{{ t("客观题答对") }}</text></view><view class="stat-item"><text class="stat-value">{{ result.objectiveCount ? result.correctRate + '%' : '—' }}</text><text class="stat-label">{{ t("客观题正确率") }}</text></view><view class="stat-item"><text class="stat-value">{{ result.timeUsed }}</text><text class="stat-label">{{ t("用时") }}</text></view></view>
      </view></view>
      <view v-if="result.subjectiveCount" class="app-section"><view class="app-card app-card-pad"><text class="app-section-title">{{ t("开放题自评") }}</text><text class="score-subtitle">{{ t('共 {total} 题，已作答 {answered} 题，{pending} 题待自评', { total: result.subjectiveCount, answered: result.subjectiveAnsweredCount || 0, pending: result.pendingSelfReview }) }}</text><text class="score-subtitle">{{ t('已自评得分：{score} / {max}。自评不会计入客观题正确率或自动错题。', { score: result.selfScore || 0, max: result.selfMaxScore || 0 }) }}</text></view></view>
      <view class="app-section" v-if="analysisItems.length"><text class="app-section-title">{{ t("客观题分析") }}</text><view class="analysis-card app-card"><view class="analysis-item" v-for="item in analysisItems" :key="item.name"><view class="analysis-top"><text>{{ item.name }}</text><text>{{ item.correct }}/{{ item.total }}</text></view><view class="analysis-track"><view class="analysis-fill" :style="{width:item.correctRate + '%'}" /></view></view></view></view>
      <view class="app-section" v-if="wrongQuestions.length"><text class="app-section-title">{{ t('错题回顾（{n} 题）', { n: wrongQuestions.length }) }}</text><view class="wrong-list"><view class="wrong-item app-card" v-for="q in wrongQuestions" :key="q.id" @tap="goDetail(q.id)"><text class="wrong-stem">{{ q.stem }}</text><text class="wrong-your">{{ t("你的答案：") }}{{ q.yourAnswer }}</text><text class="wrong-correct">{{ t("正确答案：") }}{{ q.correctAnswer }}</text></view></view></view>
      <view class="app-section"><t-button theme="default" variant="outline" block shape="round" @click="showReview = !showReview">{{ showReview ? t("收起题目与解析") : t("查看题目、解析与自评") }}</t-button></view>
      <view class="app-section" v-if="showReview"><view class="review-list"><view class="review-item app-card app-card-pad" v-for="(q,index) in reviewQuestions" :key="q.id">
        <text class="score-subtitle">{{ q.evaluationStatus === 'unanswered' ? t("未作答") : q.correct === null ? (q.selfScore == null ? t("待自评") : t('已自评') + ' ' + t('{n}分', { n: q.selfScore })) : q.correct ? t("回答正确") : t("需要巩固") }}</text>
        <c-question-item v-if="q.question" :question="q.question" :index="index" :user-answer="q.userAnswer" :show-result="true" :readonly="true" @self-review="selfReview(q.id, $event)" />
      </view></view></view>
      <view class="actions"><t-button theme="primary" block shape="round" @click="goHome">{{ t("返回首页") }}</t-button><t-button v-if="wrongQuestions.length" theme="default" variant="outline" block shape="round" @click="retryWrong">{{ t("错题重做") }}</t-button></view>
    </template>
  </view>
</template>
<script setup lang="ts">
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { ref } from 'vue'
import { onLoad, onShareAppMessage } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import { getExamLabel } from '@/constants/exam'
import { examApi } from '@/features/exam/api'
import { toExamResultSummary, toResultReviewQuestions, toResultWrongQuestions } from '@/api/contracts'
import { useExamStore } from '@/stores/exam'
import type { ExamResultSummary, ExamType, ResultReviewQuestion, ResultWrongQuestion } from '@/types/exam'

usePageI18n('pages/exam/result')
const examStore = useExamStore()
const resultPaperId = ref(0)
const isLoading = ref(true)
const loadError = ref('')
const paperExamType = ref<ExamType>('CSCA')
const showReview = ref(true)
const reviewQuestions = ref<ResultReviewQuestion[]>([])
const wrongQuestions = ref<ResultWrongQuestion[]>([])
const analysisItems = ref<Array<{name:string; total:number; correct:number; correctRate:number}>>([])
const result = ref<ExamResultSummary>({score:0, correctCount:0, totalCount:0, correctRate:0, timeUsed:'00:00'})
const selfReviewing = ref(false)
async function loadResult(quiet = false) {
  if (!resultPaperId.value) return
  if (!quiet) isLoading.value = true
  loadError.value = ''
  try {
    const payload = await examApi.getResult(resultPaperId.value)
    result.value = toExamResultSummary(payload)
    paperExamType.value = payload.paper.exam_type
    wrongQuestions.value = toResultWrongQuestions(payload)
    reviewQuestions.value = toResultReviewQuestions(payload).map(q => {
      if (q.question) Object.assign(q.question, {evaluationStatus:q.evaluationStatus, selfScore:q.selfScore})
      return q
    })
    analysisItems.value = Object.entries(payload.knowledge_analysis).map(([name,bucket]) => ({name, total:bucket.total, correct:bucket.correct, correctRate:bucket.correct_rate}))
  } catch { loadError.value = '请检查网络后重试。' } finally { isLoading.value = false }
}
async function selfReview(questionId:number, score:number) {
  if (selfReviewing.value) return
  selfReviewing.value = true
  try { await examApi.selfReview({paperId:resultPaperId.value, questionId, score}); await loadResult(true) } catch {} finally { selfReviewing.value = false }
}
onLoad(query => { resultPaperId.value = Number(query?.paperId || examStore.paperId); if (resultPaperId.value) loadResult(); else { isLoading.value = false; loadError.value = '未找到练习记录。' } })
const goHome = () => uni.switchTab({url:'/pages/index/index'})
const goDetail = (id:number) => uni.navigateTo({url:'/pages/wrongbook/detail?questionId=' + id})
const retryWrong = () => uni.navigateTo({url:'/pages/wrongbook/redo?examType=' + paperExamType.value})
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
// #endif
</script>
<style lang="scss" scoped>
.score-header {
  background: var(--app-surface);
}

.score-header.failed {
  background: var(--app-accent-soft);
}

.score-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.score-copy {
  flex: 1;
  min-width: 0;
}

.score-title {
  display: block;
  margin-top: 12rpx;
  font-size: 34rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.score-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--app-text-weak);
}

.score-ring-wrap {
  flex: none;
}

.score-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12rpx;
  margin-top: 20rpx;
}

.stat-item {
  padding: 16rpx 12rpx;
  border-radius: var(--app-radius-md);
  background: transparent;
  border: 0;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 32rpx;
  line-height: 1.1;
  font-weight: 600;
  color: var(--app-text);
}

.stat-label {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.analysis-head {
  margin-bottom: 16rpx;
}

.analysis-card,
.time-card {
  padding: 22rpx;
}

.analysis-item {
  margin-bottom: 16rpx;
}

.analysis-item:last-child {
  margin-bottom: 0;
}

.analysis-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14rpx;
  margin-bottom: 10rpx;
}

.analysis-name {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-text);
}

.analysis-rate {
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.analysis-track {
  height: 12rpx;
  background: var(--app-border);
  border-radius: 999px;
  overflow: hidden;
}

.analysis-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--app-secondary);
}

.analysis-desc {
  display: block;
  margin-top: 8rpx;
  font-size: var(--app-font-xs);
  color: var(--app-text-weak);
}

.time-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.bar-label {
  flex: none;
  width: 72rpx;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.bar-track {
  flex: 1;
  height: 12rpx;
  background: var(--app-border);
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--app-primary);
}

.bar-time {
  flex: none;
  width: 84rpx;
  text-align: right;
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.wrong-list,
.review-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.wrong-item {
  padding: 22rpx;
}

.wrong-stem {
  display: block;
  font-size: 26rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.wrong-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx 14rpx;
  margin-top: 12rpx;
}

.wrong-your,
.wrong-correct {
  font-size: var(--app-font-xs);
}

.wrong-your {
  color: var(--app-danger);
}

.wrong-correct {
  color: var(--app-success);
}

.review-item {
  padding: 22rpx;
}

.review-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-bottom: 14rpx;
}

.review-index {
  font-size: 22rpx;
  color: var(--app-text-weak);
}

.review-stem {
  display: block;
  font-size: 26rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.review-options {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-top: 14rpx;
}

.review-option {
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--app-text-weak);
}

.review-answer-row {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-top: 16rpx;
  padding-top: 14rpx;
  border-top: 1rpx solid var(--app-border);
  font-size: 22rpx;
  color: var(--app-danger);
}

.review-correct-answer {
  color: var(--app-success);
}

.review-analysis {
  margin-top: 14rpx;
  padding: 16rpx;
  border-radius: var(--app-radius-md);
  background: var(--app-surface-quiet);
  font-size: 24rpx;
  line-height: 1.65;
  color: var(--app-text-weak);
}

.actions {
  padding: 8rpx 24rpx 36rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}
</style>

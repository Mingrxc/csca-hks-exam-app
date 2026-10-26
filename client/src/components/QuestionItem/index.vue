<template>
  <view class="question-item">
    <view class="q-header">
      <view class="q-index-wrap">
        <text class="q-index">{{ t('第 {n} 题', { n: index + 1 }) }}</text>
        <text class="q-index-sub">{{ getExamLabel(question.examType) }} {{ question.level ? levelLabel(question.level) : '' }}</text>
        <text v-if="question.bankId" class="q-index-sub">{{ question.bankId }}</text>
      </view>
      <view class="q-tags">
        <t-tag theme="primary" variant="light" shape="round" size="small">{{ t(question.nativeTask || typeLabel) }}</t-tag>
        <t-tag theme="default" variant="light" shape="round" size="small">{{ t(diffLabel) }}</t-tag>
        <t-tag v-if="question.sourceType" theme="default" variant="light" size="small">{{ t(question.sourceType) }}</t-tag>
        <t-button v-if="!readonly" theme="default" variant="text" size="small" @click.stop="$emit('favorite')">{{ isFavorite ? t("已收藏") : t("收藏") }}</t-button>
      </view>
    </view>
    <text class="q-index-sub">{{ t(domainLabel) }} · {{ t(domainValue) }}</text>
    <text v-if="question.sourceLanguage && question.targetLanguage" class="q-index-sub">{{ t("翻译方向：") }}{{ t(languageLabel(question.sourceLanguage)) }} → {{ t(languageLabel(question.targetLanguage)) }}</text>
    <text v-if="question.stimulusNote" class="q-index-sub">{{ question.stimulusNote }}</text>
    <view v-if="question.stemAudio" class="media-card">
      <button class="audio-button" @tap="toggleAudio">{{ audioError ? t("重试播放") : playing ? t("暂停音频") : t("播放音频") }}</button>
      <text>{{ t(audioError) || (clock(audioPosition) + ' / ' + clock(audioDuration)) }}</text>
    </view>
    <view class="q-stem"><text user-select>{{ question.stem }}</text></view>
    <image v-if="question.stemImage" class="stem-image" :src="question.stemImage" mode="widthFix" @tap="preview(question.stemImage)" />
    <view class="q-options" v-if="question.options.length">
      <view class="option-item" :class="getOptionClass(opt.key)" v-for="opt in question.options" :key="opt.key" @click="!readonly && $emit('select', opt.key)">
        <view class="option-key">{{ opt.key }}</view>
        <view class="option-body">
          <image v-if="opt.image" class="option-image" :src="opt.image" mode="aspectFit" />
          <text v-if="opt.image" class="q-index-sub" @tap.stop="preview(opt.image)">{{ t("查看大图") }}</text>
          <text v-else class="option-text">{{ opt.text }}</text>
        </view>
        <text class="option-icon" v-if="showResult && opt.key === question.answer">✓</text>
        <text class="option-icon wrong" v-else-if="showResult && userAnswer === opt.key">✗</text>
      </view>
    </view>
    <view v-else-if="!readonly" class="written-answer">
      <text v-if="question.minimumCharacters" class="q-index-sub">{{ t('不少于 {n} 字', { n: question.minimumCharacters }) }}</text>
      <textarea class="response-input" :value="userAnswer" :maxlength="20000" :disabled="showResult || submitting" :auto-height="true" :placeholder="t('写下你的答案或思路')" @input="$emit('draft', $event.detail.value)" />
      <text class="q-index-sub">{{ t('已输入 {n} 字', { n: userAnswer.length }) }}</text>
      <button v-if="!showResult" class="submit-answer" :disabled="!userAnswer.trim() || submitting" @tap="$emit('submit', userAnswer)">{{ submitting ? t("正在保存…") : t("提交答案") }}</button>
    </view>
    <view v-if="readonly && userAnswer" class="media-card"><text user-select>{{ t("你的作答：") }}{{ userAnswer }}</text></view>
    <template v-if="showResult">
      <view v-if="!question.options.length" class="analysis"><text class="analysis-label">{{ t("参考答案") }}</text><text class="analysis-text" user-select>{{ question.answer }}</text></view>
      <view v-if="question.transcript" class="analysis"><text class="analysis-label">{{ t("听力原文") }}</text><text class="analysis-text" user-select>{{ question.transcript }}</text></view>
      <view v-if="question.termNotes" class="analysis"><text class="analysis-label">{{ t("术语参考") }}</text><text v-for="(note, term) in question.termNotes" :key="term" class="analysis-text">{{ term }}：{{ note }}</text></view>
      <view v-if="question.analysis" class="analysis"><text class="analysis-label">{{ t("解析") }}</text><text class="analysis-text" user-select>{{ question.analysis }}</text></view>
      <view v-if="question.gradingKeyPoints?.length" class="analysis">
        <text class="analysis-label">{{ t("评分要点") }}</text>
        <text v-for="(point, i) in question.gradingKeyPoints" :key="i" class="analysis-text">{{ i + 1 }}. {{ point }}</text>
        <view v-for="item in question.gradingRubric || []" :key="item.dimension" class="rubric-item"><text>{{ item.dimension }} ({{ t('{n}分', { n: item.max_score }) }})</text><text class="analysis-text">{{ item.criteria }}</text></view>
      </view>
      <view v-if="selfReview && question.evaluationStatus !== 'unanswered'" class="media-card self-review">
        <text class="analysis-label">{{ t('练习自评 · 满分 {n} 分', { n: question.maxScore || 10 }) }}</text>
        <text class="q-index-sub">{{ t("对照参考答案和评分要点自评，结果单独记录。") }}</text>
        <picker :range="scoreOptions" :value="Math.max(0, scoreOptions.indexOf(question.selfScore || 0))" @change="$emit('self-review', scoreOptions[Number($event.detail.value)])">
          <view class="score-picker">{{ question.selfScore != null ? t('当前自评：{n} 分（点击调整）', { n: question.selfScore }) : t("点击选择自评分") }}</view>
        </picker>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { t, levelLabel } from '@/i18n'
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { onHide } from '@dcloudio/uni-app'
import type { Question } from '@/types/exam'
import { DIFFICULTY_MAP, QUESTION_TYPE_MAP, getQuestionDomain, getQuestionDomainLabel, getExamLabel } from '@/constants/exam'
const props = defineProps<{ question: Question; index: number; userAnswer: string; showResult: boolean; isFavorite?: boolean; readonly?: boolean; submitting?: boolean }>()
defineEmits<{ (e: 'select', key: string): void; (e: 'favorite'): void; (e: 'draft', value: string): void; (e: 'submit', value: string): void; (e: 'self-review', score: number): void }>()
const typeLabel = computed(() => QUESTION_TYPE_MAP[props.question.type] || props.question.type)
const diffLabel = computed(() => DIFFICULTY_MAP[props.question.difficulty] || props.question.difficulty)
const domainLabel = computed(() => getQuestionDomainLabel(props.question.examType))
const domainValue = computed(() => getQuestionDomain(props.question))
const selfReview = computed(() => ['written_response', 'essay', 'short_answer', 'translation'].includes(props.question.responseMode || ''))
const scoreOptions = computed(() => Array.from({ length: Math.floor(props.question.maxScore || 10) + 1 }, (_, i) => i))
const playing = ref(false)
const audioError = ref('')
const audioPosition = ref(0)
const audioDuration = ref(0)
let audio: ReturnType<typeof uni.createInnerAudioContext> | undefined
function clock(seconds: number) { const value = Math.floor(seconds || 0); return Math.floor(value / 60) + ':' + String(value % 60).padStart(2, '0') }
function languageLabel(value: string) { return ({ en: '英语', zh: '中文' } as Record<string, string>)[value] || value }
function stopAudio() { if (audio) { audio.stop(); audio.destroy(); audio = undefined } playing.value = false; audioPosition.value = 0; audioDuration.value = 0; audioError.value = '' }
function toggleAudio() {
  if (!props.question.stemAudio) return
  if (!audio) {
    audio = uni.createInnerAudioContext()
    audio.src = props.question.stemAudio
    audio.onPlay(() => { playing.value = true; audioError.value = '' })
    audio.onPause(() => { playing.value = false })
    audio.onEnded(() => { playing.value = false; audioPosition.value = 0 })
    audio.onTimeUpdate(() => { audioPosition.value = audio?.currentTime || 0; audioDuration.value = audio?.duration || 0 })
    audio.onError(() => { playing.value = false; audioError.value = '音频暂时无法播放，请重试'; audio?.destroy(); audio = undefined })
  }
  if (playing.value) audio.pause()
  else audio.play()
}
function preview(url: string) { uni.previewImage({ urls: [url], current: url }) }
watch(() => props.question.id, stopAudio)
onHide(() => { audio?.pause(); playing.value = false })
onBeforeUnmount(stopAudio)
function getOptionClass(key: string) {
  return { selected: props.userAnswer === key && !props.showResult, correct: props.showResult && key === props.question.answer, wrong: props.showResult && props.userAnswer === key && key !== props.question.answer }
}
</script>

<style lang="scss" scoped>
.question-item {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.q-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18rpx;
  flex-wrap: wrap;
}

.q-index-wrap {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.q-index {
  font-size: 22rpx;
  font-weight: 600;
  color: var(--app-text-weak);
}

.q-index-sub {
  font-size: var(--app-font-xs);
  color: var(--app-text-mute);
}

.q-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10rpx;
}

.favorite-btn {
  min-width: 110rpx;
}

.q-stem {
  position: relative;
  padding: 16rpx 18rpx 16rpx 24rpx;
  border-radius: var(--app-radius-md);
  background: var(--app-surface-quiet);
  border: 1rpx solid rgba(201, 151, 118, 0.12);
  font-size: 30rpx;
  line-height: 1.8;
  color: var(--app-text);
}

.stem-ribbon {
  position: absolute;
  left: 0;
  top: 18rpx;
  bottom: 18rpx;
  width: 6rpx;
  border-radius: 999px;
  background: var(--app-primary);
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.option-item {
  display: flex;
  align-items: center;
  min-height: 96rpx;
  padding: 22rpx 20rpx;
  border-radius: var(--app-radius-md);
  border: 1rpx solid var(--app-border);
  background: rgba(255, 253, 249, 0.94);
}

.option-item.selected {
  border-color: rgba(184, 107, 75, 0.28);
  background: var(--app-primary-soft);
}

.option-item.correct {
  border-color: rgba(126, 154, 128, 0.26);
  background: #f0f6f1;
}

.option-item.wrong {
  border-color: rgba(198, 95, 82, 0.22);
  background: #fbefeb;
}

.option-key {
  width: 44rpx;
  height: 44rpx;
  border-radius: 999px;
  background: var(--app-surface-quiet);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  color: var(--app-text-weak);
}

.option-item.selected .option-key {
  background: var(--app-primary);
  color: #ffffff;
}

.option-item.correct .option-key {
  background: var(--app-success);
  color: #ffffff;
}

.option-item.wrong .option-key {
  background: var(--app-danger);
  color: #ffffff;
}

.option-text {
  flex: 1;
  margin-left: 12rpx;
  font-size: 28rpx;
  line-height: 1.7;
  color: var(--app-text);
}

.option-icon {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-success);
}

.option-icon.wrong {
  color: var(--app-danger);
}

.analysis {
  margin-top: 4rpx;
  padding: 18rpx;
  background: var(--app-secondary-soft);
  border-radius: var(--app-radius-md);
  border: 1rpx solid rgba(126, 154, 128, 0.12);
}

.analysis-label {
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-primary);
  display: block;
  margin-bottom: 8rpx;
}

.analysis-text {
  font-size: 24rpx;
  color: var(--app-text-weak);
  line-height: 1.7;
}

.q-stem, .analysis-text { white-space: pre-wrap; overflow-wrap: anywhere; }
.media-card, .written-answer { padding: 22rpx; border: 1rpx solid var(--app-border); border-radius: 22rpx; background: var(--app-surface); display: flex; flex-direction: column; gap: 18rpx; }
.audio-button, .submit-answer { margin: 0; border: 0; border-radius: 18rpx; color: #fff; background: var(--app-primary); font-size: 28rpx; }
.submit-answer[disabled] { opacity: .5; }
.response-input { width: 100%; min-height: 180rpx; font-size: 29rpx; line-height: 1.8; }
.stem-image { width: 100%; }
.option-body { flex: 1; min-width: 0; }
.option-image { width: 100%; height: 180rpx; }
.rubric-item { margin-top: 16rpx; }
.score-picker { padding: 18rpx; color: var(--app-primary); background: var(--app-primary-soft); border-radius: 14rpx; }

</style>

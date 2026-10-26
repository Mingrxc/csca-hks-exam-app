<template>
  <view class="page app-shell">
    <view class="app-section"><view class="hero app-card app-card-pad">
      <text class="hero-brand">{{ t("组卷中心") }}</text><text class="hero-title">{{ t(currentStrategy.title) }}</text>
      <text class="hero-subtitle">{{ t(currentStrategy.desc) }}</text>
    </view></view>
    <view class="app-section" v-if="catalogLoading || catalogError">
      <c-app-state v-if="catalogLoading" state="loading" :title="t('正在读取题库分类')" />
      <c-app-state v-else state="error" :title="t('分类暂时无法加载')" :description="catalogError" @retry="loadCatalog" />
    </view>
    <view v-else class="app-section config-list">
      <view class="config-card app-card"><text class="config-label">{{ t("考试类型") }}</text><view class="config-options">
        <view v-for="exam in ['CSCA', 'HKS']" :key="exam" class="option-tag" :class="{ active: form.examType === exam }" @tap="setExamType(exam)">{{ getExamLabel(exam) }}</view>
      </view></view>
      <template v-if="form.examType === 'HKS'">
        <view class="config-card app-card"><text class="config-label">{{ t("考试版本") }}</text><view class="config-options"><view v-for="version in versions" :key="version" class="option-tag" :class="{ active: form.examVersion === version }" @tap="form.examVersion = version">{{ version }}</view></view></view>
        <view class="config-card app-card"><text class="config-label">{{ t("考试等级") }}</text><view class="config-options"><view v-for="level in levels" :key="level" class="option-tag" :class="{ active: form.level === level }" @tap="selectLevel(level)">{{ levelLabel(level) }}</view></view></view>
      </template>
      <view v-if="form.examType === 'CSCA' || (form.level && !isRealStrategy)" class="config-card app-card">
        <text class="config-label">{{ form.examType === 'CSCA' ? t("科目") : t("考试模块") }}</text>
        <view class="config-options">
          <view v-if="form.examType === 'HKS' && strategyType === 'random'" class="option-tag" :class="{active: !form.subject}" @tap="selectSubject('')">{{ t("全部模块") }}</view>
          <view v-for="subject in subjects" :key="subject" class="option-tag" :class="{active: form.subject === subject}" @tap="selectSubject(subject)">{{ t(subject) }}</view>
        </view>
      </view>
      <view v-if="!isRealStrategy && form.subject && modules.length" class="config-card app-card"><text class="config-label">{{ t("知识模块") }}</text><picker :range="[t('全部模块'), ...modules.map(label => t(label))]" :value="form.knowledgeModule ? modules.indexOf(form.knowledgeModule)+1 : 0" @change="selectModule(Number($event.detail.value))"><view class="option-tag">{{ t(form.knowledgeModule || "全部模块") }} ›</view></picker></view>
      <view v-if="!isRealStrategy && form.subject && points.length" class="config-card app-card"><text class="config-label">{{ t("知识点") }}</text><picker :range="[t('全部知识点'), ...points.map(label => t(label))]" :value="form.knowledgePoint ? points.indexOf(form.knowledgePoint)+1 : 0" @change="form.knowledgePoint = Number($event.detail.value) ? points[Number($event.detail.value)-1] : ''"><view class="option-tag">{{ t(form.knowledgePoint || "全部知识点") }} ›</view></picker></view>
      <view v-if="!isRealStrategy" class="config-card app-card"><text class="config-label">{{ t("题目数量") }}</text><view class="config-options"><view v-for="count in QUESTION_COUNT_OPTIONS" :key="count" class="option-tag" :class="{active: form.questionCount === count}" @tap="form.questionCount = count">{{ t('{n}题', { n: count }) }}</view></view><text class="hero-subtitle">{{ t("共享材料按完整题组抽取，实际题量以组卷结果为准。") }}</text></view>
      <view v-if="!isRealStrategy && strategyType !== 'progressive'" class="config-card app-card"><text class="config-label">{{ t("难度") }}</text><view class="config-options"><view v-for="item in DIFFICULTY_OPTIONS" :key="item.value" class="option-tag" :class="{active: form.difficulty === item.value}" @tap="form.difficulty = item.value">{{ t(item.label) }}</view></view></view>
      <view v-if="!isRealStrategy" class="config-card app-card"><text class="config-label">{{ t("答题模式") }}</text><view class="config-options"><view class="option-tag" :class="{active: form.mode === 'practice'}" @tap="form.mode = 'practice'">{{ t("练习模式") }}</view><view class="option-tag" :class="{active: form.mode === 'exam'}" @tap="form.mode = 'exam'">{{ t("考试模式") }}</view></view></view>
      <view v-if="isRealStrategy || form.mode === 'exam'" class="config-card app-card"><text class="config-label">{{ t("限时（分钟）") }}</text><view class="config-options"><view v-for="time in TIME_LIMIT_OPTIONS" :key="time" class="option-tag" :class="{active: form.timeLimit === time}" @tap="form.timeLimit = time">{{ time }}</view></view><text class="hero-subtitle" v-if="isRealStrategy">{{ t("按所选等级的当前模块配置练习，不含口语与口译。") }}</text></view>
      <view v-if="!subjects.length && (form.examType === 'CSCA' || form.level)" class="config-card app-card">{{ t("当前筛选暂无可用题目。") }}</view>
    </view>
    <view class="footer"><view class="summary"><text>{{ getExamLabel(form.examType) }} {{ form.level ? levelLabel(form.level) : '' }} · {{ t(form.subject || "综合练习") }}</text></view><t-button theme="primary" block size="large" shape="round" :loading="isGenerating" :disabled="catalogLoading || !!catalogError" @click="startExam">{{ t("开始练习") }}</t-button></view>
  </view>
</template>
<script setup lang="ts">
import { showToast } from '@/i18n/ui'
import { t, levelLabel } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { computed, reactive, ref } from 'vue'
import { onLoad, onShareAppMessage } from '@dcloudio/uni-app'
import { createAppShareMessage } from '@/constants/share'
import { getExamLabel, PAPER_STRATEGY_MAP, DIFFICULTY_OPTIONS, QUESTION_COUNT_OPTIONS, TIME_LIMIT_OPTIONS } from '@/constants/exam'
import { questionApi } from '@/features/exam/api'
import { toQuestion } from '@/api/contracts'
import type { ApiCatalogItem } from '@/api/contracts'
import type { ExamType, PaperStrategy, DifficultyFilter, ExamMode } from '@/types/exam'
import { useExamStore } from '@/stores/exam'
import { confirmAction } from '@/shared/ui/confirm'

usePageI18n('pages/exam/paper')
const examStore = useExamStore()
const strategyType = ref<PaperStrategy>('random')
const catalog = ref<ApiCatalogItem[]>([])
const catalogLoading = ref(true)
const catalogError = ref('')
const isGenerating = ref(false)
const form = reactive({ examType: 'CSCA' as ExamType, examVersion: 'HSK3.0', level: '', subject: '', knowledgeModule: '', knowledgePoint: '', questionCount: 20, difficulty: 'all' as DifficultyFilter, mode: 'practice' as ExamMode, timeLimit: 60 })
const currentStrategy = computed(() => PAPER_STRATEGY_MAP[strategyType.value] || PAPER_STRATEGY_MAP.random)
const isRealStrategy = computed(() => strategyType.value === 'real')
const unique = (values: (string | undefined)[]) => [...new Set(values.filter(Boolean))] as string[]
const examRows = computed(() => catalog.value.filter(row => row.exam_type === form.examType))
const versions = computed(() => unique(examRows.value.map(row => row.exam_version)))
const levels = computed(() => unique(examRows.value.filter(row => row.exam_version === form.examVersion).map(row => row.level)).sort((a,b) => parseInt(a)-parseInt(b)))
const levelRows = computed(() => examRows.value.filter(row => form.examType === 'CSCA' || (row.exam_version === form.examVersion && row.level === form.level)))
const subjects = computed(() => unique(levelRows.value.map(row => row.subject)))
const subjectRows = computed(() => levelRows.value.filter(row => row.subject === form.subject))
const modules = computed(() => unique(subjectRows.value.map(row => row.knowledge_module)))
const points = computed(() => unique(subjectRows.value.filter(row => !form.knowledgeModule || row.knowledge_module === form.knowledgeModule).map(row => row.knowledge_point)))
function selectSubject(subject: string) { form.subject = subject; form.knowledgeModule = ''; form.knowledgePoint = '' }
function selectLevel(level: string) { form.level = level; selectSubject('') }
function selectModule(index: number) { form.knowledgeModule = index ? modules.value[index-1] : ''; form.knowledgePoint = '' }
function setExamType(value: string) { form.examType = value as ExamType; form.level = ''; selectSubject('') }
async function loadCatalog() {
  catalogLoading.value = true; catalogError.value = ''
  try { catalog.value = await questionApi.getCatalog() } catch { catalogError.value = '请检查网络后重试。' } finally { catalogLoading.value = false }
}
onLoad(async query => {
  if (query?.strategy && query.strategy in PAPER_STRATEGY_MAP) strategyType.value = query.strategy as PaperStrategy
  if (query?.examType === 'HKS' || query?.examType === 'CSCA') form.examType = query.examType
  if (examStore.config.examVersion) form.examVersion = examStore.config.examVersion
  if (examStore.config.level) form.level = examStore.config.level
  await loadCatalog()
  const initial = String(query?.special || query?.subject || '')
  if (subjects.value.includes(initial)) selectSubject(initial)
})
async function startExam() {
  if (isGenerating.value || catalogLoading.value || catalogError.value) return
  if (form.examType === 'HKS' && !form.level) { showToast({title: '请选择考试等级', icon: 'none'}); return }
  if ((form.examType === 'CSCA' || ['knowledge','progressive'].includes(strategyType.value)) && !form.subject) { showToast({title: '请选择科目或模块', icon:'none'}); return }
  if (examStore.hasActiveProgress && !await confirmAction({title:'开始新练习', content:'将替换本机保存的未完成练习，是否继续？'})) return
  isGenerating.value = true
  try {
    const config = { examType: form.examType, examVersion: form.examType === 'HKS' ? form.examVersion : undefined,
      level: form.examType === 'HKS' ? form.level : undefined,
      subjects: isRealStrategy.value && form.examType === 'HKS' ? [] : form.subject ? [form.subject] : [],
      knowledgeModules: !isRealStrategy.value && form.knowledgeModule ? [form.knowledgeModule] : [],
      knowledgePoints: !isRealStrategy.value && form.knowledgePoint ? [form.knowledgePoint] : [],
      questionCount: form.questionCount, difficulty: isRealStrategy.value || strategyType.value === 'progressive' ? 'all' : form.difficulty,
      mode: isRealStrategy.value ? 'exam' : form.mode, timeLimit: isRealStrategy.value || form.mode === 'exam' ? form.timeLimit : 0,
      strategy: strategyType.value }
    const paper = await questionApi.generatePaper(config)
    examStore.setConfig({ ...config, mode: config.mode as ExamMode, difficulty: config.difficulty as DifficultyFilter, questionCount: paper.questions.length })
    examStore.setPaper(paper.id, paper.questions.map(toQuestion)); examStore.start()
    uni.navigateTo({url:'/pages/exam/answer'})
  } catch {} finally { isGenerating.value = false }
}
// #ifdef MP-WEIXIN
onShareAppMessage(createAppShareMessage)
// #endif
</script>
<style lang="scss" scoped>
.hero {
  border-radius: var(--app-radius-lg);
  overflow: hidden;
}

.hero-head {
  display: flex;
  align-items: center;
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

.hero-visual {
  flex: none;
  width: 170rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.visual-main,
.visual-mini {
  border-radius: 22rpx;
  overflow: hidden;
  background: rgba(255, 251, 246, 0.9);
  border: 1rpx solid rgba(201, 151, 118, 0.14);
  box-shadow: var(--app-shadow-sm);
}

.visual-main {
  padding: 18rpx 16rpx;
  text-align: center;
}

.visual-value {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: var(--app-primary);
}

.visual-label {
  display: block;
  margin-top: 4rpx;
  font-size: var(--app-font-xs);
  color: var(--app-text-weak);
}

.visual-stack {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10rpx;
}

.visual-mini {
  padding: 12rpx 8rpx;
  text-align: center;
}

.visual-mini-value {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: var(--app-text);
}

.visual-mini-label {
  display: block;
  margin-top: 4rpx;
  font-size: var(--app-font-xs);
  white-space: nowrap;
  color: var(--app-text-weak);
}

.hero-band {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 18rpx;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.config-card {
  padding: 22rpx;
}

.config-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 14rpx;
}

.config-label {
  display: block;
  font-size: 28rpx;
  line-height: 1.4;
  font-weight: 600;
  color: var(--app-text);
}

.config-note {
  flex: none;
  font-size: var(--app-font-xs);
  color: var(--app-text-mute);
}

.config-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.option-tag {
  min-height: 72rpx;
  padding: 18rpx 24rpx;
  border-radius: var(--app-radius-md);
  background: var(--app-surface);
  color: var(--app-text);
  font-size: 24rpx;
  line-height: 1.35;
  border: 1rpx solid var(--app-border);
}

.option-tag.active {
  background: var(--app-primary);
  color: #fffaf3;
  border-color: var(--app-primary);
  box-shadow: none;
  font-weight: 600;
}

.footer {
  position: sticky;
  bottom: 0;
  z-index: 5;
  margin-top: 28rpx;
  padding: 20rpx 28rpx calc(24rpx + env(safe-area-inset-bottom));
  background: var(--app-bg);
  border-top: 1rpx solid var(--app-border);
}

.summary {
  margin-bottom: 14rpx;
  text-align: center;
  font-size: 22rpx;
  line-height: 1.5;
  color: var(--app-text-weak);
}
</style>

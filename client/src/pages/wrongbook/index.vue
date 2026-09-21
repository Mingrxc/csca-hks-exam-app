<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-card app-card-soft app-card-pad">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">错题本</text>
            <text class="hero-title">把容易错的地方收拢起来</text>
            <text class="hero-subtitle">先筛选，再复习，最后重做，顺着来会更清楚。</text>
          </view>
          <t-tag theme="danger" variant="light" shape="round">{{ wrongList.length }}</t-tag>
        </view>
      </view>
    </view>

    <view class="app-section filter-section">
      <view class="filter-bar app-card">
        <view class="filter-tabs">
          <view
            class="filter-tab"
            :class="{ active: activeTab === t.key }"
            v-for="t in tabs"
            :key="t.key"
            @click="selectTab(t.key)"
          >
            {{ t.label }}
          </view>
        </view>
        <t-button theme="default" variant="text" size="small" shape="round" @click="showFilters = true">
          {{ activeFilterLabel }}
        </t-button>
      </view>
    </view>

    <view class="filter-dropdown" v-if="showFilters">
      <view class="dropdown-section">
        <text class="dropdown-title">考试类型</text>
        <view class="dropdown-tags">
          <view
            class="dropdown-tag"
            :class="{ active: filters.examType === 'all' }"
            @click="setExamTypeFilter('all')"
          >全部</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.examType === 'CSCA' }"
            @click="setExamTypeFilter('CSCA')"
          >CSCA</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.examType === 'HKS' }"
            @click="setExamTypeFilter('HKS')"
          >HKS</view>
        </view>
      </view>
      <view class="dropdown-section">
        <text class="dropdown-title">{{ specialLabel }}</text>
        <view class="dropdown-tags">
          <view
            class="dropdown-tag"
            :class="{ active: filters.knowledge === 'all' }"
            @click="filters.knowledge = 'all'; applyFilters()"
          >全部</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.knowledge === k }"
            v-for="k in specialOptions"
            :key="k"
            @click="filters.knowledge = k; applyFilters()"
          >{{ k }}</view>
        </view>
      </view>
      <view class="dropdown-section">
        <text class="dropdown-title">错误次数</text>
        <view class="dropdown-tags">
          <view
            class="dropdown-tag"
            :class="{ active: filters.wrongCount === 'all' }"
            @click="filters.wrongCount = 'all'; applyFilters()"
          >全部</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.wrongCount === '1' }"
            @click="filters.wrongCount = '1'; applyFilters()"
          >1次</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.wrongCount === '2+' }"
            @click="filters.wrongCount = '2+'; applyFilters()"
          >2次及以上</view>
        </view>
      </view>
      <view class="dropdown-actions">
        <t-button class="dropdown-btn" theme="default" variant="outline" shape="round" @click="resetFilters">重置</t-button>
        <t-button class="dropdown-btn" theme="primary" shape="round" @click="showFilters = false">确定</t-button>
      </view>
    </view>

    <view class="app-section" v-if="wrongList.length > 0">
      <view class="stats-bar app-card">
        <text class="stats-text">共 {{ wrongList.length }} 道错题</text>
        <text class="stats-text">{{ masteredCount }} 道已掌握</text>
      </view>
    </view>

    <view class="app-section">
      <view class="wrong-list">
        <view class="wrong-card app-card" v-for="item in wrongList" :key="item.id" @click="goDetail(item.id)">
          <view class="card-header">
          <view class="card-tags">
            <t-tag theme="primary" variant="light" shape="round" size="small">{{ item.examType }}</t-tag>
            <t-tag theme="warning" variant="light" shape="round" size="small">{{ domainLabel(item) }}·{{ domainValue(item) }}</t-tag>
            <t-tag theme="default" variant="light" shape="round" size="small">{{ item.typeLabel }}</t-tag>
            <t-tag :theme="item.mastered ? 'success' : 'danger'" variant="light" shape="round" size="small">
              {{ item.mastered ? '已掌握' : `错${item.wrongCount}次` }}
            </t-tag>
            </view>
          </view>
          <text class="card-stem">{{ item.stem }}</text>
          <view class="card-footer">
            <text class="card-date">{{ item.lastWrongAt }}</text>
            <text class="card-action">查看详情 ›</text>
          </view>
        </view>
      </view>

      <t-empty v-if="!isLoading && wrongList.length === 0" description="太棒了！没有错题" />
    </view>

    <view class="footer-actions" v-if="wrongList.length > 0">
      <t-button class="footer-btn" theme="primary" block shape="round" @click="goRedo">错题重做</t-button>
      <t-button class="footer-btn" theme="default" variant="outline" block shape="round" @click="exportPdf">导出 PDF</t-button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { questionApi } from '@/features/exam/api'
import { wrongBookApi } from '@/features/wrongbook/api'
import { toWrongBookListItem } from '@/api/contracts'
import {
  CSCA_SUBJECT_OPTIONS,
  HSK_KNOWLEDGE_OPTIONS,
  getQuestionDomain,
  getQuestionDomainLabel,
  getSpecialLabel,
} from '@/constants/exam'
import type { WrongBookListItem } from '@/types/wrongbook'
import type { ExamType } from '@/types/exam'

const activeTab = ref('all')
const showFilters = ref(false)
const isLoading = ref(false)

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'CSCA', label: 'CSCA' },
  { key: 'HKS', label: 'HKS' },
]

const filters = reactive({
  examType: 'all',
  knowledge: 'all',
  wrongCount: 'all',
})
const specialFetched = reactive<Record<ExamType, boolean>>({
  CSCA: false,
  HKS: false,
})
const specialOptionsByExam = reactive<Record<ExamType, string[]>>({
  CSCA: [...CSCA_SUBJECT_OPTIONS],
  HKS: [...HSK_KNOWLEDGE_OPTIONS],
})

const specialLabel = computed(() => {
  if (filters.examType === 'CSCA') return getSpecialLabel('CSCA')
  if (filters.examType === 'HKS') return getSpecialLabel('HKS')
  return '专项'
})

const specialOptions = computed(() => {
  if (filters.examType === 'CSCA') return specialOptionsByExam.CSCA
  if (filters.examType === 'HKS') return specialOptionsByExam.HKS
  return Array.from(new Set([...specialOptionsByExam.CSCA, ...specialOptionsByExam.HKS]))
})

const activeFilterLabel = computed(() => {
  const parts = []
  if (filters.examType !== 'all') parts.push(filters.examType)
  if (filters.knowledge !== 'all') parts.push(filters.knowledge)
  if (filters.wrongCount !== 'all') parts.push(filters.wrongCount === '1' ? '错1次' : '错2次+')
  return parts.length > 0 ? parts.join(' · ') : '筛选'
})

const wrongList = ref<WrongBookListItem[]>([])

const masteredCount = computed(() => wrongList.value.filter((w) => w.mastered).length)

const domainLabel = (item: WrongBookListItem) => getQuestionDomainLabel(item.examType)
const domainValue = (item: WrongBookListItem) => getQuestionDomain(item)

const loadSpecialOptions = async (examType: ExamType) => {
  if (specialFetched[examType]) return
  try {
    const options = await questionApi.getSpecialOptions(examType)
    specialOptionsByExam[examType] = options.map((item) => item.label || item.value).filter(Boolean)
  } catch {
    specialOptionsByExam[examType] =
      examType === 'CSCA' ? [...CSCA_SUBJECT_OPTIONS] : [...HSK_KNOWLEDGE_OPTIONS]
  } finally {
    specialFetched[examType] = true
  }
}

const loadWrongList = async () => {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const items = await wrongBookApi.getList({
      examType: filters.examType,
      knowledge: filters.knowledge,
      wrongCount: filters.wrongCount,
    })
    wrongList.value = items.map(toWrongBookListItem)
  } catch {
    // The shared request layer already displays the error message.
  } finally {
    isLoading.value = false
  }
}

const setExamTypeFilter = (tab: 'all' | ExamType) => {
  if (filters.examType === tab) {
    activeTab.value = tab
    return
  }
  activeTab.value = tab
  filters.examType = tab
  filters.knowledge = 'all'
  loadWrongList()
}

const selectTab = (tab: string) => {
  setExamTypeFilter(tab as 'all' | ExamType)
}

const applyFilters = () => {
  loadWrongList()
}

const resetFilters = () => {
  filters.examType = 'all'
  filters.knowledge = 'all'
  filters.wrongCount = 'all'
  activeTab.value = 'all'
  showFilters.value = false
  loadWrongList()
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/wrongbook/detail?id=${id}` })
}

const goRedo = () => {
  if (filters.examType === 'CSCA' || filters.examType === 'HKS') {
    openRedo(filters.examType)
    return
  }

  uni.showActionSheet({
    itemList: ['CSCA 错题', 'HKS 错题'],
    success: ({ tapIndex }) => openRedo(tapIndex === 0 ? 'CSCA' : 'HKS'),
  })
}

const openRedo = (examType: ExamType) => {
  uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${examType}` })
}

const exportPdf = async () => {
  uni.showLoading({ title: '正在生成...', mask: true })
  try {
    const filePath = await wrongBookApi.exportPdf({
      examType: filters.examType,
      knowledge: filters.knowledge,
      wrongCount: filters.wrongCount,
    })
    await new Promise<void>((resolve, reject) => {
      uni.openDocument({
        filePath,
        fileType: 'pdf',
        showMenu: true,
        success: () => resolve(),
        fail: reject,
      })
    })
  } catch {
    uni.showToast({ title: 'PDF 导出失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

void loadSpecialOptions('CSCA')
void loadSpecialOptions('HKS')

onShow(loadWrongList)
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

.filter-section {
  margin-top: 18rpx;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 18rpx 20rpx;
}

.filter-tabs {
  display: flex;
  gap: 10rpx;
}

.filter-tab {
  padding: 8rpx 18rpx;
  border-radius: 999px;
  background: #f8efe4;
  color: var(--app-text-weak);
  font-size: 23rpx;
}

.filter-tab.active {
  background: var(--app-primary-soft);
  color: var(--app-primary);
  font-weight: 600;
}

.filter-dropdown {
  margin: 14rpx 24rpx 0;
  padding: 20rpx;
  border: 1rpx solid var(--app-border);
  border-radius: var(--app-radius-lg);
  background: #fffaf3;
  box-shadow: var(--app-shadow-sm);
}

.dropdown-section {
  margin-bottom: 20rpx;
}

.dropdown-section:last-child {
  margin-bottom: 0;
}

.dropdown-title {
  display: block;
  margin-bottom: 12rpx;
  font-size: 24rpx;
  color: var(--app-text-weak);
}

.dropdown-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.dropdown-tag {
  padding: 8rpx 18rpx;
  border-radius: 999px;
  background: #f8efe4;
  color: var(--app-text-weak);
  font-size: 22rpx;
}

.dropdown-tag.active {
  background: var(--app-primary-soft);
  color: var(--app-primary);
}

.dropdown-actions {
  display: flex;
  gap: 12rpx;
}

.dropdown-btn {
  flex: 1;
}

.stats-bar {
  display: flex;
  justify-content: space-between;
  gap: 16rpx;
  padding: 18rpx 20rpx;
  color: var(--app-text-weak);
  font-size: 22rpx;
  background: rgba(255, 251, 246, 0.92);
}

.wrong-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.wrong-card {
  padding: 22rpx;
}

.card-header {
  margin-bottom: 14rpx;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.card-stem {
  display: block;
  font-size: 26rpx;
  line-height: 1.65;
  color: var(--app-text);
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 14rpx;
}

.card-date {
  font-size: 21rpx;
  color: var(--app-text-mute);
}

.card-action {
  font-size: 22rpx;
  color: var(--app-primary);
}

.footer-actions {
  display: flex;
  gap: 12rpx;
  padding: 8rpx 24rpx 36rpx;
}

.footer-btn {
  flex: 1;
}

.error-card {
  padding: 24rpx;
  text-align: center;
  color: var(--app-danger);
  background: var(--app-danger-soft);
}
</style>

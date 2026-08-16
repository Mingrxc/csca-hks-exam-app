<template>
  <view class="page">
    <!-- 筛选栏 -->
    <view class="filter-bar">
      <view class="filter-tabs">
        <view
          class="filter-tab"
          :class="{ active: activeTab === t.key }"
          v-for="t in tabs"
          :key="t.key"
          @click="selectTab(t.key)"
        >{{ t.label }}</view>
      </view>
      <view class="filter-more" @click="showFilters = true">
        <text>{{ activeFilterLabel }}</text>
        <text class="filter-arrow">▾</text>
      </view>
    </view>

    <!-- 筛选下拉 -->
    <view class="filter-dropdown" v-if="showFilters">
      <view class="dropdown-section">
        <text class="dropdown-title">考试类型</text>
        <view class="dropdown-tags">
          <view
            class="dropdown-tag"
            :class="{ active: filters.examType === 'all' }"
            @click="filters.examType = 'all'; applyFilters()"
          >全部</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.examType === 'CSCA' }"
            @click="filters.examType = 'CSCA'; applyFilters()"
          >CSCA</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.examType === 'HKS' }"
            @click="filters.examType = 'HKS'; applyFilters()"
          >HKS</view>
        </view>
      </view>
      <view class="dropdown-section">
        <text class="dropdown-title">知识点</text>
        <view class="dropdown-tags">
          <view
            class="dropdown-tag"
            :class="{ active: filters.knowledge === 'all' }"
            @click="filters.knowledge = 'all'; applyFilters()"
          >全部</view>
          <view
            class="dropdown-tag"
            :class="{ active: filters.knowledge === k }"
            v-for="k in knowledgePoints"
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
        <button class="dropdown-btn reset" @click="resetFilters">重置</button>
        <button class="dropdown-btn confirm" @click="showFilters = false">确定</button>
      </view>
    </view>

    <!-- 错题统计 -->
    <view class="stats-bar" v-if="wrongList.length > 0">
      <text class="stats-text">共 {{ wrongList.length }} 道错题</text>
      <text class="stats-text">{{ masteredCount }} 道已掌握</text>
    </view>

    <!-- 错题列表 -->
    <view class="list">
      <view class="wrong-card" v-for="item in wrongList" :key="item.id" @click="goDetail(item.id)">
        <view class="card-header">
          <view class="card-tags">
            <text class="card-tag exam">{{ item.examType }}</text>
            <text class="card-tag type">{{ item.typeLabel }}</text>
            <text class="card-tag diff" :class="item.difficulty">{{ item.diffLabel }}</text>
            <text class="card-tag point">{{ item.knowledgePoint }}</text>
          </view>
          <view class="card-status" :class="{ mastered: item.mastered }">
            {{ item.mastered ? '已掌握' : '错' + item.wrongCount + '次' }}
          </view>
        </view>
        <text class="card-stem">{{ item.stem }}</text>
        <view class="card-footer">
          <text class="card-date">{{ item.lastWrongAt }}</text>
          <text class="card-action">查看详情 →</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="!isLoading && wrongList.length === 0">
      <text class="empty-icon">🎉</text>
      <text class="empty-title">太棒了！没有错题</text>
      <text class="empty-desc">继续保持，你是最棒的</text>
    </view>

    <!-- 底部操作 -->
    <view class="footer-actions" v-if="wrongList.length > 0">
      <button class="footer-btn" @click="goRedo">错题重做</button>
      <button class="footer-btn outline" @click="exportPdf">导出 PDF</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { wrongBookApi } from '@/api'
import { toWrongBookListItem } from '@/api/contracts'
import { WRONG_BOOK_KNOWLEDGE_POINTS } from '@/constants/exam'
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

const knowledgePoints = WRONG_BOOK_KNOWLEDGE_POINTS

const filters = reactive({
  examType: 'all',
  knowledge: 'all',
  wrongCount: 'all',
})

const activeFilterLabel = computed(() => {
  const parts = []
  if (filters.examType !== 'all') parts.push(filters.examType)
  if (filters.knowledge !== 'all') parts.push(filters.knowledge)
  if (filters.wrongCount !== 'all') parts.push(filters.wrongCount === '1' ? '错1次' : '错2次+')
  return parts.length > 0 ? parts.join(' · ') : '筛选'
})

const wrongList = ref<WrongBookListItem[]>([])

const masteredCount = computed(() => wrongList.value.filter(w => w.mastered).length)

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

const selectTab = (tab: string) => {
  activeTab.value = tab
  filters.examType = tab
  loadWrongList()
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

onShow(loadWrongList)
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; padding-bottom: 120rpx; background: #F5F5F7; }

.filter-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16rpx 24rpx; background: #fff; border-bottom: 1rpx solid #E5E7EB;
  position: sticky; top: 0; z-index: 10;
}
.filter-tabs { display: flex; gap: 8rpx; }
.filter-tab { padding: 8rpx 24rpx; border-radius: 20rpx; font-size: 24rpx; background: #F3F4F6; color: #6B7280; }
.filter-tab.active { background: #EEF2FF; color: #4F46E5; font-weight: 600; }
.filter-more { font-size: 24rpx; color: #4F46E5; display: flex; align-items: center; gap: 4rpx; }
.filter-arrow { font-size: 20rpx; }

.filter-dropdown {
  background: #fff; padding: 24rpx; border-bottom: 1rpx solid #E5E7EB;
}
.dropdown-section { margin-bottom: 20rpx; }
.dropdown-title { font-size: 24rpx; color: #9CA3AF; display: block; margin-bottom: 12rpx; }
.dropdown-tags { display: flex; flex-wrap: wrap; gap: 12rpx; }
.dropdown-tag {
  padding: 8rpx 24rpx; border-radius: 16rpx; font-size: 22rpx;
  background: #F3F4F6; color: #6B7280;
}
.dropdown-tag.active { background: #EEF2FF; color: #4F46E5; }
.dropdown-actions { display: flex; gap: 16rpx; }
.dropdown-btn { flex: 1; border-radius: 24rpx; font-size: 26rpx; padding: 12rpx 0; border: none; text-align: center; }
.dropdown-btn.reset { background: #F3F4F6; color: #374151; }
.dropdown-btn.confirm { background: #4F46E5; color: #fff; }

.stats-bar {
  display: flex; justify-content: space-between;
  padding: 16rpx 24rpx; font-size: 22rpx; color: #9CA3AF;
}

.list { padding: 0 24rpx; }
.wrong-card {
  background: #fff; border-radius: 16rpx; padding: 24rpx;
  margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.card-tags { display: flex; flex-wrap: wrap; gap: 8rpx; }
.card-tag { padding: 2rpx 12rpx; border-radius: 8rpx; font-size: 20rpx; }
.card-tag.exam { background: #ECFDF5; color: #047857; }
.card-tag.type { background: #DBEAFE; color: #1E40AF; }
.card-tag.diff { background: #F3F4F6; color: #6B7280; }
.card-tag.diff.hard { background: #FEE2E2; color: #991B1B; }
.card-tag.point { background: #F3F4F6; color: #6B7280; }
.card-status { font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 12rpx; background: #FEE2E2; color: #991B1B; }
.card-status.mastered { background: #D1FAE5; color: #065F46; }
.card-stem { font-size: 26rpx; color: #1F2937; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; margin-top: 16rpx; }
.card-date { font-size: 22rpx; color: #9CA3AF; }
.card-action { font-size: 22rpx; color: #4F46E5; }

.empty-state { padding: 120rpx 0; text-align: center; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 20rpx; }
.empty-title { font-size: 30rpx; font-weight: 600; color: #1F2937; display: block; margin-bottom: 8rpx; }
.empty-desc { font-size: 24rpx; color: #9CA3AF; }

.footer-actions {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 20rpx 24rpx 40rpx; background: #fff;
  box-shadow: 0 -2rpx 12rpx rgba(0,0,0,0.06);
  display: flex; gap: 16rpx;
}
.footer-btn {
  flex: 1; border-radius: 48rpx; font-size: 28rpx; font-weight: 600;
  padding: 20rpx 0; border: none; text-align: center;
  background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #fff;
}
.footer-btn.outline { background: #fff; color: #4F46E5; border: 2rpx solid #4F46E5; }
</style>

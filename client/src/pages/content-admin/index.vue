<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-heading">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">内容管理</text>
            <text class="hero-title">维护内容与更新公告</text>
            <text class="hero-subtitle">更新公告发布后会显示在“关于”中。</text>
          </view>
          <t-tag theme="primary" variant="light" shape="round">{{ items.length }}</t-tag>
        </view>
      </view>
    </view>

    <view v-if="loading || loadError" class="app-section">
      <view class="app-card"><c-app-state :state="loading ? 'loading' : 'error'" :title="loading ? '正在加载内容' : '暂时无法访问内容管理'" description="仅配置了管理权限的账号可以维护内容。" @retry="load" /></view>
    </view>
    <view v-else class="app-section">
      <view class="form-card app-card app-card-pad">
        <picker :range="categoryOptions" range-key="label" @change="changeCategory">
          <view class="field picker">{{ categoryLabel }}</view>
        </picker>
        <view class="switch-row"><text>作为更新公告展示</text><switch :checked="isAnnouncement" :disabled="saving" color="#b86b4b" @change="toggleAnnouncement" /></view>
        <input v-if="isAnnouncement" v-model="form.release_version" class="native-field" :disabled="saving" maxlength="24" placeholder="版本号，例如 1.5.1" />
        <input v-model="form.title" class="native-field" :disabled="saving" maxlength="128" placeholder="标题" />
        <input v-model="form.summary" class="native-field" :disabled="saving" maxlength="255" placeholder="摘要" />
        <textarea v-model="form.body" class="native-field native-body" :disabled="saving" maxlength="12000" placeholder="正文" />
        <view class="switch-row"><text>{{ form.is_active ? '发布展示' : '仅保存草稿' }}</text><switch :checked="form.is_active" :disabled="saving" color="#b86b4b" @change="togglePublished" /></view>
        <view class="form-actions">
          <t-button theme="default" variant="outline" shape="round" :disabled="saving" @click="reset">新建</t-button>
          <t-button theme="primary" shape="round" :loading="saving" :disabled="saving" @click="save">
            {{ form.is_active ? '保存并发布' : '保存草稿' }}
          </t-button>
        </view>
      </view>
    </view>

    <view v-if="!loading && !loadError" class="app-section">
      <view v-for="item in items" :key="item.id" class="content-item app-card">
        <view class="content-head">
          <text class="content-title">{{ item.release_version ? 'v' + item.release_version + ' · ' : '' }}{{ item.title }}</text>
          <t-tag :theme="item.is_active ? 'success' : 'default'" variant="light" shape="round" size="small">
            {{ item.is_active ? '已启用' : '已停用' }}
          </t-tag>
        </view>
        <text class="content-summary">{{ item.summary }}</text>
        <view class="content-actions">
          <t-button theme="default" variant="outline" size="small" shape="round" @click="edit(item)">编辑</t-button>
          <t-button theme="danger" variant="outline" size="small" shape="round" @click="remove(item.id)">删除</t-button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { contentApi } from '@/features/content/api'
import type { ApiContentItem } from '@/api/contracts'
import { APP_VERSION } from '@/constants/brand'

const categoryOptions = [
  { value: 'consulting', label: '留学资讯' },
  { value: 'club', label: '社团信息' },
  { value: 'ad', label: '合作广告' },
  { value: 'notice', label: '通知 / 更新公告' },
] as const
const items = ref<ApiContentItem[]>([])
const editingId = ref<number | null>(null)
const saving = ref(false)
const loading = ref(false)
const loadError = ref(false)
const isAnnouncement = ref(false)
const categoryIndex = ref(0)
const form = reactive({
  category: 'consulting' as ApiContentItem['category'],
  title: '',
  summary: '',
  body: '',
  release_version: '',
  published_at: null as string | null,
  is_active: true,
  sort_order: 0,
})
const categoryLabel = computed(() => categoryOptions[categoryIndex.value].label)

const load = async () => {
  if (loading.value) return
  loading.value = true
  loadError.value = false
  try {
    items.value = await contentApi.listAdmin()
  } catch { loadError.value = true }
  finally { loading.value = false }
}

const changeCategory = (event: any) => {
  categoryIndex.value = Number(event.detail.value)
  form.category = categoryOptions[categoryIndex.value].value
  if (form.category !== 'notice') isAnnouncement.value = false
}

const toggleAnnouncement = (event: any) => {
  isAnnouncement.value = !!event.detail.value
  if (isAnnouncement.value) {
    categoryIndex.value = categoryOptions.findIndex((option) => option.value === 'notice')
    form.category = 'notice'
    form.release_version ||= APP_VERSION
  }
}

const togglePublished = (event: any) => { form.is_active = !!event.detail.value }

const reset = () => {
  if (saving.value) return
  editingId.value = null
  categoryIndex.value = 0
  isAnnouncement.value = false
  Object.assign(form, { category: 'consulting', title: '', summary: '', body: '', release_version: '', published_at: null, is_active: true, sort_order: 0 })
}

const edit = (item: ApiContentItem) => {
  if (saving.value) return
  editingId.value = item.id
  categoryIndex.value = categoryOptions.findIndex((option) => option.value === item.category)
  Object.assign(form, {
    category: item.category,
    title: item.title,
    summary: item.summary,
    body: item.body,
    release_version: item.release_version || '',
    published_at: item.published_at || null,
    is_active: item.is_active,
    sort_order: item.sort_order,
  })
  isAnnouncement.value = !!item.release_version
}

const save = async () => {
  if (saving.value) return
  if (!form.title.trim() || !form.summary.trim() || !form.body.trim()) {
    uni.showToast({ title: '请填写完整内容', icon: 'none' })
    return
  }
  if (isAnnouncement.value && !/^\d+\.\d+\.\d+$/.test(form.release_version.trim())) {
    uni.showToast({ title: '请填写正确版本号，例如 1.5.1', icon: 'none' })
    return
  }
  saving.value = true
  try {
    const payload = { ...form, release_version: isAnnouncement.value ? form.release_version.trim() : null }
    if (editingId.value) await contentApi.update(editingId.value, payload)
    else await contentApi.create(payload)
    saving.value = false
    reset()
    await load()
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch {
  } finally {
    saving.value = false
  }
}

const remove = (id: number) => {
  if (saving.value) return
  uni.showModal({
    title: '删除内容',
    content: '确定删除这条内容吗？',
    success: async (result: any) => {
      if (!result.confirm) return
      try {
        await contentApi.remove(id)
        await load()
      } catch {}
    },
  })
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

.form-card {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.native-field { display: block; width: 100%; min-height: 82rpx; padding: 18rpx 20rpx; border: 1rpx solid var(--app-border); border-radius: 16rpx; background: var(--app-surface); color: var(--app-text); font-size: 26rpx; }
.native-body { height: 340rpx; line-height: 1.8; }
.switch-row { display: flex; align-items: center; justify-content: space-between; gap: 20rpx; font-size: 25rpx; color: var(--app-text-weak); }

.field {
  width: 100%;
  box-sizing: border-box;
  padding: 0;
}

.picker {
  padding: 18rpx 20rpx;
  border: 1rpx solid var(--app-border);
  border-radius: var(--app-radius-md);
  color: var(--app-primary);
  font-size: 24rpx;
  background: var(--app-surface);
}

.body {
  min-height: 220rpx;
}

.form-actions,
.content-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12rpx;
}

.content-item {
  padding: 22rpx;
  margin-top: 14rpx;
}

.content-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.content-title {
  flex: 1;
  font-size: 28rpx;
  line-height: 1.45;
  font-weight: 600;
  color: var(--app-text);
}

.content-summary {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.65;
  color: var(--app-text-weak);
}

.content-actions {
  margin-top: 16rpx;
}
</style>

<template>
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-card app-card-soft app-card-pad">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">首页内容管理</text>
            <text class="hero-title">维护首页资讯卡片</text>
            <text class="hero-subtitle">修改后会直接读数据库里的启用内容。</text>
          </view>
          <t-tag theme="primary" variant="light" shape="round">{{ items.length }}</t-tag>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view class="form-card app-card app-card-pad">
        <picker :range="categoryOptions" range-key="label" @change="changeCategory">
          <view class="field picker">{{ categoryLabel }}</view>
        </picker>
        <t-input v-model:value="form.title" class="field" maxlength="128" placeholder="标题" />
        <t-input v-model:value="form.summary" class="field" maxlength="255" placeholder="摘要" />
        <t-textarea v-model:value="form.body" class="field body" maxlength="3000" autosize placeholder="正文" />
        <view class="form-actions">
          <t-button theme="default" variant="outline" shape="round" @click="reset">新建</t-button>
          <t-button theme="primary" shape="round" :loading="saving" @click="save">
            {{ editingId ? '保存修改' : '发布内容' }}
          </t-button>
        </view>
      </view>
    </view>

    <view class="app-section">
      <view v-for="item in items" :key="item.id" class="content-item app-card">
        <view class="content-head">
          <text class="content-title">{{ item.title }}</text>
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

const categoryOptions = [
  { value: 'consulting', label: '留学资讯' },
  { value: 'club', label: '社团信息' },
  { value: 'ad', label: '合作广告' },
  { value: 'notice', label: '学习通知' },
] as const
const items = ref<ApiContentItem[]>([])
const editingId = ref<number | null>(null)
const saving = ref(false)
const categoryIndex = ref(0)
const form = reactive({
  category: 'consulting' as ApiContentItem['category'],
  title: '',
  summary: '',
  body: '',
  is_active: true,
  sort_order: 0,
})
const categoryLabel = computed(() => categoryOptions[categoryIndex.value].label)

const load = async () => {
  try {
    items.value = await contentApi.listAdmin()
  } catch {}
}

const changeCategory = (event: any) => {
  categoryIndex.value = Number(event.detail.value)
  form.category = categoryOptions[categoryIndex.value].value
}

const reset = () => {
  editingId.value = null
  categoryIndex.value = 0
  Object.assign(form, { category: 'consulting', title: '', summary: '', body: '', is_active: true, sort_order: 0 })
}

const edit = (item: ApiContentItem) => {
  editingId.value = item.id
  categoryIndex.value = categoryOptions.findIndex((option) => option.value === item.category)
  Object.assign(form, {
    category: item.category,
    title: item.title,
    summary: item.summary,
    body: item.body,
    is_active: item.is_active,
    sort_order: item.sort_order,
  })
}

const save = async () => {
  if (!form.title.trim() || !form.summary.trim() || !form.body.trim()) {
    uni.showToast({ title: '请填写完整内容', icon: 'none' })
    return
  }
  saving.value = true
  try {
    if (editingId.value) await contentApi.update(editingId.value, { ...form })
    else await contentApi.create({ ...form })
    reset()
    await load()
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch {
  } finally {
    saving.value = false
  }
}

const remove = (id: number) => {
  uni.showModal({
    title: '删除内容',
    content: '确定删除这条首页内容吗？',
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
  background: #ffffff;
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
  font-size: 23rpx;
  line-height: 1.65;
  color: var(--app-text-weak);
}

.content-actions {
  margin-top: 16rpx;
}
</style>

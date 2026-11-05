<template>
  <c-admin-frame :loading="loading" :allowed="allowed" :error="loadError" @retry="load">
  <view class="page app-shell">
    <view class="app-section">
      <view class="hero app-heading">
        <view class="hero-head">
          <view class="hero-copy">
            <text class="hero-brand">{{ t("内容管理") }}</text>
            <text class="hero-title">{{ user.isOwner ? t('维护内容与更新公告') : t('公告与内容') }}</text>
          </view>
          <t-tag theme="primary" variant="light" shape="round">{{ items.length }}</t-tag>
        </view>
      </view>
    </view>

    <view v-if="user.isOwner" class="app-section">
      <view class="form-card app-card app-card-pad">
        <picker :range="localizedCategories" range-key="label" @change="changeCategory">
          <view class="field picker">{{ t(categoryLabel) }}</view>
        </picker>
        <view class="switch-row"><text>{{ t("作为更新公告展示") }}</text><switch :checked="isAnnouncement" :disabled="saving" color="#b86b4b" @change="toggleAnnouncement" /></view>
        <input v-if="isAnnouncement" v-model="form.release_version" class="native-field" :disabled="saving" maxlength="24" :placeholder="t('版本号，例如 1.5.1')" />
        <input v-model="form.title" class="native-field" :disabled="saving" maxlength="128" :placeholder="t('标题')" />
        <input v-model="form.summary" class="native-field" :disabled="saving" maxlength="255" :placeholder="t('摘要')" />
        <textarea v-model="form.body" class="native-field native-body" :disabled="saving" maxlength="12000" :placeholder="t('正文')" />
        <view class="form-actions">
          <t-button theme="default" variant="outline" shape="round" :disabled="saving" @click="reset">{{ t("新建") }}</t-button>
          <t-button v-if="!form.is_active" theme="default" variant="outline" shape="round" :disabled="saving" @click="save(false)">{{ t("保存草稿") }}</t-button>
          <t-button theme="primary" shape="round" :loading="saving" :disabled="saving" @click="save(true)">
            {{ form.is_active ? t("保存修改") : t("发布") }}
          </t-button>
        </view>
      </view>
    </view>

    <view v-if="!loading" class="app-section">
      <view v-for="item in items" :key="item.id" class="content-item app-card">
        <view class="content-head">
          <text class="content-title">{{ item.release_version ? 'v' + item.release_version + ' · ' : '' }}{{ item.title }}</text>
          <t-tag :theme="item.is_active ? 'success' : 'default'" variant="light" shape="round" size="small">
            {{ item.is_active ? t("已启用") : t("已停用") }}
          </t-tag>
        </view>
        <text class="content-summary">{{ item.summary }}</text>
        <text class="admin-body" selectable>{{ item.body }}</text>
        <view v-if="user.isOwner" class="content-actions">
          <t-button theme="default" variant="outline" size="small" shape="round" :disabled="saving" @click="edit(item)">{{ t("编辑") }}</t-button>
          <t-button v-if="!item.is_active" theme="primary" size="small" shape="round" :disabled="saving" @click="publish(item)">{{ t("发布") }}</t-button>
          <t-button v-else theme="default" variant="outline" size="small" shape="round" :disabled="saving" @click="withdraw(item)">{{ t("撤下") }}</t-button>
          <t-button theme="danger" variant="outline" size="small" shape="round" :disabled="saving" @click="remove(item.id)">{{ t("删除") }}</t-button>
        </view>
      </view>
    </view>
  </view>
  </c-admin-frame>
</template>

<script setup lang="ts">
import { showToast, showModal } from '@/i18n/ui'
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { computed, reactive, ref, watch } from 'vue'
import { activeUserId, adminRole } from '@/shared/auth/session'
import { useAdminPage } from '@/features/admin/useAdminPage'
import { contentApi } from '@/features/content/api'
import type { ApiContentItem } from '@/api/contracts'
import { APP_VERSION } from '@/constants/brand'

usePageI18n('pages/content-admin/index')

const categoryOptions = [
  { value: 'consulting', label: '留学资讯' },
  { value: 'club', label: '社团信息' },
  { value: 'ad', label: '合作广告' },
  { value: 'notice', label: '通知 / 更新公告' },
] as const
const { user, data: items, loading, saving, error: loadError, allowed, load, write } = useAdminPage<ApiContentItem[]>([], contentApi.listAdmin)
const editingId = ref<number | null>(null)
const isAnnouncement = ref(false)
const categoryIndex = ref(0)
const form = reactive({
  category: 'consulting' as ApiContentItem['category'],
  title: '',
  summary: '',
  body: '',
  release_version: '',
  published_at: null as string | null,
  is_active: false,
  sort_order: 0,
})
const categoryLabel = computed(() => categoryOptions[categoryIndex.value].label)
const localizedCategories = computed(() => categoryOptions.map(option => ({ ...option, label: t(option.label) })))

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

const reset = () => {
  if (!user.isOwner || saving.value) return
  editingId.value = null
  categoryIndex.value = 0
  isAnnouncement.value = false
  Object.assign(form, { category: 'consulting', title: '', summary: '', body: '', release_version: '', published_at: null, is_active: false, sort_order: 0 })
}

const edit = (item: ApiContentItem) => {
  if (!user.isOwner || saving.value) return
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

const save = async (publish: boolean) => {
  if (!user.isOwner || saving.value) return
  if (!form.title.trim() || !form.summary.trim() || !form.body.trim()) {
    showToast({ title: '请填写完整内容', icon: 'none' })
    return
  }
  if (isAnnouncement.value && !/^\d+\.\d+\.\d+$/.test(form.release_version.trim())) {
    showToast({ title: '请填写正确版本号，例如 1.5.1', icon: 'none' })
    return
  }
  const publishing = publish && (!editingId.value || !form.is_active)
  const payload = { ...form, is_active: publish, published_at: publishing ? null : form.published_at,
    release_version: isAnnouncement.value ? form.release_version.trim() : null }
  const result = await write(() => editingId.value ? contentApi.update(editingId.value, payload) : contentApi.create(payload))
  if (result) { reset(); await load(); showToast({ title: publishing ? '已发布' : '已保存', icon: 'success' }) }
}

const updatePublication = async (item: ApiContentItem, active: boolean) => {
  if (!user.isOwner || saving.value) return
  const result = await write(() => contentApi.update(item.id, { is_active: active, ...(active ? { published_at: null } : {}) }))
  if (!result) return
  if (editingId.value === item.id) {
    form.is_active = result.is_active
    form.published_at = result.published_at || null
  }
  await load()
  showToast({ title: active ? '已发布' : '已撤下', icon: 'success' })
}

const publish = (item: ApiContentItem) => updatePublication(item, true)
const withdraw = (item: ApiContentItem) => {
  if (!user.isOwner || saving.value) return
  showModal({ title: '撤下内容', content: '确定撤下这条内容吗？',
    success: async result => { if (result.confirm) await updatePublication(item, false) },
  })
}

const remove = (id: number) => {
  if (!user.isOwner || saving.value) return
  showModal({
    title: '删除内容',
    content: '确定删除这条内容吗？',
    success: async (result: any) => {
      if (!result.confirm) return
      try {
        const result = await write(() => contentApi.remove(id))
        if (result) await load()
      } catch {}
    },
  })
}

watch([activeUserId, adminRole], () => {
  editingId.value = null
  categoryIndex.value = 0
  isAnnouncement.value = false
  Object.assign(form, { category: 'consulting', title: '', summary: '', body: '', release_version: '', published_at: null, is_active: false, sort_order: 0 })
}, { flush: 'sync' })
</script>

<style src="@/features/admin/admin.css"></style>
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
  flex-wrap: wrap;
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

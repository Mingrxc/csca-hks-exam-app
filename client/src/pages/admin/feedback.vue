<template>
  <c-admin-frame :loading="loading" :allowed="allowed" :error="error" @retry="load">
    <view class="app-section admin-tabs"><button v-for="option in filters" :key="option.value" class="admin-tab" :class="{ active: status === option.value }" :disabled="saving" @tap="filter(option.value)">{{ t(option.label) }}</button></view>
    <view v-for="item in data.items" :key="item.id" class="app-section app-card app-card-pad">
      <view class="admin-row-head"><text class="admin-name">{{ item.nickname || t('用户反馈') }}</text><text class="admin-code">{{ item.user_code }}</text><text class="admin-role">{{ t(statusLabels[item.status]) }}</text></view>
      <text class="admin-meta">#{{ item.id }} · {{ t(categoryLabel(item.category)) }} · {{ adminDate(item.created_at) }} · v{{ item.app_version }}</text>
      <text class="admin-body" selectable>{{ item.content }}</text>
      <view v-if="user.isOwner" class="admin-actions">
        <button v-for="option in statuses.filter(option => option.value !== item.status)" :key="option.value" class="admin-button admin-button-secondary" :disabled="saving" @tap="mark(item.id, option.value)">{{ t(option.action) }}</button>
      </view>
    </view>
    <view v-if="!data.items.length && !error" class="app-section app-card admin-empty">{{ t('暂无用户反馈') }}</view>
    <c-admin-pager :page="page" :total="data.total" :loading="loading" @change="changePage" />
  </c-admin-frame>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { adminApi } from '@/features/admin/api'
import type { Page, AdminFeedback } from '@/features/admin/api'
import { FEEDBACK_CATEGORIES } from '@/features/feedback/api'
import { adminDate } from '@/features/admin/format'
import { useAdminPage } from '@/features/admin/useAdminPage'
usePageI18n('pages/admin/feedback')
const page = ref(1), status = ref('')
const statuses = [{ value: 'unread', label: '未读', action: '标为未读' }, { value: 'read', label: '已读', action: '标为已读' }, { value: 'resolved', label: '已处理', action: '标为已处理' }] as const
const filters = [{ value: '', label: '全部' }, ...statuses]
const statusLabels = { unread: '未读', read: '已读', resolved: '已处理' }
const categoryLabel = (value: string) => FEEDBACK_CATEGORIES.find(option => option.value === value)?.label || '其他'
const { user, data, loading, saving, error, allowed, load, write } = useAdminPage<Page<AdminFeedback>>({ items: [], total: 0, page: 1, page_size: 20 }, () => adminApi.feedback(status.value, page.value))
function filter(value: string) { status.value = value; page.value = 1; load() }
function changePage(value: number) { page.value = value; load() }
async function mark(id: number, value: AdminFeedback['status']) {
  const result = await write(() => adminApi.feedbackStatus(id, value))
  if (result) await load()
}
</script>
<style src="@/features/admin/admin.css"></style>

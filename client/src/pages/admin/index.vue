<template>
  <c-admin-frame :loading="loading" :allowed="allowed" :error="error" @retry="load">
    <view class="app-section">
      <view class="admin-heading"><text class="app-section-title">{{ t('管理中心') }}</text><text class="admin-role">{{ t('管理员') }}</text></view>
      <text class="admin-note">{{ t('今日数据按北京时间统计') }}</text>
    </view>
    <view v-if="data" class="app-section admin-grid">
      <view v-for="metric in metrics" :key="metric.key" class="app-card admin-metric"><text class="admin-number">{{ data[metric.key] }}</text><text class="admin-label">{{ t(metric.label) }}</text></view>
    </view>
    <view class="app-section app-card">
      <button class="admin-link" @tap="open('/pages/admin/users')"><text>{{ t('用户列表') }}</text><text>›</text></button>
      <button class="admin-link" @tap="open('/pages/admin/feedback')"><text>{{ t('反馈查看') }}</text><text>›</text></button>
      <button class="admin-link" @tap="open('/pages/content-admin/index')"><text>{{ t('公告与内容') }}</text><text>›</text></button>
      <button v-if="user.isOwner" class="admin-link" @tap="open('/pages/admin/members')"><text>{{ t('管理员管理') }}</text><text>›</text></button>
    </view>
  </c-admin-frame>
</template>
<script setup lang="ts">
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { adminApi } from '@/features/admin/api'
import type { Overview } from '@/features/admin/api'
import { useAdminPage } from '@/features/admin/useAdminPage'
usePageI18n('pages/admin/index')
const { user, data, loading, error, allowed, load } = useAdminPage<Overview | null>(null, adminApi.overview)
const metrics: { key: keyof Omit<Overview, 'study_timezone'>; label: string }[] = [
  { key: 'total_users', label: '用户总数' }, { key: 'new_users_today', label: '今日新增用户' },
  { key: 'answering_users_today', label: '今日答题人数' }, { key: 'total_answers', label: '累计答题数' },
  { key: 'total_papers', label: '累计试卷数' }, { key: 'total_feedback', label: '反馈总数' },
  { key: 'unread_feedback', label: '未读反馈' },
]
const open = (url: string) => { if (user.isAdmin) uni.navigateTo({ url }) }
</script>
<style src="@/features/admin/admin.css"></style>

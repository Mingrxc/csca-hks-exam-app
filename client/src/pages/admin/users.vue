<template>
  <c-admin-frame :loading="loading" :allowed="allowed" :error="error" @retry="load">
    <view class="app-section app-card app-card-pad">
      <view class="admin-search"><input v-model="searchDraft" class="admin-input" maxlength="64" :placeholder="t('按用户编号或昵称查找')" confirm-type="search" @confirm="search" /><button class="admin-button" @tap="search">{{ t('查找') }}</button></view>
      <text class="admin-note">{{ t('共 {n} 位用户', { n: data.total }) }}</text>
    </view>
    <view v-for="item in data.items" :key="item.id" class="app-section app-card app-card-pad">
      <view class="admin-row-head"><text class="admin-name">{{ item.nickname }}</text><text class="admin-code">{{ item.user_code }}</text><text class="admin-role">{{ t(roleLabels[item.role]) }}</text></view>
      <text class="admin-meta">{{ t('注册时间') }} · {{ adminDate(item.created_at) }}</text>
      <text class="admin-meta">{{ t('累计答题数') }} {{ item.total_questions }} · {{ t('正确率') }} {{ item.total_objective ? item.correct_rate + '%' : '—' }}</text>
      <text class="admin-meta">{{ t('最近学习时间') }} · {{ adminDate(item.last_study_at) }}</text>
    </view>
    <view v-if="!data.items.length && !error" class="app-section app-card admin-empty">{{ t('暂无匹配用户') }}</view>
    <c-admin-pager :page="page" :total="data.total" :loading="loading" @change="changePage" />
  </c-admin-frame>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { t } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { adminApi } from '@/features/admin/api'
import type { Page, AdminUser } from '@/features/admin/api'
import { adminDate } from '@/features/admin/format'
import { useAdminPage } from '@/features/admin/useAdminPage'
usePageI18n('pages/admin/users')
const page = ref(1), searchDraft = ref(''), query = ref('')
const roleLabels = { user: '普通用户', viewer: '管理员', owner: '管理员' }
const { data, loading, error, allowed, load } = useAdminPage<Page<AdminUser>>({ items: [], total: 0, page: 1, page_size: 20 }, () => adminApi.users(query.value, page.value))
function search() { query.value = searchDraft.value.trim(); page.value = 1; load() }
function changePage(value: number) { page.value = value; load() }
</script>
<style src="@/features/admin/admin.css"></style>

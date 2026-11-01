<template>
  <c-admin-frame :loading="loading" :allowed="allowed" :error="error" @retry="load">
    <view class="app-section app-card app-card-pad">
      <text class="app-card-title">{{ t('添加管理员') }}</text>
      <text class="admin-note">{{ t('对方需先登录。核对编号和昵称后授权，无需对方确认。') }}</text>
      <view class="admin-search admin-actions"><input :value="code" class="admin-input" maxlength="32" :disabled="saving" placeholder="lw001" confirm-type="search" @input="changeCode" @confirm="lookup" /><button class="admin-button" :loading="looking" :disabled="looking || saving" @tap="lookup">{{ t('查找') }}</button></view>
      <text v-if="lookupError" class="admin-note">{{ lookupError }}</text>
      <view v-if="candidate" class="admin-actions"><text class="admin-name">{{ candidate.nickname }}</text><text class="admin-code">{{ candidate.user_code }}</text><text class="admin-meta">{{ t(roleLabels[candidate.role]) }}</text>
        <button v-if="candidate.role === 'user'" class="admin-button" :disabled="saving" @tap="grant">{{ t('设为管理员') }}</button></view>
    </view>
    <view v-for="item in data.items" :key="item.id" class="app-section app-card app-card-pad">
      <view class="admin-row-head"><text class="admin-name">{{ item.nickname }}</text><text class="admin-code">{{ item.user_code }}</text><text class="admin-role">{{ t(roleLabels[item.role]) }}</text></view>
      <view v-if="item.role === 'viewer'" class="admin-actions"><button class="admin-button admin-button-secondary" :disabled="saving" @tap="revoke(item)">{{ t('撤销管理员权限') }}</button></view>
    </view>
    <c-admin-pager :page="page" :total="data.total" :loading="loading" @change="changePage" />
  </c-admin-frame>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { t, errorText } from '@/i18n'
import { usePageI18n } from '@/i18n/page'
import { showToast } from '@/i18n/ui'
import { confirmAction } from '@/shared/ui/confirm'
import { activeUserId, adminRole, sessionGeneration } from '@/shared/auth/session'
import { adminApi } from '@/features/admin/api'
import type { Page, AdminUser } from '@/features/admin/api'
import { useAdminPage } from '@/features/admin/useAdminPage'
usePageI18n('pages/admin/members')
const page = ref(1), code = ref(''), looking = ref(false), lookupError = ref('')
const candidate = ref<AdminUser | null>(null)
let lookupSequence = 0
const roleLabels = { user: '普通用户', viewer: '管理员', owner: '管理员' }
const { user, data, loading, saving, error, allowed, load, write } = useAdminPage<Page<AdminUser>>({ items: [], total: 0, page: 1, page_size: 20 }, () => adminApi.members(page.value), true)
function clearCandidate() { lookupSequence++; candidate.value = null; looking.value = false; lookupError.value = '' }
watch([activeUserId, adminRole], () => { clearCandidate(); code.value = '' }, { flush: 'sync' })
function changeCode(event: any) { code.value = String(event.detail?.value || ''); clearCandidate() }
async function lookup() {
  const value = code.value.trim()
  if (!user.isOwner || looking.value || saving.value) return
  clearCandidate()
  if (!/^lw[0-9]{3,}$/.test(value)) { lookupError.value = t('请输入有效用户编号，例如lw001'); return }
  const current = ++lookupSequence, session = sessionGeneration()
  looking.value = true
  try {
    const result = await adminApi.lookup(value)
    if (current === lookupSequence && session === sessionGeneration() && user.isOwner) candidate.value = result
  } catch (reason: any) {
    if (current === lookupSequence) lookupError.value = errorText(reason?.message || '加载失败')
  } finally { if (current === lookupSequence) looking.value = false }
}
async function grant() {
  const target = candidate.value
  if (!user.isOwner || saving.value || !target || target.role !== 'user') return
  if (!await confirmAction({ title: '添加管理员', content: t('将 {name}（{code}）设为管理员？', { name: target.nickname, code: target.user_code }) })) return
  if (candidate.value?.id !== target.id || code.value.trim() !== target.user_code) return
  const result = await write(() => adminApi.grant(target.user_code))
  if (result) { clearCandidate(); await load(); showToast({ title: '管理员已添加', icon: 'success' }) }
}
async function revoke(target: AdminUser) {
  if (!user.isOwner || saving.value || target.role !== 'viewer') return
  if (!await confirmAction({ title: '撤销管理员权限', content: t('撤销 {name}（{code}）的管理员权限？', { name: target.nickname, code: target.user_code }) })) return
  const result = await write(() => adminApi.revoke(target.id))
  if (result) { clearCandidate(); await load(); showToast({ title: '管理员权限已撤销', icon: 'success' }) }
}
function changePage(value: number) { page.value = value; load() }
</script>
<style src="@/features/admin/admin.css"></style>

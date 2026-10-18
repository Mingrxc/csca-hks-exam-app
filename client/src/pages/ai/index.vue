<template>
  <view class="ai-page app-shell">
    <view v-if="historyOpen" class="history-mask" @click="historyOpen = false"></view>
    <view v-show="historyOpen" class="history-drawer" :class="{ open: historyOpen }">
      <view class="history-head"><text class="history-title">历史问答</text><t-button theme="default" variant="text" size="small" :disabled="sending" @click="clearCurrentSession">新建</t-button><button class="icon-button" aria-label="关闭历史问答" @click="historyOpen = false"><t-icon name="close" size="30rpx" /></button></view>
      <scroll-view class="history-list" scroll-y>
        <button v-for="session in sessions" :key="session.id" class="history-item" :class="{ active: session.id === currentSessionId }" :disabled="sending" @click="switchSession(session.id)">
          <text class="history-item-title">{{ session.title }}</text><view class="history-item-meta"><text>{{ session.messages.length }} 条消息</text><text>{{ formatTimeLabel(session.updatedAt) }}</text></view>
        </button>
      </scroll-view>
    </view>

    <view class="chat-shell">
      <view class="chat-head">
        <button class="icon-button" aria-label="历史问答" @click="historyOpen = true"><t-icon name="menu" size="34rpx" /></button>
        <view class="chat-heading"><text class="chat-title">学习 AI 助手</text><text class="chat-subtitle">{{ getExamLabel(activeExamType) }} · 题目讲解与复习建议</text></view>
        <button class="icon-button" aria-label="新建会话" :disabled="sending" @click="clearCurrentSession"><t-icon name="edit-1" size="34rpx" /></button>
      </view>

      <scroll-view class="chat-list" scroll-y :scroll-into-view="lastMessageId">
        <view v-if="currentMessages.length === 0" class="empty-state">
          <view class="welcome-icon"><t-icon name="chat" size="52rpx" /></view><text class="welcome-title">一起把问题想明白</text><text class="welcome-desc">贴上题目和你的困惑，从思路讲起。</text>
          <view class="suggestion-list"><button v-for="item in suggestions" :key="item.key" class="suggestion-chip" @click="useSuggestion(item)"><view><text class="suggestion-title">{{ item.title }}</text><text class="suggestion-desc">{{ item.desc }}</text></view><t-icon name="arrow-right" size="28rpx" /></button></view>
        </view>
        <view v-for="(message, index) in currentMessages" :id="'message-' + index" :key="currentSessionId + '-' + index" class="message-row" :class="message.role">
          <view class="message-avatar" :class="message.role">{{ message.role === 'assistant' ? 'AI' : '我' }}</view>
          <view class="message-bubble"><view class="message-head"><text class="message-role">{{ message.role === 'assistant' ? 'AI 助手' : userStore.userInfo.nickname || '我' }}</text><text class="message-time">{{ formatTimeLabel(message.createdAt) }}</text></view><text class="message-content" selectable>{{ message.content }}</text></view>
        </view>
        <view v-if="sending" class="message-row assistant"><view class="message-avatar assistant">AI</view><view class="message-bubble"><text class="message-content typing">正在整理思路…</text></view></view>
      </scroll-view>

      <view class="composer">
        <view v-if="contextDraft" class="attachment-row"><view class="attachment-chip"><t-icon name="book" size="24rpx" /><text>已带上题目上下文</text><button class="attachment-close" aria-label="移除上下文" @click="contextDraft = ''"><t-icon name="close" size="22rpx" /></button></view></view>
        <view class="composer-input-bar"><t-textarea v-model:value="draft" class="composer-textarea" :maxlength="1000" autosize :disabled="sending" :custom-style="{ padding: '0', backgroundColor: 'transparent' }" placeholder="输入题目或你的困惑" /><t-button class="composer-send" theme="primary" size="small" :loading="sending" :disabled="!canSend || sending" @click="send">发送</t-button></view>
        <text class="composer-hint">结合题目与解析，理解每一步思路</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { aiApi } from '@/features/ai/api'
import { useUserStore } from '@/stores/user'
import { getExamLabel } from '@/constants/exam'
import type { ExamType } from '@/types/exam'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  createdAt: number
}

interface ChatSession {
  id: string
  title: string
  updatedAt: number
  messages: ChatMessage[]
}

interface PrefillPayload {
  content?: string
  topic?: string
  context?: string
  examType?: ExamType
}

const SESSION_KEY = 'ai_sessions'
const CURRENT_SESSION_KEY = 'ai_current_session_id'
const PREFILL_KEY = 'ai_prefill'

const userStore = useUserStore()
const sessions = ref<ChatSession[]>([])
const currentSessionId = ref('')
const draft = ref('')
const contextDraft = ref('')
const sending = ref(false)
const historyOpen = ref(false)
const activeExamType = ref<ExamType>('CSCA')

const suggestions = [
  { key: 's1', title: '备考怎么安排', desc: '把目标拆成每天的练习' },
  { key: 's2', title: '这道题怎么想', desc: '理解思路和判断依据' },
  { key: 's3', title: '错题怎么复盘', desc: '找到错因，整理复习方法' },
] as const

const currentSession = computed(() => sessions.value.find((item) => item.id === currentSessionId.value) || null)
const currentMessages = computed(() => currentSession.value?.messages || [])
const lastMessageId = computed(() => (currentMessages.value.length ? `message-${currentMessages.value.length - 1}` : ''))
const canSend = computed(() => !!(draft.value.trim() || contextDraft.value.trim()))

function createSession(title = '新会话'): ChatSession {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    title,
    updatedAt: Date.now(),
    messages: [],
  }
}

function normalizeSession(raw: any): ChatSession | null {
  if (!raw || typeof raw !== 'object') return null
  const messages = Array.isArray(raw.messages)
    ? raw.messages
        .map((message: any) => ({
          role: message?.role === 'assistant' ? 'assistant' : 'user',
          content: String(message?.content || '').trim(),
          createdAt: Number(message?.createdAt || Date.now()),
        }))
        .filter((message: ChatMessage) => !!message.content)
    : []
  return {
    id: String(raw.id || `${Date.now()}`),
    title: String(raw.title || '新会话'),
    updatedAt: Number(raw.updatedAt || Date.now()),
    messages,
  }
}

function saveSessions() {
  uni.setStorageSync(SESSION_KEY, sessions.value)
  uni.setStorageSync(CURRENT_SESSION_KEY, currentSessionId.value)
}

function ensureCurrentSession() {
  if (!currentSessionId.value || !sessions.value.some((item) => item.id === currentSessionId.value)) {
    const session = createSession()
    sessions.value = [session, ...sessions.value]
    currentSessionId.value = session.id
    saveSessions()
  }
}

function loadSessions() {
  const stored = uni.getStorageSync(SESSION_KEY)
  const current = String(uni.getStorageSync(CURRENT_SESSION_KEY) || '')
  const normalized = Array.isArray(stored) ? stored.map(normalizeSession).filter(Boolean) as ChatSession[] : []
  sessions.value = normalized.length ? normalized.sort((a, b) => b.updatedAt - a.updatedAt) : [createSession()]
  currentSessionId.value = sessions.value.some((item) => item.id === current) ? current : sessions.value[0].id
  saveSessions()
}

function updateCurrentSession(mutator: (session: ChatSession) => void) {
  const index = sessions.value.findIndex((item) => item.id === currentSessionId.value)
  if (index < 0) return
  const session = { ...sessions.value[index], messages: [...sessions.value[index].messages] }
  mutator(session)
  session.updatedAt = Date.now()
  sessions.value.splice(index, 1, session)
  sessions.value = [...sessions.value].sort((a, b) => b.updatedAt - a.updatedAt)
  saveSessions()
}

function switchSession(id: string) {
  if (sending.value) return
  currentSessionId.value = id
  historyOpen.value = false
  saveSessions()
}

function clearCurrentSession() {
  if (sending.value) return
  if (currentSession.value && currentMessages.value.length === 0) {
    draft.value = ''
    contextDraft.value = ''
    historyOpen.value = false
    return
  }
  const nextSession = createSession()
  sessions.value = [nextSession, ...sessions.value]
  currentSessionId.value = nextSession.id
  draft.value = ''
  contextDraft.value = ''
  historyOpen.value = false
  saveSessions()
}

function formatTimeLabel(timestamp: number) {
  const date = new Date(timestamp)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function syncExamType() {
  activeExamType.value = userStore.selectedExams[0] || userStore.userInfo.targetExam
}

function appendPrefill(payload: PrefillPayload | string) {
  if (typeof payload === 'string') {
    draft.value = payload
    return
  }
  if (payload.examType === 'CSCA' || payload.examType === 'HKS') {
    activeExamType.value = payload.examType
  }
  const parts = [payload.topic ? `主题：${payload.topic}` : '', payload.content || '', payload.context || '']
    .filter(Boolean)
    .join('\n\n')
    .trim()
  if (parts) draft.value = parts
}

function consumePrefill() {
  const raw = uni.getStorageSync(PREFILL_KEY)
  if (!raw) return
  appendPrefill(raw)
  uni.removeStorageSync(PREFILL_KEY)
}

function useSuggestion(item: (typeof suggestions)[number]) {
  if (item.key === 's1') {
    activeExamType.value = userStore.primaryExam
    draft.value = '帮我安排一个循序渐进的备考计划，先问清楚我的目标和可用时间。'
    contextDraft.value = '我希望把刷题、错题复习和模拟练习安排到每天。'
    return
  }
  if (item.key === 's2') {
    activeExamType.value = userStore.primaryExam
    draft.value = '这道题我卡住了，请直接讲解思路和判断依据。'
    contextDraft.value = ''
    return
  }
  activeExamType.value = userStore.primaryExam
  draft.value = '这道题我做错了，帮我整理一下错因和复盘方法。'
  contextDraft.value = ''
}

async function send() {
  const questionText = draft.value.trim()
  const contextText = contextDraft.value.trim()
  const userContent = [questionText, contextText].filter(Boolean).join('\n').trim()

  if (!userContent || sending.value) return

  ensureCurrentSession()
  updateCurrentSession((session) => {
    session.messages.push({ role: 'user', content: userContent, createdAt: Date.now() })
    if (session.title === '新会话') {
      session.title = questionText.slice(0, 14) || '新会话'
    }
  })

  sending.value = true
  try {
    const history = currentMessages.value.slice(-11).map((message) => ({
      role: message.role,
      content: message.content,
    }))
    const response = await aiApi.chat({
      messages: history,
      examType: activeExamType.value,
      question: questionText,
      context: contextText || undefined,
    })
    draft.value = ''
    contextDraft.value = ''
    updateCurrentSession((session) => {
      session.messages.push({ role: 'assistant', content: response.reply, createdAt: Date.now() })
    })
  } catch {
    updateCurrentSession((session) => {
      session.messages.push({ role: 'assistant', content: '这次回复没有成功送达，请稍后再试。', createdAt: Date.now() })
    })
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  loadSessions()
})

onShow(() => {
  if (sending.value) return
  if (!userStore.isLogin) userStore.login().catch(() => {})
  loadSessions()
  syncExamType()
  consumePrefill()
})
</script>

<style lang="scss" scoped>
.ai-page { height: calc(100vh - var(--window-top, 0px) - var(--window-bottom, 0px)); min-height: 0; padding: 0; overflow: hidden; }
.chat-shell { height: 100%; display: flex; flex-direction: column; padding: 0 28rpx; }
.chat-head { display: flex; align-items: center; gap: 16rpx; padding: 24rpx 0; border-bottom: 1rpx solid var(--app-border); flex-shrink: 0; }
.chat-heading { flex: 1; min-width: 0; }
.chat-title { display: block; color: var(--app-text); font-size: 30rpx; font-weight: 600; }
.chat-subtitle { display: block; margin-top: 4rpx; color: var(--app-text-weak); font-size: 20rpx; }
.icon-button { display: flex; align-items: center; justify-content: center; width: 64rpx; height: 64rpx; margin: 0; padding: 0; background: var(--app-surface); color: var(--app-primary); border: 1rpx solid var(--app-border); border-radius: var(--app-radius-md); flex: none; }
.chat-list { flex: 1; height: 0; min-height: 0; width: 100%; }
.empty-state { padding: 60rpx 8rpx 32rpx; }
.welcome-icon { display: flex; align-items: center; justify-content: center; width: 96rpx; height: 96rpx; margin-bottom: 24rpx; border-radius: 28rpx; color: var(--app-success); background: var(--app-secondary-soft); }
.welcome-title { display: block; color: var(--app-text); font-size: 38rpx; line-height: 1.4; font-weight: 600; }
.welcome-desc { display: block; margin-top: 12rpx; font-size: 24rpx; color: var(--app-text-weak); line-height: 1.7; }
.suggestion-list { display: flex; flex-direction: column; gap: 16rpx; margin-top: 36rpx; }
.suggestion-chip { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; width: 100%; margin: 0; padding: 24rpx; border: 1rpx solid var(--app-border); border-radius: var(--app-radius-lg); background: var(--app-surface); color: var(--app-primary); text-align: left; line-height: 1.6; }
.suggestion-title { display: block; color: var(--app-text); font-size: 26rpx; font-weight: 500; }
.suggestion-desc { display: block; margin-top: 4rpx; color: var(--app-text-weak); font-size: 22rpx; }
.message-row { display: flex; align-items: flex-start; gap: 14rpx; margin: 24rpx 0; }
.message-row.user { flex-direction: row-reverse; }
.message-avatar { display: flex; align-items: center; justify-content: center; width: 56rpx; height: 56rpx; flex: none; border-radius: 16rpx; color: var(--app-primary); background: var(--app-primary-soft); font-size: 20rpx; font-weight: 600; }
.message-avatar.assistant { color: var(--app-success); background: var(--app-secondary-soft); }
.message-bubble { flex: 1; min-width: 0; padding: 22rpx; border: 1rpx solid var(--app-border); border-radius: var(--app-radius-lg); background: var(--app-surface); }
.message-row.user .message-bubble { background: var(--app-primary-soft); border-color: #e5c9b7; }
.message-head { display: flex; align-items: center; justify-content: space-between; gap: 12rpx; }
.message-role, .message-time { font-size: 20rpx; color: var(--app-text-mute); }
.message-content { display: block; margin-top: 10rpx; font-size: 28rpx; line-height: 1.75; color: var(--app-text); white-space: pre-wrap; overflow-wrap: anywhere; }
.typing { color: var(--app-text-weak); }
.composer { flex-shrink: 0; padding: 20rpx 0 calc(18rpx + env(safe-area-inset-bottom)); border-top: 1rpx solid var(--app-border); }
.composer-input-bar { display: flex; align-items: flex-end; gap: 18rpx; padding: 20rpx; border: 1rpx solid var(--app-border); border-radius: var(--app-radius-lg); background: var(--app-surface); }
.composer-textarea { flex: 1; min-width: 0; }
.composer-textarea :deep(.t-textarea), .composer-textarea :deep(.t-textarea__wrapper-inner) { padding: 0; background: transparent; }
.composer-textarea :deep(textarea) { max-height: 240rpx; font-size: 26rpx; line-height: 1.6; }
.composer-send { flex: none; }
.composer-hint { display: block; margin-top: 10rpx; color: var(--app-text-mute); text-align: center; font-size: 20rpx; }
.attachment-row { margin-bottom: 12rpx; }
.attachment-chip { display: inline-flex; align-items: center; gap: 8rpx; padding: 8rpx 14rpx; border-radius: 999px; background: var(--app-secondary-soft); color: var(--app-success); font-size: 20rpx; }
.attachment-close { margin: 0; padding: 0; background: transparent; color: inherit; display: flex; }
.history-mask { position: fixed; top: var(--window-top, 0px); bottom: var(--window-bottom, 0px); left: 0; right: 0; z-index: 30; background: rgba(47, 41, 38, 0.3); }
.history-drawer { position: fixed; top: var(--window-top, 0px); bottom: var(--window-bottom, 0px); left: 0; z-index: 31; width: 82%; max-width: 640rpx; padding: 28rpx; background: var(--app-surface); box-shadow: var(--app-shadow-lg); transform: translateX(-110%); transition: transform 0.2s ease; display: flex; flex-direction: column; }
.history-drawer.open { transform: translateX(0); }
.history-head { display: flex; align-items: center; gap: 10rpx; flex-shrink: 0; }
.history-title { flex: 1; font-size: 30rpx; font-weight: 600; }
.history-list { flex: 1; height: 0; margin-top: 24rpx; }
.history-item { width: 100%; margin: 0 0 14rpx; padding: 20rpx; background: var(--app-surface-quiet); border: 1rpx solid transparent; border-radius: var(--app-radius-md); text-align: left; line-height: 1.6; }
.history-item.active { background: var(--app-primary-soft); border-color: #e5c9b7; }
.history-item-title { display: block; font-size: 26rpx; color: var(--app-text); }
.history-item-meta { display: flex; justify-content: space-between; gap: 12rpx; margin-top: 8rpx; color: var(--app-text-mute); font-size: 20rpx; }
</style>

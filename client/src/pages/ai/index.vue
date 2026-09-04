<template>
  <view class="page app-shell ai-page">
    <view v-if="!historyOpen" class="history-toggle" @click="historyOpen = true">
      <t-icon name="menu" size="30rpx" color="#c77f5e" />
    </view>

    <view v-if="historyOpen" class="history-mask" @click="historyOpen = false"></view>
    <view class="history-drawer" :class="{ open: historyOpen }">
      <view class="history-head">
        <text class="history-title">历史问答</text>
        <t-button theme="default" variant="text" size="small" shape="round" @click="clearCurrentSession">
          清空会话
        </t-button>
      </view>
      <scroll-view class="history-list" scroll-y>
        <view
          v-for="session in sessions"
          :key="session.id"
          class="history-item"
          :class="{ active: session.id === currentSessionId }"
          @click="switchSession(session.id)"
        >
          <text class="history-item-title">{{ session.title }}</text>
          <view class="history-item-meta">
            <text>{{ session.messages.length }} 条</text>
            <text>{{ formatTimeLabel(session.updatedAt) }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="chat-shell app-card">
      <view class="chat-head">
        <t-button
          class="new-chat-button"
          theme="default"
          variant="text"
          size="small"
          shape="circle"
          :custom-style="{
            width: '56rpx',
            height: '56rpx',
            padding: '0',
            backgroundColor: '#f4e4d8',
            borderColor: '#f4e4d8',
            color: '#c77f5e',
            marginLeft: 'auto',
            marginRight: '0',
          }"
          @click="clearCurrentSession"
        >
          <t-icon name="edit-1" size="26rpx" color="#c77f5e" />
        </t-button>
      </view>

      <scroll-view class="chat-list" scroll-y :scroll-into-view="lastMessageId">
        <view
          v-for="(message, index) in currentMessages"
          :id="`message-${index}`"
          :key="`${currentSessionId}-${index}`"
          class="message-row"
          :class="message.role"
        >
          <view class="message-avatar" :class="message.role">
            {{ message.role === 'assistant' ? 'AI' : '我' }}
          </view>
          <view class="message-bubble">
            <view class="message-head">
              <text class="message-role">{{ message.role === 'assistant' ? 'AI 助手' : userStore.userInfo.nickname || '我' }}</text>
              <text class="message-time">{{ formatTimeLabel(message.createdAt) }}</text>
            </view>
            <text class="message-content">{{ message.content }}</text>
          </view>
        </view>

        <view v-if="sending" class="message-row assistant">
          <view class="message-avatar assistant">AI</view>
          <view class="message-bubble typing">
            <view class="message-head">
              <text class="message-role">AI 助手</text>
              <text class="message-time">正在整理</text>
            </view>
            <text class="message-content">我在整理答案，马上给你一个更直接的说法。</text>
          </view>
        </view>
      </scroll-view>

      <view v-if="currentMessages.length === 0" class="empty-state">
        <view class="suggestion-block">
          <text class="suggestion-title">为你推荐</text>
          <view class="suggestion-grid">
            <view class="suggestion-chip" v-for="item in suggestions" :key="item.key" @click="useSuggestion(item)">
              <text class="suggestion-chip-title">{{ item.title }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="composer">
        <view class="composer-row">
          <view class="composer-input-bar">
            <view class="composer-photo-slot">
              <t-button
                class="composer-photo"
                theme="default"
                variant="text"
                size="small"
                shape="circle"
                :custom-style="{
                  width: '42rpx',
                  height: '42rpx',
                  padding: '0',
                  backgroundColor: '#f4e4d8',
                  borderColor: '#f4e4d8',
                  color: '#c77f5e',
                  marginLeft: '0',
                  marginRight: '0',
                }"
                @click="pickPhoto"
              >
                <t-icon name="camera" size="26rpx" color="#c77f5e" />
              </t-button>
            </view>
            <t-textarea
              v-model:value="draft"
              class="composer-textarea"
              maxlength="1000"
              autosize
              :custom-style="{
                height: '34rpx',
                minHeight: '34rpx',
                padding: '0',
                backgroundColor: 'transparent',
              }"
              placeholder="输入题目、政策或错题上下文"
            />
            <view class="composer-send-slot">
              <t-button
                class="composer-send"
                theme="primary"
                size="small"
                shape="round"
                :custom-style="{
                  width: '72rpx',
                  minWidth: '72rpx',
                  height: '40rpx',
                  padding: '0',
                  fontSize: '22rpx',
                  lineHeight: '40rpx',
                  backgroundColor: '#c77f5e',
                  borderColor: '#c77f5e',
                  color: '#ffffff',
                  marginLeft: '0',
                  marginRight: '0',
                }"
                :loading="sending"
                :disabled="!canSend"
                @click="send"
              >
                发送
              </t-button>
            </view>
          </view>
        </view>

        <view v-if="photoCount || contextDraft" class="attachment-row">
          <view v-if="photoCount" class="attachment-chip">
            <t-icon name="image" size="24rpx" />
            <text>图片 {{ photoCount }} 张</text>
            <t-button theme="default" variant="text" size="small" shape="round" @click="clearPhotos">
              <t-icon name="close" size="22rpx" />
            </t-button>
          </view>
          <view v-if="contextDraft" class="attachment-chip soft">
            <t-icon name="book" size="24rpx" />
            <text>已带上上下文</text>
            <t-button theme="default" variant="text" size="small" shape="round" @click="contextDraft = ''">
              <t-icon name="close" size="22rpx" />
            </t-button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { aiApi } from '@/api'
import { useUserStore } from '@/stores/user'
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
const photoCount = ref(0)
const sending = ref(false)
const historyOpen = ref(false)
const activeExamType = ref<ExamType>('CSCA')

const suggestions = [
  { key: 's1', title: '留学政策怎么问' },
  { key: 's2', title: '这道题怎么想' },
  { key: 's3', title: '错题怎么复盘' },
] as const

const currentSession = computed(() => sessions.value.find((item) => item.id === currentSessionId.value) || null)
const currentMessages = computed(() => currentSession.value?.messages || [])
const lastMessageId = computed(() => (currentMessages.value.length ? `message-${currentMessages.value.length - 1}` : ''))
const canSend = computed(() => !!(draft.value.trim() || contextDraft.value.trim() || photoCount.value))

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
  currentSessionId.value = id
  historyOpen.value = false
  saveSessions()
}

function clearCurrentSession() {
  uni.showModal({
    title: '清空会话',
    content: '要新开一个空白会话吗？',
    success: (res: any) => {
      if (!res.confirm) return
      const nextSession = createSession()
      sessions.value = [nextSession, ...sessions.value.filter((item) => item.id !== currentSessionId.value)]
      currentSessionId.value = nextSession.id
      draft.value = ''
      contextDraft.value = ''
      photoCount.value = 0
      historyOpen.value = false
      saveSessions()
    },
  })
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
    draft.value = '帮我梳理一下留学申请流程，先给结论，再给步骤。'
    contextDraft.value = '我更关心申请材料、时间安排和签证准备。'
    return
  }
  if (item.key === 's2') {
    activeExamType.value = 'CSCA'
    draft.value = '这道题我卡住了，请直接讲解思路和判断依据。'
    contextDraft.value = ''
    return
  }
  activeExamType.value = 'HKS'
  draft.value = '这道题我做错了，帮我整理一下错因和复盘方法。'
  contextDraft.value = ''
}

function pickPhoto() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['camera', 'album'],
    success: (res) => {
      if (!res.tempFilePaths.length) return
      photoCount.value = res.tempFilePaths.length
      if (!draft.value.trim()) {
        draft.value = '我拍了一张题目图片，请结合图片和上下文帮我分析。'
      }
      contextDraft.value = contextDraft.value
        ? `${contextDraft.value}\n已选择 ${photoCount.value} 张题目图片，请结合图片一起判断。`
        : `已选择 ${photoCount.value} 张题目图片，请结合图片一起判断。`
    },
  })
}

function clearPhotos() {
  photoCount.value = 0
}

async function send() {
  const questionText = draft.value.trim()
  const contextText = contextDraft.value.trim()
  const imageContext = photoCount.value ? `已选择 ${photoCount.value} 张题目图片，请结合图片一起判断。` : ''
  const userContent = [questionText, contextText, imageContext].filter(Boolean).join('\n').trim()

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
      context: [contextText, imageContext].filter(Boolean).join('\n') || undefined,
    })
    updateCurrentSession((session) => {
      session.messages.push({ role: 'assistant', content: response.reply, createdAt: Date.now() })
    })
  } catch {
    updateCurrentSession((session) => {
      session.messages.push({ role: 'assistant', content: '这次回复没有成功送达，请稍后再试。', createdAt: Date.now() })
    })
  } finally {
    sending.value = false
    draft.value = ''
    contextDraft.value = ''
    photoCount.value = 0
  }
}

onMounted(() => {
  loadSessions()
})

onShow(() => {
  if (!userStore.isLogin) userStore.login().catch(() => {})
  loadSessions()
  syncExamType()
  consumePrefill()
})
</script>

<style lang="scss" scoped>
.ai-page {
  position: relative;
  min-height: 100vh;
}

.history-toggle {
  position: fixed;
  left: 18rpx;
  top: 18rpx;
  z-index: 18;
  width: 56rpx;
  height: 56rpx;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f4e4d8;
  border: 1rpx solid #f4e4d8;
  box-shadow: var(--app-shadow-sm);
  color: #c77f5e;
}

.history-mask {
  position: fixed;
  inset: 0;
  z-index: 16;
  background: rgba(47, 41, 38, 0.18);
}

.history-drawer {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 17;
  width: 70vw;
  max-width: 520rpx;
  height: 100vh;
  padding: 24rpx 18rpx 20rpx 84rpx;
  background: linear-gradient(180deg, #fffaf4 0%, #f8ecdf 100%);
  border-right: 1rpx solid var(--app-border);
  box-shadow: 18rpx 0 42rpx rgba(98, 76, 57, 0.12);
  transform: translateX(-100%);
  transition: transform 0.22s ease;
}

.history-drawer.open {
  transform: translateX(0);
}

.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.history-title {
  font-size: 30rpx;
  line-height: 1.3;
  font-weight: 600;
  color: var(--app-text);
}

.history-list {
  height: calc(100vh - 96rpx);
  margin-top: 18rpx;
}

.history-item {
  padding: 18rpx;
  margin-bottom: 12rpx;
  border-radius: var(--app-radius-md);
  background: rgba(255, 251, 246, 0.92);
  border: 1rpx solid transparent;
}

.history-item.active {
  background: var(--app-primary-soft);
  border-color: rgba(199, 127, 94, 0.2);
}

.history-item-title {
  display: block;
  font-size: 26rpx;
  line-height: 1.45;
  font-weight: 600;
  color: var(--app-text);
}

.history-item-meta {
  display: flex;
  justify-content: space-between;
  gap: 12rpx;
  margin-top: 8rpx;
  font-size: 20rpx;
  color: var(--app-text-mute);
}

.chat-shell {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  margin: 0 20rpx 20rpx 84rpx;
  padding: 12rpx 18rpx calc(18rpx + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, rgba(255, 251, 246, 0.98), rgba(247, 241, 232, 0.98));
  border-color: transparent;
  border-radius: 30rpx;
  box-shadow: none;
  overflow: visible;
}

.chat-head {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 12rpx;
  min-height: 64rpx;
  width: 100%;
}

.new-chat-button {
  flex: none;
  width: 56rpx;
  height: 56rpx;
  padding: 0;
  border-radius: 999px;
}

.chat-list {
  flex: 1;
  min-height: 0;
  padding-top: 0;
}

.empty-state {
  padding: 0 0 18rpx;
}

.suggestion-block {
  margin-top: 0;
}

.suggestion-title {
  display: block;
  margin-bottom: 16rpx;
  font-size: 28rpx;
  line-height: 1.35;
  font-weight: 600;
  color: var(--app-text);
}

.suggestion-grid {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12rpx;
}

.suggestion-chip {
  max-width: 100%;
  padding: 16rpx 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.9);
  border: 1rpx solid var(--app-border);
  box-shadow: 0 4rpx 12rpx rgba(98, 76, 57, 0.04);
}

.suggestion-chip-title {
  display: block;
  font-size: 24rpx;
  line-height: 1.45;
  color: var(--app-text);
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  margin-top: 16rpx;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 58rpx;
  height: 58rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: 600;
  color: #ffffff;
  background: var(--app-primary);
  flex: none;
}

.message-avatar.assistant {
  background: linear-gradient(180deg, #d98a68 0%, #c77f5e 100%);
}

.message-bubble {
  flex: 1;
  min-width: 0;
  max-width: 620rpx;
  padding: 16rpx 18rpx;
  border-radius: 24rpx;
  background: rgba(255, 251, 246, 0.96);
  border: 1rpx solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
}

.message-row.user .message-bubble {
  background: var(--app-primary);
  border-color: var(--app-primary);
}

.message-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.message-role {
  font-size: 20rpx;
  font-weight: 600;
  color: var(--app-text-mute);
}

.message-row.user .message-role,
.message-row.user .message-time,
.message-row.user .message-content {
  color: rgba(255, 255, 255, 0.88);
}

.message-time {
  font-size: 18rpx;
  color: var(--app-text-mute);
}

.message-content {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  line-height: 1.68;
  white-space: pre-wrap;
  color: var(--app-text);
}

.typing .message-content {
  color: var(--app-text-weak);
}

.composer {
  padding-top: 14rpx;
}

.composer-row {
  width: calc(100% + 44rpx);
  margin-left: -54rpx;
}

.composer-input-bar {
  display: flex;
  align-items: center;
  width: 100%;
  height: 74rpx;
  min-height: 74rpx;
  padding: 2rpx 18rpx;
  transform: translateY(-10rpx);
  margin-bottom: -20rpx;
  border-radius: 999px;
  background: #ffffff;
  border: 1rpx solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
}

.composer-textarea {
  flex: 1;
  min-width: 0;
  margin: 0 8rpx;
  padding: 0;
  background: transparent;
}

.composer-textarea :deep(.t-textarea) {
  height: 34rpx;
  min-height: 34rpx;
  padding: 0;
  background: transparent;
}

.composer-textarea :deep(.t-textarea__wrapper-inner) {
  min-height: 34rpx;
  padding: 0;
  font-size: 24rpx;
  line-height: 1.35;
}

.composer-photo {
  flex: none;
  width: 42rpx;
  height: 42rpx;
  padding: 0;
  border-radius: 999px;
  background: var(--app-primary-soft) !important;
  border: 0;
  color: var(--app-primary) !important;
}

.composer-photo-slot {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex: none;
  width: 42rpx;
  height: 42rpx;
}

.composer-send {
  flex: none;
  min-width: 72rpx;
  height: 40rpx;
  padding: 0;
  font-size: 22rpx;
  line-height: 40rpx;
  --td-button-primary-bg-color: var(--app-primary);
  --td-button-primary-border-color: var(--app-primary);
  --td-button-primary-active-bg-color: var(--app-primary-strong);
  --td-button-primary-active-border-color: var(--app-primary-strong);
}

.composer-send-slot {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: none;
  width: 72rpx;
  height: 40rpx;
  margin-left: auto;
}

.attachment-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 12rpx;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 14rpx;
  border-radius: 999px;
  background: var(--app-primary-soft);
  color: var(--app-primary);
  font-size: 20rpx;
}

.attachment-chip.soft {
  background: var(--app-accent-soft);
  color: var(--app-accent);
}
</style>

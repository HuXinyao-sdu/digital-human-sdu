<template>
  <div class="guide-page">
    <h2 class="page-title">数字人校史讲解</h2>

    <div class="guide-layout">
      <!-- 数字人展示区 -->
      <div class="avatar-section">
        <div class="avatar-placeholder">
          <div class="avatar-circle">
            <span class="avatar-emoji">小山</span>
          </div>
          <p class="avatar-name">小山 · 校史讲解员</p>
          <p class="avatar-status" :class="{ speaking: isSpeaking }">
            {{ speechTotal ? `正在讲解（${speechSegment}/${speechTotal}）` : '待命中' }}
          </p>
          <button v-if="speechTotal" class="stop-speaking-btn" @click="stopSpeaking">停止讲解</button>
        </div>
        <div class="video-area">
          <AvatarViewer ref="avatarViewer" @loaded="avatarReady = true" @error="avatarReady = false" />
          <p v-if="!avatarReady" class="video-hint">正在准备数字人讲解员…</p>
        </div>
      </div>

      <!-- 交互区 -->
      <div class="interaction-section">
        <!-- 主题选择 -->
        <div class="topic-panel">
          <h3 class="panel-title">选择讲解主题</h3>
          <div class="topic-list">
            <button
              v-for="topic in topics"
              :key="topic.id"
              class="topic-btn"
              :class="{ active: activeTopic === topic.id }"
              :disabled="loading"
              @click="selectTopic(topic)"
            >
              <span class="topic-era">{{ topic.era }}</span>
              <span class="topic-name">{{ topic.name }}</span>
            </button>
          </div>
        </div>

        <!-- 问答区 -->
        <div class="chat-panel">
          <div class="chat-panel-header">
            <h3 class="panel-title">互动问答</h3>
            <button class="new-chat-btn" :disabled="loading" @click="startNewConversation">新建对话</button>
          </div>
          <div class="chat-messages" ref="chatContainer">
            <div class="message bot-message">
              <div class="message-avatar">🎓</div>
              <div class="message-bubble">
                你好！我是山大校史讲解员小山，可以问我任何关于趵突泉校区校史的问题。
              </div>
            </div>
            <div v-for="(msg, idx) in messages" :key="idx"
              :class="['message', msg.role === 'user' ? 'user-message' : 'bot-message']">
              <div class="message-avatar">{{ msg.role === 'user' ? '🧑' : '🎓' }}</div>
              <div class="message-bubble">
                <div>{{ msg.content }}</div>
                <details v-if="msg.role === 'bot' && msg.sources?.length" class="message-sources">
                  <summary>资料依据（{{ msg.sources.length }}）</summary>
                  <ul>
                    <li v-for="source in msg.sources" :key="source">{{ source }}</li>
                  </ul>
                </details>
              </div>
            </div>
            <div v-if="loading" class="message bot-message">
              <div class="message-avatar">🎓</div>
              <div class="message-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <input
              v-model="inputText"
              type="text"
              placeholder="输入你的校史问题..."
              @keyup.enter="sendMessage"
            />
            <button class="send-btn" @click="sendMessage" :disabled="loading || !inputText.trim()">
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref, nextTick } from 'vue'
import { chat, textToSpeech } from '@/api'
import AvatarViewer from '@/components/AvatarViewer.vue'

const topics = [
  { id: 1, era: '1901', name: '山东大学堂创办', question: '请介绍山东大学堂的创办背景和意义。' },
  { id: 2, era: '1920s', name: '齐鲁大学与医学院', question: '请介绍齐鲁大学及其医学教育的发展。' },
  { id: 3, era: '1930s', name: '老舍在山大任教', question: '请介绍老舍在山东大学任教的经历。' },
  { id: 4, era: '1940s', name: '侯宝璋与医学教育', question: '请介绍侯宝璋与山东大学医学教育的关系。' },
  { id: 5, era: '1950s', name: '院系调整与新山大', question: '请介绍1950年代院系调整对山东大学发展的影响。' },
  { id: 6, era: '当代', name: '趵突泉校区今昔', question: '请介绍趵突泉校区的历史沿革和代表性建筑。' }
]

const activeTopic = ref(null)
const isSpeaking = ref(false)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const chatContainer = ref(null)
const avatarReady = ref(false)
const avatarViewer = ref(null)
const CHAT_SESSION_STORAGE_KEY = 'sdu-digital-human-chat-session'
const chatSessionId = ref(window.localStorage.getItem(CHAT_SESSION_STORAGE_KEY) || null)
const speechSegment = ref(0)
const speechTotal = ref(0)
let audioPlayer = null
let activePlaybackResolver = null
let speechRunId = 0

const MAX_SPEECH_CHARS = 220

const selectTopic = (topic) => {
  activeTopic.value = topic.id
  submitQuestion(topic.question)
}

const saveChatSessionId = (sessionId) => {
  chatSessionId.value = sessionId || null
  if (sessionId) {
    window.localStorage.setItem(CHAT_SESSION_STORAGE_KEY, sessionId)
  } else {
    window.localStorage.removeItem(CHAT_SESSION_STORAGE_KEY)
  }
}

const startNewConversation = async () => {
  stopSpeaking()
  saveChatSessionId(null)
  activeTopic.value = null
  messages.value = []
  await scrollToBottom()
}

const sendMessage = async () => {
  if (!inputText.value.trim() || loading.value) return
  const text = inputText.value.trim()
  inputText.value = ''
  await submitQuestion(text)
}

const submitQuestion = async (text) => {
  if (!text || loading.value) return
  // 新问题优先，避免旧回答继续播报造成混淆。
  stopSpeaking()
  messages.value.push({ role: 'user', content: text })
  loading.value = true
  await scrollToBottom()

  try {
    const res = await chat({ question: text, session_id: chatSessionId.value || undefined })
    saveChatSessionId(res.session_id || chatSessionId.value)
    const answer = res.answer || '抱歉，我暂时无法回答这个问题。'
    messages.value.push({ role: 'bot', content: answer, sources: res.sources || [] })
    // 语音播放不阻塞下一轮提问；用户可随时停止或发送新问题。
    void speakAnswer(answer)
  } catch (e) {
    messages.value.push({ role: 'bot', content: '暂时无法连接校史知识库。请确认后端服务已启动后重试。' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const splitForSpeech = (text) => {
  const sentences = text.replace(/\s+/g, ' ').match(/[^。！？；…]+[。！？；…]?/g) || [text]
  const segments = []
  let current = ''

  const append = (piece) => {
    if (!piece) return
    if (current && current.length + piece.length > MAX_SPEECH_CHARS) {
      segments.push(current)
      current = ''
    }
    if (piece.length <= MAX_SPEECH_CHARS) {
      current += piece
      return
    }
    // 个别超长句优先按逗号断开，仍超长时才按字符截取。
    const clauses = piece.split(/(?<=[，、：])/)
    if (clauses.length > 1) {
      clauses.forEach(append)
      return
    }
    while (piece.length > MAX_SPEECH_CHARS) {
      if (current) segments.push(current)
      segments.push(piece.slice(0, MAX_SPEECH_CHARS))
      current = ''
      piece = piece.slice(MAX_SPEECH_CHARS)
    }
    current += piece
  }

  sentences.forEach(append)
  if (current) segments.push(current)
  return segments.filter(Boolean)
}

const stopSpeaking = () => {
  speechRunId += 1
  if (audioPlayer) {
    audioPlayer.pause()
    audioPlayer.currentTime = 0
    audioPlayer.src = ''
    audioPlayer = null
  }
  activePlaybackResolver?.('stopped')
  activePlaybackResolver = null
  avatarViewer.value?.stopLipSync()
  isSpeaking.value = false
  speechSegment.value = 0
  speechTotal.value = 0
}

const playSpeechSegment = async (audioUrl, runId) => {
  if (runId !== speechRunId) return 'stopped'

  return new Promise((resolve, reject) => {
    const player = new Audio(audioUrl)
    audioPlayer = player
    const finish = (result) => {
      if (audioPlayer === player) audioPlayer = null
      if (activePlaybackResolver === finish) activePlaybackResolver = null
      avatarViewer.value?.stopLipSync()
      resolve(result)
    }
    activePlaybackResolver = finish
    player.addEventListener('ended', () => finish('ended'), { once: true })
    player.addEventListener('error', () => reject(new Error('音频播放失败')), { once: true })

    Promise.resolve(avatarViewer.value?.startLipSync(player))
      .then(() => player.play())
      .then(() => { isSpeaking.value = true })
      .catch(reject)
  })
}

const speakAnswer = async (text) => {
  const segments = splitForSpeech(text)
  if (!segments.length) return
  const runId = ++speechRunId
  speechTotal.value = segments.length
  speechSegment.value = 0

  try {
    for (let index = 0; index < segments.length; index += 1) {
      if (runId !== speechRunId) return
      speechSegment.value = index + 1
      const speech = await textToSpeech({ text: segments[index] })
      if (runId !== speechRunId) return
      const result = await playSpeechSegment(speech.audio_url, runId)
      if (result !== 'ended') return
    }
  } catch (error) {
    // TTS 未配置或暂时不可用时，保留文字回答，不影响问答流程。
    console.info('TTS unavailable:', error.message)
  } finally {
    if (runId === speechRunId) {
      isSpeaking.value = false
      speechSegment.value = 0
      speechTotal.value = 0
      avatarViewer.value?.stopLipSync()
    }
  }
}

onBeforeUnmount(stopSpeaking)

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.guide-page { max-width: 1100px; margin: 0 auto; }
.page-title { font-size: 24px; color: #8B0000; margin-bottom: 24px; padding-left: 12px; border-left: 4px solid #8B0000; }
.guide-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; }
.avatar-section { display: flex; flex-direction: column; gap: 16px; }
.avatar-placeholder {
  background: linear-gradient(135deg, #f5f0e8, #ebe3d5);
  border-radius: 12px;
  padding: 32px;
  text-align: center;
}
.avatar-circle {
  width: 100px; height: 100px;
  border-radius: 50%;
  background: #fff;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.avatar-emoji { font-size: 22px; font-weight: 700; color: #8B0000; }
.avatar-name { font-size: 17px; font-weight: 600; color: #333; }
.avatar-status { font-size: 13px; color: #999; margin-top: 4px; }
.avatar-status.speaking { color: #8B0000; }
.stop-speaking-btn { margin-top: 12px; padding: 7px 14px; border: 1px solid #8B0000; border-radius: 16px; background: #fff; color: #8B0000; font-size: 13px; }
.stop-speaking-btn:hover { background: #fdf5f5; }
.video-area {
  position: relative;
  background: #1a1a1a;
  border-radius: 12px;
  height: 280px;
  display: flex; align-items: center; justify-content: center;
}
.video-hint {
  position: absolute;
  left: 0; right: 0; bottom: 12px;
  z-index: 2;
  margin: 0;
  color: #d9d3ca;
  font-size: 13px;
  text-align: center;
  pointer-events: none;
}
.interaction-section { display: flex; flex-direction: column; gap: 16px; }
.panel-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 12px; }
.chat-panel-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.chat-panel-header .panel-title { margin-bottom: 12px; }
.new-chat-btn { padding: 5px 10px; border: 1px solid #ddd; border-radius: 6px; background: #fff; color: #666; font-size: 12px; white-space: nowrap; }
.new-chat-btn:hover:not(:disabled) { border-color: #8B0000; color: #8B0000; }
.new-chat-btn:disabled { cursor: not-allowed; opacity: 0.6; }
.topic-panel, .chat-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.topic-list { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.topic-btn {
  display: flex; flex-direction: column; align-items: flex-start;
  padding: 12px 14px;
  background: #f8f5f0;
  border-radius: 8px;
  border: 1.5px solid transparent;
  transition: all 0.2s;
  text-align: left;
}
.topic-btn:hover { background: #f0e8dc; }
.topic-btn:disabled { cursor: not-allowed; opacity: 0.65; }
.topic-btn.active { border-color: #8B0000; background: #fdf5f5; }
.topic-era { font-size: 12px; color: #8B0000; font-weight: 600; }
.topic-name { font-size: 14px; color: #333; margin-top: 2px; }
.chat-messages {
  height: 240px;
  overflow-y: auto;
  padding: 12px;
  background: #faf8f5;
  border-radius: 8px;
  margin-bottom: 12px;
}
.message { display: flex; gap: 10px; margin-bottom: 14px; }
.message-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #eee;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.message-bubble {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  max-width: 80%;
}
.bot-message .message-bubble { background: #fff; color: #333; border-top-left-radius: 2px; }
.message-sources { margin-top: 8px; color: #777; font-size: 12px; line-height: 1.5; }
.message-sources summary { width: fit-content; cursor: pointer; color: #8B0000; font-weight: 600; list-style: none; }
.message-sources summary::-webkit-details-marker { display: none; }
.message-sources summary::before { content: '⌄'; display: inline-block; margin-right: 4px; transition: transform 0.2s; }
.message-sources[open] summary::before { transform: rotate(180deg); }
.message-sources ul { margin: 6px 0 0; padding: 8px 0 0 18px; border-top: 1px solid #eee; }
.user-message { flex-direction: row-reverse; }
.user-message .message-bubble { background: #8B0000; color: #fff; border-top-right-radius: 2px; }
.typing { display: flex; gap: 4px; align-items: center; padding: 14px; }
.typing span {
  width: 6px; height: 6px;
  background: #999;
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }
.chat-input { display: flex; gap: 10px; }
.chat-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}
.chat-input input:focus { border-color: #8B0000; }
.send-btn {
  padding: 10px 24px;
  background: #8B0000;
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
}
.send-btn:disabled { background: #ccc; cursor: not-allowed; }

@media (max-width: 760px) {
  .guide-layout { grid-template-columns: 1fr; }
  .video-area { height: 360px; }
}
</style>

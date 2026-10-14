<template>
<main id="main" tabindex="-1" class="page-width inner-page">
<PageHeading number="01" english="THE DIGITAL GUIDE" title="与历史，面对面。">让数字人小山，陪你读懂山大。<br>选一段故事，或从一个问题开始。</PageHeading>
<div class="guide-layout enter"><section class="guide-stage" aria-label="数字人讲解区"><div class="stage-background"></div><div class="stage-topline"><span class="caps">SHANDONG UNIVERSITY</span><span class="pill"><span class="red-dot"></span>{{ speechTotal ? '正在准备或播放讲解' : '校史讲解员' }}</span></div><div class="stage-mark">山大<br>记忆</div><div id="avatar-canvas"><AvatarViewer ref="avatarViewer" @loaded="avatarReady = true" @error="avatarReady = false" /></div><div class="guide-name"><span>你的校史讲解员</span><strong>小山</strong><small>XIAO SHAN</small></div><div class="stage-controls"><button class="icon-button" :disabled="!speechTotal" @click="stopSpeaking" aria-label="停止讲解"><Icon name="close" /></button><button class="round-play" :disabled="!lastAnswer || loading" @click="speechTotal ? stopSpeaking() : speakAnswer(lastAnswer)" :aria-label="speechTotal ? '停止播放' : '播放最近回答'"><Icon :name="speechTotal ? 'close' : 'play'" /></button><div class="track"><span :style="{width: (speechTotal ? speechSegment / speechTotal * 100 : 0) + '%'}"></span></div><span class="caps">{{ speechSegment }} / {{ speechTotal }}</span><button class="icon-button" :aria-pressed="autoVoice" :aria-label="autoVoice ? '关闭自动朗读' : '开启自动朗读'" @click="autoVoice = !autoVoice; !autoVoice && stopSpeaking()"><Icon :name="autoVoice ? 'volume' : 'mute'" /></button></div></section>
<section class="chat-panel"><header class="panel-heading"><div><span class="eyebrow">ASK XIAO SHAN</span><h2>你想知道的山大</h2></div><button class="text-link" :disabled="loading" @click="startNewConversation">新建对话</button></header><div class="chat-messages" ref="chatContainer" aria-live="polite"><div class="chat-message bot"><span class="chat-avatar">山</span><div><span class="message-name">小山 · 校史讲解员</span><div class="message-bubble">你好，欢迎来到百廿回响。关于山大的故事，你想从哪里听起？</div></div></div><div v-for="(msg, idx) in messages" :key="idx" class="chat-message" :class="msg.role === 'user' ? 'user' : 'bot'"><span class="chat-avatar">{{ msg.role === 'user' ? '你' : '山' }}</span><div><span class="message-name">{{ msg.role === 'user' ? '访客' : '小山' }}</span><div class="message-bubble">{{ msg.content }}<details v-if="msg.sources?.length" class="message-sources"><summary>查看资料依据 · {{ msg.sources.length }}</summary><ul><li v-for="source in msg.sources" :key="source">{{ source }}</li></ul></details></div></div></div><p v-if="loading" role="status">正在查阅校史资料…</p></div><p v-if="speechError" class="service-note" role="status">{{ speechError }}</p><form class="chat-form" @submit.prevent="sendMessage"><label for="question" class="sr-only">输入校史问题</label><input id="question" v-model="inputText" placeholder="写下你的校史问题…" maxlength="1000" required><button class="send-button" :disabled="loading || !inputText.trim()" aria-label="发送问题"><Icon name="arrow" /></button></form><p class="prototype-note">回答依据校史知识库生成，请结合资料依据阅读。</p></section></div>
<section class="topic-section"><div class="section-label"><span>挑选一段故事</span><small>CURATED STORIES</small></div><div class="topic-grid"><button v-for="topic in topics" :key="topic.id" class="topic-card" :class="{active: activeTopic === topic.id}" :disabled="loading" @click="selectTopic(topic)"><span class="topic-number">0{{ topic.id }}</span><div><h3>{{ topic.name }}</h3><p>{{ topic.era }}</p></div><Icon name="arrow" /></button></div></section>
</main></template>
<script setup>
import { onBeforeUnmount, ref, nextTick } from 'vue'
import { chat, textToSpeech, mediaUrl } from '@/api'
import { useRoute } from 'vue-router'
import Icon from '@/components/ExhibitIcon.vue'
import PageHeading from '@/components/PageHeading.vue'
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
const inputText = ref(String(useRoute().query.question || ''))
const speechError = ref('')
const autoVoice = ref(true)
const lastAnswer = ref('')
let disposed = false
const loading = ref(false)
const chatContainer = ref(null)
const avatarReady = ref(false)
const avatarViewer = ref(null)
const CHAT_SESSION_STORAGE_KEY = 'sdu-digital-human-chat-session'
let savedSession = null
try { savedSession = localStorage.getItem(CHAT_SESSION_STORAGE_KEY) } catch {}
const chatSessionId = ref(savedSession)
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
  try { if (sessionId) {
    window.localStorage.setItem(CHAT_SESSION_STORAGE_KEY, sessionId)
  } else {
    window.localStorage.removeItem(CHAT_SESSION_STORAGE_KEY)
  } } catch {}
}

const startNewConversation = async () => {
  stopSpeaking()
  saveChatSessionId(null)
  activeTopic.value = null
  messages.value = []
  lastAnswer.value = ''
  speechError.value = ''
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
    if (disposed) return
    saveChatSessionId(res.session_id || chatSessionId.value)
    const answer = res.answer || '抱歉，我暂时无法回答这个问题。'
    messages.value.push({ role: 'bot', content: answer, sources: res.sources || [] })
    // 语音播放不阻塞下一轮提问；用户可随时停止或发送新问题。
    lastAnswer.value = answer
    if (autoVoice.value) void speakAnswer(answer)
  } catch (e) {
    if (disposed) return
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
    const player = new Audio(mediaUrl(audioUrl))
    player.crossOrigin = 'anonymous'
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
      .then(() => { if (runId !== speechRunId) return; return player.play() })
      .then(() => { if (runId === speechRunId) isSpeaking.value = true })
      .catch(reject)
  })
}

const speakAnswer = async (text) => {
  stopSpeaking()
  speechError.value = ''
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
    if (runId === speechRunId) {
      stopSpeaking()
      speechError.value = '语音暂时未能播放，请点击播放重试；文字回答仍可阅读。'
    }
  } finally {
    if (runId === speechRunId) {
      isSpeaking.value = false
      speechSegment.value = 0
      speechTotal.value = 0
      avatarViewer.value?.stopLipSync()
    }
  }
}

onBeforeUnmount(() => { disposed = true; stopSpeaking() })

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}
</script>

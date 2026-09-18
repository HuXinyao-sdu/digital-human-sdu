<template>
  <div class="guide-page">
    <h2 class="page-title">数字人校史讲解</h2>

    <div class="guide-layout">
      <!-- 数字人展示区 -->
      <div class="avatar-section">
        <div class="avatar-placeholder">
          <div class="avatar-circle">
            <span class="avatar-emoji">🎓</span>
          </div>
          <p class="avatar-name">小山 · 校史讲解员</p>
          <p class="avatar-status" :class="{ speaking: isSpeaking }">
            {{ isSpeaking ? '正在讲解...' : '待命中' }}
          </p>
        </div>
        <div class="video-area">
          <p class="video-hint">数字人视频区域（接入3D模型/AI视频后替换）</p>
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
              @click="selectTopic(topic)"
            >
              <span class="topic-era">{{ topic.era }}</span>
              <span class="topic-name">{{ topic.name }}</span>
            </button>
          </div>
        </div>

        <!-- 问答区 -->
        <div class="chat-panel">
          <h3 class="panel-title">互动问答</h3>
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
              <div class="message-bubble">{{ msg.content }}</div>
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
import { ref, nextTick } from 'vue'
import { chat } from '@/api'

const topics = [
  { id: 1, era: '1901', name: '山东大学堂创办' },
  { id: 2, era: '1920s', name: '齐鲁大学与医学院' },
  { id: 3, era: '1930s', name: '老舍在山大任教' },
  { id: 4, era: '1940s', name: '侯宝璋与医学教育' },
  { id: 5, era: '1950s', name: '院系调整与新山大' },
  { id: 6, era: '当代', name: '趵突泉校区今昔' }
]

const activeTopic = ref(null)
const isSpeaking = ref(false)
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const chatContainer = ref(null)

const selectTopic = (topic) => {
  activeTopic.value = topic.id
  isSpeaking.value = true
  // 模拟讲解（后续替换为实际视频播放/TTS）
  setTimeout(() => { isSpeaking.value = false }, 3000)
}

const sendMessage = async () => {
  if (!inputText.value.trim() || loading.value) return
  const text = inputText.value.trim()
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await chat({ question: text })
    messages.value.push({ role: 'bot', content: res.answer || '抱歉，我暂时无法回答这个问题。' })
  } catch (e) {
    messages.value.push({ role: 'bot', content: '（后端未连接，这是模拟回复）关于这个问题，我正在学习中，敬请期待！' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

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
.avatar-emoji { font-size: 48px; }
.avatar-name { font-size: 17px; font-weight: 600; color: #333; }
.avatar-status { font-size: 13px; color: #999; margin-top: 4px; }
.avatar-status.speaking { color: #8B0000; }
.video-area {
  background: #1a1a1a;
  border-radius: 12px;
  height: 280px;
  display: flex; align-items: center; justify-content: center;
}
.video-hint { color: #666; font-size: 14px; }
.interaction-section { display: flex; flex-direction: column; gap: 16px; }
.panel-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 12px; }
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
</style>

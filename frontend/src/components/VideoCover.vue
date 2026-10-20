<template>
  <span ref="container" class="video-cover">
    <img v-if="cover" :src="cover" :alt="title + ' · 视频首帧'">
    <span v-else class="video-cover-status">{{ failed ? '点击播放动态影像' : '封面加载中…' }}</span>
    <span class="video-cover-play" aria-hidden="true"><Icon name="play" /></span>
  </span>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import Icon from '@/components/ExhibitIcon.vue'

const props = defineProps({ src: { type: String, required: true }, title: { type: String, default: '' } })
const container = ref(null), cover = ref(''), failed = ref(false)
let observer, video, timeout
let visible = false

function release() {
  clearTimeout(timeout)
  if (!video) return
  video.onloadeddata = null
  video.onerror = null
  video.pause()
  video.removeAttribute('src')
  video.load()
  video = null
}

function loadCover() {
  release()
  cover.value = ''
  failed.value = false
  if (!visible) return
  const media = document.createElement('video')
  video = media
  media.crossOrigin = 'anonymous'
  media.muted = true
  media.playsInline = true
  media.preload = 'auto'
  const fail = () => { failed.value = true; release() }
  media.onerror = fail
  // loadeddata means the frame at time zero is decoded; never start playback.
  media.onloadeddata = () => {
    try {
      if (!media.videoWidth || !media.videoHeight) throw new Error('Empty video frame')
      const canvas = document.createElement('canvas')
      const scale = Math.min(1, 800 / media.videoWidth)
      canvas.width = Math.round(media.videoWidth * scale)
      canvas.height = Math.round(media.videoHeight * scale)
      canvas.getContext('2d').drawImage(media, 0, 0, canvas.width, canvas.height)
      cover.value = canvas.toDataURL('image/webp', 0.85)
      release()
    } catch { fail() }
  }
  timeout = setTimeout(fail, 20000)
  media.src = props.src
  media.load()
}

watch(() => props.src, loadCover)
onMounted(() => {
  observer = new IntersectionObserver(entries => {
    if (!entries.some(entry => entry.isIntersecting)) return
    visible = true
    observer.disconnect()
    loadCover()
  }, { rootMargin: '200px' })
  observer.observe(container.value)
})
onBeforeUnmount(() => { observer?.disconnect(); release() })
</script>

<style scoped>
.video-cover{display:block;position:relative;width:100%;height:100%;background:#ddd6c8}
.video-cover img{width:100%;height:100%;object-fit:cover}
.video-cover-status{display:grid;place-items:center;height:100%;padding:60px 15px 15px;color:var(--red);font-size:12px}
.video-cover-play{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:#302e2980;color:white;border:1px solid #ffffffa0;pointer-events:none}
</style>

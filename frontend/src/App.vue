<template>
  <a class="skip-link" href="#main" @click.prevent="skipToMain">跳至正文</a>
  <header class="site-header">
    <RouterLink class="brand" to="/" aria-label="百廿回响 首页"><img class="university-emblem" src="/design-assets/sdu-emblem.png" width="40" height="40" alt="山东大学校徽"><span class="brand-name">山东大学<small>SHANDONG UNIVERSITY</small></span><span class="brand-divider"></span><span class="exhibit-name">百廿回响<small>校史数字展馆</small></span></RouterLink>
    <nav id="navigation" aria-label="主导航" :class="{ open: menuOpen }"><RouterLink v-for="[url, name] in links" :key="url" :to="url" :class="{ active: route.path === url }" :aria-current="route.path === url ? 'page' : undefined">{{ name }}</RouterLink></nav>
    <RouterLink class="header-entry" to="/guide">开启探索 <Icon name="diagonal" /></RouterLink>
    <button class="menu-button icon-button" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-controls="navigation" :aria-label="menuOpen ? '收起导航' : '展开导航'"><Icon :name="menuOpen ? 'close' : 'menu'" /></button>
  </header>
  <RouterView />
  <footer class="site-footer"><div class="footer-top"><RouterLink class="footer-name" to="/">百廿回响<span>在这里，与山大的昨天相遇。</span></RouterLink><p class="motto">学无止境<span>·</span>气有浩然</p><button class="back-top" @click="toTop">回到顶部 ↑</button></div><div class="footer-bottom"><span>山东大学校史数字展馆 · 让历史动起来</span><span>影像来自项目校史资料 · AI 修复效果不等同于历史原貌</span><span>EST. 1901</span></div></footer>
</template>
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Icon from '@/components/ExhibitIcon.vue'
const route = useRoute()
const menuOpen = ref(false)
const links = [['/', '首页'], ['/guide', '数字人讲解'], ['/gallery', '光影展廊'], ['/dialogue', '跨时空对话'], ['/quiz', '校史拾趣']]
watch(() => route.fullPath, () => { menuOpen.value = false })
function toTop() { window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' }) }
function skipToMain() { const main = document.querySelector('main'); main?.focus(); main?.scrollIntoView() }
</script>

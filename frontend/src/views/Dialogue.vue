<template><main id="main" tabindex="-1" class="page-width inner-page"><PageHeading number="03" english="A CONVERSATION ACROSS TIME" title="隔着岁月，仍可对谈。">当治史与行医的目光相遇，<br>听见不同学科之间，共同的求真之心。</PageHeading><div class="dialogue-layout enter"><section class="dialogue-stage"><div class="dialogue-stage-heading"><span class="eyebrow">THE SALON / 学人会客厅</span><span class="pill">创作性演绎</span></div><div class="portrait-pair"><template v-for="(person, i) in people" :key="person.id"><span v-if="i" class="dialogue-between">对<br>话<span>以学问相逢</span></span><div class="portrait-person" :class="{speaking: current?.speaker === person.id, 'is-playing': playing}"><div class="portrait-frame"><img :src="'/design-assets/' + person.id + '.webp'" :alt="person.name + '彩色化肖像'"><span class="speaker-wave"><i v-for="n in 5" :key="n"></i></span></div><span class="portrait-role">{{ person.role }}</span><h2>{{ person.name }}</h2><span class="portrait-line"></span></div></template></div><div class="dialogue-caption" aria-live="polite"><span>{{ current ? names[current.speaker] : '一场跨越时间的思想相遇' }}</span><p>{{ current?.text || '学问的方向不同，求真的心意相通。' }}</p></div><div class="dialogue-controls"><button class="icon-button" @click="reset" aria-label="重置对话"><Icon name="reset"/></button><button class="button primary" @click="toggle"><Icon :name="playing ? 'pause' : 'play'"/>{{ playing ? '暂停对话' : '开始对话' }}</button><button class="icon-button" @click="next" :disabled="step >= turns.length - 1" aria-label="下一轮对话"><Icon name="chevron"/></button><span>{{ step + 1 }} / {{ turns.length }}</span></div></section><aside class="dialogue-notebook"><div class="eyebrow">CONVERSATION NOTES</div><h2>今天，聊些什么？</h2><div class="dialogue-topic-list"><button v-for="(d, i) in dialogues" :key="d.title" :class="{active: topic === i}" @click="reset(); topic = i"><span>0{{ i + 1 }} / {{ d.label }}</span><strong>{{ d.title }}</strong><Icon name="diagonal"/></button></div><div class="transcript-header"><span>对谈手记</span><span>文字演绎</span></div><div class="transcript"><p v-if="step < 0" class="transcript-empty">点击「开始对话」<br>让思想，在此相逢。</p><div v-for="(turn, i) in turns.slice(0, step + 1)" :key="i" class="transcript-turn"><strong>{{ names[turn.speaker] }}</strong><p>{{ turn.text }}</p></div></div><p class="prototype-note">此对话为创作性文字演绎，并非人物真实谈话或历史引语；暂未接入语音。</p></aside></div></main></template>
<script setup>
import { ref, computed, onBeforeUnmount, onMounted } from 'vue'
import { dialogues } from '@/data/exhibit'
import PageHeading from '@/components/PageHeading.vue'
import Icon from '@/components/ExhibitIcon.vue'
const people = [{id:'gu',name:'顾颉刚',role:'史学 · 求真'},{id:'hou',name:'侯宝璋',role:'医学 · 济世'}], names = {gu:'顾颉刚',hou:'侯宝璋'}
const topic = ref(0), step = ref(-1), playing = ref(false)
const turns = computed(() => dialogues[topic.value].turns), current = computed(() => turns.value[step.value])
let timer
function pause() { clearInterval(timer); playing.value = false }
function reset() { pause(); step.value = -1 }
function next() { if (step.value < turns.value.length - 1) step.value++; if (step.value >= turns.value.length - 1) pause() }
function toggle() { if (playing.value) return pause(); if (step.value >= turns.value.length - 1) step.value = -1; playing.value = true; if (step.value < 0) next(); timer = setInterval(next, 8000) }
function hidden() { if (document.hidden) pause() }
onMounted(() => document.addEventListener('visibilitychange', hidden))
onBeforeUnmount(() => { pause(); document.removeEventListener('visibilitychange', hidden) })
</script>

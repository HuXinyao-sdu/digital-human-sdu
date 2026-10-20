<template><div class="page-heading enter"><div class="eyebrow"><span class="small-number">{{ number }}</span>{{ english }}</div><div class="page-title-row"><h1>{{ title }}</h1><p><slot /></p></div></div></template>
<script setup>defineProps(['number', 'english', 'title'])</script>

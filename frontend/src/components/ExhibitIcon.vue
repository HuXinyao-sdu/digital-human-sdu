<template><svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" v-html="paths[name] || paths.arrow"></svg></template>
<script setup>
import { paths } from '@/data/icons'
defineProps({ name: { type: String, default: 'arrow' } })
</script>

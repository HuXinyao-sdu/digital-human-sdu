<template>
  <div class="gallery-page">
    <h2 class="page-title">老照片彩色修复图库</h2>
    <p class="page-desc">历史黑白照片经AI彩色修复，还原真实历史场景</p>

    <div class="filter-bar">
      <button v-for="era in eras" :key="era"
        class="filter-btn" :class="{ active: activeEra === era }"
        @click="activeEra = era">
        {{ era }}
      </button>
    </div>

    <div class="gallery-grid">
      <div v-for="photo in filteredPhotos" :key="photo.id" class="photo-card">
        <div class="photo-wrapper">
          <div class="photo-placeholder" :style="{ background: photo.color }">
            <span class="photo-icon">🖼️</span>
          </div>
          <div class="photo-overlay">
            <span class="overlay-text">点击查看</span>
          </div>
        </div>
        <div class="photo-info">
          <h3 class="photo-title">{{ photo.title }}</h3>
          <p class="photo-era">{{ photo.era }} · {{ photo.location }}</p>
        </div>
      </div>
    </div>

    <div v-if="filteredPhotos.length === 0" class="empty">
      <p>暂无该年代照片</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const eras = ['全部', '1900s', '1920s', '1930s', '1950s', '1980s']
const activeEra = ref('全部')

const photos = ref([
  { id: 1, title: '山东大学堂校门', era: '1900s', location: '济南泺源书院', color: 'linear-gradient(135deg,#d4c5a9,#a89880)' },
  { id: 2, title: '齐鲁大学主楼', era: '1920s', location: '趵突泉校区', color: 'linear-gradient(135deg,#c9b896,#8b7355)' },
  { id: 3, title: '老舍在山大任教', era: '1930s', location: '青岛校区', color: 'linear-gradient(135deg,#b8a88a,#6b5b4a)' },
  { id: 4, title: '侯宝璋在实验室', era: '1930s', location: '齐鲁大学医学院', color: 'linear-gradient(135deg,#a8b5c9,#5a6b80)' },
  { id: 5, title: '院系调整大会', era: '1950s', location: '趵突泉校区', color: 'linear-gradient(135deg,#c9a8a8,#806060)' },
  { id: 6, title: '医学院教学楼', era: '1950s', location: '趵突泉校区', color: 'linear-gradient(135deg,#b8c9a8,#608060)' },
  { id: 7, title: '山东医科大学校门', era: '1980s', location: '趵突泉校区', color: 'linear-gradient(135deg,#a8b8c9,#607080)' },
  { id: 8, title: '校园全景俯瞰', era: '1980s', location: '趵突泉校区', color: 'linear-gradient(135deg,#c9c0a8,#807860)' }
])

const filteredPhotos = computed(() => {
  if (activeEra.value === '全部') return photos.value
  return photos.value.filter(p => p.era === activeEra.value)
})
</script>

<style scoped>
.gallery-page { max-width: 1100px; margin: 0 auto; }
.page-title { font-size: 24px; color: #8B0000; margin-bottom: 8px; padding-left: 12px; border-left: 4px solid #8B0000; }
.page-desc { color: #777; font-size: 14px; margin-bottom: 24px; padding-left: 16px; }
.filter-bar { display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; }
.filter-btn {
  padding: 8px 18px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  transition: all 0.2s;
}
.filter-btn:hover { border-color: #8B0000; color: #8B0000; }
.filter-btn.active { background: #8B0000; color: #fff; border-color: #8B0000; }
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
.photo-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: transform 0.2s;
}
.photo-card:hover { transform: translateY(-4px); }
.photo-wrapper { position: relative; aspect-ratio: 4/3; overflow: hidden; }
.photo-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
}
.photo-icon { font-size: 48px; opacity: 0.5; }
.photo-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.photo-card:hover .photo-overlay { opacity: 1; }
.overlay-text { color: #fff; font-size: 14px; }
.photo-info { padding: 14px 16px; }
.photo-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
.photo-era { font-size: 12px; color: #999; }
.empty { text-align: center; padding: 60px; color: #999; }
</style>

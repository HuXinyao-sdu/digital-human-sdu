<template>
  <div class="home">
    <section class="hero">
      <h1 class="hero-title">让历史动起来</h1>
      <p class="hero-subtitle">山东大学趵突泉校史 · 交互式数字人讲解平台</p>
      <div class="hero-actions">
        <button class="btn btn-primary" @click="$router.push('/guide')">
          开始聆听校史
        </button>
        <button class="btn btn-outline" @click="$router.push('/timeline')">
          浏览时间轴
        </button>
      </div>
    </section>

    <section class="features">
      <div class="feature-card" v-for="item in features" :key="item.title">
        <div class="feature-icon">{{ item.icon }}</div>
        <h3 class="feature-title">{{ item.title }}</h3>
        <p class="feature-desc">{{ item.desc }}</p>
      </div>
    </section>

    <section class="about">
      <h2 class="section-title">项目简介</h2>
      <p class="about-text">
        本项目聚焦山东大学趵突泉校区百年校史，通过AI数字人、老照片彩色修复、
        动态图片处理与RAG智能问答技术，打造可交互、可对话的校史文化体验平台。
        让尘封的历史照片重新焕发光彩，让校史人物的故事被更多人听见。
      </p>
    </section>
  </div>
</template>

<script setup>
const features = [
  { icon: '🎙️', title: 'AI数字人讲解', desc: '虚拟讲解员实时讲述校史故事，支持互动问答' },
  { icon: '🖼️', title: '老照片彩色修复', desc: '历史黑白照片智能上色，还原真实历史场景' },
  { icon: '📅', title: '校史时间轴', desc: '按年代梳理山大发展脉络，点击探索历史细节' },
  { icon: '💬', title: 'RAG智能问答', desc: '基于校史知识库，随时提问获得准确解答' }
]
</script>

<style scoped>
.home { max-width: 1000px; margin: 0 auto; }
.hero {
  text-align: center;
  padding: 60px 20px 50px;
  background: linear-gradient(180deg, #f5f0e8 0%, #faf8f5 100%);
  border-radius: 16px;
  margin-bottom: 40px;
}
.hero-title {
  font-size: 42px;
  font-weight: 700;
  color: #8B0000;
  margin-bottom: 16px;
  letter-spacing: 4px;
}
.hero-subtitle {
  font-size: 18px;
  color: #666;
  margin-bottom: 32px;
}
.hero-actions { display: flex; gap: 16px; justify-content: center; }
.btn {
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-primary { background: #8B0000; color: #fff; }
.btn-primary:hover { background: #6d0000; transform: translateY(-1px); }
.btn-outline { background: transparent; color: #8B0000; border: 1.5px solid #8B0000; }
.btn-outline:hover { background: rgba(139,0,0,0.06); }
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}
.feature-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: transform 0.2s;
}
.feature-card:hover { transform: translateY(-4px); }
.feature-icon { font-size: 36px; margin-bottom: 12px; }
.feature-title { font-size: 17px; font-weight: 600; color: #333; margin-bottom: 8px; }
.feature-desc { font-size: 14px; color: #777; line-height: 1.6; }
.about { background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.section-title { font-size: 22px; color: #8B0000; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #8B0000; }
.about-text { font-size: 15px; color: #555; line-height: 1.9; }
</style>

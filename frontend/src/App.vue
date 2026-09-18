<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo" @click="$router.push('/')">
        <span class="logo-icon">📜</span>
        <span class="logo-text">让历史动起来</span>
      </div>
      <nav class="nav-menu">
        <router-link to="/" class="nav-item">首页</router-link>
        <router-link to="/guide" class="nav-item">数字人讲解</router-link>
        <router-link to="/timeline" class="nav-item">校史时间轴</router-link>
        <router-link to="/gallery" class="nav-item">老照片图库</router-link>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>山东大学人工智能学院 · "让历史动起来"项目组</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
  background: linear-gradient(135deg, #8B0000 0%, #A52A2A 100%);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #fff;
}
.logo-icon { font-size: 24px; }
.logo-text { font-size: 18px; font-weight: 600; letter-spacing: 1px; }
.nav-menu { display: flex; gap: 8px; }
.nav-item {
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 15px;
  transition: all 0.2s;
}
.nav-item:hover { background: rgba(255,255,255,0.15); color: #fff; }
.nav-item.router-link-active { background: rgba(255,255,255,0.2); color: #fff; font-weight: 500; }
.app-main { flex: 1; padding: 32px; max-width: 1200px; margin: 0 auto; width: 100%; }
.app-footer {
  text-align: center;
  padding: 20px;
  background: #2c2c2c;
  color: #999;
  font-size: 13px;
}
</style>

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/guide',
    name: 'Guide',
    component: () => import('@/views/Guide.vue'),
    meta: { title: '数字人讲解' }
  },
  {
    path: '/timeline',
    name: 'Timeline',
    component: () => import('@/views/Timeline.vue'),
    meta: { title: '校史时间轴' }
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/Gallery.vue'),
    meta: { title: '老照片图库' }
  },
  {
    path: '/dialogue', name: 'Dialogue',
    component: () => import('@/views/Dialogue.vue'), meta: { title: '跨时空对话' }
  },
  {
    path: '/quiz', name: 'Quiz',
    component: () => import('@/views/Quiz.vue'), meta: { title: '校史拾趣' }
  },
  {
    path: '/:pathMatch(.*)*', redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, from, saved) { return saved || { top: 0 } },
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '首页'} · 百廿回响`
  next()
})

export default router

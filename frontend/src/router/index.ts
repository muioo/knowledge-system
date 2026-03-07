import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

// 临时占位路由 - 将在后续任务中实现
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'), // 占位组件，稍后创建
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router

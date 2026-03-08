import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { TOKEN_KEY } from '@/utils/constants'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false, title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false, title: '注册' },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'articles',
        name: 'ArticleList',
        component: () => import('@/views/article/ArticleListView.vue'),
        meta: { title: '文章列表' },
      },
      {
        path: 'articles/:id',
        name: 'ArticleDetail',
        component: () => import('@/views/article/ArticleDetailView.vue'),
        meta: { title: '文章详情' },
      },
      {
        path: 'articles/create',
        name: 'ArticleCreate',
        component: () => import('@/views/article/ArticleCreateView.vue'),
        meta: { title: '创建文章' },
      },
      {
        path: 'tags',
        name: 'TagManage',
        component: () => import('@/views/tag/TagManageView.vue'),
        meta: { title: '标签管理' },
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/user/UserManageView.vue'),
        meta: { title: '用户管理', requiresAdmin: true },
      },
      {
        path: 'reading-stats',
        name: 'ReadingStats',
        component: () => import('@/views/reading/ReadingStatsView.vue'),
        meta: { title: '阅读统计' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem(TOKEN_KEY)
  const requiresAuth = to.matched.some((record) => record.meta?.requiresAuth !== false)
  const requiresAdmin = to.matched.some((record) => record.meta?.requiresAdmin === true)

  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 知识管理系统`
  }

  if (requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/dashboard')
  } else if (requiresAdmin && token) {
    // 检查用户是否是管理员
    // 从 localStorage 获取用户信息
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        if (user.role === 'admin') {
          next()
        } else {
          // 非管理员跳转到仪表盘
          next('/dashboard')
        }
      } catch {
        next('/dashboard')
      }
    } else {
      next('/dashboard')
    }
  } else {
    next()
  }
})

export default router

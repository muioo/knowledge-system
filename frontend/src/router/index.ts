/**
 * Vue Router 配置
 * Router configuration with authentication guards
 */

import { createRouter, createWebHistory, type RouteRecordRaw, type NavigationGuardNext, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '../stores/auth'

/**
 * 路由定义
 * Route definitions with lazy loading
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: {
      requiresAuth: false,
      title: 'Login',
    },
  },
  {
    path: '/',
    component: () => import('../layouts/DashboardLayout.vue'),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/dashboard/Dashboard.vue'),
        meta: {
          requiresAuth: true,
          title: 'Dashboard',
        },
      },
      {
        path: 'articles',
        name: 'ArticleList',
        component: () => import('../views/articles/ArticleList.vue'),
        meta: {
          requiresAuth: true,
          title: 'Articles',
        },
      },
      {
        path: 'articles/create',
        name: 'ArticleCreate',
        component: () => import('../views/articles/ArticleCreate.vue'),
        meta: {
          requiresAuth: true,
          title: 'Create Article',
        },
      },
      {
        path: 'articles/:id',
        name: 'ArticleDetail',
        component: () => import('../views/articles/ArticleDetail.vue'),
        meta: {
          requiresAuth: true,
          title: 'Article Detail',
        },
      },
      {
        path: 'articles/:id/edit',
        name: 'ArticleEdit',
        component: () => import('../views/articles/ArticleEdit.vue'),
        meta: {
          requiresAuth: true,
          title: 'Edit Article',
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/error/NotFound.vue'),
    meta: {
      requiresAuth: false,
      title: '404 Not Found',
    },
  },
]

/**
 * 创建路由实例
 * Create router instance
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

/**
 * 全局前置导航守卫
 * Global navigation guard for authentication
 */
router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Knowledge System`
  }

  // 检查是否需要认证
  if (requiresAuth && !authStore.isAuthenticated) {
    // 未登录用户访问需要认证的页面 → 重定向到登录页
    next({
      name: 'Login',
      query: { redirect: to.fullPath }, // 保存目标路径，登录后可跳转回来
    })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页 → 重定向到首页
    next({ name: 'Dashboard' })
  } else {
    // 允许访问
    next()
  }
})

/**
 * 全局后置钩子
 * Global after hook for cleanup
 */
router.afterEach(() => {
  // 可以在这里添加页面加载完成后的逻辑
  // 例如：关闭加载动画、记录页面访问等
})

export default router

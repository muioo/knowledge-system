# 前端布局与文章管理页面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现知识系统前端的 DashboardLayout 布局组件、Sidebar、Header，以及文章列表和文章表单页面

**Architecture:** 采用渐进式实现策略，先搭建布局框架（DashboardLayout + Sidebar + Header），再实现功能页面（ArticleList + ArticleForm）。使用 Vue 3 Composition API + TypeScript + Pinia + Element Plus。

**Tech Stack:** Vue 3.4, TypeScript 5.3, Pinia 2.1, Vue Router 4.2, Element Plus 2.5, Sass

---

## 阶段 1: 路由配置

### Task 1: 创建路由配置文件

**Files:**
- Create: `frontend/src/router/index.ts`

**Step 1: 创建路由配置文件**

```typescript
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../components/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'articles',
        name: 'ArticleList',
        component: () => import('../views/articles/ArticleList.vue')
      },
      {
        path: 'articles/create',
        name: 'ArticleCreate',
        component: () => import('../views/articles/ArticleForm.vue')
      },
      {
        path: 'articles/:id',
        name: 'ArticleDetail',
        component: () => import('../views/articles/ArticleDetail.vue')
      },
      {
        path: 'articles/:id/edit',
        name: 'ArticleEdit',
        component: () => import('../views/articles/ArticleForm.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
```

**Step 2: 提交路由配置**

```bash
git add frontend/src/router/index.ts
git commit -m "feat: 创建路由配置和导航守卫"
```

---

## 阶段 2: 布局组件

### Task 2: 创建 DashboardLayout 组件

**Files:**
- Create: `frontend/src/components/layouts/DashboardLayout.vue`

**Step 1: 创建 DashboardLayout 组件**

```vue
<template>
  <div class="dashboard-layout">
    <Sidebar :collapsed="uiStore.sidebarCollapsed" />
    <div class="main-container" :class="{ 'sidebar-collapsed': uiStore.sidebarCollapsed }">
      <Header />
      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUiStore } from '../../stores/ui'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const uiStore = useUiStore()

onMounted(() => {
  uiStore.initializeSidebar()
})
</script>

<style scoped lang="scss">
.dashboard-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  overflow: hidden;

  &.sidebar-collapsed {
    margin-left: 64px;
  }
}

.content-area {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 24px;
}

@media (max-width: 768px) {
  .main-container {
    margin-left: 0;
  }
}
</style>
```

**Step 2: 提交 DashboardLayout 组件**

```bash
git add frontend/src/components/layouts/DashboardLayout.vue
git commit -m "feat: 创建 DashboardLayout 布局组件"
```

---

### Task 3: 创建 Sidebar 组件

**Files:**
- Create: `frontend/src/components/layouts/Sidebar.vue`

**Step 1: 创建 Sidebar 组件**

```vue
<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div v-if="!collapsed" class="logo">
        <span class="logo-text">知识系统</span>
      </div>
      <el-icon v-else class="logo-icon"><Document /></el-icon>
    </div>

    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :unique-opened="true"
      class="sidebar-menu"
      background-color="#001529"
      text-color="#ffffff"
      active-text-color="#1890ff"
      @select="handleMenuSelect"
    >
      <el-menu-item index="/">
        <el-icon><House /></el-icon>
        <template #title>首页</template>
      </el-menu-item>

      <el-sub-menu index="articles">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>文章管理</span>
        </template>
        <el-menu-item index="/articles">文章列表</el-menu-item>
        <el-menu-item index="/articles/create">创建文章</el-menu-item>
      </el-sub-menu>

      <el-menu-item index="/tags">
        <el-icon><Collection /></el-icon>
        <template #title>标签管理</template>
      </el-menu-item>

      <el-menu-item index="/search">
        <el-icon><Search /></el-icon>
        <template #title>搜索</template>
      </el-menu-item>

      <el-menu-item index="/history">
        <el-icon><Clock /></el-icon>
        <template #title>阅读历史</template>
      </el-menu-item>

      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <template #title>设置</template>
      </el-menu-item>
    </el-menu>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { House, Document, Collection, Search, Clock, Setting } from '@element-plus/icons-vue'

interface Props {
  collapsed: boolean
}

defineProps<Props>()

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/articles')) {
    return path === '/articles/create' ? '/articles/create' : '/articles'
  }
  return path
})

function handleMenuSelect(index: string): void {
  router.push(index)
}
</script>

<style scoped lang="scss">
.sidebar {
  width: 240px;
  height: 100vh;
  background-color: #001529;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;

  &.collapsed {
    width: 64px;
  }
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
}

.logo-icon {
  font-size: 24px;
  color: #1890ff;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;

    &:hover {
      background-color: rgba(255, 255, 255, 0.08);
    }
  }

  :deep(.el-menu-item.is-active) {
    background-color: #1890ff !important;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);

    &.mobile-open {
      transform: translateX(0);
    }
  }
}
</style>
```

**Step 2: 提交 Sidebar 组件**

```bash
git add frontend/src/components/layouts/Sidebar.vue
git commit -m "feat: 创建 Sidebar 侧边栏组件"
```

---

### Task 4: 创建 Header 组件

**Files:**
- Create: `frontend/src/components/layouts/Header.vue`

**Step 1: 创建 Header 组件**

```vue
<template>
  <header class="header">
    <div class="header-left">
      <el-button
        :icon="uiStore.sidebarCollapsed ? Expand : Fold"
        circle
        @click="uiStore.toggleSidebar"
      />
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <el-input
        v-model="searchQuery"
        placeholder="搜索文章..."
        :prefix-icon="Search"
        class="search-input"
        clearable
        @keyup.enter="handleSearch"
      />

      <el-badge :value="0" :hidden="true" class="notification-badge">
        <el-button :icon="Bell" circle />
      </el-badge>

      <el-dropdown @command="handleUserCommand">
        <div class="user-info">
          <el-avatar :size="32" :icon="UserFilled" />
          <span v-if="authStore.user" class="username">{{ authStore.user.username }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人信息
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Fold,
  Expand,
  Search,
  Bell,
  UserFilled,
  User,
  SwitchButton
} from '@element-plus/icons-vue'
import { useUiStore } from '../../stores/ui'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()
const authStore = useAuthStore()

const searchQuery = ref('')

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const breadcrumbList = matched.map(item => ({
    path: item.path,
    title: item.meta.title as string
  }))

  // Fallback breadcrumbs based on route path
  if (breadcrumbList.length === 0) {
    const pathSegments = route.path.split('/').filter(Boolean)
    if (pathSegments.length === 0) {
      return [{ path: '/', title: '首页' }]
    }

    const breadcrumbs = [{ path: '/', title: '首页' }]
    if (pathSegments[0] === 'articles') {
      breadcrumbs.push({ path: '/articles', title: '文章管理' })
      if (pathSegments[1] === 'create') {
        breadcrumbs.push({ path: '/articles/create', title: '创建文章' })
      } else if (pathSegments[1] && pathSegments[2] === 'edit') {
        breadcrumbs.push({ path: route.path, title: '编辑文章' })
      } else if (pathSegments[1]) {
        breadcrumbs.push({ path: route.path, title: '文章详情' })
      }
    }
    return breadcrumbs
  }

  return breadcrumbList
})

function handleSearch(): void {
  if (searchQuery.value.trim()) {
    router.push({ name: 'Search', query: { q: searchQuery.value } })
  }
}

async function handleUserCommand(command: string): Promise<void> {
  if (command === 'profile') {
    router.push({ name: 'Profile' })
  } else if (command === 'logout') {
    try {
      await authStore.logout()
      ElMessage.success('退出登录成功')
      router.push({ name: 'Login' })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '退出登录失败'
      ElMessage.error(errorMessage)
    }
  }
}
</script>

<style scoped lang="scss">
.header {
  height: 64px;
  background-color: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 240px;
}

.notification-badge {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #f5f5f5;
  }
}

.username {
  font-size: 14px;
  color: #333;
}

@media (max-width: 768px) {
  .search-input {
    width: 160px;
  }

  .username {
    display: none;
  }
}
</style>
```

**Step 2: 提交 Header 组件**

```bash
git add frontend/src/components/layouts/Header.vue
git commit -m "feat: 创建 Header 顶部导航组件"
```

---

## 阶段 3: Dashboard 页面

### Task 5: 创建 Dashboard 首页

**Files:**
- Create: `frontend/src/views/Dashboard.vue`

**Step 1: 创建 Dashboard 页面**

```vue
<template>
  <div class="dashboard-page">
    <h1 class="page-title">欢迎使用知识系统</h1>

    <el-row :gutter="24" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#1890ff"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.articleCount }}</div>
              <div class="stat-label">文章总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#52c41a"><Collection /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.tagCount }}</div>
              <div class="stat-label">标签总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#faad14"><View /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.viewCount }}</div>
              <div class="stat-label">总阅读量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f5222d"><Clock /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayCount }}</div>
              <div class="stat-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="content-row">
      <el-col :xs="24" :md="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近文章</span>
              <el-button type="primary" link @click="router.push('/articles')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-empty v-if="recentArticles.length === 0" description="暂无文章" />
          <div v-else class="article-list">
            <div
              v-for="article in recentArticles"
              :key="article.id"
              class="article-item"
              @click="router.push(`/articles/${article.id}`)"
            >
              <div class="article-title">{{ article.title }}</div>
              <div class="article-meta">
                <span>{{ formatDate(article.created_at) }}</span>
                <span>{{ article.view_count }} 次阅读</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card>
          <template #header>
            <span>热门标签</span>
          </template>
          <el-empty v-if="popularTags.length === 0" description="暂无标签" />
          <div v-else class="tag-list">
            <el-tag
              v-for="tag in popularTags"
              :key="tag.id"
              :color="tag.color"
              class="tag-item"
              @click="router.push({ name: 'ArticleList', query: { tag: tag.id } })"
            >
              {{ tag.name }} ({{ tag.article_count }})
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Collection, View, Clock } from '@element-plus/icons-vue'
import { useArticleStore } from '../stores/article'
import { useTagStore } from '../stores/tag'
import { formatDate } from '../utils/date'
import type { Article, Tag } from '../types'

const router = useRouter()
const articleStore = useArticleStore()
const tagStore = useTagStore()

const stats = ref({
  articleCount: 0,
  tagCount: 0,
  viewCount: 0,
  todayCount: 0
})

const recentArticles = ref<Article[]>([])
const popularTags = ref<Tag[]>([])

onMounted(async () => {
  await loadDashboardData()
})

async function loadDashboardData(): Promise<void> {
  try {
    // Load recent articles
    await articleStore.fetchArticles({ page: 1, page_size: 5 })
    recentArticles.value = articleStore.articles.slice(0, 5)

    // Load popular tags
    await tagStore.fetchTags()
    popularTags.value = tagStore.tags.slice(0, 10)

    // Calculate stats
    stats.value.articleCount = articleStore.total
    stats.value.tagCount = tagStore.tags.length
    stats.value.viewCount = recentArticles.value.reduce((sum, article) => sum + article.view_count, 0)
    stats.value.todayCount = 0 // TODO: Implement today's count
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}
</script>

<style scoped lang="scss">
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #333;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  cursor: default;

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.content-row {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.article-item {
  padding: 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: #f5f5f5;
  }
}

.article-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.article-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #999;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.05);
  }
}

@media (max-width: 768px) {
  .stats-row {
    :deep(.el-col) {
      margin-bottom: 16px;
    }
  }

  .content-row {
    :deep(.el-col) {
      margin-bottom: 16px;
    }
  }
}
</style>
```

**Step 2: 提交 Dashboard 页面**

```bash
git add frontend/src/views/Dashboard.vue
git commit -m "feat: 创建 Dashboard 首页"
```

---

## 阶段 4: 文章列表页面

### Task 6: 创建 ArticleList 页面

**Files:**
- Create: `frontend/src/views/articles/ArticleList.vue`

**Step 1: 创建 ArticleList 页面（第1部分）**

```vue
<template>
  <div class="article-list-page">
    <div class="page-header">
      <h1 class="page-title">文章管理</h1>
      <el-button type="primary" :icon="Plus" @click="router.push('/articles/create')">
        创建文章
      </el-button>
    </div>

    <!-- Filters -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索标题或内容"
            :prefix-icon="Search"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="filters.tag_id"
            placeholder="选择标签"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="tag in tagStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-select v-model="filters.sort_by" @change="handleSearch">
            <el-option label="最新创建" value="created_at" />
            <el-option label="最多阅读" value="view_count" />
            <el-option label="最近更新" value="updated_at" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Loading State -->
    <div v-if="articleStore.loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- Error State -->
    <el-alert
      v-else-if="articleStore.error"
      type="error"
      :title="articleStore.error"
      :closable="false"
      show-icon
    />

    <!-- Article List -->
    <div v-else-if="articleStore.articles.length > 0" class="article-list">
      <el-card
        v-for="article in articleStore.articles"
        :key="article.id"
        class="article-card"
        shadow="hover"
      >
        <div class="article-content" @click="handleView(article.id)">
          <div class="article-header">
            <h3 class="article-title">{{ article.title }}</h3>
            <div class="article-tags">
              <el-tag
                v-for="tag in article.tags"
                :key="tag.id"
                :color="tag.color"
                size="small"
              >
                {{ tag.name }}
              </el-tag>
            </div>
          </div>

          <p v-if="article.summary" class="article-summary">
            {{ article.summary }}
          </p>

          <div class="article-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              作者 ID: {{ article.author_id }}
            </span>
            <span class="meta-item">
              <el-icon><View /></el-icon>
              {{ article.view_count }} 次阅读
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatDate(article.created_at) }}
            </span>
          </div>
        </div>

        <div class="article-actions">
          <el-button
            v-if="canEdit(article.author_id)"
            type="warning"
            size="small"
            :icon="Edit"
            @click="handleEdit(article.id)"
          >
            编辑
          </el-button>
          <el-button
            v-if="canDelete(article.author_id)"
            type="danger"
            size="small"
            :icon="Delete"
            @click="handleDelete(article)"
          >
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- Empty State -->
    <el-empty v-else description="暂无文章" />

    <!-- Pagination -->
    <div v-if="articleStore.total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="articleStore.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>
```


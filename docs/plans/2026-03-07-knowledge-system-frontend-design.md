# 知识管理系统前端设计文档

> 版本: v1.0
> 创建日期: 2026-03-07
> 设计方案: 方案一（渐进式实现）

---

## 1. 项目概述

基于后端API文档，创建一个参考 Figma 设计的三栏布局知识管理系统，采用 Vue 3 + TypeScript + Tailwind CSS 技术栈。

### 核心功能

- 用户认证（登录/注册）
- 文章管理（列表、详情、创建、编辑、删除）
- 标签管理（CRUD）
- 搜索功能
- 阅读统计

### 设计参考

参考 `img.png` 中的设计风格：
- 三栏布局（左侧导航、中间内容、右侧统计）
- 蓝色主题（#3B82F6）为主色
- 简洁现代的卡片式设计

---

## 2. 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| TypeScript | 5.x | 类型系统 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Tailwind CSS | 3.x | 样式系统 |
| Element Plus | 2.x | UI组件库 |
| VueUse | 10.x | 组合式函数库 |
| Axios | 1.x | HTTP客户端 |
| Vite | 5.x | 构建工具 |

---

## 3. 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口封装
│   │   ├── auth.ts       # 认证相关接口
│   │   ├── article.ts    # 文章相关接口
│   │   ├── tag.ts        # 标签相关接口
│   │   ├── search.ts     # 搜索相关接口
│   │   ├── reading.ts    # 阅读记录接口
│   │   └── request.ts    # axios封装
│   ├── components/       # 公共组件
│   │   ├── layout/       # 布局组件
│   │   │   ├── AppLayout.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppHeader.vue
│   │   │   └── AppStatsPanel.vue
│   │   ├── article/      # 文章相关组件
│   │   │   ├── ArticleCard.vue
│   │   │   ├── ArticleList.vue
│   │   │   ├── ArticleDetail.vue
│   │   │   └── ArticleForm.vue
│   │   ├── tag/          # 标签相关组件
│   │   │   ├── TagCard.vue
│   │   │   ├── TagGrid.vue
│   │   │   └── TagSelector.vue
│   │   └── common/       # 通用组件
│   │       ├── LoadingSpinner.vue
│   │       ├── ErrorAlert.vue
│   │       ├── EmptyState.vue
│   │       └── Pagination.vue
│   ├── views/            # 页面组件
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── article/
│   │   │   ├── ArticleListView.vue
│   │   │   ├── ArticleDetailView.vue
│   │   │   ├── ArticleCreateView.vue
│   │   │   └── ArticleImportView.vue
│   │   ├── tag/
│   │   │   └── TagManageView.vue
│   │   ├── search/
│   │   │   └── SearchView.vue
│   │   ├── reading/
│   │   │   └── ReadingStatsView.vue
│   │   ├── profile/
│   │   │   └── ProfileView.vue
│   │   └── dashboard/
│   │       └── DashboardView.vue
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── store/            # Pinia状态管理
│   │   ├── auth.ts
│   │   ├── article.ts
│   │   ├── tag.ts
│   │   └── index.ts
│   ├── types/            # TypeScript类型定义
│   │   ├── api.ts        # API响应类型
│   │   ├── article.ts    # 文章类型
│   │   ├── tag.ts        # 标签类型
│   │   └── user.ts       # 用户类型
│   ├── utils/            # 工具函数
│   │   ├── validators.ts
│   │   ├── formatters.ts
│   │   └── constants.ts
│   ├── styles/           # 全局样式
│   │   ├── main.css
│   │   └── tailwind.css
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── public/               # 静态资源
├── example_html/         # HTML示例页面
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

---

## 4. 设计系统

### 4.1 颜色方案

```typescript
// utils/constants.ts
export const colors = {
  primary: '#3B82F6',      // 品牌蓝
  success: '#10B981',      // 成功绿
  accent: '#8B5CF6',       // 强调紫
  warning: '#F59E0B',      // 警告黄
  danger: '#EF4444',       // 危险红
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',        // 边框灰
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',        // 主要文字
    900: '#111827',
  },
  white: '#FFFFFF',
}
```

### 4.2 布局规范

| 区域 | 宽度 | 说明 |
|------|------|------|
| 左侧边栏 | 200px | 固定宽度 |
| 右侧统计面板 | 300px | 固定宽度 |
| 中间内容区 | flex-1 | 自适应 |
| 最大内容宽度 | 1200px | 内容区域最大宽度 |

### 4.3 间距规范

```typescript
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',    // 卡片间距
  lg: '24px',    // 主内容内边距
  xl: '32px',
}
```

### 4.4 字体规范

```typescript
export const typography = {
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  fontSize: {
    xs: '12px',
    sm: '14px',     // 描述文字
    base: '16px',   // 副标题
    lg: '18px',     // 内容标题
    xl: '24px',     // 标题
    '2xl': '32px',  // 大标题
  },
  fontWeight: {
    normal: '400',
    medium: '500',
    bold: '600',
  },
}
```

---

## 5. 核心组件设计

### 5.1 布局组件

#### AppLayout.vue

主布局容器，包含三栏布局结构。

```vue
<template>
  <div class="app-layout">
    <AppSidebar />
    <main class="main-content">
      <router-view />
    </main>
    <AppStatsPanel />
  </div>
</template>
```

#### AppSidebar.vue

左侧导航菜单组件。

**菜单项**：
- 📊 仪表盘 (Dashboard)
- 📚 文章管理
  - 📝 文章列表
  - ➕ 创建文章
  - 📥 URL导入
- 🏷️ 标签管理 (Tags)
- 🔍 搜索 (Search)
- 📖 阅读统计 (Reading Stats)
- 👤 个人资料 (Profile)
- ⚙️ 设置 (Settings)

#### AppStatsPanel.vue

右侧统计面板组件。

**显示内容**：
- 阅读统计（总阅读数、本月阅读）
- 热门标签（标签云）
- 最近阅读（文章列表）

### 5.2 文章组件

#### ArticleCard.vue

文章卡片组件，显示文章摘要信息。

**Props**：
```typescript
interface ArticleCardProps {
  article: Article
  showActions?: boolean  // 是否显示操作按钮
}
```

**显示内容**：
- 文章标题
- 文章摘要
- 标签列表
- 浏览量
- 创建时间

#### ArticleList.vue

文章列表组件，包含搜索、筛选、分页功能。

**Props**：
```typescript
interface ArticleListProps {
  articles: Article[]
  pagination: PaginationInfo
  loading?: boolean
}
```

#### ArticleForm.vue

文章创建/编辑表单组件。

**表单字段**：
- 标题（必填，1-255字符）
- 摘要（必填）
- 关键词（必填）
- 标签（多选）
- 文件上传 / URL输入

### 5.3 标签组件

#### TagCard.vue

标签卡片组件，显示标签信息和关联文章数。

**Props**：
```typescript
interface TagCardProps {
  tag: Tag
  articleCount: number
  showActions?: boolean
}
```

#### TagSelector.vue

标签选择器组件，支持多选。

**Props**：
```typescript
interface TagSelectorProps {
  modelValue: number[]  // 选中的标签ID列表
  multiple?: boolean    // 是否多选
}
```

---

## 6. 状态管理

### 6.1 Auth Store

```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

interface AuthActions {
  login(username: string, password: string): Promise<void>
  register(data: RegisterData): Promise<void>
  logout(): void
  refreshToken(): Promise<void>
  fetchUser(): Promise<void>
}
```

### 6.2 Article Store

```typescript
interface ArticleState {
  articles: Article[]
  currentArticle: Article | null
  pagination: {
    total: number
    page: number
    size: number
  }
  filters: {
    tagId?: number
    searchQuery?: string
  }
  loading: boolean
}

interface ArticleActions {
  fetchArticles(params?: FetchParams): Promise<void>
  fetchArticle(id: number): Promise<void>
  createArticle(data: CreateArticleData): Promise<Article>
  updateArticle(id: number, data: UpdateArticleData): Promise<Article>
  deleteArticle(id: number): Promise<void>
  uploadArticle(file: File, data: ArticleFormData): Promise<Article>
  importFromUrl(data: UrlImportData): Promise<Article>
  setFilters(filters: Partial<ArticleState['filters']>): void
}
```

### 6.3 Tag Store

```typescript
interface TagState {
  tags: Tag[]
  selectedTags: number[]
  loading: boolean
}

interface TagActions {
  fetchTags(): Promise<void>
  createTag(data: CreateTagData): Promise<Tag>
  updateTag(id: number, data: UpdateTagData): Promise<Tag>
  deleteTag(id: number): Promise<void>
  setSelectedTags(tagIds: number[]): void
}
```

---

## 7. 路由配置

```typescript
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue')
      },
      {
        path: 'articles',
        name: 'ArticleList',
        component: () => import('@/views/article/ArticleListView.vue')
      },
      {
        path: 'articles/:id',
        name: 'ArticleDetail',
        component: () => import('@/views/article/ArticleDetailView.vue')
      },
      {
        path: 'articles/create',
        name: 'ArticleCreate',
        component: () => import('@/views/article/ArticleCreateView.vue')
      },
      {
        path: 'articles/import',
        name: 'ArticleImport',
        component: () => import('@/views/article/ArticleImportView.vue')
      },
      {
        path: 'tags',
        name: 'TagManage',
        component: () => import('@/views/tag/TagManageView.vue')
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('@/views/search/SearchView.vue')
      },
      {
        path: 'reading/stats',
        name: 'ReadingStats',
        component: () => import('@/views/reading/ReadingStatsView.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileView.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/SettingsView.vue')
      }
    ]
  }
]
```

### 路由守卫

```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})
```

---

## 8. API 封装

### 8.1 请求配置

```typescript
// api/request.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const authStore = useAuthStore()

    // Token过期，尝试刷新
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true
      try {
        await authStore.refreshToken()
        return apiClient(error.config)
      } catch {
        authStore.logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)
```

### 8.2 API 接口定义

```typescript
// api/article.ts
export const articleApi = {
  // 获取文章列表
  getList: (params?: { page?: number; size?: number; tag_id?: number }) =>
    apiClient.get('/articles/', { params }),

  // 获取文章详情
  getDetail: (id: number) =>
    apiClient.get(`/articles/${id}`),

  // 上传文件创建文章
  upload: (data: FormData) =>
    apiClient.post('/articles/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  // URL导入文章
  importFromUrl: (data: { url: string; tag_ids?: number[]; title?: string }) =>
    apiClient.post('/articles/from-url-html', data),

  // 更新文章
  update: (id: number, data: Partial<Article>) =>
    apiClient.put(`/articles/${id}`, data),

  // 删除文章
  delete: (id: number) =>
    apiClient.delete(`/articles/${id}`),

  // 获取文章HTML内容
  getHtml: (id: number) =>
    apiClient.get(`/articles/${id}/html`),
}
```

---

## 9. 数据流设计

### 9.1 认证流程

```
用户输入 → 表单验证 → API调用
   ↓
成功 → 保存Token → 更新Store → 跳转首页
   ↓
失败 → 显示错误提示 → 保持在登录页
```

### 9.2 文章列表加载流程

```
页面加载 → 从Store获取筛选条件 → API调用
   ↓
成功 → 更新Store文章列表 → 渲染列表
   ↓
失败 → 显示错误提示 → 显示重试按钮
```

### 9.3 文章创建流程

```
用户填写表单 → 表单验证
   ↓
选择方式：上传/URL导入
   ↓
上传文件 → API上传 → 创建文章记录
URL导入 → 抓取内容 → AI提取 → 创建文章记录
   ↓
成功 → 跳转文章详情 / 显示成功提示
失败 → 显示错误 → 保留表单数据
```

---

## 10. 错误处理策略

### 10.1 网络错误
- 请求失败时显示友好提示
- 提供重试按钮
- 网络恢复后自动重试（可选）

### 10.2 认证错误
- Token过期自动跳转登录
- 401/403权限提示
- 登录后返回原页面

### 10.3 表单验证错误
- 实时验证反馈
- 错误信息定位到具体字段
- 提交前整体验证

### 10.4 业务错误
- 文章不存在（404）引导返回列表
- 文件过大提示大小限制
- URL导入失败提供替代方案

---

## 11. 实施阶段

### 阶段一：认证 + 基础布局框架

**Week 1: 项目初始化 + 认证**
- Day 1-2: 项目脚手架、依赖安装、配置
- Day 3-4: 登录/注册页面开发
- Day 5: API封装、Store初始化、路由守卫

**Week 2: 布局框架 + 文章列表**
- Day 1-2: 三栏布局组件开发
- Day 3-4: 文章列表页面
- Day 5: 右侧统计面板

**Week 3: 文章详情 + 创建**
- Day 1-2: 文章详情页面
- Day 3-4: 文章创建（上传/URL导入）
- Day 5: 测试和修复

**Week 4: 标签管理 + 优化**
- Day 1-2: 标签管理页面
- Day 3: 搜索功能
- Day 4: 性能优化和测试
- Day 5: 文档和部署准备

### 阶段二：完善功能

- 阅读统计页面
- 个人资料页面
- 设置页面
- 数据可视化

### 阶段三：优化和部署

- 性能优化
- SEO优化
- 部署配置

---

## 12. 类型定义

```typescript
// types/api.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface ApiPaginationResponse<T> {
  total: number
  page: number
  size: number
  items: T[]
}

// types/article.ts
export interface Article {
  id: number
  title: string
  source_url: string | null
  summary: string | null
  keywords: string | null
  author_id: number
  original_filename: string | null
  view_count: number
  created_at: string
  updated_at: string
  tags: TagInfo[]
  html_content: string | null
  html_path: string | null
  processing_status: string | null
  original_html_url: string | null
}

export interface TagInfo {
  id: number
  name: string
  color: string
}

// types/tag.ts
export interface Tag {
  id: number
  name: string
  color: string
  created_at: string
}

// types/user.ts
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}
```

---

## 13. 总结

本设计文档基于后端API文档和参考设计图，制定了完整的前端实现方案。采用渐进式开发策略，分阶段实现核心功能，确保项目稳步推进。

**核心优势**：
- 清晰的技术栈和架构设计
- 完善的组件和状态管理方案
- 详细的实施计划和时间表
- 参考Figma设计的一致性保证

**下一步**：创建详细的实施计划文档

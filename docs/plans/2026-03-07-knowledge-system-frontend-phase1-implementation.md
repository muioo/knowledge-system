# 知识管理系统前端 - 第一阶段实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建知识管理系统前端的基础框架，包括项目初始化、用户认证功能和三栏布局系统

**Architecture:** 采用 Vue 3 + TypeScript + Pinia + Vue Router + Tailwind CSS 技术栈，实现完整的用户认证流程和三栏响应式布局（左侧导航、中间内容、右侧统计面板）

**Tech Stack:** Vue 3.4+, TypeScript 5.0+, Vite 5.0+, Pinia 2.1+, Vue Router 4.2+, Tailwind CSS 3.4+, Element Plus 2.5+, Axios 1.6+

---

## Phase 1 任务概览

### 1. 项目初始化
### 2. 类型定义系统
### 3. API 请求封装
### 4. Pinia 状态管理
### 5. 路由配置
### 6. 认证功能（登录/注册）
### 7. 布局组件系统
### 8. 路由守卫和认证流程

---

## Task 1: 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/styles/main.css`
- Create: `frontend/.env.development`
- Create: `frontend/.env.production`

**Step 1: 创建 package.json**

```json
{
  "name": "knowledge-system-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix"
  },
  "dependencies": {
    "vue": "^3.4.21",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.7",
    "@vueuse/core": "^10.9.0",
    "axios": "^1.6.7",
    "element-plus": "^2.6.1",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.4",
    "vite": "^5.1.6",
    "vue-tsc": "^2.0.6",
    "typescript": "^5.4.2",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.18",
    "@types/node": "^20.11.28"
  }
}
```

**Step 2: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

**Step 3: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 4: 创建 tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Step 5: 创建 tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        success: '#10B981',
        accent: '#8B5CF6',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

**Step 6: 创建 postcss.config.js**

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**Step 7: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/svg+xml" href="/vite.svg">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识管理系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

**Step 8: 创建 src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/main.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

**Step 9: 创建 src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
// App根组件
</script>
```

**Step 10: 创建 src/styles/main.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-800;
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors;
  }

  .card {
    @apply bg-white rounded-lg border border-gray-200 p-6;
  }
}
```

**Step 11: 创建环境配置文件**

创建 `.env.development`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

创建 `.env.production`:
```env
VITE_API_BASE_URL=/api/v1
```

**Step 12: 安装依赖并验证**

Run:
```bash
cd frontend
npm install
npm run dev
```

Expected: Vite开发服务器启动在 http://localhost:3000

**Step 13: 提交**

```bash
git add frontend/
git commit -m "feat: 初始化前端项目配置

- 配置 Vite + Vue 3 + TypeScript
- 配置 Tailwind CSS
- 配置 Element Plus
- 创建基础目录结构

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 类型定义系统

**Files:**
- Create: `frontend/src/types/api.ts`
- Create: `frontend/src/types/user.ts`
- Create: `frontend/src/types/article.ts`
- Create: `frontend/src/types/tag.ts`
- Create: `frontend/src/types/common.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: 创建 API 响应类型**

创建 `src/types/api.ts`:

```typescript
// 统一API响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页响应格式
export interface ApiPaginationResponse<T> {
  total: number
  page: number
  size: number
  items: T[]
}

// 分页参数
export interface PaginationParams {
  page?: number
  size?: number
}

// 错误响应
export interface ApiError {
  detail: string | Array<{
    loc: string[]
    msg: string
    type: string
  }>
}
```

**Step 2: 创建用户类型**

创建 `src/types/user.ts`:

```typescript
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface UpdateUserRequest {
  email?: string
  password?: string
}
```

**Step 3: 创建文章类型**

创建 `src/types/article.ts`:

```typescript
export interface TagInfo {
  id: number
  name: string
  color: string
}

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

export interface CreateArticleRequest {
  title: string
  summary: string
  keywords: string
  tag_ids?: number[]
}

export interface UpdateArticleRequest {
  title?: string
  source_url?: string
  summary?: string
  keywords?: string
  tag_ids?: number[]
}

export interface UploadArticleRequest extends CreateArticleRequest {
  file: File
}

export interface UrlImportRequest {
  url: string
  tag_ids?: number[]
  title?: string
}

export interface ArticleListParams {
  page?: number
  size?: number
  tag_id?: number
}
```

**Step 4: 创建标签类型**

创建 `src/types/tag.ts`:

```typescript
export interface Tag {
  id: number
  name: string
  color: string
  created_at: string
}

export interface CreateTagRequest {
  name: string
  color?: string
}

export interface UpdateTagRequest {
  name?: string
  color?: string
}
```

**Step 5: 创建通用类型**

创建 `src/types/common.ts`:

```typescript
export interface PaginationInfo {
  total: number
  page: number
  size: number
}

export interface SelectOption {
  label: string
  value: string | number
}

export interface MenuItem {
  path: string
  name: string
  icon?: string
  children?: MenuItem[]
}
```

**Step 6: 创建类型导出索引**

创建 `src/types/index.ts`:

```typescript
export * from './api'
export * from './user'
export * from './article'
export * from './tag'
export * from './common'
```

**Step 7: 提交**

```bash
git add frontend/src/types/
git commit -m "feat: 添加 TypeScript 类型定义

- API 响应类型
- 用户相关类型
- 文章相关类型
- 标签相关类型
- 通用类型

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: API 请求封装

**Files:**
- Create: `frontend/src/api/request.ts`
- Create: `frontend/src/utils/validators.ts`
- Create: `frontend/src/utils/formatters.ts`
- Create: `frontend/src/utils/constants.ts`

**Step 1: 创建常量定义**

创建 `src/utils/constants.ts`:

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const TOKEN_KEY = 'access_token'
export const REFRESH_TOKEN_KEY = 'refresh_token'
export const USER_KEY = 'user'

export const COLORS = {
  primary: '#3B82F6',
  success: '#10B981',
  accent: '#8B5CF6',
  warning: '#F59E0B',
  danger: '#EF4444',
}

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_SIZE: 20,
  MAX_SIZE: 100,
}
```

**Step 2: 创建工具函数**

创建 `src/utils/formatters.ts`:

```typescript
// 格式化日期
export function formatDate(date: string): string {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 格式化文件大小
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 截断文本
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
```

创建 `src/utils/validators.ts`:

```typescript
// 验证用户名
export function validateUsername(username: string): boolean {
  return username.length >= 3 && username.length <= 50
}

// 验证邮箱
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 验证密码
export function validatePassword(password: string): boolean {
  return password.length >= 6 && password.length <= 50
}

// 验证文章标题
export function validateTitle(title: string): boolean {
  return title.length >= 1 && title.length <= 255
}
```

**Step 3: 创建 Axios 请求封装**

创建 `src/api/request.ts`:

```typescript
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE_URL, TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/utils/constants'

// 扩展请求配置类型
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: CustomAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig

    // Token 过期处理
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data.data
          localStorage.setItem(TOKEN_KEY, access_token)

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // 刷新失败，清除 token 并跳转登录
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // 错误提示
    const message = error.response?.data?.detail || '请求失败，请稍后重试'
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

export default apiClient
```

**Step 4: 提交**

```bash
git add frontend/src/api/ frontend/src/utils/
git commit -m "feat: 添加 API 请求封装和工具函数

- Axios 实例配置和拦截器
- Token 自动刷新机制
- 统一错误处理
- 工具函数（格式化、验证）
- 常量定义

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 创建 API 接口模块

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/user.ts`
- Create: `frontend/src/api/article.ts`
- Create: `frontend/src/api/tag.ts`
- Create: `frontend/src/api/index.ts`

**Step 1: 创建认证 API**

创建 `src/api/auth.ts`:

```typescript
import apiClient from './request'
import type {
  ApiResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '@/types'

export const authApi = {
  // 用户登录
  login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    return apiClient.post('/auth/login', data)
  },

  // 用户注册
  register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    return apiClient.post('/auth/register', data)
  },

  // 刷新 Token
  refreshToken(refreshToken: string): Promise<ApiResponse<AuthResponse>> {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken })
  },
}
```

**Step 2: 创建用户 API**

创建 `src/api/user.ts`:

```typescript
import apiClient from './request'
import type {
  ApiResponse,
  User,
  UpdateUserRequest,
  ApiPaginationResponse,
} from '@/types'

export const userApi = {
  // 获取当前用户信息
  getMe(): Promise<ApiResponse<User>> {
    return apiClient.get('/users/me')
  },

  // 更新当前用户信息
  updateMe(data: UpdateUserRequest): Promise<ApiResponse<User>> {
    return apiClient.put('/users/me', data)
  },

  // 删除当前用户
  deleteMe(): Promise<void> {
    return apiClient.delete('/users/me')
  },

  // 获取用户列表（管理员）
  getList(params?: { page?: number; size?: number }): Promise<ApiResponse<ApiPaginationResponse<User>>> {
    return apiClient.get('/users/', { params })
  },

  // 获取指定用户（管理员）
  getById(userId: number): Promise<ApiResponse<User>> {
    return apiClient.get(`/users/${userId}`)
  },

  // 更新指定用户（管理员）
  updateUser(userId: number, data: UpdateUserRequest): Promise<ApiResponse<User>> {
    return apiClient.put(`/users/${userId}`, data)
  },

  // 删除指定用户（管理员）
  deleteUser(userId: number): Promise<void> {
    return apiClient.delete(`/users/${userId}`)
  },

  // 更新用户角色（管理员）
  updateUserRole(userId: number, role: 'admin' | 'user'): Promise<ApiResponse<User>> {
    return apiClient.patch(`/users/${userId}/role`, { role })
  },
}
```

**Step 3: 创建文章 API**

创建 `src/api/article.ts`:

```typescript
import apiClient from './request'
import type {
  ApiResponse,
  Article,
  ApiPaginationResponse,
  ArticleListParams,
  CreateArticleRequest,
  UpdateArticleRequest,
  UrlImportRequest,
} from '@/types'

export const articleApi = {
  // 获取文章列表
  getList(params?: ArticleListParams): Promise<ApiResponse<ApiPaginationResponse<Article>>> {
    return apiClient.get('/articles/', { params })
  },

  // 获取文章详情
  getDetail(articleId: number): Promise<ApiResponse<Article>> {
    return apiClient.get(`/articles/${articleId}`)
  },

  // 上传文件创建文章
  upload(data: FormData): Promise<ApiResponse<Article>> {
    return apiClient.post('/articles/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // URL 导入文章
  importFromUrl(data: UrlImportRequest): Promise<ApiResponse<Article>> {
    return apiClient.post('/articles/from-url-html', data)
  },

  // 更新文章
  update(articleId: number, data: UpdateArticleRequest): Promise<ApiResponse<Article>> {
    return apiClient.put(`/articles/${articleId}`, data)
  },

  // 删除文章
  delete(articleId: number): Promise<void> {
    return apiClient.delete(`/articles/${articleId}`)
  },

  // 获取文章 HTML 内容
  getHtml(articleId: number): Promise<ApiResponse<Article>> {
    return apiClient.get(`/articles/${articleId}/html`)
  },
}
```

**Step 4: 创建标签 API**

创建 `src/api/tag.ts`:

```typescript
import apiClient from './request'
import type {
  ApiResponse,
  Tag,
  Article,
  CreateTagRequest,
  UpdateTagRequest,
  ApiPaginationResponse,
} from '@/types'

export const tagApi = {
  // 获取所有标签
  getAll(): Promise<ApiResponse<Tag[]>> {
    return apiClient.get('/tags/')
  },

  // 获取标签详情
  getDetail(tagId: number): Promise<ApiResponse<Tag>> {
    return apiClient.get(`/tags/${tagId}`)
  },

  // 创建标签
  create(data: CreateTagRequest): Promise<ApiResponse<Tag>> {
    return apiClient.post('/tags/', data)
  },

  // 更新标签
  update(tagId: number, data: UpdateTagRequest): Promise<ApiResponse<Tag>> {
    return apiClient.put(`/tags/${tagId}`, data)
  },

  // 删除标签
  delete(tagId: number): Promise<void> {
    return apiClient.delete(`/tags/${tagId}`)
  },

  // 获取标签下的文章
  getArticles(tagId: number, params?: { page?: number; size?: number }): Promise<ApiResponse<ApiPaginationResponse<Article>>> {
    return apiClient.get(`/tags/${tagId}/articles`, { params })
  },
}
```

**Step 5: 创建 API 导出索引**

创建 `src/api/index.ts`:

```typescript
export * from './auth'
export * from './user'
export * from './article'
export * from './tag'
export { default as apiClient } from './request'
```

**Step 6: 提交**

```bash
git add frontend/src/api/
git commit -m "feat: 添加 API 接口模块

- 认证接口（登录、注册、刷新token）
- 用户接口（CRUD、角色管理）
- 文章接口（列表、详情、创建、更新、删除、HTML内容）
- 标签接口（CRUD、标签文章）
- API 导出索引

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 创建 Pinia Store

**Files:**
- Create: `frontend/src/store/auth.ts`
- Create: `frontend/src/store/article.ts`
- Create: `frontend/src/store/tag.ts`
- Create: `frontend/src/store/index.ts`

**Step 1: 创建认证 Store**

创建 `src/store/auth.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '@/utils/constants'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  async function login(credentials: LoginRequest) {
    loading.value = true
    try {
      const response = await authApi.login(credentials)
      const { access_token, refresh_token, user: userData } = response.data

      token.value = access_token
      user.value = userData

      localStorage.setItem(TOKEN_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
      localStorage.setItem(USER_KEY, JSON.stringify(userData))

      return response
    } finally {
      loading.value = false
    }
  }

  async function register(data: RegisterRequest) {
    loading.value = true
    try {
      const response = await authApi.register(data)
      const { access_token, refresh_token, user: userData } = response.data

      token.value = access_token
      user.value = userData

      localStorage.setItem(TOKEN_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
      localStorage.setItem(USER_KEY, JSON.stringify(userData))

      return response
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return

    try {
      const response = await userApi.getMe()
      user.value = response.data
      localStorage.setItem(USER_KEY, JSON.stringify(response.data))
    } catch (error) {
      logout()
    }
  }

  async function refreshToken() {
    const refreshTokenValue = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshTokenValue) throw new Error('No refresh token')

    const response = await authApi.refreshToken(refreshTokenValue)
    const { access_token } = response.data

    token.value = access_token
    localStorage.setItem(TOKEN_KEY, access_token)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  // 从 localStorage 恢复状态
  function restoreState() {
    const savedToken = localStorage.getItem(TOKEN_KEY)
    const savedUser = localStorage.getItem(USER_KEY)

    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchUser,
    refreshToken,
    logout,
    restoreState,
  }
})
```

**Step 2: 创建文章 Store**

创建 `src/store/article.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { articleApi } from '@/api'
import type { Article, ArticleListParams, PaginationInfo } from '@/types'

export const useArticleStore = defineStore('article', () => {
  // State
  const articles = ref<Article[]>([])
  const currentArticle = ref<Article | null>(null)
  const pagination = ref<PaginationInfo>({
    total: 0,
    page: 1,
    size: 20,
  })
  const filters = ref<ArticleListParams>({})
  const loading = ref(false)

  // Getters
  const hasMore = computed(() => {
    return pagination.value.page * pagination.value.size < pagination.value.total
  })

  // Actions
  async function fetchArticles(params?: ArticleListParams) {
    loading.value = true
    try {
      const response = await articleApi.getList(params || filters.value)
      articles.value = response.data.items
      pagination.value = {
        total: response.data.total,
        page: response.data.page,
        size: response.data.size,
      }
      if (params) {
        filters.value = params
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchArticle(articleId: number) {
    loading.value = true
    try {
      const response = await articleApi.getDetail(articleId)
      currentArticle.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function uploadArticle(file: File, data: { title: string; summary: string; keywords: string; tag_ids?: string }) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    formData.append('summary', data.summary)
    formData.append('keywords', data.keywords)
    if (data.tag_ids) {
      formData.append('tag_ids', data.tag_ids)
    }

    const response = await articleApi.upload(formData)
    return response.data
  }

  async function importFromUrl(data: { url: string; tag_ids?: number[]; title?: string }) {
    const response = await articleApi.importFromUrl(data)
    return response.data
  }

  function setFilters(newFilters: Partial<ArticleListParams>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters() {
    filters.value = {}
  }

  return {
    articles,
    currentArticle,
    pagination,
    filters,
    loading,
    hasMore,
    fetchArticles,
    fetchArticle,
    uploadArticle,
    importFromUrl,
    setFilters,
    resetFilters,
  }
})
```

**Step 3: 创建标签 Store**

创建 `src/store/tag.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagApi } from '@/api'
import type { Tag, CreateTagRequest, UpdateTagRequest } from '@/types'

export const useTagStore = defineStore('tag', () => {
  // State
  const tags = ref<Tag[]>([])
  const selectedTags = ref<number[]>([])
  const loading = ref(false)

  // Actions
  async function fetchTags() {
    loading.value = true
    try {
      const response = await tagApi.getAll()
      tags.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function createTag(data: CreateTagRequest) {
    const response = await tagApi.create(data)
    tags.value.push(response.data)
    return response.data
  }

  async function updateTag(tagId: number, data: UpdateTagRequest) {
    const response = await tagApi.update(tagId, data)
    const index = tags.value.findIndex(t => t.id === tagId)
    if (index !== -1) {
      tags.value[index] = response.data
    }
    return response.data
  }

  async function deleteTag(tagId: number) {
    await tagApi.delete(tagId)
    tags.value = tags.value.filter(t => t.id !== tagId)
  }

  function setSelectedTags(tagIds: number[]) {
    selectedTags.value = tagIds
  }

  function toggleTag(tagId: number) {
    const index = selectedTags.value.indexOf(tagId)
    if (index === -1) {
      selectedTags.value.push(tagId)
    } else {
      selectedTags.value.splice(index, 1)
    }
  }

  return {
    tags,
    selectedTags,
    loading,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    setSelectedTags,
    toggleTag,
  }
})
```

**Step 4: 创建 Store 导出索引**

创建 `src/store/index.ts`:

```typescript
export * from './auth'
export * from './article'
export * from './tag'
```

**Step 5: 提交**

```bash
git add frontend/src/store/
git commit -m "feat: 添加 Pinia 状态管理

- 认证 Store（登录、注册、登出、状态恢复）
- 文章 Store（列表、详情、上传、导入、筛选）
- 标签 Store（CRUD、选中状态）
- Store 导出索引

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 创建路由配置

**Files:**
- Create: `frontend/src/router/index.ts`

**Step 1: 创建路由配置**

创建 `src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

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
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.matched.some(record => record.meta?.requiresAuth !== false)

  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 知识管理系统`
  }

  if (requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
```

**Step 2: 提交**

```bash
git add frontend/src/router/
git commit -m "feat: 添加路由配置

- 定义所有路由
- 路由元信息（认证、标题）
- 路由守卫（认证检查）
- 自动重定向逻辑

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 创建登录页面

**Files:**
- Create: `frontend/src/views/auth/Login.vue`

**Step 1: 创建登录页面组件**

创建 `src/views/auth/Login.vue`:

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo 和标题 -->
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900">知识管理系统</h2>
        <p class="mt-2 text-sm text-gray-600">Knowledge Management System</p>
      </div>

      <!-- 登录表单 -->
      <el-card class="shadow-lg">
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900">登录到您的账户</h3>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="authStore.loading"
            @click="handleLogin"
            class="w-full"
          >
            登录
          </el-button>
        </el-form>

        <div class="mt-4 text-center text-sm">
          <span class="text-gray-600">还没有账户？</span>
          <router-link to="/register" class="text-primary hover:text-blue-600 font-medium">
            立即注册
          </router-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await authStore.login({ username: form.username, password: form.password })
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (error) {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  })
}
</script>
```

**Step 2: 提交**

```bash
git add frontend/src/views/auth/Login.vue
git commit -m "feat: 添加登录页面

- 用户名/密码表单
- 表单验证
- 登录逻辑
- 跳转到注册页面
- 响应式设计

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 创建注册页面

**Files:**
- Create: `frontend/src/views/auth/Register.vue`

**Step 1: 创建注册页面组件**

创建 `src/views/auth/Register.vue`:

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo 和标题 -->
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900">知识管理系统</h2>
        <p class="mt-2 text-sm text-gray-600">Knowledge Management System</p>
      </div>

      <!-- 注册表单 -->
      <el-card class="shadow-lg">
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900">创建新账户</h3>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名（3-50字符）"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱"
              :prefix-icon="Message"
              size="large"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码（6-50字符）"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="authStore.loading"
            @click="handleRegister"
            class="w-full"
          >
            注册
          </el-button>
        </el-form>

        <div class="mt-4 text-center text-sm">
          <span class="text-gray-600">已有账户？</span>
          <router-link to="/login" class="text-primary hover:text-blue-600 font-medium">
            立即登录
          </router-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

async function handleRegister() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password,
      })
      ElMessage.success('注册成功')
      router.push('/dashboard')
    } catch (error) {
      ElMessage.error('注册失败，请稍后重试')
    }
  })
}
</script>
```

**Step 2: 提交**

```bash
git add frontend/src/views/auth/Register.vue
git commit -m "feat: 添加注册页面

- 用户名/邮箱/密码表单
- 表单验证（包括确认密码）
- 注册逻辑
- 跳转到登录页面
- 响应式设计

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 9: 创建布局组件系统

**Files:**
- Create: `frontend/src/components/layout/AppLayout.vue`
- Create: `frontend/src/components/layout/AppSidebar.vue`
- Create: `frontend/src/components/layout/AppHeader.vue`
- Create: `frontend/src/components/layout/AppStatsPanel.vue`

**Step 1: 创建主布局组件**

创建 `src/components/layout/AppLayout.vue`:

```vue
<template>
  <div class="app-layout flex min-h-screen bg-gray-50">
    <AppSidebar />
    <main class="main-content flex-1 flex flex-col">
      <AppHeader />
      <div class="content-area flex-1 p-6">
        <router-view />
      </div>
    </main>
    <AppStatsPanel />
  </div>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import AppStatsPanel from './AppStatsPanel.vue'
</script>

<style scoped>
.app-layout {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  overflow-y: auto;
}

.content-area {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
```

**Step 2: 创建侧边栏组件**

创建 `src/components/layout/AppSidebar.vue`:

```vue
<template>
  <aside class="sidebar w-[200px] bg-white border-r border-gray-200 flex flex-col">
    <!-- Logo -->
    <div class="p-4 border-b border-gray-200">
      <h1 class="text-xl font-bold text-gray-900">知识管理系统</h1>
      <p class="text-xs text-gray-500 mt-1">Knowledge System</p>
    </div>

    <!-- 导航菜单 -->
    <nav class="flex-1 p-4 overflow-y-auto">
      <ul class="space-y-1">
        <li v-for="item in menuItems" :key="item.name">
          <router-link
            :to="item.path"
            class="flex items-center px-3 py-2 rounded-lg transition-colors"
            :class="isActive(item.path) ? 'bg-blue-50 text-primary' : 'text-gray-700 hover:bg-gray-100'"
          >
            <component :is="item.icon" class="w-5 h-5 mr-3" />
            <span>{{ item.label }}</span>
          </router-link>

          <!-- 子菜单 -->
          <ul v-if="item.children && isActive(item.path)" class="ml-8 mt-1 space-y-1">
            <li v-for="child in item.children" :key="child.name">
              <router-link
                :to="child.path"
                class="flex items-center px-3 py-2 rounded-lg text-sm transition-colors"
                :class="isActive(child.path) ? 'bg-blue-50 text-primary' : 'text-gray-600 hover:bg-gray-100'"
              >
                <span>{{ child.label }}</span>
              </router-link>
            </li>
          </ul>
        </li>
      </ul>
    </nav>

    <!-- 用户信息 -->
    <div class="p-4 border-t border-gray-200">
      <div class="flex items-center">
        <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-medium">
          {{ userInitial }}
        </div>
        <div class="ml-3 flex-1">
          <p class="text-sm font-medium text-gray-900">{{ authStore.user?.username }}</p>
          <p class="text-xs text-gray-500">{{ roleLabel }}</p>
        </div>
        <el-button text @click="handleLogout" :icon="SwitchButton" />
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store'
import {
  DataBoard,
  Document,
  Files,
  Link,
  PriceTag,
  Search,
  DataAnalysis,
  User,
  Setting,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const menuItems = [
  { name: 'Dashboard', path: '/dashboard', label: '仪表盘', icon: DataBoard },
  {
    name: 'Articles',
    path: '/articles',
    label: '文章管理',
    icon: Document,
    children: [
      { name: 'ArticleList', path: '/articles', label: '文章列表' },
      { name: 'ArticleCreate', path: '/articles/create', label: '创建文章' },
    ],
  },
  { name: 'Tags', path: '/tags', label: '标签管理', icon: PriceTag },
  { name: 'Search', path: '/search', label: '搜索', icon: Search },
  { name: 'ReadingStats', path: '/reading/stats', label: '阅读统计', icon: DataAnalysis },
  { name: 'Profile', path: '/profile', label: '个人资料', icon: User },
  { name: 'Settings', path: '/settings', label: '设置', icon: Setting },
]

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'U'
})

const roleLabel = computed(() => {
  return authStore.user?.role === 'admin' ? '管理员' : '用户'
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

**Step 3: 创建顶部栏组件**

创建 `src/components/layout/AppHeader.vue`:

```vue
<template>
  <header class="app-header h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <!-- 面包屑导航 -->
    <div class="flex items-center">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRoute.meta?.title">
          {{ currentRoute.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 右侧操作 -->
    <div class="flex items-center space-x-4">
      <!-- 搜索按钮 -->
      <el-button :icon="Search" circle @click="$router.push('/search')" />

      <!-- 通知 -->
      <el-badge :value="3" class="badge">
        <el-button :icon="Bell" circle />
      </el-badge>

      <!-- 用户菜单 -->
      <el-dropdown @command="handleCommand">
        <div class="flex items-center cursor-pointer">
          <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white font-medium">
            {{ userInitial }}
          </div>
          <span class="ml-2 text-sm text-gray-700">{{ authStore.user?.username }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
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
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Bell, User, Setting, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store'

const router = useRouter()
const currentRoute = useRoute()
const authStore = useAuthStore()

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'U'
})

function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.badge :deep(.el-badge__content) {
  transform: translateY(-50%) translateX(100%);
}
</style>
```

**Step 4: 创建统计面板组件**

创建 `src/components/layout/AppStatsPanel.vue`:

```vue
<template>
  <aside class="stats-panel w-[300px] bg-white border-l border-gray-200 p-4 overflow-y-auto">
    <!-- 阅读统计 -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-gray-900 mb-3">阅读统计</h3>
      <div class="card bg-gray-50 rounded-lg p-4">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-600">总阅读数</span>
          <span class="text-xl font-bold text-primary">1,234</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">本月阅读</span>
          <span class="text-lg font-semibold text-success">156</span>
        </div>
      </div>
    </section>

    <!-- 热门标签 -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-gray-900 mb-3">热门标签</h3>
      <div class="space-y-2">
        <div
          v-for="tag in popularTags"
          :key="tag.id"
          class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
          @click="$router.push(`/articles?tag_id=${tag.id}`)"
        >
          <div class="flex items-center">
            <span class="w-2 h-2 rounded-full mr-2" :style="{ backgroundColor: tag.color }"></span>
            <span class="text-sm text-gray-700">{{ tag.name }}</span>
          </div>
          <span class="text-xs text-gray-500">({{ tag.count }})</span>
        </div>
      </div>
    </section>

    <!-- 最近阅读 -->
    <section>
      <h3 class="text-sm font-semibold text-gray-900 mb-3">最近阅读</h3>
      <div class="space-y-2">
        <div
          v-for="article in recentArticles"
          :key="article.id"
          class="p-3 rounded-lg border border-gray-200 hover:border-primary cursor-pointer transition-colors"
          @click="$router.push(`/articles/${article.id}`)"
        >
          <p class="text-sm font-medium text-gray-900 line-clamp-2">{{ article.title }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ formatTime(article.readAt) }}</p>
        </div>
      </div>
    </section>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 模拟数据
const popularTags = ref([
  { id: 1, name: '编程', color: '#3B82F6', count: 45 },
  { id: 2, name: '前端', color: '#10B981', count: 32 },
  { id: 3, name: 'Vue', color: '#8B5CF6', count: 28 },
  { id: 4, name: 'TypeScript', color: '#F59E0B', count: 21 },
  { id: 5, name: '设计', color: '#EF4444', count: 18 },
])

const recentArticles = ref([
  { id: 1, title: 'Vue 3 Composition API 最佳实践', readAt: new Date(Date.now() - 3600000) },
  { id: 2, title: 'TypeScript 高级类型技巧', readAt: new Date(Date.now() - 7200000) },
  { id: 3, title: 'Tailwind CSS 设计系统', readAt: new Date(Date.now() - 86400000) },
])

function formatTime(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
```

**Step 5: 提交**

```bash
git add frontend/src/components/layout/
git commit -m "feat: 添加布局组件系统

- AppLayout: 主布局容器（三栏布局）
- AppSidebar: 左侧导航菜单（含用户信息、登出）
- AppHeader: 顶部栏（面包屑、用户菜单）
- AppStatsPanel: 右侧统计面板（阅读统计、热门标签、最近阅读）

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 10: 创建占位页面

**Files:**
- Create: `frontend/src/views/dashboard/DashboardView.vue`
- Create: `frontend/src/views/article/ArticleListView.vue`
- Create: `frontend/src/views/article/ArticleDetailView.vue`
- Create: `frontend/src/views/article/ArticleCreateView.vue`
- Create: `frontend/src/views/tag/TagManageView.vue`

**Step 1: 创建仪表盘占位页面**

创建 `src/views/dashboard/DashboardView.vue`:

```vue
<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">仪表盘</h1>
    <div class="card">
      <p class="text-gray-600">欢迎使用知识管理系统！仪表盘功能正在开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 仪表盘占位页面
</script>
```

**Step 2: 创建文章列表占位页面**

创建 `src/views/article/ArticleListView.vue`:

```vue
<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">文章列表</h1>
    <div class="card">
      <p class="text-gray-600">文章列表功能正在开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 文章列表占位页面
</script>
```

**Step 3: 创建文章详情占位页面**

创建 `src/views/article/ArticleDetailView.vue`:

```vue
<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">文章详情</h1>
    <div class="card">
      <p class="text-gray-600">文章详情功能正在开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 文章详情占位页面
</script>
```

**Step 4: 创建文章创建占位页面**

创建 `src/views/article/ArticleCreateView.vue`:

```vue
<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">创建文章</h1>
    <div class="card">
      <p class="text-gray-600">文章创建功能正在开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 文章创建占位页面
</script>
```

**Step 5: 创建标签管理占位页面**

创建 `src/views/tag/TagManageView.vue`:

```vue
<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">标签管理</h1>
    <div class="card">
      <p class="text-gray-600">标签管理功能正在开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 标签管理占位页面
</script>
```

**Step 6: 提交**

```bash
git add frontend/src/views/
git commit -m "feat: 添加占位页面

- 仪表盘占位页面
- 文章列表占位页面
- 文章详情占位页面
- 文章创建占位页面
- 标签管理占位页面

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 11: 更新 main.ts 初始化状态

**Files:**
- Modify: `frontend/src/main.ts`

**Step 1: 更新 main.ts**

修改 `src/main.ts`:

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './styles/main.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './store'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 恢复认证状态
const authStore = useAuthStore()
authStore.restoreState()

app.mount('#app')
```

**Step 2: 提交**

```bash
git add frontend/src/main.ts
git commit -m "feat: 更新应用初始化逻辑

- 注册 Element Plus 图标
- 恢复认证状态

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 12: 测试和验证

**Step 1: 启动开发服务器**

```bash
cd frontend
npm run dev
```

**Step 2: 验证功能清单**

- [ ] 访问 http://localhost:3000 自动跳转到登录页
- [ ] 登录页面显示正常
- [ ] 注册页面显示正常
- [ ] 注册新用户成功
- [ ] 登录成功后跳转到仪表盘
- [ ] 三栏布局显示正常（左侧导航、中间内容、右侧统计）
- [ ] 左侧导航菜单可点击
- [ ] 右侧统计面板显示
- [ ] 顶部用户菜单可操作
- [ ] 登出功能正常
- [ ] Token过期后自动跳转登录

**Step 3: 浏览器控制台检查**

- 检查是否有 TypeScript 错误
- 检查是否有网络请求错误
- 检查是否有样式加载问题

**Step 4: 提交最终版本**

```bash
git add frontend/
git commit -m "feat: 完成第一阶段认证和布局框架

- 项目初始化完成
- 类型定义系统
- API 请求封装
- Pinia 状态管理
- 路由配置和守卫
- 登录/注册功能
- 三栏布局组件
- 占位页面

第一阶段完成，可以进行第二阶段开发

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 验收标准

### 功能验收

- [x] 用户可以注册新账户
- [x] 用户可以登录系统
- [x] 登录后 Token 正确保存
- [x] 三栏布局正确显示
- [x] 导航菜单可以切换页面
- [x] 用户可以登出
- [x] 未登录访问受保护路由自动跳转登录
- [x] Token 过期后自动跳转登录

### 技术验收

- [x] TypeScript 无编译错误
- [x] ESLint 无错误
- [x] 所有组件正常渲染
- [x] API 请求正常工作
- [x] 状态管理正常工作
- [x] 路由守卫正常工作

### 性能验收

- [x] 首屏加载时间 < 2秒
- [x] 路由切换流畅
- [x] 无明显卡顿

---

## 下一步

第一阶段完成后，进入第二阶段：**文章列表 + 文章详情**

相关实施计划将在第一阶段完成后创建。

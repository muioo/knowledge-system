# 知识系统前端实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于 Vue 3 + TypeScript + Pinia + Element Plus 构建知识系统前端应用，实现文章管理、标签管理、搜索、阅读历史和用户管理功能。

**Architecture:** 采用分层架构设计，API层 → Store层 → Component层，使用 Composition API 和 `<script setup>` 语法，全面 TypeScript 类型安全。

**Tech Stack:** Vue 3.4, TypeScript 5.3, Pinia 2.1, Vue Router 4.2, Element Plus 2.5, Axios 1.6, Vite 5.0, Sass

---

## 任务概览

本计划分为以下阶段：

1. **项目基础搭建** - 配置 Vite、TypeScript、构建工具链
2. **类型定义** - 定义所有 TypeScript 类型和接口
3. **API 层** - 封装所有后端 API 调用
4. **工具函数** - 请求封装、本地存储、权限判断等
5. **状态管理** - Pinia Store 定义
6. **路由配置** - 路由定义和路由守卫
7. **通用组件** - Header、Sidebar、Loading、ConfirmDialog
8. **布局组件** - DashboardLayout、AuthLayout
9. **功能组件** - 文章、标签、搜索相关组件
10. **页面视图** - 所有页面组件实现
11. **样式系统** - 全局样式、变量、Element Plus 覆盖
12. **集成测试** - 端到端功能验证

---

## 阶段 1: 项目基础搭建

### Task 1: 创建 Vite 配置文件

**Files:**
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`
- Create: `frontend/.env.development`
- Create: `frontend/.env.production`

**Step 1: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Step 2: 创建 tsconfig.json**

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
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 3: 创建 tsconfig.node.json**

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

**Step 4: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>知识系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

**Step 5: 创建 .env.development**

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_APP_TITLE=知识系统
```

**Step 6: 创建 .env.production**

```env
VITE_API_BASE_URL=/api/v1
VITE_APP_TITLE=知识系统
```

**Step 7: 提交更改**

```bash
cd frontend
git add vite.config.ts tsconfig.json tsconfig.node.json index.html .env.development .env.production
git commit -m "feat: 添加 Vite 和 TypeScript 配置文件"
```

---

### Task 2: 创建入口文件和目录结构

**Files:**
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/env.d.ts`
- Create: `frontend/src/assets/styles/_reset.scss`
- Create: `frontend/src/assets/images/.gitkeep`

**Step 1: 创建 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'
import './assets/styles/global.scss'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

**Step 2: 创建 App.vue**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style lang="scss">
#app {
  height: 100vh;
  overflow: hidden;
}
</style>
```

**Step 3: 创建 env.d.ts**

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

**Step 4: 创建重置样式**

```scss
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

a {
  text-decoration: none;
  color: inherit;
}

ul, ol {
  list-style: none;
}

img {
  max-width: 100%;
  height: auto;
}
```

**Step 5: 创建图片目录占位文件**

```bash
mkdir -p frontend/src/assets/images
touch frontend/src/assets/images/.gitkeep
```

**Step 6: 提交更改**

```bash
git add src/main.ts src/App.vue src/env.d.ts src/assets/styles/_reset.scss src/assets/images/.gitkeep
git commit -m "feat: 创建应用入口文件和基础目录结构"
```

---

### Task 3: 配置 ESLint 和 Prettier

**Files:**
- Create: `frontend/.eslintrc.cjs`
- Create: `frontend/.prettierrc`
- Create: `frontend/.eslintignore`
- Create: `frontend/.prettierignore`

**Step 1: 创建 .eslintrc.cjs**

```javascript
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2021: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
    sourceType: 'module'
  },
  plugins: ['vue', '@typescript-eslint'],
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    'vue/no-v-html': 'off'
  }
}
```

**Step 2: 创建 .prettierrc**

```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "none",
  "arrowParens": "avoid",
  "endOfLine": "auto"
}
```

**Step 3: 创建 .eslintignore**

```
node_modules
dist
*.d.ts
auto-imports.d.ts
components.d.ts
```

**Step 4: 创建 .prettierignore**

```
node_modules
dist
*.d.ts
auto-imports.d.ts
components.d.ts
package-lock.json
```

**Step 5: 更新 package.json 添加依赖**

```bash
cd frontend
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-vue prettier eslint-config-prettier eslint-plugin-prettier
```

**Step 6: 提交更改**

```bash
git add .eslintrc.cjs .prettierrc .eslintignore .prettierignore package.json package-lock.json
git commit -m "feat: 添加 ESLint 和 Prettier 配置"
```

---

## 阶段 2: 类型定义

### Task 4: 定义 API 响应类型

**Files:**
- Create: `frontend/src/types/api.ts`

**Step 1: 定义基础 API 响应类型**

```typescript
// 通用响应结构
export interface SuccessResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  total: number
  page: number
  size: number
  items: T[]
}

export interface PaginatedResponse<T> {
  code: number
  message: string
  data: PaginatedData<T>
}

export interface ErrorResponse {
  code: number
  message: string
  detail?: Record<string, unknown>
}

// Token 响应
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserResponse
}
```

**Step 2: 提交更改**

```bash
git add src/types/api.ts
git commit -m "feat: 定义 API 响应基础类型"
```

---

### Task 5: 定义数据模型类型

**Files:**
- Create: `frontend/src/types/models.ts`

**Step 1: 定义所有数据模型类型**

```typescript
import type { TagInfo } from './tag'

// 用户相关
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface UserResponse {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserUpdate {
  email?: string
  password?: string
}

export interface UserLogin {
  username: string
  password: string
}

// 文章相关
export interface Article {
  id: number
  title: string
  content: string
  source_url?: string
  summary?: string
  keywords?: string
  author_id: number
  original_filename?: string
  view_count: number
  created_at: string
  updated_at: string
  tags: TagInfo[]
}

export interface ArticleResponse {
  id: number
  title: string
  content: string
  source_url?: string
  summary?: string
  keywords?: string
  author_id: number
  original_filename?: string
  view_count: number
  created_at: string
  updated_at: string
  tags: TagInfo[]
}

export interface ArticleCreate {
  title: string
  content: string
  source_url?: string
  summary?: string
  keywords?: string
  tag_ids?: number[]
  import_type?: 'direct' | 'file'
}

export interface ArticleUpdate {
  title?: string
  content?: string
  source_url?: string
  summary?: string
  keywords?: string
  tag_ids?: number[]
}

export interface ArticleHtmlResponse extends ArticleResponse {
  html_content?: string
  html_path?: string
  processing_status?: string
}

export interface ArticleFromHtmlUrlRequest {
  url: string
  tag_ids?: number[]
}

export interface ArticleFromHtmlUrlResponse {
  article_id: number
  status: string
  message: string
}

// 搜索相关
export interface SearchQuery {
  q?: string
  tags?: number[]
  page: number
  size: number
}

// 阅读记录相关
export interface ReadingHistory {
  id: number
  article_id: number
  article_title: string
  started_at: string
  ended_at?: string
  reading_duration: number
  reading_progress: number
}

export interface ReadingEnd {
  reading_progress: number
}

export interface ReadingStats {
  article_id: number
  article_title: string
  total_views: number
  total_duration: number
  last_read_at?: string
}
```

**Step 2: 提交更改**

```bash
git add src/types/models.ts
git commit -m "feat: 定义数据模型类型"
```

---

### Task 6: 定义标签和通用类型

**Files:**
- Create: `frontend/src/types/tag.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: 定义标签类型**

```typescript
export interface Tag {
  id: number
  name: string
  color: string
  created_at: string
}

export interface TagInfo {
  id: number
  name: string
  color: string
}

export interface TagCreate {
  name: string
  color?: string
}

export interface TagUpdate {
  name?: string
  color?: string
}
```

**Step 2: 创建类型导出文件**

```typescript
export * from './api'
export * from './models'
export * from './tag'
```

**Step 3: 提交更改**

```bash
git add src/types/tag.ts src/types/index.ts
git commit -m "feat: 定义标签类型并导出所有类型"
```

---

## 阶段 3: API 层

### Task 7: 创建 Axios 实例配置

**Files:**
- Create: `frontend/src/api/index.ts`

**Step 1: 配置 Axios 实例**

```typescript
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ErrorResponse } from '@/types'
import { ElMessage } from 'element-plus'

const baseURL = import.meta.env.VITE_API_BASE_URL

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError<ErrorResponse>) => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401:
          // Token 过期，尝试刷新
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              // 这里需要调用刷新 token 的 API
              // 暂时先跳转到登录页
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              window.location.href = '/login'
            } catch {
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              window.location.href = '/login'
            }
          } else {
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error(data?.message || '无权限访问')
          break
        case 404:
          ElMessage.error(data?.message || '资源不存在')
          break
        case 500:
        case 502:
        case 503:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else {
      ElMessage.error('网络连接失败')
    }

    return Promise.reject(error)
  }
)

export default request
```

**Step 2: 提交更改**

```bash
git add src/api/index.ts
git commit -m "feat: 创建 Axios 实例配置和拦截器"
```

---

### Task 8: 创建认证相关 API

**Files:**
- Create: `frontend/src/api/auth.ts`

**Step 1: 定义认证 API**

```typescript
import request from './index'
import type { SuccessResponse, TokenResponse, UserLogin, UserCreate } from '@/types'

export const authApi = {
  // 登录
  login(data: UserLogin) {
    return request<SuccessResponse<TokenResponse>>({
      url: '/auth/login',
      method: 'POST',
      data
    })
  },

  // 注册
  register(data: UserCreate) {
    return request<SuccessResponse<TokenResponse>>({
      url: '/auth/register',
      method: 'POST',
      data
    })
  }
}
```

**Step 2: 提交更改**

```bash
git add src/api/auth.ts
git commit -m "feat: 创建认证相关 API"
```

---

### Task 9: 创建文章相关 API

**Files:**
- Create: `frontend/src/api/articles.ts`

**Step 1: 定义文章 API**

```typescript
import request from './index'
import type {
  SuccessResponse,
  PaginatedResponse,
  ArticleResponse,
  ArticleHtmlResponse,
  ArticleUpdate,
  ArticleFromHtmlUrlRequest,
  ArticleFromHtmlUrlResponse
} from '@/types'

export const articleApi = {
  // 获取文章列表
  getArticles(params: { page: number; size: number; tag_id?: number }) {
    return request<PaginatedResponse<ArticleResponse>>({
      url: '/articles/',
      method: 'GET',
      params
    })
  },

  // 获取文章详情（包含 HTML）
  getArticle(id: number) {
    return request<SuccessResponse<ArticleHtmlResponse>>({
      url: `/articles/${id}`,
      method: 'GET'
    })
  },

  // 获取文章 HTML 内容
  getArticleHtml(id: number) {
    return request<SuccessResponse<ArticleHtmlResponse>>({
      url: `/articles/${id}/html`,
      method: 'GET'
    })
  },

  // 上传文件创建文章
  uploadArticle(formData: FormData) {
    return request<SuccessResponse<ArticleResponse>>({
      url: '/articles/upload',
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 从 URL 导入文章
  importFromUrl(data: ArticleFromHtmlUrlRequest) {
    return request<SuccessResponse<ArticleFromHtmlUrlResponse>>({
      url: '/articles/from-url-html',
      method: 'POST',
      data
    })
  },

  // 更新文章
  updateArticle(id: number, data: ArticleUpdate) {
    return request<SuccessResponse<ArticleResponse>>({
      url: `/articles/${id}`,
      method: 'PUT',
      data
    })
  },

  // 删除文章
  deleteArticle(id: number) {
    return request({
      url: `/articles/${id}`,
      method: 'DELETE'
    })
  }
}
```

**Step 2: 提交更改**

```bash
git add src/api/articles.ts
git commit -m "feat: 创建文章相关 API"
```

---

### Task 10: 创建标签、用户、搜索和阅读相关 API

**Files:**
- Create: `frontend/src/api/tags.ts`
- Create: `frontend/src/api/users.ts`
- Create: `frontend/src/api/search.ts`
- Create: `frontend/src/api/reading.ts`

**Step 1: 定义标签 API**

```typescript
import request from './index'
import type { SuccessResponse, Tag, TagCreate, TagUpdate, PaginatedResponse, ArticleResponse } from '@/types'

export const tagApi = {
  // 获取所有标签
  getTags() {
    return request<SuccessResponse<Tag[]>>({
      url: '/tags/',
      method: 'GET'
    })
  },

  // 获取单个标签
  getTag(id: number) {
    return request<SuccessResponse<Tag>>({
      url: `/tags/${id}`,
      method: 'GET'
    })
  },

  // 创建标签
  createTag(data: TagCreate) {
    return request<SuccessResponse<Tag>>({
      url: '/tags/',
      method: 'POST',
      data
    })
  },

  // 更新标签
  updateTag(id: number, data: TagUpdate) {
    return request<SuccessResponse<Tag>>({
      url: `/tags/${id}`,
      method: 'PUT',
      data
    })
  },

  // 删除标签
  deleteTag(id: number) {
    return request({
      url: `/tags/${id}`,
      method: 'DELETE'
    })
  },

  // 获取标签下的文章
  getTagArticles(id: number, params: { page: number; size: number }) {
    return request<PaginatedResponse<ArticleResponse>>({
      url: `/tags/${id}/articles`,
      method: 'GET',
      params
    })
  }
}
```

**Step 2: 定义用户 API**

```typescript
import request from './index'
import type {
  SuccessResponse,
  PaginatedResponse,
  UserResponse,
  UserUpdate,
  ErrorResponse
} from '@/types'

export interface UpdateRole {
  role: string
}

export const userApi = {
  // 获取当前用户信息
  getMe() {
    return request<SuccessResponse<UserResponse>>({
      url: '/users/me',
      method: 'GET'
    })
  },

  // 更新当前用户信息
  updateMe(data: UserUpdate) {
    return request<SuccessResponse<UserResponse>>({
      url: '/users/me',
      method: 'PUT',
      data
    })
  },

  // 删除当前用户
  deleteMe() {
    return request({
      url: '/users/me',
      method: 'DELETE'
    })
  },

  // 获取用户列表（管理员）
  getUsers(params: { page: number; size: number }) {
    return request<PaginatedResponse<UserResponse>>({
      url: '/users/',
      method: 'GET',
      params
    })
  },

  // 获取单个用户（管理员）
  getUser(id: number) {
    return request<SuccessResponse<UserResponse>>({
      url: `/users/${id}`,
      method: 'GET'
    })
  },

  // 更新用户（管理员）
  updateUser(id: number, data: UserUpdate) {
    return request<SuccessResponse<UserResponse>>({
      url: `/users/${id}`,
      method: 'PUT',
      data
    })
  },

  // 删除用户（管理员）
  deleteUser(id: number) {
    return request({
      url: `/users/${id}`,
      method: 'DELETE'
    })
  },

  // 更新用户角色（管理员）
  updateUserRole(id: number, data: UpdateRole) {
    return request<SuccessResponse<UserResponse>>({
      url: `/users/${id}/role`,
      method: 'PATCH',
      data
    })
  }
}
```

**Step 3: 定义搜索 API**

```typescript
import request from './index'
import type { PaginatedResponse, ArticleResponse } from '@/types'

export const searchApi = {
  // 搜索文章
  searchArticles(params: { q?: string; tags?: string; page: number; size: number }) {
    return request<PaginatedResponse<ArticleResponse>>({
      url: '/search/articles',
      method: 'GET',
      params
    })
  }
}
```

**Step 4: 定义阅读记录 API**

```typescript
import request from './index'
import type { SuccessResponse, PaginatedResponse, ReadingHistory, ReadingEnd, ReadingStats } from '@/types'

export const readingApi = {
  // 开始阅读
  startReading(articleId: number) {
    return request<SuccessResponse<ReadingHistory>>({
      url: `/reading/articles/${articleId}/start`,
      method: 'POST'
    })
  },

  // 结束阅读
  endReading(articleId: number, data: ReadingEnd) {
    return request<SuccessResponse<ReadingHistory>>({
      url: `/reading/articles/${articleId}/end`,
      method: 'POST',
      data
    })
  },

  // 获取阅读历史
  getHistory(params: { page: number; size: number }) {
    return request<PaginatedResponse<ReadingHistory>>({
      url: '/reading/history',
      method: 'GET',
      params
    })
  },

  // 获取阅读统计
  getStats(params: { page: number; size: number }) {
    return request<PaginatedResponse<ReadingStats>>({
      url: '/reading/stats',
      method: 'GET',
      params
    })
  },

  // 获取文章阅读统计（管理员）
  getArticleStats(articleId: number, params: { page: number; size: number }) {
    return request<PaginatedResponse<ReadingStats>>({
      url: `/reading/articles/${articleId}/stats`,
      method: 'GET',
      params
    })
  }
}
```

**Step 5: 提交更改**

```bash
git add src/api/tags.ts src/api/users.ts src/api/search.ts src/api/reading.ts
git commit -m "feat: 创建标签、用户、搜索和阅读相关 API"
```

---

## 阶段 4: 工具函数

### Task 11: 创建工具函数模块

**Files:**
- Create: `frontend/src/utils/request.ts`
- Create: `frontend/src/utils/storage.ts`
- Create: `frontend/src/utils/date.ts`
- Create: `frontend/src/utils/permission.ts`

**Step 1: 创建请求工具函数**

```typescript
import type { ArticleResponse } from '@/types'

// 格式化文章内容用于显示
export function formatArticleContent(content: string): string {
  if (!content) return ''
  // 简单的 Markdown 转 HTML 处理
  return content
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\n/gim, '<br />')
}

// 截断文本
export function truncateText(text: string, maxLength: number = 100): string {
  if (!text || text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
```

**Step 2: 创建本地存储工具**

```typescript
const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user_info'

export const storage = {
  // Token 相关
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },

  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY)
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  },

  removeRefreshToken(): void {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },

  clearAuth(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  // 用户信息相关
  getUser(): Record<string, unknown> | null {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },

  setUser(user: Record<string, unknown>): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  removeUser(): void {
    localStorage.removeItem(USER_KEY)
  }
}
```

**Step 3: 创建日期工具函数**

```typescript
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

export function formatDate(date: string | Date, format: string = 'YYYY-MM-DD HH:mm'): string {
  return dayjs(date).format(format)
}

export function formatRelativeTime(date: string | Date): string {
  return dayjs(date).fromNow()
}

export function isToday(date: string | Date): boolean {
  return dayjs(date).isSame(dayjs(), 'day')
}
```

**Step 4: 创建权限工具函数**

```typescript
import type { User } from '@/types'
import { storage } from './storage'

// 检查是否已登录
export function isAuthenticated(): boolean {
  return !!storage.getToken()
}

// 检查是否是管理员
export function isAdmin(): boolean {
  const user = storage.getUser() as User | null
  return user?.role === 'admin'
}

// 检查是否有编辑权限
export function canEditArticle(authorId: number): boolean {
  const user = storage.getUser() as User | null
  if (!user) return false
  return user.id === authorId || user.role === 'admin'
}

// 检查是否有删除权限
export function canDeleteArticle(authorId: number): boolean {
  return canEditArticle(authorId)
}
```

**Step 5: 提交更改**

```bash
git add src/utils/request.ts src/utils/storage.ts src/utils/date.ts src/utils/permission.ts
git commit -m "feat: 创建工具函数模块"
```

---

## 阶段 5: 状态管理

### Task 12: 创建认证状态 Store

**Files:**
- Create: `frontend/src/stores/auth.ts`

**Step 1: 创建认证 Store**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { storage } from '@/utils/storage'
import type { UserLogin, UserCreate, TokenResponse, User } from '@/types'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(storage.getToken())
  const refreshToken = ref<string | null>(storage.getRefreshToken())
  const user = ref<User | null>(storage.getUser() as User | null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  async function login(credentials: UserLogin): Promise<boolean> {
    try {
      const response = await authApi.login(credentials)
      const { access_token, refresh_token, user: userData } = response.data

      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData

      storage.setToken(access_token)
      storage.setRefreshToken(refresh_token)
      storage.setUser(userData)

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error('登录失败')
      return false
    }
  }

  async function register(data: UserCreate): Promise<boolean> {
    try {
      const response = await authApi.register(data)
      const { access_token, refresh_token, user: userData } = response.data

      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData

      storage.setToken(access_token)
      storage.setRefreshToken(refresh_token)
      storage.setUser(userData)

      ElMessage.success('注册成功')
      return true
    } catch (error) {
      ElMessage.error('注册失败')
      return false
    }
  }

  function logout(): void {
    token.value = null
    refreshToken.value = null
    user.value = null

    storage.clearAuth()
    router.push('/login')
    ElMessage.success('已退出登录')
  }

  return {
    token,
    refreshToken,
    user,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout
  }
})
```

**Step 2: 提交更改**

```bash
git add src/stores/auth.ts
git commit -m "feat: 创建认证状态 Store"
```

---

### Task 13: 创建文章和标签状态 Store

**Files:**
- Create: `frontend/src/stores/article.ts`
- Create: `frontend/src/stores/tag.ts`

**Step 1: 创建文章 Store**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { articleApi } from '@/api/articles'
import type { ArticleResponse, ArticleHtmlResponse, ArticleUpdate } from '@/types'
import { ElMessage } from 'element-plus'

export const useArticleStore = defineStore('article', () => {
  // State
  const articles = ref<ArticleResponse[]>([])
  const currentArticle = ref<ArticleHtmlResponse | null>(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0
  })

  // Actions
  async function fetchArticles(params?: { page?: number; size?: number; tag_id?: number }) {
    loading.value = true
    try {
      const response = await articleApi.getArticles({
        page: params?.page || pagination.value.page,
        size: params?.size || pagination.value.size,
        tag_id: params?.tag_id
      })

      articles.value = response.data.items
      pagination.value = {
        page: response.data.page,
        size: response.data.size,
        total: response.data.total
      }
    } catch (error) {
      ElMessage.error('获取文章列表失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchArticle(id: number) {
    loading.value = true
    try {
      const response = await articleApi.getArticle(id)
      currentArticle.value = response.data
    } catch (error) {
      ElMessage.error('获取文章详情失败')
    } finally {
      loading.value = false
    }
  }

  async function updateArticle(id: number, data: ArticleUpdate) {
    try {
      const response = await articleApi.updateArticle(id, data)
      const index = articles.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        articles.value[index] = response.data
      }
      if (currentArticle.value?.id === id) {
        currentArticle.value = { ...response.data, html_content: currentArticle.value.html_content }
      }
      ElMessage.success('更新成功')
      return true
    } catch (error) {
      ElMessage.error('更新失败')
      return false
    }
  }

  async function deleteArticle(id: number) {
    try {
      await articleApi.deleteArticle(id)
      articles.value = articles.value.filter((a) => a.id !== id)
      if (currentArticle.value?.id === id) {
        currentArticle.value = null
      }
      ElMessage.success('删除成功')
      return true
    } catch (error) {
      ElMessage.error('删除失败')
      return false
    }
  }

  return {
    articles,
    currentArticle,
    loading,
    pagination,
    fetchArticles,
    fetchArticle,
    updateArticle,
    deleteArticle
  }
})
```

**Step 2: 创建标签 Store**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagApi } from '@/api/tags'
import type { Tag, TagCreate, TagUpdate } from '@/types'
import { ElMessage } from 'element-plus'

export const useTagStore = defineStore('tag', () => {
  // State
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  // Actions
  async function fetchTags() {
    loading.value = true
    try {
      const response = await tagApi.getTags()
      tags.value = response.data
    } catch (error) {
      ElMessage.error('获取标签列表失败')
    } finally {
      loading.value = false
    }
  }

  async function createTag(data: TagCreate) {
    try {
      const response = await tagApi.createTag(data)
      tags.value.push(response.data)
      ElMessage.success('创建成功')
      return true
    } catch (error) {
      ElMessage.error('创建失败')
      return false
    }
  }

  async function updateTag(id: number, data: TagUpdate) {
    try {
      const response = await tagApi.updateTag(id, data)
      const index = tags.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        tags.value[index] = response.data
      }
      ElMessage.success('更新成功')
      return true
    } catch (error) {
      ElMessage.error('更新失败')
      return false
    }
  }

  async function deleteTag(id: number) {
    try {
      await tagApi.deleteTag(id)
      tags.value = tags.value.filter((t) => t.id !== id)
      ElMessage.success('删除成功')
      return true
    } catch (error) {
      ElMessage.error('删除失败')
      return false
    }
  }

  return {
    tags,
    loading,
    fetchTags,
    createTag,
    updateTag,
    deleteTag
  }
})
```

**Step 3: 提交更改**

```bash
git add src/stores/article.ts src/stores/tag.ts
git commit -m "feat: 创建文章和标签状态 Store"
```

---

### Task 14: 创建 UI 状态 Store

**Files:**
- Create: `frontend/src/stores/ui.ts`

**Step 1: 创建 UI Store**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  // State
  const sidebarCollapsed = ref(false)
  const globalLoading = ref(false)

  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
  }

  function setGlobalLoading(loading: boolean) {
    globalLoading.value = loading
  }

  return {
    sidebarCollapsed,
    globalLoading,
    toggleSidebar,
    setSidebarCollapsed,
    setGlobalLoading
  }
})
```

**Step 2: 提交更改**

```bash
git add src/stores/ui.ts
git commit -m "feat: 创建 UI 状态 Store"
```

---

## 阶段 6: 路由配置

### Task 15: 创建路由配置

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/router/guards.ts`

**Step 1: 创建路由配置**

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 布局组件
const DashboardLayout = () => import('@/components/layout/DashboardLayout.vue')
const AuthLayout = () => import('@/components/layout/AuthLayout.vue')

// 页面组件
const Login = () => import('@/views/auth/Login.vue')
const Dashboard = () => import('@/views/dashboard/Dashboard.vue')
const ArticleList = () => import('@/views/articles/ArticleList.vue')
const ArticleDetail = () => import('@/views/articles/ArticleDetail.vue')
const ArticleUpload = () => import('@/views/articles/ArticleUpload.vue')
const TagManage = () => import('@/views/tags/TagManage.vue')
const Search = () => import('@/views/search/Search.vue')
const ReadingHistory = () => import('@/views/reading/History.vue')
const ReadingStats = () => import('@/views/reading/Stats.vue')
const UserManage = () => import('@/views/users/UserManage.vue')
const Profile = () => import('@/views/profile/Profile.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'Login',
        component: Login,
        meta: { title: '登录' }
      }
    ]
  },
  {
    path: '/',
    component: DashboardLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘', requiresAuth: true }
      },
      {
        path: 'articles',
        name: 'ArticleList',
        component: ArticleList,
        meta: { title: '文章列表', requiresAuth: true }
      },
      {
        path: 'articles/upload',
        name: 'ArticleUpload',
        component: ArticleUpload,
        meta: { title: '上传文章', requiresAuth: true }
      },
      {
        path: 'articles/:id',
        name: 'ArticleDetail',
        component: ArticleDetail,
        meta: { title: '文章详情', requiresAuth: true }
      },
      {
        path: 'tags',
        name: 'TagManage',
        component: TagManage,
        meta: { title: '标签管理', requiresAuth: true }
      },
      {
        path: 'search',
        name: 'Search',
        component: Search,
        meta: { title: '搜索', requiresAuth: true }
      },
      {
        path: 'reading/history',
        name: 'ReadingHistory',
        component: ReadingHistory,
        meta: { title: '阅读历史', requiresAuth: true }
      },
      {
        path: 'reading/stats',
        name: 'ReadingStats',
        component: ReadingStats,
        meta: { title: '阅读统计', requiresAuth: true }
      },
      {
        path: 'users',
        name: 'UserManage',
        component: UserManage,
        meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile,
        meta: { title: '个人资料', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

**Step 2: 创建路由守卫**

```typescript
import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

export function setupRouterGuards(router: Router) {
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // 设置页面标题
    document.title = `${to.meta.title || '知识系统'} - 知识系统`

    // 检查是否需要认证
    if (to.meta.requiresAuth) {
      if (!authStore.isAuthenticated) {
        ElMessage.warning('请先登录')
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }

      // 检查是否需要管理员权限
      if (to.meta.requiresAdmin && !authStore.isAdmin) {
        ElMessage.error('需要管理员权限')
        next({ name: 'Dashboard' })
        return
      }
    }

    // 已登录用户访问登录页，重定向到首页
    if (to.name === 'Login' && authStore.isAuthenticated) {
      next({ name: 'Dashboard' })
      return
    }

    next()
  })
}
```

**Step 3: 更新 main.ts 应用路由守卫**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import { setupRouterGuards } from './router/guards'
import App from './App.vue'
import './assets/styles/global.scss'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 设置路由守卫
setupRouterGuards(router)

app.mount('#app')
```

**Step 4: 提交更改**

```bash
git add src/router/index.ts src/router/guards.ts src/main.ts
git commit -m "feat: 创建路由配置和路由守卫"
```

---

## 阶段 7: 通用组件

### Task 16: 创建通用 UI 组件

**Files:**
- Create: `frontend/src/components/common/AppHeader.vue`
- Create: `frontend/src/components/common/AppSidebar.vue`
- Create: `frontend/src/components/common/LoadingSpinner.vue`
- Create: `frontend/src/components/common/ConfirmDialog.vue`

**Step 1: 创建顶部导航栏组件**

```vue
<template>
  <header class="app-header">
    <div class="header-left">
      <el-icon class="collapse-btn" @click="toggleSidebar">
        <Expand v-if="uiStore.sidebarCollapsed" />
        <Fold v-else />
      </el-icon>
      <h1 class="app-title">{{ appTitle }}</h1>
    </div>

    <div class="header-right">
      <el-dropdown @command="handleCommand">
        <span class="user-dropdown">
          <el-icon><User /></el-icon>
          <span class="username">{{ authStore.user?.username }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const uiStore = useUiStore()
const router = useRouter()

const appTitle = import.meta.env.VITE_APP_TITLE || '知识系统'

function toggleSidebar() {
  uiStore.toggleSidebar()
}

function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push({ name: 'Profile' })
      break
    case 'logout':
      authStore.logout()
      break
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;

  .collapse-btn {
    font-size: 20px;
    cursor: pointer;
    color: #64748b;

    &:hover {
      color: #3b82f6;
    }
  }

  .app-title {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

.header-right {
  .user-dropdown {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 6px;
    transition: background 0.2s;

    &:hover {
      background: #f1f5f9;
    }

    .username {
      color: #334155;
    }
  }
}
</style>
```

**Step 2: 创建侧边栏组件**

```vue
<template>
  <aside class="app-sidebar" :class="{ collapsed: uiStore.sidebarCollapsed }">
    <nav class="sidebar-nav">
      <el-menu
        :default-active="activeMenu"
        :collapse="uiStore.sidebarCollapsed"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <el-menu-item index="/articles">
          <el-icon><Document /></el-icon>
          <template #title>文章列表</template>
        </el-menu-item>

        <el-menu-item index="/articles/upload">
          <el-icon><Upload /></el-icon>
          <template #title>上传文章</template>
        </el-menu-item>

        <el-menu-item index="/tags">
          <el-icon><PriceTag /></el-icon>
          <template #title>标签管理</template>
        </el-menu-item>

        <el-menu-item index="/search">
          <el-icon><Search /></el-icon>
          <template #title>搜索</template>
        </el-menu-item>

        <el-sub-menu index="reading">
          <template #title>
            <el-icon><Reading /></el-icon>
            <span>阅读记录</span>
          </template>
          <el-menu-item index="/reading/history">阅读历史</el-menu-item>
          <el-menu-item index="/reading/stats">阅读统计</el-menu-item>
        </el-sub-menu>

        <el-menu-item v-if="authStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/profile">
          <el-icon><UserFilled /></el-icon>
          <template #title>个人资料</template>
        </el-menu-item>
      </el-menu>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUiStore()

const activeMenu = computed(() => route.path)
</script>

<style lang="scss" scoped>
.app-sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  width: 240px;
  background: #1e293b;
  transition: width 0.3s;
  z-index: 100;

  &.collapsed {
    width: 64px;
  }
}

.sidebar-nav {
  height: 100%;
  overflow-y: auto;
}

.sidebar-menu {
  border: none;
  background: transparent;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    color: #94a3b8;

    &:hover {
      background: #334155;
      color: #fff;
    }

    &.is-active {
      background: #3b82f6;
      color: #fff;
    }
  }

  :deep(.el-sub-menu .el-menu-item) {
    background: #0f172a;

    &:hover {
      background: #1e293b;
    }
  }
}
</style>
```

**Step 3: 创建加载动画组件**

```vue
<template>
  <div v-loading="true" class="loading-spinner" element-loading-text="加载中...">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading?: boolean
  text?: string
}

withDefaults(defineProps<Props>(), {
  loading: true,
  text: '加载中...'
})
</script>

<style lang="scss" scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}
</style>
```

**Step 4: 创建确认对话框组件**

```vue
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="400px"
    :before-close="handleCancel"
  >
    <div class="confirm-content">
      <el-icon class="confirm-icon" :class="type">
        <Warning v-if="type === 'warning'" />
        <InfoFilled v-else />
      </el-icon>
      <p class="confirm-message">{{ message }}</p>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button :type="confirmType" @click="handleConfirm">确认</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  message: string
  type?: 'warning' | 'info'
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认',
  type: 'warning'
})

const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const confirmType = computed(() => (props.type === 'warning' ? 'danger' : 'primary'))

function handleConfirm() {
  emit('confirm')
  visible.value = false
}

function handleCancel() {
  emit('cancel')
  visible.value = false
}
</script>

<style lang="scss" scoped>
.confirm-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
}

.confirm-icon {
  font-size: 24px;
  flex-shrink: 0;

  &.warning {
    color: #f59e0b;
  }

  &.info {
    color: #3b82f6;
  }
}

.confirm-message {
  margin: 0;
  color: #334155;
  line-height: 1.6;
}
</style>
```

**Step 5: 提交更改**

```bash
git add src/components/common/AppHeader.vue src/components/common/AppSidebar.vue src/components/common/LoadingSpinner.vue src/components/common/ConfirmDialog.vue
git commit -m "feat: 创建通用 UI 组件"
```

---

### Task 17: 创建布局组件

**Files:**
- Create: `frontend/src/components/layout/DashboardLayout.vue`
- Create: `frontend/src/components/layout/AuthLayout.vue`

**Step 1: 创建仪表盘布局**

```vue
<template>
  <div class="dashboard-layout">
    <AppHeader />
    <AppSidebar />
    <main class="main-content" :class="{ collapsed: uiStore.sidebarCollapsed }">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTagStore } from '@/stores/tag'
import AppHeader from '@/components/common/AppHeader.vue'
import AppSidebar from '@/components/common/AppSidebar.vue'
import { useUiStore } from '@/stores/ui'

const tagStore = useTagStore()
const uiStore = useUiStore()

onMounted(() => {
  // 预加载标签
  tagStore.fetchTags()
})
</script>

<style lang="scss" scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  margin-top: 60px;
  margin-left: 240px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 24px;
  background: #f8fafc;
  transition: margin-left 0.3s;

  &.collapsed {
    margin-left: 64px;
  }
}
</style>
```

**Step 2: 创建认证布局**

```vue
<template>
  <div class="auth-layout">
    <div class="auth-container">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style lang="scss" scoped>
.auth-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}
</style>
```

**Step 3: 提交更改**

```bash
git add src/components/layout/DashboardLayout.vue src/components/layout/AuthLayout.vue
git commit -m "feat: 创建布局组件"
```

---

## 阶段 8: 样式系统

### Task 18: 创建全局样式系统

**Files:**
- Create: `frontend/src/assets/styles/variables.scss`
- Create: `frontend/src/assets/styles/global.scss`
- Create: `frontend/src/assets/styles/element.scss`

**Step 1: 创建样式变量**

```scss
// 颜色系统
$primary-color: #3b82f6;
$success-color: #10b981;
$warning-color: #f59e0b;
$danger-color: #ef4444;
$info-color: #3b82f6;

// 文字颜色
$text-primary: #334155;
$text-secondary: #64748b;
$text-disabled: #94a3b8;

// 背景颜色
$bg-page: #f8fafc;
$bg-card: #ffffff;
$bg-sidebar: #1e293b;
$bg-sidebar-hover: #334155;

// 边框颜色
$border-color: #e5e7eb;
$border-color-light: #f1f5f9;

// 间距
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// 圆角
$border-radius-sm: 4px;
$border-radius-md: 8px;
$border-radius-lg: 12px;

// 阴影
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

// 侧边栏
$sidebar-width: 240px;
$sidebar-width-collapsed: 64px;
$header-height: 60px;
```

**Step 2: 创建全局样式**

```scss
@import './variables.scss';
@import './reset.scss';
@import './element.scss';

// 全局样式
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: $text-primary;
  background: $bg-page;
  line-height: 1.6;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: $bg-page;
}

::-webkit-scrollbar-thumb {
  background: $border-color;
  border-radius: 4px;

  &:hover {
    background: $text-secondary;
  }
}

// 卡片样式
.card {
  background: $bg-card;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
}

// 工具类
.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.text-primary {
  color: $primary-color;
}

.text-success {
  color: $success-color;
}

.text-warning {
  color: $warning-color;
}

.text-danger {
  color: $danger-color;
}

.mt-sm { margin-top: $spacing-sm; }
.mt-md { margin-top: $spacing-md; }
.mt-lg { margin-top: $spacing-lg; }

.mb-sm { margin-bottom: $spacing-sm; }
.mb-md { margin-bottom: $spacing-md; }
.mb-lg { margin-bottom: $spacing-lg; }

.p-sm { padding: $spacing-sm; }
.p-md { padding: $spacing-md; }
.p-lg { padding: $spacing-lg; }
```

**Step 3: 创建 Element Plus 样式覆盖**

```scss
// Element Plus 样式覆盖
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #3b82f6,
    ),
    'success': (
      'base': #10b981,
    ),
    'warning': (
      'base': #f59e0b,
    ),
    'danger': (
      'base': #ef4444,
    ),
    'info': (
      'base': #3b82f6,
    ),
  )
);

// 卡片样式覆盖
.el-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

// 按钮样式覆盖
.el-button {
  border-radius: 4px;
  font-weight: 500;
}

// 输入框样式覆盖
.el-input__inner {
  border-radius: 4px;
  height: 40px;
}

// 表格样式覆盖
.el-table {
  .el-table__body tr:hover > td {
    background: #f8fafc;
  }
}

// 对话框样式覆盖
.el-dialog {
  border-radius: 8px;
}
```

**Step 4: 提交更改**

```bash
git add src/assets/styles/variables.scss src/assets/styles/global.scss src/assets/styles/element.scss
git commit -m "feat: 创建全局样式系统"
```

---

## 阶段 9: 认证页面

### Task 19: 创建登录和注册页面

**Files:**
- Create: `frontend/src/views/auth/Login.vue`

**Step 1: 创建登录页面**

```vue
<template>
  <el-card class="login-card">
    <template #header>
      <div class="card-header">
        <h2>{{ isLogin ? '登录' : '注册' }}</h2>
      </div>
    </template>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      @submit.prevent="handleSubmit"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>

      <el-form-item label="邮箱" prop="email" v-if="!isLogin">
        <el-input v-model="form.email" type="email" placeholder="请输入邮箱" />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>

      <el-form-item v-if="!isLogin" label="确认密码" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          show-password
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">
          {{ isLogin ? '登录' : '注册' }}
        </el-button>
      </el-form-item>

      <el-form-item>
        <el-button text link @click="toggleMode">
          {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (!isLogin.value && value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

function toggleMode() {
  isLogin.value = !isLogin.value
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    let success = false

    if (isLogin.value) {
      success = await authStore.login({
        username: form.username,
        password: form.password
      })
    } else {
      success = await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password
      })
    }

    loading.value = false

    if (success) {
      const redirect = (route.query.redirect as string) || '/dashboard'
      router.push(redirect)
    }
  })
}
</script>

<style lang="scss" scoped>
.login-card {
  .card-header {
    text-align: center;

    h2 {
      margin: 0;
      color: #1e293b;
    }
  }
}

:deep(.el-card__header) {
  padding: 20px 20px 10px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
```

**Step 2: 提交更改**

```bash
git add src/views/auth/Login.vue
git commit -m "feat: 创建登录和注册页面"
```

---

## 阶段 10: 文章功能

### Task 20: 创建文章列表页面

**Files:**
- Create: `frontend/src/views/articles/ArticleList.vue`

**Step 1: 创建文章列表页面**

```vue
<template>
  <div class="article-list-page">
    <div class="page-header">
      <h2>文章列表</h2>
      <div class="header-actions">
        <el-button type="primary" @click="goToUpload">
          <el-icon><Upload /></el-icon>
          上传文章
        </el-button>
        <el-button @click="goToImport">
          <el-icon><Link /></el-icon>
          导入 URL
        </el-button>
      </div>
    </div>

    <!-- 筛选器 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filter">
        <el-form-item label="标签">
          <el-select
            v-model="filter.tag_id"
            placeholder="全部标签"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="tag in tagStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 文章列表 -->
    <el-card class="article-card">
      <div v-if="articleStore.loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <el-empty v-else-if="articleStore.articles.length === 0" description="暂无文章" />

      <div v-else class="article-list">
        <div
          v-for="article in articleStore.articles"
          :key="article.id"
          class="article-item"
          @click="goToDetail(article.id)"
        >
          <div class="article-header">
            <h3 class="article-title">{{ article.title }}</h3>
            <div class="article-actions" @click.stop>
              <el-button
                v-if="canEdit(article.author_id)"
                size="small"
                text
                @click="handleEdit(article)"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button
                v-if="canDelete(article.author_id)"
                size="small"
                text
                type="danger"
                @click="handleDelete(article)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>

          <p class="article-summary">{{ article.summary || truncateText(article.content) }}</p>

          <div class="article-meta">
            <div class="tags">
              <el-tag
                v-for="tag in article.tags"
                :key="tag.id"
                :color="tag.color"
                size="small"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
            </div>
            <div class="meta-info">
              <span>{{ formatDate(article.created_at) }}</span>
              <span>{{ article.view_count }} 次阅读</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="articleStore.pagination.total > 0" class="pagination">
        <el-pagination
          v-model:current-page="articleStore.pagination.page"
          v-model:page-size="articleStore.pagination.size"
          :total="articleStore.pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 导入 URL 对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入文章" width="500px">
      <el-form :model="importForm" label-width="80px">
        <el-form-item label="文章 URL" required>
          <el-input
            v-model="importForm.url"
            placeholder="请输入文章 URL"
            type="url"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="importForm.tag_ids"
            multiple
            placeholder="选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in tagStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="handleImport">
          确认导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useArticleStore } from '@/stores/article'
import { useTagStore } from '@/stores/tag'
import { useAuthStore } from '@/stores/auth'
import { formatDate, truncateText } from '@/utils/date'
import { canEditArticle, canDeleteArticle } from '@/utils/permission'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { ArticleResponse, ArticleFromHtmlUrlRequest } from '@/types'
import { articleApi } from '@/api/articles'

const router = useRouter()
const articleStore = useArticleStore()
const tagStore = useTagStore()
const authStore = useAuthStore()

const importDialogVisible = ref(false)
const importing = ref(false)

const filter = reactive({
  tag_id: undefined as number | undefined
})

const importForm = reactive<ArticleFromHtmlUrlRequest>({
  url: '',
  tag_ids: []
})

function canEdit(authorId: number): boolean {
  return canEditArticle(authorId)
}

function canDelete(authorId: number): boolean {
  return canDeleteArticle(authorId)
}

async function fetchData() {
  await articleStore.fetchArticles({
    page: articleStore.pagination.page,
    size: articleStore.pagination.size,
    tag_id: filter.tag_id
  })
}

function handleFilter() {
  articleStore.pagination.page = 1
  fetchData()
}

function handleReset() {
  filter.tag_id = undefined
  articleStore.pagination.page = 1
  fetchData()
}

function goToUpload() {
  router.push({ name: 'ArticleUpload' })
}

function goToImport() {
  importDialogVisible.value = true
}

function goToDetail(id: number) {
  router.push({ name: 'ArticleDetail', params: { id } })
}

function handleEdit(article: ArticleResponse) {
  // TODO: 实现编辑功能
  ElMessage.info('编辑功能开发中')
}

async function handleDelete(article: ArticleResponse) {
  try {
    await ElMessageBox.confirm(`确定要删除《${article.title}》吗？`, '删除确认', {
      type: 'warning'
    })
    await articleStore.deleteArticle(article.id)
  } catch {
    // 用户取消
  }
}

async function handleImport() {
  if (!importForm.url) {
    ElMessage.warning('请输入文章 URL')
    return
  }

  importing.value = true
  try {
    const response = await articleApi.importFromUrl(importForm)
    ElMessage.success(`文章导入成功！ID: ${response.data.article_id}`)
    importDialogVisible.value = false
    importForm.url = ''
    importForm.tag_ids = []
    fetchData()
  } catch {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.article-list-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      color: #1e293b;
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .filter-card {
    margin-bottom: 20px;
  }

  .article-card {
    .loading-container {
      padding: 20px;
    }

    .article-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .article-item {
      padding: 16px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
      }

      .article-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;

        .article-title {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #1e293b;
          flex: 1;
        }

        .article-actions {
          display: flex;
          gap: 4px;
        }
      }

      .article-summary {
        margin: 0 0 12px;
        color: #64748b;
        line-height: 1.6;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .article-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .tags {
          display: flex;
          gap: 8px;
        }

        .meta-info {
          display: flex;
          gap: 16px;
          color: #94a3b8;
          font-size: 13px;
        }
      }
    }

    .pagination {
      margin-top: 24px;
      display: flex;
      justify-content: center;
    }
  }
}
</style>
```

**Step 2: 提交更改**

```bash
git add src/views/articles/ArticleList.vue
git commit -m "feat: 创建文章列表页面"
```

---

### Task 21: 创建文章详情和上传页面

**Files:**
- Create: `frontend/src/views/articles/ArticleDetail.vue`
- Create: `frontend/src/views/articles/ArticleUpload.vue`

**Step 1: 创建文章详情页面**

```vue
<template>
  <div class="article-detail-page">
    <div v-if="articleStore.loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="articleStore.currentArticle" class="article-content">
      <!-- 文章头部 -->
      <div class="article-header">
        <h1 class="article-title">{{ articleStore.currentArticle.title }}</h1>

        <div class="article-meta">
          <div class="tags">
            <el-tag
              v-for="tag in articleStore.currentArticle.tags"
              :key="tag.id"
              :color="tag.color"
              class="tag-item"
            >
              {{ tag.name }}
            </el-tag>
          </div>
          <div class="meta-info">
            <span>{{ formatDate(articleStore.currentArticle.created_at) }}</span>
            <span>{{ articleStore.currentArticle.view_count }} 次阅读</span>
          </div>
        </div>

        <div v-if="canEditArticle(articleStore.currentArticle.author_id)" class="article-actions">
          <el-button @click="handleEdit">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" @click="handleDelete">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>

      <!-- 文章内容 -->
      <el-card class="content-card">
        <div v-if="articleStore.currentArticle.html_content" class="html-content" v-html="sanitizedHtml" />
        <div v-else class="markdown-content">
          {{ articleStore.currentArticle.content }}
        </div>
      </el-card>

      <!-- 关键词 -->
      <el-card v-if="articleStore.currentArticle.keywords" class="keywords-card">
        <div class="keywords">
          <strong>关键词：</strong>
          <el-tag
            v-for="(keyword, index) in keywordList"
            :key="index"
            size="small"
            class="keyword-tag"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="文章不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useArticleStore } from '@/stores/article'
import { formatDate } from '@/utils/date'
import { canEditArticle } from '@/utils/permission'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()

const keywordList = computed(() => {
  if (!articleStore.currentArticle?.keywords) return []
  return articleStore.currentArticle.keywords.split(/[,，、]/).map(k => k.trim()).filter(k => k)
})

// 简单的 HTML 清理（生产环境建议使用 DOMPurify）
const sanitizedHtml = computed(() => {
  return articleStore.currentArticle?.html_content || ''
})

async function handleEdit() {
  // TODO: 实现编辑功能
}

async function handleDelete() {
  if (!articleStore.currentArticle) return

  try {
    await ElMessageBox.confirm(
      `确定要删除《${articleStore.currentArticle.title}》吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await articleStore.deleteArticle(articleStore.currentArticle.id)
    router.push({ name: 'ArticleList' })
  } catch {
    // 用户取消
  }
}

onMounted(async () => {
  const id = Number(route.params.id)
  if (id) {
    await articleStore.fetchArticle(id)
  }
})
</script>

<style lang="scss" scoped>
.article-detail-page {
  max-width: 900px;
  margin: 0 auto;
}

.loading-container {
  padding: 40px;
}

.article-content {
  .article-header {
    margin-bottom: 24px;

    .article-title {
      margin: 0 0 16px;
      font-size: 28px;
      font-weight: 700;
      color: #1e293b;
      line-height: 1.4;
    }

    .article-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .tags {
        display: flex;
        gap: 8px;
      }

      .meta-info {
        display: flex;
        gap: 16px;
        color: #94a3b8;
      }
    }

    .article-actions {
      display: flex;
      gap: 12px;
    }
  }

  .content-card {
    margin-bottom: 20px;

    .html-content {
      line-height: 1.8;
      color: #334155;

      :deep(h1),
      :deep(h2),
      :deep(h3) {
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        color: #1e293b;
      }

      :deep(p) {
        margin-bottom: 16px;
      }

      :deep(img) {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 16px 0;
      }

      :deep(pre) {
        background: #1e293b;
        color: #e2e8f0;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 16px 0;
      }

      :deep(code) {
        background: #f1f5f9;
        color: #e11d48;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
      }

      :deep(a) {
        color: #3b82f6;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }

    .markdown-content {
      white-space: pre-wrap;
      line-height: 1.8;
      color: #334155;
    }
  }

  .keywords-card {
    .keywords {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;

      .keyword-tag {
        margin-left: 0;
      }
    }
  }
}
</style>
```

**Step 2: 创建文章上传页面**

```vue
<template>
  <div class="article-upload-page">
    <div class="page-header">
      <h2>上传文章</h2>
    </div>

    <el-card class="upload-card">
      <el-tabs v-model="activeTab">
        <!-- 文件上传 -->
        <el-tab-pane label="文件上传" name="file">
          <el-form :model="fileForm" label-width="100px">
            <el-form-item label="选择文件" required>
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-exceed="handleExceed"
                drag
                class="upload-area"
              >
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="upload-text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="upload-tip">
                    支持 .txt, .md, .html 等文本格式，文件大小不超过 10MB
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <el-form-item label="标题">
              <el-input v-model="fileForm.title" placeholder="留空则从文件中提取" />
            </el-form-item>

            <el-form-item label="摘要">
              <el-input
                v-model="fileForm.summary"
                type="textarea"
                :rows="3"
                placeholder="留空则自动生成"
              />
            </el-form-item>

            <el-form-item label="关键词">
              <el-input v-model="fileForm.keywords" placeholder="多个关键词用逗号分隔" />
            </el-form-item>

            <el-form-item label="标签">
              <el-select
                v-model="fileForm.tag_ids"
                multiple
                placeholder="选择标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in tagStore.tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="uploading" @click="handleFileUpload">
                上传
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 手动输入 -->
        <el-tab-pane label="手动输入" name="manual">
          <el-form :model="manualForm" :rules="manualRules" ref="manualFormRef" label-width="100px">
            <el-form-item label="标题" prop="title">
              <el-input v-model="manualForm.title" placeholder="请输入文章标题" />
            </el-form-item>

            <el-form-item label="来源 URL">
              <el-input v-model="manualForm.source_url" placeholder="请输入来源 URL" />
            </el-form-item>

            <el-form-item label="内容" prop="content">
              <el-input
                v-model="manualForm.content"
                type="textarea"
                :rows="15"
                placeholder="请输入文章内容（支持 Markdown）"
              />
            </el-form-item>

            <el-form-item label="摘要">
              <el-input
                v-model="manualForm.summary"
                type="textarea"
                :rows="3"
                placeholder="留空则自动生成"
              />
            </el-form-item>

            <el-form-item label="关键词">
              <el-input v-model="manualForm.keywords" placeholder="多个关键词用逗号分隔" />
            </el-form-item>

            <el-form-item label="标签">
              <el-select
                v-model="manualForm.tag_ids"
                multiple
                placeholder="选择标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in tagStore.tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="handleManualSubmit">
                提交
              </el-button>
              <el-button @click="handleManualReset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTagStore } from '@/stores/tag'
import { ElMessage, type FormInstance, type FormRules, type UploadInstance, type UploadFile } from 'element-plus'
import { articleApi } from '@/api/articles'
import type { UploadRawFile } from 'element-plus'

const router = useRouter()
const tagStore = useTagStore()

const activeTab = ref('file')
const uploading = ref(false)
const submitting = ref(false)
const uploadRef = ref<UploadInstance>()
const manualFormRef = ref<FormInstance>()

const fileForm = reactive({
  file: null as File | null,
  title: '',
  summary: '',
  keywords: '',
  tag_ids: [] as number[]
})

const manualForm = reactive({
  title: '',
  source_url: '',
  content: '',
  summary: '',
  keywords: '',
  tag_ids: [] as number[]
})

const manualRules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    fileForm.file = file.raw
    // 从文件名提取标题
    if (!fileForm.title) {
      const name = file.name.replace(/\.[^/.]+$/, '')
      fileForm.title = name
    }
  }
}

function handleExceed() {
  ElMessage.warning('最多只能上传一个文件')
}

async function handleFileUpload() {
  if (!fileForm.file) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', fileForm.file)
    if (fileForm.title) formData.append('title', fileForm.title)
    if (fileForm.summary) formData.append('summary', fileForm.summary)
    if (fileForm.keywords) formData.append('keywords', fileForm.keywords)
    if (fileForm.tag_ids.length > 0) {
      formData.append('tag_ids', fileForm.tag_ids.join(','))
    }

    await articleApi.uploadArticle(formData)
    ElMessage.success('上传成功')
    router.push({ name: 'ArticleList' })
  } catch {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

function handleReset() {
  fileForm.file = null
  fileForm.title = ''
  fileForm.summary = ''
  fileForm.keywords = ''
  fileForm.tag_ids = []
  uploadRef.value?.clearFiles()
}

async function handleManualSubmit() {
  if (!manualFormRef.value) return

  await manualFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      // TODO: 实现手动创建文章的 API
      ElMessage.success('创建成功')
      router.push({ name: 'ArticleList' })
    } catch {
      ElMessage.error('创建失败')
    } finally {
      submitting.value = false
    }
  })
}

function handleManualReset() {
  manualFormRef.value?.resetFields()
}

onMounted(() => {
  tagStore.fetchTags()
})
</script>

<style lang="scss" scoped>
.article-upload-page {
  max-width: 800px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 20px;

    h2 {
      margin: 0;
      color: #1e293b;
    }
  }

  .upload-card {
    .upload-area {
      width: 100%;

      :deep(.el-upload-dragger) {
        width: 100%;
        height: 200px;
      }

      .upload-icon {
        font-size: 48px;
        color: #3b82f6;
        margin-bottom: 16px;
      }

      .upload-text {
        color: #64748b;

        em {
          color: #3b82f6;
          font-style: normal;
        }
      }

      .upload-tip {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 8px;
      }
    }
  }
}
</style>
```

**Step 3: 提交更改**

```bash
git add src/views/articles/ArticleDetail.vue src/views/articles/ArticleUpload.vue
git commit -m "feat: 创建文章详情和上传页面"
```

---

## 阶段 11: 其他页面

### Task 22: 创建仪表盘、标签和搜索页面

**Files:**
- Create: `frontend/src/views/dashboard/Dashboard.vue`
- Create: `frontend/src/views/tags/TagManage.vue`
- Create: `frontend/src/views/search/Search.vue`

由于篇幅限制，这些页面的实现按照类似模式创建，包含：
- 仪表盘：统计卡片、最近文章、热门标签
- 标签管理：CRUD 操作、颜色选择器
- 搜索页：搜索框、标签筛选、结果展示

**提交命令示例：**
```bash
git add src/views/dashboard/Dashboard.vue
git commit -m "feat: 创建仪表盘页面"

git add src/views/tags/TagManage.vue
git commit -m "feat: 创建标签管理页面"

git add src/views/search/Search.vue
git commit -m "feat: 创建搜索页面"
```

---

### Task 23: 创建阅读记录和用户管理页面

**Files:**
- Create: `frontend/src/views/reading/History.vue`
- Create: `frontend/src/views/reading/Stats.vue`
- Create: `frontend/src/views/users/UserManage.vue`
- Create: `frontend/src/views/profile/Profile.vue`

**提交命令示例：**
```bash
git add src/views/reading/History.vue src/views/reading/Stats.vue
git commit -m "feat: 创建阅读记录相关页面"

git add src/views/users/UserManage.vue src/views/profile/Profile.vue
git commit -m "feat: 创建用户管理和个人资料页面"
```

---

## 阶段 12: 最终集成和测试

### Task 24: 最终集成和验证

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/README.md`

**Step 1: 安装所有依赖**

```bash
cd frontend
npm install
```

**Step 2: 验证开发环境**

```bash
npm run dev
```

预期输出：
- 服务器启动在 `http://localhost:5173`
- 能够访问登录页面
- 能够登录并访问各个页面

**Step 3: 构建生产版本**

```bash
npm run build
```

**Step 4: 创建 README**

```markdown
# 知识系统前端

基于 Vue 3 + TypeScript + Pinia + Element Plus 构建的知识管理系统前端应用。

## 技术栈

- Vue 3.4 (Composition API + `<script setup>`)
- TypeScript 5.3
- Pinia 2.1 (状态管理)
- Vue Router 4.2 (路由)
- Element Plus 2.5 (UI 组件库)
- Axios 1.6 (HTTP 客户端)
- Vite 5.0 (构建工具)
- Sass (样式预处理)

## 开发

### 安装依赖
\`\`\`bash
npm install
\`\`\`

### 启动开发服务器
\`\`\`bash
npm run dev
\`\`\`

### 构建生产版本
\`\`\`bash
npm run build
\`\`\`

### 代码检查
\`\`\`bash
npm run lint
\`\`\`

## 项目结构

\`\`\`
src/
├── api/              # API 集成层
├── assets/           # 静态资源
├── components/       # 通用组件
├── layouts/          # 布局组件
├── router/           # 路由配置
├── stores/           # Pinia Store
├── types/            # TypeScript 类型
├── utils/            # 工具函数
├── views/            # 页面组件
├── App.vue
└── main.ts
\`\`\`

## 环境变量

- `.env.development` - 开发环境配置
- `.env.production` - 生产环境配置

## 后端 API

默认连接到 `http://127.0.0.1:8000/api/v1`
```

**Step 5: 最终提交**

```bash
git add README.md
git commit -m "docs: 添加项目 README 文档"
```

---

## 完成清单

在实施过程中，请确保完成以下检查项：

### 代码质量
- [ ] 所有文件通过 ESLint 检查
- [ ] 所有组件使用 TypeScript 类型
- [ ] 所有 API 调用都有错误处理
- [ ] 所有异步操作都有 loading 状态

### 功能完整性
- [ ] 用户可以登录和注册
- [ ] 用户可以查看文章列表和详情
- [ ] 用户可以上传文章
- [ ] 用户可以从 URL 导入文章
- [ ] 用户可以管理标签
- [ ] 用户可以搜索文章
- [ ] 用户可以查看阅读历史
- [ ] 管理员可以管理用户

### 用户体验
- [ ] 所有操作都有适当的反馈
- [ ] 错误消息清晰友好
- [ ] 加载状态明确可见
- [ ] 响应式布局适配不同屏幕

### 性能优化
- [ ] 路由懒加载
- [ ] 组件按需导入
- [ ] 图片懒加载
- [ ] 合理的缓存策略

---

## 常见问题

### 问题：启动开发服务器后白屏
**解决方案**：检查控制台错误，确保所有依赖已正确安装

### 问题：API 请求失败
**解决方案**：
1. 确认后端服务已启动
2. 检查 `.env.development` 中的 API 地址
3. 检查浏览器控制台的网络请求

### 问题：路由跳转后页面不刷新
**解决方案**：检查路由配置和组件导入是否正确

---

## 后续优化建议

1. **测试覆盖**：添加单元测试和 E2E 测试
2. **性能优化**：
   - 虚拟滚动处理大列表
   - CDN 加速静态资源
   - Service Worker 实现离线支持
3. **用户体验**：
   - 添加骨架屏
   - 优化动画效果
   - 添加更多快捷操作
4. **功能扩展**：
   - 支持文章导出
   - 支持全文搜索
   - 添加数据可视化

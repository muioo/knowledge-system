# 知识系统前端设计方案

> 日期: 2025-03-28
> 技术栈: Vite + React + Tailwind CSS + React Router + Context API

---

## 1. 项目概述

构建一个基于 React 的知识管理系统前端，完整对接后端 API，提供用户认证、文章管理、标签管理、阅读统计等功能。

### 技术选型

| 技术 | 用途 | 说明 |
|------|------|------|
| Vite | 构建工具 | 快速开发体验 |
| React 18 | UI框架 | 组件化开发 |
| Tailwind CSS | 样式框架 | 快速构建样式 |
| React Router | 路由管理 | 单页应用路由 |
| Axios | HTTP客户端 | API请求 |
| Context API | 状态管理 | 轻量级状态管理 |

---

## 2. 项目结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/              # API请求模块
│   │   ├── client.ts     # Axios配置
│   │   ├── auth.ts       # 认证API
│   │   ├── article.ts    # 文章API
│   │   ├── tag.ts        # 标签API
│   │   ├── user.ts       # 用户API
│   │   └── reading.ts    # 阅读记录API
│   ├── components/       # 通用组件
│   │   ├── layout/       # 布局组件
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── MainLayout.tsx
│   │   └── ui/           # 基础UI组件
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       └── ...
│   ├── contexts/         # Context状态管理
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── pages/            # 页面组件
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── ArticleList.tsx
│   │   ├── ArticleCreate.tsx
│   │   ├── ArticleDetail.tsx
│   │   └── TagManage.tsx
│   ├── hooks/            # 自定义Hooks
│   ├── utils/            # 工具函数
│   ├── types/            # TypeScript类型定义
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

---

## 3. 页面架构与路由

### 路由结构

```
/ (login)                 → 登录页
/dashboard                → 仪表盘（首页）
/articles                 → 文章列表
/articles/create          → 创建文章
/articles/:id             → 文章详情
/tags                     → 标签管理
/reading/stats            → 阅读统计
```

### 页面说明

| 页面 | 功能描述 | 对应API |
|------|----------|---------|
| 登录页 | 用户登录，还原login.html样式（无Google登录、忘记密码、注册） | POST /api/v1/auth/login |
| 仪表盘 | 数据统计卡片，还原home.html卡片布局风格 | GET /api/v1/users/me |
| 文章列表 | 分页展示、搜索、标签筛选 | GET /api/v1/articles/ |
| 文章创建 | 文件上传、URL导入两种方式 | POST /api/v1/articles/upload<br>POST /api/v1/articles/from-url-html |
| 文章详情 | 展示文章内容和元信息 | GET /api/v1/articles/:id |
| 标签管理 | CRUD操作、颜色选择 | GET/POST/PUT/DELETE /api/v1/tags/ |
| 阅读统计 | 个人阅读历史和统计数据 | GET /api/v1/reading/stats |

---

## 4. 核心组件设计

### 布局组件（还原 home.html 样式）

| 组件 | 功能 | 样式参考 |
|------|------|----------|
| `Sidebar` | 左侧导航栏，支持响应式折叠 | home.html 的侧边栏 |
| `Header` | 顶部栏，包含用户信息和汉堡菜单 | home.html 的移动端顶部栏 |
| `MainLayout` | 主布局容器，组合 Sidebar + Header | home.html 的整体布局 |

### 基础UI组件（还原 login.html 样式）

| 组件 | 功能 | 样式参考 |
|------|------|----------|
| `Button` | 渐变按钮、hover效果 | login.html 的提交按钮 |
| `Input` | 带边框和焦点状态的输入框 | login.html 的输入框 |
| `Card` | 卡片容器，带阴影和hover效果 | home.html 的统计卡片 |
| `PasswordInput` | 带显示/隐藏切换的密码输入框 | login.html 的密码输入框 |
| `DotMap` | 装饰性点地图动画组件 | login.html 的左侧地图 |

### 业务组件

| 组件 | 功能 |
|------|------|
| `ArticleCard` | 文章卡片，显示标题、摘要、标签 |
| `TagBadge` | 标签徽章，带颜色 |
| `Pagination` | 分页组件 |
| `SearchBar` | 搜索栏，支持关键词和标签筛选 |
| `FileUploader` | 文件上传组件 |
| `UrlImporter` | URL导入组件 |

---

## 5. API 集成方案

### HTTP 客户端配置

```typescript
// 基础配置
- baseURL: http://localhost:8022/api/v1
- timeout: 30000ms
- 使用 axios 拦截器处理 token
- 请求拦截器：自动添加 Authorization header
- 响应拦截器：统一处理错误、token刷新
```

### API 模块划分

| 模块 | 文件 | 功能 |
|------|------|------|
| auth | `api/auth.ts` | 登录、获取当前用户信息 |
| article | `api/article.ts` | 文章CRUD、文件上传、URL导入 |
| tag | `api/tag.ts` | 标签CRUD、获取标签文章 |
| user | `api/user.ts` | 用户管理（管理员功能） |
| reading | `api/reading.ts` | 阅读记录、统计数据 |
| search | `api/search.ts` | 文章搜索 |

### Token 管理策略

```
1. 登录成功后存储 access_token 和 refresh_token 到 localStorage
2. 每次请求自动携带 Bearer token
3. 401 错误时尝试使用 refresh_token 刷新
4. 刷新失败则跳转登录页
```

---

## 6. 状态管理方案（Context API）

### AuthContext - 认证状态

```typescript
状态：
- user: User | null          // 当前用户信息
- isAuthenticated: boolean   // 是否已登录
- isLoading: boolean         // 加载状态

方法：
- login(username, password)  // 登录
- logout()                   // 登出
- refreshUser()              // 刷新用户信息
```

### ArticleContext - 文章状态

```typescript
状态：
- articles: Article[]        // 文章列表
- total: number              // 总数
- currentPage: number        // 当前页
- filters: ArticleFilters    // 筛选条件

方法：
- fetchArticles(params)      // 获取文章列表
- createArticle(data)        // 创建文章
- updateArticle(id, data)    // 更新文章
- deleteArticle(id)          // 删除文章
```

### TagContext - 标签状态

```typescript
状态：
- tags: Tag[]                // 标签列表

方法：
- fetchTags()                // 获取所有标签
- createTag(data)            // 创建标签
- updateTag(id, data)        // 更新标签
- deleteTag(id)              // 删除标签
```

---

## 7. 开发阶段划分

### 阶段一：项目初始化
- 清空并重建 frontend 目录
- 初始化 Vite + React 项目
- 安装依赖：react-router-dom, axios, tailwindcss
- 配置 Tailwind CSS
- 创建基础目录结构

### 阶段二：基础组件和布局
- 创建基础 UI 组件（Button, Input, Card等）
- 创建布局组件（Sidebar, Header, MainLayout）
- 还原 login.html 的登录页面
- 还原 home.html 的仪表盘布局框架

### 阶段三：认证功能
- 实现 AuthContext
- 配置 API 客户端
- 实现登录功能和路由守卫
- 实现登出功能

### 阶段四：文章管理
- 文章列表页面（分页、搜索、筛选）
- 文章创建页面（文件上传、URL导入）
- 文章详情页面
- 实现 ArticleContext

### 阶段五：其他功能
- 标签管理页面
- 阅读统计页面
- 实现 TagContext 和相关功能

### 阶段六：优化和完善
- 响应式适配
- 加载状态和错误处理
- 动画效果优化

---

## 8. 设计参考

- **登录页样式**: `login.html` - 简化版（移除Google登录、忘记密码、注册功能）
- **仪表盘样式**: `home.html` - 侧边栏布局、卡片组件
- **后端API**: `API_DOCUMENTATION.md` - 完整的API接口文档

---

**文档结束**

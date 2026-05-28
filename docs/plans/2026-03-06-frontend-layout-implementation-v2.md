# 前端布局与文章管理页面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现知识系统前端的 DashboardLayout 布局组件、Sidebar、Header，以及文章列表和文章表单页面

**Architecture:** 采用渐进式实现策略，先搭建布局框架（DashboardLayout + Sidebar + Header），再实现功能页面（ArticleList + ArticleForm）。使用 Vue 3 Composition API + TypeScript + Pinia + Element Plus。

**Tech Stack:** Vue 3.4, TypeScript 5.3, Pinia 2.1, Vue Router 4.2, Element Plus 2.5, Sass

---

## 任务概览

本计划包含以下主要任务：

1. **路由配置** - 创建路由文件和导航守卫
2. **布局组件** - DashboardLayout、Sidebar、Header
3. **Dashboard 首页** - 统计卡片和最近文章
4. **文章列表页面** - 列表展示、筛选、分页
5. **文章表单页面** - 创建和编辑文章
6. **样式优化** - 全局样式和响应式适配

---

## Task 1: 创建路由配置

**Files:**
- Create: `frontend/src/router/index.ts`

**实现内容:**
- 定义所有路由（Dashboard、ArticleList、ArticleCreate、ArticleDetail、ArticleEdit）
- 实现路由守卫（检查认证状态）
- 配置路由懒加载

**提交:**
```bash
git add frontend/src/router/index.ts
git commit -m "feat: 创建路由配置和导航守卫"
```

---

## Task 2: 创建 DashboardLayout 组件

**Files:**
- Create: `frontend/src/components/layouts/DashboardLayout.vue`

**实现内容:**
- 整体布局框架（Sidebar + Main Container）
- 响应式设计（侧边栏宽度根据折叠状态变化）
- 集成 Sidebar 和 Header 组件

**提交:**
```bash
git add frontend/src/components/layouts/DashboardLayout.vue
git commit -m "feat: 创建 DashboardLayout 布局组件"
```

---

## Task 3: 创建 Sidebar 组件

**Files:**
- Create: `frontend/src/components/layouts/Sidebar.vue`

**实现内容:**
- 导航菜单（首页、文章管理、标签、搜索、阅读历史、设置）
- 深色背景样式（#001529）
- 支持折叠/展开
- 高亮当前路由
- 二级菜单（文章管理下的子菜单）

**提交:**
```bash
git add frontend/src/components/layouts/Sidebar.vue
git commit -m "feat: 创建 Sidebar 侧边栏组件"
```

---

## Task 4: 创建 Header 组件

**Files:**
- Create: `frontend/src/components/layouts/Header.vue`

**实现内容:**
- 折叠按钮（切换侧边栏）
- 面包屑导航
- 搜索框
- 通知图标
- 用户下拉菜单（个人信息、退出登录）

**提交:**
```bash
git add frontend/src/components/layouts/Header.vue
git commit -m "feat: 创建 Header 顶部导航组件"
```

---

## Task 5: 创建 Dashboard 首页

**Files:**
- Create: `frontend/src/views/Dashboard.vue`

**实现内容:**
- 统计卡片（文章总数、标签总数、总阅读量、今日新增）
- 最近文章列表
- 热门标签
- 响应式布局

**提交:**
```bash
git add frontend/src/views/Dashboard.vue
git commit -m "feat: 创建 Dashboard 首页"
```

---

## Task 6: 创建 ArticleList 页面

**Files:**
- Create: `frontend/src/views/articles/ArticleList.vue`

**实现内容:**
- 页面头部（标题 + 创建按钮）
- 筛选表单（关键词搜索、标签筛选、排序）
- 文章卡片列表（标题、摘要、标签、元信息）
- 操作按钮（查看、编辑、删除）
- 分页组件
- 加载状态和错误处理

**提交:**
```bash
git add frontend/src/views/articles/ArticleList.vue
git commit -m "feat: 创建文章列表页面"
```

---

## Task 7: 创建 ArticleForm 页面

**Files:**
- Create: `frontend/src/views/articles/ArticleForm.vue`

**实现内容:**
- 表单字段（标题、内容、摘要、标签、来源URL、关键词）
- 表单验证规则
- 创建和编辑模式切换
- 提交和取消按钮
- 加载状态和错误处理

**提交:**
```bash
git add frontend/src/views/articles/ArticleForm.vue
git commit -m "feat: 创建文章表单页面"
```

---

## Task 8: 创建全局样式文件

**Files:**
- Create: `frontend/src/assets/styles/global.scss`
- Create: `frontend/src/assets/styles/variables.scss`

**实现内容:**
- CSS 变量定义（颜色、间距、字体、阴影、圆角）
- 全局样式重置
- 通用工具类

**提交:**
```bash
git add frontend/src/assets/styles/
git commit -m "feat: 创建全局样式文件"
```

---

## Task 9: 更新 main.ts 引入路由

**Files:**
- Modify: `frontend/src/router/index.ts`

**实现内容:**
- 确保 main.ts 正确引入 router
- 初始化 uiStore

**提交:**
```bash
git add frontend/src/main.ts
git commit -m "feat: 更新 main.ts 引入路由"
```

---

## Task 10: 测试和优化

**测试流程:**
1. 启动开发服务器：`npm run dev`
2. 测试登录功能
3. 测试侧边栏折叠/展开
4. 测试文章列表加载和筛选
5. 测试文章创建和编辑
6. 测试响应式布局（桌面、平板、移动端）

**优化项:**
- 检查控制台错误
- 优化加载性能
- 调整样式细节

**提交:**
```bash
git add .
git commit -m "chore: 测试和优化前端布局"
```

---

## 实施注意事项

### 代码规范
- 使用 TypeScript 严格模式
- 遵循 Vue 3 Composition API 最佳实践
- 使用 `<script setup>` 语法
- 所有组件添加类型注解

### 错误处理
- 所有 API 调用使用 try-catch
- 显示友好的错误提示
- 加载状态和错误状态分离

### 性能优化
- 路由懒加载
- 合理使用 computed 和 watch
- 避免不必要的重渲染

### 响应式设计
- 移动端优先
- 使用 Element Plus 的响应式栅格系统
- 媒体查询断点：768px（平板）、1024px（桌面）

---

## 执行方式选择

计划已完成并保存到 `docs/plans/2026-03-06-frontend-layout-implementation-v2.md`。

**两种执行方式：**

**1. Subagent-Driven（当前会话）**
- 我为每个任务派发新的子代理
- 任务间进行代码审查
- 快速迭代

**2. Parallel Session（独立会话）**
- 在新会话中使用 executing-plans 技能
- 批量执行，设置检查点

**你选择哪种方式？**

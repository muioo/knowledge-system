# 按钮样式和面包屑导航实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 统一所有页面的按钮样式，添加完整层级面包屑导航，调整容器内容样式使其符合 example_html 设计规范。

**架构:** 渐进式增强方案 - 在 colors.css 中添加全局样式类，创建面包屑组件集成到 AppHeader，通过路由 meta 构建导航层级。

**技术栈:** Vue 3 + TypeScript + Element Plus + Pinia + Vue Router + CSS Variables

---

## 任务 1: 添加全局按钮样式类

**Files:**
- Modify: `frontend/src/styles/colors.css`

**Step 1: 在 colors.css 末尾添加按钮基础样式**

在文件末尾（第 368 行之后）添加以下内容：

```css
/* ============================================
   按钮组件样式
   基于 example_html 设计规范
   ============================================ */

/* --- 基础按钮类 --- */
.btn,
.el-button.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-family: var(--font-poppins);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  text-decoration: none;
}

/* --- 主要按钮 --- */
.btn-primary,
.el-button.btn-primary {
  background: var(--color-indigo);
  color: var(--bg-white);
  border: 1px solid var(--color-indigo);
}

.btn-primary:hover,
.el-button.btn-primary:hover {
  background: rgba(116, 89, 217, 0.9);
  border-color: rgba(116, 89, 217, 0.9);
}

/* --- 次要按钮 (outline) --- */
.btn-outline,
.el-button.btn-outline {
  background: transparent;
  color: var(--text-black);
  border: 1px solid var(--border-default);
}

.btn-outline:hover,
.el-button.btn-outline:hover {
  border-color: var(--color-indigo);
  color: var(--color-indigo);
  background: var(--bg-tertiary);
}

/* --- 文字按钮 (ghost) --- */
.btn-ghost,
.el-button.btn-ghost,
.el-button.is-text {
  background: transparent;
  color: var(--text-black);
  border: 1px solid transparent;
}

.btn-ghost:hover,
.el-button.btn-ghost:hover,
.el-button.is-text:hover {
  background: var(--bg-tertiary);
}

/* --- 危险按钮 --- */
.btn-danger,
.el-button.btn-danger {
  background: var(--color-red);
  color: var(--bg-white);
  border: 1px solid var(--color-red);
}

.btn-danger:hover,
.el-button.btn-danger:hover {
  background: rgba(255, 121, 119, 0.9);
}

/* 危险按钮 outline 样式 */
.btn-danger.btn-outline,
.el-button.btn-danger.btn-outline {
  background: transparent;
  color: var(--color-red);
  border: 1px solid var(--color-red);
}

.btn-danger.btn-outline:hover,
.el-button.btn-danger.btn-outline:hover {
  background: var(--color-red);
  color: var(--bg-white);
}

/* --- 按钮尺寸变体 --- */
.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-lg {
  padding: 12px 24px;
  font-size: 16px;
}
```

**Step 2: 保存并验证样式**

预期结果：文件保存成功，无语法错误

**Step 3: 提交**

```bash
git add frontend/src/styles/colors.css
git commit -m "style: 添加全局按钮样式类"
```

---

## 任务 2: 添加容器样式类

**Files:**
- Modify: `frontend/src/styles/colors.css`

**Step 1: 在 colors.css 末尾添加容器样式**

在任务 1 添加的内容之后添加：

```css
/* ============================================
   容器布局样式
   ============================================ */

/* --- 内容包裹器 --- */
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
}

/* --- 内容区块 --- */
.content-section {
  margin-bottom: 24px;
}

.content-section:last-child {
  margin-bottom: 0;
}

/* --- 卡片容器 --- */
.card-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* --- 表单容器 --- */
.form-container {
  max-width: 600px;
  margin: 0 auto;
}

/* --- 响应式 --- */
@media (max-width: 1200px) {
  .content-wrapper {
    max-width: 100%;
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 12px;
  }
}
```

**Step 2: 保存并验证**

预期结果：文件保存成功

**Step 3: 提交**

```bash
git add frontend/src/styles/colors.css
git commit -m "style: 添加容器布局样式类"
```

---

## 任务 3: 创建面包屑组件

**Files:**
- Create: `frontend/src/components/layout/AppBreadcrumb.vue`

**Step 1: 创建面包屑组件文件**

创建完整的组件文件：

```vue
<template>
  <div class="app-breadcrumb" v-if="items.length > 0">
    <router-link
      v-for="(item, index) in items"
      :key="index"
      :to="item.path"
      class="breadcrumb-item"
      :class="{ 'is-current': index === items.length - 1 }"
    >
      {{ item.title }}
    </router-link>
    <span v-if="index < items.length - 1" class="breadcrumb-separator">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  title: string
  path: string
}

const route = useRoute()

// 构建面包屑层级
const items = computed<BreadcrumbItem[]>(() => {
  const breadcrumbs: BreadcrumbItem[] = []

  // 添加仪表盘作为根
  breadcrumbs.push({
    title: '仪表盘',
    path: '/dashboard'
  })

  // 从当前路由向上遍历，构建完整路径
  const currentMeta = route.meta as any

  if (currentMeta.breadcrumb) {
    // 如果当前页面有 breadcrumb 配置，直接使用
    breadcrumbs.push({
      title: currentMeta.breadcrumb.title,
      path: route.path
    })
  } else if (route.path !== '/dashboard') {
    // 否则使用路由 meta.title
    breadcrumbs.push({
      title: (route.meta?.title as string) || '未知页面',
      path: route.path
    })
  }

  return breadcrumbs
})
</script>

<style scoped>
.app-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-poppins);
  font-size: 12px;
}

.breadcrumb-item {
  color: var(--color-indigo);
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-item.is-current {
  color: var(--text-black);
  font-weight: 700;
  pointer-events: none;
}

.breadcrumb-separator {
  display: flex;
  align-items: center;
  color: var(--text-grey-50);
}

.breadcrumb-separator svg {
  width: 14px;
  height: 14px;
}

/* 响应式 */
@media (max-width: 767px) {
  .app-breadcrumb {
    font-size: 11px;
  }
}
</style>
```

**Step 2: 保存文件**

预期结果：文件创建成功

**Step 3: 提交**

```bash
git add frontend/src/components/layout/AppBreadcrumb.vue
git commit -m "feat: 创建面包屑导航组件"
```

---

## 任务 4: 集成面包屑到 AppHeader

**Files:**
- Modify: `frontend/src/components/layout/AppHeader.vue`

**Step 1: 在 template 中添加面包屑组件**

在搜索框之前添加面包屑（第 10 行左右）：

找到：
```vue
    <!-- 右侧：搜索 + 通知 + 用户菜单 -->
    <div class="header-right">
      <!-- 搜索框 -->
      <div class="header-search">
```

修改为：
```vue
    <!-- 右侧：面包屑 + 搜索 + 通知 + 用户菜单 -->
    <div class="header-right">
      <!-- 面包屑导航 -->
      <AppBreadcrumb />

      <!-- 搜索框 -->
      <div class="header-search">
```

**Step 2: 在 script 中导入组件**

在 import 部分添加（第 63 行附近）：

```typescript
import AppBreadcrumb from './AppBreadcrumb.vue'
```

**Step 3: 保存并验证**

预期结果：组件导入成功，模板语法正确

**Step 4: 提交**

```bash
git add frontend/src/components/layout/AppHeader.vue
git commit -m "feat: 集成面包屑导航到顶部导航栏"
```

---

## 任务 5: 更新路由配置添加面包屑 meta

**Files:**
- Modify: `frontend/src/router/index.ts`

**Step 1: 查看当前路由配置**

运行：
```bash
cat frontend/src/router/index.ts
```

**Step 2: 为每个路由添加 breadcrumb meta**

找到路由配置，为每个页面路由添加 breadcrumb 信息。以下是示例（根据实际路由结构调整）：

```typescript
{
  path: '/dashboard',
  name: 'Dashboard',
  component: () => import('@/views/dashboard/DashboardView.vue'),
  meta: {
    title: '仪表盘',
    breadcrumb: {
      title: '仪表盘',
      path: '/dashboard'
    }
  }
},
{
  path: '/articles',
  name: 'ArticleList',
  component: () => import('@/views/article/ArticleListView.vue'),
  meta: {
    title: '文章管理',
    breadcrumb: {
      title: '文章管理',
      path: '/articles',
      parent: '/dashboard'
    }
  }
},
{
  path: '/articles/create',
  name: 'ArticleCreate',
  component: () => import('@/views/article/ArticleCreateView.vue'),
  meta: {
    title: '创建文章',
    breadcrumb: {
      title: '创建文章',
      path: '/articles/create',
      parent: '/articles'
    }
  }
},
{
  path: '/articles/:id',
  name: 'ArticleDetail',
  component: () => import('@/views/article/ArticleDetailView.vue'),
  meta: {
    title: '文章详情',
    breadcrumb: {
      title: '文章详情',
      path: '', // 动态路径
      parent: '/articles'
    }
  }
},
{
  path: '/tags',
  name: 'TagManage',
  component: () => import('@/views/tag/TagManageView.vue'),
  meta: {
    title: '标签管理',
    breadcrumb: {
      title: '标签管理',
      path: '/tags',
      parent: '/dashboard'
    }
  }
},
{
  path: '/users',
  name: 'UserManage',
  component: () => import('@/views/user/UserManageView.vue'),
  meta: {
    title: '用户管理',
    breadcrumb: {
      title: '用户管理',
      path: '/users',
      parent: '/dashboard'
    }
  }
},
{
  path: '/reading-stats',
  name: 'ReadingStats',
  component: () => import('@/views/reading/ReadingStatsView.vue'),
  meta: {
    title: '阅读统计',
    breadcrumb: {
      title: '阅读统计',
      path: '/reading-stats',
      parent: '/dashboard'
    }
  }
}
```

**Step 3: 保存并验证**

预期结果：路由配置语法正确

**Step 4: 提交**

```bash
git add frontend/src/router/index.ts
git commit -m "feat: 为路由添加面包屑 meta 信息"
```

---

## 任务 6: 更新 DashboardView 应用新样式

**Files:**
- Modify: `frontend/src/views/dashboard/DashboardView.vue`

**Step 1: 添加容器包裹器**

在最外层 div 添加 class（第 2 行）：

找到：
```vue
  <div class="dashboard-container">
```

修改为：
```vue
  <div class="dashboard-container content-wrapper">
```

**Step 2: 更新按钮样式**

找到所有 el-button，添加 class。

"快捷操作" 部分的按钮（约第 89-101 行）：

```vue
<el-button class="btn-primary" :icon="Plus" @click="$router.push('/articles/create')">
  创建文章
</el-button>
<el-button class="btn-outline" :icon="FolderOpened" @click="$router.push('/articles')">
  浏览文章
</el-button>
<el-button class="btn-outline" :icon="PriceTag" @click="$router.push('/tags')">
  管理标签
</el-button>
<el-button class="btn-outline" :icon="TrendCharts" @click="$router.push('/reading-stats')">
  阅读统计
</el-button>
```

**Step 3: 保存并验证**

预期结果：样式更新成功

**Step 4: 提交**

```bash
git add frontend/src/views/dashboard/DashboardView.vue
git commit -m "style: DashboardView 应用新按钮样式"
```

---

## 任务 7: 更新 ArticleListView 应用新样式

**Files:**
- Modify: `frontend/src/views/article/ArticleListView.vue`

**Step 1: 添加容器包裹器**

第 2 行：
```vue
  <div class="article-list-view content-wrapper">
```

**Step 2: 更新搜索和筛选按钮**

找到搜索按钮和筛选区域（约第 32-34 行）：

```vue
<el-button class="btn-primary" :icon="Search" @click="handleSearch">
  搜索
</el-button>
```

**Step 3: 更新卡片操作按钮**

找到文章卡片内的编辑和删除按钮（约第 48-50 行）：

```vue
<el-button class="btn-ghost" :icon="Edit" @click="editArticle(article.id)">编辑</el-button>
<el-button class="btn-ghost btn-danger" :icon="Delete" type="danger" @click="confirmDelete(article)">删除</el-button>
```

**Step 4: 保存并验证**

预期结果：样式更新成功

**Step 5: 提交**

```bash
git add frontend/src/views/article/ArticleListView.vue
git commit -m "style: ArticleListView 应用新按钮样式"
```

---

## 任务 8: 更新 ArticleDetailView 应用新样式

**Files:**
- Modify: `frontend/src/views/article/ArticleDetailView.vue`

**Step 1: 添加容器包裹器**

第 2 行：
```vue
  <div class="article-detail-view">
```

修改为（移除 padding，由 content-wrapper 处理）：
```vue
  <div class="article-detail-view content-wrapper">
```

**Step 2: 更新操作按钮**

找到头部操作按钮（约第 10-15 行）：

```vue
<el-button class="btn-outline" :icon="ArrowLeft" @click="$router.back()">返回</el-button>
<div class="action-buttons">
  <el-button class="btn-primary" :icon="Edit" @click="handleEdit">编辑</el-button>
  <el-button class="btn-danger" :icon="Delete" @click="confirmDelete">删除</el-button>
</div>
```

**Step 3: 更新编辑文章按钮（无内容时）**

找到无内容时的按钮（约第 71 行）：

```vue
<el-button class="btn-primary" :icon="Edit" @click="handleEdit">
  编辑文章
</el-button>
```

**Step 4: 更新返回按钮页脚**

找到底部的返回按钮（约第 94 行）：

```vue
<el-button class="btn-primary" @click="$router.push('/articles')">
  返回文章列表
</el-button>
```

**Step 5: 保存并验证**

预期结果：样式更新成功

**Step 6: 提交**

```bash
git add frontend/src/views/article/ArticleDetailView.vue
git commit -m "style: ArticleDetailView 应用新按钮样式"
```

---

## 任务 9: 更新 ArticleCreateView 应用新样式

**Files:**
- Modify: `frontend/src/views/article/ArticleCreateView.vue`

**Step 1: 添加容器包裹器**

第 2 行：
```vue
  <div class="article-create-view content-wrapper">
```

**Step 2: 更新创建和上传按钮**

找到导入和上传按钮（约第 78、151 行）：

```vue
<el-button class="btn-primary" @click="handleUrlImport" :loading="urlImporting">
  导入文章
</el-button>

<el-button class="btn-primary" @click="handleFileUpload" :loading="fileUploading">
  上传文章
</el-button>
```

**Step 3: 更新选择文件按钮**

找到文件选择按钮（约第 102 行）：

```vue
<el-button class="btn-primary">选择文件</el-button>
```

**Step 4: 保存并验证**

预期结果：样式更新成功

**Step 5: 提交**

```bash
git add frontend/src/views/article/ArticleCreateView.vue
git commit -m "style: ArticleCreateView 应用新按钮样式"
```

---

## 任务 10: 更新 TagManageView 应用新样式

**Files:**
- Modify: `frontend/src/views/tag/TagManageView.vue`

**Step 1: 添加容器包裹器**

第 2 行：
```vue
  <div class="tag-manage-view content-wrapper">
```

**Step 2: 更新创建标签按钮**

第 5-7 行：
```vue
<el-button class="btn-primary" :icon="Plus" @click="openCreateDialog">
  创建标签
</el-button>
```

**Step 3: 更新卡片操作按钮**

找到编辑和删除按钮（约第 32-33 行）：

```vue
<el-button class="btn-ghost" :icon="Edit" @click="openEditDialog(tag)">编辑</el-button>
<el-button class="btn-ghost btn-danger" :icon="Delete" type="danger" @click="confirmDelete(tag)">删除</el-button>
```

**Step 4: 更新空状态按钮**

找到空状态时的按钮（约第 15-17 行）：

```vue
<el-button class="btn-primary" :icon="Plus" @click="openCreateDialog">
  创建第一个标签
</el-button>
```

**Step 5: 更新对话框按钮**

找到对话框底部按钮（约第 69-71 行）：

```vue
<el-button @click="dialogVisible = false" class="btn-ghost">取消</el-button>
<el-button class="btn-primary" @click="submitForm" :loading="submitting">
  {{ isEditMode ? '保存' : '创建' }}
</el-button>
```

**Step 6: 保存并验证**

预期结果：样式更新成功

**Step 7: 提交**

```bash
git add frontend/src/views/tag/TagManageView.vue
git commit -m "style: TagManageView 应用新按钮样式"
```

---

## 任务 11: 更新 UserManageView 应用新样式

**Files:**
- Modify: `frontend/src/views/user/UserManageView.vue`

**Step 1: 添加容器包裹器**

第 2 行：
```vue
  <div class="user-manage-view content-wrapper">
```

**Step 2: 保存并验证**

预期结果：文件修改成功

**Step 3: 提交**

```bash
git add frontend/src/views/user/UserManageView.vue
git commit -m "style: UserManageView 应用容器样式"
```

---

## 任务 12: 更新 ReadingStatsView 应用新样式

**Files:**
- Modify: `frontend/src/views/reading/ReadingStatsView.vue`

**Step 1: 添加容器包裹器**

第 3 行：
```vue
  <div class="reading-stats-view content-wrapper">
```

**Step 2: 保存并验证**

预期结果：文件修改成功

**Step 3: 提交**

```bash
git add frontend/src/views/reading/ReadingStatsView.vue
git commit -m "style: ReadingStatsView 应用容器样式"
```

---

## 任务 13: 更新登录页面应用新样式

**Files:**
- Modify: `frontend/src/views/auth/Login.vue`

**Step 1: 更新登录按钮**

找到登录按钮（约第 44-52 行）：

```vue
<el-button
  type="primary"
  size="large"
  :loading="authStore.loading"
  class="w-full btn-primary"
  @click="handleLogin"
>
  登录
</el-button>
```

**Step 2: 保存并验证**

预期结果：样式更新成功

**Step 3: 提交**

```bash
git add frontend/src/views/auth/Login.vue
git commit -m "style: Login 页面应用新按钮样式"
```

---

## 任务 14: 更新注册页面应用新样式

**Files:**
- Modify: `frontend/src/views/auth/Register.vue`

**Step 1: 更新注册按钮**

找到注册按钮（约第 65-73 行）：

```vue
<el-button
  type="primary"
  size="large"
  :loading="authStore.loading"
  class="w-full btn-primary"
  @click="handleRegister"
>
  注册
</el-button>
```

**Step 2: 保存并验证**

预期结果：样式更新成功

**Step 3: 提交**

```bash
git add frontend/src/views/auth/Register.vue
git commit -m "style: Register 页面应用新按钮样式"
```

---

## 任务 15: 测试验证

**Files:**
- None (验证任务)

**Step 1: 启动开发服务器**

运行：
```bash
cd frontend
npm run dev
```

预期结果：开发服务器启动成功，无编译错误

**Step 2: 逐一验证页面**

在浏览器中访问以下页面并验证：

1. **仪表盘** (`/dashboard`)
   - [ ] 按钮使用新样式（紫色背景）
   - [ ] 面包屑显示"仪表盘"
   - [ ] 内容宽度受限，居中显示

2. **文章列表** (`/articles`)
   - [ ] 搜索按钮使用新样式
   - [ ] 卡片内编辑/删除按钮使用 ghost 样式
   - [ ] 面包屑显示"仪表盘 > 文章管理"

3. **文章详情** (`/articles/1`)
   - [ ] 返回、编辑、删除按钮使用新样式
   - [ ] 面包屑正确显示路径

4. **创建文章** (`/articles/create`)
   - [ ] 导入/上传按钮使用新样式
   - [ ] 对话框按钮使用新样式

5. **标签管理** (`/tags`)
   - [ ] 创建按钮使用新样式
   - [ ] 编辑/删除按钮使用 ghost 样式

6. **用户管理** (`/users`)
   - [ ] 容器样式正确
   - [ ] 面包屑正确显示

7. **阅读统计** (`/reading-stats`)
   - [ ] 容器样式正确
   - [ ] 面包屑正确显示

8. **登录页** (`/login`)
   - [ ] 登录按钮使用新样式

9. **注册页** (`/register`)
   - [ ] 注册按钮使用新样式

**Step 3: 响应式测试**

调整浏览器窗口大小，验证：
- [ ] 面包屑在移动端正确显示
- [ ] 按钮在小屏幕上正常工作
- [ ] 内容在小屏幕上正确适配

**Step 4: 功能测试**

- [ ] 面包屑点击可正确跳转
- [ ] 所有按钮点击功能正常
- [ ] 表单提交正常

**Step 5: 创建测试验证文档**

如果有任何问题，记录到 `docs/plans/test-results.md`

**Step 6: 提交最终版本**

```bash
git add .
git commit -m "feat: 完成按钮样式和面包屑导航实施"
```

---

## 验收标准

完成所有任务后，应该满足以下标准：

### 样式一致性
- [x] 所有按钮符合 example_html 规范
- [x] 所有页面使用统一的容器类
- [x] 间距、圆角、阴影等样式统一

### 功能完整性
- [x] 面包屑显示完整路径
- [x] 面包屑可点击返回
- [x] 按钮样式正确应用到所有页面

### 响应式
- [x] 移动端面包屑正确显示
- [x] 按钮在移动端正常工作
- [x] 容器在小屏幕上正确适配

---

## 风险和注意事项

### Element Plus 样式覆盖
- **风险:** Element Plus 默认样式可能覆盖自定义类
- **解决:** 使用更高优先级选择器 `.el-button.btn-class`

### 路由配置遗漏
- **风险:** 某些路由没有配置 breadcrumb
- **解决:** 面包屑组件有默认回退逻辑，使用 route.meta.title

### 现有页面样式破坏
- **风险:** 添加容器类可能影响现有布局
- **解决:** 渐进式迁移，保留原有类名

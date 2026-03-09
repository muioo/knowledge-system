# 按钮样式和面包屑导航设计文档

**日期:** 2025-03-08
**状态:** 已批准
**方案:** 方案 A - 渐进式增强

---

## 概述

本设计旨在统一知识管理系统的按钮样式和导航体验，使其符合 example_html 目录中的设计规范。

主要包含：
1. 全局按钮样式系统
2. 完整层级面包屑导航
3. 统一的容器内容样式

---

## 一、按钮样式设计

### 1.1 按钮类型

| 类名 | 用途 | 样式特征 |
|------|------|----------|
| `.btn-primary` | 主要操作（保存、提交、登录） | indigo 背景 (#7459D9)，白色文字，圆角 10px |
| `.btn-outline` | 次要操作（取消、编辑） | 透明背景，边框，hover 变 indigo |
| `.btn-ghost` | 文字/图标按钮 | 透明背景，hover 浅灰背景 (#F8F9FE) |
| `.btn-danger` | 危险操作（删除、退出） | 红色背景或边框 (#FF7977) |

### 1.2 基础样式规范

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-family: var(--font-poppins);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}
```

### 1.3 使用方式

```vue
<!-- 主要按钮 -->
<el-button class="btn-primary" type="primary">保存</el-button>

<!-- 次要按钮 -->
<el-button class="btn-outline">取消</el-button>

<!-- 文字按钮 -->
<el-button class="btn-ghost" text>编辑</el-button>

<!-- 危险按钮 -->
<el-button class="btn-danger" type="danger">删除</el-button>
```

---

## 二、面包屑导航设计

### 2.1 位置和布局

```
┌─────────────────────────────────────────────────────────────┐
│ [≡] 仪表盘    [仪表盘 > 文章管理 > 文章列表]  🔍  🔔  用户  │
└─────────────────────────────────────────────────────────────┘
```

- **位置:** AppHeader 右侧，搜索框之前
- **对齐:** 垂直居中

### 2.2 样式规范

- **字体:** Poppins，12px
- **分隔符:** `>` 或 `/`，颜色 `var(--text-grey-50)` (#D0D1D2)
- **当前页面:** `var(--text-black)` (#11263C)，字重 700
- **可点击层级:** `var(--color-indigo)` (#7459D9)，hover 下划线

### 2.3 路由配置

```typescript
{
  path: '/articles',
  meta: {
    title: '文章管理',
    breadcrumb: {
      title: '文章管理',
      path: '/articles',
      parent: '/dashboard'
    }
  }
}
```

### 2.4 组件结构

```vue
<Breadcrumb>
  <BreadcrumbItem to="/dashboard">仪表盘</BreadcrumbItem>
  <BreadcrumbSeparator />
  <BreadcrumbItem to="/articles">文章管理</BreadcrumbItem>
  <BreadcrumbSeparator />
  <BreadcrumbItem current>文章列表</BreadcrumbItem>
</Breadcrumb>
```

---

## 三、容器内容调整

### 3.1 统一容器类

```css
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.content-section {
  margin-bottom: 24px;
}
```

### 3.2 间距规范

| 元素 | 间距值 |
|------|--------|
| 页面内边距 | `padding: 20px` |
| 卡片间距 | `gap: 20px` |
| 卡片内边距 | `padding: 20px` |
| 章节间距 | `margin-bottom: 24px` |

### 3.3 样式变量统一

```css
/* 卡片 */
.card {
  background: var(--bg-white);
  border-radius: var(--radius-lg); /* 15px */
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
}

/* 输入框 */
.input {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm); /* 4px */
  padding: 10px 16px;
  font-family: var(--font-poppins);
  font-size: 14px;
}

.input:focus {
  outline: none;
  border-color: var(--color-indigo);
}
```

### 3.4 内容组件样式

**表格:**
- 边框颜色: `var(--border-default)`
- 头背景: `var(--bg-tertiary)`
- Hover 行背景: `var(--bg-tertiary)`

**表单:**
- 标签宽度: 100px
- 标签对齐: right
- 必填标记: `var(--color-red)`

**列表:**
- 卡片样式: 统一 `.card` 类
- 间距: `gap: 20px`

---

## 四、实施计划

### 4.1 文件修改清单

| 文件 | 修改内容 | 优先级 |
|------|----------|--------|
| `frontend/src/styles/colors.css` | 添加按钮样式类、容器类 | 高 |
| `frontend/src/components/layout/AppHeader.vue` | 添加面包屑组件 | 高 |
| `frontend/src/router/index.ts` | 添加面包屑 meta 信息 | 高 |
| `frontend/src/views/dashboard/DashboardView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/article/ArticleListView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/article/ArticleDetailView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/article/ArticleCreateView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/tag/TagManageView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/user/UserManageView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/reading/ReadingStatsView.vue` | 应用新样式类 | 中 |
| `frontend/src/views/auth/Login.vue` | 应用新样式类 | 低 |
| `frontend/src/views/auth/Register.vue` | 应用新样式类 | 低 |

### 4.2 实施步骤

**阶段 1: 基础样式系统**
1. 在 `colors.css` 添加按钮样式类
2. 添加容器类
3. 添加内容组件样式

**阶段 2: 导航组件**
1. 创建 Breadcrumb 组件
2. 更新路由配置
3. 集成到 AppHeader

**阶段 3: 视图迁移**
1. 迁移 DashboardView
2. 迁移文章相关视图
3. 迁移其他视图

**阶段 4: 测试验证**
1. 功能测试
2. 样式一致性检查
3. 响应式测试

---

## 五、验收标准

### 5.1 样式一致性
- [ ] 所有按钮符合 example_html 规范
- [ ] 所有页面使用统一的容器类
- [ ] 间距、圆角、阴影等样式统一

### 5.2 功能完整性
- [ ] 面包屑显示完整路径
- [ ] 面包屑可点击返回
- [ ] 按钮样式正确应用

### 5.3 响应式
- [ ] 移动端面包屑正确显示
- [ ] 按钮在移动端正常工作
- [ ] 容器在小屏幕上正确适配

---

## 六、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Element Plus 样式冲突 | 中 | 使用更高优先级的选择器 |
| 路由配置遗漏 | 低 | 提供默认面包屑逻辑 |
| 现有页面样式破坏 | 中 | 渐进式迁移，保留原样式类 |

---

## 七、后续优化

1. 添加按钮加载状态样式
2. 支持按钮尺寸变体（small, large）
3. 添加动画效果增强
4. 支持自定义面包屑分隔符

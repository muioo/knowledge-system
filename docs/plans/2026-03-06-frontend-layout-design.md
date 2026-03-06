# 知识系统前端布局与页面设计方案

**日期：** 2026-03-06
**目标：** 实现知识系统前端的布局组件和文章管理相关页面
**方案：** 渐进式实现 - 先搭建布局框架，再实现功能页面

---

## 一、架构设计

### 1.1 整体架构

采用三层架构，借鉴现代管理后台的布局风格：

```
┌─────────────────────────────────────────┐
│           DashboardLayout               │
│  ┌──────────┬──────────────────────┐   │
│  │          │                      │   │
│  │ Sidebar  │   Main Content       │   │
│  │          │   ┌──────────────┐   │   │
│  │ - 首页   │   │   Header     │   │   │
│  │ - 文章   │   ├──────────────┤   │   │
│  │ - 标签   │   │              │   │   │
│  │ - 搜索   │   │  Router View │   │   │
│  │ - 设置   │   │              │   │   │
│  │          │   │              │   │   │
│  └──────────┴───┴──────────────┘   │   │
└─────────────────────────────────────────┘
```

### 1.2 布局组件结构

**DashboardLayout.vue**
- 负责整体布局框架
- 包含 Sidebar 和 Header
- 响应式设计（移动端可折叠侧边栏）

**Sidebar.vue**
- 左侧导航菜单
- 支持图标 + 文字
- 高亮当前路由
- 深色背景风格

**Header.vue**
- 顶部导航栏
- 包含：面包屑、搜索框、用户信息、通知
- 白色背景 + 操作按钮

### 1.3 样式设计

借鉴现代管理后台的视觉风格：
- **配色**：蓝色主题（Element Plus 默认蓝）+ 深色侧边栏（#001529）
- **圆角**：8px 卡片圆角
- **阴影**：轻微阴影效果（box-shadow）
- **间距**：16px/24px 标准间距
- **字体**：系统默认字体栈

---

## 二、组件设计

### 2.1 DashboardLayout 组件

**文件位置：** `frontend/src/components/layouts/DashboardLayout.vue`

**职责：**
- 提供整体布局框架
- 管理侧边栏展开/收起状态
- 响应式适配（桌面/移动端）

**核心功能：**
- 侧边栏宽度：展开 240px，收起 64px
- 移动端（<768px）：侧边栏变为抽屉模式
- 使用 Pinia uiStore 管理 UI 状态

### 2.2 Sidebar 组件

**文件位置：** `frontend/src/components/layouts/Sidebar.vue`

**导航菜单项：**
```
- Dashboard (首页) - icon: House
- Articles (文章管理) - icon: Document
  - Article List (文章列表)
  - Create Article (创建文章)
- Tags (标签管理) - icon: Collection
- Search (搜索) - icon: Search
- Reading History (阅读历史) - icon: Clock
- Settings (设置) - icon: Setting
```

**样式特点：**
- 深色背景（#001529）
- 选中项高亮（蓝色背景）
- 图标 + 文字布局
- 支持二级菜单折叠

### 2.3 Header 组件

**文件位置：** `frontend/src/components/layouts/Header.vue`

**包含元素：**
- 左侧：折叠按钮 + 面包屑导航
- 右侧：搜索框 + 通知图标 + 用户头像下拉菜单

**用户菜单：**
- 个人信息
- 退出登录

### 2.4 文章相关页面组件

**ArticleList.vue** (`frontend/src/views/articles/ArticleList.vue`)
- 文章列表展示（表格或卡片模式）
- 筛选：按标签、按作者、按时间
- 分页
- 操作：查看、编辑、删除

**ArticleForm.vue** (`frontend/src/views/articles/ArticleForm.vue`)
- 创建/编辑文章表单
- 字段：标题、内容、摘要、标签、来源URL、关键词
- Markdown 编辑器或富文本编辑器
- 表单验证

---

## 三、数据流设计

### 3.1 状态管理（Pinia Stores）

**已有的 Stores：**
- ✅ `authStore` - 用户认证状态
- ✅ `articleStore` - 文章数据管理
- ✅ `tagStore` - 标签数据管理
- ✅ `uiStore` - UI 状态（侧边栏展开/收起等）

### 3.2 页面数据流

**文章列表页面流程：**
```
用户访问 /articles
  ↓
ArticleList.vue 组件挂载
  ↓
调用 articleStore.fetchArticles()
  ↓
API 请求 → 后端返回数据
  ↓
Store 更新状态
  ↓
组件响应式更新视图
```

**文章创建/编辑流程：**
```
用户填写表单
  ↓
表单验证（Element Plus rules）
  ↓
提交 → articleStore.createArticle() / updateArticle()
  ↓
API 请求成功
  ↓
显示成功消息 → 跳转到文章详情页
```

### 3.3 路由配置

**需要添加的路由：**
- `/` - Dashboard（需要认证）
- `/articles` - 文章列表（需要认证）
- `/articles/create` - 创建文章（需要认证）
- `/articles/:id` - 文章详情（需要认证）
- `/articles/:id/edit` - 编辑文章（需要认证 + 权限检查）
- `/login` - 登录页（已有）

**路由守卫逻辑：**
- 检查 `authStore.isAuthenticated`
- 未登录 → 重定向到 `/login`
- 已登录 → 允许访问

---

## 四、错误处理与测试

### 4.1 错误处理策略

**API 层错误处理：**
- 已有 `utils/request.ts` 封装了 axios 拦截器
- 统一处理：401 未授权 → 跳转登录
- 统一处理：403 无权限 → 显示错误提示
- 统一处理：500 服务器错误 → 显示友好错误信息

**组件层错误处理：**
- 使用 `try-catch` 包裹异步操作
- 使用 `ElMessage.error()` 显示错误提示
- 加载状态：`loading` 状态变量
- 错误状态：`error` 状态变量用于显示错误信息

**表单验证：**
- Element Plus 表单验证规则
- 必填字段、格式验证、长度限制
- 实时验证反馈

### 4.2 测试策略

**集成测试：**
- 手动测试关键用户流程：
  1. 登录 → 查看文章列表 → 查看文章详情
  2. 创建文章 → 编辑文章 → 删除文章
  3. 标签筛选 → 搜索功能

**浏览器兼容性：**
- 主要支持：Chrome、Firefox、Safari、Edge（最新版本）
- 响应式测试：桌面端（>1024px）、平板（768-1024px）、移动端（<768px）

### 4.3 性能优化

- 路由懒加载
- 图片懒加载（如需要）
- 分页加载（避免一次加载大量数据）
- Element Plus 按需引入（已配置 unplugin-vue-components）

---

## 五、实施顺序

### 阶段 1：布局组件（优先级：高）
1. 创建 DashboardLayout.vue
2. 创建 Sidebar.vue
3. 创建 Header.vue
4. 配置路由使用 DashboardLayout

### 阶段 2：文章列表页面（优先级：高）
1. 创建 ArticleList.vue
2. 实现文章列表展示
3. 实现筛选和分页功能

### 阶段 3：文章表单页面（优先级：高）
1. 创建 ArticleForm.vue
2. 实现创建文章功能
3. 实现编辑文章功能

### 阶段 4：完善文章详情页面（优先级：中）
1. 将现有 ArticleDetail.vue 集成到 DashboardLayout
2. 优化样式和交互

---

## 六、技术栈

- **框架：** Vue 3.4 + TypeScript 5.3
- **状态管理：** Pinia 2.1
- **路由：** Vue Router 4.2
- **UI 组件库：** Element Plus 2.5
- **图标：** @element-plus/icons-vue 2.3
- **HTTP 客户端：** Axios 1.6
- **构建工具：** Vite 5.0
- **样式：** Sass + Tailwind CSS

---

## 七、设计原则

1. **YAGNI（You Aren't Gonna Need It）**：只实现当前需要的功能，避免过度设计
2. **响应式优先**：确保在各种设备上都有良好的用户体验
3. **一致性**：保持 UI 风格和交互模式的一致性
4. **可维护性**：代码结构清晰，组件职责单一
5. **性能优化**：合理使用懒加载和分页，避免性能问题

---

**设计完成日期：** 2026-03-06
**下一步：** 创建详细的实施计划（Implementation Plan）

<template>
  <div class="app-sidebar" :class="{ collapsed }">
    <!-- Logo 区域 -->
    <div class="logo-section">
      <router-link to="/dashboard" class="logo-link" title="知识管理系统">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none">
            <rect width="40" height="40" rx="12" fill="var(--color-indigo)"/>
            <path d="M12 10 L12 30 L28 30 L28 10 Z" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 10 L16 26 L24 26 L24 10" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M16 16 L24 16" fill="none" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <path d="M16 20 L24 20" fill="none" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <transition name="fade">
          <span v-if="!collapsed" class="logo-text">知识管理系统</span>
        </transition>
      </router-link>
      <div class="logo-spacer"></div>
    </div>

    <!-- 导航菜单 -->
    <nav class="menu-items">
      <template v-for="item in menuItems" :key="item.index">
        <!-- 普通菜单项 -->
        <router-link
          v-if="!item.children"
          :to="item.index"
          class="menu-item"
          :class="{ active: activeMenu === item.index }"
          :title="collapsed ? item.title : ''"
        >
          <div class="menu-content">
            <div class="menu-icon-wrapper" :class="item.colorClass">
              <component :is="item.icon" />
            </div>
            <transition name="fade">
              <span v-if="!collapsed" class="menu-title">{{ item.title }}</span>
            </transition>
          </div>
        </router-link>

        <!-- 有子菜单的项（文章管理） -->
        <div v-else class="menu-item-group">
          <div
            class="menu-item menu-item-parent"
            :class="{ active: isArticleMenuActive }"
            @click="handleArticleMenuClick"
          >
            <div class="menu-content">
              <div class="menu-icon-wrapper" :class="item.colorClass">
                <component :is="item.icon" />
              </div>
              <transition name="fade">
                <span v-if="!collapsed" class="menu-title">{{ item.title }}</span>
              </transition>
            </div>
            <transition name="fade">
              <el-icon v-if="!collapsed" class="submenu-arrow" :class="{ expanded: articleSubmenuExpanded }">
                <ArrowDown />
              </el-icon>
            </transition>
          </div>

          <!-- 子菜单：标签列表 -->
          <transition name="submenu">
            <div v-if="articleSubmenuExpanded && !collapsed" class="submenu">
              <div
                v-for="tag in tags"
                :key="tag.id"
                class="submenu-item"
                :class="{ active: activeTagId === tag.id }"
                @click="goToTagArticles(tag)"
              >
                <div class="tag-color-dot" :style="{ backgroundColor: tag.color }"></div>
                <span class="submenu-title">{{ tag.name }}</span>
                <span class="article-count">({{ tag.article_count || 0 }})</span>
              </div>
              <div v-if="tags.length === 0" class="submenu-empty">
                暂无标签
              </div>
            </div>
          </transition>
        </div>
      </template>
    </nav>

    <!-- 用户信息（底部） -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar-circle">
          <span class="user-initials">{{ userInitials }}</span>
        </div>
        <transition name="fade">
          <div v-if="!collapsed" class="user-details">
            <div class="user-name">{{ userName }}</div>
            <div class="user-role">{{ userRole }}</div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { ArrowDown } from '@element-plus/icons-vue'
import {
  DataAnalysis,
  Document,
  Plus,
  PriceTag,
  TrendCharts,
  UserFilled,
} from '@element-plus/icons-vue'
import { tagApi } from '@/api/tag'
import type { Tag } from '@/types/tag'
import { ElMessage } from 'element-plus'

interface Props {
  collapsed?: boolean
}

const { collapsed = false } = defineProps<Props>()

// 路由
const route = useRoute()
const router = useRouter()

// 用户状态
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// 标签列表
const tags = ref<Tag[]>([])

// 文章子菜单展开状态
const articleSubmenuExpanded = ref(false)

// 当前激活的标签ID
const activeTagId = computed(() => {
  const tagId = route.query.tag_id as string
  return tagId ? parseInt(tagId) : null
})

// 判断文章菜单是否激活
const isArticleMenuActive = computed(() => {
  const path = route.path
  return path === '/articles'
})

// 当有标签被选中时，自动展开子菜单
watch(activeTagId, (newTagId) => {
  if (newTagId) {
    articleSubmenuExpanded.value = true
  }
}, { immediate: true })

// 菜单项配置
const menuItems = computed(() => {
  const items = [
    {
      index: '/dashboard',
      title: '仪表盘',
      icon: DataAnalysis,
      colorClass: 'orange',
    },
    {
      index: '/articles',
      title: '文章管理',
      icon: Document,
      colorClass: 'blue',
      hasChildren: true,
      children: 'articles', // 标记这个菜单项有子菜单
    },
    {
      index: '/articles/create',
      title: '创建文章',
      icon: Plus,
      colorClass: 'green',
    },
    {
      index: '/tags',
      title: '标签管理',
      icon: PriceTag,
      colorClass: 'yellow',
    },
    {
      index: '/reading-stats',
      title: '阅读统计',
      icon: TrendCharts,
      colorClass: 'pink',
    },
  ]

  // 如果是管理员，添加用户管理
  if (user.value?.role === 'admin') {
    items.splice(4, 0, {
      index: '/users',
      title: '用户管理',
      icon: UserFilled,
      colorClass: 'red',
    })
  }

  return items
})

// 当前激活的菜单
const activeMenu = computed(() => {
  const path = route.path
  // 文章详情页高亮文章列表
  if (path.startsWith('/articles/') && path !== '/articles/create' && !path.match(/^\/articles\/\d+$/)) {
    return '/articles'
  }
  // 文章详情页也高亮文章列表
  if (path.match(/^\/articles\/\d+$/)) {
    return '/articles'
  }
  return path
})

// 用户首字母缩写
const userInitials = computed(() => {
  const username = user.value?.username || 'U'
  return username.slice(0, 2).toUpperCase()
})

// 用户名
const userName = computed(() => {
  return user.value?.username || '用户'
})

// 用户角色
const userRole = computed(() => {
  return user.value?.role === 'admin' ? '管理员' : '普通用户'
})

// 处理文章菜单点击
function handleArticleMenuClick() {
  if (activeTagId.value) {
    // 如果有选中的标签，清除标签筛选并跳转到文章列表
    router.push('/articles')
  } else {
    // 否则切换子菜单展开状态
    articleSubmenuExpanded.value = !articleSubmenuExpanded.value
  }
}

// 跳转到标签文章列表
function goToTagArticles(tag: Tag) {
  router.push({
    path: '/articles',
    query: { tag_id: tag.id.toString() }
  })
}

// 加载标签列表
async function loadTags() {
  try {
    const res = await tagApi.getList()
    tags.value = res.data
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

// 初始化
onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
  height: 100vh;
  background: var(--bg-white);
  padding: 10px 12px;
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.app-sidebar.collapsed {
  width: 80px;
}

/* Logo 区域 */
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  width: 100%;
}

.logo-link {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  text-decoration: none;
  width: 100%;
  padding: 8px;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  font-family: var(--font-dinpro);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-black);
  white-space: nowrap;
  overflow: hidden;
}

.logo-spacer {
  width: 100%;
  height: 2px;
  background: linear-gradient(180deg, rgba(238, 236, 250, 0) 0%, rgba(249, 249, 249, 1) 51%, rgba(238, 236, 250, 0) 100%);
  margin: 10px 0;
}

.collapsed .logo-spacer {
  width: 40px;
}

/* 导航菜单 */
.menu-items {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 4px;
  width: 100%;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.menu-item-group {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 8px;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.2s ease;
  border-radius: var(--radius-md);
}

.menu-item-parent {
  justify-content: space-between;
}

.menu-item:hover {
  background: var(--bg-tertiary);
}

.menu-item.active {
  background: var(--bg-tertiary);
}

.menu-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.menu-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon-wrapper svg {
  width: 24px;
  height: 24px;
  stroke: currentColor;
  stroke-width: 2;
  fill: none;
}

.menu-title {
  font-family: var(--font-dinpro);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-black);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 子菜单箭头 */
.submenu-arrow {
  font-size: 12px;
  color: var(--text-grey-40);
  transition: transform 0.3s ease;
}

.submenu-arrow.expanded {
  transform: rotate(180deg);
}

/* 子菜单 */
.submenu {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
}

.submenu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  padding-left: 40px;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: background 0.2s ease;
}

.submenu-item:hover {
  background: var(--bg-tertiary);
}

.submenu-item.active {
  background: var(--bg-tertiary);
}

.tag-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.submenu-title {
  font-family: var(--font-dinpro);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-black);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-count {
  font-size: 12px;
  color: var(--text-grey-40);
  flex-shrink: 0;
}

.submenu-empty {
  padding: 12px;
  font-size: 12px;
  color: var(--text-grey-40);
  text-align: center;
}

/* 子菜单过渡动画 */
.submenu-enter-active,
.submenu-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.submenu-enter-from,
.submenu-leave-to {
  max-height: 0;
  opacity: 0;
}

.submenu-enter-to,
.submenu-leave-from {
  max-height: 500px;
  opacity: 1;
}

/* 颜色变体 */
.menu-icon-wrapper.orange {
  background: rgba(247, 147, 26, 0.1);
}
.menu-icon-wrapper.orange svg {
  color: var(--color-orange);
}

.menu-icon-wrapper.blue {
  background: rgba(31, 141, 237, 0.1);
}
.menu-icon-wrapper.blue svg {
  color: var(--color-blue);
}

.menu-icon-wrapper.red {
  background: rgba(255, 121, 119, 0.1);
}
.menu-icon-wrapper.red svg {
  color: var(--color-red);
}

.menu-icon-wrapper.green {
  background: rgba(43, 222, 115, 0.1);
}
.menu-icon-wrapper.green svg {
  color: var(--color-green);
}

.menu-icon-wrapper.yellow {
  background: rgba(255, 232, 18, 0.1);
}
.menu-icon-wrapper.yellow svg {
  color: var(--color-yellow);
}

.menu-icon-wrapper.pink {
  background: rgba(250, 71, 120, 0.1);
}
.menu-icon-wrapper.pink svg {
  color: var(--color-pink);
}

/* 底部用户信息 */
.sidebar-footer {
  margin-top: auto;
  width: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.user-avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-indigo);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.user-initials {
  font-family: var(--font-dinpro);
  font-size: 14px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.user-name {
  font-family: var(--font-dinpro);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-black);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: var(--text-grey-40);
  white-space: nowrap;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 767px) {
  .app-sidebar {
    width: 80px;
  }

  .app-sidebar.collapsed {
    width: 80px;
  }

  .logo-text,
  .menu-title,
  .user-details {
    display: none;
  }
}
</style>

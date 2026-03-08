<template>
  <div class="app-sidebar">
    <!-- Logo 区域 -->
    <div class="sidebar-logo">
      <router-link to="/dashboard" class="logo-link">
        <el-icon :size="32" color="#409eff">
          <Reading />
        </el-icon>
        <span v-if="!collapsed" class="logo-text">知识管理系统</span>
      </router-link>
    </div>

    <!-- 导航菜单 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :unique-opened="true"
      @select="handleMenuSelect"
      class="sidebar-menu"
    >
      <el-menu-item index="/dashboard">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>仪表盘</template>
      </el-menu-item>

      <el-menu-item index="/articles">
        <el-icon><Document /></el-icon>
        <template #title>文章管理</template>
      </el-menu-item>

      <el-menu-item index="/articles/create">
        <el-icon><Plus /></el-icon>
        <template #title>创建文章</template>
      </el-menu-item>

      <el-menu-item index="/tags">
        <el-icon><PriceTag /></el-icon>
        <template #title>标签管理</template>
      </el-menu-item>

      <el-menu-item v-if="isAdmin" index="/users">
        <el-icon><UserFilled /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>

      <el-menu-item index="/reading-stats">
        <el-icon><TrendCharts /></el-icon>
        <template #title>阅读统计</template>
      </el-menu-item>
    </el-menu>

    <!-- 用户信息（底部） -->
    <div v-if="!collapsed" class="sidebar-user">
      <el-avatar :size="40" :src="userAvatar">
        <el-icon><User /></el-icon>
      </el-avatar>
      <div class="user-info">
        <div class="user-name">{{ userName }}</div>
        <div class="user-role">{{ userRole }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import {
  Reading,
  DataAnalysis,
  Document,
  PriceTag,
  TrendCharts,
  User,
  UserFilled,
  Plus,
} from '@element-plus/icons-vue'

interface Props {
  collapsed?: boolean
}

const { collapsed } = withDefaults(defineProps<Props>(), {
  collapsed: false,
})

// 路由
const route = useRoute()
const router = useRouter()

// 用户状态
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// 菜单选择处理
function handleMenuSelect(index: string) {
  router.push(index)
}

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

// 用户名
const userName = computed(() => user.value?.username || '未登录')

// 用户角色
const userRole = computed(() => {
  if (!user.value) return ''
  return user.value.role === 'admin' ? '管理员' : '普通用户'
})

// 是否是管理员
const isAdmin = computed(() => {
  return user.value?.role === 'admin'
})

// 用户头像
const userAvatar = computed(() => {
  // 这里可以返回用户的头像URL
  // 目前使用默认头像
  return ''
})
</script>

<style scoped>
.app-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 200px;
  flex-shrink: 0;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 16px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  transition: opacity 0.2s;
}

.logo-link:hover {
  opacity: 0.8;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.user-info {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

/* 响应式设计 */
@media (max-width: 767px) {
  .sidebar-user {
    display: none;
  }
}
</style>

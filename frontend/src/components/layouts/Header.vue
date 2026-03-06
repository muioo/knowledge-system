<template>
  <header class="app-header">
    <div class="header-left">
      <!-- 折叠按钮 -->
      <el-button
        :icon="uiStore.sidebarCollapsed ? Expand : Fold"
        circle
        @click="uiStore.toggleSidebar()"
      />

      <!-- 面包屑导航 -->
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item
          v-for="item in breadcrumbs"
          :key="item.path"
          :to="item.path"
        >
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <!-- 搜索框 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索文章..."
        :prefix-icon="Search"
        class="search-input"
        @keyup.enter="handleSearch"
      />

      <!-- 通知图标 -->
      <el-badge :hidden="true" :value="0" class="notification">
        <el-button :icon="Bell" circle />
      </el-badge>

      <!-- 用户下拉菜单 -->
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar :icon="UserFilled" />
          <span class="username">{{ authStore.user?.username || '用户' }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人信息</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Expand, Fold, Search, Bell, UserFilled } from '@element-plus/icons-vue'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const authStore = useAuthStore()

// 搜索关键词
const searchKeyword = ref('')

// 面包屑映射
const breadcrumbMap: Record<string, string> = {
  '/': '首页',
  '/articles': '文章列表',
  '/articles/create': '创建文章',
  '/tags': '标签管理',
  '/search': '搜索',
  '/history': '阅读历史',
  '/settings': '设置'
}

// 生成面包屑
const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean)
  const items = [{ path: '/', title: '首页' }]

  let currentPath = ''
  for (const path of paths) {
    currentPath += `/${path}`
    const title = breadcrumbMap[currentPath]
    if (title) {
      items.push({ path: currentPath, title })
    }
  }

  return items
})

// 处理搜索
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchKeyword.value.trim())}`)
    searchKeyword.value = ''
  }
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  if (command === 'profile') {
    router.push('/settings')
  } else if (command === 'logout') {
    await authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background-color: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .breadcrumb {
      font-size: 14px;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .search-input {
      width: 240px;
    }

    .notification {
      cursor: pointer;
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 4px;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      .username {
        font-size: 14px;
        color: #333;
      }
    }
  }
}
</style>

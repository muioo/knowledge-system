<template>
  <div class="app-header">
    <!-- 左侧：折叠按钮 + 页面标题 -->
    <div class="header-left">
      <el-button :icon="collapsed ? Expand : Fold" text @click="$emit('toggle-sidebar')" />
      <h1 class="page-title">{{ currentPageTitle }}</h1>
    </div>

    <!-- 右侧：搜索 + 通知 + 用户菜单 -->
    <div class="header-right">
      <!-- 搜索框 -->
      <div class="header-search">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文章..."
          :prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
        />
      </div>

      <!-- 通知 -->
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="header-badge">
        <el-button :icon="Bell" text />
      </el-badge>

      <!-- 用户菜单 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-dropdown">
          <el-avatar :size="32" :src="userAvatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <span class="username">{{ userName }}</span>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              <span>个人资料</span>
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              <span>设置</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import {
  Fold,
  Expand,
  Search,
  Bell,
  User,
  ArrowDown,
  Setting,
  SwitchButton,
} from '@element-plus/icons-vue'

interface Props {
  sidebarCollapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sidebarCollapsed: false,
})

defineEmits<{
  'toggle-sidebar': []
}>()

// 路由
const route = useRoute()
const router = useRouter()

// 用户状态
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// 搜索关键词
const searchKeyword = ref('')

// 未读通知数量
const unreadCount = ref(0)

// 侧边栏是否折叠
const collapsed = computed(() => props.sidebarCollapsed)

// 当前页面标题
const currentPageTitle = computed(() => {
  return (route.meta?.title as string) || '知识管理系统'
})

// 用户名
const userName = computed(() => user.value?.username || '用户')

// 用户头像
const userAvatar = computed(() => {
  // 这里可以返回用户的头像URL
  return ''
})

// 搜索处理
function handleSearch() {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  router.push({
    path: '/search',
    query: { q: searchKeyword.value },
  })
}

// 下拉菜单命令处理
function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录
function handleLogout() {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px; /* 固定高度 */
  padding: 0 24px;
  background: #ffffff; /* 添加背景色 */
  border-bottom: 1px solid #e5e7eb; /* 添加底边框 */
  flex-shrink: 0; /* 防止被压缩 */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-search {
  width: 240px;
}

.header-badge {
  margin-right: 8px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-dropdown:hover {
  background: #f3f4f6;
}

.username {
  font-size: 14px;
  color: #1f2937;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 12px;
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 1023px) {
  .app-header {
    padding: 0 16px;
  }

  .header-search {
    width: 180px;
  }

  .username {
    display: none;
  }
}

@media (max-width: 767px) {
  .page-title {
    font-size: 16px;
  }

  .header-search {
    width: 140px;
  }

  .header-badge {
    display: none;
  }
}
</style>

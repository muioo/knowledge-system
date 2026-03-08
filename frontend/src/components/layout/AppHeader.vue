<template>
  <div class="app-header">
    <!-- 左侧：折叠按钮 + 面包屑导航 -->
    <div class="header-left">
      <el-button :icon="Reading" text class="toggle-btn" :class="{ 'is-collapsed': collapsed }" @click="$emit('toggle-sidebar')" />
      <AppBreadcrumb />
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
  Reading,
  Search,
  Bell,
  User,
  ArrowDown,
  Setting,
  SwitchButton,
} from '@element-plus/icons-vue'
import AppBreadcrumb from './AppBreadcrumb.vue'

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
  height: 82px;
  padding: 0 35px;
  background: var(--bg-white);
  position: relative;
  flex-shrink: 0;
}

.app-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--text-black);
  border-radius: 2px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-search {
  width: 240px;
}

.header-badge {
  margin-right: 0;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.2s;
}

.user-dropdown:hover {
  background: var(--bg-tertiary);
}

.username {
  font-family: var(--font-dinpro);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-black);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-grey-40);
}

/* 折叠按钮样式 */
.toggle-btn {
  transition: transform 0.3s ease;
}

.toggle-btn.is-collapsed {
  transform: rotate(180deg);
}

/* 响应式设计 */
@media (max-width: 1023px) {
  .app-header {
    padding: 0 24px;
  }

  .header-search {
    width: 180px;
  }

  .username {
    max-width: 80px;
  }
}

@media (max-width: 767px) {
  .app-header {
    height: 64px;
    padding: 0 16px;
  }

  .header-search {
    width: 140px;
  }

  .username {
    display: none;
  }

  .header-badge {
    display: none;
  }
}
</style>

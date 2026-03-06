<template>
  <aside class="sidebar" :class="{ collapsed }">
    <!-- Logo Area -->
    <div class="logo-area">
      <div class="logo-content">
        <el-icon class="logo-icon" :size="28">
          <Reading />
        </el-icon>
        <transition name="fade">
          <span v-if="!collapsed" class="logo-text">知识系统</span>
        </transition>
      </div>
    </div>

    <!-- Navigation Menu -->
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :unique-opened="true"
      background-color="#001529"
      text-color="#ffffff"
      active-text-color="#1890ff"
      class="sidebar-menu"
      router
    >
      <!-- 首页 -->
      <el-menu-item index="/">
        <el-icon><House /></el-icon>
        <template #title>首页</template>
      </el-menu-item>

      <!-- 文章管理 -->
      <el-sub-menu index="articles">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>文章管理</span>
        </template>
        <el-menu-item index="/articles">文章列表</el-menu-item>
        <el-menu-item index="/articles/create">创建文章</el-menu-item>
      </el-sub-menu>

      <!-- 标签管理 -->
      <el-menu-item index="/tags">
        <el-icon><Collection /></el-icon>
        <template #title>标签管理</template>
      </el-menu-item>

      <!-- 搜索 -->
      <el-menu-item index="/search">
        <el-icon><Search /></el-icon>
        <template #title>搜索</template>
      </el-menu-item>

      <!-- 阅读历史 -->
      <el-menu-item index="/history">
        <el-icon><Clock /></el-icon>
        <template #title>阅读历史</template>
      </el-menu-item>

      <!-- 设置 -->
      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <template #title>设置</template>
      </el-menu-item>
    </el-menu>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface Props {
  collapsed: boolean
}

defineProps<Props>()

const route = useRoute()

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  const path = route.path

  // 文章相关路由
  if (path.startsWith('/articles')) {
    return path
  }

  // 其他路由直接返回路径
  return path
})
</script>

<style scoped lang="scss">
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 240px;
  height: 100vh;
  background-color: #001529;
  transition: width 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;

  &.collapsed {
    width: 64px;
  }
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0 16px;
}

.logo-content {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #ffffff;
}

.logo-icon {
  color: #1890ff;
  flex-shrink: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;

  &:not(.el-menu--collapse) {
    width: 240px;
  }

  // 菜单项高度
  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    height: 48px;
    line-height: 48px;
  }

  // 子菜单项样式
  :deep(.el-menu-item) {
    &:hover {
      background-color: rgba(24, 144, 255, 0.1) !important;
    }

    &.is-active {
      background-color: rgba(24, 144, 255, 0.2) !important;
    }
  }

  // 子菜单标题样式
  :deep(.el-sub-menu__title) {
    &:hover {
      background-color: rgba(24, 144, 255, 0.1) !important;
    }
  }

  // 子菜单展开后的背景
  :deep(.el-menu--inline) {
    background-color: #000c17 !important;
  }

  // 滚动条样式
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 3px;

    &:hover {
      background-color: rgba(255, 255, 255, 0.3);
    }
  }

  &::-webkit-scrollbar-track {
    background-color: transparent;
  }
}

// Fade 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 响应式设计 - 移动端
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);

    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
}
</style>

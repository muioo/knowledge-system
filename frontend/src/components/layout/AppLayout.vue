<template>
  <div class="app-layout">
    <el-container class="layout-container">
      <!-- 左侧导航 -->
      <el-aside
        :width="sidebarWidth"
        class="layout-sidebar"
        :class="{ 'is-collapsed': isSidebarCollapsed }"
      >
        <AppSidebar :collapsed="isSidebarCollapsed" />
      </el-aside>

      <!-- 中间主内容区 -->
      <el-container class="layout-main">
        <!-- 顶部栏 -->
        <el-header height="60px" class="layout-header">
          <AppHeader
            :sidebar-collapsed="isSidebarCollapsed"
            @toggle-sidebar="toggleSidebar"
          />
        </el-header>

        <!-- 内容区 + 右侧统计面板 -->
        <el-container class="layout-content-wrapper">
          <!-- 主内容区 -->
          <el-main class="layout-content">
            <router-view v-slot="{ Component, route }">
              <transition name="fade" mode="out-in">
                <component :is="Component" :key="route.path" />
              </transition>
            </router-view>
          </el-main>

          <!-- 右侧统计面板 -->
          <el-aside
            v-if="showStatsPanel"
            width="300px"
            class="layout-stats"
          >
            <AppStatsPanel />
          </el-aside>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import AppStatsPanel from './AppStatsPanel.vue'

// 侧边栏状态
const isSidebarCollapsed = ref(false)

// 响应式断点
const windowWidth = ref(window.innerWidth)

// 是否显示右侧统计面板
const showStatsPanel = computed(() => windowWidth.value >= 1280)

// 侧边栏宽度
const sidebarWidth = computed(() => (isSidebarCollapsed.value ? '64px' : '200px'))

// 切换侧边栏
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 监听窗口大小变化
function handleResize() {
  windowWidth.value = window.innerWidth
  // 小屏幕时自动收起侧边栏
  if (windowWidth.value < 768) {
    isSidebarCollapsed.value = true
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize() // 初始化
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.app-layout {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.layout-container {
  height: 100%;
}

.layout-sidebar {
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  transition: width 0.3s ease;
  overflow: hidden;
}

.layout-sidebar.is-collapsed {
  width: 64px !important;
}

.layout-main {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-header {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0;
  line-height: 60px;
  height: 60px;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

.layout-content-wrapper {
  flex: 1;
  overflow: hidden;
}

.layout-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f9fafb;
}

.layout-stats {
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  overflow-y: auto;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 1279px) {
  .layout-stats {
    display: none;
  }
}

@media (max-width: 767px) {
  .layout-content {
    padding: 16px;
  }

  .layout-sidebar {
    position: absolute;
    z-index: 1000;
    height: 100%;
  }

  .layout-sidebar.is-collapsed {
    width: 0 !important;
    border-right: none;
  }
}
</style>

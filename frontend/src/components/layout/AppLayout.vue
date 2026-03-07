<template>
  <div class="app-layout flex min-h-screen bg-gray-50">
    <AppSidebar :collapsed="isSidebarCollapsed" />
    <main class="main-content flex-1 flex flex-col">
      <AppHeader :sidebar-collapsed="isSidebarCollapsed" @toggle-sidebar="toggleSidebar" />
      <div class="content-area flex-1 p-0">
        <router-view v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'

// 侧边栏状态
const isSidebarCollapsed = ref(false)

// 切换侧边栏
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 监听窗口大小变化
function handleResize() {
  // 小屏幕时自动收起侧边栏
  if (window.innerWidth < 768) {
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
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  overflow-y: auto;
}

.content-area {
  max-width: 100%;
  margin: 0 auto;
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
@media (max-width: 767px) {
  .content-area {
    padding: 8px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .content-area {
    padding: 12px;
  }
}
</style>

<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <Sidebar :collapsed="uiStore.sidebarCollapsed" />

    <!-- Main Container -->
    <div
      class="main-container"
      :class="{ 'sidebar-collapsed': uiStore.sidebarCollapsed }"
    >
      <!-- Header -->
      <Header />

      <!-- Content Area -->
      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import Sidebar from '@/components/layouts/Sidebar.vue'
import Header from '@/components/layouts/Header.vue'

const uiStore = useUiStore()

onMounted(() => {
  uiStore.initializeSidebar()
})
</script>

<style scoped lang="scss">
.dashboard-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  background-color: #f5f5f5;

  &.sidebar-collapsed {
    margin-left: 64px;
  }
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

// 响应式设计 - 移动端
@media (max-width: 768px) {
  .main-container {
    margin-left: 0;

    &.sidebar-collapsed {
      margin-left: 0;
    }
  }
}
</style>

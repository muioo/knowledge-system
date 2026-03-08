<template>
  <div class="app-breadcrumb" v-if="items.length > 0">
    <template v-for="(item, index) in items" :key="index">
      <router-link
        :to="item.path"
        class="breadcrumb-item"
        :class="{ 'is-current': index === items.length - 1 }"
      >
        {{ item.title }}
      </router-link>
      <span v-if="index < items.length - 1" class="breadcrumb-separator">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </span>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  title: string
  path: string
}

const route = useRoute()

// 构建面包屑层级
const items = computed<BreadcrumbItem[]>(() => {
  const breadcrumbs: BreadcrumbItem[] = []

  // 添加仪表盘作为根
  breadcrumbs.push({
    title: '仪表盘',
    path: '/dashboard'
  })

  // 从当前路由向上遍历，构建完整路径
  const currentMeta = route.meta as any

  if (currentMeta.breadcrumb) {
    // 如果当前页面有 breadcrumb 配置，直接使用
    breadcrumbs.push({
      title: currentMeta.breadcrumb.title,
      path: route.path
    })
  } else if (route.path !== '/dashboard') {
    // 否则使用路由 meta.title
    breadcrumbs.push({
      title: (route.meta?.title as string) || '未知页面',
      path: route.path
    })
  }

  return breadcrumbs
})
</script>

<style scoped>
.app-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-poppins);
  font-size: 14px;
}

.breadcrumb-item {
  color: var(--color-indigo);
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-item.is-current {
  color: var(--text-black);
  font-weight: 700;
  pointer-events: none;
}

.breadcrumb-separator {
  display: flex;
  align-items: center;
  color: var(--text-grey-50);
}

.breadcrumb-separator svg {
  width: 14px;
  height: 14px;
}

/* 响应式 */
@media (max-width: 767px) {
  .app-breadcrumb {
    font-size: 12px;
  }
}
</style>

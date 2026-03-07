<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">仪表盘</h1>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#3B82F6"><Document /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">文章总数</p>
            <p class="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#10B981"><PriceTag /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">标签数量</p>
            <p class="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#8B5CF6"><View /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">已读文章</p>
            <p class="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#F59E0B"><Clock /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">阅读时长</p>
            <p class="text-2xl font-bold text-gray-900">0小时</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="card">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">快捷操作</h2>
      <div class="flex gap-4">
        <el-button type="primary" :icon="Plus" @click="$router.push('/articles/create')">
          创建文章
        </el-button>
        <el-button :icon="FolderOpened" @click="$router.push('/articles')">
          浏览文章
        </el-button>
        <el-button :icon="PriceTag" @click="$router.push('/tags')">
          管理标签
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document, PriceTag, View, Clock, Plus, FolderOpened } from '@element-plus/icons-vue'
</script>

<style scoped>
.card {
  background: #ffffff;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  border: 1px solid #e5e7eb;
}

.card:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}
</style>

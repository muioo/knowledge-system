<template>
  <div class="article-list-view">
    <el-card class="placeholder-card">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" :size="80">
          <Document />
        </el-icon>
        <h2 class="placeholder-title">文章列表</h2>
        <p class="placeholder-description">文章浏览与管理功能开发中...</p>
        <div class="placeholder-features">
          <el-tag v-for="feature in features" :key="feature" class="feature-tag">
            {{ feature }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document } from '@element-plus/icons-vue'

const features = ref([
  '搜索与筛选',
  '批量操作',
  '分类浏览',
  '状态管理'
])
</script>

<style scoped>
.article-list-view {
  width: 100%;
}

.placeholder-card {
  max-width: 600px;
  margin: 40px auto;
}

.placeholder-content {
  text-align: center;
  padding: 40px 20px;
}

.placeholder-icon {
  color: #67c23a;
  margin-bottom: 24px;
}

.placeholder-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.placeholder-description {
  font-size: 16px;
  color: #606266;
  margin-bottom: 32px;
}

.placeholder-features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.feature-tag {
  font-size: 14px;
}
</style>

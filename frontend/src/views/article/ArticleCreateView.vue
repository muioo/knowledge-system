<template>
  <div class="article-create-view">
    <el-card class="placeholder-card">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" :size="80">
          <EditPen />
        </el-icon>
        <h2 class="placeholder-title">创建文章</h2>
        <p class="placeholder-description">文章编辑与发布功能开发中...</p>
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
import { EditPen } from '@element-plus/icons-vue'

const features = ref([
  'Markdown编辑',
  '本地文件上传',
  'URL导入',
  'AI自动提取'
])
</script>

<style scoped>
.article-create-view {
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
  color: #f56c6c;
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

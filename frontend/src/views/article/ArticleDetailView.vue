<template>
  <div class="article-detail-view">
    <el-card class="placeholder-card">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" :size="80">
          <Reading />
        </el-icon>
        <h2 class="placeholder-title">文章详情</h2>
        <p class="placeholder-description">文章内容展示与编辑功能开发中...</p>
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
import { Reading } from '@element-plus/icons-vue'

const features = ref(['Markdown渲染', '目录导航', '相关推荐', '评论互动'])
</script>

<style scoped>
.article-detail-view {
  width: 100%;
  padding: 16px;
}

.placeholder-card {
  max-width: 100%;
  margin: 0;
}

.placeholder-content {
  text-align: center;
  padding: 40px 20px;
}

.placeholder-icon {
  color: #e6a23c;
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

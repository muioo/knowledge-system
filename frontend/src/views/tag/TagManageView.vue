<template>
  <div class="tag-manage-view">
    <el-card class="placeholder-card">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" :size="80">
          <PriceTag />
        </el-icon>
        <h2 class="placeholder-title">标签管理</h2>
        <p class="placeholder-description">标签组织与管理功能开发中...</p>
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
import { PriceTag } from '@element-plus/icons-vue'

const features = ref(['标签创建', '标签编辑', '标签合并', '批量管理'])
</script>

<style scoped>
.tag-manage-view {
  width: 100%;
  padding: 16px;
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
  color: #909399;
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

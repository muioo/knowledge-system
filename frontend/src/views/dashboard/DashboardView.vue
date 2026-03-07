<template>
  <div class="dashboard-view">
    <el-card class="placeholder-card">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" :size="80">
          <DataAnalysis />
        </el-icon>
        <h2 class="placeholder-title">仪表盘</h2>
        <p class="placeholder-description">数据统计与可视化功能开发中...</p>
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
import { DataAnalysis } from '@element-plus/icons-vue'

const features = ref([
  '文章统计',
  '标签分析',
  '最近活动',
  '数据趋势'
])
</script>

<style scoped>
.dashboard-view {
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
  color: #409eff;
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

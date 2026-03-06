<template>
  <div class="tag-list-page">
    <div class="page-header">
      <h1 class="page-title">标签管理</h1>
      <el-button type="primary" :icon="Plus" @click="handleCreate">
        创建标签
      </el-button>
    </div>

    <el-card v-if="tagStore.loading" class="loading-card">
      <el-skeleton :rows="5" animated />
    </el-card>

    <el-alert
      v-else-if="tagStore.error"
      type="error"
      :title="tagStore.error"
      :closable="false"
      show-icon
    />

    <div v-else-if="tagStore.tags.length > 0" class="tag-grid">
      <el-card
        v-for="tag in tagStore.tags"
        :key="tag.id"
        class="tag-card"
        shadow="hover"
      >
        <div class="tag-content">
          <el-tag :color="tag.color" size="large" class="tag-display">
            {{ tag.name }}
          </el-tag>
          <div class="tag-meta">
            <span>{{ tag.article_count || 0 }} 篇文章</span>
          </div>
        </div>
        <div class="tag-actions">
          <el-button size="small" :icon="Edit" @click="handleEdit(tag)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            :icon="Delete"
            @click="handleDelete(tag)"
          >
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="暂无标签" />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { useTagStore } from '../../stores/tag'
import type { Tag } from '../../types'

const tagStore = useTagStore()

onMounted(async () => {
  await loadTags()
})

async function loadTags(): Promise<void> {
  try {
    await tagStore.fetchTags()
  } catch (error) {
    console.error('Failed to load tags:', error)
  }
}

function handleCreate(): void {
  ElMessage.info('创建标签功能待实现')
}

function handleEdit(tag: Tag): void {
  ElMessage.info(`编辑标签: ${tag.name}`)
}

async function handleDelete(tag: Tag): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.name}" 吗？`,
      '删除标签',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    ElMessage.info('删除标签功能待实现')
  } catch (error) {
    // User cancelled
  }
}
</script>

<style scoped lang="scss">
.tag-list-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.loading-card {
  margin-bottom: 24px;
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.tag-card {
  cursor: default;

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.tag-content {
  margin-bottom: 16px;
}

.tag-display {
  font-size: 16px;
  padding: 8px 16px;
  margin-bottom: 12px;
}

.tag-meta {
  font-size: 14px;
  color: #666;
}

.tag-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .tag-grid {
    grid-template-columns: 1fr;
  }
}
</style>

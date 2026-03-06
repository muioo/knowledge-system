<template>
  <div class="history-page">
    <div class="page-header">
      <h1 class="page-title">阅读历史</h1>
      <el-button :icon="Delete" @click="handleClearAll">
        清空历史
      </el-button>
    </div>

    <el-card v-if="loading" class="loading-card">
      <el-skeleton :rows="5" animated />
    </el-card>

    <div v-else-if="historyList.length > 0" class="history-list">
      <el-card
        v-for="item in historyList"
        :key="item.id"
        class="history-card"
        shadow="hover"
        @click="handleView(item.article_id)"
      >
        <div class="history-content">
          <h3 class="history-title">{{ item.article_title }}</h3>
          <div class="history-meta">
            <span><el-icon><Clock /></el-icon> {{ formatDate(item.read_at) }}</span>
          </div>
        </div>
        <el-button
          type="danger"
          size="small"
          :icon="Delete"
          circle
          @click.stop="handleDelete(item.id)"
        />
      </el-card>
    </div>

    <el-empty v-else description="暂无阅读历史" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Clock } from '@element-plus/icons-vue'
import { formatDate } from '../../utils/date'

const router = useRouter()

interface HistoryItem {
  id: number
  article_id: number
  article_title: string
  read_at: string
}

const historyList = ref<HistoryItem[]>([])
const loading = ref(false)

onMounted(() => {
  loadHistory()
})

function loadHistory(): void {
  loading.value = true
  // TODO: 从 API 或 localStorage 加载阅读历史
  setTimeout(() => {
    historyList.value = []
    loading.value = false
  }, 500)
}

function handleView(articleId: number): void {
  router.push(`/articles/${articleId}`)
}

function handleDelete(id: number): void {
  ElMessage.info(`删除历史记录 ${id} 功能待实现`)
}

async function handleClearAll(): Promise<void> {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有阅读历史吗？',
      '清空历史',
      {
        confirmButtonText: '清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    ElMessage.info('清空历史功能待实现')
  } catch (error) {
    // User cancelled
  }
}
</script>

<style scoped lang="scss">
.history-page {
  max-width: 900px;
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

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  cursor: pointer;
  transition: transform 0.2s;

  :deep(.el-card__body) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
  }

  &:hover {
    transform: translateX(4px);
  }
}

.history-content {
  flex: 1;
}

.history-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 8px 0;
}

.history-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #999;

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}
</style>

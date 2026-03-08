<template>
  <div class="reading-stats-view content-wrapper">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">阅读统计</h1>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#3B82F6"><Document /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">总阅读次数</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalViews }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#10B981"><Clock /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">总阅读时长</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalReadingHours }}小时</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <el-icon :size="24" color="#8B5CF6"><TrendCharts /></el-icon>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-600">已读文章</p>
            <p class="text-2xl font-bold text-gray-900">{{ readArticles }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 选项卡 -->
    <el-tabs v-model="activeTab" class="stats-tabs">
      <el-tab-pane label="阅读历史" name="history">
        <div v-loading="loading" class="content-area">
          <div v-if="readingHistory.length === 0 && !loading" class="empty-state">
            <el-icon :size="64" color="#9CA3AF"><Clock /></el-icon>
            <p class="text-gray-500 mt-4">暂无阅读记录</p>
          </div>

          <div v-else class="history-list">
            <div
              v-for="item in readingHistory"
              :key="item.id"
              class="history-item"
              @click="goToArticle(item.article_id)"
            >
              <div class="history-main">
                <h3 class="article-title">{{ item.article_title }}</h3>
                <div class="history-meta">
                  <span class="text-gray-500 text-sm">
                    开始时间: {{ formatDateTime(item.started_at) }}
                  </span>
                  <span v-if="item.ended_at" class="text-gray-500 text-sm">
                    结束时间: {{ formatDateTime(item.ended_at) }}
                  </span>
                </div>
              </div>
              <div class="history-stats">
                <div class="stat-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatDuration(item.reading_duration) }}</span>
                </div>
                <div v-if="item.reading_progress > 0" class="stat-item">
                  <el-icon><TrendCharts /></el-icon>
                  <span>进度: {{ item.reading_progress }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="historyPagination.total > 0" class="pagination-container">
            <el-pagination
              v-model:current-page="historyPagination.page"
              v-model:page-size="historyPagination.size"
              :total="historyPagination.total"
              layout="total, prev, pager, next"
              @current-change="loadHistory"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="文章统计" name="stats">
        <div v-loading="loadingStats" class="content-area">
          <div v-if="articleStats.length === 0 && !loadingStats" class="empty-state">
            <el-icon :size="64" color="#9CA3AF"><Document /></el-icon>
            <p class="text-gray-500 mt-4">暂无统计数据</p>
          </div>

          <div v-else class="stats-list">
            <div
              v-for="item in articleStats"
              :key="item.article_id"
              class="stat-item"
              @click="goToArticle(item.article_id)"
            >
              <div class="stat-main">
                <h3 class="article-title">{{ item.article_title }}</h3>
                <p class="text-gray-500 text-sm">
                  最后阅读: {{ item.last_read_at ? formatDateTime(item.last_read_at) : '未阅读' }}
                </p>
              </div>
              <div class="stat-values">
                <div class="stat-value">
                  <span class="label">阅读次数</span>
                  <span class="value">{{ item.total_views }}</span>
                </div>
                <div class="stat-value">
                  <span class="label">阅读时长</span>
                  <span class="value">{{ formatDuration(item.total_duration) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="statsPagination.total > 0" class="pagination-container">
            <el-pagination
              v-model:current-page="statsPagination.page"
              v-model:page-size="statsPagination.size"
              :total="statsPagination.total"
              layout="total, prev, pager, next"
              @current-change="loadStats"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Clock, TrendCharts } from '@element-plus/icons-vue'
import { getReadingHistory, getReadingStats } from '@/api/reading'
import type { ReadingHistory, ReadingStats } from '@/api/reading'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 当前选项卡
const activeTab = ref('history')

// 数据
const loading = ref(false)
const loadingStats = ref(false)
const readingHistory = ref<ReadingHistory[]>([])
const articleStats = ref<ReadingStats[]>([])

// 分页
const historyPagination = ref({
  page: 1,
  size: 20,
  total: 0
})

const statsPagination = ref({
  page: 1,
  size: 20,
  total: 0
})

// 统计数据
const totalViews = computed(() => {
  return articleStats.value.reduce((sum, item) => sum + item.total_views, 0)
})

const totalReadingHours = computed(() => {
  const totalSeconds = articleStats.value.reduce((sum, item) => sum + item.total_duration, 0)
  return Math.round(totalSeconds / 3600)
})

const readArticles = computed(() => {
  return articleStats.value.filter(item => item.total_views > 0).length
})

// 加载阅读历史
async function loadHistory() {
  loading.value = true
  try {
    const res = await getReadingHistory({
      page: historyPagination.value.page,
      size: historyPagination.value.size
    })
    readingHistory.value = res.data.items
    historyPagination.value.total = res.data.total
  } catch (error) {
    console.error('加载阅读历史失败:', error)
    ElMessage.error('加载阅读历史失败')
  } finally {
    loading.value = false
  }
}

// 加载文章统计
async function loadStats() {
  loadingStats.value = true
  try {
    const res = await getReadingStats({
      page: statsPagination.value.page,
      size: statsPagination.value.size
    })
    articleStats.value = res.data.items
    statsPagination.value.total = res.data.total
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loadingStats.value = false
  }
}

// 格式化日期时间
function formatDateTime(dateStr: string | null) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化时长
function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// 跳转到文章详情
function goToArticle(articleId: number) {
  router.push(`/articles/${articleId}`)
}

onMounted(() => {
  loadHistory()
  loadStats()
})
</script>

<style scoped>
.reading-stats-view {
  width: 100%;
  padding: 20px;
}

.card {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
}

.grid {
  display: grid;
  gap: 20px;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .md\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.stats-tabs {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
}

.content-area {
  min-height: 400px;
}

.history-list,
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-item,
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover,
.stat-item:hover {
  background: var(--bg-secondary);
  border-color: var(--color-indigo);
}

.article-title {
  font-family: var(--font-dinpro);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-black);
  margin: 0 0 4px 0;
}

.history-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-meta span {
  color: var(--text-grey-40);
  font-size: 14px;
}

.history-stats,
.stat-values {
  display: flex;
  gap: 16px;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--text-grey-40);
}

.stat-value {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.stat-value .label {
  font-size: 12px;
  color: var(--text-grey-40);
}

.stat-value .value {
  font-family: var(--font-dinpro);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-black);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-state p {
  color: var(--text-grey-40);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>

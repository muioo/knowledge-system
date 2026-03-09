<template>
  <div class="dashboard-container content-wrapper">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">仪表盘</h1>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p class="mt-4">加载中...</p>
    </div>

    <!-- 内容区域 -->
    <div v-else class="dashboard-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon stat-icon-blue">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <p class="stat-label">文章总数</p>
            <p class="stat-value">{{ stats.totalArticles }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-green">
            <el-icon :size="28"><PriceTag /></el-icon>
          </div>
          <div class="stat-content">
            <p class="stat-label">标签数量</p>
            <p class="stat-value">{{ stats.totalTags }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-purple">
            <el-icon :size="28"><View /></el-icon>
          </div>
          <div class="stat-content">
            <p class="stat-label">已读文章</p>
            <p class="stat-value">{{ stats.readArticles }}</p>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-orange">
            <el-icon :size="28"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <p class="stat-label">阅读时长</p>
            <p class="stat-value">{{ stats.readingHours }}<span class="stat-unit">小时</span></p>
          </div>
        </div>
      </div>

      <!-- 主要内容区域：最近阅读 + 快捷操作 -->
      <div class="main-content">
        <!-- 最近阅读 -->
        <div v-if="recentReadings.length > 0" class="content-card">
          <h2 class="card-title">最近阅读</h2>
          <div class="reading-list">
            <div
              v-for="item in recentReadings"
              :key="item.article_id"
              class="reading-item"
              @click="goToArticle(item.article_id)"
            >
              <div class="reading-info">
                <p class="reading-title">{{ item.article_title }}</p>
                <p class="reading-date">{{ formatDate(item.last_read_at) }}</p>
              </div>
              <div class="reading-stats">
                <p class="reading-count">{{ item.total_views }} 次阅读</p>
                <p class="reading-duration">{{ formatDuration(item.total_duration) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="content-card">
          <h2 class="card-title">快捷操作</h2>
          <div class="quick-actions">
            <div class="action-item" @click="$router.push('/articles/create')">
              <div class="action-icon action-icon-primary">
                <el-icon :size="24"><Plus /></el-icon>
              </div>
              <span>创建文章</span>
            </div>
            <div class="action-item" @click="$router.push('/articles')">
              <div class="action-icon action-icon-blue">
                <el-icon :size="24"><FolderOpened /></el-icon>
              </div>
              <span>浏览文章</span>
            </div>
            <div class="action-item" @click="$router.push('/tags')">
              <div class="action-icon action-icon-green">
                <el-icon :size="24"><PriceTag /></el-icon>
              </div>
              <span>管理标签</span>
            </div>
            <div class="action-item" @click="$router.push('/reading-stats')">
              <div class="action-icon action-icon-purple">
                <el-icon :size="24"><TrendCharts /></el-icon>
              </div>
              <span>阅读统计</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, PriceTag, View, Clock, Plus, FolderOpened, TrendCharts, Loading } from '@element-plus/icons-vue'
import { articleApi } from '@/api/article'
import { tagApi } from '@/api/tag'
import { getReadingStats } from '@/api/reading'
import type { ReadingStats } from '@/api/reading'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 加载状态
const loading = ref(true)

// 统计数据
const stats = ref({
  totalArticles: 0,
  totalTags: 0,
  readArticles: 0,
  readingHours: 0
})

// 最近阅读
const recentReadings = ref<ReadingStats[]>([])

// 加载统计数据
async function loadStats() {
  loading.value = true

  try {
    console.log('开始加载统计数据...')

    // 加载文章统计
    console.log('加载文章列表...')
    const articlesRes = await articleApi.getList({ page: 1, size: 1 })
    console.log('文章响应:', articlesRes)
    stats.value.totalArticles = articlesRes.data.total

    // 加载标签统计
    console.log('加载标签列表...')
    const tagsRes = await tagApi.getList()
    console.log('标签响应:', tagsRes)
    stats.value.totalTags = tagsRes.data.length

    // 加载阅读统计
    console.log('加载阅读统计...')
    const readingRes = await getReadingStats({ page: 1, size: 10 })
    console.log('阅读统计响应:', readingRes)
    stats.value.readArticles = readingRes.data.total
    recentReadings.value = readingRes.data.items

    // 计算总阅读时长
    const totalDuration = readingRes.data.items.reduce((sum, item) => sum + item.total_duration, 0)
    stats.value.readingHours = Math.round(totalDuration / 3600)

    console.log('统计数据加载完成:', stats.value)
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载数据失败，请检查网络连接或后端服务')
  } finally {
    loading.value = false
  }
}

// 格式化日期
function formatDate(dateStr: string | null) {
  if (!dateStr) return '未阅读'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
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
  loadStats()
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-container > h1 {
  font-family: var(--font-dinpro);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-black);
  margin-bottom: 16px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0px 12px 24px 0px rgba(50, 50, 71, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-blue {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

.stat-icon-green {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.stat-icon-purple {
  background: rgba(139, 92, 246, 0.1);
  color: #8B5CF6;
}

.stat-icon-orange {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-family: var(--font-dinpro);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-grey-40);
  margin-bottom: 8px;
}

.stat-value {
  font-family: var(--font-dinpro);
  font-size: 28px;
  font-weight: 700;
  color: var(--text-black);
  line-height: 1;
}

.stat-unit {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-grey-40);
  margin-left: 4px;
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  min-height: 0;
}

.content-card {
  background: var(--bg-white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.card-title {
  font-family: var(--font-dinpro);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-black);
  margin-bottom: 20px;
}

/* 最近阅读列表 */
.reading-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  min-height: 0;
}

.reading-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.reading-item:hover {
  background: rgba(116, 89, 217, 0.05);
  transform: translateX(4px);
}

.reading-info {
  flex: 1;
  min-width: 0;
}

.reading-title {
  font-family: var(--font-dinpro);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-black);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reading-date {
  font-size: 13px;
  color: var(--text-grey-40);
}

.reading-stats {
  text-align: right;
  flex-shrink: 0;
  margin-left: 16px;
}

.reading-count {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-black);
  margin-bottom: 2px;
}

.reading-duration {
  font-size: 13px;
  color: var(--text-grey-40);
}

/* 快捷操作 */
.quick-actions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-dinpro);
  font-size: 15px;
  font-weight: 500;
  color: var(--text-black);
}

.action-item:hover {
  background: rgba(116, 89, 217, 0.05);
  transform: translateX(4px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.action-icon-primary {
  background: var(--color-indigo);
  color: white;
}

.action-icon-blue {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

.action-icon-green {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.action-icon-purple {
  background: rgba(139, 92, 246, 0.1);
  color: #8B5CF6;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 20px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>

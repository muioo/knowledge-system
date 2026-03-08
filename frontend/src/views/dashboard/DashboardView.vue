<template>
  <div class="dashboard-container content-wrapper">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">仪表盘</h1>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p class="mt-4">加载中...</p>
    </div>

    <!-- 内容区域 -->
    <div v-else>
      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="card">
          <div class="flex items-center">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <el-icon :size="24" color="#3B82F6"><Document /></el-icon>
            </div>
            <div class="ml-4">
              <p class="text-sm text-gray-600">文章总数</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.totalArticles }}</p>
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
              <p class="text-2xl font-bold text-gray-900">{{ stats.totalTags }}</p>
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
              <p class="text-2xl font-bold text-gray-900">{{ stats.readArticles }}</p>
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
              <p class="text-2xl font-bold text-gray-900">{{ stats.readingHours }}小时</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近阅读 -->
      <div v-if="recentReadings.length > 0" class="card">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">最近阅读</h2>
        <div class="space-y-2">
          <div
            v-for="item in recentReadings"
            :key="item.article_id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
            @click="goToArticle(item.article_id)"
          >
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ item.article_title }}</p>
              <p class="text-sm text-gray-500">{{ formatDate(item.last_read_at) }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-600">{{ item.total_views }} 次阅读</p>
              <p class="text-sm text-gray-500">{{ formatDuration(item.total_duration) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="card">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">快捷操作</h2>
        <div class="flex flex-wrap gap-3">
          <el-button type="primary" :icon="Plus" @click="$router.push('/articles/create')" class="btn-primary">
            创建文章
          </el-button>
          <el-button :icon="FolderOpened" @click="$router.push('/articles')" class="btn-outline">
            浏览文章
          </el-button>
          <el-button :icon="PriceTag" @click="$router.push('/tags')" class="btn-outline">
            管理标签
          </el-button>
          <el-button :icon="TrendCharts" @click="$router.push('/reading-stats')" class="btn-outline">
            阅读统计
          </el-button>
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
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.card {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0px 12px 24px 0px rgba(50, 50, 71, 0.1);
}

.grid {
  display: grid;
  gap: 20px;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}
</style>

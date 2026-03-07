<template>
  <div class="article-detail-view">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p class="mt-4">加载中...</p>
    </div>

    <div v-else-if="article" class="article-container">
      <!-- 返回按钮 -->
      <div class="header-actions">
        <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
        <div class="action-buttons">
          <el-button :icon="Edit" @click="handleEdit">编辑</el-button>
          <el-button :icon="Delete" type="danger" @click="confirmDelete">删除</el-button>
        </div>
      </div>

      <!-- 文章标题 -->
      <h1 class="article-title">{{ article.title }}</h1>

      <!-- 文章元信息 -->
      <div class="article-meta">
        <div class="tags">
          <el-tag
            v-for="tag in article.tags"
            :key="tag.id"
            :color="tag.color"
            size="small"
          >
            {{ tag.name }}
          </el-tag>
          <span v-if="article.tags.length === 0" class="text-gray-400 text-sm">无标签</span>
        </div>
        <div class="meta-info">
          <span class="text-gray-500">
            <el-icon><View /></el-icon> {{ article.view_count }} 次浏览
          </span>
          <span class="text-gray-500">
            {{ formatDate(article.created_at) }}
          </span>
        </div>
      </div>

      <!-- 文章摘要 -->
      <div v-if="article.summary" class="article-summary">
        <h3>摘要</h3>
        <p>{{ article.summary }}</p>
      </div>

      <!-- 关键词 -->
      <div v-if="article.keywords" class="article-keywords">
        <h3>关键词</h3>
        <div class="keywords-list">
          <el-tag
            v-for="(keyword, index) in keywordList"
            :key="index"
            type="info"
            size="small"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>

      <!-- 文章内容 -->
      <div class="article-content">
        <div v-if="article.html_content" v-html="article.html_content" class="html-content"></div>
        <div v-else class="no-content">
          <el-icon :size="48" color="#9CA3AF"><Document /></el-icon>
          <p class="text-gray-500 mt-2">暂无内容</p>
          <el-button type="primary" :icon="Edit" @click="handleEdit" class="mt-4">
            编辑文章
          </el-button>
        </div>
      </div>

      <!-- 来源信息 -->
      <div v-if="article.source_url || article.original_html_url" class="source-info">
        <h4>来源</h4>
        <a v-if="article.source_url" :href="article.source_url" target="_blank" class="source-link">
          {{ article.source_url }}
          <el-icon><TopRight /></el-icon>
        </a>
        <a v-else-if="article.original_html_url" :href="article.original_html_url" target="_blank" class="source-link">
          {{ article.original_html_url }}
          <el-icon><TopRight /></el-icon>
        </a>
      </div>
    </div>

    <div v-else class="error-container">
      <el-icon :size="64" color="#EF4444"><Warning /></el-icon>
      <h2 class="text-xl font-semibold mt-4">文章不存在</h2>
      <el-button type="primary" @click="$router.push('/articles')" class="mt-4">
        返回文章列表
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Loading,
  ArrowLeft,
  Edit,
  Delete,
  View,
  Document,
  Warning,
  TopRight,
} from '@element-plus/icons-vue'
import { articleApi } from '@/api/article'
import { startReading, endReading } from '@/api/reading'
import type { Article } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const article = ref<Article | null>(null)

// 阅读追踪
let readingStartTime: number | null = null
let readingSessionId: number | null = null

// 关键词列表
const keywordList = computed(() => {
  if (!article.value?.keywords) return []
  return article.value.keywords.split(',').map(k => k.trim()).filter(k => k)
})

// 开始阅读追踪
async function startReadingTracking() {
  if (!article.value) return

  readingStartTime = Date.now()
  try {
    const res = await startReading(article.value.id)
    readingSessionId = res.data.id
    console.log('开始阅读追踪:', readingSessionId)
  } catch (error) {
    console.error('开始阅读追踪失败:', error)
  }
}

// 结束阅读追踪
async function endReadingTracking() {
  if (!article.value || !readingStartTime) return

  const readingDuration = Math.floor((Date.now() - readingStartTime) / 1000) // 秒
  const readingProgress = 100 // 假设阅读完成

  try {
    await endReading(article.value.id, { reading_progress: readingProgress })
    console.log('结束阅读追踪:', { duration: readingDuration, progress: readingProgress })
  } catch (error) {
    console.error('结束阅读追踪失败:', error)
  }

  readingStartTime = null
  readingSessionId = null
}

// 加载文章详情
async function loadArticle() {
  const articleId = Number(route.params.id)
  if (!articleId) {
    ElMessage.error('无效的文章ID')
    router.push('/articles')
    return
  }

  loading.value = true
  try {
    const res = await articleApi.getDetail(articleId)
    article.value = res.data

    // 文章加载完成后开始阅读追踪
    await startReadingTracking()
  } catch (error) {
    console.error('加载文章失败:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

// 编辑文章
function handleEdit() {
  if (article.value) {
    router.push(`/articles/${article.value.id}/edit`)
  }
}

// 确认删除
function confirmDelete() {
  if (!article.value) return

  ElMessageBox.confirm(
    `确定要删除文章《${article.value.title}》吗？此操作不可撤销。`,
    '确认删除',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteArticle()
  }).catch(() => {
    // 用户取消
  })
}

// 删除文章
async function deleteArticle() {
  if (!article.value) return

  try {
    await articleApi.delete(article.value.id)
    ElMessage.success('删除成功')
    router.push('/articles')
  } catch (error: any) {
    console.error('删除文章失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadArticle()
})

// 页面卸载时结束阅读追踪
onUnmounted(() => {
  endReadingTracking()
})

// 监听页面可见性变化（用户切换标签页等）
document.addEventListener('visibilitychange', () => {
  if (document.hidden && readingStartTime) {
    // 页面隐藏时，可以考虑是否结束阅读追踪
    // 这里暂不处理，让用户离开页面时才结束
  }
})

// 监听用户离开页面
window.addEventListener('beforeunload', () => {
  if (readingStartTime) {
    // 使用sendBeacon确保数据发送
    const data = JSON.stringify({ reading_progress: 100 })
    navigator.sendBeacon(
      `/api/v1/reading/articles/${article.value?.id}/end`,
      new Blob([data], { type: 'application/json' })
    )
  }
})
</script>

<style scoped>
.article-detail-view {
  width: 100%;
  padding: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.article-container {
  background: #ffffff;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  border: 1px solid #e5e7eb;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.article-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-info {
  display: flex;
  gap: 16px;
  align-items: center;
}

.meta-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.article-summary,
.article-keywords,
.source-info {
  margin-bottom: 1.5rem;
}

.article-summary h3,
.article-keywords h3,
.source-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.75rem 0;
}

.article-summary p {
  color: #4b5563;
  line-height: 1.6;
  margin: 0;
}

.keywords-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.article-content {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.html-content {
  color: #374151;
  line-height: 1.8;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.html-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1rem 0;
  display: block;
}

.html-content :deep(h1),
.html-content :deep(h2),
.html-content :deep(h3),
.html-content :deep(h4),
.html-content :deep(h5),
.html-content :deep(h6) {
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #1f2937;
  line-height: 1.4;
}

.html-content :deep(p) {
  margin-bottom: 1rem;
}

.html-content :deep(ul),
.html-content :deep(ol) {
  margin-left: 2rem;
  margin-bottom: 1rem;
}

.html-content :deep(li) {
  margin-bottom: 0.5rem;
}

.html-content :deep(pre) {
  background: #1f2937;
  color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.html-content :deep(code) {
  background: #f3f4f6;
  color: #ef4444;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

.html-content :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}

.no-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.source-info {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px dashed #e5e7eb;
}

.source-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #3b82f6;
  text-decoration: none;
  word-break: break-all;
}

.source-link:hover {
  text-decoration: underline;
}
</style>

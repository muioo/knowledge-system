<template>
  <div class="article-detail-view content-wrapper">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p class="mt-4">加载中...</p>
    </div>

    <div v-else-if="article" class="article-container">
      <!-- 返回按钮 -->
      <div class="header-actions">
        <el-button :icon="ArrowLeft" @click="$router.back()" class="btn-outline">返回</el-button>
        <div class="action-buttons">
          <el-button :icon="Edit" @click="handleEdit" class="btn-primary">编辑</el-button>
          <el-button :icon="Delete" type="danger" @click="confirmDelete" class="btn-danger">删除</el-button>
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
          <el-button type="primary" :icon="Edit" @click="handleEdit" class="mt-4 btn-primary">
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
      <el-button type="primary" @click="$router.push('/articles')" class="mt-4 btn-primary">
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
  padding: 12px;
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
  background: var(--bg-white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.article-title {
  font-family: var(--font-yuanti);
  font-size: 26px;
  font-weight: 700;
  color: var(--text-black);
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-default);
  margin-bottom: 24px;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tags .el-tag {
  font-family: var(--font-dinpro);
  font-size: 13px;
  font-weight: 500;
  padding: 4px 10px;
  border: none;
  color: white !important;
}

.tags .el-tag.el-tag--light {
  border: none !important;
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
  color: var(--text-grey-40);
  font-size: 14px;
}

.article-summary,
.article-keywords,
.source-info {
  margin-bottom: 24px;
}

.article-summary h3,
.article-keywords h3,
.source-info h4 {
  font-family: var(--font-dinpro);
  font-size: 16px;
  font-weight: 700;
  color: var(--text-black);
  margin: 0 0 12px 0;
}

.article-summary p {
  color: var(--text-grey-40);
  line-height: 1.6;
  margin: 0;
}

.keywords-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.keywords-list .el-tag {
  font-family: var(--font-dinpro);
  font-size: 13px;
  font-weight: 500;
  padding: 4px 10px;
  border: none;
  background: rgba(116, 89, 217, 0.1) !important;
  color: var(--color-indigo) !important;
}

.article-content {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid var(--border-default);
}

.html-content {
  color: var(--text-black);
  line-height: 1.8;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.html-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: 16px 0;
  display: block;
}

.html-content :deep(h1),
.html-content :deep(h2),
.html-content :deep(h3),
.html-content :deep(h4),
.html-content :deep(h5),
.html-content :deep(h6) {
  font-family: var(--font-dinpro);
  font-weight: 700;
  margin-top: 24px;
  margin-bottom: 12px;
  color: var(--text-black);
  line-height: 1.4;
}

.html-content :deep(p) {
  margin-bottom: 16px;
  color: var(--text-black);
}

.html-content :deep(ul),
.html-content :deep(ol) {
  margin-left: 32px;
  margin-bottom: 16px;
}

.html-content :deep(li) {
  margin-bottom: 8px;
}

.html-content :deep(pre) {
  background: #F8F9FE;
  color: var(--text-black);
  padding: 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 16px 0;
  border: 1px solid var(--border-default);
}

.html-content :deep(code) {
  background: rgba(116, 89, 217, 0.1);
  color: var(--color-indigo);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: 0.875em;
  font-weight: 500;
}

.html-content :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.html-content :deep(a) {
  color: var(--color-indigo);
  text-decoration: none;
}

.html-content :deep(a:hover) {
  text-decoration: underline;
}

.no-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  text-align: center;
}

.no-content p {
  color: var(--text-grey-40);
}

.source-info {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px dashed var(--border-default);
}

.source-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--color-indigo);
  text-decoration: none;
  word-break: break-all;
}

.source-link:hover {
  text-decoration: underline;
}
</style>

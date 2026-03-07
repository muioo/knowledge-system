<template>
  <div class="app-stats-panel">
    <!-- 统计卡片 -->
    <div class="stats-section">
      <h3 class="section-title">统计概览</h3>

      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon stat-icon-primary">
            <el-icon :size="20"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalArticles }}</div>
            <div class="stat-label">文章总数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-success">
            <el-icon :size="20"><PriceTag /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalTags }}</div>
            <div class="stat-label">标签数量</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-warning">
            <el-icon :size="20"><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.articlesRead }}</div>
            <div class="stat-label">已读文章</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon stat-icon-info">
            <el-icon :size="20"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.readingTime }}h</div>
            <div class="stat-label">阅读时长</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签云 -->
    <div class="stats-section">
      <h3 class="section-title">热门标签</h3>
      <div class="tag-cloud">
        <el-tag
          v-for="tag in popularTags"
          :key="tag.id"
          :type="getTagType(tag.count)"
          effect="plain"
          class="tag-item"
          @click="handleTagClick(tag.name)"
        >
          {{ tag.name }} ({{ tag.count }})
        </el-tag>
      </div>
    </div>

    <!-- 最近阅读 -->
    <div class="stats-section">
      <h3 class="section-title">最近阅读</h3>
      <div class="recent-list">
        <div
          v-for="item in recentArticles"
          :key="item.id"
          class="recent-item"
          @click="handleArticleClick(item.id)"
        >
          <div class="recent-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="recent-content">
            <div class="recent-title">{{ item.title }}</div>
            <div class="recent-time">{{ formatTime(item.readAt) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 阅读进度 -->
    <div class="stats-section">
      <h3 class="section-title">阅读进度</h3>
      <div class="progress-list">
        <div v-for="item in readingProgress" :key="item.id" class="progress-item">
          <div class="progress-title">{{ item.title }}</div>
          <el-progress :percentage="item.progress" :stroke-width="8" :show-text="true" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, PriceTag, Reading, Clock } from '@element-plus/icons-vue'

const router = useRouter()

// 统计数据
const stats = ref({
  totalArticles: 0,
  totalTags: 0,
  articlesRead: 0,
  readingTime: 0,
})

// 热门标签
const popularTags = ref<Array<{ id: number; name: string; count: number }>>([])

// 最近阅读
const recentArticles = ref<Array<{ id: number; title: string; readAt: string }>>([])

// 阅读进度
const readingProgress = ref<Array<{ id: number; title: string; progress: number }>>([])

// 获取标签类型
function getTagType(count: number) {
  if (count >= 10) return 'danger'
  if (count >= 5) return 'warning'
  if (count >= 3) return 'success'
  return 'info'
}

// 格式化时间
function formatTime(time: string) {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 点击标签
function handleTagClick(tagName: string) {
  router.push({
    path: '/search',
    query: { tag: tagName },
  })
}

// 点击文章
function handleArticleClick(articleId: number) {
  router.push(`/articles/${articleId}`)
}

// 加载统计数据
async function loadStats() {
  try {
    // 这里应该调用 API 获取真实数据
    // 目前使用模拟数据
    stats.value = {
      totalArticles: 128,
      totalTags: 24,
      articlesRead: 86,
      readingTime: 42,
    }

    popularTags.value = [
      { id: 1, name: 'Vue.js', count: 15 },
      { id: 2, name: 'TypeScript', count: 12 },
      { id: 3, name: '前端开发', count: 10 },
      { id: 4, name: '性能优化', count: 8 },
      { id: 5, name: '架构设计', count: 6 },
      { id: 6, name: '最佳实践', count: 5 },
      { id: 7, name: '工具链', count: 4 },
      { id: 8, name: '测试', count: 3 },
    ]

    recentArticles.value = [
      {
        id: 1,
        title: 'Vue 3 组合式 API 最佳实践',
        readAt: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 2,
        title: 'TypeScript 高级类型技巧',
        readAt: new Date(Date.now() - 7200000).toISOString(),
      },
      { id: 3, title: '前端性能优化指南', readAt: new Date(Date.now() - 86400000).toISOString() },
      { id: 4, title: '微前端架构实践', readAt: new Date(Date.now() - 172800000).toISOString() },
    ]

    readingProgress.value = [
      { id: 1, title: '深入理解 Vue 响应式原理', progress: 75 },
      { id: 2, title: 'TypeScript 类型体操进阶', progress: 45 },
      { id: 3, title: 'Web 性能优化实战', progress: 30 },
    ]
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.app-stats-panel {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}

.stats-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  transition: all 0.2s;
}

.stat-card:hover {
  background: #f3f4f6;
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  flex-shrink: 0;
}

.stat-icon-primary {
  background: #dbeafe;
  color: #3b82f6;
}

.stat-icon-success {
  background: #d1fae5;
  color: #10b981;
}

.stat-icon-warning {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon-info {
  background: #e0e7ff;
  color: #6366f1;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* 标签云 */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  transform: scale(1.05);
}

/* 最近阅读 */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.recent-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.recent-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #e5e7eb;
  border-radius: 6px;
  color: #6b7280;
  flex-shrink: 0;
}

.recent-content {
  flex: 1;
  min-width: 0;
}

.recent-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-time {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* 阅读进度 */
.progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-title {
  font-size: 14px;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 滚动条样式 */
.app-stats-panel::-webkit-scrollbar {
  width: 6px;
}

.app-stats-panel::-webkit-scrollbar-track {
  background: transparent;
}

.app-stats-panel::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.app-stats-panel::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 响应式设计 */
@media (max-width: 1535px) {
  .app-stats-panel {
    padding: 16px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>

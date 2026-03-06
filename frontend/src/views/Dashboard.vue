<template>
  <div class="dashboard">
    <!-- 统计卡片区域 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="32">
                <Document />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ articleStore.pagination.total }}</div>
              <div class="stat-label">文章总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="32">
                <Collection />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ tagStore.tags.length }}</div>
              <div class="stat-label">标签总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="32">
                <View />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalViews }}</div>
              <div class="stat-label">总阅读量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="32">
                <TrendCharts />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayNewArticles }}</div>
              <div class="stat-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近文章和热门标签 -->
    <el-row :gutter="16" class="content-row">
      <!-- 最近文章列表 -->
      <el-col :xs="24" :md="16">
        <el-card class="section-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近文章</span>
            </div>
          </template>

          <!-- 加载状态 -->
          <div v-if="articleStore.loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>

          <!-- 错误状态 -->
          <el-empty
            v-else-if="articleStore.error"
            description="加载失败"
            :image-size="100"
          />

          <!-- 空状态 -->
          <el-empty
            v-else-if="!articleStore.hasArticles"
            description="暂无文章"
            :image-size="100"
          />

          <!-- 文章列表 -->
          <div v-else class="article-list">
            <div
              v-for="article in recentArticles"
              :key="article.id"
              class="article-item"
              @click="goToArticle(article.id)"
            >
              <div class="article-header">
                <h3 class="article-title">{{ article.title }}</h3>
                <span class="article-date">{{ formatDate(article.created_at, 'YYYY-MM-DD') }}</span>
              </div>
              <p class="article-summary">{{ article.summary || '暂无摘要' }}</p>
              <div class="article-tags">
                <el-tag
                  v-for="tag in article.tags"
                  :key="tag.id"
                  :type="getTagType(tag.color)"
                  size="small"
                  @click.stop="goToTagArticles(tag.id)"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 热门标签 -->
      <el-col :xs="24" :md="8">
        <el-card class="section-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">热门标签</span>
            </div>
          </template>

          <!-- 加载状态 -->
          <div v-if="tagStore.loading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>

          <!-- 错误状态 -->
          <el-empty
            v-else-if="tagStore.error"
            description="加载失败"
            :image-size="100"
          />

          <!-- 空状态 -->
          <el-empty
            v-else-if="!tagStore.hasTags"
            description="暂无标签"
            :image-size="100"
          />

          <!-- 标签列表 -->
          <div v-else class="tag-list">
            <div
              v-for="tag in popularTags"
              :key="tag.id"
              class="tag-item"
              @click="goToTagArticles(tag.id)"
            >
              <el-tag :type="getTagType(tag.color)" size="large">
                {{ tag.name }}
              </el-tag>
              <span class="tag-count">{{ tag.article_count }} 篇</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Collection, View, TrendCharts } from '@element-plus/icons-vue'
import { useArticleStore } from '../stores/article'
import { useTagStore } from '../stores/tag'
import { formatDate, isToday } from '../utils/date'
import type { Tag } from '../types'

const router = useRouter()
const articleStore = useArticleStore()
const tagStore = useTagStore()

// 最近文章（取前5篇）
const recentArticles = computed(() => articleStore.articles.slice(0, 5))

// 热门标签（按文章数量排序，取前10个）
const popularTags = computed(() => {
  return [...tagStore.tags]
    .sort((a, b) => (b.article_count || 0) - (a.article_count || 0))
    .slice(0, 10)
})

// 总阅读量
const totalViews = computed(() => {
  return articleStore.articles.reduce((sum, article) => sum + (article.views || 0), 0)
})

// 今日新增文章数
const todayNewArticles = computed(() => {
  return articleStore.articles.filter((article) => isToday(article.created_at)).length
})

/**
 * 获取标签类型（根据颜色映射到 Element Plus 的 type）
 */
function getTagType(color?: string): '' | 'success' | 'info' | 'warning' | 'danger' {
  if (!color) return ''

  const colorMap: Record<string, '' | 'success' | 'info' | 'warning' | 'danger'> = {
    blue: '',
    green: 'success',
    gray: 'info',
    yellow: 'warning',
    red: 'danger',
  }

  return colorMap[color] || ''
}

/**
 * 跳转到文章详情页
 */
function goToArticle(id: number): void {
  router.push(`/articles/${id}`)
}

/**
 * 跳转到标签文章列表页
 */
function goToTagArticles(tagId: number): void {
  router.push({
    path: '/articles',
    query: { tag: tagId },
  })
}

/**
 * 加载数据
 */
async function loadData(): Promise<void> {
  try {
    // 并行加载文章和标签数据
    await Promise.all([
      articleStore.fetchArticles({ page: 1, limit: 20 }),
      tagStore.fetchTags(),
    ])
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('Failed to load dashboard data:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);

  .stats-row {
    margin-bottom: 24px;
  }

  .stat-card {
    border-radius: 8px;
    margin-bottom: 16px;

    :deep(.el-card__body) {
      padding: 20px;
    }

    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .stat-icon {
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        flex-shrink: 0;
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
          line-height: 1.2;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }

    &:hover {
      transform: translateY(-2px);
      transition: transform 0.3s ease;
    }
  }

  .content-row {
    .section-card {
      border-radius: 8px;
      margin-bottom: 16px;

      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        .card-title {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
        }
      }

      .loading-container {
        padding: 20px 0;
      }
    }
  }

  // 文章列表样式
  .article-list {
    .article-item {
      padding: 16px;
      border-bottom: 1px solid #ebeef5;
      cursor: pointer;
      transition: background-color 0.3s ease;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background-color: #f5f7fa;
      }

      .article-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;

        .article-title {
          font-size: 16px;
          font-weight: 500;
          color: #303133;
          margin: 0;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .article-date {
          font-size: 12px;
          color: #909399;
          margin-left: 12px;
          flex-shrink: 0;
        }
      }

      .article-summary {
        font-size: 14px;
        color: #606266;
        margin: 0 0 12px 0;
        line-height: 1.6;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .article-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .el-tag {
          cursor: pointer;

          &:hover {
            opacity: 0.8;
          }
        }
      }
    }
  }

  // 标签列表样式
  .tag-list {
    .tag-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border-bottom: 1px solid #ebeef5;
      cursor: pointer;
      transition: background-color 0.3s ease;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background-color: #f5f7fa;
      }

      .el-tag {
        font-size: 14px;
      }

      .tag-count {
        font-size: 14px;
        color: #909399;
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;

    .stat-card {
      .stat-content {
        .stat-icon {
          width: 48px;
          height: 48px;

          .el-icon {
            font-size: 24px;
          }
        }

        .stat-info {
          .stat-value {
            font-size: 24px;
          }
        }
      }
    }

    .article-list {
      .article-item {
        padding: 12px;

        .article-header {
          flex-direction: column;
          align-items: flex-start;

          .article-date {
            margin-left: 0;
            margin-top: 4px;
          }
        }
      }
    }
  }
}
</style>

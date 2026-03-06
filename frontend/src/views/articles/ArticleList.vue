<template>
  <div class="article-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">文章列表</h1>
      <el-button type="primary" :icon="Plus" @click="handleCreate">
        创建文章
      </el-button>
    </div>

    <!-- 筛选表单 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索标题和内容"
            :prefix-icon="Search"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="filterForm.tagIds"
            multiple
            placeholder="选择标签"
            clearable
            style="width: 240px"
          >
            <el-option
              v-for="tag in tagStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-select
            v-model="filterForm.sortBy"
            placeholder="选择排序方式"
            style="width: 160px"
          >
            <el-option label="最新" value="created_at" />
            <el-option label="最热" value="view_count" />
            <el-option label="最多阅读" value="view_count" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 加载状态 -->
    <div v-if="articleStore.loading" class="skeleton-container">
      <el-skeleton v-for="i in 3" :key="i" :rows="5" animated />
    </div>

    <!-- 错误状态 -->
    <el-card v-else-if="articleStore.error" class="error-card">
      <el-result icon="error" title="加载失败" :sub-title="articleStore.error">
        <template #extra>
          <el-button type="primary" @click="loadArticles">重试</el-button>
        </template>
      </el-result>
    </el-card>

    <!-- 空数据状态 -->
    <el-card v-else-if="!articleStore.hasArticles" class="empty-card">
      <el-empty description="暂无文章">
        <el-button type="primary" @click="handleCreate">创建第一篇文章</el-button>
      </el-empty>
    </el-card>

    <!-- 文章卡片列表 -->
    <div v-else class="article-grid">
      <el-card
        v-for="article in articleStore.articles"
        :key="article.id"
        class="article-card"
        shadow="hover"
      >
        <!-- 文章标题 -->
        <h3 class="article-title" @click="handleView(article.id)">
          {{ article.title }}
        </h3>

        <!-- 文章摘要 -->
        <p class="article-summary">
          {{ truncateSummary(article.summary || article.content) }}
        </p>

        <!-- 标签列表 -->
        <div class="article-tags">
          <el-tag
            v-for="tag in article.tags"
            :key="tag.id"
            :type="getTagType(tag.id)"
            size="small"
            class="tag-item"
            @click="handleTagFilter(tag.id)"
          >
            {{ tag.name }}
          </el-tag>
        </div>

        <!-- 元信息 -->
        <div class="article-meta">
          <span class="meta-item">
            <el-icon><User /></el-icon>
            作者ID: {{ article.author_id }}
          </span>
          <span class="meta-item">
            <el-icon><View /></el-icon>
            {{ article.view_count }} 次阅读
          </span>
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            {{ formatDate(article.created_at, 'YYYY-MM-DD HH:mm') }}
          </span>
        </div>

        <!-- 操作按钮 -->
        <div class="article-actions">
          <el-button
            type="primary"
            :icon="View"
            size="small"
            @click="handleView(article.id)"
          >
            查看
          </el-button>
          <el-button
            v-if="canEdit(article)"
            type="warning"
            :icon="Edit"
            size="small"
            @click="handleEdit(article.id)"
          >
            编辑
          </el-button>
          <el-button
            v-if="canDelete(article)"
            type="danger"
            :icon="Delete"
            size="small"
            @click="handleDelete(article.id)"
          >
            删除
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 分页组件 -->
    <div v-if="articleStore.hasArticles" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="articleStore.pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  View,
  Edit,
  Delete,
  Clock,
  User,
} from '@element-plus/icons-vue'
import { useArticleStore } from '@/stores/article'
import { useTagStore } from '@/stores/tag'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/date'
import { canEditArticle, canDeleteArticle } from '@/utils/permission'
import type { Article } from '@/types'

const router = useRouter()
const articleStore = useArticleStore()
const tagStore = useTagStore()
const authStore = useAuthStore()

// 筛选表单
const filterForm = ref({
  keyword: '',
  tagIds: [] as number[],
  sortBy: 'created_at',
})

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 加载文章列表
async function loadArticles() {
  const params: any = {
    page: currentPage.value,
    limit: pageSize.value,
  }

  // 添加关键词搜索
  if (filterForm.value.keyword) {
    params.q = filterForm.value.keyword
  }

  // 添加标签筛选
  if (filterForm.value.tagIds.length > 0) {
    params.tags = filterForm.value.tagIds
  }

  // 添加排序
  if (filterForm.value.sortBy) {
    params.sort_by = filterForm.value.sortBy
    params.order = 'desc'
  }

  await articleStore.fetchArticles(params)
}

// 搜索
function handleSearch() {
  currentPage.value = 1
  loadArticles()
}

// 重置
function handleReset() {
  filterForm.value = {
    keyword: '',
    tagIds: [],
    sortBy: 'created_at',
  }
  currentPage.value = 1
  loadArticles()
}

// 创建文章
function handleCreate() {
  router.push('/articles/create')
}

// 查看文章
function handleView(id: number) {
  router.push(`/articles/${id}`)
}

// 编辑文章
function handleEdit(id: number) {
  router.push(`/articles/${id}/edit`)
}

// 删除文章
async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await articleStore.deleteArticle(id)
    ElMessage.success('删除成功')

    // 重新加载列表
    await loadArticles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 标签筛选
function handleTagFilter(tagId: number) {
  if (!filterForm.value.tagIds.includes(tagId)) {
    filterForm.value.tagIds = [tagId]
    handleSearch()
  }
}

// 分页变化
function handlePageChange(page: number) {
  currentPage.value = page
  loadArticles()
}

// 每页条数变化
function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadArticles()
}

// 截断摘要
function truncateSummary(text: string): string {
  if (!text) return ''
  return text.length > 200 ? text.substring(0, 200) + '...' : text
}

// 获取标签类型
function getTagType(tagId: number): 'success' | 'info' | 'warning' | 'danger' | '' {
  const types: Array<'success' | 'info' | 'warning' | 'danger' | ''> = ['success', 'info', 'warning', 'danger', '']
  return types[tagId % types.length]
}

// 权限检查
function canEdit(article: Article): boolean {
  return canEditArticle(article, authStore.userId ?? undefined)
}

function canDelete(article: Article): boolean {
  return canDeleteArticle(article, authStore.userId ?? undefined)
}

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadArticles(),
    tagStore.fetchTags(),
  ])
})
</script>

<style lang="scss" scoped>
.article-list-container {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0;
  }
}

.filter-card {
  margin-bottom: 24px;

  :deep(.el-card__body) {
    padding: 24px;
  }
}

.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.error-card,
.empty-card {
  margin-top: 24px;
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.article-card {
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  cursor: pointer;
  transition: color 0.3s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;

  &:hover {
    color: #409eff;
  }
}

.article-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 16px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  min-height: 24px;

  .tag-item {
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: scale(1.05);
    }
  }
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #909399;

    .el-icon {
      font-size: 14px;
    }
  }
}

.article-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
</style>

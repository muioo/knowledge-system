<template>
  <div class="article-list-view content-wrapper">
    <div class="header-section">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ currentTagName ? `${currentTagName} 的文章` : '文章管理' }}
      </h1>
    </div>

    <!-- 搜索和筛选 -->
    <div class="card">
      <div class="filter-row">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文章标题、摘要..."
          :prefix-icon="Search"
          clearable
          @keyup.enter="handleSearch"
          class="search-input"
        />
        <el-select
          v-model="selectedTagId"
          placeholder="按标签筛选"
          clearable
          @change="handleFilterChange"
          class="tag-select"
        >
          <el-option
            v-for="tag in tags"
            :key="tag.id"
            :label="tag.name"
            :value="tag.id"
          />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch" class="btn-primary">
          搜索
        </el-button>
      </div>
    </div>

    <!-- 文章列表 -->
    <div v-loading="loading" class="article-list">
      <div v-if="articles.length === 0 && !loading" class="empty-state">
        <el-icon :size="64" color="#9CA3AF"><Document /></el-icon>
        <p class="text-gray-500 mt-4">暂无文章</p>
      </div>

      <div v-for="article in articles" :key="article.id" class="article-card" @click="goToArticle(article.id)">
        <div class="article-header">
          <h3 class="article-title">{{ article.title }}</h3>
          <div class="article-actions" @click.stop>
            <el-button text :icon="Edit" @click="editArticle(article.id)" class="btn-ghost">编辑</el-button>
            <el-button text :icon="Delete" type="danger" @click="confirmDelete(article)" class="btn-ghost btn-danger">删除</el-button>
          </div>
        </div>
        <p class="article-summary">{{ article.summary || '暂无摘要' }}</p>
        <div class="article-meta">
          <div class="tags">
            <el-tag
              v-for="tag in article.tags"
              :key="tag.id"
              :color="tag.color"
              size="small"
              class="mr-2"
            >
              {{ tag.name }}
            </el-tag>
            <span v-if="article.tags.length === 0" class="text-gray-400 text-sm">无标签</span>
          </div>
          <div class="meta-info">
            <span class="text-gray-500 text-sm">
              <el-icon><View /></el-icon> {{ article.view_count }}
            </span>
            <span class="text-gray-500 text-sm">
              {{ formatDate(article.created_at) }}
            </span>
          </div>
        </div>
        <div v-if="article.keywords" class="article-keywords">
          <el-icon><PriceTag /></el-icon>
          <span>{{ article.keywords }}</span>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Document, Search, Edit, Delete, View, PriceTag } from '@element-plus/icons-vue'
import { articleApi } from '@/api/article'
import { tagApi } from '@/api/tag'
import type { Article } from '@/types'
import type { Tag } from '@/types/tag'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(false)
const articles = ref<Article[]>([])
const tags = ref<Tag[]>([])

// 搜索和筛选
const searchKeyword = ref('')
const selectedTagId = ref<number | null>(null)

// 当前标签名称（用于显示）
const currentTagName = computed(() => {
  if (!selectedTagId.value) return ''
  const tag = tags.value.find(t => t.id === selectedTagId.value)
  return tag ? tag.name : ''
})

// 分页
const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

// 加载文章列表
async function loadArticles() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.value.page,
      size: pagination.value.size
    }
    if (selectedTagId.value) {
      params.tag_id = selectedTagId.value
    }

    const res = await articleApi.getList(params)
    articles.value = res.data.items
    pagination.value.total = res.data.total
  } catch (error) {
    console.error('加载文章列表失败:', error)
    ElMessage.error('加载文章列表失败')
  } finally {
    loading.value = false
  }
}

// 加载标签列表
async function loadTags() {
  try {
    const res = await tagApi.getList()
    tags.value = res.data
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

// 搜索处理
function handleSearch() {
  // TODO: 实现关键词搜索功能（需要后端支持）
  pagination.value.page = 1
  loadArticles()
}

// 筛选变化
function handleFilterChange() {
  pagination.value.page = 1
  loadArticles()
}

// 分页变化
function handlePageChange(page: number) {
  pagination.value.page = page
  loadArticles()
}

function handleSizeChange(size: number) {
  pagination.value.size = size
  pagination.value.page = 1
  loadArticles()
}

// 跳转到文章详情
function goToArticle(id: number) {
  router.push(`/articles/${id}`)
}

// 编辑文章
function editArticle(id: number) {
  router.push(`/articles/${id}/edit`)
}

// 确认删除
function confirmDelete(article: Article) {
  ElMessageBox.confirm(
    `确定要删除文章《${article.title}》吗？此操作不可撤销。`,
    '确认删除',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteArticle(article.id)
  }).catch(() => {
    // 用户取消
  })
}

// 删除文章
async function deleteArticle(id: number) {
  try {
    await articleApi.delete(id)
    ElMessage.success('删除成功')
    loadArticles()
  } catch (error: any) {
    console.error('删除文章失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  // 从路由查询参数中获取 tag_id
  const tagIdFromQuery = route.query.tag_id as string
  if (tagIdFromQuery) {
    selectedTagId.value = parseInt(tagIdFromQuery)
  }

  loadArticles()
  loadTags()
})

// 监听路由变化，当 tag_id 变化时重新加载文章
watch(() => route.query.tag_id, (newTagId) => {
  if (newTagId) {
    selectedTagId.value = parseInt(newTagId as string)
  } else {
    selectedTagId.value = null
  }
  pagination.value.page = 1
  loadArticles()
})
</script>

<style scoped>
.article-list-view {
  width: 100%;
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-prompt);
  border: 1px solid var(--border-default);
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.tag-select {
  width: 180px;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-card {
  background: var(--bg-white);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.article-card:hover {
  box-shadow: 0px 12px 24px 0px rgba(50, 50, 71, 0.1);
  border-color: var(--color-indigo);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.article-title {
  font-family: var(--font-dinpro);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-black);
  margin: 0;
}

.article-actions {
  display: flex;
  gap: 4px;
}

.article-summary {
  color: var(--text-grey-40);
  font-size: 14px;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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
  color: var(--text-grey-40);
  font-size: 14px;
}

.article-keywords {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-grey-40);
  font-size: 13px;
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

.mr-2 {
  margin-right: 8px;
}
</style>

<template>
  <div class="search-page">
    <div class="search-header">
      <h1 class="page-title">搜索</h1>
      <el-input
        v-model="searchQuery"
        placeholder="搜索文章标题或内容..."
        :prefix-icon="Search"
        size="large"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button :icon="Search" @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <el-card v-if="loading" class="loading-card">
      <el-skeleton :rows="5" animated />
    </el-card>

    <div v-else-if="results.length > 0" class="search-results">
      <div class="results-header">
        <span>找到 {{ results.length }} 个结果</span>
      </div>
      <el-card
        v-for="article in results"
        :key="article.id"
        class="result-card"
        shadow="hover"
        @click="handleView(article.id)"
      >
        <h3 class="result-title">{{ article.title }}</h3>
        <p v-if="article.summary" class="result-summary">{{ article.summary }}</p>
        <div class="result-meta">
          <span><el-icon><Clock /></el-icon> {{ formatDate(article.created_at) }}</span>
          <span><el-icon><View /></el-icon> {{ article.view_count }} 次阅读</span>
        </div>
      </el-card>
    </div>

    <el-empty v-else-if="searched" description="未找到相关文章" />
    <el-empty v-else description="输入关键词开始搜索" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, Clock, View } from '@element-plus/icons-vue'
import { useArticleStore } from '../../stores/article'
import { formatDate } from '../../utils/date'
import type { Article } from '../../types'

const router = useRouter()
const route = useRoute()
const articleStore = useArticleStore()

const searchQuery = ref('')
const results = ref<Article[]>([])
const loading = ref(false)
const searched = ref(false)

onMounted(() => {
  const query = route.query.q as string
  if (query) {
    searchQuery.value = query
    handleSearch()
  }
})

async function handleSearch(): Promise<void> {
  if (!searchQuery.value.trim()) return

  loading.value = true
  searched.value = true

  try {
    await articleStore.fetchArticles({ keyword: searchQuery.value })
    results.value = articleStore.articles
  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    loading.value = false
  }
}

function handleView(id: number): void {
  router.push(`/articles/${id}`)
}
</script>

<style scoped lang="scss">
.search-page {
  max-width: 900px;
  margin: 0 auto;
}

.search-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #333;
}

.loading-card {
  margin-bottom: 24px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.results-header {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.result-card {
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
  }
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.result-summary {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.result-meta {
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

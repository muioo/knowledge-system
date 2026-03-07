import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { articleApi } from '@/api'
import type { Article, ArticleListParams, PaginationInfo } from '@/types'

export const useArticleStore = defineStore('article', () => {
  // State
  const articles = ref<Article[]>([])
  const currentArticle = ref<Article | null>(null)
  const pagination = ref<PaginationInfo>({
    total: 0,
    page: 1,
    size: 20,
  })
  const filters = ref<ArticleListParams>({})
  const loading = ref(false)

  // Getters
  const hasMore = computed(() => {
    return pagination.value.page * pagination.value.size < pagination.value.total
  })

  // Actions
  async function fetchArticles(params?: ArticleListParams) {
    loading.value = true
    try {
      const response = await articleApi.getList(params || filters.value)
      articles.value = response.data.items
      pagination.value = {
        total: response.data.total,
        page: response.data.page,
        size: response.data.size,
      }
      if (params) {
        filters.value = params
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchArticle(articleId: number) {
    loading.value = true
    try {
      const response = await articleApi.getDetail(articleId)
      currentArticle.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function uploadArticle(file: File, data: { title: string; summary: string; keywords: string; tag_ids?: string }) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    formData.append('summary', data.summary)
    formData.append('keywords', data.keywords)
    if (data.tag_ids) {
      formData.append('tag_ids', data.tag_ids)
    }

    const response = await articleApi.upload(formData)
    return response.data
  }

  async function importFromUrl(data: { url: string; tag_ids?: number[]; title?: string }) {
    const response = await articleApi.importFromUrl(data)
    return response.data
  }

  function setFilters(newFilters: Partial<ArticleListParams>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters() {
    filters.value = {}
  }

  return {
    articles,
    currentArticle,
    pagination,
    filters,
    loading,
    hasMore,
    fetchArticles,
    fetchArticle,
    uploadArticle,
    importFromUrl,
    setFilters,
    resetFilters,
  }
})

/**
 * 文章状态管理 Store
 * Article state management store with Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { articleApi, type ArticleQueryParams } from '../api/articles'
import type { Article, ArticleCreate, ArticleUpdate } from '../types'

export const useArticleStore = defineStore('article', () => {
  // State
  const articles = ref<Article[]>([])
  const currentArticle = ref<Article | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination state
  const pagination = ref({
    total: 0,
    page: 1,
    size: 20,
  })

  // Query params state
  const queryParams = ref<ArticleQueryParams>({
    page: 1,
    size: 20,
  })

  // Getters
  const hasArticles = computed(() => articles.value.length > 0)
  const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.size))
  const hasNextPage = computed(() => pagination.value.page < totalPages.value)
  const hasPrevPage = computed(() => pagination.value.page > 1)

  // Actions

  /**
   * Set loading state
   * @param isLoading - Loading state
   */
  function setLoading(isLoading: boolean): void {
    loading.value = isLoading
  }

  /**
   * Set error state
   * @param errorMsg - Error message
   */
  function setError(errorMsg: string | null): void {
    error.value = errorMsg
  }

  /**
   * Fetch articles list
   * @param params - Query parameters (optional)
   * @returns Promise with paginated articles
   */
  async function fetchArticles(params?: ArticleQueryParams): Promise<void> {
    setLoading(true)
    setError(null)

    try {
      // Update query params if provided
      if (params) {
        queryParams.value = { ...queryParams.value, ...params }
      }

      const response = await articleApi.getArticles(queryParams.value)

      articles.value = response.data.items
      pagination.value = {
        total: response.data.total,
        page: response.data.page,
        size: response.data.size,
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch articles'
      setError(errorMessage)
      articles.value = []
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Fetch single article by ID
   * @param id - Article ID
   * @returns Promise with article data
   */
  async function fetchArticle(id: number): Promise<void> {
    setLoading(true)
    setError(null)

    try {
      const article = await articleApi.getArticle(id)
      currentArticle.value = article
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch article'
      setError(errorMessage)
      currentArticle.value = null
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Fetch article HTML content
   * @param id - Article ID
   * @returns Promise with HTML content
   */
  async function fetchArticleHtml(id: number): Promise<{ html: string; title: string }> {
    setLoading(true)
    setError(null)

    try {
      const response = await articleApi.getArticleHtml(id)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch article HTML'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Create new article
   * @param data - Article creation data
   * @returns Promise with created article
   */
  async function createArticle(_data: ArticleCreate): Promise<Article> {
    setLoading(true)
    setError(null)

    try {
      // Note: API doesn't have a direct create endpoint, use upload or import
      // This is a placeholder for future implementation
      throw new Error('Direct article creation not implemented. Use upload or import.')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create article'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Update article
   * @param id - Article ID
   * @param data - Article update data
   * @returns Promise with updated article
   */
  async function updateArticle(id: number, data: ArticleUpdate): Promise<Article> {
    setLoading(true)
    setError(null)

    try {
      const updatedArticle = await articleApi.updateArticle(id, data)

      // Update in articles list if present
      const index = articles.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        articles.value[index] = updatedArticle
      }

      // Update current article if it's the same one
      if (currentArticle.value?.id === id) {
        currentArticle.value = updatedArticle
      }

      return updatedArticle
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update article'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Delete article
   * @param id - Article ID
   * @returns Promise with deletion confirmation
   */
  async function deleteArticle(id: number): Promise<void> {
    setLoading(true)
    setError(null)

    try {
      await articleApi.deleteArticle(id)

      // Remove from articles list
      articles.value = articles.value.filter((a) => a.id !== id)

      // Clear current article if it's the deleted one
      if (currentArticle.value?.id === id) {
        currentArticle.value = null
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete article'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Upload article file
   * @param file - File to upload
   * @param tagIds - Optional tag IDs
   * @returns Promise with uploaded article
   */
  async function uploadArticle(file: File, tagIds?: number[]): Promise<Article> {
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      if (tagIds && tagIds.length > 0) {
        formData.append('tag_ids', JSON.stringify(tagIds))
      }

      const uploadedArticle = await articleApi.uploadArticle(formData)

      // Add to articles list
      articles.value.unshift(uploadedArticle)

      return uploadedArticle
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload article'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Import article from URL
   * @param url - URL to import from
   * @param tagIds - Optional tag IDs
   * @returns Promise with imported article
   */
  async function importFromUrl(url: string, tagIds?: number[]): Promise<Article> {
    setLoading(true)
    setError(null)

    try {
      const importedArticle = await articleApi.importFromUrl({
        url,
        tag_ids: tagIds,
      })

      // Add to articles list
      articles.value.unshift(importedArticle)

      return importedArticle
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to import article'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Go to next page
   */
  async function nextPage(): Promise<void> {
    if (hasNextPage.value) {
      await fetchArticles({ page: pagination.value.page + 1 })
    }
  }

  /**
   * Go to previous page
   */
  async function prevPage(): Promise<void> {
    if (hasPrevPage.value) {
      await fetchArticles({ page: pagination.value.page - 1 })
    }
  }

  /**
   * Go to specific page
   * @param page - Page number
   */
  async function goToPage(page: number): Promise<void> {
    if (page >= 1 && page <= totalPages.value) {
      await fetchArticles({ page })
    }
  }

  /**
   * Search articles
   * @param searchQuery - Search query string
   */
  async function searchArticles(searchQuery: string): Promise<void> {
    await fetchArticles({ search: searchQuery, page: 1 })
  }

  /**
   * Filter articles by tag
   * @param tagId - Tag ID to filter by
   */
  async function filterByTag(tagId: number): Promise<void> {
    await fetchArticles({ tag_id: tagId, page: 1 })
  }

  /**
   * Sort articles
   * @param sortBy - Field to sort by
   * @param sortOrder - Sort order (asc or desc)
   */
  async function sortArticles(
    sortBy: 'created_at' | 'updated_at' | 'title' | 'read_count',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<void> {
    await fetchArticles({ sort_by: sortBy, sort_order: sortOrder })
  }

  /**
   * Clear current article
   */
  function clearCurrentArticle(): void {
    currentArticle.value = null
  }

  /**
   * Reset articles state
   */
  function resetArticles(): void {
    articles.value = []
    currentArticle.value = null
    pagination.value = {
      total: 0,
      page: 1,
      size: 20,
    }
    queryParams.value = {
      page: 1,
      size: 20,
    }
    error.value = null
  }

  return {
    // State
    articles,
    currentArticle,
    loading,
    error,
    pagination,
    queryParams,

    // Getters
    hasArticles,
    totalPages,
    hasNextPage,
    hasPrevPage,

    // Actions
    fetchArticles,
    fetchArticle,
    fetchArticleHtml,
    createArticle,
    updateArticle,
    deleteArticle,
    uploadArticle,
    importFromUrl,
    nextPage,
    prevPage,
    goToPage,
    searchArticles,
    filterByTag,
    sortArticles,
    clearCurrentArticle,
    resetArticles,
    setLoading,
    setError,
  }
})

/**
 * 标签状态管理 Store
 * Tag state management store with Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tagApi } from '../api/tags'
import type { Tag, TagCreate, TagUpdate, PaginatedData, Article } from '../types'

export const useTagStore = defineStore('tag', () => {
  // State
  const tags = ref<Tag[]>([])
  const currentTag = ref<Tag | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination state
  const pagination = ref({
    total: 0,
    page: 1,
    limit: 100,
  })

  // Getters
  const hasTags = computed(() => tags.value.length > 0)
  const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.limit))
  const hasNextPage = computed(() => pagination.value.page < totalPages.value)
  const hasPrevPage = computed(() => pagination.value.page > 1)

  // Tag map for quick lookup by ID
  const tagMap = computed(() => {
    const map = new Map<number, Tag>()
    tags.value.forEach((tag) => {
      map.set(tag.id, tag)
    })
    return map
  })

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
   * Fetch all tags
   * @param page - Page number (default: 1)
   * @param limit - Items per page (default: 100)
   * @returns Promise with paginated tags
   */
  async function fetchTags(page?: number, limit?: number): Promise<void> {
    setLoading(true)
    setError(null)

    try {
      const response = await tagApi.getTags({
        page: page ?? 1,
        limit: limit ?? 100,
      })

      tags.value = response.data.items
      pagination.value = {
        total: response.data.total,
        page: response.data.page,
        limit: response.data.size,
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tags'
      setError(errorMessage)
      tags.value = []
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Fetch single tag by ID
   * @param id - Tag ID
   * @returns Promise with tag data
   */
  async function fetchTag(id: number): Promise<void> {
    setLoading(true)
    setError(null)

    try {
      const tag = await tagApi.getTag(id)
      currentTag.value = tag
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tag'
      setError(errorMessage)
      currentTag.value = null
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Create new tag
   * @param data - Tag creation data
   * @returns Promise with created tag
   */
  async function createTag(data: TagCreate): Promise<Tag> {
    setLoading(true)
    setError(null)

    try {
      const newTag = await tagApi.createTag(data)

      // Add to tags list
      tags.value.unshift(newTag)

      return newTag
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create tag'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Update tag
   * @param id - Tag ID
   * @param data - Tag update data
   * @returns Promise with updated tag
   */
  async function updateTag(id: number, data: TagUpdate): Promise<Tag> {
    setLoading(true)
    setError(null)

    try {
      const updatedTag = await tagApi.updateTag(id, data)

      // Update in tags list if present
      const index = tags.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        tags.value[index] = updatedTag
      }

      // Update current tag if it's the same one
      if (currentTag.value?.id === id) {
        currentTag.value = updatedTag
      }

      return updatedTag
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update tag'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Delete tag
   * @param id - Tag ID
   * @returns Promise with deletion confirmation
   */
  async function deleteTag(id: number): Promise<void> {
    setLoading(true)
    setError(null)

    try {
      await tagApi.deleteTag(id)

      // Remove from tags list
      tags.value = tags.value.filter((t) => t.id !== id)

      // Clear current tag if it's the deleted one
      if (currentTag.value?.id === id) {
        currentTag.value = null
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete tag'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Fetch articles by tag
   * @param id - Tag ID
   * @param page - Page number (default: 1)
   * @param limit - Items per page (default: 20)
   * @returns Promise with paginated articles
   */
  async function fetchTagArticles(id: number, page?: number, limit?: number): Promise<PaginatedData<Article>> {
    setLoading(true)
    setError(null)

    try {
      const response = await tagApi.getTagArticles(id, {
        page: page ?? 1,
        limit: limit ?? 20,
      })

      return response.data
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tag articles'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * Get tag by ID
   * @param id - Tag ID
   * @returns Tag or undefined
   */
  function getTagById(id: number): Tag | undefined {
    return tagMap.value.get(id)
  }

  /**
   * Get tag color by ID
   * @param id - Tag ID
   * @returns Tag color or default color
   */
  function getTagColor(id: number): string {
    const tag = tagMap.value.get(id)
    return tag?.color ?? '#999999'
  }

  /**
   * Get tag name by ID
   * @param id - Tag ID
   * @returns Tag name or empty string
   */
  function getTagName(id: number): string {
    const tag = tagMap.value.get(id)
    return tag?.name ?? ''
  }

  /**
   * Go to next page
   */
  async function nextPage(): Promise<void> {
    if (hasNextPage.value) {
      await fetchTags(pagination.value.page + 1)
    }
  }

  /**
   * Go to previous page
   */
  async function prevPage(): Promise<void> {
    if (hasPrevPage.value) {
      await fetchTags(pagination.value.page - 1)
    }
  }

  /**
   * Go to specific page
   * @param page - Page number
   */
  async function goToPage(page: number): Promise<void> {
    if (page >= 1 && page <= totalPages.value) {
      await fetchTags(page)
    }
  }

  /**
   * Clear current tag
   */
  function clearCurrentTag(): void {
    currentTag.value = null
  }

  /**
   * Reset tags state
   */
  function resetTags(): void {
    tags.value = []
    currentTag.value = null
    pagination.value = {
      total: 0,
      page: 1,
      limit: 100,
    }
    error.value = null
  }

  return {
    // State
    tags,
    currentTag,
    loading,
    error,
    pagination,

    // Getters
    hasTags,
    totalPages,
    hasNextPage,
    hasPrevPage,
    tagMap,

    // Actions
    fetchTags,
    fetchTag,
    createTag,
    updateTag,
    deleteTag,
    fetchTagArticles,
    getTagById,
    getTagColor,
    getTagName,
    nextPage,
    prevPage,
    goToPage,
    clearCurrentTag,
    resetTags,
    setLoading,
    setError,
  }
})

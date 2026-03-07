import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagApi } from '@/api'
import type { Tag, CreateTagRequest, UpdateTagRequest } from '@/types'

export const useTagStore = defineStore('tag', () => {
  // State
  const tags = ref<Tag[]>([])
  const selectedTags = ref<number[]>([])
  const loading = ref(false)

  // Actions
  async function fetchTags() {
    loading.value = true
    try {
      const response = await tagApi.getAll()
      tags.value = response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createTag(data: CreateTagRequest) {
    const response = await tagApi.create(data)
    tags.value = [...tags.value, response.data]
    return response.data
  }

  async function updateTag(tagId: number, data: UpdateTagRequest) {
    const response = await tagApi.update(tagId, data)
    const index = tags.value.findIndex(t => t.id === tagId)
    if (index !== -1) {
      tags.value = [...tags.value.slice(0, index), response.data, ...tags.value.slice(index + 1)]
    }
    return response.data
  }

  async function deleteTag(tagId: number) {
    await tagApi.delete(tagId)
    tags.value = tags.value.filter(t => t.id !== tagId)
  }

  function setSelectedTags(tagIds: number[]) {
    selectedTags.value = tagIds
  }

  function toggleTag(tagId: number) {
    const index = selectedTags.value.indexOf(tagId)
    if (index === -1) {
      selectedTags.value.push(tagId)
    } else {
      selectedTags.value.splice(index, 1)
    }
  }

  return {
    tags,
    selectedTags,
    loading,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    setSelectedTags,
    toggleTag,
  }
})

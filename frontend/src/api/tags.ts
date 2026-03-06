/**
 * 标签相关 API
 * Tags API methods
 */
import api from './index'
import type { Tag, TagCreate, TagUpdate, PaginatedResponse, Article } from '../types'

/**
 * Tags API
 */
export const tagApi = {
  /**
   * Get all tags with pagination
   * GET /tags/
   */
  getTags: async (params?: { page?: number; limit?: number }): Promise<PaginatedResponse<Tag>> => {
    const response = await api.get<PaginatedResponse<Tag>>('/tags/', { params })
    return response.data
  },

  /**
   * Get single tag by ID
   * GET /tags/{id}
   */
  getTag: async (id: number): Promise<Tag> => {
    const response = await api.get<Tag>(`/tags/${id}`)
    return response.data
  },

  /**
   * Create new tag
   * POST /tags/
   */
  createTag: async (data: TagCreate): Promise<Tag> => {
    const response = await api.post<Tag>('/tags/', data)
    return response.data
  },

  /**
   * Update tag
   * PUT /tags/{id}
   */
  updateTag: async (id: number, data: TagUpdate): Promise<Tag> => {
    const response = await api.put<Tag>(`/tags/${id}`, data)
    return response.data
  },

  /**
   * Delete tag
   * DELETE /tags/{id}
   */
  deleteTag: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/tags/${id}`)
    return response.data
  },

  /**
   * Get articles by tag
   * GET /tags/{id}/articles
   */
  getTagArticles: async (
    id: number,
    params?: { page?: number; limit?: number }
  ): Promise<PaginatedResponse<Article>> => {
    const response = await api.get<PaginatedResponse<Article>>(`/tags/${id}/articles`, { params })
    return response.data
  },
}

export default tagApi

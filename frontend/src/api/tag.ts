import apiClient from './request'
import type {
  ApiResponse,
  Tag,
  CreateTagRequest,
  UpdateTagRequest,
  Article,
  ApiPaginatedResponse,
} from '@/types'

export const tagApi = {
  // 获取所有标签
  getAll(): Promise<ApiResponse<Tag[]>> {
    return apiClient.get('/tags/')
  },

  // 获取标签详情
  getDetail(tagId: number): Promise<ApiResponse<Tag>> {
    return apiClient.get(`/tags/${tagId}`)
  },

  // 创建标签
  create(data: CreateTagRequest): Promise<ApiResponse<Tag>> {
    return apiClient.post('/tags/', data)
  },

  // 更新标签
  update(tagId: number, data: UpdateTagRequest): Promise<ApiResponse<Tag>> {
    return apiClient.put(`/tags/${tagId}`, data)
  },

  // 删除标签
  delete(tagId: number): Promise<void> {
    return apiClient.delete(`/tags/${tagId}`)
  },

  // 获取标签下的文章
  getArticles(tagId: number, params?: { page?: number; size?: number }): Promise<ApiPaginatedResponse<Article>> {
    return apiClient.get(`/tags/${tagId}/articles`, { params })
  },
}

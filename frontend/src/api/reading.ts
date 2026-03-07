import apiClient from './request'
import type { ApiPaginatedResponse } from '@/types/api'

// 阅读历史响应
export interface ReadingHistory {
  id: number
  article_id: number
  article_title: string
  started_at: string
  ended_at: string | null
  reading_duration: number
  reading_progress: number
}

// 阅读统计响应
export interface ReadingStats {
  article_id: number
  article_title: string
  total_views: number
  total_duration: number
  last_read_at: string | null
}

// 结束阅读请求
export interface EndReadingRequest {
  reading_progress?: number
}

// 开始阅读文章
export const startReading = (articleId: number) =>
  apiClient.post(`/reading/articles/${articleId}/start`)

// 结束阅读文章
export const endReading = (articleId: number, data: EndReadingRequest) =>
  apiClient.post(`/reading/articles/${articleId}/end`, data)

// 获取阅读历史
export const getReadingHistory = (params?: { page?: number; size?: number }) =>
  apiClient.get<ApiPaginatedResponse<ReadingHistory>>('/reading/history', { params })

// 获取个人阅读统计
export const getReadingStats = (params?: { page?: number; size?: number }) =>
  apiClient.get<ApiPaginatedResponse<ReadingStats>>('/reading/stats', { params })

// 获取文章阅读统计（管理员）
export const getArticleStats = (articleId: number, params?: { page?: number; size?: number }) =>
  apiClient.get<ApiPaginatedResponse<ReadingStats>>(`/reading/articles/${articleId}/stats`, { params })

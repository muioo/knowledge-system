/**
 * 阅读历史和统计相关 API
 * Reading history and statistics API methods
 */
import api from './index'
import type { PaginatedResponse, Article, ReadingHistory, ReadingStats, ArticleReadingStats } from '../types'

export interface StartReadingRequest {
  article_id: number
}

/**
 * Reading API
 */
export const readingApi = {
  /**
   * Start reading session
   * POST /reading/start
   */
  startReading: async (data: StartReadingRequest): Promise<ReadingHistory> => {
    const response = await api.post<ReadingHistory>('/reading/start', data)
    return response.data
  },

  /**
   * End reading session
   * POST /reading/end/{session_id}
   */
  endReading: async (sessionId: number): Promise<ReadingHistory> => {
    const response = await api.post<ReadingHistory>(`/reading/end/${sessionId}`)
    return response.data
  },

  /**
   * Get reading history
   * GET /reading/history
   */
  getHistory: async (params?: {
    page?: number
    limit?: number
    article_id?: number
  }): Promise<PaginatedResponse<ReadingHistory>> => {
    const response = await api.get<PaginatedResponse<ReadingHistory>>('/reading/history', { params })
    return response.data
  },

  /**
   * Get reading statistics
   * GET /reading/stats
   */
  getStats: async (): Promise<ReadingStats> => {
    const response = await api.get<ReadingStats>('/reading/stats')
    return response.data
  },

  /**
   * Get article reading statistics
   * GET /reading/article-stats/{article_id}
   */
  getArticleStats: async (articleId: number): Promise<ArticleReadingStats> => {
    const response = await api.get<ArticleReadingStats>(`/reading/article-stats/${articleId}`)
    return response.data
  },
}

export default readingApi

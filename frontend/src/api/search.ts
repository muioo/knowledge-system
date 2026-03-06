/**
 * 搜索相关 API
 * Search API methods
 */
import api from './index'
import type { PaginatedResponse, Article, Tag } from '../types'

export interface SearchQueryParams {
  q: string
  page?: number
  limit?: number
  type?: 'all' | 'articles' | 'tags'
}

export interface SearchResult {
  articles: Article[]
  tags: Tag[]
  total: number
}

/**
 * Search API
 */
export const searchApi = {
  /**
   * Search articles and tags
   * GET /search/
   */
  search: async (params: SearchQueryParams): Promise<SearchResult> => {
    const response = await api.get<SearchResult>('/search/', { params })
    return response.data
  },

  /**
   * Search articles only
   * GET /search/articles
   */
  searchArticles: async (
    params: { q: string; page?: number; limit?: number }
  ): Promise<PaginatedResponse<Article>> => {
    const response = await api.get<PaginatedResponse<Article>>('/search/articles', { params })
    return response.data
  },

  /**
   * Search tags only
   * GET /search/tags
   */
  searchTags: async (
    params: { q: string; page?: number; limit?: number }
  ): Promise<PaginatedResponse<Tag>> => {
    const response = await api.get<PaginatedResponse<Tag>>('/search/tags', { params })
    return response.data
  },
}

export default searchApi

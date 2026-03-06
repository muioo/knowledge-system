/**
 * 文章相关 API
 * Articles API methods
 */
import api from './index'
import type {
  Article,
  ArticleCreate,
  ArticleUpdate,
  ArticleListResponse,
  ImportFromUrlRequest,
  PaginatedResponse,
} from '../types'

export interface ArticleQueryParams {
  page?: number
  limit?: number
  search?: string
  tag_id?: number
  sort_by?: 'created_at' | 'updated_at' | 'title' | 'read_count'
  sort_order?: 'asc' | 'desc'
}

/**
 * Articles API
 */
export const articleApi = {
  /**
   * Get articles list with pagination
   * GET /articles/
   */
  getArticles: async (params?: ArticleQueryParams): Promise<PaginatedResponse<Article>> => {
    const response = await api.get<PaginatedResponse<Article>>('/articles/', { params })
    return response.data
  },

  /**
   * Get single article by ID
   * GET /articles/{id}
   */
  getArticle: async (id: number): Promise<Article> => {
    const response = await api.get<Article>(`/articles/${id}`)
    return response.data
  },

  /**
   * Get article HTML content
   * GET /articles/{id}/html
   */
  getArticleHtml: async (id: number): Promise<{ html: string; title: string }> => {
    const response = await api.get<{ html: string; title: string }>(`/articles/${id}/html`)
    return response.data
  },

  /**
   * Upload article file (markdown, html, txt)
   * POST /articles/upload
   */
  uploadArticle: async (formData: FormData): Promise<Article> => {
    const response = await api.post<Article>('/articles/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Import article from URL
   * POST /articles/from-url-html
   */
  importFromUrl: async (data: ImportFromUrlRequest): Promise<Article> => {
    const response = await api.post<Article>('/articles/from-url-html', data)
    return response.data
  },

  /**
   * Update article
   * PUT /articles/{id}
   */
  updateArticle: async (id: number, data: ArticleUpdate): Promise<Article> => {
    const response = await api.put<Article>(`/articles/${id}`, data)
    return response.data
  },

  /**
   * Delete article
   * DELETE /articles/{id}
   */
  deleteArticle: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/articles/${id}`)
    return response.data
  },
}

export default articleApi

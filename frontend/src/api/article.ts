import apiClient from './request'
import type {
  ApiResponse,
  Article,
  ApiPaginatedResponse,
  ArticleListParams,
  UpdateArticleRequest,
  UrlImportRequest,
} from '@/types'

export const articleApi = {
  // 获取文章列表
  getList(params?: ArticleListParams): Promise<ApiResponse<ApiPaginatedResponse<Article>>> {
    return apiClient.get('/articles/', { params })
  },

  // 获取文章详情
  getDetail(articleId: number): Promise<ApiResponse<Article>> {
    return apiClient.get(`/articles/${articleId}`)
  },

  // 上传文件创建文章
  upload(data: FormData): Promise<ApiResponse<Article>> {
    return apiClient.post('/articles/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // URL 导入文章
  importFromUrl(data: UrlImportRequest): Promise<ApiResponse<Article>> {
    return apiClient.post('/articles/from-url-html', data)
  },

  // 更新文章
  update(articleId: number, data: UpdateArticleRequest): Promise<ApiResponse<Article>> {
    return apiClient.put(`/articles/${articleId}`, data)
  },

  // 删除文章
  delete(articleId: number): Promise<void> {
    return apiClient.delete(`/articles/${articleId}`)
  },

  // 获取文章 HTML 内容
  getHtml(articleId: number): Promise<ApiResponse<Article>> {
    return apiClient.get(`/articles/${articleId}/html`)
  },
}

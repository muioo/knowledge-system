import apiClient from './client';
import type { ApiResponse, PaginatedResponse, Article, ArticleCreateData, UrlImportData } from '../types/api';

export const articleApi = {
  /**
   * 获取文章列表
   */
  getArticles: async (params?: Record<string, any>): Promise<PaginatedResponse<Article>> => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<Article>>>('/articles/', { params });
    return response.data.data;
  },

  /**
   * 获取文章详情
   */
  getArticle: async (id: number): Promise<Article> => {
    const response = await apiClient.get<ApiResponse<Article>>(`/articles/${id}`);
    return response.data.data;
  },

  /**
   * 获取文章 HTML 内容
   */
  getArticleHtml: async (id: number): Promise<{ html_content: string }> => {
    const response = await apiClient.get<ApiResponse<{ html_content: string }>>(`/articles/${id}/html`);
    return response.data.data;
  },

  /**
   * 上传文件创建文章
   */
  uploadArticle: async (file: File, data: ArticleCreateData): Promise<Article> => {
    const formData = new FormData();
    formData.append('file', file);
    if (data.title) formData.append('title', data.title);
    if (data.summary) formData.append('summary', data.summary);
    if (data.keywords) formData.append('keywords', data.keywords);
    if (data.tagIds && data.tagIds.length > 0) {
      formData.append('tag_ids', data.tagIds.join(','));
    }

    const response = await apiClient.post<ApiResponse<Article>>('/articles/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data.data;
  },

  /**
   * 从 URL 导入文章
   */
  importFromUrl: async (data: UrlImportData): Promise<Article> => {
    const response = await apiClient.post<ApiResponse<Article>>('/articles/from-url-html', data);
    return response.data.data;
  },

  /**
   * 更新文章
   */
  updateArticle: async (id: number, data: Partial<ArticleCreateData> & { tagIds?: number[] }): Promise<Article> => {
    const response = await apiClient.put<ApiResponse<Article>>(`/articles/${id}`, data);
    return response.data.data;
  },

  /**
   * 删除文章
   */
  deleteArticle: async (id: number): Promise<void> => {
    await apiClient.delete(`/articles/${id}`);
  },
};

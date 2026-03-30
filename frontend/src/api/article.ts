import apiClient from './client';
import type { ApiResponse, PaginatedResponse, Article, ArticleCreateData, UrlImportData } from '../types/api';

export const articleApi = {
  /**
   * 获取文章列表
   */
  getArticles: async (params?: Record<string, any>): Promise<PaginatedResponse<Article>> => {
    const response = await apiClient.get<any>('/articles/', { params });
    return response.data;
  },

  /**
   * 获取文章详情
   */
  getArticle: async (id: number): Promise<Article> => {
    const response = await apiClient.get<any>(`/articles/${id}`);
    return response.data;
  },

  /**
   * 获取文章 HTML 内容
   */
  getArticleHtml: async (id: number): Promise<{ html_content: string }> => {
    const response = await apiClient.get<any>(`/articles/${id}/html`);
    return response.data;
  },

  /**
   * 上传文件创建文章
   * @param file HTML 文件
   * @param data 文章数据（可包含图片文件数组）
   */
  uploadArticle: async (file: File, data: ArticleCreateData & { images?: File[] }): Promise<Article> => {
    const formData = new FormData();
    formData.append('file', file);
    if (data.title) formData.append('title', data.title);
    if (data.summary) formData.append('summary', data.summary);
    if (data.keywords) formData.append('keywords', data.keywords);
    if (data.tagIds && data.tagIds.length > 0) {
      formData.append('tag_ids', data.tagIds.join(','));
    }

    // 添加图片文件
    if (data.images && data.images.length > 0) {
      data.images.forEach(imageFile => {
        formData.append('images', imageFile);
      });
    }

    const response = await apiClient.post<any>('/articles/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * 从 URL 导入文章
   */
  importFromUrl: async (data: UrlImportData): Promise<Article> => {
    const payload: Record<string, any> = {
      url: data.url,
      use_ai: data.use_ai ?? false,
    };
    if (data.tagIds && data.tagIds.length > 0) payload.tag_ids = data.tagIds;
    if (data.title) payload.title = data.title;
    if (data.summary) payload.summary = data.summary;
    if (data.keywords) payload.keywords = data.keywords;
    if (data.api_key) payload.api_key = data.api_key;

    const response = await apiClient.post<any>('/articles/from-url-html', payload, {
      timeout: 120000,
    });
    // 后端返回: { code, message, data: Article }
    // axios拦截器返回: { code, message, data: Article }
    return response.data;
  },

  /**
   * 更新文章
   */
  updateArticle: async (id: number, data: Partial<ArticleCreateData> & { tagIds?: number[] }): Promise<Article> => {
    const payload: Record<string, any> = { ...data };
    if (data.tagIds) {
      payload.tag_ids = data.tagIds;
      delete payload.tagIds;
    }
    const response = await apiClient.put<any>(`/articles/${id}`, payload);
    return response.data;
  },

  /**
   * 删除文章
   */
  deleteArticle: async (id: number): Promise<void> => {
    await apiClient.delete(`/articles/${id}`);
  },
};

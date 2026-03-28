import apiClient, { ApiResponse, PaginatedResponse, Article } from './client';

export const articleApi = {
  // 获取文章列表
  getArticles: async (params = {}) => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse>>('/articles/', { params });
    return response.data;
  },

  // 获取文章详情
  getArticle: async (id) => {
    const response = await apiClient.get<ApiResponse<Article>>(`/articles/${id}`);
    return response.data;
  },

  // 获取文章 HTML 内容
  getArticleHtml: async (id) => {
    const response = await apiClient.get<ApiResponse<Article>>(`/articles/${id}/html`);
    return response.data;
  },

  // 上传文件创建文章
  uploadArticle: async (file, data) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', data.title);
    formData.append('summary', data.summary);
    formData.append('keywords', data.keywords);
    if (data.tagIds && data.tagIds.length > 0) {
      formData.append('tag_ids', data.tagIds.join(','));
    }

    const response = await apiClient.post<ApiResponse<Article>>('/articles/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // 从 URL 导入文章
  importFromUrl: async (data) => {
    const response = await apiClient.post<ApiResponse<Article>>('/articles/from-url-html', data);
    return response.data;
  },

  // 更新文章
  updateArticle: async (id, data) => {
    const response = await apiClient.put<ApiResponse<Article>>(`/articles/${id}`, data);
    return response.data;
  },

  // 删除文章
  deleteArticle: async (id) => {
    await apiClient.delete(`/articles/${id}`);
  },
};

export default articleApi;

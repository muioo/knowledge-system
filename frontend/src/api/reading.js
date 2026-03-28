import apiClient, { ApiResponse, PaginatedResponse } from './client';

export const readingApi = {
  // 开始阅读
  startReading: async (articleId) => {
    const response = await apiClient.post<ApiResponse>(`/reading/articles/${articleId}/start`);
    return response.data;
  },

  // 结束阅读
  endReading: async (articleId, progress = 0) => {
    const response = await apiClient.post<ApiResponse>(`/reading/articles/${articleId}/end`, {
      reading_progress: progress,
    });
    return response.data;
  },

  // 获取阅读历史
  getHistory: async (page = 1, size = 20) => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse>>('/reading/history', {
      params: { page, size },
    });
    return response.data;
  },

  // 获取阅读统计
  getStats: async (page = 1, size = 20) => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse>>('/reading/stats', {
      params: { page, size },
    });
    return response.data;
  },
};

export default readingApi;

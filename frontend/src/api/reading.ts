import apiClient from './client';
import type { ApiResponse, PaginatedResponse, ReadingStats, ReadingHistory } from '../types/api';

export const readingApi = {
  /**
   * 开始阅读
   */
  startReading: async (articleId: number): Promise<ReadingHistory> => {
    const response = await apiClient.post<ApiResponse<ReadingHistory>>(`/reading/articles/${articleId}/start`);
    return response.data;
  },

  /**
   * 结束阅读
   */
  endReading: async (articleId: number, progress = 0): Promise<ReadingHistory> => {
    const response = await apiClient.post<ApiResponse<ReadingHistory>>(`/reading/articles/${articleId}/end`, {
      reading_progress: progress,
    });
    return response.data;
  },

  /**
   * 获取阅读历史
   */
  getHistory: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingHistory>> => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<ReadingHistory>>>('/reading/history', {
      params: { page, size },
    });
    return response.data;
  },

  /**
   * 获取阅读统计
   */
  getStats: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingStats>> => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<ReadingStats>>>('/reading/stats', {
      params: { page, size },
    });
    return response.data;
  },
};

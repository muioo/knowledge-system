import apiClient from './client';
import type { ApiResponse, PaginatedResponse, ReadingStats, ReadingHistory, ReadingTrend, TimeDistribution, ReadingProgress } from '../types/api';

export const readingApi = {
  /**
   * 开始阅读
   */
  startReading: async (articleId: number): Promise<ReadingHistory> => {
    const response = await apiClient.post<any>(`/reading/articles/${articleId}/start`);
    return response.data;
  },

  /**
   * 结束阅读
   */
  endReading: async (articleId: number, progress = 0): Promise<ReadingHistory> => {
    const response = await apiClient.post<any>(`/reading/articles/${articleId}/end`, {
      reading_progress: progress,
    });
    return response.data;
  },

  /**
   * 获取阅读历史
   */
  getHistory: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingHistory>> => {
    const response = await apiClient.get<any>('/reading/history', {
      params: { page, size },
    });
    return response.data;
  },

  /**
   * 获取阅读统计
   */
  getStats: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingStats>> => {
    const response = await apiClient.get<any>('/reading/stats', {
      params: { page, size },
    });
    return response.data;
  },

  /**
   * 获取阅读趋势
   */
  getTrends: async (days = 7): Promise<{ items: ReadingTrend[]; total: number }> => {
    const response = await apiClient.get<any>('/reading/trends', {
      params: { days },
    });
    return response.data;
  },

  /**
   * 获取时段分布
   */
  getTimeDistribution: async (): Promise<TimeDistribution> => {
    const response = await apiClient.get<any>('/reading/time-distribution');
    return response.data;
  },

  /**
   * 获取阅读进度
   */
  getProgress: async (page = 1, size = 20): Promise<{ items: ReadingProgress[]; total: number; page: number; size: number }> => {
    const response = await apiClient.get<any>('/reading/progress', {
      params: { page, size },
    });
    return response.data;
  },
};

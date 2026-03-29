import apiClient from './client';
import type { ApiResponse, PaginatedResponse, ReadingStats, ReadingHistory, ReadingTrend, TimeDistribution, ReadingProgress } from '../types/api';

export const readingApi = {
  /**
   * 开始阅读
   */
  startReading: async (articleId: number): Promise<ReadingHistory> => {
    const response = await apiClient.post<any>(`/reading/articles/${articleId}/start`);
    // 响应拦截器已返回 response.data，格式: { code: 200, message: "success", data: {...} }
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
    // PaginatedResponse 格式: { code: 200, message: "success", data: { total, page, size, items } }
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
    // SuccessResponse 格式: { code: 200, message: "success", data: { items, total } }
    return response.data;
  },

  /**
   * 获取时段分布（后端直接返回字典，不包装）
   */
  getTimeDistribution: async (): Promise<TimeDistribution> => {
    const response = await apiClient.get<any>('/reading/time-distribution');
    // 后端直接返回: { periods: [...], heatmap: [...] }
    return response;
  },

  /**
   * 获取阅读进度（后端直接返回字典，不包装）
   */
  getProgress: async (page = 1, size = 20): Promise<{ items: ReadingProgress[]; total: number; page: number; size: number }> => {
    const response = await apiClient.get<any>('/reading/progress', {
      params: { page, size },
    });
    // 后端直接返回: { items, total, page, size }
    return response;
  },

  /**
   * 更新阅读进度（基于滚动位置）
   */
  updateProgress: async (articleId: number, data: {
    scroll_position: number;
    total_content_length: number;
    actual_progress: number;
  }): Promise<{
    scroll_position: number;
    total_content_length: number;
    actual_progress: number;
    reading_progress: number;
  }> => {
    const response = await apiClient.put<any>(`/reading/articles/${articleId}/progress`, data);
    // SuccessResponse 格式: { code: 200, message: "success", data: {...} }
    return response.data;
  },
};

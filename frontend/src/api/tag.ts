import apiClient from './client';
import type { ApiResponse, Tag, PaginatedResponse } from '../types/api';

export const tagApi = {
  /**
   * 获取所有标签
   */
  getTags: async (): Promise<Tag[]> => {
    const response = await apiClient.get<any>('/tags/');
    return response.data;
  },

  /**
   * 获取标签详情
   */
  getTag: async (id: number): Promise<Tag> => {
    const response = await apiClient.get<any>(`/tags/${id}`);
    return response.data;
  },

  /**
   * 创建标签
   */
  createTag: async (data: { name: string; color?: string }): Promise<Tag> => {
    const response = await apiClient.post<any>('/tags/', data);
    return response.data;
  },

  /**
   * 更新标签
   */
  updateTag: async (id: number, data: { name?: string; color?: string }): Promise<Tag> => {
    const response = await apiClient.put<any>(`/tags/${id}`, data);
    return response.data;
  },

  /**
   * 删除标签
   */
  deleteTag: async (id: number): Promise<void> => {
    await apiClient.delete(`/tags/${id}`);
  },

  /**
   * 获取标签下的文章
   */
  getTagArticles: async (id: number, page = 1, size = 20): Promise<PaginatedResponse<any>> => {
    const response = await apiClient.get<any>(`/tags/${id}/articles`, {
      params: { page, size },
    });
    return response.data;
  },
};

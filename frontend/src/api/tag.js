import apiClient, { ApiResponse, Tag } from './client';

export const tagApi = {
  // 获取所有标签
  getTags: async () => {
    const response = await apiClient.get<ApiResponse<Tag[]>>('/tags/');
    return response.data;
  },

  // 获取标签详情
  getTag: async (id) => {
    const response = await apiClient.get<ApiResponse<Tag>>(`/tags/${id}`);
    return response.data;
  },

  // 创建标签
  createTag: async (data) => {
    const response = await apiClient.post<ApiResponse<Tag>>('/tags/', data);
    return response.data;
  },

  // 更新标签
  updateTag: async (id, data) => {
    const response = await apiClient.put<ApiResponse<Tag>>(`/tags/${id}`, data);
    return response.data;
  },

  // 删除标签
  deleteTag: async (id) => {
    await apiClient.delete(`/tags/${id}`);
  },

  // 获取标签下的文章
  getTagArticles: async (id, page = 1, size = 20) => {
    const response = await apiClient.get<ApiResponse>(`/tags/${id}/articles`, {
      params: { page, size },
    });
    return response.data;
  },
};

export default tagApi;

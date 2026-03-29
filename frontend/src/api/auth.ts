import apiClient from './client';
import type { ApiResponse, LoginResponse, User } from '../types/api';

export interface LoginRequest {
  username: string;
  password: string;
}

export const authApi = {
  /**
   * 用户登录
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<any>('/auth/login', data);
    return response.data;
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<any>('/users/me');
    return response.data;
  },
};

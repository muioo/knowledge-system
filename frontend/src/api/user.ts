import apiClient from './request'
import type { ApiResponse, User, UpdateUserRequest, ApiPaginatedResponse } from '@/types'

export const userApi = {
  // 获取当前用户信息
  getMe(): Promise<ApiResponse<User>> {
    return apiClient.get('/users/me')
  },

  // 更新当前用户信息
  updateMe(data: UpdateUserRequest): Promise<ApiResponse<User>> {
    return apiClient.put('/users/me', data)
  },

  // 删除当前用户
  deleteMe(): Promise<void> {
    return apiClient.delete('/users/me')
  },

  // 获取用户列表（管理员）
  getList(params?: { page?: number; size?: number }): Promise<ApiPaginatedResponse<User>> {
    return apiClient.get('/users/', { params })
  },

  // 获取指定用户（管理员）
  getById(userId: number): Promise<ApiResponse<User>> {
    return apiClient.get(`/users/${userId}`)
  },

  // 更新指定用户（管理员）
  updateUser(userId: number, data: UpdateUserRequest): Promise<ApiResponse<User>> {
    return apiClient.put(`/users/${userId}`, data)
  },

  // 删除指定用户（管理员）
  deleteUser(userId: number): Promise<void> {
    return apiClient.delete(`/users/${userId}`)
  },

  // 更新用户角色（管理员）
  updateUserRole(userId: number, role: 'admin' | 'user'): Promise<ApiResponse<User>> {
    return apiClient.patch(`/users/${userId}/role`, { role })
  },

  // 更新用户状态（管理员）
  updateUserStatus(userId: number, is_active: boolean): Promise<ApiResponse<User>> {
    return apiClient.patch(`/users/${userId}/status`, { is_active })
  },
}

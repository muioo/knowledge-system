/**
 * 用户相关 API
 * Users API methods
 */
import api from './index'
import type { User, UserUpdate, PaginatedResponse, UserRole } from '../types'

/**
 * Users API
 */
export const userApi = {
  /**
   * Get current user info
   * GET /users/me
   */
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  /**
   * Update current user profile
   * PUT /users/me
   */
  updateMe: async (data: UserUpdate): Promise<User> => {
    const response = await api.put<User>('/users/me', data)
    return response.data
  },

  /**
   * Delete current user account
   * DELETE /users/me
   */
  deleteMe: async (): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>('/users/me')
    return response.data
  },

  /**
   * Get all users with pagination (admin only)
   * GET /users/
   */
  getUsers: async (params?: { page?: number; limit?: number }): Promise<PaginatedResponse<User>> => {
    const response = await api.get<PaginatedResponse<User>>('/users/', { params })
    return response.data
  },

  /**
   * Get single user by ID (admin only)
   * GET /users/{id}
   */
  getUser: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`)
    return response.data
  },

  /**
   * Update user (admin only)
   * PUT /users/{id}
   */
  updateUser: async (id: number, data: UserUpdate): Promise<User> => {
    const response = await api.put<User>(`/users/${id}`, data)
    return response.data
  },

  /**
   * Delete user (admin only)
   * DELETE /users/{id}
   */
  deleteUser: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/users/${id}`)
    return response.data
  },

  /**
   * Update user role (admin only)
   * PUT /users/{id}/role
   */
  updateUserRole: async (id: number, role: UserRole): Promise<User> => {
    const response = await api.put<User>(`/users/${id}/role`, { role })
    return response.data
  },
}

export default userApi

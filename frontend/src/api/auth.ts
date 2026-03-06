/**
 * 认证相关 API
 * Authentication API methods
 */
import api from './index'
import type { UserLogin, UserCreate, User, AuthTokens, SuccessResponse } from '../types'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RegisterResponse {
  message: string
  user: User
}

/**
 * Authentication API
 */
export const authApi = {
  /**
   * User login
   * POST /auth/login
   */
  login: async (data: UserLogin): Promise<LoginResponse> => {
    const response = await api.post<SuccessResponse<LoginResponse>>('/auth/login', data)
    // Extract data from SuccessResponse wrapper
    const authData = response.data.data
    // Store tokens in localStorage
    localStorage.setItem('access_token', authData.access_token)
    localStorage.setItem('refresh_token', authData.refresh_token)
    return authData
  },

  /**
   * User registration
   * POST /auth/register
   */
  register: async (data: UserCreate): Promise<RegisterResponse> => {
    const response = await api.post<SuccessResponse<LoginResponse>>('/auth/register', data)
    const authData = response.data.data
    // Note: Registration automatically logs in user
    localStorage.setItem('access_token', authData.access_token)
    localStorage.setItem('refresh_token', authData.refresh_token)
    return {
      message: response.data.message,
      user: authData.user
    }
  },

  /**
   * Logout (client-side only - clear tokens)
   */
  logout: (): void => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  },

  /**
   * Refresh access token
   * POST /auth/refresh
   */
  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await api.post<SuccessResponse<AuthTokens>>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data.data
  },
}

export default authApi

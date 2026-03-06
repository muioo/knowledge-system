/**
 * 认证相关 API
 * Authentication API methods
 */
import api from './index'
import type { UserLogin, UserCreate, AuthTokens, User } from '../types'

export interface LoginResponse {
  access_token: string
  refresh_token: string
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
    const response = await api.post<LoginResponse>('/auth/login', data)
    // Store tokens in localStorage
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
    return response.data
  },

  /**
   * User registration
   * POST /auth/register
   */
  register: async (data: UserCreate): Promise<RegisterResponse> => {
    const response = await api.post<RegisterResponse>('/auth/register', data)
    return response.data
  },

  /**
   * Logout (client-side only - clear tokens)
   */
  logout: (): void => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  /**
   * Refresh access token
   * POST /auth/refresh
   */
  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}

export default authApi

import apiClient from './request'
import type {
  ApiResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '@/types'

export const authApi = {
  // 用户登录
  login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    return apiClient.post('/auth/login', data)
  },

  // 用户注册
  register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    return apiClient.post('/auth/register', data)
  },

  // 刷新 Token
  refreshToken(refreshToken: string): Promise<ApiResponse<AuthResponse>> {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken })
  },
}

/**
 * API 响应基础类型定义
 * Defines base API response types for the knowledge system
 */

/**
 * 导入 User 类型以避免循环依赖
 * Import User type to avoid circular dependency
 * 这里使用前向声明，实际类型在 models.ts 中定义
 * Forward declaration - actual type defined in models.ts
 */
import type { User } from './models'

/**
 * 成功响应包装器
 * Wrapper for successful API responses
 */
export interface SuccessResponse<T> {
  code: number
  message: string
  data: T
}

/**
 * 分页数据结构
 * Paginated data structure
 */
export interface PaginatedData<T> {
  total: number
  page: number
  size: number
  items: T[]
}

/**
 * 分页响应包装器
 * Wrapper for paginated API responses
 */
export interface PaginatedResponse<T> {
  code: number
  message: string
  data: PaginatedData<T>
}

/**
 * 错误响应结构
 * Error response structure
 */
export interface ErrorResponse {
  code: number
  message: string
  detail?: string
}

/**
 * Token 响应结构
 * Token response structure for authentication
 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

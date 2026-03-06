/**
 * 数据模型类型定义
 * Defines data model types for the knowledge system
 */

import type { TagInfo } from './tag'

/**
 * 用户基础类型
 * Base user type
 */
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

/**
 * 用户响应类型
 * User response type
 */
export interface UserResponse extends User {
  // Inherits all fields from User
}

/**
 * 用户创建请求类型
 * User creation request type
 */
export interface UserCreate {
  username: string
  email: string
  password: string
}

/**
 * 用户更新请求类型
 * User update request type
 */
export interface UserUpdate {
  email?: string
  password?: string
}

/**
 * 用户登录请求类型
 * User login request type
 */
export interface UserLogin {
  username: string
  password: string
}

/**
 * 文章基础类型
 * Base article type
 */
export interface Article {
  id: number
  title: string
  content: string
  author_id: number
  source_url?: string
  summary?: string
  keywords?: string
  original_filename?: string
  view_count: number
  created_at: string
  updated_at: string
  tags: TagInfo[]
}

/**
 * 文章响应类型
 * Article response type
 */
export interface ArticleResponse extends Article {
  // Inherits all fields from Article
}

/**
 * 文章创建请求类型
 * Article creation request type
 */
export interface ArticleCreate {
  title: string
  content: string
  source_url?: string
  summary?: string
  keywords?: string
  tag_ids?: number[]
  import_type?: 'direct' | 'file'
}

/**
 * 文章更新请求类型
 * Article update request type
 */
export interface ArticleUpdate {
  title?: string
  content?: string
  source_url?: string
  summary?: string
  keywords?: string
  tag_ids?: number[]
}

/**
 * 包含 HTML 内容的文章响应类型
 * Article response type with HTML content
 */
export interface ArticleHtmlResponse extends ArticleResponse {
  html_content?: string
  html_path?: string
  processing_status?: string
}

/**
 * 从 HTML URL 导入文章请求类型
 * Request type for importing article from HTML URL
 */
export interface ArticleFromHtmlUrlRequest {
  url: string
  tag_ids?: number[]
}

/**
 * 从 HTML URL 导入文章响应类型
 * Response type for importing article from HTML URL
 */
export interface ArticleFromHtmlUrlResponse {
  article_id: number
  status: string
  message: string
}

/**
 * 搜索查询请求类型
 * Search query request type
 */
export interface SearchQuery {
  q?: string
  tags?: number[]
  page?: number
  size?: number
}

/**
 * 阅读历史类型
 * Reading history type
 */
export interface ReadingHistory {
  id: number
  article_id: number
  article_title: string
  started_at: string
  ended_at?: string
  reading_duration: number
  reading_progress: number
}

/**
 * 阅读结束请求类型
 * Reading end request type
 */
export interface ReadingEnd {
  reading_progress: number
}

/**
 * 阅读统计类型
 * Reading statistics type
 */
export interface ReadingStats {
  article_id: number
  article_title: string
  total_views: number
  total_duration: number
  last_read_at?: string
}

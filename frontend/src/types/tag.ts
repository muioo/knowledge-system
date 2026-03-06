/**
 * 标签类型定义
 * Defines tag-related types for the knowledge system
 */

/**
 * 标签基础类型
 * Base tag type
 */
export interface Tag {
  id: number
  name: string
  color: string
  created_at: string
}

/**
 * 标签信息类型（用于关联数据）
 * Tag info type (used in related data)
 */
export interface TagInfo {
  id: number
  name: string
  color: string
}

/**
 * 标签创建请求类型
 * Tag creation request type
 */
export interface TagCreate {
  name: string
  color?: string
}

/**
 * 标签更新请求类型
 * Tag update request type
 */
export interface TagUpdate {
  name?: string
  color?: string
}

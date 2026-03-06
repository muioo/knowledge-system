/**
 * 权限工具函数
 * Permission utility functions for checking user permissions
 */

import { storage } from './storage'
import type { User, Article } from '../types'

/**
 * Check if user is authenticated
 * @returns True if user has valid access token
 */
export function isAuthenticated(): boolean {
  const token = storage.getToken()
  return !!token && token.length > 0
}

/**
 * Check if current user is admin
 * @returns True if current user has admin role
 */
export function isAdmin(): boolean {
  const user = storage.getUser()
  return user?.role === 'admin'
}

/**
 * Check if user can edit article
 * @param article - Article to check
 * @param userId - Current user ID (optional, will get from storage if not provided)
 * @returns True if user is admin or article author
 */
export function canEditArticle(article: Article, userId?: number): boolean {
  // Admin can edit any article
  if (isAdmin()) {
    return true
  }

  // Get current user ID from storage if not provided
  const currentUserId = userId ?? storage.getUser()?.id

  // User can edit their own articles
  return article.author_id === currentUserId
}

/**
 * Check if user can delete article
 * @param article - Article to check
 * @param userId - Current user ID (optional, will get from storage if not provided)
 * @returns True if user is admin or article author
 */
export function canDeleteArticle(article: Article, userId?: number): boolean {
  // Same logic as edit permission
  return canEditArticle(article, userId)
}

/**
 * Check if user can manage tags (create, update, delete)
 * @returns True if user is authenticated
 */
export function canManageTags(): boolean {
  return isAuthenticated()
}

/**
 * Check if user can manage users (view, update roles, delete)
 * @returns True if user is admin
 */
export function canManageUsers(): boolean {
  return isAdmin()
}

/**
 * Check if user can upload articles
 * @returns True if user is authenticated
 */
export function canUploadArticles(): boolean {
  return isAuthenticated()
}

/**
 * Check if user can import from URL
 * @returns True if user is authenticated
 */
export function canImportFromUrl(): boolean {
  return isAuthenticated()
}

/**
 * Get current user ID
 * @returns Current user ID or null if not authenticated
 */
export function getCurrentUserId(): number | null {
  const user = storage.getUser()
  return user?.id ?? null
}

/**
 * Get current username
 * @returns Current username or null if not authenticated
 */
export function getCurrentUsername(): string | null {
  const user = storage.getUser()
  return user?.username ?? null
}

/**
 * Get current user role
 * @returns Current user role or null if not authenticated
 */
export function getCurrentUserRole(): 'admin' | 'user' | null {
  const user = storage.getUser()
  return user?.role ?? null
}

/**
 * Check if user is owner of resource
 * @param resourceUserId - User ID of resource owner
 * @param currentUserId - Current user ID (optional, will get from storage if not provided)
 * @returns True if current user is the owner
 */
export function isOwner(resourceUserId: number, currentUserId?: number): boolean {
  const userId = currentUserId ?? getCurrentUserId()
  return resourceUserId === userId
}

/**
 * Permission levels for UI display
 */
export enum PermissionLevel {
  NONE = 'none',
  READ = 'read',
  WRITE = 'write',
  ADMIN = 'admin',
}

/**
 * Get permission level for current user
 * @returns Permission level based on user role
 */
export function getPermissionLevel(): PermissionLevel {
  if (!isAuthenticated()) {
    return PermissionLevel.NONE
  }

  if (isAdmin()) {
    return PermissionLevel.ADMIN
  }

  return PermissionLevel.WRITE
}

/**
 * Check if user has required permission level
 * @param requiredLevel - Required permission level
 * @returns True if user has at least the required permission level
 */
export function hasPermissionLevel(requiredLevel: PermissionLevel): boolean {
  const currentLevel = getPermissionLevel()

  const levels = [PermissionLevel.NONE, PermissionLevel.READ, PermissionLevel.WRITE, PermissionLevel.ADMIN]

  return levels.indexOf(currentLevel) >= levels.indexOf(requiredLevel)
}

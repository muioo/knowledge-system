/**
 * 本地存储工具函数
 * Local storage utility functions for authentication and user data
 */

import type { User } from '../types'

/**
 * Storage keys constant
 */
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
} as const

/**
 * Storage object with authentication and user data methods
 */
export const storage = {
  /**
   * Get access token from localStorage
   * @returns Access token or null
   */
  getToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
  },

  /**
   * Set access token in localStorage
   * @param token - Access token to store
   */
  setToken(token: string): void {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token)
  },

  /**
   * Remove access token from localStorage
   */
  removeToken(): void {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
  },

  /**
   * Get refresh token from localStorage
   * @returns Refresh token or null
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
  },

  /**
   * Set refresh token in localStorage
   * @param token - Refresh token to store
   */
  setRefreshToken(token: string): void {
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, token)
  },

  /**
   * Remove refresh token from localStorage
   */
  removeRefreshToken(): void {
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
  },

  /**
   * Clear all authentication data from localStorage
   */
  clearAuth(): void {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER)
  },

  /**
   * Get user data from localStorage
   * @returns User object or null
   */
  getUser(): User | null {
    const userStr = localStorage.getItem(STORAGE_KEYS.USER)
    if (!userStr) {
      return null
    }

    try {
      return JSON.parse(userStr) as User
    } catch {
      return null
    }
  },

  /**
   * Set user data in localStorage
   * @param user - User object to store
   */
  setUser(user: User): void {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user))
  },

  /**
   * Remove user data from localStorage
   */
  removeUser(): void {
    localStorage.removeItem(STORAGE_KEYS.USER)
  },

  /**
   * Clear all data from localStorage
   */
  clear(): void {
    localStorage.clear()
  },

  /**
   * Get item from localStorage
   * @param key - Storage key
   * @returns Item value or null
   */
  getItem(key: string): string | null {
    return localStorage.getItem(key)
  },

  /**
   * Set item in localStorage
   * @param key - Storage key
   * @param value - Value to store
   */
  setItem(key: string, value: string): void {
    localStorage.setItem(key, value)
  },

  /**
   * Remove item from localStorage
   * @param key - Storage key
   */
  removeItem(key: string): void {
    localStorage.removeItem(key)
  },
}

/**
 * Session storage wrapper (similar to localStorage but clears on session end)
 */
export const sessionStorage = {
  /**
   * Get item from sessionStorage
   * @param key - Storage key
   * @returns Item value or null
   */
  getItem(key: string): string | null {
    return window.sessionStorage.getItem(key)
  },

  /**
   * Set item in sessionStorage
   * @param key - Storage key
   * @param value - Value to store
   */
  setItem(key: string, value: string): void {
    window.sessionStorage.setItem(key, value)
  },

  /**
   * Remove item from sessionStorage
   * @param key - Storage key
   */
  removeItem(key: string): void {
    window.sessionStorage.removeItem(key)
  },

  /**
   * Clear all items from sessionStorage
   */
  clear(): void {
    window.sessionStorage.clear()
  },
}

export default storage

/**
 * 认证状态管理 Store
 * Authentication state management store with Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type LoginResponse, type RegisterResponse } from '../api/auth'
import { storage } from '../utils/storage'
import type { User, UserLogin, UserCreate } from '../types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(storage.getToken())
  const refreshToken = ref<string | null>(storage.getRefreshToken())
  const user = ref<User | null>(storage.getUser())

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const currentUser = computed(() => user.value)
  const userId = computed(() => user.value?.id ?? null)
  const username = computed(() => user.value?.username ?? '')
  const userEmail = computed(() => user.value?.email ?? '')
  const userRole = computed(() => user.value?.role ?? null)

  // Actions

  /**
   * Set authentication state
   * @param tokens - Authentication tokens
   * @param userData - User data
   */
  function setAuthState(tokens: { access_token: string; refresh_token: string }, userData: User): void {
    token.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    user.value = userData

    // Persist to storage
    storage.setToken(tokens.access_token)
    storage.setRefreshToken(tokens.refresh_token)
    storage.setUser(userData)
  }

  /**
   * Clear authentication state
   */
  function clearAuthState(): void {
    token.value = null
    refreshToken.value = null
    user.value = null

    // Clear from storage
    storage.clearAuth()
  }

  /**
   * Update user data
   * @param userData - Updated user data
   */
  function updateUserData(userData: User): void {
    user.value = userData
    storage.setUser(userData)
  }

  /**
   * Login user
   * @param credentials - User login credentials
   * @returns Promise with login response
   */
  async function login(credentials: UserLogin): Promise<LoginResponse> {
    try {
      const response = await authApi.login(credentials)

      // Set authentication state
      setAuthState(
        {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
        },
        response.user
      )

      return response
    } catch (error) {
      clearAuthState()
      throw error
    }
  }

  /**
   * Register new user
   * @param userData - User registration data
   * @returns Promise with registration response
   */
  async function register(userData: UserCreate): Promise<RegisterResponse> {
    try {
      const response = await authApi.register(userData)

      // Note: Registration doesn't automatically log in user
      // User needs to login separately after registration

      return response
    } catch (error) {
      throw error
    }
  }

  /**
   * Logout user
   */
  async function logout(): Promise<void> {
    try {
      // Call logout API (client-side only)
      authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Always clear local state
      clearAuthState()
    }
  }

  /**
   * Refresh access token
   * @returns Promise with new tokens
   */
  async function refreshAccessToken(): Promise<{ access_token: string }> {
    const currentRefreshToken = refreshToken.value

    if (!currentRefreshToken) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await authApi.refreshToken(currentRefreshToken)

      // Update access token
      token.value = response.access_token
      storage.setToken(response.access_token)

      return response
    } catch (error) {
      // Refresh failed, clear auth state
      clearAuthState()
      throw error
    }
  }

  /**
   * Initialize auth state from storage (call on app startup)
   */
  function initializeAuth(): void {
    token.value = storage.getToken()
    refreshToken.value = storage.getRefreshToken()
    user.value = storage.getUser()
  }

  /**
   * Check if current user can edit article
   * @param authorId - Article author ID
   * @returns True if user is admin or article author
   */
  function canEditArticle(authorId: number): boolean {
    return isAdmin.value || userId.value === authorId
  }

  /**
   * Check if current user can delete article
   * @param authorId - Article author ID
   * @returns True if user is admin or article author
   */
  function canDeleteArticle(authorId: number): boolean {
    return canEditArticle(authorId)
  }

  return {
    // State
    token,
    refreshToken,
    user,

    // Getters
    isAuthenticated,
    isAdmin,
    currentUser,
    userId,
    username,
    userEmail,
    userRole,

    // Actions
    login,
    register,
    logout,
    refreshAccessToken,
    initializeAuth,
    canEditArticle,
    canDeleteArticle,
    updateUserData,
  }
})

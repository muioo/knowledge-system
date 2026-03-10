import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '@/utils/constants'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  async function login(credentials: LoginRequest) {
    loading.value = true
    const response = await authApi.login(credentials) as any
    // 调试日志：检查响应格式
    console.log('[Login] 完整响应:', response)
    console.log('[Login] response.data:', response.data)

    // 防御性处理：兼容不同的响应格式
    let tokenData
    if (response.data) {
      tokenData = response.data
    } else if (response.access_token) {
      tokenData = response
    } else {
      throw new Error('登录响应格式错误')
    }

    const { access_token, refresh_token, user: userData } = tokenData

    token.value = access_token
    user.value = userData

    localStorage.setItem(TOKEN_KEY, access_token)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))

    loading.value = false
    return response
  }

  async function register(data: RegisterRequest) {
    loading.value = true
    const response = await authApi.register(data) as any

    // 防御性处理：兼容不同的响应格式
    let tokenData
    if (response.data) {
      tokenData = response.data
    } else if (response.access_token) {
      tokenData = response
    } else {
      throw new Error('注册响应格式错误')
    }

    const { access_token, refresh_token, user: userData } = tokenData

    token.value = access_token
    user.value = userData

    localStorage.setItem(TOKEN_KEY, access_token)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))

    loading.value = false
    return response
  }

  async function fetchUser() {
    if (!token.value) return

    try {
      const response = await userApi.getMe() as any
      // 防御性处理：兼容不同的响应格式
      const userData = response.data || response
      user.value = userData
      localStorage.setItem(USER_KEY, JSON.stringify(userData))
    } catch (error) {
      logout()
      throw error
    }
  }

  async function refreshToken() {
    const refreshTokenValue = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshTokenValue) throw new Error('No refresh token')

    const response = await authApi.refreshToken(refreshTokenValue) as any
    // 防御性处理：兼容不同的响应格式
    let tokenData
    if (response.data) {
      tokenData = response.data
    } else if (response.access_token) {
      tokenData = response
    } else {
      throw new Error('Token刷新响应格式错误')
    }

    const { access_token } = tokenData

    token.value = access_token
    localStorage.setItem(TOKEN_KEY, access_token)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  // 从 localStorage 恢复状态
  function restoreState() {
    const savedToken = localStorage.getItem(TOKEN_KEY)
    const savedUser = localStorage.getItem(USER_KEY)

    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch {
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
      }
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchUser,
    refreshToken,
    logout,
    restoreState,
  }
})

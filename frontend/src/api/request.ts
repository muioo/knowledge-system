import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE_URL, TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/utils/constants'

// API 错误响应类型
interface ApiError {
  detail:
    | string
    | Array<{
        loc: string[]
        msg: string
        type: string
      }>
}

// 扩展请求配置类型
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

// Token刷新锁机制
let isRefreshing = false
let failedQueue: Array<(token: string) => void> = []

function processQueue(token: string) {
  failedQueue.forEach((callback) => callback(token))
  failedQueue = []
}

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config: CustomAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig

    // Token 过期处理
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          failedQueue.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(apiClient(originalRequest))
          })
        }).then(() => apiClient(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          // 检查响应格式
          if (!response.data || !response.data.data) {
            throw new Error('Token 刷新失败：响应格式错误')
          }

          const { access_token } = response.data.data
          if (!access_token) {
            throw new Error('Token 刷新失败：未返回 access_token')
          }

          localStorage.setItem(TOKEN_KEY, access_token)
          processQueue(access_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } else {
          // 没有 refresh_token，直接跳转到登录页
          localStorage.removeItem(TOKEN_KEY)
          window.location.href = '/login'
          return Promise.reject(new Error('未找到 refresh_token'))
        }
      } catch (refreshError: any) {
        console.error('[Token Refresh] 失败:', refreshError)
        console.error('[Token Refresh] 响应数据:', refreshError.response?.data)
        failedQueue.forEach((callback) => callback('' as any))
        failedQueue = []

        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 错误提示
    const errorData = error.response?.data as ApiError
    let message = '请求失败，请稍后重试'
    if (errorData?.detail) {
      if (typeof errorData.detail === 'string') {
        message = errorData.detail
      } else if (Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
        message = errorData.detail[0].msg
      }
    }
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

export default apiClient

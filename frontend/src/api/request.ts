import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE_URL, TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/utils/constants'

// 扩展请求配置类型
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
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
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomAxiosRequestConfig

    // Token 过期处理
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data.data
          localStorage.setItem(TOKEN_KEY, access_token)

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // 刷新失败，清除 token 并跳转登录
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // 错误提示
    const errorData = error.response?.data as { detail?: string | Array<any> }
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

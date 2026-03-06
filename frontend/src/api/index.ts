/**
 * Axios 实例配置
 * Axios instance configuration with interceptors
 */
import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: add Authorization header
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Flag to prevent multiple token refresh attempts
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Response interceptor: handle errors and auto token refresh
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Network errors
    if (!error.response) {
      console.error('Network Error:', error.message)
      return Promise.reject(new Error('Network error. Please check your connection.'))
    }

    const { status } = error.response

    // Handle 401 Unauthorized - try to refresh token
    if (status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, add request to queue
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Try to refresh token
          const response = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/auth/refresh`,
            { refresh_token: refreshToken }
          )

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          // Set new token in header
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }

          processQueue(null, access_token)
          isRefreshing = false

          // Retry original request
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          processQueue(refreshError as AxiosError, null)
          isRefreshing = false

          // Redirect to login page if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }

          return Promise.reject(new Error('Session expired. Please login again.'))
        }
      } else {
        // No refresh token available, redirect to login
        localStorage.removeItem('access_token')
        isRefreshing = false

        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }

        return Promise.reject(new Error('No session found. Please login.'))
      }
    }

    // Handle other error status codes
    switch (status) {
      case 400:
        console.error('Bad Request:', error.response.data)
        return Promise.reject(new Error('Invalid request. Please check your input.'))
      case 403:
        console.error('Forbidden:', error.response.data)
        return Promise.reject(new Error('You do not have permission to perform this action.'))
      case 404:
        console.error('Not Found:', error.response.data)
        return Promise.reject(new Error('The requested resource was not found.'))
      case 422:
        console.error('Validation Error:', error.response.data)
        return Promise.reject(new Error('Validation failed. Please check your input.'))
      case 500:
      case 502:
      case 503:
        console.error('Server Error:', error.response.data)
        return Promise.reject(new Error('Server error. Please try again later.'))
      default:
        console.error('Unexpected Error:', error.response.data)
        return Promise.reject(new Error('An unexpected error occurred.'))
    }
  }
)

export default api

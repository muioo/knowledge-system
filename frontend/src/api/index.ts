/**
 * Axios 实例配置
 * Axios instance configuration with interceptors
 */
import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

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

// Response interceptor: handle errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    // Network errors
    if (!error.response) {
      console.error('Network Error:', error.message)
      return Promise.reject(new Error('Network error. Please check your connection.'))
    }

    const { status } = error.response

    // Handle 401 Unauthorized - clear tokens and redirect to login
    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')

      // Redirect to login page if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }

      return Promise.reject(new Error('Session expired. Please login again.'))
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

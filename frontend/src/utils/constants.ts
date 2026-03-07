export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const TOKEN_KEY = 'access_token'
export const REFRESH_TOKEN_KEY = 'refresh_token'
export const USER_KEY = 'user'

export const COLORS = {
  primary: '#3B82F6',
  success: '#10B981',
  accent: '#8B5CF6',
  warning: '#F59E0B',
  danger: '#EF4444',
}

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_SIZE: 20,
  MAX_SIZE: 100,
}

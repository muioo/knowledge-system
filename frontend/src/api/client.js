import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022/api/v1';

/**
 * Token 刷新锁机制
 * 防止多个并发请求同时触发 token 刷新
 */
let isRefreshing = false;
let failedQueue = [];

/**
 * 处理等待队列中的请求
 * @param {Error|null} error - 刷新过程中的错误
 * @param {string|null} token - 新的 access token
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Axios 客户端实例
 * 配置了基础 URL、超时时间和默认请求头
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 请求拦截器
 * 自动添加认证 token 到请求头
 *
 * 安全警告: 当前使用 localStorage 存储 token，这存在 XSS 攻击风险。
 * 建议后续改用 httpOnly cookie 或更安全的存储机制。
 * 在此之前，确保：
 * 1. 实施 CSP (Content Security Policy)
 * 2. 对所有用户输入进行验证和转义
 * 3. 定期审计前端依赖库的安全性
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 * 处理错误和 token 刷新逻辑
 */
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;

    // 处理 401 未授权错误
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // 如果正在刷新 token，将请求加入等待队列
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch(err => {
            return Promise.reject(err);
          });
      }

      // 开始刷新 token 流程
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          // 尝试刷新 token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data.data;
          localStorage.setItem('access_token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }

          // 处理等待队列中的请求
          processQueue(null, access_token);

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，处理等待队列并清除 token
        processQueue(refreshError, null);
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // 处理其他错误
    const errorMessage = error.response?.data?.message || error.message || '请求失败';
    console.error('API Error:', errorMessage);
    return Promise.reject(error);
  }
);

export default apiClient;

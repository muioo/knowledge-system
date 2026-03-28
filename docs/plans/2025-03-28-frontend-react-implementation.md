# 知识系统前端 React 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 构建一个完整的 React 前端应用，对接后端 API，提供用户认证、文章管理、标签管理、阅读统计等功能，完全还原 login.html 和 home.html 的设计样式。

**架构:** 使用 Vite + React + Tailwind CSS + React Router + Context API 构建单页应用。组件化设计，Context API 管理全局状态，Axios 处理 API 请求，路由守卫保护需要认证的页面。

**技术栈:** React 18, Vite, Tailwind CSS, React Router v6, Axios, Context API

---

## Task 1: 项目初始化

**目标:** 清空现有 frontend 目录并创建全新的 Vite + React 项目

### Step 1: 清空现有 frontend 目录

```bash
# 备份当前目录（如果有需要的内容）
cd D:/Code/Python/FastApi/knowledge-system
# 删除 frontend 目录内容
rm -rf frontend/*
```

### Step 2: 创建 Vite + React 项目

```bash
cd frontend
npm create vite@latest . -- --template react
```

### Step 3: 安装依赖

```bash
npm install
npm install react-router-dom axios
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 4: 配置 Tailwind CSS

创建/修改 `frontend/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Step 5: 配置 Tailwind 指令

修改 `frontend/src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 6: 创建基础目录结构

```bash
cd src
mkdir -p api/components/layout components/ui contexts pages hooks utils types
```

### Step 7: 提交初始配置

```bash
git add .
git commit -m "feat: 初始化 Vite + React + Tailwind CSS 项目"
```

---

## Task 2: 创建 API 客户端配置

**目标:** 配置 Axios 客户端，处理认证和错误拦截

### Step 1: 创建类型定义文件

创建 `frontend/src/types/api.ts`:

```typescript
// 通用响应格式
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 分页响应
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  size: number;
  items: T[];
}

// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// 标签类型
export interface Tag {
  id: number;
  name: string;
  color: string;
  created_at?: string;
}

// 文章类型
export interface Article {
  id: number;
  title: string;
  source_url: string | null;
  summary: string | null;
  keywords: string | null;
  author_id: number;
  original_filename: string | null;
  view_count: number;
  created_at: string;
  updated_at: string;
  tags: Tag[];
  html_content: string | null;
  html_path: string | null;
  processing_status: string | null;
  original_html_url: string | null;
}

// 阅读统计类型
export interface ReadingStats {
  article_id: number;
  article_title: string;
  total_views: number;
  total_duration: number;
  last_read_at: string | null;
}

// 阅读历史类型
export interface ReadingHistory {
  id: number;
  article_id: number;
  article_title: string;
  started_at: string;
  ended_at: string | null;
  reading_duration: number;
  reading_progress: number;
}
```

### Step 2: 创建 Axios 客户端配置

创建 `frontend/src/api/client.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8022/api/v1';

// 创建 axios 实例
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 token
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

// 响应拦截器 - 处理错误和 token 刷新
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;

    // 如果是 401 错误且没有尝试过刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

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

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除 token 并跳转登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### Step 3: 创建认证 API

创建 `frontend/src/api/auth.ts`:

```typescript
import apiClient, { ApiResponse, LoginResponse, User } from './client';

export interface LoginRequest {
  username: string;
  password: string;
}

export const authApi = {
  // 登录
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<ApiResponse<LoginResponse>>('/auth/login', data);
    return response.data;
  },

  // 获取当前用户信息
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<ApiResponse<User>>('/users/me');
    return response.data;
  },
};
```

### Step 4: 提交 API 配置

```bash
git add src/types src/api
git commit -m "feat: 配置 Axios 客户端和类型定义"
```

---

## Task 3: 创建基础 UI 组件

**目标:** 还原 login.html 样式的基础 UI 组件

### Step 1: 创建 Button 组件

创建 `frontend/src/components/ui/Button.jsx`:

```jsx
import React from 'react';

const Button = ({
  children,
  variant = 'default',
  className = '',
  isHovered = false,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';

  const variantStyles = {
    default:
      'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700',
    outline:
      'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
  };

  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${className} ${isHovered ? 'shadow-lg shadow-blue-200' : ''}`;

  return (
    <button className={combinedClassName} {...props}>
      {children}
    </button>
  );
};

export default Button;
```

### Step 2: 创建 Input 组件

创建 `frontend/src/components/ui/Input.jsx`:

```jsx
import React from 'react';

const Input = ({ className = '', ...props }) => {
  const baseStyles =
    'flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm text-gray-800 ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 border-gray-200 bg-gray-50 focus:border-blue-500';

  return <input className={`${baseStyles} ${className}`} {...props} />;
};

export default Input;
```

### Step 3: 创建 Card 组件

创建 `frontend/src/components/ui/Card.jsx`:

```jsx
import React from 'react';

const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={`bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
```

### Step 4: 创建图标组件

创建 `frontend/src/components/ui/Icons.jsx`:

```jsx
import React from 'react';

export const EyeIcon = ({ className = '', size = 18 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

export const EyeOffIcon = ({ className = '', size = 18 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
    <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
    <line x1="2" x2="22" y1="2" y2="22" />
  </svg>
);

export const ArrowRightIcon = ({ className = '', size = 24 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M5 12h14" />
    <path d="m12 5 7 7-7 7" />
  </svg>
);

export const HomeIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

export const FileTextIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
);

export const TagIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z" />
    <path d="M7 7h.01" />
  </svg>
);

export const BarChartIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <line x1="12" x2="12" y1="20" y2="10" />
    <line x1="18" x2="18" y1="20" y2="4" />
    <line x1="6" x2="6" y1="20" y2="16" />
  </svg>
);

export const MenuIcon = ({ className = '', size = 24 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    className={className}
  >
    <line x1="3" y1="6" x2="21" y2="6" />
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
);
```

### Step 5: 创建 DotMap 动画组件

创建 `frontend/src/components/ui/DotMap.jsx`:

```jsx
import React, { useRef, useState, useEffect } from 'react';

const DotMap = () => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const routes = [
    { start: { x: 100, y: 150, delay: 0 }, end: { x: 200, y: 80, delay: 2 }, color: '#2563eb' },
    { start: { x: 200, y: 80, delay: 2 }, end: { x: 260, y: 120, delay: 4 }, color: '#2563eb' },
    { start: { x: 50, y: 50, delay: 1 }, end: { x: 150, y: 180, delay: 3 }, color: '#2563eb' },
    { start: { x: 280, y: 60, delay: 0.5 }, end: { x: 180, y: 180, delay: 2.5 }, color: '#2563eb' }
  ];

  const generateDots = (width, height) => {
    const dots = [];
    const gap = 12;
    const dotRadius = 1;

    for (let x = 0; x < width; x += gap) {
      for (let y = 0; y < height; y += gap) {
        const isInMapShape =
          ((x < width * 0.25 && x > width * 0.05) && (y < height * 0.4 && y > height * 0.1)) ||
          ((x < width * 0.25 && x > width * 0.15) && (y < height * 0.8 && y > height * 0.4)) ||
          ((x < width * 0.45 && x > width * 0.3) && (y < height * 0.35 && y > height * 0.15)) ||
          ((x < width * 0.5 && x > width * 0.35) && (y < height * 0.65 && y > height * 0.35)) ||
          ((x < width * 0.7 && x > width * 0.45) && (y < height * 0.5 && y > height * 0.1)) ||
          ((x < width * 0.8 && x > width * 0.65) && (y < height * 0.8 && y > height * 0.6));

        if (isInMapShape && Math.random() > 0.3) {
          dots.push({ x, y, radius: dotRadius, opacity: Math.random() * 0.5 + 0.2 });
        }
      }
    }
    return dots;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
      canvas.width = width;
      canvas.height = height;
    });

    resizeObserver.observe(canvas.parentElement);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    if (!dimensions.width || !dimensions.height) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dots = generateDots(dimensions.width, dimensions.height);
    let animationFrameId;
    let startTime = Date.now();

    function drawDots() {
      ctx.clearRect(0, 0, dimensions.width, dimensions.height);
      dots.forEach((dot) => {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(37, 99, 235, ${dot.opacity})`;
        ctx.fill();
      });
    }

    function drawRoutes() {
      const currentTime = (Date.now() - startTime) / 1000;

      routes.forEach((route) => {
        const elapsed = currentTime - route.start.delay;
        if (elapsed <= 0) return;

        const duration = 3;
        const progress = Math.min(elapsed / duration, 1);

        const x = route.start.x + (route.end.x - route.start.x) * progress;
        const y = route.start.y + (route.end.y - route.start.y) * progress;

        ctx.beginPath();
        ctx.moveTo(route.start.x, route.start.y);
        ctx.lineTo(x, y);
        ctx.strokeStyle = route.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(route.start.x, route.start.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = route.color;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#3b82f6';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
        ctx.fill();

        if (progress === 1) {
          ctx.beginPath();
          ctx.arc(route.end.x, route.end.y, 3, 0, Math.PI * 2);
          ctx.fillStyle = route.color;
          ctx.fill();
        }
      });
    }

    function animate() {
      drawDots();
      drawRoutes();

      const currentTime = (Date.now() - startTime) / 1000;
      if (currentTime > 15) {
        startTime = Date.now();
      }

      animationFrameId = requestAnimationFrame(animate);
    }

    animate();

    return () => cancelAnimationFrame(animationFrameId);
  }, [dimensions]);

  return (
    <div className="relative w-full h-full overflow-hidden">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
    </div>
  );
};

export default DotMap;
```

### Step 6: 提交基础 UI 组件

```bash
git add src/components/ui
git commit -m "feat: 创建基础 UI 组件（Button、Input、Card、Icons、DotMap）"
```

---

## Task 4: 创建认证 Context

**目标:** 实现 AuthContext 管理认证状态

### Step 1: 创建 AuthContext

创建 `frontend/src/contexts/AuthContext.jsx`:

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // 检查本地存储的 token 并获取用户信息
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await authApi.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          // Token 无效，清除本地存储
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authApi.login({ username, password });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setUser(response.user);
      setIsAuthenticated(true);
      navigate('/dashboard');
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || '登录失败，请检查用户名和密码',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/');
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

### Step 2: 创建路由守卫组件

创建 `frontend/src/components/ProtectedRoute.jsx`:

```jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### Step 3: 提交认证相关代码

```bash
git add src/contexts src/components/ProtectedRoute.jsx
git commit -m "feat: 实现 AuthContext 和路由守卫"
```

---

## Task 5: 创建登录页面

**目标:** 还原 login.html 样式的登录页面（简化版）

### Step 1: 创建登录页面

创建 `frontend/src/pages/Login.jsx`:

```jsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import DotMap from '../components/ui/DotMap';
import { EyeIcon, EyeOffIcon, ArrowRightIcon } from '../components/ui/Icons';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();

  const EyeIconComponent = isPasswordVisible ? EyeOffIcon : EyeIcon;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const result = await login(username, password);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-4xl overflow-hidden rounded-2xl flex bg-white shadow-xl">
        {/* Left side - Map */}
        <div className="hidden md:block w-1/2 h-[600px] relative overflow-hidden border-r border-gray-100">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100">
            <DotMap />

            {/* Logo and text overlay */}
            <div className="absolute inset-0 flex flex-col items-center justify-center p-8 z-10">
              <div className="mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-200">
                  <ArrowRightIcon className="text-white h-6 w-6" />
                </div>
              </div>
              <h2 className="text-3xl font-bold mb-2 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                知识管理系统
              </h2>
              <p className="text-sm text-center text-gray-600 max-w-xs">
                登录以访问您的知识库，管理文章、标签和阅读统计
              </p>
            </div>
          </div>
        </div>

        {/* Right side - Sign In Form */}
        <div className="w-full md:w-1/2 p-8 md:p-10 flex flex-col justify-center bg-white">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold mb-1 text-gray-800">欢迎回来</h1>
            <p className="text-gray-500 mb-8">登录您的账户</p>

            {/* Sign In Form */}
            <form className="space-y-5" onSubmit={handleSubmit}>
              {/* Username Input */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  用户名 <span className="text-blue-500">*</span>
                </label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="请输入用户名"
                  required
                />
              </div>

              {/* Password Input */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  密码 <span className="text-blue-500">*</span>
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={isPasswordVisible ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="请输入密码"
                    required
                    className="pr-10"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-700"
                    onClick={() => setIsPasswordVisible(!isPasswordVisible)}
                  >
                    <EyeIconComponent size={18} />
                  </button>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="text-red-500 text-sm">{error}</div>
              )}

              {/* Submit Button */}
              <div
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                className="pt-2"
              >
                <Button
                  type="submit"
                  disabled={isLoading}
                  className={`w-full py-2 rounded-lg ${isHovered ? 'shadow-lg shadow-blue-200' : ''}`}
                >
                  <span className="flex items-center justify-center">
                    {isLoading ? '登录中...' : '登录'}
                    {!isLoading && <ArrowRightIcon className="ml-2 h-4 w-4" />}
                  </span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

### Step 2: 提交登录页面

```bash
git add src/pages/Login.jsx
git commit -m "feat: 创建登录页面（还原 login.html 样式）"
```

---

## Task 6: 创建布局组件

**目标:** 还原 home.html 样式的布局组件

### Step 1: 创建 Sidebar 组件

创建 `frontend/src/components/layout/Sidebar.jsx`:

```jsx
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, FileTextIcon, TagIcon, BarChartIcon, MenuIcon } from '../components/ui/Icons';

const Sidebar = ({ isOpen, onClose, user }) => {
  const location = useLocation();
  const [openSections, setOpenSections] = useState({});

  const toggleSection = (key) => {
    setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const navItems = [
    { path: '/dashboard', icon: HomeIcon, label: '仪表盘' },
    { path: '/articles', icon: FileTextIcon, label: '文章管理' },
    { path: '/articles/create', icon: FileTextIcon, label: '创建文章', indent: true },
    { path: '/tags', icon: TagIcon, label: '标签管理' },
    { path: '/reading/stats', icon: BarChartIcon, label: '阅读统计' },
  ];

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-[9998] md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:sticky top-0 left-0 h-screen z-[9999] bg-white text-black shadow-lg
        transform transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        w-64 flex flex-col
      `}>
        {/* Profile Section */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <div>
              <p className="font-semibold">{user?.username || '用户'}</p>
              <p className="text-sm text-gray-500">{user?.email || ''}</p>
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul>
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path} className={`mb-2 ${item.indent ? 'ml-4' : ''}`}>
                  <Link
                    to={item.path}
                    onClick={onClose}
                    className={`
                      flex gap-2 font-medium text-sm items-center w-full py-2 px-4 rounded-xl
                      transition-colors
                      ${isActive(item.path)
                        ? 'bg-blue-50 text-blue-600'
                        : 'hover:bg-gray-100'
                      }
                    `}
                  >
                    <Icon size={20} />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="md:hidden w-full font-medium text-sm p-3 text-center bg-blue-100 rounded-xl hover:bg-blue-200 transition-colors"
          >
            关闭菜单
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
```

### Step 2: 创建 Header 组件

创建 `frontend/src/components/layout/Header.jsx`:

```jsx
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { MenuIcon } from './ui/Icons';

const Header = ({ onMenuToggle }) => {
  const { user, logout } = useAuth();

  return (
    <div className="p-4 bg-white border-b border-gray-200 md:hidden flex justify-between items-center shadow-sm">
      <h1 className="text-xl font-bold text-gray-900">知识管理系统</h1>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-600">{user?.username}</span>
        <button
          onClick={onMenuToggle}
          aria-label="Toggle menu"
          className="focus:outline-none p-2 rounded-lg hover:bg-gray-100"
        >
          <MenuIcon />
        </button>
      </div>
    </div>
  );
};

export default Header;
```

### Step 3: 创建 MainLayout 组件

创建 `frontend/src/components/layout/MainLayout.jsx`:

```jsx
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';
import Header from './Header';

const MainLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { user } = useAuth();

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        user={user}
      />

      <div className="flex-1 ml-0 md:ml-64 transition-all duration-300">
        <Header onMenuToggle={() => setIsSidebarOpen(true)} />

        <main className="p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
```

### Step 4: 提交布局组件

```bash
git add src/components/layout
git commit -m "feat: 创建布局组件（Sidebar、Header、MainLayout）"
```

---

## Task 7: 创建仪表盘页面

**目标:** 还原 home.html 样式的仪表盘页面

### Step 1: 创建仪表盘页面

创建 `frontend/src/pages/Dashboard.jsx`:

```jsx
import React from 'react';
import Card from '../components/ui/Card';
import { HomeIcon, FileTextIcon, TagIcon, BarChartIcon } from '../components/ui/Icons';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();

  const stats = [
    { title: '总文章数', value: '0', icon: FileTextIcon, color: 'bg-blue-500', path: '/articles' },
    { title: '标签数量', value: '0', icon: TagIcon, color: 'bg-green-500', path: '/tags' },
    { title: '阅读统计', value: '查看', icon: BarChartIcon, color: 'bg-purple-500', path: '/reading/stats' },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          欢迎回来，{user?.username || '用户'}
        </h1>
        <p className="text-gray-600">
          这是您的知识管理仪表盘
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card
              key={index}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`w-12 h-12 ${stat.color} rounded-lg mb-4 flex items-center justify-center`}>
                <Icon className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-lg mb-1">{stat.title}</h3>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-100">
        <h2 className="font-semibold text-lg mb-4">快速操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/articles/create"
            className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-shadow"
          >
            <FileTextIcon className="text-blue-500" size={20} />
            <span>创建新文章</span>
          </a>
          <a
            href="/tags"
            className="flex items-center gap-3 p-4 bg-white rounded-lg hover:shadow-md transition-shadow"
          >
            <TagIcon className="text-green-500" size={20} />
            <span>管理标签</span>
          </a>
        </div>
      </Card>

      {/* Info Section */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
        <h2 className="font-semibold text-lg mb-4">系统功能</h2>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
            文章管理：上传文件或从 URL 导入
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            标签系统：组织和管理您的知识
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
            阅读统计：追踪您的阅读进度
          </li>
          <li className="flex items-center gap-2">
            <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
            搜索功能：快速找到您需要的内容
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
```

### Step 2: 提交仪表盘页面

```bash
git add src/pages/Dashboard.jsx
git commit -m "feat: 创建仪表盘页面（还原 home.html 样式）"
```

---

## Task 8: 配置路由

**目标:** 配置 React Router，整合所有页面

### Step 1: 修改 App.jsx

修改 `frontend/src/App.jsx`:

```jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="articles" element={<div>文章列表页面（待实现）</div>} />
            <Route path="articles/create" element={<div>创建文章页面（待实现）</div>} />
            <Route path="articles/:id" element={<div>文章详情页面（待实现）</div>} />
            <Route path="tags" element={<div>标签管理页面（待实现）</div>} />
            <Route path="reading/stats" element={<div>阅读统计页面（待实现）</div>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

### Step 2: 修改 main.jsx

修改 `frontend/src/main.jsx`:

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

### Step 3: 测试基础功能

```bash
npm run dev
```

访问 http://localhost:5173 测试：
1. 登录页面样式是否正确
2. 登录功能是否正常
3. 仪表盘布局是否正确

### Step 4: 提交路由配置

```bash
git add src/App.jsx src/main.jsx
git commit -m "feat: 配置路由系统，整合登录和仪表盘页面"
```

---

## Task 9: 创建文章相关 API

**目标:** 实现文章相关的 API 调用

### Step 1: 创建文章 API

创建 `frontend/src/api/article.ts`:

```typescript
import apiClient, { ApiResponse, PaginatedResponse, Article } from './client';

export interface ArticleFilters {
  page?: number;
  size?: number;
  tag_id?: number;
}

export interface ArticleCreateData {
  title: string;
  summary: string;
  keywords: string;
  tag_ids?: number[];
}

export interface UrlImportData {
  url: string;
  tag_ids?: number[];
  title?: string;
}

export const articleApi = {
  // 获取文章列表
  getArticles: async (params: ArticleFilters = {}): Promise<PaginatedResponse<Article>> => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<Article>>>('/articles/', {
      params,
    });
    return response.data;
  },

  // 获取文章详情
  getArticle: async (id: number): Promise<Article> => {
    const response = await apiClient.get<ApiResponse<Article>>(`/articles/${id}`);
    return response.data;
  },

  // 获取文章 HTML 内容
  getArticleHtml: async (id: number): Promise<Article> => {
    const response = await apiClient.get<ApiResponse<Article>>(`/articles/${id}/html`);
    return response.data;
  },

  // 上传文件创建文章
  uploadArticle: async (file: File, data: ArticleCreateData): Promise<Article> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', data.title);
    formData.append('summary', data.summary);
    formData.append('keywords', data.keywords);
    if (data.tag_ids && data.tag_ids.length > 0) {
      formData.append('tag_ids', data.tag_ids.join(','));
    }

    const response = await apiClient.post<ApiResponse<Article>>('/articles/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 从 URL 导入文章
  importFromUrl: async (data: UrlImportData): Promise<Article> => {
    const response = await apiClient.post<ApiResponse<Article>>('/articles/from-url-html', data);
    return response.data;
  },

  // 更新文章
  updateArticle: async (id: number, data: Partial<ArticleCreateData> & { tag_ids?: number[] }): Promise<Article> => {
    const response = await apiClient.put<ApiResponse<Article>>(`/articles/${id}`, data);
    return response.data;
  },

  // 删除文章
  deleteArticle: async (id: number): Promise<void> => {
    await apiClient.delete(`/articles/${id}`);
  },
};
```

### Step 2: 创建标签 API

创建 `frontend/src/api/tag.ts`:

```typescript
import apiClient, { ApiResponse, Tag } from './client';

export const tagApi = {
  // 获取所有标签
  getTags: async (): Promise<Tag[]> => {
    const response = await apiClient.get<ApiResponse<Tag[]>>('/tags/');
    return response.data;
  },

  // 获取标签详情
  getTag: async (id: number): Promise<Tag> => {
    const response = await apiClient.get<ApiResponse<Tag>>(`/tags/${id}`);
    return response.data;
  },

  // 创建标签
  createTag: async (data: { name: string; color?: string }): Promise<Tag> => {
    const response = await apiClient.post<ApiResponse<Tag>>('/tags/', data);
    return response.data;
  },

  // 更新标签
  updateTag: async (id: number, data: { name?: string; color?: string }): Promise<Tag> => {
    const response = await apiClient.put<ApiResponse<Tag>>(`/tags/${id}`, data);
    return response.data;
  },

  // 删除标签
  deleteTag: async (id: number): Promise<void> => {
    await apiClient.delete(`/tags/${id}`);
  },

  // 获取标签下的文章
  getTagArticles: async (id: number, page = 1, size = 20): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(`/tags/${id}/articles`, {
      params: { page, size },
    });
    return response.data;
  },
};
```

### Step 3: 创建阅读记录 API

创建 `frontend/src/api/reading.ts`:

```typescript
import apiClient, { ApiResponse, PaginatedResponse, ReadingStats, ReadingHistory } from './client';

export const readingApi = {
  // 开始阅读
  startReading: async (articleId: number): Promise<ReadingHistory> => {
    const response = await apiClient.post<ApiResponse<ReadingHistory>>(`/reading/articles/${articleId}/start`);
    return response.data;
  },

  // 结束阅读
  endReading: async (articleId: number, progress = 0): Promise<ReadingHistory> => {
    const response = await apiClient.post<ApiResponse<ReadingHistory>>(`/reading/articles/${articleId}/end`, {
      reading_progress: progress,
    });
    return response.data;
  },

  // 获取阅读历史
  getHistory: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingHistory>> => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<ReadingHistory>>>('/reading/history', {
      params: { page, size },
    });
    return response.data;
  },

  // 获取阅读统计
  getStats: async (page = 1, size = 20): Promise<PaginatedResponse<ReadingStats>> => {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<ReadingStats>>>('/reading/stats', {
      params: { page, size },
    });
    return response.data;
  },
};
```

### Step 4: 提交 API 模块

```bash
git add src/api/article.ts src/api/tag.ts src/api/reading.ts
git commit -m "feat: 实现文章、标签、阅读记录 API"
```

---

## Task 10: 创建文章列表页面

**目标:** 实现文章列表页面，支持分页、搜索、标签筛选

### Step 1: 创建 ArticleContext

创建 `frontend/src/contexts/ArticleContext.jsx`:

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { articleApi } from '../api/article';
import { tagApi } from '../api/tag';

const ArticleContext = createContext(undefined);

export const useArticles = () => {
  const context = useContext(ArticleContext);
  if (!context) {
    throw new Error('useArticles must be used within an ArticleProvider');
  }
  return context;
};

export const ArticleProvider = ({ children }) => {
  const [articles, setArticles] = useState([]);
  const [tags, setTags] = useState([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取标签列表
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const data = await tagApi.getTags();
        setTags(data);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
      }
    };
    fetchTags();
  }, []);

  const fetchArticles = async (params = {}) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await articleApi.getArticles({
        page: currentPage,
        size: pageSize,
        ...params,
      });
      setArticles(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err.message || '获取文章列表失败');
    } finally {
      setIsLoading(false);
    }
  };

  const createArticle = async (data) => {
    setIsLoading(true);
    try {
      await articleApi.uploadArticle(data.file, data);
      await fetchArticles();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '创建文章失败' };
    } finally {
      setIsLoading(false);
    }
  };

  const importFromUrl = async (data) => {
    setIsLoading(true);
    try {
      await articleApi.importFromUrl(data);
      await fetchArticles();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '导入文章失败' };
    } finally {
      setIsLoading(false);
    }
  };

  const deleteArticle = async (id) => {
    try {
      await articleApi.deleteArticle(id);
      setArticles(articles.filter(a => a.id !== id));
      setTotal(prev => prev - 1);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '删除文章失败' };
    }
  };

  const value = {
    articles,
    tags,
    total,
    currentPage,
    pageSize,
    isLoading,
    error,
    fetchArticles,
    createArticle,
    importFromUrl,
    deleteArticle,
    setCurrentPage,
  };

  return <ArticleContext.Provider value={value}>{children}</ArticleContext.Provider>;
};
```

### Step 2: 创建 ArticleCard 组件

创建 `frontend/src/components/ArticleCard.jsx`:

```jsx
import React from 'react';
import { Link } from 'react-router-dom';
import Card from './ui/Card';
import { FileTextIcon, EyeIcon } from './ui/Icons';

const ArticleCard = ({ article, onDelete }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <Link
            to={`/articles/${article.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors"
          >
            {article.title}
          </Link>
        </div>
        <button
          onClick={() => onDelete(article.id)}
          className="text-gray-400 hover:text-red-500 transition-colors ml-2"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
      </div>

      {article.summary && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{article.summary}</p>
      )}

      {article.keywords && (
        <p className="text-xs text-gray-500 mb-3">
          关键词: {article.keywords}
        </p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <EyeIcon size={14} />
            {article.view_count || 0}
          </span>
          <span>{formatDate(article.created_at)}</span>
        </div>

        {article.tags && article.tags.length > 0 && (
          <div className="flex gap-1">
            {article.tags.map(tag => (
              <span
                key={tag.id}
                className="px-2 py-0.5 rounded text-xs text-white"
                style={{ backgroundColor: tag.color }}
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default ArticleCard;
```

### Step 3: 创建文章列表页面

创建 `frontend/src/pages/ArticleList.jsx`:

```jsx
import React, { useEffect } from 'react';
import { useArticles } from '../contexts/ArticleContext';
import ArticleCard from '../components/ArticleCard';
import Input from '../components/ui/Input';

const ArticleList = () => {
  const {
    articles,
    tags,
    total,
    currentPage,
    pageSize,
    isLoading,
    error,
    fetchArticles,
    deleteArticle,
    setCurrentPage,
  } = useArticles();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState(null);

  useEffect(() => {
    fetchArticles();
  }, [currentPage]);

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchArticles({
      ...(searchQuery && { q: searchQuery }),
      ...(selectedTag && { tag_id: selectedTag }),
    });
  };

  const handleTagFilter = (tagId) => {
    setSelectedTag(tagId === selectedTag ? null : tagId);
    setCurrentPage(1);
    fetchArticles({
      q: searchQuery,
      ...(tagId !== selectedTag && { tag_id: tagId }),
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm('确定要删除这篇文章吗？')) {
      const result = await deleteArticle(id);
      if (!result.success) {
        alert(result.error);
      }
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">文章管理</h1>
        <p className="text-gray-600">管理和查看您的文章</p>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100 mb-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索文章..."
            className="flex-1"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            搜索
          </button>
        </form>

        {/* Tag Filters */}
        {tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-gray-600 mr-2">标签筛选:</span>
            {tags.map(tag => (
              <button
                key={tag.id}
                onClick={() => handleTagFilter(tag.id)}
                className={`
                  px-3 py-1 rounded-full text-sm transition-colors
                  ${selectedTag === tag.id
                    ? 'text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
                style={selectedTag === tag.id ? { backgroundColor: tag.color } : {}}
              >
                {tag.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Articles List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      ) : articles.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无文章，<a href="/articles/create" className="text-blue-600 hover:underline">创建第一篇文章</a>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {articles.map(article => (
              <ArticleCard key={article.id} article={article} onDelete={handleDelete} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <span className="text-sm text-gray-600">
                第 {currentPage} / {totalPages} 页，共 {total} 篇
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ArticleList;
```

### Step 4: 提交文章列表页面

```bash
git add src/contexts/ArticleContext.jsx src/components/ArticleCard.jsx src/pages/ArticleList.jsx
git commit -m "feat: 实现文章列表页面（分页、搜索、标签筛选）"
```

---

## Task 11: 创建文章创建页面

**目标:** 实现文章创建页面，支持文件上传和 URL 导入

### Step 1: 创建文章创建页面

创建 `frontend/src/pages/ArticleCreate.jsx`:

```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useArticles } from '../contexts/ArticleContext';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';

const ArticleCreate = () => {
  const navigate = useNavigate();
  const { tags, createArticle, importFromUrl, isLoading } = useArticles();

  const [mode, setMode] = useState('file'); // 'file' or 'url'
  const [fileData, setFileData] = useState({
    file: null,
    title: '',
    summary: '',
    keywords: '',
    tag_ids: [],
  });
  const [urlData, setUrlData] = useState({
    url: '',
    tag_ids: [],
    title: '',
  });
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFileData({ ...fileData, file: e.target.files[0] });
  };

  const handleTagToggle = (tagId) => {
    const currentData = mode === 'file' ? fileData : urlData;
    const newTagIds = currentData.tag_ids.includes(tagId)
      ? currentData.tag_ids.filter(id => id !== tagId)
      : [...currentData.tag_ids, tagId];

    if (mode === 'file') {
      setFileData({ ...fileData, tag_ids: newTagIds });
    } else {
      setUrlData({ ...urlData, tag_ids: newTagIds });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (mode === 'file') {
      if (!fileData.file || !fileData.title || !fileData.summary || !fileData.keywords) {
        setError('请填写所有必填字段');
        return;
      }
      const result = await createArticle(fileData);
      if (result.success) {
        navigate('/articles');
      } else {
        setError(result.error);
      }
    } else {
      if (!urlData.url) {
        setError('请输入文章 URL');
        return;
      }
      const result = await importFromUrl(urlData);
      if (result.success) {
        navigate('/articles');
      } else {
        setError(result.error);
      }
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">创建文章</h1>
        <p className="text-gray-600">通过文件上传或 URL 导入创建新文章</p>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode('file')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            mode === 'file'
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          文件上传
        </button>
        <button
          onClick={() => setMode('url')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            mode === 'url'
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          URL 导入
        </button>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
          )}

          {mode === 'file' ? (
            <>
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  HTML 文件 <span className="text-blue-500">*</span>
                </label>
                <input
                  type="file"
                  accept=".html,.htm"
                  onChange={handleFileChange}
                  className="w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
                />
                {fileData.file && (
                  <p className="mt-2 text-sm text-gray-600">已选择: {fileData.file.name}</p>
                )}
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  标题 <span className="text-blue-500">*</span>
                </label>
                <Input
                  type="text"
                  value={fileData.title}
                  onChange={(e) => setFileData({ ...fileData, title: e.target.value })}
                  placeholder="请输入文章标题"
                  required
                />
              </div>

              {/* Summary */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  摘要 <span className="text-blue-500">*</span>
                </label>
                <textarea
                  value={fileData.summary}
                  onChange={(e) => setFileData({ ...fileData, summary: e.target.value })}
                  placeholder="请输入文章摘要"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              {/* Keywords */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  关键词 <span className="text-blue-500">*</span>
                </label>
                <Input
                  type="text"
                  value={fileData.keywords}
                  onChange={(e) => setFileData({ ...fileData, keywords: e.target.value })}
                  placeholder="请输入关键词，用逗号分隔"
                  required
                />
              </div>
            </>
          ) : (
            <>
              {/* URL Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  文章 URL <span className="text-blue-500">*</span>
                </label>
                <Input
                  type="url"
                  value={urlData.url}
                  onChange={(e) => setUrlData({ ...urlData, url: e.target.value })}
                  placeholder="https://example.com/article"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">
                  系统将自动抓取内容并使用 AI 提取标题、摘要和关键词
                </p>
              </div>

              {/* Custom Title (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  自定义标题（可选）
                </label>
                <Input
                  type="text"
                  value={urlData.title}
                  onChange={(e) => setUrlData({ ...urlData, title: e.target.value })}
                  placeholder="留空则由 AI 自动提取"
                />
              </div>
            </>
          )}

          {/* Tag Selection */}
          {tags.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择标签
              </label>
              <div className="flex flex-wrap gap-2">
                {tags.map(tag => {
                  const isSelected = (mode === 'file' ? fileData.tag_ids : urlData.tag_ids).includes(tag.id);
                  return (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => handleTagToggle(tag.id)}
                      className={`
                        px-3 py-1 rounded-full text-sm transition-colors
                        ${isSelected ? 'text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
                      `}
                      style={isSelected ? { backgroundColor: tag.color } : {}}
                    >
                      {tag.name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-colors disabled:opacity-50"
            >
              {isLoading ? '处理中...' : mode === 'file' ? '上传文章' : '导入文章'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/articles')}
              className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default ArticleCreate;
```

### Step 2: 更新 App.jsx 路由

修改 `frontend/src/App.jsx`，添加文章创建和列表路由：

```jsx
import ArticleList from './pages/ArticleList';
import ArticleCreate from './pages/ArticleCreate';

// 在路由配置中更新：
<Route path="articles" element={<ArticleList />} />
<Route path="articles/create" element={<ArticleCreate />} />
```

### Step 3: 提交文章创建页面

```bash
git add src/pages/ArticleCreate.jsx src/App.jsx
git commit -m "feat: 实现文章创建页面（文件上传和URL导入）"
```

---

## Task 12: 创建标签管理页面

**目标:** 实现标签管理页面，支持 CRUD 操作

### Step 1: 创建 TagContext

创建 `frontend/src/contexts/TagContext.jsx`:

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { tagApi } from '../api/tag';

const TagContext = createContext(undefined);

export const useTags = () => {
  const context = useContext(TagContext);
  if (!context) {
    throw new Error('useTags must be used within a TagProvider');
  }
  return context;
};

export const TagProvider = ({ children }) => {
  const [tags, setTags] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTags = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await tagApi.getTags();
      setTags(data);
    } catch (err) {
      setError(err.message || '获取标签失败');
    } finally {
      setIsLoading(false);
    }
  };

  const createTag = async (data) => {
    try {
      const newTag = await tagApi.createTag(data);
      setTags([...tags, newTag]);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '创建标签失败' };
    }
  };

  const updateTag = async (id, data) => {
    try {
      const updatedTag = await tagApi.updateTag(id, data);
      setTags(tags.map(t => t.id === id ? updatedTag : t));
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '更新标签失败' };
    }
  };

  const deleteTag = async (id) => {
    try {
      await tagApi.deleteTag(id);
      setTags(tags.filter(t => t.id !== id));
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || '删除标签失败' };
    }
  };

  const value = {
    tags,
    isLoading,
    error,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
  };

  return <TagContext.Provider value={value}>{children}</TagContext.Provider>;
};
```

### Step 2: 创建标签管理页面

创建 `frontend/src/pages/TagManage.jsx`:

```jsx
import React, { useState, useEffect } from 'react';
import { useTags } from '../contexts/TagContext';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';

const TagManage = () => {
  const { tags, isLoading, error, fetchTags, createTag, updateTag, deleteTag } = useTags();

  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ name: '', color: '#3b82f6' });
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchTags();
  }, []);

  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    const result = editingId
      ? await updateTag(editingId, formData)
      : await createTag(formData);

    if (result.success) {
      setMessage(editingId ? '标签已更新' : '标签已创建');
      setIsCreating(false);
      setEditingId(null);
      setFormData({ name: '', color: '#3b82f6' });
      setTimeout(() => setMessage(''), 3000);
    } else {
      setMessage(result.error);
    }
  };

  const handleEdit = (tag) => {
    setEditingId(tag.id);
    setFormData({ name: tag.name, color: tag.color });
    setIsCreating(false);
  };

  const handleDelete = async (id) => {
    if (window.confirm('确定要删除这个标签吗？')) {
      const result = await deleteTag(id);
      if (result.success) {
        setMessage('标签已删除');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(result.error);
      }
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingId(null);
    setFormData({ name: '', color: '#3b82f6' });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">标签管理</h1>
        <p className="text-gray-600">管理和组织您的文章标签</p>
      </div>

      {message && (
        <div className={`mb-4 p-4 rounded-lg ${message.includes('失败') || message.includes('错误') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
          {message}
        </div>
      )}

      {/* Create/Edit Form */}
      {(isCreating || editingId) && (
        <Card className="mb-6">
          <h2 className="text-lg font-semibold mb-4">
            {editingId ? '编辑标签' : '创建新标签'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                标签名称
              </label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="请输入标签名称"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                标签颜色
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {colors.map(color => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => setFormData({ ...formData, color })}
                    className={`
                      w-8 h-8 rounded-full transition-transform
                      ${formData.color === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''}
                    `}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
              <Input
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-20 h-10"
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                {editingId ? '更新' : '创建'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
            </div>
          </form>
        </Card>
      )}

      {/* Create Button */}
      {!isCreating && !editingId && (
        <button
          onClick={() => setIsCreating(true)}
          className="mb-6 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          + 创建新标签
        </button>
      )}

      {/* Tags List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      ) : tags.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无标签，点击上方按钮创建第一个标签
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tags.map(tag => (
            <Card key={tag.id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                  style={{ backgroundColor: tag.color }}
                >
                  {tag.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{tag.name}</h3>
                  <p className="text-xs text-gray-500">{tag.color}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(tag)}
                  className="p-2 text-gray-400 hover:text-blue-500 transition-colors"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleDelete(tag.id)}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TagManage;
```

### Step 3: 更新 App.jsx 和 main.jsx

修改 `frontend/src/App.jsx`，添加 TagProvider 和标签路由：

```jsx
import { AuthProvider } from './contexts/AuthContext';
import { ArticleProvider } from './contexts/ArticleContext';
import { TagProvider } from './contexts/TagContext';
import TagManage from './pages/TagManage';

// 在路由配置中更新：
<Route path="tags" element={<TagManage />} />

// 更新 Providers 包裹：
<AuthProvider>
  <ArticleProvider>
    <TagProvider>
      <BrowserRouter>
        {/* 路由配置 */}
      </BrowserRouter>
    </TagProvider>
  </ArticleProvider>
</AuthProvider>
```

### Step 4: 提交标签管理页面

```bash
git add src/contexts/TagContext.jsx src/pages/TagManage.jsx src/App.jsx
git commit -m "feat: 实现标签管理页面（CRUD操作）"
```

---

## Task 13: 创建阅读统计页面

**目标:** 实现阅读统计页面

### Step 1: 创建阅读统计页面

创建 `frontend/src/pages/ReadingStats.jsx`:

```jsx
import React, { useState, useEffect } from 'react';
import { readingApi } from '../api/reading';
import Card from '../components/ui/Card';
import { BarChartIcon, ClockIcon, EyeIcon, BookOpenIcon } from './components/ui/Icons';

const ReadingStats = () => {
  const [stats, setStats] = useState([]);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('stats'); // 'stats' or 'history'

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (activeTab === 'stats') {
        const data = await readingApi.getStats();
        setStats(data.items || []);
      } else {
        const data = await readingApi.getHistory();
        setHistory(data.items || []);
      }
    } catch (err) {
      setError(err.message || '获取数据失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`;
    }
    return `${minutes}分钟`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">阅读统计</h1>
        <p className="text-gray-600">查看您的阅读历史和统计数据</p>
      </div>

      {/* Tab Toggle */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setActiveTab('stats')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'stats'
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          文章统计
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'history'
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
          }`}
        >
          阅读历史
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">{error}</div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : activeTab === 'stats' ? (
        <>
          {stats.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              暂无阅读统计数据
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {stats.map(stat => (
                <Card key={stat.article_id}>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <BookOpenIcon className="text-purple-500" size={24} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                        {stat.article_title}
                      </h3>
                      <div className="space-y-1 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <EyeIcon size={14} />
                          <span>阅读 {stat.total_views} 次</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <ClockIcon size={14} />
                          <span>累计 {formatDuration(stat.total_duration)}</span>
                        </div>
                        {stat.last_read_at && (
                          <div className="text-xs text-gray-500">
                            最后阅读: {formatDate(stat.last_read_at)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </>
      ) : (
        <>
          {history.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              暂无阅读历史记录
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">文章</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">开始时间</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时长</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">进度</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {history.map(record => (
                    <tr key={record.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <a
                          href={`/articles/${record.article_id}`}
                          className="text-blue-600 hover:underline"
                        >
                          {record.article_title}
                        </a>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {formatDate(record.started_at)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {record.reading_duration > 0 ? formatDuration(record.reading_duration) : '-'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 w-24">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${record.reading_progress}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-600">{record.reading_progress}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ReadingStats;
```

### Step 2: 更新 App.jsx 路由

修改 `frontend/src/App.jsx`，添加阅读统计路由：

```jsx
import ReadingStats from './pages/ReadingStats';

// 在路由配置中更新：
<Route path="reading/stats" element={<ReadingStats />} />
```

### Step 3: 添加 ClockIcon 到 Icons.jsx

修改 `frontend/src/components/ui/Icons.jsx`，添加缺失的图标：

```jsx
export const ClockIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

export const BookOpenIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
);
```

### Step 4: 提交阅读统计页面

```bash
git add src/pages/ReadingStats.jsx src/components/ui/Icons.jsx src/App.jsx
git commit -m "feat: 实现阅读统计页面"
```

---

## Task 14: 创建文章详情页面

**目标:** 实现文章详情页面

### Step 1: 创建文章详情页面

创建 `frontend/src/pages/ArticleDetail.jsx`:

```jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { articleApi } from '../api/article';
import { readingApi } from '../api/reading';
import Card from '../components/ui/Card';
import { EyeIcon, CalendarIcon, TagIcon } from './components/ui/Icons';

const ArticleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [htmlContent, setHtmlContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchArticle();
    // 记录阅读开始
    readingApi.startReading(parseInt(id)).catch(console.error);
  }, [id]);

  const fetchArticle = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [articleData, htmlData] = await Promise.all([
        articleApi.getArticle(parseInt(id)),
        articleApi.getArticleHtml(parseInt(id)),
      ]);
      setArticle(articleData);
      setHtmlContent(htmlData.html_content || '');
    } catch (err) {
      setError(err.message || '获取文章详情失败');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
        <button
          onClick={() => navigate('/articles')}
          className="mt-4 px-4 py-2 text-blue-600 hover:underline"
        >
          返回文章列表
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <Link
        to="/articles"
        className="inline-flex items-center gap-2 text-blue-600 hover:underline mb-6"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        返回文章列表
      </Link>

      {/* Article Header */}
      <Card className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>

        {/* Meta Info */}
        <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-2">
            <EyeIcon size={16} />
            <span>{article.view_count || 0} 次浏览</span>
          </div>
          <div className="flex items-center gap-2">
            <CalendarIcon size={16} />
            <span>{formatDate(article.created_at)}</span>
          </div>
        </div>

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex items-center gap-2 mb-4">
            <TagIcon size={16} className="text-gray-500" />
            <div className="flex gap-2">
              {article.tags.map(tag => (
                <span
                  key={tag.id}
                  className="px-3 py-1 rounded-full text-sm text-white"
                  style={{ backgroundColor: tag.color }}
                >
                  {tag.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        {article.summary && (
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">摘要</h3>
            <p className="text-gray-600">{article.summary}</p>
          </div>
        )}

        {/* Keywords */}
        {article.keywords && (
          <div className="border-t border-gray-200 pt-4 mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">关键词</h3>
            <p className="text-gray-600">{article.keywords}</p>
          </div>
        )}

        {/* Source URL */}
        {article.source_url && (
          <div className="border-t border-gray-200 pt-4 mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">来源</h3>
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline text-sm break-all"
            >
              {article.source_url}
            </a>
          </div>
        )}
      </Card>

      {/* Article Content */}
      {htmlContent ? (
        <Card>
          <div
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: htmlContent }}
          />
        </Card>
      ) : (
        <Card>
          <div className="text-center py-12 text-gray-500">
            此文章没有可显示的内容
          </div>
        </Card>
      )}
    </div>
  );
};

export default ArticleDetail;
```

### Step 2: 添加 CalendarIcon 到 Icons.jsx

修改 `frontend/src/components/ui/Icons.jsx`：

```jsx
export const CalendarIcon = ({ className = '', size = 20 }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);
```

### Step 3: 更新 App.jsx 路由

修改 `frontend/src/App.jsx`，添加文章详情路由：

```jsx
import ArticleDetail from './pages/ArticleDetail';

// 在路由配置中更新：
<Route path="articles/:id" element={<ArticleDetail />} />
```

### Step 4: 提交文章详情页面

```bash
git add src/pages/ArticleDetail.jsx src/components/ui/Icons.jsx src/App.jsx
git commit -m "feat: 实现文章详情页面"
```

---

## Task 15: 最终优化和测试

**目标:** 完成项目并进行最终测试

### Step 1: 添加全局样式

修改 `frontend/src/index.css`，添加自定义样式：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Line clamp utility */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Prose styles for article content */
.prose {
  color: #374151;
  max-width: 65ch;
}

.prose h1 {
  font-size: 2.25em;
  margin-top: 0;
  margin-bottom: 0.8888889em;
  line-height: 1.1111111;
}

.prose h2 {
  font-size: 1.5em;
  margin-top: 2em;
  margin-bottom: 1em;
  line-height: 1.3333333;
}

.prose p {
  margin-top: 1.25em;
  margin-bottom: 1.25em;
}

.prose a {
  color: #2563eb;
  text-decoration: underline;
}

.prose strong {
  color: #111827;
  font-weight: 600;
}

.prose code {
  color: #111827;
  font-weight: 600;
  font-size: 0.875em;
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
}

.prose pre {
  color: #e5e7eb;
  background-color: #1f2937;
  overflow-x: auto;
  font-size: 0.875em;
  border-radius: 0.375rem;
  padding: 0.8571429em 1.1428571em;
}

.prose img {
  margin-top: 2em;
  margin-bottom: 2em;
  border-radius: 0.375rem;
}

.prose ul, .prose ol {
  margin-top: 1.25em;
  margin-bottom: 1.25em;
  padding-left: 1.625em;
}

.prose li {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}
```

### Step 2: 添加环境变量配置

创建 `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8022/api/v1
```

创建 `frontend/.env.development`:

```env
VITE_API_BASE_URL=http://localhost:8022/api/v1
```

创建 `frontend/.env.production`:

```env
VITE_API_BASE_URL=/api/v1
```

### Step 3: 更新 API 客户端使用环境变量

修改 `frontend/src/api/client.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022/api/v1';
```

### Step 4: 添加 package.json 脚本

修改 `frontend/package.json`，确保有以下脚本：

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext jsx --ext js"
  }
}
```

### Step 5: 创建 .gitignore

创建 `frontend/.gitignore`:

```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment variables
.env.local
.env.*.local
```

### Step 6: 最终测试

```bash
# 启动开发服务器
npm run dev
```

测试清单：
- [ ] 登录页面显示正常，样式正确
- [ ] 登录功能正常
- [ ] 登录后跳转到仪表盘
- [ ] 仪表盘布局和样式正确
- [ ] 侧边栏导航正常工作
- [ ] 文章列表页面显示正常
- [ ] 文章搜索功能正常
- [ ] 标签筛选功能正常
- [ ] 分页功能正常
- [ ] 文章创建页面（文件上传）正常
- [ ] 文章创建页面（URL导入）正常
- [ ] 文章详情页面显示正常
- [ ] 标签管理功能正常
- [ ] 阅读统计页面显示正常
- [ ] 登出功能正常
- [ ] 路由守卫正常工作（未登录无法访问受保护页面）

### Step 7: 构建生产版本

```bash
npm run build
```

### Step 8: 提交最终代码

```bash
git add .
git commit -m "feat: 完成知识系统前端开发，包含所有功能模块"
```

---

## 实施计划完成

所有任务已完成。前端项目包含以下功能：

1. ✅ 用户登录（还原 login.html 样式）
2. ✅ 仪表盘（还原 home.html 样式）
3. ✅ 文章列表（分页、搜索、标签筛选）
4. ✅ 文章创建（文件上传、URL导入）
5. ✅ 文章详情
6. ✅ 标签管理（CRUD）
7. ✅ 阅读统计
8. ✅ 响应式布局
9. ✅ 路由守卫
10. ✅ Token 自动刷新

**技术栈:** Vite + React + Tailwind CSS + React Router + Context API + Axios

**运行项目:**
```bash
cd frontend
npm install
npm run dev1

```

访问 http://localhost:5173 查看应用。

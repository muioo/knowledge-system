import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // 启用 TypeScript 的 React JSX 运行时
      jsxRuntime: 'automatic',
    }),
  ],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    proxy: {
      // 代理所有 /api 请求到后端
      '/api': {
        target: 'http://localhost:8022',
        changeOrigin: true,
        secure: false,
        // 不重写路径
      },
    },
  },
})

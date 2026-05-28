<<<<<<< HEAD
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // 修改为服务器后端ip:port
        target: 'http://localhost:8022',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
})
=======
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
>>>>>>> d00c5f1e62fbececc7e9b8e88bfcf89eddc0f08a

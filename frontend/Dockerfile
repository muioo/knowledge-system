# ===== 构建阶段：在 Docker 内编译前端静态资源，无需本地预先构建 dist =====
FROM node:20-alpine AS build

WORKDIR /app

# 可注入的同源 API 路径（compose 里默认 /api/v1，经 nginx 反代到后端）
ARG VITE_API_BASE_URL=/api/v1

# 先复制依赖清单再安装，充分利用构建缓存
COPY package.json package-lock.json ./
RUN npm ci

# 复制源码
COPY . .

# 将构建期参数写入 .env.production，确保 Vite 一定能读到 VITE_API_BASE_URL
RUN echo "VITE_API_BASE_URL=$VITE_API_BASE_URL" > .env.production

RUN npm run build

# ===== 运行阶段：nginx 承载静态资源 + 反向代理 API =====
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# 默认前台运行，跟随容器生命周期
CMD ["nginx", "-g", "daemon off;"]
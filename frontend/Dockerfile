# ===== 构建阶段：在 Docker 内编译前端静态资源，无需本地预先构建 dist =====
FROM node:20-alpine AS build

WORKDIR /app

# 先复制依赖清单再安装，充分利用构建缓存
COPY package.json package-lock.json ./
RUN npm ci

# 复制源码
COPY . .

RUN npm run build

# ===== 运行阶段：nginx 承载静态资源 + 反向代理 API =====
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# 默认前台运行，跟随容器生命周期
CMD ["nginx", "-g", "daemon off;"]
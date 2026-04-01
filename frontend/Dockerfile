# 生产阶段 - 直接使用本地构建好的 dist 目录
FROM nginx:alpine

# 复制本地已构建的 dist 目录（通过 docker-compose 挂载或复制）
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

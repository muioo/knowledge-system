# 图片请求失败问题排查与解决方案

## 问题描述

在服务器部署后，文章详情页面的图片无法正常显示，出现 404 错误。

**错误表现**：
- 浏览器控制台显示图片请求失败：`/api/v1/media/articles/7/images/img_0002.png` 返回 404
- 前端构建的静态资源正常加载，只有后端 API 返回的图片无法访问

**环境信息**：
- 部署方式：Docker Compose
- 前端：React + Vite，通过 Nginx 提供服务
- 后端：FastAPI + TortoiseORM
- 服务器：阿里云 ECS（Ubuntu/CentOS）

---

## 问题原因分析

经过排查，发现存在两个主要问题：

### 问题 1：前端硬编码 localhost

**位置**：`frontend/src/pages/ArticleDetail.tsx`

```typescript
// ❌ 错误代码
const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
if (isDev) {
  htmlContent = htmlContent.replace(/src="\/api\/v1\/media\//g, 'src="http://localhost:8022/api/v1/media/');
}
```

**问题**：
- 在开发环境判断逻辑中，硬编码了 `http://localhost:8022`
- 在 Docker 环境中，前端容器无法访问 `localhost:8022`
- 导致所有图片请求都指向 `localhost`，而不是通过 Nginx 代理

### 问题 2：Nginx 静态资源缓存规则冲突

**位置**：`frontend/nginx.conf`

```nginx
# ❌ 错误配置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location /api/ {
    proxy_pass http://backend:8022;
    # ...
}
```

**问题**：
- Nginx location 匹配优先级：**正则匹配 > 前缀匹配**
- 请求 `/api/v1/media/articles/7/images/img_0002.png` 时，先被正则规则 `~* \.png$` 匹配
- 正则规则没有配置 root，默认从 `/usr/share/nginx/html` 查找文件
- 文件不存在，返回 404
- **`location /api/` 的代理规则根本没有生效**

---

## 排查步骤

### 步骤 1：检查后端文件是否存在

```bash
# 检查容器内文件路径
docker exec knowledge-backend ls -la /app/backend/uploads/articles/7/images/

# 预期输出：
# -rw-r--r-- 1 root root  50138 Apr  2 03:41 img_0002.png
```

**如果文件不存在**：检查 Docker volumes 挂载配置
```bash
# 查看 docker-compose.yml 中的挂载配置
cat docker-compose.yml | grep -A 5 "volumes:"
```

### 步骤 2：检查后端 API 是否正常

```bash
# 从 frontend 容器测试后端连接
docker exec knowledge-frontend curl -v http://backend:8022/api/v1/media/articles/7/images/img_0002.png

# 预期输出：
# < HTTP/1.1 200 OK
# < content-type: image/png
```

**如果返回 404**：检查后端路由配置
```bash
# 查看后端路由注册
docker exec knowledge-backend python -c "
from backend.settings.config import settings
print(f'upload_dir: {settings.upload_dir}')
import os
print(f'upload_dir exists: {os.path.exists(settings.upload_dir)}')
"
```

**如果返回 405 Method Not Allowed**：这是正常的，因为使用了 HEAD 方法（curl -I），改用 GET：
```bash
docker exec knowledge-frontend curl http://backend:8022/api/v1/media/articles/7/images/img_0002.png
```

### 步骤 3：检查 Nginx 配置

```bash
# 查看容器内的 Nginx 配置
docker exec knowledge-frontend cat /etc/nginx/conf.d/default.conf

# 检查是否有问题的静态资源缓存规则
docker exec knowledge-frontend cat /etc/nginx/conf.d/default.conf | grep -A 3 "location ~*"
```

**预期看到**：
```nginx
# ✅ 正确配置：只缓存前端自己的资源
location ~* ^/assets/.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
}

# ❌ 错误配置：会拦截所有 png 文件
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
}
```

### 步骤 4：测试完整链路

```bash
# 通过 Nginx 访问（正确的访问方式）
curl -I http://localhost:5173/api/v1/media/articles/7/images/img_0002.png

# 预期输出：
# HTTP/1.1 200 OK
# Content-Type: image/png
```

**如果返回 404**：Nginx 配置有问题，需要更新配置并重建容器

**如果返回 405 Method Not Allowed**：这是正常的，`curl -I` 使用 HEAD 方法，改用 GET 测试：
```bash
curl http://localhost:5173/api/v1/media/articles/7/images/img_0002.png --output /tmp/test.png
file /tmp/test.png
```

---

## 解决方案

### 方案 1：修复前端代码

**文件**：`frontend/src/pages/ArticleDetail.tsx`

**修改前**：
```typescript
const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
if (isDev) {
  htmlContent = htmlContent.replace(/src="\/api\/v1\/media\//g, 'src="http://localhost:8022/api/v1/media/');
}
```

**修改后**：
```typescript
// 根据环境变量判断是否为开发环境
const apiBaseUrl = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1';

// 判断是否为开发环境（API URL 以 http 开头）
const isDev = apiBaseUrl.startsWith('http');

if (isDev) {
  // 开发环境：使用完整 API 地址访问后端（支持 Docker 服务名）
  const mediaBaseUrl = apiBaseUrl.replace(/\/api\/v1$/, '') + '/api/v1/media';
  htmlContent = htmlContent.replace(/src="\/api\/v1\/media\//g, `src="${mediaBaseUrl}/`);
}
// 生产环境：保持相对路径，通过 Nginx 代理
```

**原理**：
- 开发环境（`VITE_API_BASE_URL=http://localhost:8022/api/v1`）：使用完整 URL
- 生产环境（`VITE_API_BASE_URL=/api/v1`）：使用相对路径，通过 Nginx 代理

### 方案 2：修复 Nginx 配置

**文件**：`frontend/nginx.conf`

**修改前**：
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8022;
        # ...
    }

    # ❌ 问题：会拦截所有 png 文件，包括 API 请求
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**修改后**：
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;

    # ✅ 只缓存前端自己的资源（/assets/ 路径）
    location ~* ^/assets/.*\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 请求代理到后端
    location /api/ {
        proxy_pass http://backend:8022;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # 前端 SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**原理**：
- 将静态资源缓存规则限制为 `/assets/` 路径
- 确保 `/api/` 路径的所有请求都被代理到后端
- 调整 location 顺序，API 代理放在 SPA fallback 之前

### 方案 3：优化 Dockerfile

**文件**：`frontend/Dockerfile`

**修改前**：
```dockerfile
FROM nginx:alpine

COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**修改后**：
```dockerfile
FROM nginx:alpine

# 只复制 nginx.conf，dist 通过 volumes 挂载
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**原理**：
- `docker-compose.yml` 已通过 volumes 挂载 dist 目录：`./frontend/dist:/usr/share/nginx/html:ro`
- Dockerfile 中不需要再复制 dist，避免构建时找不到 dist 目录的问题

---

## 部署步骤

### 本地开发环境

```bash
# 1. 修改代码后重新构建前端
cd frontend
npm run build

# 2. 提交并推送
git add .
git commit -m "fix: 修复图片访问问题"
git push origin production
```

### 服务器部署

```bash
# 1. 拉取最新代码
cd /path/to/knowledge-system
git pull origin production

# 2. 验证文件已更新
cat frontend/nginx.conf | grep -A 2 "location ~*"
cat frontend/Dockerfile

# 3. 停止并删除旧容器
docker compose down frontend

# 4. 重新构建并启动
docker compose build --no-cache frontend
docker compose up -d frontend

# 5. 验证 Nginx 配置已更新
docker exec knowledge-frontend cat /etc/nginx/conf.d/default.conf | grep -A 2 "location ~*"

# 6. 测试图片访问
curl http://localhost:5173/api/v1/media/articles/7/images/img_0002.png --output /tmp/test.png
file /tmp/test.png

# 预期输出：/tmp/test.png: PNG image data
```

---

## 常见问题排查

### Q1: curl -I 返回 405 Method Not Allowed

**原因**：`curl -I` 使用 HEAD 方法，后端只支持 GET

**解决**：
```bash
# 使用 GET 方法
curl http://localhost:5173/api/v1/media/articles/7/images/img_0002.png --output /tmp/test.png

# 或使用 wget
wget -O /tmp/test.png http://localhost:5173/api/v1/media/articles/7/images/img_0002.png
```

### Q2: Docker 构建失败：failed to calculate checksum of ref: "/dist": not found

**原因**：Dockerfile 中 `COPY dist` 在构建时找不到 dist 目录

**解决**：
```bash
# 方案 1：修改 Dockerfile，移除 COPY dist（推荐）
# 因为 docker-compose.yml 已通过 volumes 挂载 dist

# 方案 2：如果必须 COPY，确保在正确的目录构建
cd /path/to/knowledge-system
docker compose build --no-cache frontend
```

### Q3: 更新代码后图片仍然 404

**原因**：Docker 镜像使用了缓存，nginx.conf 没有更新

**解决**：
```bash
# 强制重新构建（不使用缓存）
docker compose build --no-cache frontend
docker compose up -d frontend

# 验证配置
docker exec knowledge-frontend cat /etc/nginx/conf.d/default.conf
```

### Q4: 后端文件存在但 API 返回 404

**排查步骤**：
```bash
# 1. 检查后端 upload_dir 配置
docker exec knowledge-backend python -c "from backend.settings.config import settings; print(settings.upload_dir)"

# 2. 检查文件是否在正确的路径
docker exec knowledge-backend ls -la /app/backend/uploads/articles/7/images/

# 3. 检查容器内挂载
docker exec knowledge-backend ls -la /app/backend/uploads/

# 4. 查看后端日志
docker logs knowledge-backend --tail 50
```

---

## 架构说明

### 正确的请求流程

```
浏览器请求: http://服务器IP:5173/api/v1/media/articles/7/images/img_0002.png
         ↓
Nginx (frontend 容器)
         ↓
匹配 location /api/
         ↓
代理到后端: http://backend:8022/api/v1/media/articles/7/images/img_0002.png
         ↓
FastAPI 处理请求
         ↓
返回文件: /app/backend/uploads/articles/7/images/img_0002.png
         ↓
Nginx 返回给浏览器
```

### Docker 网络架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network: knowledge-net           │
│                                                              │
│  ┌──────────────────┐              ┌──────────────────┐     │
│  │  frontend 容器    │              │   backend 容器    │     │
│  │  (Nginx + React) │◄─────────────│  (FastAPI)       │     │
│  │  Port: 80        │   http://     │  Port: 8022      │     │
│  │  Host: 5173      │   backend:8022│                  │     │
│  └──────────────────┘              └──────────────────┘     │
│         │                                                   │
│         │ ./frontend/dist:/usr/share/nginx/html            │
│         │ (volumes 挂载)                                    │
│         ▼                                                   │
│  ┌──────────────────┐                                       │
│  │  宿主机目录       │                                       │
│  │  ./frontend/dist │                                       │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### 环境变量配置

| 环境 | VITE_API_BASE_URL | 图片路径 | 访问方式 |
|------|-------------------|----------|----------|
| 开发环境 | `http://localhost:8022/api/v1` | `http://localhost:8022/api/v1/media/...` | 直接访问后端 |
| 生产环境（Docker） | `/api/v1` | `/api/v1/media/...` | 通过 Nginx 代理 |

---

## 验证清单

部署完成后，按以下清单验证：

- [ ] 前端页面能正常访问
- [ ] 文章列表能正常加载
- [ ] 文章详情页面能正常显示
- [ ] 文章中的图片能正常显示
- [ ] 浏览器控制台没有 404 错误
- [ ] 浏览器网络请求中图片返回 200 OK
- [ ] 后端日志没有错误
- [ ] Nginx 日志没有错误

---

## 总结

这次问题的核心在于：

1. **前端代码问题**：硬编码 localhost 导致在 Docker 环境中无法访问后端
2. **Nginx 配置问题**：静态资源缓存规则优先级高于 API 代理，导致图片请求被拦截

**关键经验**：
- Docker 环境中要使用相对路径或服务名，不要硬编码 localhost
- Nginx location 匹配优先级：精确匹配 > 正则匹配 > 前缀匹配
- 配置修改后要强制重新构建镜像，避免使用缓存
- 部署前要在本地充分测试，确保配置正确

**推荐实践**：
- 使用环境变量管理不同环境的配置
- 编写详细的部署文档和故障排查手册
- 使用健康检查端点监控系统状态
- 定期备份重要数据和配置文件

#!/bin/bash
# 图片访问问题诊断脚本

echo "=== 1. 检查后端容器中的文件路径 ==="
docker exec knowledge-backend ls -la /app/backend/uploads/articles/7/images/ 2>/dev/null || echo "❌ 容器内路径不存在"

echo ""
echo "=== 2. 检查宿主机文件路径 ==="
ls -la ./backend/uploads/articles/7/images/ 2>/dev/null || echo "❌ 宿主机路径不存在"

echo ""
echo "=== 3. 检查后端 upload_dir 配置 ==="
docker exec knowledge-backend python -c "
from backend.settings.config import settings
import os
print(f'upload_dir: {settings.upload_dir}')
print(f'upload_dir exists: {os.path.exists(settings.upload_dir)}')
print(f'upload_dir absolute: {os.path.abspath(settings.upload_dir)}')
article_dir = os.path.join(settings.upload_dir, 'articles', '7')
print(f'article_dir: {article_dir}')
print(f'article_dir exists: {os.path.exists(article_dir)}')
image_path = os.path.join(article_dir, 'images', 'img_0002.png')
print(f'image_path: {image_path}')
print(f'image exists: {os.path.exists(image_path)}')
" 2>/dev/null || echo "❌ 无法执行 Python 检查"

echo ""
echo "=== 4. 测试后端 API ==="
curl -I http://localhost:8022/api/v1/media/articles/7/images/img_0002.png 2>/dev/null | head -5 || echo "❌ 本地 API 无法访问"

echo ""
echo "=== 5. 检查后端容器日志 ==="
docker logs knowledge-backend --tail 20 2>/dev/null | grep -i "media\|404\|error" || echo "无相关日志"

echo ""
echo "=== 6. 检查 Nginx 配置 ==="
docker exec knowledge-frontend cat /etc/nginx/conf.d/default.conf | grep -A 10 "location /api/"

echo ""
echo "=== 7. 测试完整链路 ==="
curl -I http://localhost:5173/api/v1/media/articles/7/images/img_0002.png 2>/dev/null | head -5 || echo "❌ 通过 Nginx 访问失败"

echo ""
echo "=== 诊断完成 ==="
echo "如果第 1 步失败，说明 Docker 挂载有问题"
echo "如果第 3 步失败，说明后端配置有问题"
echo "如果第 4 步失败但第 3 步成功，说明后端路由有问题"
echo "如果第 7 步失败但第 4 步成功，说明 Nginx 代理有问题"

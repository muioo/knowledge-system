# Docker 部署指南

## 前置条件

1. Ubuntu 服务器已安装 Docker 和 Docker Compose
2. MySQL 容器已运行在端口 3307

## 部署步骤

### 1. 初始化数据库

在服务器上运行：

```bash
chmod +x init-db.sh
./init-db.sh
```

这会创建：
- 数据库：`knowledge_system`
- 用户：`knowledge_user` (密码: `Knowledge@123`)

### 2. 更新 CORS 配置

编辑 `backend/.env`，将 `CORS_ORIGINS` 改为你的服务器 IP：

```bash
CORS_ORIGINS=["http://your-server-ip:5173"]
```

### 3. 一键启动

```bash
docker compose up -d --build
```

### 4. 查看日志

```bash
# 查看所有服务
docker compose logs -f

# 只看后端
docker compose logs -f backend

# 只看前端
docker compose logs -f frontend
```

### 5. 访问应用

浏览器打开：`http://your-server-ip:5173`

## 关键配置说明

- **DB_HOST**: `host.docker.internal` - 容器访问宿主机 MySQL
- **DB_PORT**: `3307` - 你的 MySQL 端口
- **extra_hosts**: 让容器能解析 `host.docker.internal` 到宿主机

## 常用命令

```bash
# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看运行状态
docker compose ps

# 进入后端容器
docker exec -it knowledge-backend bash

# 查看数据库连接
docker exec -it knowledge-backend python -c "from backend.settings.config import settings; print(settings.database_url)"
```

## 故障排查

### 后端无法连接数据库

检查 MySQL 是否允许远程连接：

```bash
docker exec -i mysql mysql -uroot -p123456 -e "SELECT User, Host FROM mysql.user WHERE User='knowledge_user';"
```

### 前端无法访问后端 API

检查 nginx 代理配置和网络连通性：

```bash
docker exec -it knowledge-frontend wget -O- http://backend:8022/health
```

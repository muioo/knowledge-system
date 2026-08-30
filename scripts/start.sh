#!/usr/bin/env bash
# ============================================================
# knowledge-system 一键启动脚本（Linux / macOS）
# 用法:
#   ./scripts/start.sh              构建并启动全部服务，并等待健康检查
# 说明:
#   1) 首次运行或代码更新后，会自动重新构建镜像
#   2) 全新数据库会自动建表，无需导入任何既有数据
#   3) 可零配置直接运行；如需覆盖默认值，在项目根目录建 .env
#   4) 启动成功后访问:  http://localhost:5173
#   5) 停止: ./scripts/stop.sh    清空数据回到全新态: ./scripts/stop.sh --reset
# ============================================================
set -euo pipefail

# 脚本位于 scripts/ 下，切换到上一级（项目根目录），确保能定位 docker-compose.yml
cd "$(dirname "$0")/.."

echo "=============================================="
echo " 构建并启动容器（MySQL / backend / frontend）"
echo "=============================================="
docker compose up -d --build

BACKEND_URL="${BACKEND_HEALTH_URL:-http://localhost:8022/health}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "等待后端健康检查: ${BACKEND_URL} ..."
MAX_WAIT=180
for i in $(seq 1 "$MAX_WAIT"); do
  if curl -fsS "$BACKEND_URL" >/dev/null 2>&1; then
    echo "后端已就绪（耗时约 ${i}s）"
    break
  fi
  if [ "$i" -eq "$MAX_WAIT" ]; then
    echo "错误：后端 ${MAX_WAIT}s 内未就绪，请运行 docker compose logs backend 查看日志。" >&2
    exit 1
  fi
  sleep 1
done

echo "=============================================="
echo " 服务状态:"
docker compose ps
echo "=============================================="
echo " 前端已启动: http://localhost:${FRONTEND_PORT}"
echo " 首次使用请点击页面“注册”创建管理员账号。"
echo " 停止服务: ./scripts/stop.sh | 回到全新态: ./scripts/stop.sh --reset"
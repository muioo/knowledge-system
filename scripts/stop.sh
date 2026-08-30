#!/usr/bin/env bash
# ============================================================
# knowledge-system 一键停止脚本（Linux / macOS）
# 用法:
#   ./stop.sh              停止全部容器（保留数据卷）
#   ./stop.sh --reset      停止并清空数据卷，回到全新态
# ============================================================
set -euo pipefail

# 脚本位于 scripts/ 下，切换到上一级（项目根目录）
cd "$(dirname "$0")/.."

EXTRA_ARGS=()
if [ "${1:-}" = "--reset" ]; then
  EXTRA_ARGS=(-v)
  echo "停止服务并清空数据卷（回到全新态）..."
else
  echo "停止服务（保留数据卷）..."
fi

docker compose down "${EXTRA_ARGS[@]}"
echo "已停止。"

if [ "${#EXTRA_ARGS[@]}" -gt 0 ]; then
  echo "提示：下次 ./scripts/start.sh 会重建全新空库，需重新注册账号。"
fi
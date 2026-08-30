@echo off
setlocal
rem ============================================================
rem knowledge-system 一键停止脚本（Windows）
rem 用法:
rem   stop.bat                 停止全部容器（保留数据卷）
rem   stop.bat --reset         停止并清空数据卷，回到全新态
rem ============================================================

rem 切换到脚本上一级（项目根目录）
cd /d "%~dp0\.."

if "%1"=="--reset" (
  echo 停止服务并清空数据卷（回到全新态）...
  docker compose down -v
  echo 提示：下次 scripts\start.bat 会重建全新空库，需重新注册账号。
) else (
  echo 停止服务（保留数据卷）...
  docker compose down
)
echo 已停止。
endlocal
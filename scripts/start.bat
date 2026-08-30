@echo off
setlocal
rem ============================================================
rem knowledge-system 一键启动脚本（Windows）
rem 用法:
rem   start.bat               构建并启动全部服务，并等待健康检查
rem 说明:
rem   1) 首次运行或代码更新后，会自动重新构建镜像
rem   2) 全新数据库会自动建表，无需导入任何既有数据
rem   3) 可零配置直接运行；如需覆盖默认值，在项目根目录建 .env
rem   4) 启动成功后访问:  http://localhost:5173
rem   5) 停止: stop.bat   回到全新态: stop.bat --reset
rem ============================================================

rem 切换到脚本上一级（项目根目录），确保能定位 docker-compose.yml
cd /d "%~dp0\.."

echo ==============================================
echo  构建并启动容器（MySQL / backend / frontend）
echo ==============================================
docker compose up -d --build
if errorlevel 1 (
  echo 启动失败，请确认已安装并启动 Docker 后重试。
  exit /b 1
)

set "BACKEND_URL=http://localhost:8022/health"
echo 等待后端健康检查: %BACKEND_URL% ...
set /a MAX_WAIT=180
for /l %%i in (1,1,%MAX_WAIT%) do (
  curl.exe -fsS %BACKEND_URL% >nul 2>&1
  if not errorlevel 1 (
    echo 后端已就绪。
    goto ready
  )
  timeout /t 1 /nobreak >nul
)
echo 错误：后端在 %MAX_WAIT%s 内未就绪，请运行 docker compose logs backend 查看日志。
exit /b 1

:ready
echo ==============================================
echo  服务状态:
docker compose ps
echo ==============================================
echo  前端已启动: http://localhost:5173
echo  首次使用请点击页面“注册”创建管理员账号。
echo  停止服务: scripts\stop.bat ^| 回到全新态: scripts\stop.bat --reset
endlocal
FROM python:3.11-slim

# 工作目录设为 /app，backend 代码放在 /app/backend/ 下，保持包路径 backend.main:app
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# 复制项目代码到 /app/backend/（保持 backend.xxx 包路径）
COPY . ./backend/

EXPOSE 8022

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8022"]

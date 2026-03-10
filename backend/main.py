from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from backend.core.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
from backend.api.v1 import register_routers
from backend.settings.config import settings, TORTOISE_ORM


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    yield
    # 关闭时清理数据库连接
    await Tortoise.close_connections()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS 中间件必须最先添加，以便正确处理 OPTIONS 预检请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注意：自定义中间件可能会干扰 CORS，需要确保它们正确处理 OPTIONS 请求
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

register_routers(app)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8022)

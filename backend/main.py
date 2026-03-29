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

# 自定义中间件先添加（内层）
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS 中间件最后添加（最外层），确保所有响应都携带 CORS 头
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

register_routers(app)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8022)

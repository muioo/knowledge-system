from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"请求: {request.method} {request.url.path}")
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"响应: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"错误: {request.method} {request.url.path} - {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "message": "服务器内部错误",
                    "detail": {"error": str(e)} if request.app.debug else None
                }
            )

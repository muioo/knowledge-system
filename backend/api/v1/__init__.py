from fastapi import FastAPI
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.users import router as users_router
from backend.api.v1.endpoints.articles import router as articles_router
from backend.api.v1.endpoints.tags import router as tags_router
from backend.api.v1.endpoints.search import router as search_router
from backend.api.v1.endpoints.reading import router as reading_router

def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(articles_router, prefix="/api/v1")
    app.include_router(tags_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(reading_router, prefix="/api/v1")

__all__ = ["register_routers"]

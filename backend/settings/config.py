import os
from pathlib import Path
from typing import List

import json
from pydantic_settings import BaseSettings


# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "知识系统后端"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str

    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str
    db_name: str = "knowledge-system"

    # JWT 配置
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # 文件上传配置
    max_file_size: int = 10485760  # 10MB
    # 使用相对于此文件的路径：backend/settings/config.py -> ../uploads -> backend/uploads
    upload_dir: str = str(Path(__file__).resolve().parent.parent / "uploads")

    # CORS 配置
    cors_origins: str = '["http://localhost:3001", "http://localhost:5173", "http://localhost:8000","http://localhost:3000"]'

    # 火山引擎 AI 配置
    ark_api_key: str

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    @property
    def database_url(self) -> str:
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def tortoise_orm(self) -> dict:
        """TortoiseORM 配置"""
        return {
            "connections": {"default": self.database_url},
            "apps": {
                "models": {
                    "models": [
                        "backend.models.user",
                        "backend.models.article",
                        "backend.models.tag",
                        "backend.models.reading"
                    ],
                    "default_connection": "default",
                },
                "aerich": {
                    "models": ["aerich.models"],
                    "default_connection": "default",
                }
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai"
        }

    model_config = {
        "env_file": ["backend/.env", ".env"],
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


settings = Settings()

# 导出 TORTOISE_ORM 配置供使用
TORTOISE_ORM = settings.tortoise_orm

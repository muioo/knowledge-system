from pydantic_settings import BaseSettings
from typing import List
import json


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
    upload_dir: str = "./uploads"

    # CORS 配置
    cors_origins: str = '["http://localhost:3000", "http://localhost:8000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    @property
    def database_url(self) -> str:
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

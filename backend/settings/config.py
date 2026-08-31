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

    # CORS 配置 服务器前端地址
    cors_origins: str = '["http://localhost:3001", "http://localhost:5173","http://localhost:3000"]'

    # 服务器外部访问地址（用于生成图片链接等）
    # 例如：http://123.45.67.89:8022 或 http://yourdomain.com
    # 留空则自动从请求头获取
    base_url: str = ""

    # 是否验证SSL证书（某些网络环境下需要禁用）
    verify_ssl: bool = True

    # ---- AI 提取多供应商配置：密钥仅从后端环境变量读取，前端不采集、不传参 ----
    # 智谱（保留 SDK 专路）
    zhipu_api_key: str = ""
    zhipu_default_model: str = "glm-4-flash"
    # 阿里云百炼/千问（OpenAI 兼容协议，专属实例按 workspace_id 拼接 base_url）
    dashscope_api_key: str = ""
    dashscope_workspace_id: str = ""
    dashscope_default_model: str = ""
    # 自定义 OpenAI 兼容供应商（DeepSeek 官方、自建 vLLM 等）
    custom_api_key: str = ""
    custom_base_url: str = ""
    custom_default_model: str = ""

    # 通用 AI 可调参数（均有默认值，可按需用环境变量覆盖）
    ai_temperature: float = 0.2  # 模型采样温度
    ai_max_workers: int = 2  # 摘要提取线程池大小
    ai_max_content_len: int = 15000  # 网页内容送入模型的截断长度
    ai_max_text_len: int = 5000  # 已有文章正文送入模型的截断长度

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
                        "backend.models.user_ai_setting",
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
            "timezone": "Asia/Shanghai",
            # 启用单例模式以支持事务
            "single_instance": True,
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

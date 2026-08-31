from pydantic import BaseModel, Field
from typing import List, Optional


class AiProviderInfo(BaseModel):
    """供应商信息：是否已配置密钥、默认模型、当前用户绑定的模型。"""

    provider: str = Field(..., description="供应商标识：zhipu / dashscope / custom")
    name: str = Field(..., description="供应商展示名")
    available: bool = Field(..., description="该供应商当前是否可用（用户自配密钥或服务端环境变量）")
    default_model: str = Field("", description="服务端配置的默认模型")
    user_model: Optional[str] = Field(None, description="当前用户绑定的模型")
    has_apikey: bool = Field(False, description="当前用户是否已为该供应商配置密钥（不回传明文）")


class UserAiSettingsResponse(BaseModel):
    """当前用户的 AI 提取配置：供应商列表 + 用户绑定情况。"""

    providers: List[AiProviderInfo]


class UserAiSettingUpdate(BaseModel):
    """保存用户级 AI 模型偏好与可选的自配密钥。"""

    provider: str = Field(..., description="供应商标识：zhipu / dashscope / custom")
    model: str = Field(..., min_length=1, max_length=100, description="用户录入的模型名称")
    api_key: Optional[str] = Field(None, description="用户录入的 API Key，为空/未传则不修改已存密钥")

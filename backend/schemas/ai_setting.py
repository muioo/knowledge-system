from pydantic import BaseModel, Field
from typing import List, Optional


class AiProviderInfo(BaseModel):
    """供应商信息：是否已配置密钥、默认模型、当前用户绑定的模型。"""

    provider: str = Field(..., description="供应商标识：zhipu / dashscope / custom")
    name: str = Field(..., description="供应商展示名")
    available: bool = Field(..., description="服务端是否已配置该供应商密钥")
    default_model: str = Field("", description="服务端配置的默认模型")
    user_model: Optional[str] = Field(None, description="当前用户绑定的模型")


class UserAiSettingsResponse(BaseModel):
    """当前用户的 AI 提取配置：供应商列表 + 用户绑定情况。"""

    providers: List[AiProviderInfo]


class UserAiSettingUpdate(BaseModel):
    """保存用户级 AI 模型偏好。"""

    provider: str = Field(..., description="供应商标识：zhipu / dashscope / custom")
    model: str = Field(..., min_length=1, max_length=100, description="用户录入的模型名称")

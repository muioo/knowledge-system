"""用户级 AI 提取配置：为每个供应商绑定常用模型，密钥仍仅在服务端环境变量。"""
import logging

from backend.models import UserAiSetting
from backend.schemas.ai_setting import AiProviderInfo, UserAiSettingsResponse
from backend.utils.ai_extractor import SUPPORTED_PROVIDERS, provider_available, provider_default_model

logger = logging.getLogger(__name__)


async def get_user_ai_settings(user_id: int) -> UserAiSettingsResponse:
    """查询供应商列表及当前用户在各供应商上绑定的模型。"""
    # 一次性取出该用户的全部绑定，避免循环查询
    settings = await UserAiSetting.filter(user_id=user_id)
    user_models = {item.provider: item.model for item in settings}

    providers = []
    for provider, name in SUPPORTED_PROVIDERS.items():
        providers.append(AiProviderInfo(
            provider=provider,
            name=name,
            available=provider_available(provider),
            default_model=provider_default_model(provider),
            user_model=user_models.get(provider),
        ))
    return UserAiSettingsResponse(providers=providers)


async def save_user_ai_setting(user_id: int, provider: str, model: str) -> AiProviderInfo:
    """保存（新增或覆盖）用户在指定供应商上的模型绑定。"""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"不支持的 AI 供应商: {provider}")

    model = model.strip()
    if not model:
        raise ValueError("模型名称不能为空")

    # 同一用户同一供应商仅保留一条记录：存在则覆盖，不存在则新建
    setting, _ = await UserAiSetting.get_or_create(user_id=user_id, provider=provider)
    setting.model = model
    await setting.save(update_fields=["model", "updated_at"])
    logger.info("[AI Setting] 用户 %s 绑定供应商 %s 模型 %s", user_id, provider, model)

    return AiProviderInfo(
        provider=provider,
        name=SUPPORTED_PROVIDERS[provider],
        available=provider_available(provider),
        default_model=provider_default_model(provider),
        user_model=model,
    )


async def get_user_model(user_id: int, provider: str) -> str:
    """读取用户在指定供应商上绑定的模型，未绑定时返回空字符串。"""
    setting = await UserAiSetting.filter(user_id=user_id, provider=provider).first()
    return setting.model if setting else ""


async def get_user_provider_model(user_id: int) -> tuple:
    """获取用户首个可用的供应商与模型，用于文章导入时自动选择。

    返回 (provider, model)，无可绑定配置时返回 (None, None)。
    """
    settings = await UserAiSetting.filter(user_id=user_id)
    # 优先选择服务端已配置密钥的供应商
    for item in settings:
        if provider_available(item.provider):
            return item.provider, item.model
    for provider in SUPPORTED_PROVIDERS:
        if provider_available(provider):
            return provider, ""
    return None, None

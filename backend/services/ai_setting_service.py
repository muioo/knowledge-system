"""用户级 AI 提取配置：为每个供应商绑定模型，并支持用户在前端自配 API Key（加密存储）。"""
import logging

from backend.models import UserAiSetting
from backend.schemas.ai_setting import AiProviderInfo, UserAiSettingsResponse
from backend.ai.ai_extractor import SUPPORTED_PROVIDERS, provider_available, provider_default_model
from backend.utils.crypto_utils import encrypt_secret, decrypt_secret

logger = logging.getLogger(__name__)


async def get_user_ai_settings(user_id: int) -> UserAiSettingsResponse:
    """查询供应商列表及当前用户在各供应商上绑定的模型与密钥状态。"""
    # 一次性取出该用户的全部绑定，避免循环查询
    settings = await UserAiSetting.filter(user_id=user_id)
    user_models = {item.provider: item.model for item in settings}
    user_has_apikey = {item.provider: bool(item.api_key) for item in settings}

    providers = []
    for provider, name in SUPPORTED_PROVIDERS.items():
        has_apikey = bool(user_has_apikey.get(provider))
        providers.append(AiProviderInfo(
            provider=provider,
            name=name,
            # 用户自配密钥计入可用性：自配过即视为可用，否则看服务端环境变量
            available=has_apikey or provider_available(provider),
            default_model=provider_default_model(provider),
            user_model=user_models.get(provider),
            has_apikey=has_apikey,
        ))
    return UserAiSettingsResponse(providers=providers)


async def get_user_api_key(user_id: int, provider: str) -> str:
    """读取用户在指定供应商上自配的 API Key 明文；未配置返回空字符串。

    密文解密失败会抛 ValueError，由上层转为明确提示。
    """
    setting = await UserAiSetting.filter(user_id=user_id, provider=provider).first()
    if not setting or not setting.api_key:
        return ""
    # 为空/无密文则返回空，外部走服务端环境变量
    return decrypt_secret(setting.api_key)


async def save_user_ai_setting(user_id: int, provider: str, model: str, api_key: str = None) -> AiProviderInfo:
    """保存（新增或覆盖）用户在指定供应商上的模型绑定，并在提供时加密存储自配密钥。"""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"不支持的 AI 供应商: {provider}")

    model = model.strip()
    if not model:
        raise ValueError("模型名称不能为空")

    # 同一用户同一供应商仅保留一条记录：存在则覆盖，不存在则以当前 model 新建
    # 注意不能用 get_or_create 再赋 model，否则新建行 model=None 会触发非空校验报错
    setting = await UserAiSetting.filter(user_id=user_id, provider=provider).first()
    if setting is None:
        setting = await UserAiSetting.create(user_id=user_id, provider=provider, model=model)
        update_fields = ["model"]
    else:
        setting.model = model
        update_fields = ["model", "updated_at"]

    # api_key 非空时加密更新；为空/未传则保留已存密钥
    if api_key and api_key.strip():
        # Fernet 密文最长约 100+ 字符，远小于 512 上限
        setting.api_key = encrypt_secret(api_key.strip())
        update_fields.append("api_key")
        has_apikey = True
    else:
        has_apikey = bool(setting.api_key)

    await setting.save(update_fields=update_fields)
    logger.info("[AI Setting] 用户 %s 绑定供应商 %s 模型 %s (has_apikey=%s)", user_id, provider, model, has_apikey)

    return AiProviderInfo(
        provider=provider,
        name=SUPPORTED_PROVIDERS[provider],
        available=True if has_apikey else provider_available(provider),
        default_model=provider_default_model(provider),
        user_model=model,
        has_apikey=has_apikey,
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
    # 优先选择服务端已配置密钥的供应商，或用户已自配密钥的供应商
    for item in settings:
        if provider_available(item.provider) or bool(item.api_key):
            return item.provider, item.model
    for provider in SUPPORTED_PROVIDERS:
        if provider_available(provider):
            return provider, ""
    return None, None

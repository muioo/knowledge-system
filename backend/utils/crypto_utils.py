"""密钥加解密工具：用 SECRET_KEY 派生密钥做 Fernet 对称加密，用于加密用户级 AI API Key。"""
import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken

from backend.settings.config import settings

logger = logging.getLogger(__name__)


def _fernet() -> Fernet:
    """由 SECRET_KEY 派生固定密钥并构造 Fernet 实例。

    派生方式：对 SECRET_KEY 取 SHA-256 摘要后做 url-safe base64 编码，
    得到 Fernet 所需的 32 字节密钥。SECRET_KEY 改变会导致历史密文无法解密。
    """
    digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(text: str) -> str:
    """加密一段明文密钥，返回可用于存储的密文字符串。"""
    return _fernet().encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str:
    """解密 encrypt_secret 产生的密文，返回原明文。"""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError) as exc:
        # 密钥错误或密文格式非法时抛错，由调用方转为明确提示
        logger.error("[Crypto] 解密失败: %s", exc, exc_info=True)
        raise ValueError("API 密钥解密失败，请在页面重新设置") from exc
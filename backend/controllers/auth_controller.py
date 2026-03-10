from backend.models import User
from backend.schemas.user import UserCreate, TokenResponse, UserResponse
from backend.utils.password import hash_password, verify_password
from backend.utils.jwt import create_access_token, create_refresh_token, decode_token
from typing import Optional

async def register_user(data: UserCreate) -> TokenResponse:
    existing = await User.get_or_none(username=data.username)
    if existing:
        raise ValueError("用户名已存在")
    existing = await User.get_or_none(email=data.email)
    if existing:
        raise ValueError("邮箱已被使用")
    hashed = hash_password(data.password)
    user = await User.create(
        username=data.username,
        email=data.email,
        hashed_password=hashed
    )
    # 注册成功后自动登录，返回 token
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await User.get_or_none(username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def login_user(username: str, password: str) -> TokenResponse:
    user = await authenticate_user(username, password)
    if not user:
        raise ValueError("用户名或密码错误")
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


async def refresh_token(refresh_token_str: str) -> TokenResponse:
    """使用 refresh_token 刷新 access_token"""
    # 解码 refresh_token
    payload = decode_token(refresh_token_str)

    if not payload:
        raise ValueError("无效的 refresh_token")

    user_id = payload.get("sub")

    if not user_id:
        raise ValueError("无效的 refresh_token")

    user = await User.get_or_none(id=int(user_id))
    if not user:
        raise ValueError("用户不存在")

    if not user.is_active:
        raise ValueError("用户已被禁用")

    # 生成新的 tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

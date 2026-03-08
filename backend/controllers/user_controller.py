from backend.models import User
from backend.schemas.user import UserResponse, UserUpdate, UpdateRole, UpdateUserStatus
from typing import List

async def get_user_by_id(user_id: int) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

async def update_user(user_id: int, data: UserUpdate) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    if data.email:
        user.email = data.email
    if data.password:
        from utils.password import hash_password
        user.hashed_password = hash_password(data.password)
    await user.save()
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

async def delete_user(user_id: int) -> bool:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    await user.delete()
    return True

async def list_users(page: int = 1, size: int = 20) -> tuple[List[UserResponse], int]:
    total = await User.all().count()
    users = await User.all().offset((page - 1) * size).limit(size)
    return (
        [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at
            ) for u in users
        ],
        total
    )

async def update_user_role(user_id: int, data: UpdateRole) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    user.role = data.role
    await user.save()
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

async def toggle_user_status(user_id: int, data: UpdateUserStatus) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    user.is_active = data.is_active
    await user.save()
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

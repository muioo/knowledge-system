from fastapi import APIRouter, HTTPException, Depends, status
from backend.core.security import get_current_user, get_current_admin
from backend.models import User
from backend.schemas.user import UserResponse, UserUpdate, UpdateRole, UpdateUserStatus
from backend.schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from backend.controllers.user_controller import (
    get_user_by_id,
    update_user,
    delete_user,
    list_users,
    update_user_role,
    toggle_user_status
)

router = APIRouter(prefix="/users", tags=["用户"])

@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return SuccessResponse(data=UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    ))

@router.put("/me", response_model=SuccessResponse[UserResponse])
async def update_current_user_info(
    data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await update_user(current_user.id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/me", status_code=204)
async def delete_current_user(current_user: User = Depends(get_current_user)):
    try:
        await delete_user(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    page: int = 1,
    size: int = 20,
    current_admin: User = Depends(get_current_admin)
):
    users, total = await list_users(page, size)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=users
    ))

@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await get_user_by_id(user_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}", response_model=SuccessResponse[UserResponse])
async def update_user_by_id(
    user_id: int,
    data: UserUpdate,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await update_user(user_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", status_code=204)
async def delete_user_by_id(
    user_id: int,
    current_admin: User = Depends(get_current_admin)
):
    try:
        await delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{user_id}/role", response_model=SuccessResponse[UserResponse])
async def update_user_role_by_id(
    user_id: int,
    data: UpdateRole,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await update_user_role(user_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{user_id}/status", response_model=SuccessResponse[UserResponse])
async def update_user_status_by_id(
    user_id: int,
    data: UpdateUserStatus,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await toggle_user_status(user_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

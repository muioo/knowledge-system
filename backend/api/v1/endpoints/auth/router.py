from fastapi import APIRouter, HTTPException, status
from backend.schemas.user import UserCreate, UserLogin, TokenResponse
from backend.controllers.auth_controller import register_user, login_user
from backend.schemas.response import SuccessResponse

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=SuccessResponse[TokenResponse])
async def register(data: UserCreate):
    try:
        result = await register_user(data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(data: UserLogin):
    try:
        result = await login_user(data.username, data.password)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

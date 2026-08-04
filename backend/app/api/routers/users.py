from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.models.schema import User
from app.schemas.user import UserChangePassword, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(session)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin profile của chính mình (yêu cầu gửi kèm Token)"""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Cập nhật thông tin cá nhân"""
    return await service.update_profile(current_user, user_in)

@router.patch("/me/password")
async def change_password(
    password_in: UserChangePassword,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Đổi mật khẩu"""
    return await service.change_password(current_user, password_in)

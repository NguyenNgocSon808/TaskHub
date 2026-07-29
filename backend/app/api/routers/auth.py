from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_session
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token, TokenRefreshRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(session)

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.register(user_in)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    service: UserService = Depends(get_user_service)
):
    # FastAPI form_data dùng field 'username', chúng ta ép nó nhận email của hệ thống
    return await service.authenticate(email=form_data.username, password=form_data.password)

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    data: TokenRefreshRequest, 
    service: UserService = Depends(get_user_service)
):
    return await service.refresh_token(data.refresh_token)

@router.post("/logout")
async def logout():
    # Stateless JWT không thể "xóa" token trên server. 
    # Tạm thời trả về 200 OK. Khi nào làm tính năng Redis Blacklist, ta sẽ code thêm tại đây.
    return {"detail": "Successfully logged out. Please remove the token from your client."}
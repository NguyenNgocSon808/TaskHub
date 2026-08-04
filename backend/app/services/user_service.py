import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.schema import UserRole
from app.models.schema import User
from app.repositories.user import UserRepository
from app.schemas.user import UserChangePassword, UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.session = session

    # ==================== CA 3: AUTHENTICATION ====================
    async def register(self, user_in: UserCreate) -> User | None:
        # Kiểm tra email tồn tại
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Băm mật khẩu và lưu database
        hashed_password = get_password_hash(user_in.password)
        new_user = await self.repo.create(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed_password,
            role=UserRole.MEMBER,
            is_active=True,
        )
        return new_user

    async def authenticate(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer"
        }

    async def refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if token_type != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
                
            user = await self.repo.get_by_id(int(user_id) if user_id is not None else 0)
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")
                
            return {
                "access_token": create_access_token(user.id),
                "refresh_token": create_refresh_token(user.id), # Có thể cấp lại luôn refresh token mới
                "token_type": "bearer"
            }
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # ==================== CA 4: USER MANAGEMENT ====================
    async def update_profile(self, user: User, user_in: UserUpdate) -> User | None:
        update_data = user_in.model_dump(exclude_unset=True)
        return await self.repo.update(user.id, **update_data)

    async def change_password(self, user: User, password_in: UserChangePassword):
        if not verify_password(password_in.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect old password")
            
        new_hashed_password = get_password_hash(password_in.new_password)
        await self.repo.update(user.id, hashed_password=new_hashed_password)
        return {"detail": "Password updated successfully"}

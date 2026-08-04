import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import sessionmanager
from app.core.exceptions import CredentialsException
from app.models.schema import User

# Khai báo với Swagger UI biết endpoint nào dùng để login lấy token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Dependency lấy DB session (bạn có thể đã viết hàm này ở bước trước)
from collections.abc import AsyncGenerator


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Trạm kiểm soát chính
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    try:
        # Giải mã token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        
        # Kiểm tra xem có đúng là access token không
        if user_id is None or token_type != "access":
            raise CredentialsException
            
    except jwt.PyJWTError:
        raise CredentialsException

    # Truy vấn DB để lấy thông tin User
    query = select(User).where(User.id == int(user_id))
    result = await session.execute(query)
    user = result.scalars().first()

    # Kiểm tra xem user có tồn tại và đang active hay không
    if user is None:
        raise CredentialsException
    if not user.is_active:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    return user


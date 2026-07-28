from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[T]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> T:
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: int, **kwargs) -> Optional[T]:
        query = update(self.model).where(self.model.id == id).values(**kwargs).returning(self.model)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()

    async def delete(self, id: int) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

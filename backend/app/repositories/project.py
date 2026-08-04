from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

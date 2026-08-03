from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.repositories.base import BaseRepository
from app.models.schema import Workspace, WorkspaceMember

class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(WorkspaceMember, session)

    async def get_member(self, workspace_id: int, user_id: int) -> Optional[WorkspaceMember]:
        query = select(self.model).where(
            and_(self.model.workspace_id == workspace_id, self.model.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

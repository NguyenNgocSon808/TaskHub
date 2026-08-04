
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def __init__(self, session: AsyncSession):
        super().__init__(Workspace, session)

class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(WorkspaceMember, session)

    async def get_member(self, workspace_id: int, user_id: int) -> WorkspaceMember | None:
        query = select(self.model).where(
            and_(self.model.workspace_id == workspace_id, self.model.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

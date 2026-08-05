
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import Task, TaskPriority, TaskStatus
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_tasks_with_filters(
        self, 
        project_id: int, 
        skip: int = 0, 
        limit: int = 20,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None
    ) -> list[Task]:
        # Khởi tạo query cơ bản theo project
        query = select(self.model).where(self.model.project_id == project_id)
        
        # Thêm điều kiện lọc động (Dynamic Filtering)
        if status:
            query = query.where(self.model.status == status)
        if priority:
            query = query.where(self.model.priority == priority)
        if assignee_id:
            query = query.where(self.model.assignee_id == assignee_id)
            
        # Thêm phân trang (Pagination)
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

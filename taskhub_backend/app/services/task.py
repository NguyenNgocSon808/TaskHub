from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession):
        self.repo = TaskRepository(session)

    async def get_tasks(self, skip: int = 0, limit: int = 10):
        return await self.repo.get_all(skip, limit)

    async def get_task(self, task_id: int):
        return await self.repo.get_by_id(task_id)

    async def create_task(self, task_data: TaskCreate):
        return await self.repo.create(**task_data.model_dump())

    async def update_task(self, task_id: int, task_data: TaskUpdate):
        payload = task_data.model_dump(exclude_unset=True)
        if not payload:
            return await self.repo.get_by_id(task_id)
        return await self.repo.update(task_id, **payload)

    async def delete_task(self, task_id: int):
        return await self.repo.delete(task_id)

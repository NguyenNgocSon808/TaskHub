from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import User
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, session: AsyncSession):
        self.task_repo = TaskRepository(session)
        self.session = session

    async def create_task(self, current_user: User, project_id: int, data: TaskCreate):
        # Lưu ý: Trong thực tế, bạn nên gọi hàm check quyền xem user có trong Project này không
        return await self.task_repo.create(
            project_id=project_id,
            created_by=current_user.id,
            **data.model_dump()
        )

    async def get_tasks(self, project_id: int, skip: int, limit: int, status, priority, assignee_id):
        return await self.task_repo.get_tasks_with_filters(
            project_id=project_id, skip=skip, limit=limit, 
            status=status, priority=priority, assignee_id=assignee_id
        )

    async def update_task(self, task_id: int, data: TaskUpdate):
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        update_data = data.model_dump(exclude_unset=True)
        return await self.task_repo.update(task_id, **update_data)

    async def delete_task(self, task_id: int):
        success = await self.task_repo.delete(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"detail": "Task deleted successfully"}

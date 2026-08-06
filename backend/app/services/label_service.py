from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import Label, Project, Task, task_labels
from app.repositories.base import BaseRepository
from app.schemas.label import LabelCreate, LabelUpdate


class LabelService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.label_repo = BaseRepository(Label, session)

    async def get_labels_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> list[Label]:
        query = select(Label).where(Label.project_id == project_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_label(self, project_id: int, data: LabelCreate) -> Label:
        # Kiểm tra xem project có tồn tại không
        query = select(Project).where(getattr(Project, "id") == project_id)
        result = await self.session.execute(query)
        if not result.scalars().first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # Create
        return await self.label_repo.create(project_id=project_id, **data.model_dump())

    async def update_label(self, label_id: int, data: LabelUpdate) -> Label:
        label = await self.label_repo.get_by_id(label_id)
        if not label:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")

        update_data = data.model_dump(exclude_unset=True)
        updated_label = await self.label_repo.update(label_id, **update_data)
        if not updated_label:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update label")
        return updated_label

    async def delete_label(self, label_id: int) -> None:
        label = await self.label_repo.get_by_id(label_id)
        if not label:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")

        # Xóa các liên kết trong task_labels trước (tuy nhiên DB có thể tự lo nếu cấu hình cascade, nhưng an toàn thì xóa tay qua ORM)
        stmt = delete(task_labels).where(task_labels.c.label_id == label_id)
        await self.session.execute(stmt)

        await self.label_repo.delete(label_id)

    async def assign_label_to_task(self, task_id: int, label_id: int) -> None:
        # Verify task and label exist
        query_task = select(Task).where(getattr(Task, "id") == task_id)
        result_task = await self.session.execute(query_task)
        if not result_task.scalars().first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        label = await self.label_repo.get_by_id(label_id)
        if not label:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")

        # Check if already assigned
        query_check = select(task_labels).where(
            (task_labels.c.task_id == task_id) & (task_labels.c.label_id == label_id)
        )
        result_check = await self.session.execute(query_check)
        if result_check.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Label already assigned to this task")

        stmt = insert(task_labels).values(task_id=task_id, label_id=label_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_label_from_task(self, task_id: int, label_id: int) -> None:
        stmt = delete(task_labels).where(
            (task_labels.c.task_id == task_id) & (task_labels.c.label_id == label_id)
        )
        result = await self.session.execute(stmt)
        if result.rowcount == 0: # type: ignore
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found on this task")
        await self.session.commit()

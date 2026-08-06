from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema import Comment, Task, User, UserRole
from app.repositories.base import BaseRepository
from app.schemas.comment import CommentCreate


class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.comment_repo = BaseRepository(Comment, session)

    async def get_comments_by_task(self, task_id: int, skip: int = 0, limit: int = 100) -> list[Comment]:
        query = select(Comment).where(Comment.task_id == task_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_comment(self, task_id: int, current_user: User, data: CommentCreate) -> Comment:
        # Kiểm tra Task có tồn tại không
        query = select(Task).where(getattr(Task, "id") == task_id)
        result = await self.session.execute(query)
        if not result.scalars().first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        # Lưu comment
        return await self.comment_repo.create(
            task_id=task_id,
            author_id=current_user.id,
            content=data.content
        )

    async def delete_comment(self, comment_id: int, current_user: User) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        # Chỉ người tạo hoặc admin mới được xóa (hoặc project owner, nhưng ở đây tối giản: author hoặc admin)
        if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to delete this comment")

        await self.comment_repo.delete(comment_id)

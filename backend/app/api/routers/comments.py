from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.models.schema import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment_service import CommentService

router = APIRouter(tags=["Comments"])

def get_comment_service(session: AsyncSession = Depends(get_db_session)) -> CommentService:
    return CommentService(session)

@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_comments_for_task(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    return await service.get_comments_by_task(task_id, skip, limit)

@router.post("/tasks/{task_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    task_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    return await service.create_comment(task_id, current_user, data)

@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service)
):
    await service.delete_comment(comment_id, current_user)

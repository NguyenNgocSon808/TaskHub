from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.dependencies import get_db_session, get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService
from app.models.schema import User
from app.models.enums import TaskStatus, TaskPriority

router = APIRouter(tags=["Tasks"])

def get_task_service(session: AsyncSession = Depends(get_db_session)) -> TaskService:
    return TaskService(session)

# Endpoint lấy danh sách Task có phân trang và lọc
@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_tasks_in_project(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    return await service.get_tasks(project_id, skip, limit, status, priority, assignee_id)

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    project_id: int,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    return await service.create_task(current_user, project_id, data)

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    return await service.update_task(task_id, data)

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    return await service.delete_task(task_id)

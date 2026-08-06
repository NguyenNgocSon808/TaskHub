from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db_session
from app.models.schema import User
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services.label_service import LabelService

router = APIRouter(tags=["Labels"])

def get_label_service(session: AsyncSession = Depends(get_db_session)) -> LabelService:
    return LabelService(session)

@router.get("/projects/{project_id}/labels", response_model=list[LabelResponse])
async def get_labels_in_project(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: LabelService = Depends(get_label_service)
):
    return await service.get_labels_by_project(project_id, skip, limit)

@router.post("/projects/{project_id}/labels", response_model=LabelResponse, status_code=201)
async def create_label(
    project_id: int,
    data: LabelCreate,
    current_user: User = Depends(get_current_user),
    service: LabelService = Depends(get_label_service)
):
    return await service.create_label(project_id, data)

@router.patch("/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: int,
    data: LabelUpdate,
    current_user: User = Depends(get_current_user),
    service: LabelService = Depends(get_label_service)
):
    return await service.update_label(label_id, data)

@router.delete("/labels/{label_id}", status_code=204)
async def delete_label(
    label_id: int,
    current_user: User = Depends(get_current_user),
    service: LabelService = Depends(get_label_service)
):
    await service.delete_label(label_id)

@router.post("/tasks/{task_id}/labels/{label_id}", status_code=201)
async def assign_label(
    task_id: int,
    label_id: int,
    current_user: User = Depends(get_current_user),
    service: LabelService = Depends(get_label_service)
):
    await service.assign_label_to_task(task_id, label_id)
    return {"detail": "Label assigned successfully"}

@router.delete("/tasks/{task_id}/labels/{label_id}", status_code=204)
async def remove_label(
    task_id: int,
    label_id: int,
    current_user: User = Depends(get_current_user),
    service: LabelService = Depends(get_label_service)
):
    await service.remove_label_from_task(task_id, label_id)

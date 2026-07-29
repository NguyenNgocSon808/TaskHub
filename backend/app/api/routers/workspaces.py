from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_session, get_current_user
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceMemberAdd
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.workspace_service import WorkspaceService
from app.models.schema import User

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

def get_workspace_service(session: AsyncSession = Depends(get_db_session)) -> WorkspaceService:
    return WorkspaceService(session)

@router.post("/", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    return await service.create_workspace(current_user, data)

@router.get("/{id}", response_model=WorkspaceResponse)
async def get_workspace(
    id: int,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    return await service.get_workspace(current_user, id)

@router.post("/{id}/members", status_code=201)
async def add_workspace_member(
    id: int,
    member_data: WorkspaceMemberAdd,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    await service.add_member(current_user, id, member_data)
    return {"detail": "Member added successfully"}

@router.delete("/{id}/members/{user_id}")
async def remove_workspace_member(
    id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    return await service.remove_member(current_user, id, user_id)

@router.post("/{id}/projects", response_model=ProjectResponse, status_code=201)
async def create_project_in_workspace(
    id: int,
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service)
):
    return await service.create_project(current_user, id, data)

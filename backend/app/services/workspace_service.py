from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException
from app.models.schema import User, WorkspaceRole
from app.repositories.project import ProjectRepository
from app.repositories.workspace import WorkspaceMemberRepository, WorkspaceRepository
from app.schemas.project import ProjectCreate
from app.schemas.workspace import WorkspaceCreate, WorkspaceMemberAdd


class WorkspaceService:
    def __init__(self, session: AsyncSession):
        self.workspace_repo = WorkspaceRepository(session)
        self.member_repo = WorkspaceMemberRepository(session)
        self.project_repo = ProjectRepository(session)
        self.session = session

    async def _check_permission(self, workspace_id: int, user_id: int, allowed_roles: list[WorkspaceRole]):
        """Hàm nội bộ kiểm tra quyền RBAC của user trong workspace"""
        member = await self.member_repo.get_member(workspace_id, user_id)
        if not member or member.role not in allowed_roles:
            raise ForbiddenException
        return member

    # ================= WORKSPACE CRUD =================
    async def create_workspace(self, user: User, data: WorkspaceCreate):
        # 1. Tạo workspace
        workspace = await self.workspace_repo.create(name=data.name, owner_id=user.id)
        # 2. Tự động gán quyền OWNER cho người tạo
        await self.member_repo.create(
            workspace_id=workspace.id, 
            user_id=user.id, 
            role=WorkspaceRole.OWNER
        )
        return workspace

    async def get_workspace(self, user: User, workspace_id: int):
        # Bất kỳ ai là thành viên (OWNER, EDITOR, VIEWER) đều được xem
        await self._check_permission(
            workspace_id, user.id, 
            [WorkspaceRole.OWNER, WorkspaceRole.EDITOR, WorkspaceRole.VIEWER]
        )
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace

    # ================= WORKSPACE MEMBERS =================
    async def add_member(self, current_user: User, workspace_id: int, member_data: WorkspaceMemberAdd):
        # Chỉ OWNER mới có quyền thêm người
        await self._check_permission(workspace_id, current_user.id, [WorkspaceRole.OWNER])
        
        # Kiểm tra xem user đã ở trong workspace chưa
        existing = await self.member_repo.get_member(workspace_id, member_data.user_id)
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member")
            
        return await self.member_repo.create(
            workspace_id=workspace_id, 
            user_id=member_data.user_id, 
            role=member_data.role
        )

    async def remove_member(self, current_user: User, workspace_id: int, user_id_to_remove: int):
        # Chỉ OWNER mới có quyền xóa người
        await self._check_permission(workspace_id, current_user.id, [WorkspaceRole.OWNER])
        if current_user.id == user_id_to_remove:
            raise HTTPException(status_code=400, detail="Owner cannot remove themselves")
            
        member = await self.member_repo.get_member(workspace_id, user_id_to_remove)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
            
        await self.session.delete(member)
        await self.session.commit()
        return {"detail": "Member removed successfully"}

    # ================= PROJECTS WITHIN WORKSPACE =================
    async def create_project(self, current_user: User, workspace_id: int, project_data: ProjectCreate):
        # Yêu cầu quyền OWNER hoặc EDITOR để tạo Project
        await self._check_permission(
            workspace_id, current_user.id, 
            [WorkspaceRole.OWNER, WorkspaceRole.EDITOR]
        )
        from app.models.schema import ProjectStatus
        return await self.project_repo.create(
            workspace_id=workspace_id,
            name=project_data.name,
            description=project_data.description,
            status=ProjectStatus.ACTIVE
        )

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.schema import WorkspaceRole


class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WorkspaceMemberAdd(BaseModel):
    user_id: int
    role: WorkspaceRole = WorkspaceRole.VIEWER

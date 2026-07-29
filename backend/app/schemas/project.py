from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import ProjectStatus

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: Optional[str]
    status: ProjectStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

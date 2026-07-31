from pydantic import BaseModel, ConfigDict
from typing import Optional

class LabelCreate(BaseModel):
    name: str
    color: Optional[str] = None

class LabelUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class LabelResponse(BaseModel):
    id: int
    project_id: int
    name: str
    color: Optional[str]

    model_config = ConfigDict(from_attributes=True)

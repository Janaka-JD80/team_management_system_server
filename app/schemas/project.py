from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    project_id: UUID

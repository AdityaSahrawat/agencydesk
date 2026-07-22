import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.project import ProjectStatus
from app.schemas.client import ClientResponse
from app.schemas.user import UserResponse


class ProjectCreate(BaseModel):
    client_id: uuid.UUID
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    client_id: Optional[uuid.UUID] = None


class ProjectMemberAssign(BaseModel):
    user_ids: List[uuid.UUID]


class ProjectResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    client_id: uuid.UUID
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    members: List[UserResponse] = []

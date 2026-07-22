import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.membership import RoleEnum


class AgencyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = None


class AgencyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    is_active: Optional[bool] = None


class AgencyResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgencyWithRoleResponse(AgencyResponse):
    role: RoleEnum
    client_id: Optional[uuid.UUID] = None

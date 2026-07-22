import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.membership import RoleEnum


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserMembershipInfo(BaseModel):
    agency_id: uuid.UUID
    agency_name: str
    role: RoleEnum
    client_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class UserWithMembershipsResponse(UserResponse):
    memberships: List[UserMembershipInfo] = []

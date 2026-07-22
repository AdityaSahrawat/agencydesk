import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.invitation import InvitationStatus
from app.models.membership import RoleEnum


class InvitationCreate(BaseModel):
    email: EmailStr
    role: RoleEnum
    client_id: Optional[uuid.UUID] = None


class AcceptInvitationRequest(BaseModel):
    token: str
    password: Optional[str] = Field(None, min_length=6, description="Required if user does not exist yet")
    full_name: Optional[str] = Field(None, min_length=2, description="Required if user does not exist yet")


class InvitationResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    email: EmailStr
    role: RoleEnum
    client_id: Optional[uuid.UUID] = None
    token: str
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

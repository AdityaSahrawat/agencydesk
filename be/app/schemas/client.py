import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    company_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ClientResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    name: str
    company_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

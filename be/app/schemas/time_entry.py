import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserResponse


class TimeEntryCreate(BaseModel):
    project_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    hours: float = Field(..., gt=0)
    date: date
    note: Optional[str] = None


class TimeEntryUpdate(BaseModel):
    hours: Optional[float] = Field(None, gt=0)
    date: Optional[date] = None
    note: Optional[str] = None


class TimeEntryResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    project_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    hours: float
    date: date
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectTotalHoursResponse(BaseModel):
    project_id: uuid.UUID
    total_hours: float

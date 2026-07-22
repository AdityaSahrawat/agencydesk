import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskPriority, TaskStatus
from app.schemas.user import UserResponse


class TaskCreate(BaseModel):
    project_id: uuid.UUID
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None
    is_internal: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None
    is_internal: Optional[bool] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskAssignUpdate(BaseModel):
    assigned_to: Optional[uuid.UUID] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None
    is_internal: bool
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class CommentCreate(BaseModel):
    task_id: uuid.UUID
    content: str
    is_internal: bool = False


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_internal: Optional[bool] = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime
    author: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.task_file import FileApprovalStatus
from app.schemas.user import UserResponse


class FileApprovalUpdate(BaseModel):
    approval_status: FileApprovalStatus


class FileResponse(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    task_id: uuid.UUID
    uploaded_by: uuid.UUID
    filename: str
    file_size: int
    content_type: str
    is_internal: bool
    approval_status: FileApprovalStatus
    created_at: datetime
    updated_at: datetime
    uploader: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

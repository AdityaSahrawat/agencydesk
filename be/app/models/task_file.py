import enum
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


class FileApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TaskFile(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "task_files"

    agency_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    approval_status: Mapped[FileApprovalStatus] = mapped_column(
        Enum(FileApprovalStatus, native_enum=False),
        default=FileApprovalStatus.PENDING,
        nullable=False
    )

    task: Mapped["Task"] = relationship("Task", back_populates="files")
    uploader: Mapped["User"] = relationship("User")
